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
    if not -1.0 <= rho_s <= 1.0:
        # NaN fails this test too, which is the point: `max(0.0, nan)` returns 0.0
        # (Python keeps the first operand because `nan > 0.0` is False), so a NaN
        # rho silently produced an all-NaN arm and a confident power of 0.00.
        raise ValueError(f"rho must lie in [-1, 1] and be non-NaN; got {rho_s}")
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
    # NO max(0.0, ...) clamp: an impossible variance must raise, not become a
    # perfect correlation. The clamp turned rho=1.5 into a deterministic arm and
    # reported power 1.00 -> PROCEED.
    z_nat = r_nat * z_y + math.sqrt(1.0 - r_nat**2) * rng.standard_normal(n)
    z_shuf = r_shuf * z_y + math.sqrt(1.0 - r_shuf**2) * rng.standard_normal(n)
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


def _validate_power_domain(*, n: int, n_targets: int, trials: int) -> None:
    """Guards for the power functions themselves — not only their callers.

    These were first written into `evaluate_halt` alone. Both public power
    functions stayed reachable and silent: `n_targets=0` returned **1.0**, because
    `all([])` is True, so a study with no targets scored full power. A second
    caller — a notebook, the P0 table driver — reproduced the defect verbatim.

    **A guard belongs where the vacuity is, not where the vacuity was noticed.**
    """
    if n_targets < 2:
        raise ValueError(
            f"n_targets={n_targets}; a unanimous sign across fewer than 2 targets is "
            "vacuous — all([]) is True and all([x]) is just x"
        )
    if n < 4:
        raise ValueError(f"n={n} ligands cannot support a rank statistic")
    if trials < 1:
        raise ValueError(f"trials={trials}; power cannot be estimated from no trials")


def wilson_lower_bound(successes: int, trials: int, *, z: float = 1.645) -> float:
    """One-sided 95% Wilson lower bound on a binomial proportion.

    **The gate compares THIS to the floor, not the point estimate.** At p=0.80 with
    300 trials the binomial SE is 0.023, so the 95% interval is about ±0.045 — it
    straddles the 0.80 floor. Measured over 20 seeds on one fixed design, the point
    estimate authorised the spend on **8 of 20**: the same study, the same roster,
    and the seed decided whether ~$27 was spent.

    A gate whose verdict is a coin flip near its own threshold is not a gate. The
    lower bound makes the comparison answer the right question — *"is power
    demonstrably at least the floor?"* rather than *"did this sample land above
    it?"* — and errs toward HALT, which is the direction a spending gate should err.
    """
    if trials < 1:
        raise ValueError(f"trials={trials}; no proportion to bound")
    if not 0 <= successes <= trials:
        raise ValueError(f"successes={successes} outside [0, {trials}]")
    phat = successes / trials
    denom = 1.0 + z * z / trials
    centre = phat + z * z / (2 * trials)
    margin = z * math.sqrt(phat * (1 - phat) / trials + z * z / (4 * trials * trials))
    return max(0.0, (centre - margin) / denom)


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
    _validate_power_domain(n=n, n_targets=n_targets, trials=trials)
    rng = np.random.default_rng(seed)
    wins = 0
    for _ in range(trials):
        signs = []
        for _ in range(n_targets):
            y, f_nat, f_shuf = simulate_ligand_set(n, rho_native, rho_shuffled, rng)
            signs.append(delta_rho(y, f_nat, f_shuf) > 0.0)
        wins += int(all(signs))
    return wins / trials


