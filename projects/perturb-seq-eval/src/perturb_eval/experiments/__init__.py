"""Experiment runners (E1 metric overlap, E2 grid fill, E3 optimizer comparison).

All runners are designed to be called both from local debug scripts (on
small synthetic data) and from Modal functions (on Adamson pilot). They
return plain Python/NumPy structures that serialise cleanly to JSON or
Parquet.

See docs/SUPPLEMENT_DESIGN.md §4 for the experimental plan.
"""

from __future__ import annotations

from perturb_eval.experiments.common import (
    GridCellResult,
    OptimizerTrajectory,
    probe_signature_from_trace,
)
from perturb_eval.experiments.e1_metric_overlap import run_e1_metric_overlap
from perturb_eval.experiments.e2_grid_fill import (
    enumerate_grid,
    train_grid_cell_synthetic,
)
from perturb_eval.experiments.e3_optimizer_comparison import run_e3_optimizer_comparison

__all__ = [
    "GridCellResult",
    "OptimizerTrajectory",
    "enumerate_grid",
    "probe_signature_from_trace",
    "run_e1_metric_overlap",
    "run_e3_optimizer_comparison",
    "train_grid_cell_synthetic",
]
