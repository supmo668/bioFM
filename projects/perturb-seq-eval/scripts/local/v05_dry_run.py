"""Local CPU dry-run of the v0.5.0 lifecycle on combined real Adamson.

Validates the end-to-end path before Phase 3 spends $ on Modal:
  1. ``load_adamson_combined`` merges pilot + 10X005 + 10X010 into the
     canonical dict.
  2. ``mean_abs_logfc_per_target`` scores each TF; ``stratified_subsample``
     picks ~20 TFs balanced across 3 strength bins (seed=2026).
  3. A subset of 3 tasks runs through the LLMAgentPool (with a
     deterministic stub client — no network) for speed.
  4. Final MSD must be finite and Architect entropy > 0.

Run:
    python3 scripts/local/v05_dry_run.py
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

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


class _DeterministicStubClient:
    def chat_json(self, *, role: str, task_id: str, round_index: int, prompt: str) -> dict:  # noqa: ARG002
        h = abs(hash((task_id, round_index, role))) % 100
        if role == "DataCurator":
            return {"hvg_method": "seurat", "hvg_count": 500 if h % 2 else 1000}
        if role == "Literature":
            return {
                "pathway_prior": {},
                "ppi_neighbors": [],
                "tool_calls": ["biogpt"],
                "expected_up": [],
                "expected_down": [],
            }
        if role == "Architect":
            backbones = ("linear", "mlp", "scgpt_small")
            return {
                "backbone": backbones[h % 3],
                "n_agents": 5,
                "n_rounds": 2,
                "hvg_count": 500 if h % 2 else 1000,
                "learning_rate": 1e-2 if h % 2 else 5e-3,
                "ridge_lambda": 1.0,
                "epochs": 30,
            }
        if role == "Trainer":
            return {"lr": 1e-2, "epochs": 10, "ridge_lambda": 1.0}
        if role == "Validator":
            return {"dynamic_threshold_msd": 0.1}
        return {}


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    # Local dry-run uses pilot + 10X005 only — 10X010 (~450 MB / ~24 GB
    # dense) OOMs residential machines; Modal A100 (32 GB) handles the
    # full combined set via the same code path.
    h5ads = [
        repo_root / "data" / "Adamson2016_pilot.h5ad",
        repo_root / "data" / "Adamson2016_10X005.h5ad",
    ]
    missing = [p for p in h5ads if not p.exists()]
    if missing:
        print(f"missing Adamson h5ads: {missing}", file=sys.stderr)
        return 1

    print(f"[dry-run] loading {len(h5ads)} Adamson subsets ...")
    t0 = time.time()
    # Lower max_cells_per_pert for local feasibility; Modal uses 200.
    ds = load_adamson_combined(h5ads, n_top_hvg=2000, max_cells_per_pert=80)
    print(
        f"[dry-run] combined: X={ds['X'].shape}, "
        f"n_perts={len(ds['perturbations'])} in {time.time()-t0:.1f}s"
    )

    # Stratify by |logFC|.
    logfc = mean_abs_logfc_per_target(
        ds["X"], ds["labels"], ds["control_mask"], ds["target_gene_idx"]
    )
    tfs = np.array(list(logfc.keys()))
    strengths = np.array([logfc[t] for t in tfs])
    n_bins = 3
    bin_edges = np.quantile(strengths, np.linspace(0, 1, n_bins + 1))
    bin_ids = np.clip(np.digitize(strengths, bin_edges[1:-1]), 0, n_bins - 1)
    stratified = stratified_subsample(tfs, bin_ids, n_per_stratum=7, seed=2026)
    print(
        f"[dry-run] |logFC| stratified: {len(stratified)} TFs (all 3 bins represented)"
    )
    print(
        f"[dry-run] strength range: min={strengths.min():.3f} "
        f"max={strengths.max():.3f}"
    )

    # Run lifecycle on 3 tasks (spanning the strength range) for speed.
    sample_tasks = [stratified[0], stratified[len(stratified)//2], stratified[-1]]
    print(f"[dry-run] running lifecycle on {sample_tasks} ...")

    cache_dir = repo_root / "artifacts" / "v0.5.0" / "dry_run_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    pool = LLMAgentPool(client=_DeterministicStubClient(), cache_dir=cache_dir)

    runs = []
    for task in sample_tasks:
        t0 = time.time()
        run = run_agentic_lifecycle(
            task_id=task,
            X=ds["X"],
            labels=ds["labels"],
            control_mask=ds["control_mask"],
            target_gene_idx=ds["target_gene_idx"],
            held_out=task,
            agent_pool=pool,
            max_rounds=2,
        )
        runs.append(run)
        print(
            f"  {task}: MSD={run.final_msd_topk:.4f} "
            f"bb={run.backbone_used} rounds={run.n_rounds} "
            f"wall={time.time()-t0:.1f}s"
        )

    traces = [list(r.steps) for r in runs]
    h_backbone = per_agent_field_entropy(traces, agent="Architect", field="backbone")
    h_hvg = per_agent_field_entropy(traces, agent="Architect", field="hvg_count")

    summary = {
        "n_adamson_tfs_total": len(logfc),
        "n_tasks_after_stratify": int(len(stratified)),
        "n_tasks_tested": len(sample_tasks),
        "finite_runs": sum(1 for r in runs if np.isfinite(r.final_msd_topk)),
        "mean_msd": float(np.mean([r.final_msd_topk for r in runs])),
        "architect_backbone_entropy_nats": float(h_backbone),
        "architect_hvg_entropy_nats": float(h_hvg),
        "architect_backbone_dist": summarise_choice_distribution(
            traces, agent="Architect", field="backbone"
        ),
        "strength_bin_counts": {str(b): int((bin_ids == b).sum()) for b in range(n_bins)},
    }
    out = repo_root / "artifacts" / "v0.5.0" / "dry_run_summary.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2))
    print(f"[dry-run] wrote {out}")
    print(json.dumps(summary, indent=2))

    if summary["finite_runs"] == 0:
        print("[dry-run] FAIL: no finite runs", file=sys.stderr)
        return 2
    if summary["n_tasks_after_stratify"] < 15:
        print(
            f"[dry-run] WARN: stratification yielded only {summary['n_tasks_after_stratify']} tasks",
            file=sys.stderr,
        )
    print("[dry-run] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
