"""v0.5.0 single-stage Modal sweep: real Adamson + Norman, A100, budget-capped.

Design:
  * A100-40G ($1.32/hr Modal) with hard kill at $28.
  * Data pulled in by the script (Phase 1 fetchers) — no manual h5ad.
  * Adamson uses all 3 scPerturb subsets (pilot + 10X005 + 10X010) via
    ``load_adamson_combined``, then stratified-subsampled to ~20 TFs by
    mean |logFC| quantile.
  * Norman stratified-subsampled (fair, seed=2026).
  * Trainer sweep: ``n_tasks × {linear, mlp, scgpt_small} × N∈{3,5} ×
    R∈{1,2,3} × 3 seeds``. Atomic JSONL append for resume safety.
  * Lifecycle sweep: ``n_tasks × 3 seeds`` with the real OpenRouter
    LLMAgentPool (free-tier rotation; $0 LLM cost).

Deploy + run::

    set -a; source .env; set +a
    cd projects/perturb-seq-eval
    modal deploy scripts/modal/app_v05.py
    modal run scripts/modal/app_v05.py::entrypoint \\
        --norman-n-singletons 15 --norman-n-doublets 5 --seeds 3

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
_GPU = "A100-40GB"

# Sweep-shape defaults shared by ``run_v05_sweep`` and the host entrypoint so the
# entrypoint can pass (and record) every resolved kwarg explicitly.
_DEFAULT_N_SWEEP: tuple[int, ...] = (3, 5)
_DEFAULT_R_SWEEP: tuple[int, ...] = (1, 2, 3)
_DEFAULT_BACKBONES: tuple[str, ...] = ("linear", "mlp", "scgpt_small")


def _env_secrets() -> dict[str, str]:
    keys = ("OPENROUTER_API_KEY",)
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
    n_sweep: tuple[int, ...] = _DEFAULT_N_SWEEP,
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
    git_sha: str = "",
    git_dirty: bool = False,
    run_id: str = "",
) -> dict:
    """Run the v0.5.0 single-stage sweep on real Adamson + Norman data.

    ``git_sha`` / ``git_dirty`` / ``run_id`` are computed on the host by the
    local entrypoint (the container has no ``.git``); a direct ``.remote()``
    call without them fails closed in ``build_provenance``.

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
    import inspect

    from perturb_eval.agentic_lifecycle.freedom_probe import (
        per_agent_field_entropy,
        summarise_choice_distribution,
    )
    from perturb_eval.agentic_lifecycle.llm_agent_pool import LLMAgentPool
    from perturb_eval.data.download import fetch_adamson_all, fetch_norman
    from perturb_eval.data.subsample import mean_abs_logfc_per_target
    from perturb_eval.experiments.e2_adamson import load_adamson_combined
    from perturb_eval.experiments.heldout import iter_trainer_records
    from perturb_eval.experiments.norman import load_norman_matrix
    from perturb_eval.experiments.v05_preflight import preflight
    from perturb_eval.experiments.v05_sweep import iter_lifecycle_records, run_guarded
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
    from perturb_eval.llm.openrouter_client import DEFAULT_POOL, OpenRouterClient

    out_dir = Path(f"/data/{version}")
    trainer_out = out_dir / "trainer_runs.jsonl"
    lifecycle_out = out_dir / "lifecycle_runs.jsonl"
    provenance_out = out_dir / "provenance.json"

    # OpenRouterClient currently hardcodes temperature=0.3 in its request body.
    # Pass the kwarg through if the client accepts it; otherwise refuse any value
    # the client would silently ignore.
    _client_params = inspect.signature(OpenRouterClient.__init__).parameters
    _client_takes_temperature = "temperature" in _client_params
    if not _client_takes_temperature and temperature != 0.3:
        raise ValueError(
            f"temperature={temperature} requested but OpenRouterClient does not accept a "
            "temperature (hardcoded 0.3)"
        )

    def _iso(ts: float) -> str:
        return _dt.datetime.fromtimestamp(ts, _dt.timezone.utc).isoformat()

    def _sha256(path: Path) -> str:
        h = hashlib.sha256()
        with Path(path).open("rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()

    def _cost_usd_so_far() -> float:
        return (time.time() - started_at) / 3600.0 * _A100_HOURLY_USD

    def _budget_exceeded() -> bool:
        return _cost_usd_so_far() > _BUDGET_HARD_KILL_USD

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
        dataset_records.append({
            "name": "adamson_full",
            "path": [str(f) for f in adamson_files],
            "sha256": [_sha256(f) for f in adamson_files],
            "n_cells": int(ds["X"].shape[0]),
            "n_genes": int(ds["X"].shape[1]),
            # CTO #250: the label contract this load applied (aliases + evidence).
            "label_contract": ds["label_contract"],
        })
        return ds

    def _load_norman() -> dict:
        norman_path = fetch_norman(dest_dir=data_dir, trust_unpinned=False)
        ds = load_norman_matrix(
            norman_path, n_top_hvg=n_top_hvg, max_cells_per_pert=max_cells_per_pert
        )
        dataset_records.append({
            "name": "norman",
            "path": str(norman_path),
            "sha256": _sha256(norman_path),
            "n_cells": int(ds["X"].shape[0]),
            "n_genes": int(ds["X"].shape[1]),
            # CTO #250: the label contract this load applied (aliases + evidence).
            "label_contract": ds["label_contract"],
        })
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
    print(f"[v0.6] preflight ok: {len(report.checks)} checks; probe={report.probe_model_id}")
    task_plan = report.task_plan
    adamson_ds = report.datasets.get("adamson_full")
    norman_ds = report.datasets.get("norman")
    out_dir.mkdir(parents=True, exist_ok=True)

    datasets: list[tuple[str, dict, list[str]]] = []

    if adamson_ds is not None:
        adamson_tasks = list(task_plan.adamson)
        datasets.append(("adamson_full", adamson_ds, adamson_tasks))
        print(
            f"[v0.5.0] adamson loaded: {task_plan.eligible_counts['adamson']} TFs "
            f"total, subsampled to {len(adamson_tasks)} stratified by |logFC|"
        )

    if norman_ds is not None:
        norman_tasks = sorted(
            list(task_plan.norman_singletons) + list(task_plan.norman_doublets)
        )
        datasets.append(("norman", norman_ds, norman_tasks))
        print(f"[v0.5.0] norman subsampled: {len(norman_tasks)} tasks")

    # ---------- 1b. Provenance record 0 (T13/T14) ----------
    tasks_excluded: list[dict] = []
    for dataset_name, ds, tasks in datasets:
        for i, t in enumerate(tasks):
            if max_tasks_override is not None and i >= max_tasks_override:
                tasks_excluded.append({"dataset": dataset_name, "label": t,
                                       "reason": f"max_tasks_override={max_tasks_override}"})
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
        llm_pool=[m.model_id for m in DEFAULT_POOL.models],
        gpu=_GPU,
        hourly_usd=_A100_HOURLY_USD,
        budget_cap_usd=_BUDGET_HARD_KILL_USD,
        started_at=_iso(started_at),
    )
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
                counts={"n_trainer_runs": len(trainer_records),
                        "n_lifecycle_runs": len(lifecycle_records)},
                hvg_n_per_task=hvg_n,
                params_per_task=params,
                budget_hit=_budget_exceeded(),
                unparseable_lines=scan_unparseable(trainer_out, lifecycle_out),
            )
            provenance_out.write_text(json.dumps(failed, indent=2, default=str))
            DATA_VOL.commit()
            print(f"[v0.6] ABORT in {phase}: {failed['failure']['error_type']} — "
                  "provenance status=failed")
        return on_abort

    def _sink(path: Path, bucket: list[dict]):
        def sink(rec: dict) -> None:
            _append(path, rec)
            bucket.append(rec)
        return sink

    # ---------- 2. Trainer-only sweep ----------
    print(f"[v0.5.0] trainer sweep start; budget_so_far=${_cost_usd_so_far():.3f}")
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
                n_sweep=n_sweep,
                r_sweep=r_sweep,
                seeds=range(2026, 2026 + seeds),
                should_stop=_budget_exceeded,
            ),
            sink=_sink(trainer_out, trainer_records),
            on_abort=_abort("trainer"),
        )
        if _budget_exceeded():
            print(
                f"[v0.5.0] budget cap hit (${_cost_usd_so_far():.2f})"
                " — stopping trainer sweep"
            )
            break
    print(
        f"[v0.5.0] trainer sweep done: {n_trainer_runs} runs; "
        f"budget_so_far=${_cost_usd_so_far():.3f}"
    )

    # ---------- 3. Lifecycle sweep (real LLMAgentPool, free-tier) ----------
    # Preflight asserted key presence + a live pool (C-KEY-1); no skip path.
    api_key = os.environ["OPENROUTER_API_KEY"]
    client_kwargs: dict = {"cooldown_sec": cooldown_sec}
    if _client_takes_temperature:
        client_kwargs["temperature"] = temperature
    client = OpenRouterClient(
        api_key=api_key,
        cache_dir=Path("/biofm_cache/llm"),
        pool=DEFAULT_POOL,
        **client_kwargs,
    )
    pool = LLMAgentPool(client=client, cache_dir=Path("/biofm_cache/llm"))

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
            max_rounds=3,
            should_stop=_budget_exceeded,
        ),
        sink=_sink(lifecycle_out, lifecycle_records),
        on_abort=_abort("lifecycle"),
    )

    # ---------- 4. Phase-2 gate re-check on real traces ----------
    # CTO #245 Q2: every unparseable line is LOCATED (line, byte offset,
    # preview) and written to provenance — never silently skipped. The
    # analyser refuses any run that has one.
    traces: list[list[dict]] = []
    lifecycle_rows, _ = read_jsonl_locating(lifecycle_out)
    for rec in lifecycle_rows:
        if not isinstance(rec, dict) or rec.get("record_type") == "provenance":
            continue
        traces.append(list(rec.get("steps", [])))
    unparseable_lines = scan_unparseable(trainer_out, lifecycle_out)
    n_unparseable = sum(len(v) for v in unparseable_lines.values())
    if n_unparseable:
        print(f"[v0.6] WARNING: {n_unparseable} unparseable JSONL line(s): {unparseable_lines}")

    h_backbone = (
        per_agent_field_entropy(traces, agent="Architect", field="backbone")
        if traces else 0.0
    )
    h_hvg = (
        per_agent_field_entropy(traces, agent="Architect", field="hvg_count")
        if traces else 0.0
    )
    bb_dist = (
        summarise_choice_distribution(traces, agent="Architect", field="backbone")
        if traces else {}
    )

    finished_at = time.time()
    # Modal exposes no per-function GPU-seconds counter inside the container.
    # This whole function holds the A100 from entry to return, so GPU time is
    # MEASURED as the wall clock of this function and labelled as such.
    gpu_seconds = finished_at - started_at
    gpu_seconds_source = "wall_clock_of_gpu_function"
    cost_usd = _cost_usd_so_far()
    budget_hit = cost_usd > _BUDGET_HARD_KILL_USD
    any_fallback = any(
        isinstance(s, dict) and s.get("source") == "fallback"
        for t in traces for s in t
    )
    if any_fallback:
        status = "failed_fallback"  # C-KEY-2
    elif budget_hit:
        status = "partial"
    else:
        status = "ok"
    hvg_n_per_task, params_per_task = collect_hvg_and_params(
        trainer_records, lifecycle_records
    )
    entropies = {
        "architect_backbone_entropy_nats": float(h_backbone),
        "architect_hvg_entropy_nats": float(h_hvg),
        "architect_backbone_distribution": bb_dist,
    }
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
    )
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
        "budget_cap_usd": _BUDGET_HARD_KILL_USD,
        "budget_hit": budget_hit,
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
) -> None:
    import sys

    src = PROJECT_DIR_HOST / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
    from perturb_eval.experiments.provenance import (
        git_state,
        make_run_id,
        write_run_config,
    )

    # Host side: the Modal container has no .git (T13).
    git_sha, git_dirty = git_state(PROJECT_DIR_HOST)
    run_id = make_run_id(git_sha)
    # Every run_v05_sweep kwarg, passed explicitly so the config copy and the
    # provenance ``entrypoint_kwargs`` block are the same resolved set.
    sweep_kwargs = {
        "norman_n_singletons": norman_n_singletons,
        "norman_n_doublets": norman_n_doublets,
        "adamson_n_per_bin": adamson_n_per_bin,
        "adamson_n_bins": adamson_n_bins,
        "seeds": seeds,
        "n_sweep": _DEFAULT_N_SWEEP,
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
        "git_sha": git_sha,
        "git_dirty": git_dirty,
        "run_id": run_id,
    }
    cfg = write_run_config(PROJECT_DIR_HOST, run_id, sweep_kwargs, git_sha)  # T17
    print(f"[v0.6] run_id={run_id} git_dirty={git_dirty} config={cfg}")
    out = run_v05_sweep.remote(**sweep_kwargs)
    print(json.dumps(out, indent=2, default=str))
