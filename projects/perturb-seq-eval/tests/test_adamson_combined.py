"""Combined Adamson loader + per-target |logFC| stratifier tests."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("anndata")


def _write_synthetic_adamson(
    path: Path,
    *,
    tf_names: list[str],
    n_cells_per_pert: int = 30,
    n_genes: int = 50,
    seed: int = 0,
) -> None:
    """Write a minimal h5ad matching scPerturb's Adamson packaging."""
    import anndata as ad
    from scipy.sparse import csr_matrix

    rng = np.random.default_rng(seed)
    # Build a shared base vocab, then overwrite a FIXED, reserved block of
    # slots with every TF name that could appear across any subset — so
    # the combined loader's vocab-intersection step retains them.
    gene_names = np.array([f"GENE{i:03d}" for i in range(n_genes)])
    reserved = ["TFA", "TFB", "TFC", "TFD", "TFE", "TFF"]
    for i, tf in enumerate(reserved[: min(len(reserved), n_genes)]):
        gene_names[i] = tf

    labels = []
    rows = []
    # Controls (use "*" as Adamson pilot does).
    for _ in range(n_cells_per_pert):
        rows.append(rng.gamma(2.0, 1.0, size=n_genes))
        labels.append("*")
    # Perturbations — each TF shifts its own gene down.
    for i, tf in enumerate(tf_names):
        for _ in range(n_cells_per_pert):
            row = rng.gamma(2.0, 1.0, size=n_genes)
            row[i] *= 0.3  # knockdown
            rows.append(row)
            labels.append(f"{tf}_pDS263")

    X = np.vstack(rows).astype(np.float32)
    adata = ad.AnnData(
        X=csr_matrix(X),
        obs={"perturbation": np.array(labels)},
        var={"gene_symbol": gene_names},
    )
    adata.obs["perturbation"] = adata.obs["perturbation"].astype("category")
    # scPerturb packs as CSC; round-trip through anndata — pyarrow-ish.
    adata.write_h5ad(path)


class TestLoadAdamsonCombined:
    def test_concatenates_two_subsets(self, tmp_path: Path) -> None:
        from perturb_eval.experiments.e2_adamson import load_adamson_combined

        p1 = tmp_path / "pilot.h5ad"
        p2 = tmp_path / "subset2.h5ad"
        _write_synthetic_adamson(p1, tf_names=["TFA", "TFB"], seed=1)
        _write_synthetic_adamson(p2, tf_names=["TFC", "TFD"], seed=2)

        # Use n_top_hvg >= n_genes so no HVG cut drops target TFs.
        ds = load_adamson_combined([p1, p2], n_top_hvg=100, max_cells_per_pert=50)
        # All four TFs must be represented.
        assert "TFA" in ds["target_gene_idx"]
        assert "TFD" in ds["target_gene_idx"]
        # Shared vocab must still contain each TF.
        assert "TFA" in ds["gene_names"]
        assert "TFD" in ds["gene_names"]

    def test_single_subset_still_works(self, tmp_path: Path) -> None:
        from perturb_eval.experiments.e2_adamson import load_adamson_combined

        p = tmp_path / "one.h5ad"
        _write_synthetic_adamson(p, tf_names=["TFA", "TFB"], seed=1)
        ds = load_adamson_combined([p], n_top_hvg=100, max_cells_per_pert=30)
        assert set(ds["perturbations"]) <= {"TFA", "TFB"}
        assert "CTRL" in ds["labels"]

    def test_empty_paths_raises(self) -> None:
        from perturb_eval.experiments.e2_adamson import load_adamson_combined

        with pytest.raises(ValueError):
            load_adamson_combined([])


class TestMeanAbsLogfcPerTarget:
    def test_returns_one_entry_per_target(self) -> None:
        from perturb_eval.data import mean_abs_logfc_per_target

        rng = np.random.default_rng(0)
        X = rng.normal(0.0, 0.1, size=(90, 10)).astype(np.float64)
        labels = np.array(["CTRL"] * 30 + ["pA"] * 30 + ["pB"] * 30)
        ctrl = labels == "CTRL"
        # Bake a stronger signal into pA than pB.
        X[labels == "pA", 0] += 2.0
        X[labels == "pB", 1] += 0.5
        out = mean_abs_logfc_per_target(X, labels, ctrl, {"pA": 0, "pB": 1})
        assert set(out) == {"pA", "pB"}
        assert out["pA"] > out["pB"]

    def test_skips_perts_with_no_cells(self) -> None:
        from perturb_eval.data import mean_abs_logfc_per_target

        X = np.zeros((30, 5))
        labels = np.array(["CTRL"] * 30)
        ctrl = labels == "CTRL"
        out = mean_abs_logfc_per_target(X, labels, ctrl, {"ghost": 0})
        assert out == {}
