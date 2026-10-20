"""A7 realised-structure tests.

Unit tests over **hand-constructed** rosters, per the r1.5/r1.6 rule: a function is
tested over its domain, not over the subset a study happens to reach. Every test
that names a branch asserts the branch was taken.

**r1.6c — the previous suite passed 12/12 while ten mutations survived it.** The
root cause was that its only exact-value assertion sat at `[5]*8`, the single point
where the arithmetic mean, the size-weighted mean and the max all equal 5, so every
competing definition of `m_A` agreed there. Every other numeric assertion was an
inequality, which cannot pin a formula. The module's entire thesis had no test that
could distinguish it from `m_A = max(sizes)`.
"""

from __future__ import annotations

import statistics

import pytest

from chipsim.audit.power import effective_n
from chipsim.audit.series import (
    cluster_by_scaffold,
    design_effect,
    effective_n_unequal,
    measure_series_structure,
    murcko_scaffold,
    structure_over_icc_range,
)

# Four para-substituted benzanilides (one analog series, identical Murcko
# scaffold) plus three structurally distinct singletons.
SERIES = [
    "O=C(Nc1ccccc1)c1ccc(C)cc1",
    "O=C(Nc1ccccc1)c1ccc(Cl)cc1",
    "O=C(Nc1ccccc1)c1ccc(F)cc1",
    "O=C(Nc1ccccc1)c1ccc(OC)cc1",
]
SINGLETONS = ["c1ccc2[nH]ccc2c1", "C1CCNCC1", "c1ccc(-c2ccncc2)cc1"]
# Topologically identical to SERIES but chemically distinct: same GENERIC
# framework, different Murcko scaffold. Pins the abstraction level.
PYRIDYL = "O=C(Nc1ccccc1)c1ccncc1"
# A textbook acyclic analog series. Murcko is blind to it.
FATTY_ACIDS = [
    "CCCCCCCC(=O)O",
    "CCCCCCCCC(=O)O",
    "CCCCCCCCCC(=O)O",
    "CCCCCCCCCCC(=O)O",
    "CCCCCCCCCCCC(=O)O",
    "CCCCCCCCCCCCC(=O)O",
]


def _m_a_from_impl(sizes, icc=0.5):
    """Back `m_A` out of `design_effect` so we test the IMPLEMENTATION, not a theorem."""
    return (design_effect(sizes, icc) - 1.0) / icc + 1.0


# --- scaffold layer -------------------------------------------------------


def test_analog_series_collapses_to_one_scaffold() -> None:
    assert len({murcko_scaffold(s) for s in SERIES}) == 1


def test_structurally_distinct_compounds_do_not_share_a_scaffold() -> None:
    assert len({murcko_scaffold(s) for s in SINGLETONS}) == len(SINGLETONS)


def test_scaffold_abstraction_does_not_merge_distinct_chemotypes() -> None:
    """Kills the `MakeScaffoldGeneric` mutation, which merges a pyridyl analog in."""
    assert murcko_scaffold(PYRIDYL) != murcko_scaffold(SERIES[0])
    st = measure_series_structure(SERIES + [PYRIDYL])
    assert st.cluster_sizes == (4, 1), "pyridyl analog was merged into the series"


def test_cluster_membership_is_correct_not_merely_the_right_sizes() -> None:
    """Kills scrambled-membership and off-by-one-enumerate mutations.

    `measure_series_structure` only reads `len(v)`, so any size-preserving
    permutation of membership is invisible to it. Membership must be asserted here.
    """
    groups = cluster_by_scaffold(SERIES + SINGLETONS)
    assert sorted(groups.values()) == [[0, 1, 2, 3], [4], [5], [6]]


# --- the design-effect formula -------------------------------------------


def test_design_effect_pins_the_size_weighted_mean_exactly() -> None:
    """The thesis test. `[5]*8` alone cannot distinguish m_A from mean or max."""
    strict = 0
    for sizes in ([12] + [1] * 28, [5] * 8, [3, 3, 2, 1, 1], [7, 2, 2, 2, 1]):
        expected = sum(m * m for m in sizes) / sum(sizes)
        got = _m_a_from_impl(sizes)
        assert got == pytest.approx(expected, rel=1e-12), sizes
        assert got >= statistics.mean(sizes) - 1e-12, sizes
        assert got <= max(sizes) + 1e-12, f"m_A exceeded max cluster: {sizes}"
        if got > statistics.mean(sizes) + 1e-9:
            strict += 1
    assert strict == 3, "unequal vectors produced no strict gap — test is vacuous"


