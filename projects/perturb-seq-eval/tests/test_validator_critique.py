"""v0.5.0 — Validator now returns a StructuredCritique.

The critique must surface:
  * which_genes_failed — top-K DEGs where prediction sign disagrees with
    observed sign.
  * suggested_next_config_delta — a small dict of config keys the
    Architect should consider changing next round (e.g. raise
    learning_rate if underfit, switch backbone if consistently wrong).
  * accept_reason — human-readable rationale.
"""

from __future__ import annotations

import numpy as np

from perturb_eval.agentic_lifecycle.types import ExecutedValidation
from perturb_eval.agentic_lifecycle.validator_gate import (
    score_and_gate,
    suggest_config_delta,
)


class _BadBackbone:
    """Predicts zeros — always fails MSD gate on non-trivial tasks."""

    name = "mock_bad"

    def predict_logfc(self, held_out: str, target_idx: int, *, n_genes: int) -> np.ndarray:  # noqa: ARG002
        return np.zeros(n_genes, dtype=np.float64)


class _PerfectBackbone:
    """Returns ``truth`` verbatim so MSD == 0."""

    name = "mock_perfect"

    def __init__(self, truth: np.ndarray) -> None:
        self._truth = truth

    def predict_logfc(self, held_out: str, target_idx: int, *, n_genes: int) -> np.ndarray:  # noqa: ARG002
        return self._truth.copy()


def _toy_matrix(n_genes: int, seed: int) -> tuple:
    rng = np.random.default_rng(seed)
    # 3 cell classes — controls, held-out perturbation p1, and p2.
    n_per = 20
    X_ctrl = rng.normal(loc=0.5, scale=0.1, size=(n_per, n_genes))
    X_p1 = rng.normal(loc=0.5, scale=0.1, size=(n_per, n_genes))
    X_p2 = rng.normal(loc=0.5, scale=0.1, size=(n_per, n_genes))
    # Bake a per-perturbation signal: p1 shifts first 5 genes up, p2 shifts them down.
    X_p1[:, :5] += 1.0
    X_p2[:, :5] -= 1.0
    X = np.vstack([X_ctrl, X_p1, X_p2]).astype(np.float64)
    labels = np.array(["CTRL"] * n_per + ["p1"] * n_per + ["p2"] * n_per)
    control_mask = labels == "CTRL"
    return X, labels, control_mask


class TestStructuredCritiqueEmitted:
    def test_rejected_run_populates_critique(self) -> None:
        X, labels, ctrl = _toy_matrix(30, seed=2026)
        bad = _BadBackbone()
        report = score_and_gate(
            backbone=bad,
            X=X,
            labels=labels,
            control_mask=ctrl,
            held_out="p1",
            held_out_target_idx=0,
            threshold_msd=0.01,
        )
        assert isinstance(report, ExecutedValidation)
        assert not report.accepted
        assert report.critique is not None
        assert len(report.critique.which_genes_failed) > 0
        assert "accept" not in report.critique.accept_reason.lower()

    def test_accepted_run_has_empty_failed_genes(self) -> None:
        X, labels, ctrl = _toy_matrix(30, seed=2027)
        truth = np.mean(X[labels == "p1"], axis=0) - np.mean(X[ctrl], axis=0)
        perfect = _PerfectBackbone(truth)
        report = score_and_gate(
            backbone=perfect,
            X=X,
            labels=labels,
            control_mask=ctrl,
            held_out="p1",
            held_out_target_idx=0,
            threshold_msd=0.5,
        )
        assert report.accepted
        assert report.critique.which_genes_failed == ()

    def test_delta_suggests_smaller_lr_on_rejection(self) -> None:
        X, labels, ctrl = _toy_matrix(30, seed=2028)
        bad = _BadBackbone()
        report = score_and_gate(
            backbone=bad,
            X=X,
            labels=labels,
            control_mask=ctrl,
            held_out="p1",
            held_out_target_idx=0,
            threshold_msd=0.01,
        )
        delta = report.critique.suggested_next_config_delta
        # Heuristic: on rejection we suggest *something* — lr, backbone, or epochs.
        assert delta, "empty delta on a rejected run"
        assert set(delta) & {"learning_rate", "backbone", "epochs", "ridge_lambda"}


class TestSuggestConfigDelta:
    def test_empty_when_accepted(self) -> None:
        delta = suggest_config_delta(
            accepted=True, msd=0.01, threshold_msd=0.1,
            current_backbone="linear", deg_sign_agreement=0.9,
        )
        assert delta == {}

    def test_switches_backbone_when_sign_agreement_low(self) -> None:
        delta = suggest_config_delta(
            accepted=False, msd=0.5, threshold_msd=0.1,
            current_backbone="linear", deg_sign_agreement=0.3,
        )
        assert "backbone" in delta
        assert delta["backbone"] != "linear"

    def test_lowers_lr_when_msd_high_but_sign_ok(self) -> None:
        delta = suggest_config_delta(
            accepted=False, msd=0.5, threshold_msd=0.1,
            current_backbone="linear", deg_sign_agreement=0.75,
        )
        # Direction is right but magnitude off — try smaller LR.
        assert "learning_rate" in delta or "ridge_lambda" in delta
