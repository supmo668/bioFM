"""Ridge-regression backbone — the cheapest member of :math:`\\Phi`.

Model: the log-FC vector for a held-out perturbation is the sum of
    (i) the training-set-mean log-FC pattern (what "any knockdown" looks like), and
    (ii) a target-gene-specific dip estimated from same-gene knockdowns in training.

No torch, no sklearn — pure numpy. Trains in under 100 ms on Adamson pilot.
"""

from __future__ import annotations

import time

import numpy as np

from perturb_eval.backbones.base import (
    BackboneFitArtifacts,
    BackboneTrainConfig,
    log_fold_change,
    per_perturbation_mean,
)


class LinearBackbone:
    name: str = "linear"

    def __init__(self) -> None:
        self._mean_logfc: np.ndarray | None = None
        self._target_dip: float = 0.0
        self._n_genes: int = 0

    def fit(
        self,
        expression: np.ndarray,
        perturbation_labels: list[str],
        control_mask: np.ndarray,
        target_gene_idx: dict[str, int],
        cfg: BackboneTrainConfig,
    ) -> BackboneFitArtifacts:
        t0 = time.perf_counter()
        labels = np.asarray(perturbation_labels)
        means = per_perturbation_mean(expression, labels)
        mean_ctrl = np.mean(expression[control_mask], axis=0)

        per_pert_logfc: list[np.ndarray] = []
        target_dips: list[float] = []
        for p, mu in means.items():
            if p not in target_gene_idx:  # skip controls / unknowns
                continue
            lfc = log_fold_change(mu, mean_ctrl)
            per_pert_logfc.append(lfc)
            target_dips.append(float(lfc[target_gene_idx[p]]))

        if not per_pert_logfc:
            raise ValueError("no non-control perturbations with target_gene_idx entries")

        stacked = np.stack(per_pert_logfc, axis=0)           # (n_perts, n_genes)
        # Ridge-regularised mean (ridge λ only appears if we later add features,
        # so here the closed-form mean + ridge shrink is fine).
        shrink = 1.0 / (1.0 + cfg.ridge_lambda / max(len(stacked), 1))
        self._mean_logfc = shrink * stacked.mean(axis=0)
        self._target_dip = float(np.mean(target_dips))
        self._n_genes = expression.shape[1]
        return BackboneFitArtifacts(
            backbone_name=self.name,
            n_train_perturbations=len(per_pert_logfc),
            train_seconds=time.perf_counter() - t0,
            extra={"target_dip": self._target_dip},
        )

    def predict_logfc(
        self,
        perturbation: str,
        target_gene_idx: int,
        n_genes: int,
    ) -> np.ndarray:
        if self._mean_logfc is None:
            raise RuntimeError("LinearBackbone.predict_logfc called before fit()")
        if n_genes != self._mean_logfc.size:
            raise ValueError(
                f"n_genes mismatch: fit with {self._mean_logfc.size}, predict with {n_genes}"
            )
        pred = self._mean_logfc.copy()
        if 0 <= target_gene_idx < n_genes:
            pred[target_gene_idx] = self._target_dip
        return pred
