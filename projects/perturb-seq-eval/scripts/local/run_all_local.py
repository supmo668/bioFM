"""Local (CPU-only) end-to-end driver.

Reproduces the full supplement pipeline on synthetic data, under 60 seconds
on a laptop. Exists so a reviewer can validate the plumbing without having
Modal credentials or a GPU.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np

from perturb_eval.experiments import (
    enumerate_grid,
    probe_signature_from_trace,
    run_e1_metric_overlap,
    run_e3_optimizer_comparison,
    train_grid_cell_synthetic,
)
from perturb_eval.experiments.e2_grid_fill import phi_identifier, write_results_jsonl
from perturb_eval.experiments.e3_optimizer_comparison import _phi_key
from perturb_eval.types import Config, DEFAULT_CONFIG_SPACE, RoundTrace, RunTrace


ARTIFACTS_DIR = Path("./artifacts/local")


def main() -> None:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()

    # ---- E1 --------------------------------------------------------------
    print("=== E1 metric overlap ===")
    e1 = run_e1_metric_overlap(n_traces=500, seed=2026)
    with (ARTIFACTS_DIR / "e1_overlap.json").open("w") as f:
        json.dump(
            {
                "spearman_matrix": np.asarray(e1["spearman_matrix"]).tolist(),
                "feature_names": e1["feature_names"],
                "drop_candidates": e1["drop_candidates"],
                "n_traces": e1["n_traces"],
            },
            f,
            indent=2,
        )
    print(f"  drop candidates: {e1['drop_candidates']}")

    # ---- E2 (tiny grid) --------------------------------------------------
    print("=== E2 grid fill (synthetic, 18 cells) ===")
    phis = tuple(
        Config(n_agents=a, n_rounds=r, backbone=b)
        for a in (3, 5)
        for r in (1, 2)
        for b in ("linear", "mlp", "scgpt_small")
    )
    # Only keep linear+mlp if torch absent.
    try:
        import torch  # noqa: F401
    except ImportError:
        phis = tuple(p for p in phis if p.backbone != "scgpt_small")

    tasks = ("T0", "T1", "T2")
    seeds = (2026, 2027)
    cells = enumerate_grid(phis, tasks, seeds)
    rows = [train_grid_cell_synthetic(phi=phi, task=t, seed=s) for phi, t, s in cells]
    write_results_jsonl(rows, ARTIFACTS_DIR / "e2_grid.jsonl")
    print(f"  wrote {len(rows)} rows to {ARTIFACTS_DIR / 'e2_grid.jsonl'}")

    # ---- E3 --------------------------------------------------------------
    print("=== E3 optimizer comparison ===")
    # Build the grid keyed by _phi_key convention.
    grid = {
        (_phi_key(Config(n_agents=int(phi_id.split("_")[0][1:]),
                         n_rounds=int(phi_id.split("_")[1][1:]),
                         backbone="_".join(phi_id.split("_")[2:]))),
         task): msd
        for phi_id, task, msd in (
            (r.phi_id, r.task, r.msd_topk) for r in rows
        )
    }
    rng_ctx = np.random.default_rng(2026)
    contexts = {}
    for t in tasks:
        confs = tuple(float(v) for v in rng_ctx.uniform(0.4, 0.9, size=5))
        rt = RoundTrace(
            round_index=0,
            agent_names=("A", "B", "C", "D", "E"),
            confidences=confs,
            critique_severities=((0.2, 0.3, 0.1, 0.25),) * 5,
            winner_index=0,
            consensus_score=0.55,
        )
        contexts[t] = probe_signature_from_trace(
            RunTrace(task_id=t, rounds=(rt,), converged=False, backbone="linear")
        )
    config_space = tuple(
        Config(n_agents=phi.n_agents, n_rounds=phi.n_rounds, backbone=phi.backbone)
        for phi in phis
    )
    trajectories = run_e3_optimizer_comparison(
        grid=grid,
        contexts=contexts,
        optimizers=("random", "cma_es", "contextual_gp"),
        n_iterations=10,
        n_seeds=3,
        config_space=config_space,
    )
    serial = [
        {
            "optimizer": t.optimizer,
            "best_msd_per_iter": list(t.best_msd_per_iter),
            "n_iterations": t.n_iterations,
            "n_seeds": t.n_seeds,
            "n_tasks": t.n_tasks,
        }
        for t in trajectories
    ]
    with (ARTIFACTS_DIR / "e3_trajectories.json").open("w") as f:
        json.dump(serial, f, indent=2)
    print("  trajectories:")
    for s in serial:
        print(f"    {s['optimizer']:<15s} best={s['best_msd_per_iter'][-1]:.4f}")

    dt = time.perf_counter() - t0
    print(f"\ntotal wall time: {dt:.1f}s")
    print(f"artifacts written under {ARTIFACTS_DIR}")


if __name__ == "__main__":
    main()
