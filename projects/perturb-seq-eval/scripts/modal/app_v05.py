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
``/data/v0.5.0/``. Download with::

    modal volume get perturb-eval-data /v0.5.0/runs.jsonl \\
        ./artifacts/v0.5.0/runs.jsonl --force
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import asdict
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
        "h5py>=3.10",
        "anndata>=0.10",
        "scikit-learn>=1.3",
        "torch>=2.2",
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


def _env_secrets() -> dict[str, str]:
    keys = ("OPENROUTER_API_KEY",)
    return {k: os.environ.get(k, "") for k in keys}


@app.function(
    image=image,
    gpu="A100-40GB",
    cpu=4.0,
    memory=32768,
    timeout=21600,  # 6 h ceiling
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
    n_sweep: tuple[int, ...] = (3, 5),
    r_sweep: tuple[int, ...] = (1, 2, 3),
    backbones: tuple[str, ...] = ("linear", "mlp", "scgpt_small"),
    include_norman: bool = True,
    include_adamson: bool = True,
    max_tasks_override: int | None = None,
) -> dict:
    """Run the v0.5.0 single-stage sweep on real Adamson + Norman data.

    Returns
    -------
    dict
        Provenance summary: ``{n_trainer_runs, n_lifecycle_runs,
        total_gpu_seconds, total_cost_usd, started_at, finished_at}``.
    """
    import numpy as np

    from perturb_eval.agentic_lifecycle.freedom_probe import (
        per_agent_field_entropy,
        summarise_choice_distribution,
    )
    from perturb_eval.agentic_lifecycle.llm_agent_pool import LLMAgentPool
    from perturb_eval.agentic_lifecycle.loop import run_agentic_lifecycle
    from perturb_eval.backbones import BackboneTrainConfig, build_backbone, mean_squared_deviation
    from perturb_eval.data.download import fetch_adamson_all, fetch_norman
    from perturb_eval.data.subsample import (
        mean_abs_logfc_per_target,
        stratified_subsample,
    )
    from perturb_eval.experiments.e2_adamson import load_adamson_combined
    from perturb_eval.experiments.norman import load_norman_matrix
    from perturb_eval.llm.openrouter_client import DEFAULT_POOL, OpenRouterClient

    out_dir = Path("/data/v0.5.0")
    out_dir.mkdir(parents=True, exist_ok=True)
    trainer_out = out_dir / "trainer_runs.jsonl"
    lifecycle_out = out_dir / "lifecycle_runs.jsonl"
    provenance_out = out_dir / "provenance.json"

    started_at = time.time()

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

    # ---------- 1. Data pull + subsample ----------
    data_dir = Path("/data/datasets")
    data_dir.mkdir(parents=True, exist_ok=True)

    datasets: list[tuple[str, dict, list[str]]] = []

    if include_adamson:
        adamson_paths = fetch_adamson_all(dest_dir=data_dir)
        adamson_ds = load_adamson_combined(
            list(adamson_paths.values()),
            n_top_hvg=2000,
            max_cells_per_pert=200,
        )
        # Stratify by per-target |logFC| into ``adamson_n_bins`` quantile
        # bins, then sample ``adamson_n_per_bin`` TFs per bin (seed=2026).
        logfc = mean_abs_logfc_per_target(
            adamson_ds["X"],
            adamson_ds["labels"],
            adamson_ds["control_mask"],
            adamson_ds["target_gene_idx"],
        )
        tfs = np.array(list(logfc.keys()))
        strengths = np.array([logfc[t] for t in tfs])
        if len(tfs) > adamson_n_per_bin * adamson_n_bins:
            bin_edges = np.quantile(strengths, np.linspace(0, 1, adamson_n_bins + 1))
            # digitize returns bin ids in [1..n_bins]; clamp to [0..n_bins-1].
            bin_ids = np.clip(np.digitize(strengths, bin_edges[1:-1]), 0, adamson_n_bins - 1)
            chosen_tfs = stratified_subsample(
                tfs, bin_ids, n_per_stratum=adamson_n_per_bin, seed=2026,
            )
            adamson_tasks = list(chosen_tfs)
        else:
            adamson_tasks = list(tfs)
        datasets.append(("adamson_full", adamson_ds, adamson_tasks))
        print(
            f"[v0.5.0] adamson loaded: {len(logfc)} TFs total, "
            f"subsampled to {len(adamson_tasks)} stratified by |logFC|"
        )

    if include_norman:
        norman_path = fetch_norman(dest_dir=data_dir)
        norman_ds = load_norman_matrix(
            norman_path, n_top_hvg=2000, max_cells_per_pert=200
        )
        # Stratify by "is_doublet" for fair balance.
        all_perts = np.array(list(norman_ds["perturbations"]))
        is_doublet = np.array([("+" in p) for p in all_perts])
        singletons = all_perts[~is_doublet]
        doublets = all_perts[is_doublet]

        chosen_singletons = stratified_subsample(
            singletons,
            strata=np.array([hash(s) % 3 for s in singletons]),
            n_per_stratum=max(1, norman_n_singletons // 3),
            seed=2026,
        )[:norman_n_singletons]
        chosen_doublets = stratified_subsample(
            doublets,
            strata=np.array([hash(s) % 2 for s in doublets]),
            n_per_stratum=max(1, norman_n_doublets // 2),
            seed=2026,
        )[:norman_n_doublets]
        norman_tasks = sorted(list(chosen_singletons) + list(chosen_doublets))
        datasets.append(("norman", norman_ds, norman_tasks))
        print(f"[v0.5.0] norman subsampled: {len(norman_tasks)} tasks")

    # ---------- 2. Trainer-only sweep ----------
    print(f"[v0.5.0] trainer sweep start; budget_so_far=${_cost_usd_so_far():.3f}")
    n_trainer_runs = 0
    for dataset_name, ds, tasks in datasets:
        if max_tasks_override is not None:
            tasks = tasks[:max_tasks_override]
        for backbone_name in backbones:
            for held in tasks:
                # Skip doublets for trainer-only (no single target_gene_idx).
                if held not in ds["target_gene_idx"]:
                    continue
                for N in n_sweep:
                    for R in r_sweep:
                        for seed in range(2026, 2026 + seeds):
                            if _budget_exceeded():
                                print(
                                    f"[v0.5.0] budget cap hit (${_cost_usd_so_far():.2f})"
                                    " — stopping trainer sweep"
                                )
                                break
                            t0 = time.time()
                            try:
                                train_mask = ds["labels"] != held
                                train_targets = {
                                    p: i for p, i in ds["target_gene_idx"].items()
                                    if p != held
                                }
                                bb = build_backbone(backbone_name)
                                bb.fit(
                                    ds["X"][train_mask],
                                    ds["labels"][train_mask].tolist(),
                                    ds["control_mask"][train_mask],
                                    train_targets,
                                    BackboneTrainConfig(
                                        max_iter=20 + 40 * R,
                                        learning_rate=1e-2,
                                        ridge_lambda=1.0,
                                        seed=seed,
                                    ),
                                )
                                target_idx = ds["target_gene_idx"][held]
                                n_genes = ds["X"].shape[1]
                                pred = bb.predict_logfc(
                                    held, target_idx, n_genes=n_genes
                                )
                                mask_p = ds["labels"] == held
                                mask_c = ds["control_mask"]
                                truth = np.mean(ds["X"][mask_p], axis=0) - np.mean(
                                    ds["X"][mask_c], axis=0
                                )
                                top_k = np.argsort(-np.abs(truth))[:20]
                                msd = float(mean_squared_deviation(pred, truth, top_k))
                                rec = {
                                    "dataset": dataset_name,
                                    "task": held,
                                    "backbone": backbone_name,
                                    "N": N,
                                    "R": R,
                                    "seed": seed,
                                    "msd_topk": msd,
                                    "wall_sec": time.time() - t0,
                                }
                            except Exception as e:  # noqa: BLE001
                                rec = {
                                    "dataset": dataset_name,
                                    "task": held,
                                    "backbone": backbone_name,
                                    "N": N, "R": R, "seed": seed,
                                    "msd_topk": float("inf"),
                                    "error": f"{type(e).__name__}: {e}",
                                    "wall_sec": time.time() - t0,
                                }
                            _append(trainer_out, rec)
                            n_trainer_runs += 1
                        if _budget_exceeded():
                            break
                    if _budget_exceeded():
                        break
                if _budget_exceeded():
                    break
            if _budget_exceeded():
                break
        if _budget_exceeded():
            break
    print(
        f"[v0.5.0] trainer sweep done: {n_trainer_runs} runs; "
        f"budget_so_far=${_cost_usd_so_far():.3f}"
    )

    # ---------- 3. Lifecycle sweep (real LLMAgentPool, free-tier) ----------
    n_lifecycle_runs = 0
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        print("[v0.5.0] WARNING: OPENROUTER_API_KEY not set; skipping lifecycle sweep")
    else:
        client = OpenRouterClient(
            api_key=api_key,
            cache_dir=Path("/biofm_cache/llm"),
            pool=DEFAULT_POOL,
            cooldown_sec=60.0,
        )
        pool = LLMAgentPool(client=client, cache_dir=Path("/biofm_cache/llm"))

        for dataset_name, ds, tasks in datasets:
            if max_tasks_override is not None:
                tasks = tasks[:max_tasks_override]
            for held in tasks:
                if held not in ds["target_gene_idx"]:
                    continue  # skip doublets; lifecycle target_idx picks a single gene
                for seed in range(2026, 2026 + seeds):
                    if _budget_exceeded():
                        break
                    t0 = time.time()
                    try:
                        run = run_agentic_lifecycle(
                            task_id=held,
                            X=ds["X"],
                            labels=ds["labels"],
                            control_mask=ds["control_mask"],
                            target_gene_idx=ds["target_gene_idx"],
                            held_out=held,
                            agent_pool=pool,
                            max_rounds=3,
                        )
                        rec = asdict(run) | {
                            "dataset": dataset_name,
                            "seed": seed,
                            "wall_sec": time.time() - t0,
                        }
                    except Exception as e:  # noqa: BLE001
                        rec = {
                            "dataset": dataset_name,
                            "task_id": held,
                            "seed": seed,
                            "error": f"{type(e).__name__}: {e}",
                            "final_msd_topk": float("inf"),
                            "n_rounds": 0,
                            "wall_sec": time.time() - t0,
                            "steps": [],
                        }
                    _append(lifecycle_out, rec)
                    n_lifecycle_runs += 1
                if _budget_exceeded():
                    break
            if _budget_exceeded():
                break

    # ---------- 4. Phase-2 gate re-check on real traces ----------
    traces: list[list[dict]] = []
    if lifecycle_out.exists():
        with lifecycle_out.open() as fh:
            for line in fh:
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                traces.append(list(rec.get("steps", [])))

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
    summary = {
        "started_at": started_at,
        "finished_at": finished_at,
        "wall_clock_sec": finished_at - started_at,
        "total_gpu_seconds": finished_at - started_at,  # entire fn ran on GPU
        "total_cost_usd": _cost_usd_so_far(),
        "budget_cap_usd": _BUDGET_HARD_KILL_USD,
        "n_trainer_runs": n_trainer_runs,
        "n_lifecycle_runs": n_lifecycle_runs,
        "architect_backbone_entropy_nats": float(h_backbone),
        "architect_hvg_entropy_nats": float(h_hvg),
        "architect_backbone_distribution": bb_dist,
    }
    provenance_out.write_text(json.dumps(summary, indent=2, default=str))
    DATA_VOL.commit()
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
) -> None:
    out = run_v05_sweep.remote(
        norman_n_singletons=norman_n_singletons,
        norman_n_doublets=norman_n_doublets,
        adamson_n_per_bin=adamson_n_per_bin,
        adamson_n_bins=adamson_n_bins,
        seeds=seeds,
        include_norman=include_norman,
        include_adamson=include_adamson,
        max_tasks_override=max_tasks_override,
    )
    print(json.dumps(out, indent=2, default=str))
