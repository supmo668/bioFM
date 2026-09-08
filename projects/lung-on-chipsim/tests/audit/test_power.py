"""P0 power-simulation tests — A&D r1.4.

The simulation decides whether ~$27 of GPU time is spent, so its own machinery is
tested before its output is believed. In particular the BCa implementation is
checked for *calibration*, not merely for running: an interval that is confidently
wrong is worse here than one that fails loudly, because its output is a go/no-go.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from chipsim.audit.power import (
    _spearman_to_pearson,
    bca_ci,
    delta_rho,
    power_scan,
    simulate_ligand_set,
    spearman,
)


def test_spearman_matches_a_known_case() -> None:
    """Perfect monotone (non-linear) agreement is rho = 1, which Pearson would miss."""
    x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    assert spearman(x, x**3) == pytest.approx(1.0)
    assert spearman(x, -(x**3)) == pytest.approx(-1.0)


def test_ties_are_averaged_not_ordinal() -> None:
    """Measured affinities tie (censored values, repeated readouts).

    Ordinal ranking invents an order the data does not have, and it does so
    silently: the rho still computes, just against an ordering nobody chose. With
    all values tied there is no information, so rho must be undefined (nan) rather
    than some artifact of input order.
    """
    tied = np.array([1.0, 1.0, 1.0, 1.0])
    assert math.isnan(spearman(tied, np.array([4.0, 3.0, 2.0, 1.0])))

    # A half-tied vector must give the same rho whichever order the ties arrive in.
    y = np.array([1.0, 2.0, 3.0, 4.0])
    a = spearman(np.array([1.0, 1.0, 2.0, 3.0]), y)
    b = spearman(np.array([1.0, 1.0, 2.0, 3.0])[::-1], y[::-1])
    assert a == pytest.approx(b)


def test_delta_rho_is_a_difference_of_agreements() -> None:
    """The reported number is a DIFFERENCE — a single-arm result is not the statistic."""
    rng = np.random.default_rng(0)
    y, f_nat, f_shuf = simulate_ligand_set(200, 0.6, 0.0, rng)
    d = delta_rho(y, f_nat, f_shuf)
    assert d == pytest.approx(spearman(f_nat, y) - spearman(f_shuf, y))
    # Identical arms cancel exactly: no shuffle effect means no delta.
    assert delta_rho(y, f_nat, f_nat) == pytest.approx(0.0)


def test_copula_hits_the_spearman_it_claims() -> None:
    """A1: the simulation must produce the rho it is labelled with.

    If this drifts, every half-width in the scan describes a different correlation
    than its label — the failure would be invisible because the numbers would still
    look entirely reasonable.
    """
    rng = np.random.default_rng(1)
    for target in (0.0, 0.3, 0.6, 0.9):
        y, f_nat, _ = simulate_ligand_set(20000, target, 0.0, rng)
        assert spearman(f_nat, y) == pytest.approx(target, abs=0.02), target


def test_spearman_to_pearson_inverts_the_standard_relation() -> None:
    r = _spearman_to_pearson(0.5)
    assert (6.0 / math.pi) * math.asin(r / 2.0) == pytest.approx(0.5)


def test_bca_refuses_a_sample_too_small_to_accelerate() -> None:
    rng = np.random.default_rng(2)
    y, f_nat, f_shuf = simulate_ligand_set(3, 0.5, 0.0, rng)
    with pytest.raises(ValueError, match="at least 4"):
        bca_ci(y, f_nat, f_shuf, rng=rng)


def test_bca_interval_is_ordered_and_contains_the_point_estimate() -> None:
    rng = np.random.default_rng(3)
    y, f_nat, f_shuf = simulate_ligand_set(40, 0.6, 0.0, rng)
    lo, hi = bca_ci(y, f_nat, f_shuf, n_boot=800, rng=rng)
    assert lo < hi
    assert lo <= delta_rho(y, f_nat, f_shuf) <= hi


@pytest.mark.slow
def test_bca_coverage_is_near_nominal_at_n40() -> None:
    """THE test that licenses using this CI for a go/no-go.

    G5 exists because percentile intervals are too narrow at small n, and the
    direction of that error suppresses `inconclusive`. Asserting that BCa RUNS
    would not have caught that; only measuring coverage does.

    The band is deliberately wide (0.86-0.99 for nominal 0.95) because 300 trials
    give a standard error near 1.3 points and a tighter assertion would flake.

    **What this test does NOT do, corrected after measuring.** An earlier version
    of this docstring claimed it was "narrow enough to fail the thing it is written
    to catch: a percentile interval at this n lands well below the floor." That is
    FALSE. Measured over 300 trials at n=40 on this statistic:

        BCa        coverage 0.930   median half-width 0.384
        percentile coverage 0.943   median half-width 0.386

    Percentile is marginally BETTER here and the half-widths differ by 0.5%. So
    this test does not discriminate the two variants, and no test in this suite
    does. The claim was written from the general small-n literature and asserted
    about a specific statistic it had not been checked against — the same defect
    class as R4 inheriting D3a's units.
    """
    rng = np.random.default_rng(4)
    true_rho_native, true_rho_shuffled = 0.6, 0.0
    truth = true_rho_native - true_rho_shuffled

    covered = 0
    trials = 300
    for _ in range(trials):
        y, f_nat, f_shuf = simulate_ligand_set(40, true_rho_native, true_rho_shuffled, rng)
        lo, hi = bca_ci(y, f_nat, f_shuf, n_boot=600, rng=rng)
        covered += int(lo <= truth <= hi)

    coverage = covered / trials
    assert 0.86 <= coverage <= 0.99, f"BCa coverage {coverage:.3f} at n=40 is off nominal"


def test_power_scan_reports_widening_intervals_as_n_falls() -> None:
    """Sanity: fewer ligands must not produce a tighter interval.

    A scan that got this backwards would recommend running the study on less data.
    """
    res = power_scan(
        n_values=(20, 80),
        rho_native=0.6,
        rho_shuffled=0.0,
        equivalence=0.10,
        sensitive_floor=0.20,
        trials=40,
        n_boot=400,
        seed=5,
    )
    small, large = res
    assert small.median_half_width > large.median_half_width


def test_verdict_frequencies_partition() -> None:
    """The three regions are a partition (D3a), so the frequencies must sum to 1.

    If they do not, `classify` is not total on simulated input and the scan is
    measuring something other than the design's verdict rule.
    """
    res = power_scan(
        n_values=(30,),
        rho_native=0.5,
        rho_shuffled=0.0,
        equivalence=0.10,
        sensitive_floor=0.20,
        trials=60,
        n_boot=400,
        seed=6,
    )[0]
    total = res.p_fits_equivalence_band + res.p_reaches_sensitive_floor + res.p_inconclusive
    assert total == pytest.approx(1.0)


def test_sign_test_power_rises_with_effect_and_is_near_chance_at_zero() -> None:
    """The statistic the GO/NO-GO now rests on, so it cannot be the untested piece.

    Two properties, and the second is the one that matters. Power must rise with
    effect size — a monotonicity failure would make the halt rule recommend running
    on weaker effects. And at a TRUE effect of zero the unanimity criterion must
    sit near its null rate of 2^-7 = 0.0078: if it did not, the sign test would be
    manufacturing unanimity from noise, and p = 0.008 would be a false claim
    printed on the study's headline result.
    """
    from chipsim.audit.power import sign_test_power

    at_zero = sign_test_power(
        n=40, n_targets=7, rho_native=0.0, rho_shuffled=0.0, trials=400, seed=31
    )
    assert at_zero <= 0.05, f"unanimity at a null effect was {at_zero:.3f}, near-chance expected"

    small = sign_test_power(
        n=40, n_targets=7, rho_native=0.2, rho_shuffled=0.0, trials=200, seed=32
    )
    large = sign_test_power(
        n=40, n_targets=7, rho_native=0.6, rho_shuffled=0.0, trials=200, seed=32
    )
    assert small < large
    assert large > 0.8, "the design's declared 'large effect' must actually be detectable"


def test_sign_test_does_not_depend_on_the_equivalence_band() -> None:
    """Why the r1.4 halt rule was wrong, pinned as a property.

    The sign test uses point estimates only. If it ever became sensitive to the
    band, the halt rule would silently inherit the defect that made P0's first
    version halt a viable study unconditionally.

    Asserted against the CODE OBJECT, not the source text. The first version of
    this test grepped `inspect.getsource` for "equivalence" and failed on the
    docstring, which says the function does *not* involve the band — a matcher
    loose enough to be satisfied by prose describing the opposite of the defect.
    Same bug as the half-(b) journal test, caught here by the test failing rather
    than by it passing.
    """
    import inspect

    from chipsim.audit.power import sign_test_power

    referenced = set(sign_test_power.__code__.co_names)
    assert "bca_ci" not in referenced, (
        "sign_test_power calls bca_ci; the primary inference must not depend on "
        "the interval machinery P0 showed cannot reach the equivalence band"
    )

    params = set(inspect.signature(sign_test_power).parameters)
    assert not params & {"equivalence", "sensitive_floor"}, (
        f"sign_test_power takes band parameters {params & {'equivalence', 'sensitive_floor'}}"
    )
