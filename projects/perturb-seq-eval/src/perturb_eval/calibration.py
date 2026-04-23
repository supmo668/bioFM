"""Fit TDI coefficients and the Bayesian recommender from logged runs.

Intended usage
--------------
After running the orchestrator N times across the calibration set and logging
``RunTrace`` records together with ground-truth difficulty labels, call

    coeffs = fit_tdi_coefficients(labelled_traces)
    rec = BayesianRecommender().fit(probe_to_config_tuples)

We use a tiny ridge regression for TDI (more robust than OLS for small N) and
let ``BayesianRecommender.fit`` handle the likelihood itself.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

import numpy as np

from perturb_eval.metrics import (
    delta_mean_confidence,
    round_metrics,
    winner_flip_rate,
)
from perturb_eval.types import RunTrace


@dataclass(frozen=True)
class TDICoeffs:
    alpha: float
    beta: float
    gamma: float
    delta: float

    def as_dict(self) -> dict[str, float]:
        return {"alpha": self.alpha, "beta": self.beta, "gamma": self.gamma, "delta": self.delta}


def fit_tdi_coefficients(
    labelled_traces: Iterable[tuple[RunTrace, float]],
    *,
    ridge_lambda: float = 0.1,
) -> TDICoeffs:
    """Fit (α, β, γ, δ) via ridge regression against a difficulty label.

    Each item is ``(run_trace, difficulty_label)`` with ``difficulty_label`` in
    [0, 1] (0 = easy, 1 = hard). The label can be a continuous difficulty
    proxy (e.g. literature sparsity, wet-lab reproducibility) or a discretised
    tier (easy=0.0, medium=0.5, hard=1.0).

    The coefficients are clipped to [0, 1] and re-normalised to sum to 1 — this
    keeps TDI in [0, 1] without retraining the normalisation step.
    """
    X: list[list[float]] = []
    y: list[float] = []
    for trace, label in labelled_traces:
        per_round = tuple(round_metrics(r) for r in trace.rounds)
        if not per_round:
            continue
        last = per_round[-1]
        dc = delta_mean_confidence(per_round)
        lack_of_conv = 1.0 - max(0.0, min(1.0, dc))
        wfr = winner_flip_rate(per_round)
        X.append([last.ace_norm, last.csd, lack_of_conv, wfr])
        y.append(float(label))

    if not X:
        # No data: fall back to the defaults.
        return TDICoeffs(alpha=0.35, beta=0.25, gamma=0.25, delta=0.15)

    A = np.asarray(X, dtype=np.float64)
    b = np.asarray(y, dtype=np.float64)
    # Ridge: (AᵀA + λI)⁻¹ Aᵀb
    gram = A.T @ A + ridge_lambda * np.eye(A.shape[1])
    w = np.linalg.solve(gram, A.T @ b)

    # Clip + normalise so TDI stays in [0, 1].
    w = np.clip(w, 0.0, None)
    total = float(np.sum(w))
    if total <= 0:
        return TDICoeffs(alpha=0.35, beta=0.25, gamma=0.25, delta=0.15)
    w = w / total
    return TDICoeffs(alpha=float(w[0]), beta=float(w[1]), gamma=float(w[2]), delta=float(w[3]))