def test_design_effect_exact_values_on_unequal_rosters() -> None:
    assert design_effect([12] + [1] * 28, 0.5) == pytest.approx(2.65, rel=1e-12)
    assert effective_n_unequal([12] + [1] * 28, 0.5) == pytest.approx(15.0943396226, rel=1e-9)
    assert design_effect([4, 1, 1, 1], 0.5) == pytest.approx(13 / 7, rel=1e-12)


def test_equal_clusters_reproduce_the_P7_table() -> None:
    """Cross-check the new path against the old where BOTH are valid."""
    assert effective_n_unequal([5] * 8, 0.5) == pytest.approx(effective_n(40, 5, 0.5), rel=1e-9)


def test_arithmetic_mean_overstates_information_pinned_not_bounded() -> None:
    sizes = [12] + [1] * 28
    correct = effective_n_unequal(sizes, 0.5)
    optimistic = sum(sizes) / (1 + (statistics.mean(sizes) - 1) * 0.5)
    assert optimistic / correct == pytest.approx(2.2276, rel=1e-3)


def test_one_shot_iterable_is_materialised_not_silently_wrong() -> None:
    """A generator previously exhausted after the first pass, giving deff = 1 - icc."""
    assert design_effect((m for m in [12, 1, 1, 1]), 0.5) == pytest.approx(5.4, rel=1e-12)


def test_design_effect_is_never_below_one() -> None:
    for sizes in ([1], [1] * 9, [12] + [1] * 28, [5] * 8):
        for icc in (0.0, 0.25, 1.0):
            assert design_effect(sizes, icc) >= 1.0


def test_icc_one_with_equal_clusters_gives_exactly_the_cluster_count() -> None:
    assert effective_n_unequal([5] * 8, 1.0) == pytest.approx(8.0, rel=1e-12)


# --- validation guards ----------------------------------------------------


@pytest.mark.parametrize("bad", [1.5, -0.1, float("nan"), float("inf")])
def test_icc_out_of_range_or_nan_raises(bad) -> None:
    with pytest.raises(ValueError, match="icc"):
        design_effect([2, 2], bad)


@pytest.mark.parametrize("bad", [[2, 0], [2, -1], [-2, -3]])
def test_non_positive_cluster_sizes_raise_positivity_not_emptiness(bad) -> None:
    with pytest.raises(ValueError, match="positive"):
        design_effect(bad, 0.5)


def test_empty_roster_raises() -> None:
    with pytest.raises(ValueError, match="empty"):
        design_effect([], 0.5)
    with pytest.raises(ValueError, match="empty"):
        measure_series_structure([])


def test_fractional_sizes_raise() -> None:
    with pytest.raises(TypeError, match="integers"):
        design_effect([0.5, 0.5], 1.0)


@pytest.mark.parametrize("bad", ["", "   ", "\n", "this-is-not-a-molecule"])
def test_blank_and_unparseable_smiles_raise(bad) -> None:
    """`MolFromSmiles('')` returns a zero-atom Mol, NOT None — the guard must not rely on None."""
    with pytest.raises(ValueError):
        murcko_scaffold(bad)


def test_salt_only_row_is_flagged_acyclic_not_silently_independent() -> None:
    """A counterion row parses legitimately — it must surface, not raise.

    r1.6c note: this test originally asserted `raises`. That was wrong about the
    CODE, not a bug in it. `[Na+].[Cl-]` is a real 2-atom molecule and rejecting it
    would be rejecting valid input. What matters is that it carries no ring system,
    so Murcko cannot place it in a series and it must not be counted as an
    independent compound — which `n_acyclic` is exactly what surfaces.
    """
    assert murcko_scaffold("[Na+].[Cl-]") == ""
    st = measure_series_structure(["[Na+].[Cl-]", "CCCCCCCC(=O)O"])
    assert st.n_acyclic == 2
    assert st.clustering_is_lower_bound


