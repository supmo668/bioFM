"""P0 · Pre-hoc power simulation — A&D r1.4, and G3's halt criterion.

**This module gates every dollar of GPU spend.** It runs locally, costs nothing,
and answers one question before any batch is authorized:

    at the pair count we can actually assemble, can the study render `insensitive`?

`insensitive` requires the **whole** 95% CI inside the equivalence band. If no
achievable CI is that narrow, D3a's three-region partition collapses to two in
practice, and the PVR's *"publishable whether positive or negative"* fails on the
negative side. Spending ~$27 to discover that is strictly worse than spending
nothing to predict it — which is what a pre-hoc halt rule is for. r1.2 named the
rule and gave no way to evaluate it (gap G3); this module is that way.

**The analytic estimate this replaces.** By Fisher-z (`SE ≈ 1.06/√(n−3)`), at
n≈40 a single Spearman ρ has a 95% half-width ≈ 0.33, and for the *difference*
fitting inside `±0.10` needs `corr(ρ_native, ρ_shuf) ≳ 0.96` — while shuffling is
*designed* to destroy that correlation. Those are approximations. The simulation
here is the measured answer, and it is allowed to disagree with them.

**Assumptions live in `workstreams/chipsim-lbm-audit/ASSUMPTIONS.md`** and are
referenced by id (A1…) at the site that depends on each. Every one of them can
make this simulation optimistic; none is hidden in a default.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import NormalDist

import numpy as np

#: Standard normal, for BCa's bias-correction and acceleration terms. `statistics`
#: is stdlib, so BCa costs no new dependency (scipy is not in this project).
_NORM = NormalDist()


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    """Spearman ρ — Pearson correlation of ranks.

    Ties are ranked by `average`, matching `scipy.stats.spearmanr`. Measured
    affinities routinely tie (censored values, repeated assay readouts), so
    `ordinal` ranking here would silently impose an ordering the data does not
    have — see A6.
    """
    return float(np.corrcoef(_rank_average(x), _rank_average(y))[0, 1])


def _rank_average(a: np.ndarray) -> np.ndarray:
    """Ranks with ties averaged."""
    order = np.argsort(a, kind="stable")
    ranks = np.empty(len(a), dtype=float)
    ranks[order] = np.arange(len(a), dtype=float)
    # Average within tied groups.
    sorted_a = a[order]
    i = 0
    while i < len(a):
        j = i
        while j + 1 < len(a) and sorted_a[j + 1] == sorted_a[i]:
            j += 1
        if j > i:
            ranks[order[i : j + 1]] = ranks[order[i : j + 1]].mean()
        i = j + 1
    return ranks


def delta_rho(y: np.ndarray, f_native: np.ndarray, f_shuffled: np.ndarray) -> float:
    """`Δρ = ρ(native, measured) − ρ(shuffled, measured)` — R3's statistic.

    `A` is *agreement with measured values* (D3a), so both arms are scored against
    the same `y` on the same ligands. That pairing is the whole reason the study is
    powered at n≈40 at all, and it is why the bootstrap resamples **ligands**
    rather than pairs.
    """
    return spearman(f_native, y) - spearman(f_shuffled, y)


def bca_ci(
    y: np.ndarray,
    f_native: np.ndarray,
    f_shuffled: np.ndarray,
    *,
    alpha: float = 0.05,
    n_boot: int = 2000,
    rng: np.random.Generator,
) -> tuple[float, float]:
    """95% BCa bootstrap CI for `Δρ`, resampling **ligands**.

    BCa rather than percentile, sealed per G5 — but for a narrower reason than G5
    first claimed, and the correction matters.

    G5's argument was that percentile intervals are too narrow at small n, and that
    the direction of that error suppresses `inconclusive`. The general claim is
    supported by the literature. **The specific claim, for this statistic at this
    n, is not:** measured over 300 trials at n=40, BCa covered 0.930 and percentile
    0.943, with median half-widths 0.384 and 0.386. They are equivalent here, and
    if anything percentile is closer to nominal.

    BCa is kept because the acceleration term tracks skew — `Δρ` is a difference of
    bounded quantities and is skewed near the ends of the ρ range, where this study
    may well land — and because a named variant is reproducible while an unnamed
    one is not. **It is not kept because percentile was shown to fail here.** That
    distinction is the difference between a justified choice and a rationalised
    one.

    Returns `(lo, hi)`. Raises on a degenerate resample rather than returning a
    number, matching `classify`'s refusal to score a broken interval.
    """
    n = len(y)
    if n < 4:
        raise ValueError(f"BCa needs at least 4 ligands, got {n}")

    theta_hat = delta_rho(y, f_native, f_shuffled)

    idx = rng.integers(0, n, size=(n_boot, n))
    boot = np.array([delta_rho(y[i], f_native[i], f_shuffled[i]) for i in idx])
    boot = boot[np.isfinite(boot)]
    if len(boot) < n_boot // 2:
        raise ValueError("more than half of bootstrap resamples were degenerate")

    # Bias correction: how far the bootstrap median sits from the point estimate.
    prop = float(np.mean(boot < theta_hat))
    prop = min(max(prop, 1.0 / len(boot)), 1.0 - 1.0 / len(boot))
    z0 = _NORM.inv_cdf(prop)

    # Acceleration, by jackknife. This is the term percentile bootstrap lacks and
    # the reason BCa tracks skew — Δρ is a difference of bounded quantities and is
    # skewed near the ends of the ρ range.
    jack = np.array(
        [
            delta_rho(np.delete(y, i), np.delete(f_native, i), np.delete(f_shuffled, i))
            for i in range(n)
        ]
    )
    jack_mean = jack.mean()
    num = float(np.sum((jack_mean - jack) ** 3))
    den = 6.0 * float(np.sum((jack_mean - jack) ** 2)) ** 1.5
    a = num / den if den != 0 else 0.0

    def _endpoint(z: float) -> float:
        adj = z0 + (z0 + z) / (1.0 - a * (z0 + z))
        return float(np.clip(_NORM.cdf(adj), 0.0, 1.0))

    lo_p = _endpoint(_NORM.inv_cdf(alpha / 2.0))
    hi_p = _endpoint(_NORM.inv_cdf(1.0 - alpha / 2.0))
    return float(np.quantile(boot, lo_p)), float(np.quantile(boot, hi_p))


def _spearman_to_pearson(rho_s: float) -> float:
    """Latent Pearson r giving a target Spearman ρ under a Gaussian copula.

    `ρ_S = (6/π)·arcsin(r/2)`, inverted. This is the standard relation and it is
    exact only for the bivariate normal — see A1. It matters because the
    simulation must hit the ρ it claims to be simulating; getting this wrong would
    make every reported half-width describe a different correlation than the label.
    """
    return 2.0 * math.sin(math.pi * rho_s / 6.0)


def simulate_ligand_set(
    n: int,
    rho_native: float,
    rho_shuffled: float,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """One synthetic ligand set: measured `y`, native and shuffled predictions.

    Gaussian copula (A1). Both prediction arms are correlated with `y` at their
    target Spearman ρ and are **conditionally independent given `y`** (A3) — the
    design's premise that shuffling destroys target information, leaving only
    whatever agreement flows through the ligand itself.

    A3 is the assumption most likely to be optimistic in the *helpful* direction
    and is therefore swept explicitly by `power_scan`: if the two arms share a
    ligand-driven component, their ρ estimates co-vary, the paired difference has
    lower variance, and the CI narrows. That is exactly the `corr ≳ 0.96` regime in
    which `insensitive` becomes reachable, so it must be measured rather than
    assumed away.
    """
    r_nat = _spearman_to_pearson(rho_native)
    r_shuf = _spearman_to_pearson(rho_shuffled)

    z_y = rng.standard_normal(n)
    z_nat = r_nat * z_y + math.sqrt(max(0.0, 1.0 - r_nat**2)) * rng.standard_normal(n)
    z_shuf = r_shuf * z_y + math.sqrt(max(0.0, 1.0 - r_shuf**2)) * rng.standard_normal(n)
    return z_y, z_nat, z_shuf


@dataclass(frozen=True)
class PowerResult:
    """One cell of the scan. Every field is an observed frequency, not a claim."""

    n: int
    rho_native: float
    rho_shuffled: float
    median_half_width: float
    p_fits_equivalence_band: float
    p_reaches_sensitive_floor: float
    p_inconclusive: float
    trials: int

    @property
    def insensitive_reachable(self) -> bool:
        """Whether `insensitive` is renderable often enough to count as available.

        The 5% floor is a **convention, not a derivation** (A5). It is recorded as
        one so that nobody later cites it as a computed threshold.
        """
        return self.p_fits_equivalence_band >= 0.05


def power_scan(
    *,
    n_values: tuple[int, ...],
    rho_native: float,
    rho_shuffled: float,
    equivalence: float,
    sensitive_floor: float,
    trials: int = 200,
    n_boot: int = 1000,
    seed: int = 0,
) -> list[PowerResult]:
    """Sweep ligand count and report what verdicts are actually reachable.

    Returns one `PowerResult` per `n`. The caller decides the halt; this function
    only reports frequencies, because a simulation that also rendered the verdict
    would be deciding the study's fate inside a helper.
    """
    rng = np.random.default_rng(seed)
    out: list[PowerResult] = []
    for n in n_values:
        widths: list[float] = []
        fits = reaches = inconclusive = 0
        for _ in range(trials):
            y, f_nat, f_shuf = simulate_ligand_set(n, rho_native, rho_shuffled, rng)
            try:
                lo, hi = bca_ci(y, f_nat, f_shuf, n_boot=n_boot, rng=rng)
            except ValueError:
                continue
            widths.append((hi - lo) / 2.0)
            is_sensitive = lo >= sensitive_floor
            is_insensitive = lo >= -equivalence and hi <= equivalence
            fits += int(is_insensitive)
            reaches += int(is_sensitive)
            inconclusive += int(not is_sensitive and not is_insensitive)
        k = len(widths)
        out.append(
            PowerResult(
                n=n,
                rho_native=rho_native,
                rho_shuffled=rho_shuffled,
                median_half_width=float(np.median(widths)) if k else float("nan"),
                p_fits_equivalence_band=fits / k if k else float("nan"),
                p_reaches_sensitive_floor=reaches / k if k else float("nan"),
                p_inconclusive=inconclusive / k if k else float("nan"),
                trials=k,
            )
        )
    return out


def sign_test_power(
    *,
    n: int,
    n_targets: int,
    rho_native: float,
    rho_shuffled: float,
    trials: int = 400,
    seed: int = 0,
) -> float:
    """Power of the study's PRIMARY inference: a unanimous sign across targets.

    **This, not `insensitive`, is what the halt rule must key on.** D3's inference
    is a one-sided sign test — *"a unanimous direction across all seven is
    publishable and a 5/7 split is not"*, giving `p = 1/2⁷ ≈ 0.008`. It asks only
    whether every per-target `Δρ` point estimate is positive; it does not require
    any target to clear the `sensitive` floor, and it does not involve the
    equivalence band at all.

    P0's first run measured `P(insensitive) = 0.000` in every cell and the r1.4
    halt rule keyed on exactly that, so it would have halted the study
    unconditionally — including in the cases where the primary inference is well
    powered. The PVR accepts *"a defensible 'inconclusive at this power'"* as
    success, so a rule that halts whenever the equivalence band is unreachable
    halts a study its own charter calls viable. Keying a go/no-go on a secondary
    statistic is the same defect class as R4 inheriting D3a's units: the machinery
    was right and it was pointed at the wrong quantity.

    Returns the fraction of trials in which all `n_targets` point estimates are
    strictly positive. No bootstrap: the sign test uses point estimates only,
    which is also why it survives the CI width that kills `insensitive`.
    """
    rng = np.random.default_rng(seed)
    wins = 0
    for _ in range(trials):
        signs = []
        for _ in range(n_targets):
            y, f_nat, f_shuf = simulate_ligand_set(n, rho_native, rho_shuffled, rng)
            signs.append(delta_rho(y, f_nat, f_shuf) > 0.0)
        wins += int(all(signs))
    return wins / trials
