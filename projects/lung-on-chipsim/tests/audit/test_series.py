"""A7 realised-structure tests.

Unit tests over **hand-constructed** rosters, per the r1.5/r1.6 rule: a function
is tested over its domain, not over the subset a study happens to reach. Every
test that names a branch asserts the branch was taken (anti-vacuity).
"""

from __future__ import annotations

import pytest

from chipsim.audit.power import effective_n
from chipsim.audit.series import (
    cluster_by_scaffold,
    design_effect,
    effective_n_unequal,
    measure_series_structure,
    murcko_scaffold,
    power_over_icc_range,
)

# A hand-built roster: four para-substituted benzanilides (one analog series,
# identical Murcko scaffold), plus three structurally distinct singletons.
SERIES = [
    "O=C(Nc1ccccc1)c1ccc(C)cc1",
    "O=C(Nc1ccccc1)c1ccc(Cl)cc1",
    "O=C(Nc1ccccc1)c1ccc(F)cc1",
    "O=C(Nc1ccccc1)c1ccc(OC)cc1",
]
SINGLETONS = [
    "c1ccc2[nH]ccc2c1",  # indole
    "C1CCNCC1",  # piperidine
    "c1ccc(-c2ccncc2)cc1",  # phenylpyridine
]


def test_analog_series_collapses_to_one_scaffold() -> None:
    scaffolds = {murcko_scaffold(s) for s in SERIES}
    assert len(scaffolds) == 1, f"expected one shared scaffold, got {scaffolds}"


def test_structurally_distinct_compounds_do_not_share_a_scaffold() -> None:
    scaffolds = {murcko_scaffold(s) for s in SINGLETONS}
    assert len(scaffolds) == len(SINGLETONS)


def test_measure_recovers_the_planted_structure() -> None:
    st = measure_series_structure(SERIES + SINGLETONS)
    assert st.n == 7
    assert st.cluster_sizes == (4, 1, 1, 1)
    assert st.n_clusters == 4
    assert st.max_cluster == 4
    # anti-vacuity: a roster with no series would make every assertion here pass
    # trivially against an implementation that never clusters at all.
    assert st.max_cluster > 1, "planted series was not detected — test is vacuous"


def test_unequal_sizes_beat_the_arithmetic_mean_and_always_in_one_direction() -> None:
    """`m_A >= mean(m)` — the correction is never optimistic relative to the mean."""
    import statistics

    for sizes in ([12] + [1] * 28, [5] * 8, [3, 3, 2, 1, 1], [7, 2, 2, 2, 1]):
        m_a = sum(m * m for m in sizes) / sum(sizes)
        assert m_a >= statistics.mean(sizes) - 1e-12, sizes


def test_equal_clusters_reproduce_the_P7_table() -> None:
    """Cross-check against the existing uniform-size machinery: 8x5 @ icc 0.5."""
    assert effective_n_unequal([5] * 8, 0.5) == pytest.approx(effective_n(40, 5, 0.5), rel=1e-9)


def test_arithmetic_mean_overstates_information_on_a_real_shaped_roster() -> None:
    import statistics

    sizes = [12] + [1] * 28
    correct = effective_n_unequal(sizes, 0.5)
    optimistic = sum(sizes) / (1 + (statistics.mean(sizes) - 1) * 0.5)
    assert optimistic > correct
    # the branch this test exists to guard: the gap is material, not rounding
    assert optimistic / correct > 2.0, "gap collapsed — test no longer has teeth"


def test_icc_zero_is_the_exchangeable_case() -> None:
    st = measure_series_structure(SERIES + SINGLETONS)
    assert st.effective_n(0.0) == pytest.approx(st.n)


def test_acyclic_molecules_are_not_pooled_into_one_phantom_series() -> None:
    groups = cluster_by_scaffold(["CCO", "CCCC", "CC(C)O"])
    assert all(len(v) == 1 for v in groups.values()), groups
    assert len(groups) == 3


def test_unparseable_smiles_raises_rather_than_silently_clustering() -> None:
    with pytest.raises(ValueError, match="unparseable"):
        murcko_scaffold("this-is-not-a-molecule")


def test_icc_out_of_range_raises() -> None:
    with pytest.raises(ValueError, match="icc"):
        design_effect([2, 2], 1.5)


def test_empty_roster_raises() -> None:
    with pytest.raises(ValueError, match="empty"):
        measure_series_structure([])


def test_power_over_icc_returns_a_range_not_a_point() -> None:
    st = measure_series_structure(SERIES + SINGLETONS)
    band = power_over_icc_range(st)
    assert len(band) > 1, "a single row would be a point estimate, which A7 forbids"
    n_effs = [n for _, _, n in band]
    assert n_effs == sorted(n_effs, reverse=True), "n_eff must fall as icc rises"
    assert n_effs[0] > n_effs[-1], "icc grid did not move n_eff — range is vacuous"