def test_bare_string_roster_is_rejected() -> None:
    with pytest.raises(TypeError):
        measure_series_structure("CCO")
    with pytest.raises(TypeError):
        cluster_by_scaffold("CCO")


# --- structure measurement ------------------------------------------------


def test_measure_recovers_the_planted_structure_including_every_field() -> None:
    st = measure_series_structure(SERIES + SINGLETONS)
    assert st.n == 7
    assert st.cluster_sizes == (4, 1, 1, 1)
    assert st.n_clusters == 4
    assert st.max_cluster == 4
    assert st.n_acyclic == 0
    assert st.singleton_cluster_fraction == pytest.approx(0.75)
    assert st.singleton_compound_fraction == pytest.approx(3 / 7)
    assert st.weighted_mean_size == pytest.approx(19 / 7)
    assert not st.clustering_is_lower_bound


def test_singleton_fractions_have_different_denominators_and_both_are_pinned() -> None:
    st = measure_series_structure(SERIES + SINGLETONS)
    assert st.singleton_cluster_fraction != st.singleton_compound_fraction


def test_acyclic_series_is_flagged_as_a_lower_bound_not_reported_independent() -> None:
    """Murcko is blind to acyclic analog series — the blindness must be visible.

    Six homologous fatty acids are a textbook series and scaffold to nothing. The
    module may not silently call them independent; `n_acyclic` and
    `clustering_is_lower_bound` are how the blindness surfaces.
    """
    st = measure_series_structure(FATTY_ACIDS)
    assert st.n_acyclic == 6
    assert st.clustering_is_lower_bound, "acyclic blindness was reported as independence"
    assert st.cluster_sizes == (1,) * 6


def test_acyclic_molecules_are_not_pooled_into_one_phantom_series() -> None:
    groups = cluster_by_scaffold(["CCO", "CCCC", "CC(C)O"])
    assert all(len(v) == 1 for v in groups.values())
    assert len(groups) == 3


# --- the sensitivity band -------------------------------------------------


def test_structure_over_icc_respects_the_callers_grid() -> None:
    """Kills the mutation that ignores `icc_grid` and hard-codes the default."""
    st = measure_series_structure(SERIES + SINGLETONS)
    band = structure_over_icc_range(st, icc_grid=(0.0, 0.25, 0.9))
    assert [r.icc for r in band] == [0.0, 0.25, 0.9]
    assert band[2].deff == pytest.approx(1 + (19 / 7 - 1) * 0.9)


def test_structure_over_icc_rejects_a_grid_that_cannot_be_a_band() -> None:
    """`all([])` is True, so an empty grid would satisfy 'holds across the band'."""
    st = measure_series_structure(SERIES + SINGLETONS)
    for bad in ((), (0.5,)):
        with pytest.raises(ValueError, match="at least 2"):
            structure_over_icc_range(st, icc_grid=bad)


def test_n_eff_falls_as_icc_rises_and_the_grid_actually_moves_it() -> None:
    st = measure_series_structure(SERIES + SINGLETONS)
    band = structure_over_icc_range(st)
    n_effs = [r.n_eff for r in band]
    assert n_effs == sorted(n_effs, reverse=True)
    assert n_effs[0] > n_effs[-1], "icc grid did not move n_eff — band is vacuous"


def test_icc_zero_is_exchangeable_and_a_nonzero_point_actually_discounts() -> None:
    """At icc=0 deff is 1 for ANY m_A, so the identity alone constrains nothing."""
    st = measure_series_structure(SERIES + SINGLETONS)
    assert st.design_effect(0.0) == 1.0
    assert st.effective_n(0.0) == pytest.approx(st.n)
    assert st.effective_n(0.5) == pytest.approx(49 / 13, rel=1e-9)
    assert st.effective_n(0.5) < st.n, "icc>0 did not discount n"


def test_upper_bound_flag_propagates_into_every_band_row() -> None:
    st = measure_series_structure(FATTY_ACIDS)
    assert all(r.n_eff_is_upper_bound for r in structure_over_icc_range(st))
