"""R5 pair-count power tests.

**Written against PINNED literal values, deliberately.** The predecessor halt-rule
suite asserted things like `d.worst_power == min(powers)` — tautologies over
whatever the function returned — and mutation testing found that `evaluate_halt`'s
entire simulation could be replaced by a constant with all 60 tests still passing.
Every numeric assertion below is a hand-computed value or an independently-derived
bound, so a constant-returning implementation fails.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from chipsim.audit.cliff_power import cliff_power, mcnemar_exact_p, simulate_cliff_trial


# --- the test statistic, against hand-computed values -------------------------


def test_mcnemar_matches_hand_computed_binomial_tails() -> None:
    """Exact one-sided binomial tails, computed by hand, not by the function.

    d=5, all 5 favouring the LBM: P = 1/32 = 0.03125.
    d=5, 4 favouring: P(X>=4) = (5+1)/32 = 6/32 = 0.1875.
    d=1, 1 favouring: P = 1/2.
    """
    assert mcnemar_exact_p(5, 0) == pytest.approx(1 / 32)
    assert mcnemar_exact_p(4, 1) == pytest.approx(6 / 32)
    assert mcnemar_exact_p(1, 0) == pytest.approx(0.5)
    assert mcnemar_exact_p(0, 5) == pytest.approx(1.0)


def test_no_discordant_pairs_is_not_evidence() -> None:
    """Total agreement is not evidence of a difference — nor against one.

    Returning anything below alpha here would let a study with zero information
    reject the null.
    """
    assert mcnemar_exact_p(0, 0) == 1.0


def test_five_discordant_all_one_way_is_the_smallest_significant_design() -> None:
    """The floor on discordance, derived rather than assumed.

    At alpha=0.05 one-sided, 5 discordant pairs all favouring one arm give exactly
    1/32 = 0.031 < 0.05, and 4 give 1/16 = 0.0625 > 0.05. **So no design with
    fewer than 5 DISCORDANT pairs can ever reach significance**, whatever the pair
    count — which is why pair count alone does not determine power.
    """
    assert mcnemar_exact_p(4, 0) == pytest.approx(1 / 16)
    assert mcnemar_exact_p(4, 0) > 0.05
    assert mcnemar_exact_p(5, 0) < 0.05


# --- the simulation -----------------------------------------------------------


def test_type_one_error_is_at_or_below_alpha_when_the_arms_are_equal() -> None:
    """H0 control: equal accuracy must not reject at more than alpha.

    An exact test on a discrete statistic is CONSERVATIVE, so the rate lands below
    0.05 rather than at it. Asserting `== 0.05` would fail correct code; asserting
    only `< 0.5` would pass a broken test. The bound is what is checkable.
    """
    r = cliff_power(n_pairs=30, p_lbm=0.70, p_base=0.70, trials=2000, seed=4242)
    assert r.power <= 0.05, f"type-I error {r.power:.3f} exceeds alpha"


def test_power_rises_with_pair_count_and_with_the_accuracy_gap() -> None:
    """Two monotonicities. A constant-returning implementation fails both."""
    small = cliff_power(n_pairs=15, p_lbm=0.80, p_base=0.55, trials=1500, seed=4242)
    large = cliff_power(n_pairs=60, p_lbm=0.80, p_base=0.55, trials=1500, seed=4242)
    assert large.power > small.power + 0.10

    narrow = cliff_power(n_pairs=40, p_lbm=0.65, p_base=0.55, trials=1500, seed=4242)
    wide = cliff_power(n_pairs=40, p_lbm=0.85, p_base=0.55, trials=1500, seed=4242)
    assert wide.power > narrow.power + 0.10


def test_shared_difficulty_cuts_discordance_but_RAISES_power() -> None:
    """This test failed on its first writing, and the model was right.

    I asserted that shared pair difficulty would LOWER power, reasoning that
    agreement removes the discordant pairs the test consumes. The first half is
    true and the conclusion is false, because **McNemar tests the SPLIT of the
    discordant pairs, not their count**. Measured over 400 studies at n=40:

        concordance=0.0   discordant 18.5   76.3% favour the LBM   power 0.70
        concordance=0.9   discordant 10.1   98.6% favour the LBM   power 0.98

    Shared difficulty strips out the SYMMETRIC noise — "baseline happened to be
    right where the LBM was wrong" collapses from 4.4 pairs to 0.14 — leaving a
    lopsided split that is far more significant despite being smaller.

    **The consequence for the gate is the useful part: assuming the arms err
    INDEPENDENTLY is the CONSERVATIVE choice**, so `concordance=0` is the
    defensible default for a power floor. Real methods share difficulty, so the
    true curve sits above the reported one — which is the opposite direction from
    A2 and must not be netted against it.
    """
    independent = cliff_power(
        n_pairs=40, p_lbm=0.80, p_base=0.55, concordance=0.0, trials=1200, seed=4242
    )
    shared = cliff_power(
        n_pairs=40, p_lbm=0.80, p_base=0.55, concordance=0.9, trials=1200, seed=4242
    )
    assert shared.median_discordant < independent.median_discordant
    assert shared.power > independent.power, (
        "shared difficulty must RAISE power by concentrating the discordant split; "
        "if this inverts, McNemar has stopped testing the split"
    )


def test_within_pair_similarity_is_NOT_discounted_the_unit_is_the_pair() -> None:
    """A7 applies BETWEEN pairs, never within one.

    A matched pair is an analog series by construction — that is what it is. The
    within-pair similarity is the SIGNAL, not correlated noise between units, so
    twenty pairs are twenty units and not forty correlated compounds. Applying A7's
    compound-level discount here would be the right machinery on the wrong unit.

    Pinned as a property: `cliff_power` exposes no within-pair knob at all, and
    `between_pair_icc` moves the answer only when pairs are actually clustered.
    """
    import inspect

    params = set(inspect.signature(cliff_power).parameters)
    assert "within_pair_icc" not in params
    assert "between_pair_icc" in params

    # icc with singleton clusters must be inert: there is nothing to correlate.
    a = cliff_power(
        n_pairs=40,
        p_lbm=0.80,
        p_base=0.55,
        between_pair_icc=0.0,
        cluster_size=1,
        trials=800,
        seed=4242,
    )
    b = cliff_power(
        n_pairs=40,
        p_lbm=0.80,
        p_base=0.55,
        between_pair_icc=0.9,
        cluster_size=1,
        trials=800,
        seed=4242,
    )
    assert a.power == pytest.approx(b.power, abs=0.02)


def test_between_pair_clustering_is_measured_not_assumed() -> None:
    """Pairs from one campaign are not independent of each other.

    This is A7 at the correct unit. Direction is asserted; magnitude is what the
    driver reports.
    """
    flat = cliff_power(
        n_pairs=40,
        p_lbm=0.80,
        p_base=0.55,
        between_pair_icc=0.0,
        cluster_size=5,
        trials=1200,
        seed=4242,
    )
    clustered = cliff_power(
        n_pairs=40,
        p_lbm=0.80,
        p_base=0.55,
        between_pair_icc=0.8,
        cluster_size=5,
        trials=1200,
        seed=4242,
    )
    assert clustered.power < flat.power


@pytest.mark.parametrize(
    ("kwargs", "match"),
    [
        ({"p_lbm": 0.0}, "accuracy"),
        ({"p_lbm": 1.0}, "accuracy"),
        ({"p_lbm": float("nan")}, "accuracy"),
        ({"concordance": 1.5}, "concordance"),
        ({"concordance": float("nan")}, "concordance"),
        ({"between_pair_icc": float("nan")}, "between_pair_icc"),
        ({"n_pairs": 0}, "at least one pair"),
        ({"trials": 0}, "no trials"),
        ({"alpha": 0.0}, "alpha"),
        ({"alpha": float("nan")}, "alpha"),
    ],
)
def test_refuses_input_it_cannot_evaluate(kwargs, match) -> None:
    """NaN is included in every numeric guard deliberately.

    `nan < threshold` is False, so a NaN that passes a domain check propagates into
    a confident-looking verdict. That defect has already appeared twice in this
    package — once in `icc` and once in `rho` — and both times it authorised rather
    than refused.
    """
    base = {"n_pairs": 20, "p_lbm": 0.8, "p_base": 0.55, "trials": 20}
    with pytest.raises(ValueError, match=match):
        cliff_power(**{**base, **kwargs})


def test_simulate_returns_counts_bounded_by_the_pair_count() -> None:
    """A discordance count above n_pairs would be arithmetically impossible."""
    rng = np.random.default_rng(4242)
    for _ in range(50):
        b, c = simulate_cliff_trial(
            n_pairs=25,
            p_lbm=0.8,
            p_base=0.55,
            concordance=0.5,
            between_pair_icc=0.0,
            cluster_size=1,
            rng=rng,
        )
        assert 0 <= b + c <= 25


def test_perfect_lbm_against_chance_baseline_saturates() -> None:
    """A hand-checkable extreme: a perfect arm vs a near-chance one must be found.

    With p_lbm=0.99 and p_base=0.50 at 40 pairs, nearly every pair is discordant in
    the LBM's favour, so power must be essentially 1. A model that cannot detect
    this cannot detect anything.
    """
    r = cliff_power(n_pairs=40, p_lbm=0.99, p_base=0.50, concordance=0.0, trials=600, seed=4242)
    assert r.power > 0.99
    assert r.median_discordant >= 15


def test_mcnemar_tail_sums_to_one_over_the_support() -> None:
    """Independent check on the tail arithmetic, not a restatement of it."""
    d = 6
    total = sum(math.comb(d, k) for k in range(d + 1))
    assert total == 2**d
    assert mcnemar_exact_p(0, d) == pytest.approx(1.0)
