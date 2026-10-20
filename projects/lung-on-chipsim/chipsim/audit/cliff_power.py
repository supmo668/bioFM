"""R5 · pair-count power curve — a MEASUREMENT, not a decision.

R5 compares the LBM arm against the descriptor baseline **on matched molecular
pairs crossing a cliff** (MMP + ≥100-fold, principal's 1B1). What has never
existed is *how many pairs the test needs*. This module computes power as a
function of pair count so the operating point can be chosen from a curve rather
than picked — the same treatment P0 gave the sign test.

**Nothing here pre-registers a pair count.** It reports what each count buys.

## The unit is the PAIR, and getting that wrong would be the next standing-check instance

A7 measured that analog series destroy effective `n` in the sign test, where the
unit is the **compound** and near-duplicate compounds carry redundant information.
A matched pair is an analog series by construction — that is what a matched pair
*is* — so it is tempting to apply the same discount and conclude the pair stratum
is crippled.

**That would be the right machinery on the wrong unit.** In the cliff test the
within-pair similarity is *the signal being measured*, not correlated noise
between units: twenty pairs are twenty units, not forty correlated compounds. The
A7 discount applies **between** pairs — several pairs drawn from one med-chem
campaign are not independent of *each other* — and that is what
`between_pair_icc` sweeps.

## The test

Paired data, so the comparison is **McNemar** on discordant pairs, not two
independent proportions. Under H₀ the two arms are equally accurate, so given `d`
discordant pairs the count favouring the LBM is `Binomial(d, ½)`; the exact
one-sided binomial test is used rather than the χ² approximation, because at these
counts `d` is routinely below 20 where χ² is unreliable.

**Every figure is an UPPER BOUND** — the A2 analogue. Predicted affinities are
treated as noise-free, which flatters the LBM arm; real prediction error moves
pairs from concordant-correct toward discordant-wrong, and the true curve is
below the reported one.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import NormalDist

import numpy as np

_NORM = NormalDist()


def mcnemar_exact_p(n_lbm_better: int, n_base_better: int) -> float:
    """One-sided exact McNemar p-value for `LBM > baseline`.

    Concordant pairs carry no information about a *difference* and are excluded by
    construction — that is what makes this a paired test rather than a comparison
    of two proportions, and it is why pair count alone does not determine power:
    a design can have many pairs and few discordances.
    """
    d = n_lbm_better + n_base_better
    if d == 0:
        # No discordant pairs: the arms agreed everywhere. That is not evidence of
        # a difference, and it is not evidence against one either.
        return 1.0
    # P(X >= n_lbm_better) under Binomial(d, 0.5).
    tail = sum(math.comb(d, k) for k in range(n_lbm_better, d + 1))
    return tail / (2**d)


@dataclass(frozen=True)
class CliffPowerRow:
    n_pairs: int
    p_lbm: float
    p_base: float
    between_pair_icc: float
    power: float
    median_discordant: float
    trials: int


def _thresholds(p: float) -> float:
    """Latent cutoff giving marginal accuracy `p`."""
    if not 0.0 < p < 1.0:
        raise ValueError(f"accuracy must lie in (0, 1); got {p}")
    return _NORM.inv_cdf(p)


def simulate_cliff_trial(
    *,
    n_pairs: int,
    p_lbm: float,
    p_base: float,
    concordance: float,
    between_pair_icc: float,
    cluster_size: int,
    rng: np.random.Generator,
) -> tuple[int, int]:
    """One study: returns `(n_lbm_better, n_base_better)` discordant counts.

    **`concordance` is the parameter that matters most and is least knowable.** A
    pair that is hard for the LBM is usually hard for the descriptor baseline too —
    difficulty is a property of the pair, not of the method. Shared difficulty
    makes the arms agree, which *removes* discordant pairs, which is what power is
    built from. At `concordance = 0` the arms err independently (most optimistic);
    at `concordance = 1` they are driven entirely by pair difficulty and discordance
    arises only from the accuracy gap itself (most conservative).

    `between_pair_icc` clusters pairs into campaigns — the A7 discount at the
    correct unit. It is applied to the **pair-difficulty** term, so pairs from one
    series succeed or fail together.
    """
    if not 0.0 <= concordance <= 1.0:
        raise ValueError(f"concordance must lie in [0, 1] and be non-NaN; got {concordance}")
    if not 0.0 <= between_pair_icc <= 1.0:
        raise ValueError(
            f"between_pair_icc must lie in [0, 1] and be non-NaN; got {between_pair_icc}"
        )
    if n_pairs < 1:
        raise ValueError(f"n_pairs={n_pairs}; a cliff test needs at least one pair")
    if cluster_size < 1:
        raise ValueError(f"cluster_size must be >= 1, got {cluster_size}")

    # Pair difficulty, clustered by campaign (A7 BETWEEN pairs).
    n_clusters = math.ceil(n_pairs / cluster_size)
    labels = np.repeat(np.arange(n_clusters), cluster_size)[:n_pairs]
    w_s, w_o = math.sqrt(between_pair_icc), math.sqrt(1.0 - between_pair_icc)
    difficulty = w_s * rng.standard_normal(n_clusters)[labels] + w_o * rng.standard_normal(n_pairs)

    c, k = math.sqrt(concordance), math.sqrt(1.0 - concordance)
    lat_lbm = c * difficulty + k * rng.standard_normal(n_pairs)
    lat_base = c * difficulty + k * rng.standard_normal(n_pairs)

    lbm_ok = lat_lbm < _thresholds(p_lbm)
    base_ok = lat_base < _thresholds(p_base)
    return int(np.sum(lbm_ok & ~base_ok)), int(np.sum(~lbm_ok & base_ok))


def cliff_power(
    *,
    n_pairs: int,
    p_lbm: float,
    p_base: float,
    concordance: float = 0.5,
    between_pair_icc: float = 0.0,
    cluster_size: int = 1,
    alpha: float = 0.05,
    trials: int = 2000,
    seed: int = 4242,
) -> CliffPowerRow:
    """Power of the one-sided exact McNemar test at `n_pairs`."""
    if trials < 1:
        raise ValueError(f"trials={trials}; power cannot be estimated from no trials")
    if not 0.0 < alpha < 1.0:
        raise ValueError(f"alpha must lie in (0, 1) and be non-NaN; got {alpha}")

    rng = np.random.default_rng(seed)
    hits, discordant = 0, []
    for _ in range(trials):
        b, c = simulate_cliff_trial(
            n_pairs=n_pairs,
            p_lbm=p_lbm,
            p_base=p_base,
            concordance=concordance,
            between_pair_icc=between_pair_icc,
            cluster_size=cluster_size,
            rng=rng,
        )
        discordant.append(b + c)
        hits += int(mcnemar_exact_p(b, c) <= alpha)
    return CliffPowerRow(
        n_pairs=n_pairs,
        p_lbm=p_lbm,
        p_base=p_base,
        between_pair_icc=between_pair_icc,
        power=hits / trials,
        median_discordant=float(np.median(discordant)),
        trials=trials,
    )
