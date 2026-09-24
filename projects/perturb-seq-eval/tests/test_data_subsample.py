"""Unit tests for the fair stratified subsampler.

The subsampler is the "fairness" contract between the paper and the
reviewer: given a list of candidate perturbations with a stratification
attribute (e.g. binned |logFC| strength), the subsampler returns a
reproducible subset that is balanced across strata at a fixed seed.
"""

from __future__ import annotations

import numpy as np
import pytest

from perturb_eval.data.subsample import stratified_subsample


class TestStratifiedSubsample:
    def test_determinism_same_seed_same_output(self) -> None:
        labels = np.array(["a", "b", "c", "d", "e", "f", "g", "h", "i"])
        strata = np.array([0, 0, 0, 1, 1, 1, 2, 2, 2])
        out1 = stratified_subsample(labels, strata, n_per_stratum=2, seed=2026)
        out2 = stratified_subsample(labels, strata, n_per_stratum=2, seed=2026)
        assert np.array_equal(out1, out2)

    def test_different_seed_different_output(self) -> None:
        labels = np.array([f"lbl{i}" for i in range(30)])
        strata = np.array([i % 3 for i in range(30)])
        out1 = stratified_subsample(labels, strata, n_per_stratum=3, seed=2026)
        out2 = stratified_subsample(labels, strata, n_per_stratum=3, seed=4242)
        assert not np.array_equal(out1, out2)

    def test_exactly_n_per_stratum(self) -> None:
        labels = np.array([f"lbl{i}" for i in range(30)])
        strata = np.array([i % 3 for i in range(30)])
        result = stratified_subsample(labels, strata, n_per_stratum=3, seed=2026)
        result_strata = strata[np.isin(labels, result)]
        assert (result_strata == 0).sum() == 3
        assert (result_strata == 1).sum() == 3
        assert (result_strata == 2).sum() == 3

    def test_returns_labels_not_indices(self) -> None:
        labels = np.array(["aaa", "bbb", "ccc", "ddd"])
        strata = np.array([0, 0, 1, 1])
        result = stratified_subsample(labels, strata, n_per_stratum=1, seed=2026)
        assert result.dtype.kind in ("U", "O")
        assert set(result) <= set(labels)

    def test_stratum_smaller_than_n_keeps_all(self) -> None:
        labels = np.array(["a", "b", "c", "d"])
        strata = np.array([0, 0, 1, 1])
        result = stratified_subsample(labels, strata, n_per_stratum=5, seed=2026)
        assert set(result) == {"a", "b", "c", "d"}

    def test_rejects_mismatched_shapes(self) -> None:
        labels = np.array(["a", "b", "c"])
        strata = np.array([0, 1])
        with pytest.raises(ValueError):
            stratified_subsample(labels, strata, n_per_stratum=1, seed=2026)

    def test_sorted_output_for_reproducibility(self) -> None:
        labels = np.array(["z", "a", "m", "b", "c"])
        strata = np.array([0, 0, 1, 1, 1])
        result = stratified_subsample(labels, strata, n_per_stratum=2, seed=2026)
        assert list(result) == sorted(result), "output must be sorted for provenance"


class TestStratifiedSubsampleExactFill:
    """T11: ``n_total`` tops up an under-filled stratified draw to exactly n."""

    def test_underfill_topped_up_to_n_total(self) -> None:
        labels = np.array([f"lbl{i}" for i in range(10)])
        strata = np.array([0] * 8 + [1] * 2)
        # per-stratum 3 -> 3 + 2 = 5; n_total asks for 6.
        out = stratified_subsample(labels, strata, n_per_stratum=3, seed=2026, n_total=6)
        assert len(out) == 6 and len(set(out)) == 6
        assert list(out) == sorted(out)
        again = stratified_subsample(labels, strata, n_per_stratum=3, seed=2026, n_total=6)
        assert np.array_equal(out, again)

    def test_n_total_keeps_the_per_stratum_draw(self) -> None:
        labels = np.array([f"lbl{i}" for i in range(10)])
        strata = np.array([0] * 8 + [1] * 2)
        base = stratified_subsample(labels, strata, n_per_stratum=3, seed=2026)
        topped = stratified_subsample(labels, strata, n_per_stratum=3, seed=2026, n_total=7)
        assert set(base) <= set(topped)

    def test_n_total_caps_at_pool_size(self) -> None:
        labels = np.array(["a", "b", "c"])
        strata = np.array([0, 0, 1])
        out = stratified_subsample(labels, strata, n_per_stratum=1, seed=2026, n_total=5)
        assert set(out) == {"a", "b", "c"}


class TestMeanAbsLogfcTupleTargets:
    X = np.array(
        [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0],   # CTRL
         [1.5, 0.2, 0.0], [2.5, 0.4, 0.0],   # pA
         [0.0, -3.0, 1.0], [0.0, -1.0, 3.0]],  # pAB
        dtype=np.float32,
    )
    labels = np.array(["CTRL", "CTRL", "pA", "pA", "pAB", "pAB"])

    def test_one_tuple_equals_int_exactly(self) -> None:
        from perturb_eval.data import mean_abs_logfc_per_target

        ctrl = self.labels == "CTRL"
        a = mean_abs_logfc_per_target(self.X, self.labels, ctrl, {"pA": 0, "pAB": 1})
        b = mean_abs_logfc_per_target(self.X, self.labels, ctrl, {"pA": (0,), "pAB": (1,)})
        assert a == b  # exact equality, not approx
        assert a["pA"] == 2.0

    def test_two_tuple_is_mean_over_targets(self) -> None:
        from perturb_eval.data import mean_abs_logfc_per_target

        ctrl = self.labels == "CTRL"
        out = mean_abs_logfc_per_target(self.X, self.labels, ctrl, {"pAB": (1, 2)})
        # |mean col1| = 2.0, |mean col2| = 2.0 -> 2.0; use asymmetric check too
        assert out["pAB"] == 2.0
        out2 = mean_abs_logfc_per_target(self.X, self.labels, ctrl, {"pA": (0, 1)})
        assert out2["pA"] == pytest.approx((2.0 + 0.3) / 2)
