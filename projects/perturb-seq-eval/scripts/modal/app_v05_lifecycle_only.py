"""v0.5.0 lifecycle-only re-run.

Reuses the cached datasets in the ``perturb-eval-data`` volume from the
prior trainer sweep, skips the trainer phase entirely, and runs ONLY the
lifecycle sweep with the corrected free-tier model pool. Trainer JSONL
already on the volume stays intact; this overwrites
``/v0.5.0/lifecycle_runs.jsonl`` with the freshly-driven results.

Cost target: ~$1.50 (lifecycle has minimal GPU activity; LLM is free).

Run::

    set -a; source .env; set +a
    cd projects/perturb-seq-eval
    modal deploy scripts/modal/app_v05_lifecycle_only.py
    modal run --detach scripts/modal/app_v05_lifecycle_only.py::entrypoint
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

app = modal.App("perturb-eval-v050-lifecycle")
DATA_VOL = modal.Volume.from_name("perturb-eval-data", create_if_missing=True)
BIOFM_VOL = modal.Volume.from_name("biofm-cache", create_if_missing=True)


def _env_secrets() -> dict[str, str]:
    return {"OPENROUTER_API_KEY": os.environ.get("OPENROUTER_API_KEY", "")}


@app.function(
    image=image,
    gpu="A100-40GB",
    cpu=4.0,
    memory=32768,
    timeout=10800,  # 3 h ceiling — lifecycle should fit comfortably
    volumes={"/data": DATA_VOL, "/biofm_cache": BIOFM_VOL},
    secrets=[modal.Secret.from_dict(_env_secrets())],
)
def run_v05_lifecycle_only(
    *,
    seeds: int = 3,
    norman_n_singletons: int = 15,
    norman_n_doublets: int = 5,
    adamson_n_per_bin: int = 7,
    adamson_n_bins: int = 3,
) -> dict:
    """Run only the lifecycle sweep on cached datasets.

    Datasets MUST already be present at ``/data/datasets/*.h5ad`` from
    the prior trainer sweep.
    """
    import numpy as np

    from perturb_eval.agentic_lifecycle.freedom_probe import (
        per_agent_field_entropy,
        summarise_choice_distribution,
    )
    from perturb_eval.agentic_lifecycle.llm_agent_pool import LLMAgentPool
    from perturb_eval.agentic_lifecycle.loop import run_agentic_lifecycle
    from perturb_eval.data.subsample import (
        mean_abs_logfc_per_target,
        stratified_subsample,
    )
    from perturb_eval.experiments.e2_adamson import load_adamson_combined
    from perturb_eval.experiments.norman import load_norman_matrix
    from perturb_eval.llm.openrouter_client import DEFAULT_POOL, OpenRouterClient

    out_dir = Path("/data/v0.5.0")
    out_dir.mkdir(parents=True, exist_ok=True)
    lifecycle_out = out_dir / "lifecycle_runs.jsonl"
    provenance_out = out_dir / "provenance.json"

    # Wipe stale rule-based fallback lifecycle file.
    if lifecycle_out.exists():
        lifecycle_out.unlink()

    started_at = time.time()

    def _append(rec: dict) -> None:
        line = json.dumps(rec, default=str)
        with lifecycle_out.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
            fh.flush()
        DATA_VOL.commit()

    # ---------- 1. Reload datasets (cached on volume) ----------
    data_dir = Path("/data/datasets")
    adamson_paths = sorted(data_dir.glob("Adamson2016_*.h5ad"))
    norman_path = data_dir / "NormanWeissman2019_filtered.h5ad"
    if not adamson_paths or not norman_path.exists():
        raise FileNotFoundError(
            f"Expected datasets in {data_dir}: adamson={adamson_paths}, norman={norman_path}"
        )

    adamson_ds = load_adamson_combined(
        list(adamson_paths), n_top_hvg=2000, max_cells_per_pert=200
    )
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
        bin_ids = np.clip(np.digitize(strengths, bin_edges[1:-1]), 0, adamson_n_bins - 1)
        chosen_tfs = stratified_subsample(
            tfs, bin_ids, n_per_stratum=adamson_n_per_bin, seed=2026,
        )
        adamson_tasks = list(chosen_tfs)
    else:
        adamson_tasks = list(tfs)
    print(f"[v0.5.0-lc] adamson: {len(adamson_tasks)} tasks")

    norman_ds = load_norman_matrix(norman_path, n_top_hvg=2000, max_cells_per_pert=200)
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
    print(f"[v0.5.0-lc] norman: {len(norman_tasks)} tasks")

    datasets = [
        ("adamson_full", adamson_ds, adamson_tasks),
        ("norman", norman_ds, norman_tasks),
    ]

    # ---------- 2. Lifecycle sweep ----------
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY missing in container env")

    client = OpenRouterClient(
        api_key=api_key,
        cache_dir=Path("/biofm_cache/llm_v2"),
        pool=DEFAULT_POOL,
        cooldown_sec=60.0,
    )
    pool = LLMAgentPool(client=client, cache_dir=Path("/biofm_cache/llm_v2"))

    n_lifecycle_runs = 0
    n_llm_calls_real = 0
    for dataset_name, ds, tasks in datasets:
        for held in tasks:
            if held not in ds["target_gene_idx"]:
                continue
            for seed in range(2026, 2026 + seeds):
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
                _append(rec)
                n_lifecycle_runs += 1
                print(
                    f"  [{dataset_name}/{held}/seed={seed}] "
                    f"msd={rec.get('final_msd_topk', 'NA')} "
                    f"backbone={rec.get('backbone_used', 'NA')} "
                    f"runs_so_far={n_lifecycle_runs}"
                )

    # ---------- 3. Phase-2 entropy gate ----------
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
        "n_lifecycle_runs": n_lifecycle_runs,
        "architect_backbone_entropy_nats": float(h_backbone),
        "architect_hvg_entropy_nats": float(h_hvg),
        "architect_backbone_distribution": bb_dist,
    }
    # Merge with prior provenance (preserve trainer numbers).
    prior = {}
    if provenance_out.exists():
        try:
            prior = json.loads(provenance_out.read_text())
        except json.JSONDecodeError:
            pass
    merged = prior | summary
    provenance_out.write_text(json.dumps(merged, indent=2, default=str))
    DATA_VOL.commit()
    print(json.dumps(summary, indent=2, default=str))
    return summary


@app.local_entrypoint()
def entrypoint() -> None:
    out = run_v05_lifecycle_only.remote()
    print(json.dumps(out, indent=2, default=str))
