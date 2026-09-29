"""v0.6.0 single-stage Modal sweep: real Adamson + Norman, A100, budget-capped.

Design:
  * A100-40G ($1.32/hr Modal). Spend guard (CTO #283): stop and report once
    actual spend passes $12 (``--spend-stop-usd``); hard kill at $28.
  * Data pulled in by the script (Phase 1 fetchers) — no manual h5ad.
  * Adamson uses all 3 scPerturb subsets (pilot + 10X005 + 10X010) via
    ``load_adamson_combined``, then stratified-subsampled to ~20 TFs by
    mean |logFC| quantile.
  * Norman stratified-subsampled (fair, seed=2026).
  * Trainer sweep: ``n_tasks × {linear, mlp, scgpt_small} × R∈{1,2,3} ×
    3 seeds`` (amendment 2 A2-4: N is not an axis; the distinct-fit count is
    recorded in provenance as ``trainer_grid``). Atomic JSONL append for
    resume safety.
  * Lifecycle sweep: ``n_tasks × 3 seeds`` with the Anthropic roster of
    amendment 4 (``llm.anthropic_client``: Haiku 4.5 for four roles, Sonnet
    5.5 for the Validator; spend metered per call at the pinned price table). Amendment 2: exactly 3
    rounds per run (A2-2); the LLM cache is the version namespace
    ``/biofm_cache/llm/<prereg_version>/`` (A2-8), whose entry count at start
    (must be 0) and cache-hit count (must be 0) are recorded in provenance; a
    run that fails either is flagged ``replay``.

Run (from ``projects/perturb-seq-eval``; the key is injected by Infisical at
run time and never written to disk; ``LLM_KEY_SOURCE`` records where it
came from, and preflight refuses the run without it)::

    LLM_KEY_SOURCE=infisical:syntropyhealth-app:dev infisical run \\
        --projectId <INFISICAL_PROJECT_ID> --env dev -- \\
        modal run scripts/modal/app_v05.py::entrypoint --version v0.6.0 \\
        --norman-n-singletons 15 --norman-n-doublets 5 --seeds 3

Preflight also requires the pinned pre-registration:
``paper/PREREGISTRATION.md`` must be tracked and committed with no local edits
(its commit + sha256 are recorded in provenance).

Artifacts land on the ``perturb-eval-data`` volume under
``/data/<version>/`` (``--version``, default ``v0.6.0``). Record 0 of
``trainer_runs.jsonl`` and ``lifecycle_runs.jsonl`` is the run's provenance
record (``{"record_type": "provenance", ...}``); ``provenance.json`` holds the
finalized copy. The host-side entrypoint also writes the resolved kwargs to
``configs/runs/<run_id>.json`` (T17). Download with::

    modal volume get perturb-eval-data /v0.6.0/trainer_runs.jsonl \\
        ./artifacts/v0.6.0/trainer_runs.jsonl --force
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import modal

try:
    PROJECT_DIR_HOST = Path(__file__).resolve().parents[2]
except IndexError:
    PROJECT_DIR_HOST = Path(__file__).resolve().parent


image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("git", "build-essential")
    .pip_install(
        "numpy>=1.26",
        "typer>=0.12",
        "pandas>=2.2",
        "pyarrow>=16",
        "scipy>=1.11",
        "h5py==3.16.0",
        "anndata==0.12.19",
        "scikit-learn>=1.3",
        "torch==2.14.0",
        "pydantic>=2.0",
        "requests>=2.31",
        "python-dotenv>=1.0",
        "anthropic>=1.9,<2",  # amendment 4: the Anthropic Messages API client
    )
    .add_local_dir(
        str(PROJECT_DIR_HOST),
        remote_path="/app",
        copy=True,
        ignore=[
            "artifacts/**",
            ".venv/**",
            ".pytest_cache/**",
            ".ruff_cache/**",
            "**/__pycache__/**",
        ],
    )
    .workdir("/app")
    .run_commands("pip install -e .")
)


app = modal.App("perturb-eval-v050")
DATA_VOL = modal.Volume.from_name("perturb-eval-data", create_if_missing=True)
BIOFM_VOL = modal.Volume.from_name("biofm-cache", create_if_missing=True)

# A100-40G on Modal — $1.32/hr (2026 rates). Hard-kill budget:
_A100_HOURLY_USD = 1.32
_BUDGET_HARD_KILL_USD = 28.0
# CTO #283 condition 3: stop and report once actual spend passes this (2x the estimate).
_SPEND_STOP_USD = 12.0
_GPU = "A100-40GB"
_LLM_CACHE_DIR = "/biofm_cache/llm"

# Sweep-shape defaults shared by ``run_v05_sweep`` and the host entrypoint so the
# entrypoint can pass (and record) every resolved kwarg explicitly.
_DEFAULT_R_SWEEP: tuple[int, ...] = (1, 2, 3)
_DEFAULT_BACKBONES: tuple[str, ...] = ("linear", "mlp", "scgpt_small")


# The pre-registration the sweep runs under, relative to the git toplevel (CTO #265).
_PREREGISTRATION_REL = "projects/perturb-seq-eval/paper/PREREGISTRATION.md"
_HOME_PROJECT = "biofm"


def _env_secrets() -> dict[str, str]:
    # LLM_KEY_SOURCE is NOT a secret ("<store>:<project_slug>:<env>");
    # it is forwarded so the container sees the same source the host recorded.
    keys = ("ANTHROPIC_API_KEY", "LLM_KEY_SOURCE")
    return {k: os.environ.get(k, "") for k in keys}


@app.function(
    image=image,
    gpu=_GPU,
    cpu=4.0,
    memory=32768,
    timeout=28800,  # 8 h ceiling (T22, R-timeout)
    volumes={"/data": DATA_VOL, "/biofm_cache": BIOFM_VOL},
    secrets=[modal.Secret.from_dict(_env_secrets())],
)
def run_v05_sweep(
    *,
    norman_n_singletons: int = 15,
    norman_n_doublets: int = 5,
    adamson_n_per_bin: int = 7,  # 3 bins × 7 = ~21 TFs
    adamson_n_bins: int = 3,
    seeds: int = 3,
    r_sweep: tuple[int, ...] = _DEFAULT_R_SWEEP,
    backbones: tuple[str, ...] = _DEFAULT_BACKBONES,
    include_norman: bool = True,
    include_adamson: bool = True,
    max_tasks_override: int | None = None,
    doublet_delim: str = "_",
    n_top_hvg: int = 2000,
    max_cells_per_pert: int = 200,
    cooldown_sec: float = 60.0,
    temperature: float = 0.3,
    version: str = "v0.6.0",
    spend_stop_usd: float = 12.0,
    prior_spend_usd: float = 1.3548,
    git_sha: str = "",
    git_dirty: bool = False,
    run_id: str = "",
    llm_key_source: dict | None = None,
    preregistration: dict | None = None,
    preregistration_error: str | None = None,
) -> dict:
    """Run the v0.6.0 single-stage sweep on real Adamson + Norman data.

    ``git_sha`` / ``git_dirty`` / ``run_id`` are computed on the host by the
    local entrypoint (the container has no ``.git``); a direct ``.remote()``
    call without them fails closed in ``build_provenance``. Likewise
    ``llm_key_source`` (parsed from ``LLM_KEY_SOURCE``) and
    ``preregistration`` (or ``preregistration_error``) are host-computed; the
    preflight refuses the run when either is missing (principal directive
    2026-09-24, CTO #265).

    Spend (CTO #283): both sweep loops stop as soon as :func:`spend_guard`
    trips — ``spend_stop_usd`` (default $12, stop and report) or the $28 hard
    kill. A stopped run finalises provenance ``status="partial"`` with
    ``stop_reason`` and ``cost_usd_at_stop``.

    Returns
    -------
    dict
        Summary: ``{run_id, status, n_trainer_runs, n_lifecycle_runs,
        gpu_seconds, gpu_seconds_source, total_cost_usd, started_at, finished_at}``.
    """
    # Every resolved kwarg, captured before any other local is bound (T13).
    resolved_kwargs = dict(locals())
    started_at = time.time()

    import datetime as _dt
    import hashlib

    from perturb_eval.agentic_lifecycle.llm_agent_pool import LLMAgentPool
    from perturb_eval.backbones.scgpt_small import training_device
    from perturb_eval.data.download import fetch_adamson_all, fetch_norman
    from perturb_eval.data.subsample import mean_abs_logfc_per_target
    from perturb_eval.experiments.e2_adamson import load_adamson_combined
    from perturb_eval.experiments.heldout import iter_trainer_records, trainer_grid
    from perturb_eval.experiments.norman import load_norman_matrix
    from perturb_eval.experiments.v05_preflight import preflight
    from perturb_eval.experiments.v05_sweep import (
        LIFECYCLE_N_ROUNDS,
        derive_status,
        iter_lifecycle_records,
        llm_cache_end,
        llm_cache_start,
        provenance_entropies,
        run_guarded,
        spend_guard,
        version_out_dir,
    )
    from perturb_eval.experiments.v05_tasks import build_task_lists
    from perturb_eval.experiments.provenance import (
        build_provenance,
        collect_hvg_and_params,
        fail_provenance,
        finalize_provenance,
        jsonl_provenance_line,
        read_jsonl_locating,
        scan_unparseable,
    )
    from perturb_eval.llm.anthropic_client import ANTHROPIC_POOL, AnthropicClient
    from perturb_eval.llm.openrouter_client import versioned_cache_dir

    # QG C22: --version is a release tag and the output stays under /data.
    out_dir = version_out_dir(version)
    trainer_out = out_dir / "trainer_runs.jsonl"
    lifecycle_out = out_dir / "lifecycle_runs.jsonl"
    provenance_out = out_dir / "provenance.json"

    # A4-1: sampling is fixed per model in the Anthropic client (Haiku temperature = the
    # entrypoint `temperature`, 0.3 by default; Sonnet 5.5 at API defaults).

    def _iso(ts: float) -> str:
        return _dt.datetime.fromtimestamp(ts, _dt.timezone.utc).isoformat()

    def _sha256(path: Path) -> str:
        h = hashlib.sha256()
        with Path(path).open("rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()

    # QG-2 (relaunch gate; CTO #467): actual spend = GPU wall-clock + the LLM
    # bill (AnthropicClient.spend_usd: usage × the pinned price table) + spend
    # carried in from an aborted run. Both guards apply to the total.
    llm_state: dict = {"client": None, "llm_cost_usd": 0.0}

    def _gpu_cost_usd() -> float:
        return (time.time() - started_at) / 3600.0 * _A100_HOURLY_USD

    def _llm_cost_usd() -> float:
        # A4-2: API-reported usage x the pinned price table, accumulated per call, plus the
        # preflight probes' billed calls (QG-7).
        client = llm_state["client"]
        run_part = float(client.spend_usd) if client is not None else 0.0
        llm_state["llm_cost_usd"] = run_part + float(llm_state.get("preflight_spend_usd") or 0.0)
        return llm_state["llm_cost_usd"]

    def _spend_breakdown() -> dict:
        # QG-3: one helper for the success AND the abort path, so a refusal's category, the
        # per-call usage, the ceilings and the price table always reach provenance.json.
        client = llm_state["client"]
        llm_report = client.spend() if client is not None else {}
        return {
            "gpu_cost_usd": _gpu_cost_usd(),
            "llm_cost_usd": _llm_cost_usd(),
            "prior_spend_usd": prior_spend_usd,
            "preflight_spend_usd": float(llm_state.get("preflight_spend_usd") or 0.0),
            "preflight_probe_spend": llm_state.get("preflight_spend_report") or {},
            "llm_report": {k: v for k, v in llm_report.items() if k != "price_table"},
            "llm_price_table": llm_report.get("price_table"),
            "llm_call_log": list(client.call_log) if client is not None else [],
        }

    def _cost_usd_so_far() -> float:
        return _gpu_cost_usd() + _llm_cost_usd() + prior_spend_usd

    def _budget_exceeded() -> bool:
        return _cost_usd_so_far() > _BUDGET_HARD_KILL_USD

    # Refuse a spend stop above the kill before any work (spend_guard raises).
    spend_guard(0.0, stop_usd=spend_stop_usd, kill_usd=_BUDGET_HARD_KILL_USD)

    # CTO #283 / OWN-1: the loops' should_stop. The first trip is latched with
    # the spend at that moment; later calls keep returning True.
    stop_state: dict = {"reason": None, "cost_usd": None}

    def _should_stop() -> bool:
        if stop_state["reason"] is not None:
            return True
        cost = _cost_usd_so_far()
        reason = spend_guard(cost, stop_usd=spend_stop_usd, kill_usd=_BUDGET_HARD_KILL_USD)
        if reason is not None:
            stop_state.update(reason=reason, cost_usd=cost)
            print(
                f"[v0.6.0] SPEND {reason}: ${cost:.2f} > "
                f"${spend_stop_usd if reason == 'spend_stop' else _BUDGET_HARD_KILL_USD:.2f}"
                " — stopping and reporting"
            )
            return True
        return False

    def _append(path: Path, rec: dict) -> None:
        # Atomic-ish append: build line, open-append, flush.
        line = json.dumps(rec, default=str)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
            fh.flush()
        DATA_VOL.commit()

    # ---------- 0. Preflight (T22) — before any GPU/model work ----------
    # Every check is collected and raised once as PreflightError: key presence
    # + pool probe (C-KEY-1), backbones available (C-TORCH-1), output dir empty,
    # datasets fetched with digest verification (trust_unpinned=False), task
    # plan built (build_task_lists asserts stratum counts), every task resolves.
    # A missing key refuses the WHOLE run — no trainer-only run (CTO #235).
    data_dir = Path("/data/datasets")
    data_dir.mkdir(parents=True, exist_ok=True)
    dataset_records: list[dict] = []

    def _load_adamson() -> dict:
        adamson_paths = fetch_adamson_all(dest_dir=data_dir, trust_unpinned=False)
        adamson_files = [adamson_paths[k] for k in sorted(adamson_paths)]
        ds = load_adamson_combined(
            adamson_files,
            n_top_hvg=n_top_hvg,
            max_cells_per_pert=max_cells_per_pert,
        )
        dataset_records.append(
            {
                "name": "adamson_full",
                "path": [str(f) for f in adamson_files],
                "sha256": [_sha256(f) for f in adamson_files],
                "n_cells": int(ds["X"].shape[0]),
                "n_genes": int(ds["X"].shape[1]),
                # CTO #250: the label contract this load applied (aliases + evidence).
                "label_contract": ds["label_contract"],
                # CTO #253: plasmids pooled into each single-gene task.
                "guides_per_gene": ds["guides_per_gene"],
            }
        )
        return ds

    def _load_norman() -> dict:
        norman_path = fetch_norman(dest_dir=data_dir, trust_unpinned=False)
        ds = load_norman_matrix(
            norman_path, n_top_hvg=n_top_hvg, max_cells_per_pert=max_cells_per_pert
        )
        dataset_records.append(
            {
                "name": "norman",
                "path": str(norman_path),
                "sha256": _sha256(norman_path),
                "n_cells": int(ds["X"].shape[0]),
                "n_genes": int(ds["X"].shape[1]),
                # CTO #250: the label contract this load applied (aliases + evidence).
                "label_contract": ds["label_contract"],
            }
        )
        return ds

    dataset_sources: dict = {}
    if include_adamson:
        dataset_sources["adamson_full"] = _load_adamson
    if include_norman:
        dataset_sources["norman"] = _load_norman

    def _build_plan(loaded: dict):
        # Per-target |logFC| on the combined Adamson dataset -> quantile strata;
        # the pure, deterministic build_task_lists (T2/T11) asserts the counts.
        adamson_summary: dict[str, dict[str, float]] = {}
        if "adamson_full" in loaded:
            a = loaded["adamson_full"]
            adamson_summary["adamson_full"] = mean_abs_logfc_per_target(
                a["X"], a["labels"], a["control_mask"], a["target_gene_idx"]
            )
        norman_labels = list(loaded["norman"]["perturbations"]) if "norman" in loaded else []
        return build_task_lists(
            adamson_summary,
            norman_labels,
            norman_n_singletons=norman_n_singletons,
            norman_n_doublets=norman_n_doublets,
            adamson_n_per_bin=adamson_n_per_bin,
            adamson_n_bins=adamson_n_bins,
            seed=2026,
            doublet_delim=doublet_delim,
        )

    report = preflight(
        kwargs=resolved_kwargs,
        datasets_spec_or_loaded=dataset_sources,
        task_plan=_build_plan,
        env=os.environ,
        out_dir=out_dir,
    )
    print(f"[v0.6.0] preflight ok: {len(report.checks)} checks; probe={report.probe_model_id}")
    # QG-7: the probes are billed calls; they join the run's LLM spend and provenance.
    llm_state["preflight_spend_usd"] = float((report.probe_spend or {}).get("spend_usd") or 0.0)
    llm_state["preflight_spend_report"] = dict(report.probe_spend or {})
    n_live = sum(1 for e in report.roster_liveness.values() if e["live"])
    print(f"[v0.6.0] roster liveness: {n_live}/{len(report.roster_liveness)} live (CTO #467)")
    task_plan = report.task_plan
    # A2-8: the version-namespaced LLM cache and its entry count at sweep start
    # (must be 0 for the pre-registered run; recorded, and a non-zero count
    # makes the run a replay — see llm_cache_end at finalisation).
    llm_cache = llm_cache_start(Path(_LLM_CACHE_DIR))
    print(f"[v0.6.0] llm cache: {llm_cache}")
    adamson_ds = report.datasets.get("adamson_full")
    norman_ds = report.datasets.get("norman")
    out_dir.mkdir(parents=True, exist_ok=True)

    datasets: list[tuple[str, dict, list[str]]] = []

    if adamson_ds is not None:
        adamson_tasks = list(task_plan.adamson)
        datasets.append(("adamson_full", adamson_ds, adamson_tasks))
        print(
            f"[v0.6.0] adamson loaded: {task_plan.eligible_counts['adamson']} TFs "
            f"total, subsampled to {len(adamson_tasks)} stratified by |logFC|"
        )

    if norman_ds is not None:
        norman_tasks = sorted(list(task_plan.norman_singletons) + list(task_plan.norman_doublets))
        datasets.append(("norman", norman_ds, norman_tasks))
        print(f"[v0.6.0] norman subsampled: {len(norman_tasks)} tasks")

    # ---------- 1b. Provenance record 0 (T13/T14) ----------
    tasks_excluded: list[dict] = []
    for dataset_name, ds, tasks in datasets:
        for i, t in enumerate(tasks):
            if max_tasks_override is not None and i >= max_tasks_override:
                tasks_excluded.append(
                    {
                        "dataset": dataset_name,
                        "label": t,
                        "reason": f"max_tasks_override={max_tasks_override}",
                    }
                )
    prov = build_provenance(
        run_id=run_id,
        git_sha=git_sha,
        git_dirty=git_dirty,
        entrypoint_kwargs=resolved_kwargs,
        datasets=dataset_records,
        task_plan=task_plan,
        tasks_excluded=tasks_excluded,
        # CTO #250: labels the contract excluded, tagged with their dataset.
        labels_excluded=report.labels_excluded,
        llm_pool=[m.model_id for m in ANTHROPIC_POOL.models],
        llm_roster_liveness=report.roster_liveness,  # CTO #467: probe date + verdict per id
        gpu=_GPU,
        hourly_usd=_A100_HOURLY_USD,
        budget_cap_usd=_BUDGET_HARD_KILL_USD,
        started_at=_iso(started_at),
        llm_key_source=llm_key_source,
        preregistration=preregistration,
        device=training_device(),  # QG C9: the device every scgpt_small fit uses
        llm_cache_dir=_LLM_CACHE_DIR,  # QG C6
        # A2-4: the grid as run — records per task, distinct fits, seeds.
        trainer_grid=trainer_grid(
            backbones=backbones, r_sweep=r_sweep, seeds=list(range(2026, 2026 + seeds))
        ),
    )
    # A2-8 / A2-2: prereg_version, the cache namespace + entry count at start,
    # and the fixed round count go into record 0 of both JSONLs.
    prov.update(llm_cache)
    prov["lifecycle_n_rounds"] = LIFECYCLE_N_ROUNDS
    prov_line = jsonl_provenance_line(prov)
    for _p in (trainer_out, lifecycle_out):
        _p.write_text(prov_line + "\n", encoding="utf-8")
    provenance_out.write_text(json.dumps(prov, indent=2, default=str))
    DATA_VOL.commit()
    trainer_records: list[dict] = []
    lifecycle_records: list[dict] = []

    def _abort(phase: str):
        # CTO #245 Q1: a non-transient exception in either sweep loop aborts the
        # run. Finalise provenance as "failed" with type + traceback, then the
        # caller (run_guarded) re-raises.
        def on_abort(exc: BaseException) -> None:
            now = time.time()
            hvg_n, params = collect_hvg_and_params(trainer_records, lifecycle_records)
            failed = fail_provenance(
                prov,
                exc,
                phase=phase,
                finished_at=_iso(now),
                gpu_seconds=now - started_at,
                gpu_seconds_source="wall_clock_of_gpu_function",
                cost_usd_actual=_cost_usd_so_far(),
                counts={
                    "n_trainer_runs": len(trainer_records),
                    "n_lifecycle_runs": len(lifecycle_records),
                },
                hvg_n_per_task=hvg_n,
                params_per_task=params,
                budget_hit=_budget_exceeded(),
                unparseable_lines=scan_unparseable(trainer_out, lifecycle_out),
                stop_reason=stop_state["reason"],
                cost_usd_at_stop=stop_state["cost_usd"],
            )
            failed.update(
                llm_cache_end(
                    lifecycle_records, entries_at_start=llm_cache["llm_cache_entries_at_start"]
                )
            )
            failed.update(_spend_breakdown())  # QG-3: never lose the call log on an abort
            provenance_out.write_text(json.dumps(failed, indent=2, default=str))
            DATA_VOL.commit()
            print(
                f"[v0.6.0] ABORT in {phase}: {failed['failure']['error_type']} — "
                "provenance status=failed"
            )

        return on_abort

    def _sink(path: Path, bucket: list[dict]):
        def sink(rec: dict) -> None:
            _append(path, rec)
            bucket.append(rec)

        return sink

    # ---------- 2. Trainer-only sweep ----------
    print(f"[v0.6.0] trainer sweep start; budget_so_far=${_cost_usd_so_far():.3f}")
    # T8b: the loop body lives in perturb_eval.experiments.heldout so it is
    # testable; HVG is selected per held-out task on training cells only and
    # each record carries hvg_n / hvg_n_forced / hvg_mode / n_params.
    # CTO #245 Q1: transient per-cell failures become error records; anything
    # else aborts the run via run_guarded (provenance status "failed").
    n_trainer_runs = 0
    for dataset_name, ds, tasks in datasets:
        if max_tasks_override is not None:
            tasks = tasks[:max_tasks_override]
        n_trainer_runs += run_guarded(
            iter_trainer_records(
                dataset_name=dataset_name,
                ds=ds,
                tasks=tasks,
                backbones=backbones,
                r_sweep=r_sweep,
                seeds=range(2026, 2026 + seeds),
                should_stop=_should_stop,
            ),
            sink=_sink(trainer_out, trainer_records),
            on_abort=_abort("trainer"),
        )
        if _should_stop():
            print(
                f"[v0.6.0] spend guard tripped ({stop_state['reason']} at "
                f"${stop_state['cost_usd']:.2f}) — stopping trainer sweep"
            )
            break
    print(
        f"[v0.6.0] trainer sweep done: {n_trainer_runs} runs; "
        f"budget_so_far=${_cost_usd_so_far():.3f}"
    )

    # ---------- 3. Lifecycle sweep (real LLMAgentPool, free-tier) ----------
    # Preflight asserted key presence + a live pool (C-KEY-1); no skip path.
    api_key = os.environ["ANTHROPIC_API_KEY"]
    # A2-8: the client reads and writes ONLY the version namespace.
    llm_cache_ns = versioned_cache_dir(Path(_LLM_CACHE_DIR))
    # A4-1: Anthropic roster; Haiku at the entrypoint temperature (0.3, as the OpenRouter
    # runs), Sonnet 5.5 at API defaults; ceilings + price table from the client module.
    from perturb_eval.llm.anthropic_client import HAIKU, SAMPLING

    sampling = {k: dict(v) for k, v in SAMPLING.items()}
    sampling[HAIKU] = {"temperature": temperature}
    client = AnthropicClient(
        api_key=api_key,
        cache_dir=llm_cache_ns,
        pool=ANTHROPIC_POOL,
        cooldown_sec=cooldown_sec,
        max_wait_sec=300.0,
        sampling=sampling,
    )
    pool = LLMAgentPool(client=client, cache_dir=llm_cache_ns)
    llm_state["client"] = client
    print(
        f"[v0.6.0] llm client: Anthropic roster {[m.model_id for m in ANTHROPIC_POOL.models]}; spend meter = usage x price table"
    )

    def _lifecycle_sink(path: Path, bucket: list[dict]):
        base = _sink(path, bucket)

        def sink(rec: dict) -> None:
            base(rec)
            # QG-4: a fallback step already invalidates the run (A2-1 / C-KEY-2);
            # latch the stop so no more GPU-hours are spent on it.
            if stop_state["reason"] is None and any(
                s.get("source") == "fallback" for s in (rec.get("steps") or [])
            ):
                stop_state.update(reason="fallback", cost_usd=_cost_usd_so_far())
                print(
                    f"[v0.6.0] first fallback step in {rec.get('task_id')!r} seed "
                    f"{rec.get('seed')!r} — run is invalid; stopping the lifecycle sweep"
                )

        return sink

    # T6 + CTO #245 Q1: the loop body lives in v05_sweep.iter_lifecycle_records
    # (testable); BackboneUnavailableError and every non-transient exception
    # propagate and abort the run; a task missing from target_gene_idx raises.
    n_lifecycle_runs = run_guarded(
        iter_lifecycle_records(
            datasets=[
                (name, ds, tasks[:max_tasks_override] if max_tasks_override is not None else tasks)
                for name, ds, tasks in datasets
            ],
            seeds=range(2026, 2026 + seeds),
            pool=pool,
            max_rounds=LIFECYCLE_N_ROUNDS,  # A2-2: exactly three rounds
            should_stop=_should_stop,
        ),
        sink=_lifecycle_sink(lifecycle_out, lifecycle_records),
        on_abort=_abort("lifecycle"),
    )

    # ---------- 4. Phase-2 gate re-check on real traces ----------
    # CTO #245 Q2: every unparseable line is LOCATED (line, byte offset,
    # preview) and written to provenance — never silently skipped. The
    # analyser refuses any run that has one.
    lifecycle_rows, _ = read_jsonl_locating(lifecycle_out)
    lifecycle_rows = [
        r for r in lifecycle_rows if isinstance(r, dict) and r.get("record_type") != "provenance"
    ]
    unparseable_lines = scan_unparseable(trainer_out, lifecycle_out)
    n_unparseable = sum(len(v) for v in unparseable_lines.values())
    if n_unparseable:
        print(f"[v0.6.0] WARNING: {n_unparseable} unparseable JSONL line(s): {unparseable_lines}")

    # QG C14: one producer — the analyser's LLM-only figures (None, not 0.0,
    # when no LLM-sourced Architect step carries the field).
    entropies = provenance_entropies(lifecycle_rows)

    finished_at = time.time()
    # Modal exposes no per-function GPU-seconds counter inside the container.
    # This whole function holds the A100 from entry to return, so GPU time is
    # MEASURED as the wall clock of this function and labelled as such.
    gpu_seconds = finished_at - started_at
    gpu_seconds_source = "wall_clock_of_gpu_function"
    cost_usd = _cost_usd_so_far()
    spend_breakdown = _spend_breakdown()
    budget_hit = cost_usd > _BUDGET_HARD_KILL_USD
    # C-KEY-2 fallback > spend stop / hard kill > ok (QG C14 / OWN-1).
    status = derive_status(
        lifecycle_rows,
        cost_usd=cost_usd,
        kill_usd=_BUDGET_HARD_KILL_USD,
        stop_reason=stop_state["reason"],
        llm_cache_entries_at_start=llm_cache["llm_cache_entries_at_start"],  # A2-8 replay
    )
    hvg_n_per_task, params_per_task = collect_hvg_and_params(trainer_records, lifecycle_records)
    counts = {
        "n_trainer_runs": n_trainer_runs,
        "n_lifecycle_runs": n_lifecycle_runs,
    }
    final = finalize_provenance(
        prov,
        finished_at=_iso(finished_at),
        gpu_seconds=gpu_seconds,
        gpu_seconds_source=gpu_seconds_source,
        cost_usd_actual=cost_usd,
        counts=counts,
        entropies=entropies,
        hvg_n_per_task=hvg_n_per_task,
        params_per_task=params_per_task,
        budget_hit=budget_hit,
        status=status,
        unparseable_lines=unparseable_lines,
        stop_reason=stop_state["reason"],
        cost_usd_at_stop=stop_state["cost_usd"],
    )
    # A2-8: cache-hit count (must be 0) and the replay flag.
    final.update(
        llm_cache_end(lifecycle_rows, entries_at_start=llm_cache["llm_cache_entries_at_start"])
    )
    final.update(spend_breakdown)  # QG-2
    provenance_out.write_text(json.dumps(final, indent=2, default=str))
    DATA_VOL.commit()
    summary = {
        "run_id": run_id,
        "status": status,
        "started_at": final["started_at"],
        "finished_at": final["finished_at"],
        "wall_clock_sec": final["wall_clock_sec"],
        "gpu_seconds": gpu_seconds,
        "gpu_seconds_source": gpu_seconds_source,
        "total_cost_usd": cost_usd,
        **{k: v for k, v in spend_breakdown.items() if k != "llm_call_log"},
        "llm_call_log_n": len(spend_breakdown["llm_call_log"]),
        "budget_cap_usd": _BUDGET_HARD_KILL_USD,
        "budget_hit": budget_hit,
        "spend_stop_usd": spend_stop_usd,
        "stop_reason": stop_state["reason"],
        "cost_usd_at_stop": stop_state["cost_usd"],
        "prereg_version": final["prereg_version"],
        "llm_cache_entries_at_start": final["llm_cache_entries_at_start"],
        "llm_cache_hit_count": final["llm_cache_hit_count"],
        "replay": final["replay"],
        **counts,
        **entropies,
    }
    print(json.dumps(summary, indent=2, default=str))
    return summary


@app.local_entrypoint()
def entrypoint(
    norman_n_singletons: int = 15,
    norman_n_doublets: int = 5,
    adamson_n_per_bin: int = 7,
    adamson_n_bins: int = 3,
    seeds: int = 3,
    include_norman: bool = True,
    include_adamson: bool = True,
    max_tasks_override: int | None = None,
    doublet_delim: str = "_",
    n_top_hvg: int = 2000,
    max_cells_per_pert: int = 200,
    cooldown_sec: float = 60.0,
    temperature: float = 0.3,
    version: str = "v0.6.0",
    spend_stop_usd: float = _SPEND_STOP_USD,
    prior_spend_usd: float = 1.3548,  # A4-2: aborted run 1.3 + authorised dry runs 0.0548
) -> None:
    import subprocess
    import sys

    src = PROJECT_DIR_HOST / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
    from perturb_eval.experiments.v05_sweep import validate_pinned_run_params, validate_version

    validate_version(version)  # QG C22: fail on the host, before any Modal work
    validate_pinned_run_params(
        version, temperature=temperature, prior_spend_usd=prior_spend_usd
    )  # A4-1/A4-2
    from perturb_eval.experiments.provenance import (
        git_state,
        make_run_id,
        parse_key_source,
        preregistration_record,
        write_run_config,
    )

    # Host side: the Modal container has no .git (T13).
    git_sha, git_dirty = git_state(PROJECT_DIR_HOST)
    run_id = make_run_id(git_sha)
    # Principal directive (2026-09-24): record WHERE the key came from, never the
    # key. Missing/malformed -> None, which the preflight refuses (C-KEY-SOURCE).
    llm_key_source = parse_key_source(os.environ.get("LLM_KEY_SOURCE"), home_project=_HOME_PROJECT)
    # CTO #265: pin the committed, clean pre-registration (C-PREREG otherwise).
    toplevel = subprocess.run(
        ["git", "-C", str(PROJECT_DIR_HOST), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    preregistration: dict | None = None
    preregistration_error: str | None = None
    try:
        preregistration = preregistration_record(toplevel, _PREREGISTRATION_REL)
    except ValueError as exc:
        preregistration_error = str(exc)
    # Every run_v05_sweep kwarg, passed explicitly so the config copy and the
    # provenance ``entrypoint_kwargs`` block are the same resolved set.
    sweep_kwargs = {
        "norman_n_singletons": norman_n_singletons,
        "norman_n_doublets": norman_n_doublets,
        "adamson_n_per_bin": adamson_n_per_bin,
        "adamson_n_bins": adamson_n_bins,
        "seeds": seeds,
        "r_sweep": _DEFAULT_R_SWEEP,
        "backbones": _DEFAULT_BACKBONES,
        "include_norman": include_norman,
        "include_adamson": include_adamson,
        "max_tasks_override": max_tasks_override,
        "doublet_delim": doublet_delim,
        "n_top_hvg": n_top_hvg,
        "max_cells_per_pert": max_cells_per_pert,
        "cooldown_sec": cooldown_sec,
        "temperature": temperature,
        "version": version,
        "spend_stop_usd": spend_stop_usd,
        "prior_spend_usd": prior_spend_usd,
        "git_sha": git_sha,
        "git_dirty": git_dirty,
        "run_id": run_id,
        "llm_key_source": llm_key_source,
        "preregistration": preregistration,
        "preregistration_error": preregistration_error,
    }
    cfg = write_run_config(PROJECT_DIR_HOST, run_id, sweep_kwargs, git_sha)  # T17
    print(f"[v0.6.0] run_id={run_id} git_dirty={git_dirty} config={cfg}")
    out = run_v05_sweep.remote(**sweep_kwargs)
    print(json.dumps(out, indent=2, default=str))
