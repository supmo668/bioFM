"""Shared dataclasses and helpers used by all experiment runners."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from perturb_eval.metrics import ace_norm, critique_severity_dispersion
from perturb_eval.types import RunTrace


@dataclass(frozen=True)
class GridCellResult:
    """One row of the offline (phi, task, seed) grid (E2)."""

    phi_id: str
    task: str
    seed: int
    msd_topk: float
    wall_time_sec: float
    backbone_name: str


@dataclass(frozen=True)
class OptimizerTrajectory:
    """One optimizer's best-so-far curve, averaged across seeds/tasks (E3).

    Responding to MC1 in docs/REVIEWER_CRITIQUE.md: the per-seed inner
    curves are retained on ``per_seed_trajectories`` so downstream code can
    compute bootstrap CIs. ``best_msd_per_iter`` keeps the across-seed
    mean for backwards compatibility with existing figures.
    """

    optimizer: str
    best_msd_per_iter: tuple[float, ...]
    n_iterations: int
    n_seeds: int
    n_tasks: int
    # Mean cumulative regret per iter = mean over (task, seed) of
    #   Σ_{t'≤t} (y_{t'} − y_min_for_that_task).
    # Added for mc5 — cumulative regret is directly comparable to the
    # Krause–Ong bound cited in SUPPLEMENT.md §6.4.
    cum_regret_per_iter: tuple[float, ...] = ()
    # One inner tuple per (task, seed) pair (order is task-major). Each
    # inner tuple is the best-so-far curve for that specific run.
    per_seed_trajectories: tuple[tuple[float, ...], ...] = ()


def probe_signature_from_trace(trace: RunTrace) -> np.ndarray:
    """Extract the 4-d probe signature ``x`` from the shallow-round trace.

    ``x = (ACE_norm, mean(c), CSD, max(c))`` on round 0. See
    docs/SUPPLEMENT_DESIGN.md §2.3.
    """
    if not trace.rounds:
        return np.zeros(4, dtype=np.float64)
    rt = trace.rounds[0]
    confs = np.asarray(rt.confidences, dtype=np.float64)
    return np.array(
        [
            ace_norm(rt.confidences),
            float(confs.mean()) if confs.size else 0.0,
            critique_severity_dispersion(rt.critique_severities),
            float(confs.max()) if confs.size else 0.0,
        ],
        dtype=np.float64,
    )
