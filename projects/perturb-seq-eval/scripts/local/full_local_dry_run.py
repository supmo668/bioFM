"""Full supplementary dry-run — synthetic data, CPU only, no Modal, no GPU.

Produces every artifact documented in ``docs/SUPPLEMENT.md`` using a scale
that finishes in under 5 minutes on a laptop:

    * E1 — 2 000 synthetic traces → Spearman matrix + drop decisions.
    * E2 — full 27-config Φ × 4 tasks × 2 seeds = 216 cells grid fill.
    * E3 — three optimizers × 20 iterations × 5 seeds × 4 tasks on cached grid.
    * Summary CSV that the journal section in SUPPLEMENT.md cites.

Output directory: ``artifacts/dry_run/``. Each artifact is plain JSON/JSONL
so reviewers can grep/jq it without tooling.
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
from perturb_eval.types import Config, RoundTrace, RunTrace


OUT = Path("./artifacts/dry_run")


def _probe_for_task(task: str, difficulty: float, seed: int) -> np.ndarray:
    """Synthesize a round-0 probe signature with the right difficulty signal."""
    rng = np.random.default_rng(seed + abs(hash(task)) % 2**30)
    # Harder tasks get flatter confidences + higher base severity.
    confs = tuple(
        float(np.clip(rng.normal(0.5, 0.08 + 0.25 * difficulty), 0.01, 1.0))
        for _ in range(5)
    )
    sev = tuple(
        tuple(float(np.clip(rng.normal(0.15 + 0.45 * difficulty, 0.15), 0.0, 1.0))
              for _ in range(4))
        for _ in range(5)
    )
    rt = RoundTrace(
        round_index=0,
        agent_names=("A", "B", "C", "D", "E"),
        confidences=confs,
        critique_severities=sev,
        winner_index=0,
        consensus_score=float(np.clip(0.9 - 0.4 * difficulty, 0.1, 0.95)),
    )
    return probe_signature_from_trace(
        RunTrace(task_id=task, rounds=(rt,), converged=False, backbone="linear")
    )


def main() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()

    summary: dict[str, object] = {}

    # ------------------------------------------------------------------
    # E1 — metric overlap at n=2000
    # ------------------------------------------------------------------
    print("=== E1 metric overlap (n_traces=2000) ===")
    t_e1 = time.perf_counter()
    e1 = run_e1_metric_overlap(n_traces=2000, seed=2026)
    e1_dt = time.perf_counter() - t_e1
    e1_payload = {
        "spearman_matrix": np.asarray(e1["spearman_matrix"]).tolist(),
        "feature_names": e1["feature_names"],
        "drop_candidates": e1["drop_candidates"],
        "n_traces": e1["n_traces"],
        "wall_time_sec": e1_dt,
    }
    (OUT / "e1_overlap.json").write_text(json.dumps(e1_payload, indent=2))

    # Extract the critical pairwise correlations for the journal.
    feats = e1["feature_names"]
    idx = {n: i for i, n in enumerate(feats)}
    rho = np.asarray(e1["spearman_matrix"])
    summary["e1"] = {
        "n_traces": 2000,
        "wall_time_sec": round(e1_dt, 3),
        "spearman_ace_h_vs_ace_d":   round(float(rho[idx["ace_h"], idx["ace_d"]]), 4),
        "spearman_csd_vs_csd_star":  round(float(rho[idx["csd"], idx["csd_star"]]), 4),
        "spearman_tdi_vs_tdi2":      round(float(rho[idx["tdi"], idx["tdi2"]]), 4),
        "drop_candidates": e1["drop_candidates"],
    }
    print(f"  {e1_dt:.1f}s  drop_candidates={e1['drop_candidates']}")

    # ------------------------------------------------------------------
    # E2 — grid fill on synthetic data
    # ------------------------------------------------------------------
    print("=== E2 grid fill (27 x 4 x 2 = 216 cells) ===")
    t_e2 = time.perf_counter()
    phis = tuple(
        Config(n_agents=a, n_rounds=r, backbone=b)
        for a in (3, 4, 5)
        for r in (1, 2, 3)
        for b in ("linear", "mlp", "scgpt_small")
    )
    try:
        import torch  # noqa: F401
        has_torch = True
    except ImportError:
        has_torch = False
        phis = tuple(p for p in phis if p.backbone != "scgpt_small")
    tasks = ("T_easy", "T_medium", "T_hard", "T_bimodal")
    seeds = (2026, 2027)
    cells = enumerate_grid(phis, tasks, seeds)
    rows = []
    for i, (phi, task, seed) in enumerate(cells):
        result = train_grid_cell_synthetic(
            phi=phi, task=task, seed=seed,
            n_cells=240, n_genes=40, n_perts=4,
        )
        rows.append(result)
        if (i + 1) % 50 == 0:
            print(f"  {i+1:>3}/{len(cells)} cells "
                  f"(MSD mean so far = {np.mean([r.msd_topk for r in rows]):.4f})")
    e2_dt = time.perf_counter() - t_e2
    write_results_jsonl(rows, OUT / "e2_grid.jsonl")

    msds = np.array([r.msd_topk for r in rows])
    per_backbone = {
        bb: float(np.mean([r.msd_topk for r in rows if r.backbone_name == bb]))
        for bb in sorted({r.backbone_name for r in rows})
    }
    summary["e2"] = {
        "n_cells": len(rows),
        "wall_time_sec": round(e2_dt, 2),
        "msd_min": round(float(msds.min()), 5),
        "msd_max": round(float(msds.max()), 5),
        "msd_mean": round(float(msds.mean()), 5),
        "msd_per_backbone_mean": {k: round(v, 5) for k, v in per_backbone.items()},
        "has_torch_backbone": has_torch,
    }
    print(f"  {e2_dt:.1f}s  MSD range=[{msds.min():.4f}, {msds.max():.4f}]  "
          f"per-backbone={per_backbone}")

    # ------------------------------------------------------------------
    # E3 — contextual BO vs CMA-ES vs random on cached grid
    # ------------------------------------------------------------------
    print("=== E3 optimizer comparison (20 iter x 5 seeds x 4 tasks) ===")
    t_e3 = time.perf_counter()

    # Build the grid keyed by _phi_key convention (a=Xr=Xb=bb).
    def _rekey(phi_id: str) -> str:
        # "a3_r1_linear" → "a=3r=1b=linear"
        parts = phi_id.split("_")
        a = parts[0][1:]
        r = parts[1][1:]
        b = "_".join(parts[2:])
        return f"a={a}r={r}b={b}"
    grid = {(_rekey(r.phi_id), r.task): r.msd_topk for r in rows}

    # Difficulty assignments drive the probe signatures: match the task names.
    difficulty_by_task = {
        "T_easy":    0.15,
        "T_medium":  0.50,
        "T_hard":    0.85,
        "T_bimodal": 0.60,
    }
    contexts = {
        t: _probe_for_task(t, difficulty_by_task[t], seed=2026)
        for t in tasks
    }
    config_space = phis
    trajectories = run_e3_optimizer_comparison(
        grid=grid,
        contexts=contexts,
        optimizers=("random", "cma_es", "contextual_gp"),
        n_iterations=20,
        n_seeds=5,
        config_space=config_space,
    )
    e3_dt = time.perf_counter() - t_e3
    traj_serial = [
        {
            "optimizer": t.optimizer,
            "best_msd_per_iter": list(t.best_msd_per_iter),
            "n_iterations": t.n_iterations,
            "n_seeds": t.n_seeds,
            "n_tasks": t.n_tasks,
        }
        for t in trajectories
    ]
    (OUT / "e3_trajectories.json").write_text(json.dumps(traj_serial, indent=2))

    # Headline numbers: final best MSD, AULC (area under learning curve = total regret proxy).
    headlines: dict[str, dict[str, float]] = {}
    for ts in traj_serial:
        arr = np.asarray(ts["best_msd_per_iter"])
        headlines[ts["optimizer"]] = {
            "final_best_msd": round(float(arr[-1]), 5),
            "aulc_sum":       round(float(arr.sum()), 5),
            "iter_to_95pct_of_best": int(_first_within_pct(arr, 5.0)),
        }
    summary["e3"] = {
        "wall_time_sec": round(e3_dt, 2),
        "n_iterations": 20,
        "n_seeds": 5,
        "n_tasks": len(tasks),
        "headlines": headlines,
        "contextual_beats_cma_es": (
            headlines["contextual_gp"]["final_best_msd"]
            < headlines["cma_es"]["final_best_msd"]
        ),
        "contextual_beats_random": (
            headlines["contextual_gp"]["final_best_msd"]
            < headlines["random"]["final_best_msd"]
        ),
    }
    print(f"  {e3_dt:.1f}s")
    for name, stats in headlines.items():
        print(f"    {name:<15s} final={stats['final_best_msd']:.5f}  "
              f"AULC={stats['aulc_sum']:.4f}  "
              f"iter→≈best={stats['iter_to_95pct_of_best']}")

    # ------------------------------------------------------------------
    # Wrap up
    # ------------------------------------------------------------------
    summary["total_wall_time_sec"] = round(time.perf_counter() - t0, 2)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2))
    print(f"\nwall time: {summary['total_wall_time_sec']}s")
    print(f"artifacts: {OUT.resolve()}")
    return summary


def _first_within_pct(arr: np.ndarray, pct: float) -> int:
    """Smallest iteration index at which ``arr`` is within ``pct``% of its
    final value. Returns ``len(arr)`` if never within tolerance."""
    if arr.size == 0:
        return 0
    final = float(arr[-1])
    if not np.isfinite(final) or final == 0:
        return len(arr)
    tol = abs(final) * (pct / 100.0)
    for i, v in enumerate(arr):
        if abs(v - final) <= tol:
            return i + 1
    return len(arr)


if __name__ == "__main__":
    main()
