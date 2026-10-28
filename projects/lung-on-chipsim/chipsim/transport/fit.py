"""MAP fit of the two free transport parameters — build-plan T23.

WHAT IS FREE, AND WHAT IS NOT. Exactly two parameters are fit: `alpha` (the permeability scale)
and `k_sink` (elimination from the tissue compartment). Every theta field stays FIXED at its
value and is never a fit target — A&D §2 objective T3. `_negative_log_posterior` closes over
theta and touches only the two-vector it is optimising, which is the mechanical form of that rule:
there is no code path here that can widen the free set.

THREE INPUTS THE RATIFIED SPEC DOES NOT SUPPLY, MADE EXPLICIT RATHER THAN INVENTED
==================================================================================

T23's signature in the build plan is `(reference_compounds, theta)`. Both stay positional and
unchanged. But that pair is not sufficient to evaluate the forward model, and rather than default
the difference into existence, each missing piece is a REQUIRED keyword argument:

**1. `prior` — its own artifact, RULED (Finding D, r2.39).**
A&D §2 T3 reads "MAP fit in log space with `theta_priors.yaml` prior", which cannot mean what it
appears to: S13/T24 scaffold that file with EXACTLY the six A&D §1 row-S5 fields, equality-enforced,
leaving no room for `alpha`/`k_sink` without breaking the S6/S13/T24 guards. Ruled: the A&D sentence
means "the fit uses theta's FIXED values"; the prior on the two free parameters lives in its own
file — S14 scaffolds the template, T28 (human) fills `configs/transport_prior.yaml`, and
`chipsim/transport/prior.py` is the validator.

`prior` stays a REQUIRED keyword argument with NO DEFAULT, and r2.39 ratifies that rather than
merely accepting it: "keep it required even after T28 exists; T28 supplies the value, the signature
does not get a default." A default prior would be the single most consequential unsourced number in
this module — exactly what the validators exist to refuse — and Finding E is why it matters, since
at three reference rows the reported pair is substantially prior-determined.

**2. `drug_params_by_key` — T21's schema carries no per-compound ADME.**
T21 supplies `{canonical_inchikey, name, published_transport_value, evidence_doi}`. The forward
model needs `P_app`, `f_u` and `k_sink` per compound; M2's ADME heads supply them for real, and
T22's interface notes M1 uses literature defaults. Those defaults do not exist in this repo, so
the caller supplies the mapping and a compound missing from it is an error, never a default.

**3. `schedule` / `t` — the operating point the published value was measured at.**
Comparing a model prediction to a published measurement taken under a different schedule is a
category error, so the caller states the operating point rather than inheriting one from here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from chipsim.transport.ode import TransportError, transport_ode
from chipsim.transport.prior import TransportPrior
from chipsim.transport.theta import ThetaConfig, ThetaSourceError, require_sourced_theta

#: A&D §1.3 — below three reference rows no split is meaningful, so a "fit" would be a
#: restatement of the prior wearing a posterior's name.
MIN_REFERENCE_ROWS = 3

#: Columns T23 reads from T21's artifact. `name` and `evidence_doi` are deliberately NOT read:
#: this module never needs to associate a name with a structure, so it never loads that pairing.
REQUIRED_COLUMNS = ("canonical_inchikey", "published_transport_value")


class FitError(ValueError):
    """A fit this routine refuses to run."""


@dataclass(frozen=True)
class FitResult:
    """The MAP estimate plus what is needed to audit it.

    Frozen, and it carries `prior` and `n_reference` deliberately: a point estimate with the prior
    it was pulled toward omitted is not auditable, and with three rows the prior does a lot of the
    work. Reporting it beside the estimate is what makes that visible instead of implicit.
    """

    alpha: float
    k_sink: float
    objective: float
    n_reference: int
    n_iterations: int
    converged: bool
    prior: TransportPrior


def _require_sourced_theta(theta: ThetaConfig) -> None:
    """Refuse a theta field with a value, no citation, and no `assumed: true`.

    AUTHORITATIVE IMPLEMENTATION: `chipsim.transport.theta.require_sourced_theta`. This is a
    thin adapter, not a second copy — Stage 1 carried its own predicate against a
    value-carrying `theta.fields` API that no longer exists, and two implementations of one
    guard is how they drift apart.

    It is still called HERE, after `ThetaConfig.load` has already run the same guard, because
    `ThetaConfig(entries=..., source_path=...)` constructs one directly and bypasses `load`
    entirely. The upstream refusal alone would make this done-condition true only for callers
    who used the front door.

    `FitError` is preserved as the raised type so the fit's error taxonomy is unchanged for its
    callers; the underlying `ThetaSourceError` is chained, so the canonical diagnosis is not lost.
    """
    try:
        require_sourced_theta(theta.entries)
    except ThetaSourceError as exc:
        raise FitError(
            f"{theta.source_path}: {exc} A fit against a silently-unsourced prior produces a "
            f"number that looks measured and is not (A&D §1.2)."
        ) from exc


def _observations(reference_compounds: Any) -> list[tuple[str, float]]:
    """Pull (key, published value) pairs, refusing anything that would fit against nonsense."""
    for column in REQUIRED_COLUMNS:
        if column not in getattr(reference_compounds, "columns", ()):
            raise FitError(f"reference_compounds has no {column!r} column (T21 supplies it)")

    n_rows = len(reference_compounds)
    if n_rows < MIN_REFERENCE_ROWS:
        raise FitError(
            f"reference_compounds has {n_rows} row(s); the fit needs at least "
            f"{MIN_REFERENCE_ROWS} (A&D §1.3 — below that no split is meaningful and the "
            f"'fit' is the prior restated)."
        )

    pairs: list[tuple[str, float]] = []
    for key, value in zip(
        reference_compounds["canonical_inchikey"],
        reference_compounds["published_transport_value"],
        strict=True,
    ):
        numeric = float(value)
        if not np.isfinite(numeric) or numeric <= 0:
            raise FitError(
                f"published_transport_value for {key!r} is {value!r}; the fit is in LOG space, "
                f"so a non-positive measurement cannot be compared."
            )
        pairs.append((str(key), numeric))

    if len({k for k, _ in pairs}) != len(pairs):
        raise FitError("reference_compounds contains duplicate canonical_inchikey values")
    return pairs


def predict_observable(
    theta: ThetaConfig,
    drug_params: dict,
    schedule: dict,
    t: np.ndarray,
    *,
    alpha: float,
    k_sink: float,
) -> float:
    """The scalar the published measurement is compared against: cumulative free-drug exposure.

    Public because it is the model's prediction, and a fit whose forward prediction cannot be
    inspected on its own is a fit nobody can check.
    """
    curve = transport_ode(theta, {**drug_params, "k_sink": k_sink}, schedule, t, alpha=alpha)
    return float(np.trapezoid(curve, t))


def _negative_log_posterior(
    log_params: np.ndarray,
    theta: ThetaConfig,
    observations: list[tuple[str, float]],
    drug_params_by_key: dict,
    schedule: dict,
    t: np.ndarray,
    prior: TransportPrior,
) -> float:
    alpha, k_sink = float(np.exp(log_params[0])), float(np.exp(log_params[1]))
    if not (np.isfinite(alpha) and np.isfinite(k_sink)) or alpha <= 0 or k_sink <= 0:
        return np.inf

    residual = 0.0
    for key, observed in observations:
        try:
            # A fixed-step integrator can overflow on an extreme trial pair the optimiser probes
            # on its way somewhere sensible. That is not an error to report -- it is a point the
            # objective should decline. The overflow is silenced and the RESULT is then checked
            # for finiteness explicitly below, so a bad point is rejected on its value rather
            # than on a warning nobody reads.
            with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
                predicted = predict_observable(
                    theta, drug_params_by_key[key], schedule, t, alpha=alpha, k_sink=k_sink
                )
        except TransportError:
            return np.inf
        if not np.isfinite(predicted) or predicted <= 0:
            return np.inf
        residual += (np.log(predicted) - np.log(observed)) ** 2

    return (
        0.5 * residual
        + _prior_penalty(prior, "alpha_prior", alpha)
        + _prior_penalty(prior, "k_sink_prior", k_sink)
    )


def _prior_numbers(prior: TransportPrior, name: str) -> tuple[float, float] | None:
    """`(mean_log, sigma_log)` for one entry, or None when either is absent or not numeric.

    HEAD's `TransportPrior` holds an entries MAPPING whose values are typed `object`, so the
    narrowing happens here rather than being asserted away. `_check_entry` already rejects a
    non-numeric pair for a LOADED prior; this also covers one constructed by hand, which is the
    same door `_require_sourced_theta` is called twice for.
    """
    entry = prior.entries[name]
    mean_log, sigma_log = entry.get("mean_log"), entry.get("sigma_log")
    if isinstance(mean_log, (int, float)) and isinstance(sigma_log, (int, float)):
        return float(mean_log), float(sigma_log)
    return None


def _is_specified(prior: TransportPrior, name: str) -> bool:
    """Both prior numbers present. A prior missing either is not a weaker prior; it is not one.

    Ported from Stage 1's `PriorEntry.is_specified`.
    """
    return _prior_numbers(prior, name) is not None


def _prior_penalty(prior: TransportPrior, name: str, value: float) -> float:
    """Negative log density up to a constant, for one prior entry.

    Constants are dropped: they shift the objective without moving its argmin, and the argmin is
    the whole output. Formula ported verbatim from Stage 1's `PriorEntry.penalty`.

    RAISES on an unspecified entry rather than returning 0.0 — returning zero would silently make
    a scaffolded prior an improper-uniform one, a choice nobody made, doing real work on the
    result (Finding E).
    """
    numbers = _prior_numbers(prior, name)
    if numbers is None:
        entry = prior.entries[name]
        raise FitError(
            f"prior entry {name!r} has mean_log={entry.get('mean_log')!r} "
            f"sigma_log={entry.get('sigma_log')!r} — it is a DISCLOSED GAP (T28 fills it), not a "
            f"usable prior. Treating it as uninformative would invent the width."
        )
    mean_log, sigma_log = numbers
    return 0.5 * ((float(np.log(value)) - mean_log) / sigma_log) ** 2


def _nelder_mead(
    objective,
    start: np.ndarray,
    *,
    max_iter: int = 2000,
    tol: float = 1e-12,
    xtol: float = 1e-8,
):
    """Deterministic derivative-free minimisation in 2-D.

    Hand-rolled for the same reason T22's integrator is: there is no SciPy in this project, and
    the alternative to writing ~40 auditable lines is adding a runtime dependency whose internals
    decide a reported number. The initial simplex is FIXED, so two identical fits agree exactly —
    a randomly perturbed start would make the reported MAP depend on a seed nobody recorded.

    TERMINATION REQUIRES BOTH A FLAT OBJECTIVE AND A SMALL SIMPLEX. The simplex-size half is
    textbook Nelder-Mead and is kept as DEFENSIVE, and this docstring says so because it once
    said something false.

    The honest history: a fit returned alpha=2.218 against a data-generating value of 2.0, and I
    added the `xtol` criterion believing it was premature termination on a shallow ridge. It was
    not. A grid search then put the objective's true minimum at (2.24, 0.2775) — the optimiser had
    been right all along, and the estimate differed from the truth because MAP is not maximum
    likelihood and the prior was tilting a nearly degenerate valley. Mutation testing confirms it:
    removing `spread < xtol` leaves the whole suite green, including a grid-oracle convergence
    test written specifically to bind it.

    So: no test distinguishes this criterion today, and no observed bug motivated it. It stays
    because a function-spread-only stop is genuinely unsafe on a flat objective and costs nothing
    here — but it is unproven, and calling it a fix would have been a false claim about my own
    code.
    """
    simplex = [start, start + np.array([0.5, 0.0]), start + np.array([0.0, 0.5])]
    values = [objective(p) for p in simplex]
    iterations = 0

    for iterations in range(1, max_iter + 1):
        order = np.argsort(values)
        simplex = [simplex[i] for i in order]
        values = [values[i] for i in order]
        spread = max(float(np.max(np.abs(v - simplex[0]))) for v in simplex[1:])
        if abs(values[-1] - values[0]) < tol and spread < xtol:
            break

        centroid = (simplex[0] + simplex[1]) / 2.0
        reflected = centroid + (centroid - simplex[-1])
        f_reflected = objective(reflected)

        if f_reflected < values[0]:
            expanded = centroid + 2.0 * (centroid - simplex[-1])
            f_expanded = objective(expanded)
            simplex[-1], values[-1] = (
                (expanded, f_expanded) if f_expanded < f_reflected else (reflected, f_reflected)
            )
        elif f_reflected < values[1]:
            simplex[-1], values[-1] = reflected, f_reflected
        else:
            contracted = centroid + 0.5 * (simplex[-1] - centroid)
            f_contracted = objective(contracted)
            if f_contracted < values[-1]:
                simplex[-1], values[-1] = contracted, f_contracted
            else:
                for i in range(1, 3):
                    simplex[i] = simplex[0] + 0.5 * (simplex[i] - simplex[0])
                    values[i] = objective(simplex[i])

    best = int(np.argmin(values))
    return simplex[best], float(values[best]), iterations, iterations < max_iter


def fit_transport_params(
    reference_compounds: Any,
    theta: ThetaConfig,
    *,
    prior: TransportPrior,
    drug_params_by_key: dict,
    schedule: dict,
    t: np.ndarray,
    start: tuple[float, float] = (1.0, 0.1),
) -> FitResult:
    """MAP fit of `(alpha, k_sink)` in log space. Everything else stays fixed.

    Raises `FitError` on fewer than `MIN_REFERENCE_ROWS` rows, and on a theta field that carries a
    value with neither a citation nor `assumed: true`. Deterministic: the simplex start is fixed
    and the forward model is T22's, which is itself deterministic.
    """
    if not isinstance(theta, ThetaConfig):
        raise FitError(
            f"theta must be a validated ThetaConfig, got {type(theta).__name__}. The container is "
            f"what guarantees every field is cited or disclosed."
        )
    _require_sourced_theta(theta)
    if not isinstance(prior, TransportPrior):
        raise FitError(
            f"prior must be a validated TransportPrior (S14/T28), got {type(prior).__name__}. "
            f"The container is what guarantees each entry is cited or disclosed."
        )
    unusable = [name for name in prior.entries if not _is_specified(prior, name)]
    if unusable:
        raise FitError(
            f"{prior.source_path}: prior entries {sorted(unusable)} are DISCLOSED GAPS, not usable "
            f"priors — T28 supplies the numbers. Treating them as uninformative would invent the "
            f"width, and at {MIN_REFERENCE_ROWS} reference rows the prior does real work on the "
            f"reported pair (Finding E, r2.39)."
        )

    observations = _observations(reference_compounds)
    missing = sorted({key for key, _ in observations} - set(drug_params_by_key))
    if missing:
        raise FitError(
            f"drug_params_by_key has no entry for {missing}. The forward model needs P_app and "
            f"f_u per compound; T21's schema does not carry them and this routine will not "
            f"default them into existence."
        )

    times = np.asarray(t, dtype=np.float64)

    def objective(log_params: np.ndarray) -> float:
        return _negative_log_posterior(
            log_params, theta, observations, drug_params_by_key, schedule, times, prior
        )

    start_log = np.log(np.asarray(start, dtype=np.float64))
    best, value, iterations, converged = _nelder_mead(objective, start_log)

    return FitResult(
        alpha=float(np.exp(best[0])),
        k_sink=float(np.exp(best[1])),
        objective=value,
        n_reference=len(observations),
        n_iterations=iterations,
        converged=converged,
        prior=prior,
    )
