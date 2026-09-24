"""Unit tests for the Norman 2019 loader.

Norman (scPerturb bundle) encodes double knockdowns as ``GENE_A_GENE_B``
(``_``-joined, e.g. ``CBL_UBASH3A``) in the ``obs.perturbation`` column. Control cells are ``non-targeting`` (or
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
        "JUN_FOS",
        "MYC_KLF4",
        "JUN_ELK1",
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
        # At least one doublet uses the _ delimiter and is preserved.
        doublets = {p for p in perts if "_" in p}
        assert len(doublets) > 0, f"no doublets found in {perts}"

    def test_singleton_targets_indexed(self, norman_h5ad: Path) -> None:
        from perturb_eval.experiments.norman import load_norman_matrix

        ds = load_norman_matrix(norman_h5ad)
        singletons = {p for p in ds["perturbations"] if "_" not in p}
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


class TestNormanDoubletsAndMissingTargets:
    """C-RG-2 / A4 / D1: ``_``-joined doublets resolve to 2-tuples; a target
    outside the HVG cut raises instead of being replaced by a random gene."""

    def test_underscore_doublet_maps_to_both_target_columns(self, norman_h5ad: Path) -> None:
        from perturb_eval.experiments.norman import load_norman_matrix

        ds = load_norman_matrix(norman_h5ad)
        col = {g: i for i, g in enumerate(ds["gene_names"])}
        assert ds["target_gene_idx"]["JUN_FOS"] == (col["JUN"], col["FOS"])
        assert ds["target_gene_idx"]["MYC_KLF4"] == (col["MYC"], col["KLF4"])
        # Singletons are 1-tuples under the D1 contract.
        assert ds["target_gene_idx"]["JUN"] == (col["JUN"],)
        assert "JUN_FOS" in ds["perturbations"]

    # T8b (CTO #227): this test used to assert the OLD behaviour — a zero-variance
    # target "falls outside" a loader-level HVG cut ranked on ALL cells and
    # raises. The loader no longer cuts genes (HVG is per held-out task on
    # training cells only), so that low-variance target now resolves; a target
    # truly absent from the gene vocabulary still raises.
    @staticmethod
    def _write_lowvar(path: Path, gene_names: np.ndarray) -> None:
        import anndata as ad
        from scipy.sparse import csr_matrix

        n_genes = len(gene_names)
        labels = ["non-targeting"] * 20 + ["JUN"] * 20 + ["LOWVAR"] * 20
        X = np.tile(np.arange(1, n_genes + 1, dtype=np.float32), (len(labels), 1))
        X[: len(labels) // 2] *= 3.0  # variance in every column ...
        X[:, 1] = 1.0  # ... except column 1's
        adata = ad.AnnData(
            X=csr_matrix(X),
            obs={"perturbation": np.array(labels)},
            var={"gene_symbol": gene_names},
        )
        adata.write_h5ad(path)

    def test_low_variance_target_is_kept_no_loader_hvg_cut(self, tmp_path: Path) -> None:
        from perturb_eval.experiments.norman import load_norman_matrix

        gene_names = np.array([f"GENE{i:03d}" for i in range(30)])
        gene_names[0], gene_names[1] = "JUN", "LOWVAR"
        path = tmp_path / "norman_lowvar.h5ad"
        self._write_lowvar(path, gene_names)
        ds = load_norman_matrix(path, n_top_hvg=10)
        assert ds["X"].shape[1] == 30  # full vocabulary
        assert ds["target_gene_idx"]["LOWVAR"] == (1,)
        assert ds["hvg_n_top"] == 10

    def test_singleton_absent_from_vocab_raises(self, tmp_path: Path) -> None:
        from perturb_eval.experiments.norman import load_norman_matrix

        gene_names = np.array([f"GENE{i:03d}" for i in range(30)])
        gene_names[0] = "JUN"  # "LOWVAR" is not a gene in this vocabulary
        path = tmp_path / "norman_absent.h5ad"
        self._write_lowvar(path, gene_names)
        with pytest.raises(ValueError, match="LOWVAR"):
            load_norman_matrix(path, n_top_hvg=10)


class TestNormanIntegration:
    """End-to-end: Norman loader output must feed LinearBackbone without error."""

    def test_linear_backbone_fits_on_norman(self, norman_h5ad: Path) -> None:
        from perturb_eval.backbones import BackboneTrainConfig, LinearBackbone
        from perturb_eval.experiments.norman import load_norman_matrix

        ds = load_norman_matrix(norman_h5ad)
        singletons = [p for p in ds["perturbations"] if "_" not in p]
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
