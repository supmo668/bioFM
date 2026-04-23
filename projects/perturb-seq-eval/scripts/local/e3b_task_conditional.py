"""E3b — optimizer comparison on a *task-conditional* synthetic grid.

The main E3 uses a DGP where every task shares the same global optimum
(``a3_r1_linear``). That design makes non-contextual CMA-ES strictly
cheaper than contextual BO — the probe cannot help if there is no routing
decision to make. This is a **correctly-flagged falsification** of
Claim A on that DGP.

E3b turns the crank the other way: it constructs a grid where the best
(n_agents, n_rounds, backbone) varies with task difficulty. We then check
whether the contextual GP dominates CMA-ES when the probe *does* carry
routing information. This is the calibration check that validates our
infrastructure.

Output: ``artifacts/dry_run/e3b_task_conditional.json``.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

from perturb_eval.experiments import run_e3_optimizer_comparison
from perturb_eval.experiments.e3_optimizer_comparison import _phi_key
from perturb_eval.types import Config


OUT = Path("./artifacts/dry_run")


def _build_task_conditional_grid() -> tuple[
    dict[tuple[str, str], float],
    dict[str, np.ndarray],
    tuple[Config, ...],
]:
    """Grid where easy tasks prefer ``(3 agents, 1 round, linear)`` and hard
    tasks prefer ``(5 agents, 3 rounds, scgpt_small)``."""
    phis = tuple(
        Config(n_agents=a, n_rounds=r, backbone=b)
        for a in (3, 4, 5)
        for r in (1, 2, 3)
        for b in ("linear", "mlp", "scgpt_small")
    )
    tasks = ("easy1", "easy2", "easy3", "hard1", "hard2", "hard3")
    # Easy: probe low on signature[0] (simulate "confident consensus").
    # Hard: probe high on signature[0] (simulate "dispersed disagreement").
    contexts: dict[str, np.ndarray] = {}
    grid: dict[tuple[str, str], float] = {}
    for t in tasks:
        hard = t.startswith("hard")
        contexts[t] = (
            np.array([0.15, 0.70, 0.05, 0.85]) if not hard
            else np.array([0.85, 0.40, 0.55, 0.45])
        )
        for phi in phis:
            size = phi.n_agents * phi.n_rounds
            # Target config size: easy prefers 3 (small), hard prefers 15 (large).
            target_size = 15.0 if hard else 3.0
            backbone_bonus = {
                "linear": 0.0 if not hard else 0.15,
                "mlp": 0.10 if not hard else 0.05,
                "scgpt_small": 0.20 if not hard else 0.0,
            }[phi.backbone]
            msd = ((size - target_size) / 15.0) ** 2 + backbone_bonus
            grid[(_phi_key(phi), t)] = float(max(0.0, msd))
    return grid, contexts, phis


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    grid, contexts, phis = _build_task_conditional_grid()
    print(f"=== E3b task-conditional grid ({len(grid)} cells, "
          f"{len(contexts)} tasks, {len(phis)} configs) ===")

    trajectories = run_e3_optimizer_comparison(
        grid=grid,
        contexts=contexts,
        optimizers=("random", "cma_es", "contextual_gp"),
        n_iterations=20,
        n_seeds=10,
        config_space=phis,
    )
    headlines = {}
    for t in trajectories:
        arr = np.asarray(t.best_msd_per_iter)
        headlines[t.optimizer] = {
            "final_best_msd": round(float(arr[-1]), 5),
            "aulc_sum": round(float(arr.sum()), 5),
            "msd_at_iter_5": round(float(arr[min(4, len(arr) - 1)]), 5),
            "msd_at_iter_10": round(float(arr[min(9, len(arr) - 1)]), 5),
        }
    payload = {
        "headlines": headlines,
        "trajectories": [
            {
                "optimizer": t.optimizer,
                "best_msd_per_iter": list(t.best_msd_per_iter),
            }
            for t in trajectories
        ],
        "contextual_beats_cma_es_aulc": (
            headlines["contextual_gp"]["aulc_sum"]
            < headlines["cma_es"]["aulc_sum"]
        ),
        "contextual_beats_cma_es_final": (
            headlines["contextual_gp"]["final_best_msd"]
            < headlines["cma_es"]["final_best_msd"]
        ),
        "wall_time_sec": round(time.perf_counter() - t0, 2),
    }
    (OUT / "e3b_task_conditional.json").write_text(json.dumps(payload, indent=2))
    for name, stats in headlines.items():
        print(f"  {name:<15s} final={stats['final_best_msd']:.5f}  "
              f"AULC={stats['aulc_sum']:.4f}  "
              f"iter5={stats['msd_at_iter_5']:.4f}  "
              f"iter10={stats['msd_at_iter_10']:.4f}")
    print(f"contextual beats CMA-ES on AULC: {payload['contextual_beats_cma_es_aulc']}")
    print(f"contextual beats CMA-ES on final MSD: {payload['contextual_beats_cma_es_final']}")


if __name__ == "__main__":
    main()
