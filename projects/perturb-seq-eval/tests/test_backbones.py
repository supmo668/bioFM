"""Unit tests for the backbone predictors.

See docs/SUPPLEMENT_DESIGN.md §3. Backbones share a Protocol so the
optimizer and experiment runners can swap them without touching call
sites. The ``scgpt_small`` backbone depends on PyTorch and is covered by
integration tests that skip when torch is unavailable.
"""

from __future__ import annotations

import numpy as np
import pytest

from perturb_eval.backbones import (
    BackboneTrainConfig,
    LinearBackbone,
    MLPBackbone,
    mean_squared_deviation,
    available_backbones,
    build_backbone,
)


# ---------------------------------------------------------------------------
# Synthetic toy dataset used to exercise every backbone
# ---------------------------------------------------------------------------


def _toy_dataset(
    n_cells: int = 400,
    n_genes: int = 40,
    perturbations: tuple[str, ...] = ("A", "B", "C", "D"),
    seed: int = 0,
) -> dict:
    """Tiny Adamson-like dataset: log-FC of each perturbation is a fixed
    deterministic pattern so that any competent backbone can recover it.
    """
    rng = np.random.default_rng(seed)
    target_gene_idx: dict[str, int] = {p: 5 * (i + 1) for i, p in enumerate(perturbations)}
    all_labels: list[str] = []
    expression_rows: list[np.ndarray] = []

    # 25% of cells are non-targeting controls.
    n_control = n_cells // 4
    base = rng.standard_normal((n_control, n_genes)).astype(np.float64) * 0.3 + 2.0
    expression_rows.append(base)
    all_labels.extend(["CTRL"] * n_control)

    # Each perturbation downregulates its target by ~2 log units + noise.
    per_pert = (n_cells - n_control) // len(perturbations)
    for p in perturbations:
        rows = rng.standard_normal((per_pert, n_genes)).astype(np.float64) * 0.3 + 2.0
        rows[:, target_gene_idx[p]] -= 2.0
        expression_rows.append(rows)
        all_labels.extend([p] * per_pert)

    X = np.vstack(expression_rows)
    labels = np.asarray(all_labels)
    control_mask = labels == "CTRL"
    return {
        "X": X,
        "labels": labels,
        "control_mask": control_mask,
        "target_gene_idx": target_gene_idx,
    }


def _held_out_truth(ds: dict, held: str) -> np.ndarray:
    """Ground-truth log-FC for the held-out perturbation, measured on data.

    Expression is synthesized in log1p space, so the log-FC is just the
    difference of mean vectors (matches :func:`log_fold_change`).
    """
    X = ds["X"]
    mask_ctrl = ds["control_mask"]
    mask_p = ds["labels"] == held
    return np.mean(X[mask_p], axis=0) - np.mean(X[mask_ctrl], axis=0)


# ---------------------------------------------------------------------------
# Common Protocol conformance checks
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.parametrize("name", ["linear", "mlp"])
class TestBackboneProtocol:
    def test_predict_returns_correct_shape(self, name: str) -> None:
        ds = _toy_dataset()
        bb = build_backbone(name)
        held = "D"
        train_mask = ds["labels"] != held
        bb.fit(
            ds["X"][train_mask],
            ds["labels"][train_mask].tolist(),
            ds["control_mask"][train_mask],
            {p: idx for p, idx in ds["target_gene_idx"].items() if p != held},
            BackboneTrainConfig(),
        )
        pred = bb.predict_logfc(held, ds["target_gene_idx"][held], n_genes=ds["X"].shape[1])
        assert pred.shape == (ds["X"].shape[1],)
        assert np.all(np.isfinite(pred))

    def test_msd_finite_on_held_out(self, name: str) -> None:
        ds = _toy_dataset()
        bb = build_backbone(name)
        held = "C"
        train_mask = ds["labels"] != held
        bb.fit(
            ds["X"][train_mask],
            ds["labels"][train_mask].tolist(),
            ds["control_mask"][train_mask],
            {p: idx for p, idx in ds["target_gene_idx"].items() if p != held},
            BackboneTrainConfig(seed=2026),
        )
        pred = bb.predict_logfc(held, ds["target_gene_idx"][held], n_genes=ds["X"].shape[1])
        truth = _held_out_truth(ds, held)
        top_k = np.argsort(np.abs(truth))[-10:]
        msd = mean_squared_deviation(pred, truth, top_k)
        assert np.isfinite(msd)
        assert msd >= 0

    def test_registered_in_catalog(self, name: str) -> None:
        assert name in available_backbones()


# ---------------------------------------------------------------------------
# Linear-specific behaviour
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestLinearBackbone:
    def test_name(self) -> None:
        assert LinearBackbone().name == "linear"

    def test_target_gene_gets_downregulated(self) -> None:
        """On the toy DGP every perturbation crushes its target gene by ~2
        log units. A trained linear backbone should assign a **negative**
        log-FC to the target gene of the held-out perturbation."""
        ds = _toy_dataset()
        bb = LinearBackbone()
        held = "B"
        train_mask = ds["labels"] != held
        bb.fit(
            ds["X"][train_mask],
            ds["labels"][train_mask].tolist(),
            ds["control_mask"][train_mask],
            {p: idx for p, idx in ds["target_gene_idx"].items() if p != held},
            BackboneTrainConfig(),
        )
        pred = bb.predict_logfc(held, ds["target_gene_idx"][held], n_genes=ds["X"].shape[1])
        assert pred[ds["target_gene_idx"][held]] < -0.5


# ---------------------------------------------------------------------------
# MLP-specific behaviour
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestMLPBackbone:
    def test_name(self) -> None:
        assert MLPBackbone().name == "mlp"

    def test_deterministic_with_same_seed(self) -> None:
        ds = _toy_dataset()
        preds = []
        for _ in range(2):
            bb = MLPBackbone()
            held = "A"
            train_mask = ds["labels"] != held
            bb.fit(
                ds["X"][train_mask],
                ds["labels"][train_mask].tolist(),
                ds["control_mask"][train_mask],
                {p: idx for p, idx in ds["target_gene_idx"].items() if p != held},
                BackboneTrainConfig(seed=42),
            )
            preds.append(
                bb.predict_logfc(held, ds["target_gene_idx"][held], n_genes=ds["X"].shape[1])
            )
        np.testing.assert_allclose(preds[0], preds[1], atol=1e-8)


# ---------------------------------------------------------------------------
# MSD helper
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestMSD:
    def test_zero_on_exact_prediction(self) -> None:
        truth = np.array([1.0, 2.0, 3.0, 4.0])
        assert mean_squared_deviation(truth.copy(), truth, np.arange(4)) == 0.0

    def test_positive_on_wrong_prediction(self) -> None:
        truth = np.array([1.0, 2.0, 3.0, 4.0])
        pred = np.array([1.0, 2.0, 0.0, 4.0])
        # Only index 2 differs → (3-0)^2 / 1 = 9 on a 1-element top-K
        assert mean_squared_deviation(pred, truth, np.array([2])) == pytest.approx(9.0)

    def test_mean_not_sum(self) -> None:
        truth = np.zeros(4)
        pred = np.ones(4)
        assert mean_squared_deviation(pred, truth, np.arange(4)) == pytest.approx(1.0)