def simulate_clustered_ligand_set(
    n: int,
    rho_native: float,
    rho_shuffled: float,
    rng: np.random.Generator,
    *,
    cluster_size: int,
    icc: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """A ligand set containing **analog series** — A7, made measurable.

    `simulate_ligand_set` assumes ligands are exchangeable independent draws. A
    ~40-compound set assembled from ChEMBL against transporters is not: it arrives
    as **analog series** — groups of near-identical structures from one
    medicinal-chemistry campaign, with similar potencies and similar predictions.

    **What clustering has to do, and what a first version got wrong.** The initial
    implementation clustered only the *prediction noise* and left the latent `z_y`
    independent. That reduced no information at all: `ρ(f, y)` is driven by `z_y`,
    so the measured power came out marginally *higher* than the unclustered case
    (0.94 vs 0.92) and the model would have argued A7 is free. The effect is not
    correlated errors — it is that **the (y, f) pairs within a series are near
    duplicates**, so a set of `n` compounds carries roughly `n_clusters` independent
    observations.

    Modelled accordingly: each series draws a prototype, and its members are that
    prototype plus a shrinking perturbation. At `icc → 1` a series collapses to one
    repeated point; at `icc = 0` the members are independent and this reduces to
    `simulate_ligand_set` in distribution. The design effect
    `n_eff ≈ n / (1 + (cluster_size − 1)·icc)` then applies — at
    `cluster_size=5, icc=0.5`, forty compounds behave like about thirteen.
    """
    if not 0.0 <= icc <= 1.0:
        raise ValueError(f"icc must be in [0, 1], got {icc}")
    if cluster_size < 1:
        raise ValueError(f"cluster_size must be >= 1, got {cluster_size}")
    if math.ceil(n / cluster_size) < 2:
        # *** THE WORST ROSTER SCORED BEST. ***
        # With one cluster the shared component is a single scalar added
        # identically to every member, and A CONSTANT OFFSET CANCELS OUT OF EVERY
        # RANK STATISTIC. So maximal clustering degenerated to NO clustering:
        # power was non-monotonic in cluster_size and inverted at the boundary —
        # cluster_size=20 gave 0.240 (HALT) and cluster_size=40 gave 0.945
        # (PROCEED) on the same 40 compounds. "All 40 from one med-chem campaign"
        # is a realistic ChEMBL-transporter roster, is the single worst case for
        # A7, and was the case this model scored best.
        raise ValueError(
            f"cluster_size={cluster_size} with n={n} yields a single cluster; a "
            "one-cluster roster carries one independent observation and cannot be "
            "represented by this construction (the shared term becomes a constant "
            "offset, which cancels out of a rank statistic)"
        )

    r_nat = _spearman_to_pearson(rho_native)
    r_shuf = _spearman_to_pearson(rho_shuffled)

    n_clusters = math.ceil(n / cluster_size)
    labels = np.repeat(np.arange(n_clusters), cluster_size)[:n]
    w_shared, w_own = math.sqrt(icc), math.sqrt(1.0 - icc)

    def _clustered() -> np.ndarray:
        """Prototype per series + per-member perturbation; unit variance overall."""
        return w_shared * rng.standard_normal(n_clusters)[labels] + w_own * rng.standard_normal(n)

    # The LATENT is clustered — this is the correction. Members of a series share
    # most of their position in affinity space, which is precisely why they carry
    # less independent information than their count suggests.
    z_y = _clustered()
    z_nat = r_nat * z_y + math.sqrt(1.0 - r_nat**2) * _clustered()
    z_shuf = r_shuf * z_y + math.sqrt(1.0 - r_shuf**2) * _clustered()
    return z_y, z_nat, z_shuf


def effective_n(n: int, cluster_size: int, icc: float) -> float:
    """`n / (1 + (cluster_size − 1)·icc)` — the design effect.

    Reported alongside power so the discount is legible as a sample size rather
    than only as a probability. A reader who sees "power fell from 0.92 to 0.61"
    learns less than one who sees "40 compounds behaved like 13".
    """
    return n / (1.0 + (cluster_size - 1) * icc)


def clustered_sign_test_power(
    *,
    n: int,
    n_targets: int,
    rho_native: float,
    rho_shuffled: float,
    cluster_size: int,
    icc: float,
    trials: int = 300,
    seed: int = 0,
) -> float:
    """Sign-test power when the ligand set contains analog series (A7)."""
    _validate_power_domain(n=n, n_targets=n_targets, trials=trials)
    rng = np.random.default_rng(seed)
    wins = 0
    for _ in range(trials):
        signs = []
        for _ in range(n_targets):
            y, f_nat, f_shuf = simulate_clustered_ligand_set(
                n, rho_native, rho_shuffled, rng, cluster_size=cluster_size, icc=icc
            )
            signs.append(delta_rho(y, f_nat, f_shuf) > 0.0)
        wins += int(all(signs))
    return wins / trials


#: The pre-registered power floor — ADR-0003, principal's ruling 2026-09-08.
#: Simulated power at `Δρ = 0.5` over seven targets. A 0.70 floor was rejected:
#: a 30% miss rate, and a missed effect reads as `insensitive` — the verdict this
#: study cannot render, so a miss is not merely a null, it is unpublishable.
POWER_FLOOR = 0.80

#: `Δρ` at which the floor is evaluated. The A&D declares the study "powered for a
#: large effect only"; P0 quantified *large* as `Δρ ≳ 0.5`.
FLOOR_EFFECT = 0.5

#: `icc` is NOT measurable before the spend — series membership is computable from
#: SMILES, but the correlation of `(y, f)` contributions is not, because `f` does
#: not exist until the batch runs. So the floor is required to hold across a
#: sensitivity band rather than at a point estimate.
DEFAULT_ICC_BAND = (0.3, 0.5, 0.8)


@dataclass(frozen=True)
class HaltDecision:
    """The pre-hoc gate. `proceed` is the only field a caller may branch on."""

    worst_icc: float
    worst_power: float
    worst_power_lcb: float
    floor: float
    trials: int
    rows: tuple[tuple[float, float], ...]

    def __post_init__(self) -> None:
        if not self.rows:
            raise ValueError("a HaltDecision over no rows attests to nothing")

    @property
    def proceed(self) -> bool:
        """DERIVED, never stored.

        This was a plain field, so nothing tied the verdict to the numbers printed
        to justify it — `HaltDecision(proceed=True, worst_power=0.11, floor=0.80)`
        constructed cleanly and its own `reason()` announced PROCEED. The docstring
        called `proceed` "the only field a caller may branch on", which made the
        invariant load-bearing while leaving it enforced by exactly one call site.

        Compares the LOWER BOUND, not the point estimate — see `wilson_lower_bound`.
        """
        return self.worst_power_lcb >= self.floor

    def reason(self) -> str:
        verdict = "PROCEED" if self.proceed else "HALT"
        # :.3f, not :.2f — at :.2f a HALT on 0.7961 printed as "power 0.80 against a
        # floor of 0.80", so the audit log contradicted the verdict beside it.
        return (
            f"{verdict}: worst-case simulated power {self.worst_power:.3f} "
            f"(95% lower bound {self.worst_power_lcb:.3f}, {self.trials} trials) at "
            f"icc={self.worst_icc} against a floor of {self.floor:.3f}. "
            "Simulated power is an UPPER BOUND (A2: measured affinities are treated "
            "as noise-free; real assay error attenuates rho_native), so the true "
            "value is lower than every figure here."
        )


def evaluate_halt(
    *,
    cluster_size: int,
    n: int,
    n_targets: int = 7,
    icc_band: tuple[float, ...] = DEFAULT_ICC_BAND,
    floor: float = POWER_FLOOR,
    effect: float = FLOOR_EFFECT,
    trials: int = 300,
    seed: int = 4242,
) -> HaltDecision:
    """G3's halt rule, keyed on DIRECTLY SIMULATED power — never on `n_eff`.

    **`n_eff` is not the gate quantity, and keying on it halts powered studies.**
    Measured: at an equal `n_eff = 20`, a diverse roster of 20 gives **0.683** and a
    clustered roster of 60 (series of 5, icc 0.5) gives **0.923**. The design effect
    is derived for estimating a *mean*; the sign test consumes only the *direction*
    of `Δρ` per target, and clustering costs less information about a direction than
    about a mean. So `n_eff` is **conservative** for this statistic — `series.py`
    computes it correctly and it is the wrong input to this decision.

    That is the sixth instance of this design's standing check, and the first in
    which the wrong quantity was *more* pessimistic rather than less: the gate would
    have refused to spend on a study that was adequately powered.

    The floor must hold across `icc_band`, not at a point, because **`icc` cannot be
    measured before the spend** — series membership is computable from SMILES, but
    the correlation of `(y, f)` contributions is not, since `f` does not exist until
    the batch runs. The decision is taken on the worst cell in the band.
    """
    # Every guard below refuses input this gate cannot evaluate. The module's
    # documented failure mode is a PLAUSIBLE NUMBER WITH NO EXCEPTION, and each of
    # these was reachable and returned exactly that.
    if not icc_band:
        raise ValueError("icc_band is empty; an empty band satisfies any floor vacuously")
    if len(set(icc_band)) < 2:
        # Counting entries is not the property. `(0.5, 0.5)` passes a length check
        # while being a point estimate, and it returned PROCEED. The rule cares
        # about DISTINCT values, so that is what is checked.
        raise ValueError(
            f"icc_band {tuple(icc_band)} has fewer than 2 distinct values; icc is "
            "unmeasurable pre-spend, so the floor must hold across a band rather "
            "than at a point estimate"
        )
    if n_targets < 2:
        # `all([])` is True, so n_targets=0 gave every trial a vacuous win: power
        # 1.0 and PROCEED, on a study with no targets. This is the SAME all([])
        # vacuity guarded above for icc_band, reintroduced one function away in
        # `clustered_sign_test_power`, in the commit that fixed the first one.
        # A unanimity criterion over fewer than two targets is not a criterion.
        raise ValueError(
            f"n_targets={n_targets}; a unanimous sign across fewer than 2 targets is "
            "vacuous — all([]) is True and all([x]) is just x"
        )
    if n < 4:
        raise ValueError(f"n={n} ligands cannot support a bootstrap or a rank statistic")
    if trials < 1:
        raise ValueError(f"trials={trials}; power cannot be estimated from no trials")

    if not 0.0 < floor <= 1.0:
        # NaN fails this too. An unvalidated floor authorised rather than raised:
        # floor=0.0 gave PROCEED on power 0.47, floor=-1.0 gave PROCEED always.
        raise ValueError(f"floor must lie in (0, 1] and be non-NaN; got {floor}")

    rows = tuple(
        (
            icc,
            clustered_sign_test_power(
                n=n,
                n_targets=n_targets,
                rho_native=effect,
                rho_shuffled=0.0,
                cluster_size=cluster_size,
                icc=icc,
                trials=trials,
                # PER-CELL seed. With one shared seed every cell drew the same
                # shapes, so the band was common random numbers — one Monte Carlo
                # sample presented as three, and an unlucky seed shifted all rows
                # together. `min` over the band then bought none of the robustness
                # the "worst cell" language implies.
                seed=seed + i,
            ),
        )
        for i, icc in enumerate(icc_band)
    )
    # Ties resolve to the HARSHER icc: `min` returns the first row on a tie, so the
    # reported worst_icc could name a milder cell than the one that set the bound.
    worst_icc, worst_power = min(rows, key=lambda r: (r[1], -r[0]))
    return HaltDecision(
        worst_icc=worst_icc,
        worst_power=worst_power,
        worst_power_lcb=wilson_lower_bound(round(worst_power * trials), trials),
        floor=floor,
        trials=trials,
        rows=rows,
    )
