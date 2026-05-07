"""Experiment runners — v0.5.0 is real-data only.

The legacy synthetic-DGP runners (E1 metric overlap from synthetic traces,
``train_grid_cell_synthetic``) were removed in v0.5.0 per the paper's
no-synthetic-Perturb-seq invariant. The current entry-points consume real
Adamson 2016 / Norman 2019 cells fetched via
:mod:`perturb_eval.data.download`.
"""

from __future__ import annotations

from perturb_eval.experiments.common import (
    GridCellResult,
    OptimizerTrajectory,
    probe_signature_from_trace,
)
from perturb_eval.experiments.e2_grid_fill import enumerate_grid, phi_identifier
from perturb_eval.experiments.e3_optimizer_comparison import run_e3_optimizer_comparison

__all__ = [
    "GridCellResult",
    "OptimizerTrajectory",
    "enumerate_grid",
    "phi_identifier",
    "probe_signature_from_trace",
    "run_e3_optimizer_comparison",
]
