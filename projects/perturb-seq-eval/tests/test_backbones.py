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


# ---------------------------------------------------------------------------
# T9 / D1 — multi-target contract: ``target_gene_idx: Mapping[str, tuple[int, ...]]``
# ---------------------------------------------------------------------------

# Regression pin captured from the pre-T9 single-int code path (commit 16f4f54)
# on ``_pin_setup()``. A 1-tuple and a plain int must reproduce these
# bit-for-bit (rtol=0, atol=0).
_PIN_LINEAR = [
    0.0018316583237388457, -0.08090151514344297, 0.009073835886043824,
    0.00114820377095907, 0.05077691989006361, -0.6317395604314169,
    0.01801914330536336, -0.06555686935383834, 0.06152788966762908,
    0.06207339829435761, -0.6331045698353186, 0.009449865180770992,
    -0.011774689481254633, 0.06684052376052133, 0.1031091229110146,
    -1.944742291219042,
]
_PIN_MLP = [
    -0.009365195013296586, -0.14963805361775354, 0.19098722259695713,
    -0.2678582565891176, 0.40536695483053803, -0.9189982415483317,
    0.37012031111759813, -0.32211288458697085, -0.37221127966963297,
    0.18888931797622535, -0.9502761244104112, -0.09854404831468926,
    0.182800894177524, 0.5907664585269514, -0.03091329616600319,
    -0.2854345396762541,
]


def _pin_setup() -> tuple[dict, str, np.ndarray]:
    ds = _toy_dataset(n_cells=120, n_genes=16, perturbations=("A", "B", "C"), seed=7)
    held = "C"
    return ds, held, ds["labels"] != held


def _pin_predict(cls, as_tuple: bool) -> np.ndarray:
    ds, held, m = _pin_setup()
    wrap = (lambda i: (i,)) if as_tuple else (lambda i: i)
    tg = {p: wrap(i) for p, i in ds["target_gene_idx"].items() if p != held}
    bb = cls()
    bb.fit(ds["X"][m], ds["labels"][m].tolist(), ds["control_mask"][m], tg,
           BackboneTrainConfig(seed=11, max_iter=50))
    return bb.predict_logfc(held, wrap(ds["target_gene_idx"][held]), 16)


@pytest.mark.unit
@pytest.mark.parametrize("cls,pin", [(LinearBackbone, _PIN_LINEAR), (MLPBackbone, _PIN_MLP)])
@pytest.mark.parametrize("as_tuple", [False, True], ids=["int", "1-tuple"])
def test_single_target_regression_pin_bit_exact(cls, pin, as_tuple: bool) -> None:
    pred = _pin_predict(cls, as_tuple)
    np.testing.assert_allclose(pred, np.asarray(pin), rtol=0, atol=0)
    assert pred.tobytes() == np.asarray(pin, dtype=np.float64).tobytes()


def _doublet_dataset() -> tuple[dict, dict[str, tuple[int, ...]]]:
    """Toy data plus a doublet ``A_B`` knocking down columns 3 and 5."""
    ds = _toy_dataset(n_cells=200, n_genes=20, perturbations=("A", "B", "C"), seed=3)
    rng = np.random.default_rng(99)
    rows = rng.standard_normal((40, 20)) * 0.3 + 2.0
    rows[:, 3] -= 2.0
    rows[:, 5] -= 1.0
    ds["X"] = np.vstack([ds["X"], rows])
    ds["labels"] = np.concatenate([ds["labels"], np.asarray(["A_B"] * 40)])
    ds["control_mask"] = ds["labels"] == "CTRL"
    targets = {p: (i,) for p, i in ds["target_gene_idx"].items()}
    targets["A_B"] = (3, 5)
    return ds, targets


@pytest.mark.unit
class TestMultiTarget:
    def test_as_targets_helper(self) -> None:
        from perturb_eval.backbones.base import _as_targets

        assert _as_targets(4) == (4,)
        assert _as_targets(np.int64(4)) == (4,)
        assert _as_targets((3, 5)) == (3, 5)
        assert _as_targets([3, 5]) == (3, 5)
        assert all(type(i) is int for i in _as_targets((np.int64(3), 5)))

    def test_linear_doublet_dip_is_mean_of_target_columns(self) -> None:
        ds, targets = _doublet_dataset()
        bb = LinearBackbone()
        bb.fit(ds["X"], ds["labels"].tolist(), ds["control_mask"], targets, BackboneTrainConfig())
        # Recompute the dip feature independently: mean over each
        # perturbation's target columns, then mean across perturbations.
        mu_ctrl = ds["X"][ds["control_mask"]].mean(axis=0)
        dips = []
        for p, idx in targets.items():
            lfc = ds["X"][ds["labels"] == p].mean(axis=0) - mu_ctrl
            dips.append(lfc[list(idx)].mean())
        assert bb._target_dip == pytest.approx(float(np.mean(dips)), abs=1e-12)
        # A_B's own contribution is the mean of columns 3 and 5 (≈ -1.5).
        lfc_ab = ds["X"][ds["labels"] == "A_B"].mean(axis=0) - mu_ctrl
        assert lfc_ab[[3, 5]].mean() == pytest.approx(-1.5, abs=0.2)

    def test_linear_predict_writes_dip_into_every_target(self) -> None:
        ds, targets = _doublet_dataset()
        held = "A_B"
        m = ds["labels"] != held
        bb = LinearBackbone()
        bb.fit(ds["X"][m], ds["labels"][m].tolist(), ds["control_mask"][m],
               {p: t for p, t in targets.items() if p != held}, BackboneTrainConfig())
        pred = bb.predict_logfc(held, (3, 5), n_genes=20)
        assert pred[3] == bb._target_dip
        assert pred[5] == bb._target_dip
        assert pred[4] != bb._target_dip
        # out-of-range members are ignored, in-range ones still written
        pred2 = bb.predict_logfc(held, (3, 999), n_genes=20)
        assert pred2[3] == bb._target_dip

    def test_mlp_doublet_fit_and_predict(self) -> None:
        ds, targets = _doublet_dataset()
        bb = MLPBackbone()
        art = bb.fit(ds["X"], ds["labels"].tolist(), ds["control_mask"], targets,
                     BackboneTrainConfig(max_iter=20))
        assert art.n_train_perturbations == 4
        pred = bb.predict_logfc("A_B", (3, 5), n_genes=20)
        assert pred.shape == (20,) and np.all(np.isfinite(pred))
        # doublet features differ from either singleton
        assert not np.array_equal(pred, bb.predict_logfc("A", (3,), n_genes=20))

    def test_scgpt_small_doublet_fit_and_predict(self) -> None:
        pytest.importorskip("torch")
        from perturb_eval.backbones import SCGPTSmallBackbone
        from perturb_eval.backbones.scgpt_small import _ArchitectureConfig

        ds, targets = _doublet_dataset()
        arch = _ArchitectureConfig(embed_dim=16, n_layers=1, n_heads=2, ffn_dim=32)
        bb = SCGPTSmallBackbone(arch)
        art = bb.fit(ds["X"], ds["labels"].tolist(), ds["control_mask"], targets,
                     BackboneTrainConfig(max_iter=5))
        assert art.n_train_perturbations == 4
        pred = bb.predict_logfc("A_B", (3, 5), n_genes=20)
        assert pred.shape == (20,) and np.all(np.isfinite(pred))
        # 1-tuple and plain int take the identical path
        np.testing.assert_array_equal(
            bb.predict_logfc("A", (3,), n_genes=20), bb.predict_logfc("A", 3, n_genes=20)
        )
