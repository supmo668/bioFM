"""Unit tests for the Norman 2019 loader.

Norman encodes double knockdowns as ``GENE_A+GENE_B`` in the
``obs.perturbation`` column. Control cells are ``non-targeting`` (or
``ctrl`` depending on repack). The loader must return the same canonical
dict shape as :func:`load_adamson_matrix` so all downstream backbones work
unchanged.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("anndata")
pytest.importorskip("scipy")


def _make_norman_fixture(path: Path, *, n_cells: int = 600, n_genes: int = 100) -> None:
    """Write a minimal h5ad mimicking scPerturb's Norman packaging."""
    import anndata as ad
    from scipy.sparse import csr_matrix

    rng = np.random.default_rng(2026)

    # Mix of singletons, doublets, and controls.
    pert_pool = [
        "non-targeting",
        "JUN",
        "FOS",
        "MYC",
        "KLF4",
        "ELK1",
        "JUN+FOS",
        "MYC+KLF4",
        "JUN+ELK1",
    ]
    perturbation = rng.choice(pert_pool, size=n_cells)

    # Counts: controls stay near 1, perturbed cells get target-gene shift.
    gene_names = np.array([f"GENE{i:03d}" for i in range(n_genes)])
    # Ensure the targets actually live in the vocab.
    for i, g in enumerate(["JUN", "FOS", "MYC", "KLF4", "ELK1"]):
        gene_names[i] = g

    X = np.abs(rng.normal(loc=1.0, scale=0.5, size=(n_cells, n_genes))).astype(np.float32)

    adata = ad.AnnData(
        X=csr_matrix(X),
        obs={"perturbation": perturbation.astype(str)},
        var={"gene_symbol": gene_names},
    )
    adata.obs["perturbation"] = adata.obs["perturbation"].astype("category")
    adata.write_h5ad(path)


@pytest.fixture
def norman_h5ad(tmp_path: Path) -> Path:
    path = tmp_path / "NormanWeissman2019.h5ad"
    _make_norman_fixture(path)
    return path


class TestLoadNormanMatrix:
    def test_returns_canonical_dict(self, norman_h5ad: Path) -> None:
        from perturb_eval.experiments.norman import load_norman_matrix

        ds = load_norman_matrix(norman_h5ad)
        for key in {
            "X",
            "labels",
            "control_mask",
            "target_gene_idx",
            "perturbations",
            "gene_names",
        }:
            assert key in ds, f"missing key {key!r}"

    def test_X_is_log1p_normalised(self, norman_h5ad: Path) -> None:
        from perturb_eval.experiments.norman import load_norman_matrix

        ds = load_norman_matrix(norman_h5ad)
        assert ds["X"].shape[0] > 0
        assert ds["X"].shape[1] > 0
        # log1p of small counts should keep values modest.
        assert ds["X"].max() < 20.0
        assert ds["X"].min() >= 0.0

    def test_control_mask_detects_non_targeting(self, norman_h5ad: Path) -> None:
        from perturb_eval.experiments.norman import load_norman_matrix

        ds = load_norman_matrix(norman_h5ad)
        assert ds["control_mask"].sum() > 0
        # Control cells are labeled CTRL in the canonical dict.
        assert (ds["labels"][ds["control_mask"]] == "CTRL").all()

    def test_double_kd_preserved_in_perturbations(self, norman_h5ad: Path) -> None:
        from perturb_eval.experiments.norman import load_norman_matrix

        ds = load_norman_matrix(norman_h5ad)
        perts = set(ds["perturbations"])
        # At least one doublet uses the + delimiter and is preserved.
        doublets = {p for p in perts if "+" in p}
        assert len(doublets) > 0, f"no doublets found in {perts}"

    def test_singleton_targets_indexed(self, norman_h5ad: Path) -> None:
        from perturb_eval.experiments.norman import load_norman_matrix

        ds = load_norman_matrix(norman_h5ad)
        singletons = {p for p in ds["perturbations"] if "+" not in p}
        for s in singletons:
            assert s in ds["target_gene_idx"], f"{s} missing from target_gene_idx"

    def test_excludes_controls_from_perturbations(self, norman_h5ad: Path) -> None:
        from perturb_eval.experiments.norman import load_norman_matrix

        ds = load_norman_matrix(norman_h5ad)
        assert "non-targeting" not in ds["perturbations"]
        assert "CTRL" not in ds["perturbations"]

    def test_deterministic_across_calls(self, norman_h5ad: Path) -> None:
        from perturb_eval.experiments.norman import load_norman_matrix

        ds1 = load_norman_matrix(norman_h5ad)
        ds2 = load_norman_matrix(norman_h5ad)
        assert np.array_equal(ds1["X"], ds2["X"])
        assert list(ds1["perturbations"]) == list(ds2["perturbations"])


class TestNormanIntegration:
    """End-to-end: Norman loader output must feed LinearBackbone without error."""

    def test_linear_backbone_fits_on_norman(self, norman_h5ad: Path) -> None:
        from perturb_eval.backbones import BackboneTrainConfig, LinearBackbone
        from perturb_eval.experiments.norman import load_norman_matrix

        ds = load_norman_matrix(norman_h5ad)
        singletons = [p for p in ds["perturbations"] if "+" not in p]
        assert len(singletons) >= 2
        held = singletons[0]

        train_mask = ds["labels"] != held
        train_targets = {p: ds["target_gene_idx"][p] for p in singletons if p != held}

        bb = LinearBackbone()
        bb.fit(
            ds["X"][train_mask],
            ds["labels"][train_mask].tolist(),
            ds["control_mask"][train_mask],
            train_targets,
            BackboneTrainConfig(max_iter=5, learning_rate=1e-2, ridge_lambda=1.0, seed=1),
        )
        pred = bb.predict_logfc(held, ds["target_gene_idx"][held], n_genes=ds["X"].shape[1])
        assert np.all(np.isfinite(pred))
