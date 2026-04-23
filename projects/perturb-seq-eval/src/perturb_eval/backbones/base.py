"""Shared types and helpers for the backbone predictors.

See docs/SUPPLEMENT_DESIGN.md §3. Every concrete backbone must satisfy
the :class:`BackbonePredictor` Protocol; the experiment runners depend on
that Protocol, not on any particular implementation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

import numpy as np


@dataclass(frozen=True)
class BackboneTrainConfig:
    """Knobs passed to every :meth:`BackbonePredictor.fit` call.

    Kept deliberately small — the HPO axes live in :class:`Config`
    (``perturb_eval.types``), not here.
    """

    top_k_genes: int = 20
    seed: int = 2026
    max_iter: int = 200
    learning_rate: float = 1e-2
    ridge_lambda: float = 1.0


@dataclass(frozen=True)
class BackboneFitArtifacts:
    backbone_name: str
    n_train_perturbations: int
    train_seconds: float = 0.0
    extra: dict = field(default_factory=dict)


class BackbonePredictor(Protocol):
    """Protocol every backbone must satisfy.

    A backbone is trained once on all non-control cells excluding the
    held-out perturbation, then asked to predict the full per-gene log-FC
    vector for that perturbation.
    """

    name: str

    def fit(
        self,
        expression: np.ndarray,            # (n_cells, n_genes), log-normalized
        perturbation_labels: list[str],    # (n_cells,) string labels, "CTRL" for control
        control_mask: np.ndarray,          # (n_cells,) bool
        target_gene_idx: dict[str, int],   # perturbation name → gene-column index
        cfg: BackboneTrainConfig,
    ) -> BackboneFitArtifacts: ...

    def predict_logfc(
        self,
        perturbation: str,
        target_gene_idx: int,
        n_genes: int,
    ) -> np.ndarray: ...                   # (n_genes,)


def mean_squared_deviation(
    predicted: np.ndarray,
    observed: np.ndarray,
    top_k_indices: np.ndarray,
) -> float:
    """Standard perturb-seq MSD on top-K differentially expressed genes.

    This is the metric reported by CPA (Lotfollahi 2023), GEARS (Roohani
    2024), and scGPT-perturb (Cui 2024). Lower is better.
    """
    if predicted.shape != observed.shape:
        raise ValueError(
            f"predicted {predicted.shape} ≠ observed {observed.shape}"
        )
    if top_k_indices.size == 0:
        return 0.0
    diff = predicted[top_k_indices] - observed[top_k_indices]
    return float(np.mean(diff * diff))


# ---------------------------------------------------------------------------
# Helpers shared by concrete backbones
# ---------------------------------------------------------------------------


def per_perturbation_mean(
    expression: np.ndarray,
    labels: list[str] | np.ndarray,
) -> dict[str, np.ndarray]:
    """Mean expression vector per label (skipping empty groups)."""
    labels_arr = np.asarray(labels)
    out: dict[str, np.ndarray] = {}
    for p in np.unique(labels_arr):
        mask = labels_arr == p
        if mask.any():
            out[str(p)] = np.mean(expression[mask], axis=0)
    return out


def log_fold_change(
    mean_perturbed: np.ndarray,
    mean_control: np.ndarray,
    pseudocount: float = 1e-3,  # noqa: ARG001 - kept for API stability
) -> np.ndarray:
    """Log-FC between two log-normalised expression vectors.

    Both inputs are assumed to be in ``log1p`` space (the scanpy/Scanpy
    default after ``sc.pp.log1p``). Log-FC in natural log is then just
    the difference; pseudocounts are already folded into ``log1p``.

    ``pseudocount`` is accepted for API stability with callers that still
    pass it; it is ignored.
    """
    return np.asarray(mean_perturbed, dtype=np.float64) - np.asarray(
        mean_control, dtype=np.float64
    )
