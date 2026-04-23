"""E3 — optimizer comparison on a cached MSD grid.

This runner accepts an already-filled (phi, task) → MSD grid (produced by
E2) and runs each optimizer against it for ``n_iterations`` iterations,
averaging across seeds and tasks. The returned trajectories feed the
iteration-vs-best-MSD figure that is the supplement's headline result.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from perturb_eval.experiments.common import OptimizerTrajectory
from perturb_eval.optimizers import Observation, build_optimizer
from perturb_eval.types import Config, DEFAULT_CONFIG_SPACE


def _phi_key(phi: Config) -> str:
    return f"a={phi.n_agents}r={phi.n_rounds}b={phi.backbone}"


def run_e3_optimizer_comparison(
    *,
    grid: dict[tuple[str, str], float],
    contexts: dict[str, np.ndarray],
    optimizers: tuple[str, ...] = ("random", "cma_es", "contextual_gp"),
    n_iterations: int = 20,
    n_seeds: int = 3,
    config_space: tuple[Config, ...] = DEFAULT_CONFIG_SPACE,
) -> list[OptimizerTrajectory]:
    """Run each optimizer ``n_seeds`` times against the cached grid.

    Parameters
    ----------
    grid:
        ``{(phi_key, task): msd}`` with ``phi_key`` produced by ``_phi_key``.
    contexts:
        ``{task: 4-d probe signature}``.
    optimizers:
        Names resolvable by :func:`build_optimizer`.
    n_iterations, n_seeds:
        Inner loop sizes.
    config_space:
        Restriction of the optimizer to this finite Φ.
    """
    trajectories: list[OptimizerTrajectory] = []
    tasks = tuple(contexts.keys())

    # Restrict to configs that have grid entries for at least one task.
    available = tuple(phi for phi in config_space if any((_phi_key(phi), t) in grid for t in tasks))
    if not available:
        raise ValueError(
            "no overlap between config_space and grid keys — "
            "make sure _phi_key convention matches the grid builder"
        )

    for opt_name in optimizers:
        # One trajectory averaged across tasks and seeds.
        best_per_iter = np.full(n_iterations, np.inf, dtype=np.float64)
        count = np.zeros(n_iterations, dtype=np.int64)
        for task in tasks:
            ctx = contexts[task]
            for seed in range(n_seeds):
                opt = build_optimizer(opt_name, config_space=available, seed=seed)
                observed: list[Observation] = []
                running_best = np.inf
                for t in range(n_iterations):
                    phi = opt.suggest(context=ctx, observed=observed)
                    key = (_phi_key(phi), task)
                    y = grid.get(key)
                    if y is None:  # grid gap → skip iteration
                        continue
                    observed.append(Observation(config=phi, context=ctx, objective=float(y)))
                    if y < running_best:
                        running_best = y
                    if running_best < best_per_iter[t]:
                        best_per_iter[t] = running_best
                    # Update running totals for per-iter average.
                    count[t] += 1
        # Collect per-(task, seed) best-so-far + cumulative regret so we
        # can bootstrap CIs downstream (responds to MC1 in REVIEWER_CRITIQUE.md).
        per_seed, cum_regret_per_iter, avg = _collect_per_seed_trajectories(
            opt_name=opt_name,
            grid=grid,
            contexts=contexts,
            available=available,
            tasks=tasks,
            n_iterations=n_iterations,
            n_seeds=n_seeds,
        )
        trajectories.append(
            OptimizerTrajectory(
                optimizer=opt_name,
                best_msd_per_iter=tuple(float(x) for x in avg),
                cum_regret_per_iter=tuple(float(x) for x in cum_regret_per_iter),
                per_seed_trajectories=tuple(
                    tuple(float(x) for x in traj) for traj in per_seed
                ),
                n_iterations=n_iterations,
                n_seeds=n_seeds,
                n_tasks=len(tasks),
            )
        )
    return trajectories


def _collect_per_seed_trajectories(
    *,
    opt_name: str,
    grid: dict[tuple[str, str], float],
    contexts: dict[str, np.ndarray],
    available: tuple[Config, ...],
    tasks: tuple[str, ...],
    n_iterations: int,
    n_seeds: int,
) -> tuple[list[list[float]], np.ndarray, np.ndarray]:
    """Roll out each ``(task, seed)`` run to completion and keep the curves.

    Returns
    -------
    per_seed_trajectories
        ``[len(tasks) × n_seeds]`` inner lists of ``n_iterations`` best-so-far
        values.
    cum_regret_per_iter
        Mean cumulative regret ``Σ(y_t − y_min_for_task)`` per iteration,
        averaged over all (task, seed) runs.
    best_mean_per_iter
        Mean best-so-far curve over all (task, seed) runs.
    """
    task_min = {
        task: min(v for (_, t_), v in grid.items() if t_ == task)
        for task in tasks
    }
    per_seed: list[list[float]] = []
    # Mean best-so-far aggregation
    sums_best = np.zeros(n_iterations, dtype=np.float64)
    # Mean cumulative regret aggregation
    sums_regret = np.zeros(n_iterations, dtype=np.float64)
    counts = np.zeros(n_iterations, dtype=np.int64)

    for task in tasks:
        ctx = contexts[task]
        y_min = task_min[task]
        for seed in range(n_seeds):
            opt = build_optimizer(opt_name, config_space=available, seed=seed)
            observed: list[Observation] = []
            running_best = np.inf
            running_regret = 0.0
            curve: list[float] = []
            for t in range(n_iterations):
                phi = opt.suggest(context=ctx, observed=observed)
                y = grid.get((_phi_key(phi), task))
                if y is not None:
                    observed.append(Observation(config=phi, context=ctx, objective=float(y)))
                    running_best = min(running_best, y)
                    running_regret += max(0.0, y - y_min)
                curve.append(running_best)
                if np.isfinite(running_best):
                    sums_best[t] += running_best
                    sums_regret[t] += running_regret
                    counts[t] += 1
            per_seed.append(curve)

    best_mean = np.where(counts > 0, sums_best / np.maximum(counts, 1), np.inf)
    regret_mean = np.where(counts > 0, sums_regret / np.maximum(counts, 1), 0.0)
    return per_seed, regret_mean, best_mean
