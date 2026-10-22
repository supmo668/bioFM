"""T23 — the MAP fit of the two free transport parameters.

Done-when, per build-plan T23:
  1. fitting a synthetic fixture with a known-recoverable (alpha, sink) recovers both within a
     stated tolerance;
  2. fitting RAISES on fewer than 3 reference rows;
  3. fitting RAISES on an uncited, unmarked theta field.

NO REAL COMPOUND IDENTITY APPEARS HERE. T21's artifact is a name-beside-structure table, which is
the hygiene-sensitive shape this project is careful about. This module never needs that pairing --
`REQUIRED_COLUMNS` reads the key and the measurement and deliberately not `name` -- so the fixtures
use obviously-synthetic tokens (`SYNTHETIC-KEY-1`) that cannot be mistaken for an InChIKey, and no
`name` column at all. The theta values are the same transparently-synthetic unit-scale placeholders
T22's tests use, built in `tmp_path` and never committed.

Clause 3 deserves a note. `load_theta` already refuses an uncited, unmarked field, so a theta that
came through the front door can never reach the fit in that state. The test therefore constructs a
`ThetaConfig` DIRECTLY -- which is possible, because it is an ordinary dataclass whose
`__post_init__` checks only field NAMES -- and that is exactly the bypass the fit's own check
exists to close. Asserting it only through `load_theta` would have tested T24 a second time and
left T23's stated refusal unexercised.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from chipsim.transport.fit import (
    MIN_REFERENCE_ROWS,
    FitError,
    _negative_log_posterior,
    fit_transport_params,
    predict_observable,
)
from chipsim.transport.prior import TransportPrior
from chipsim.transport.theta import ThetaConfig, load_theta_priors

_SYNTHETIC = {
    "flow_ul_min": (1.0, "uL/min"),
    "membrane_um": (10.0, "um"),
    "porosity": (0.5, "fraction"),
    "strain_pct": (5.0, "percent"),
    "area_mm2": (1.0, "mm^2"),
    "coating": ("synthetic-placeholder", "categorical"),
}

_SCHEDULE = {
    "dose_nmol": 10.0,
    "duration_min": 100_000.0,
    "v_apical_ul": 100.0,
    "v_basolateral_ul": 100.0,
}
_T = np.linspace(0.0, 600.0, 121)

#: The pair the synthetic observations are generated from, and the pair the fit must recover.
_TRUE_ALPHA, _TRUE_K_SINK = 2.0, 0.25

#: EFFECTIVELY FLAT, and NOT centred on the truth. Both halves are load-bearing and neither is
#: arbitrary -- this fixture was wrong twice before it was right, and the measurements are here so
#: the next reader does not repeat the reasoning.
#:
#: Not centred on the truth, because a prior sitting on the answer lets a routine that never moves
#: "recover" it.
#:
#: Effectively flat, because MAP IS NOT MAXIMUM LIKELIHOOD and done-when 1 is a statement about
#: the LIKELIHOOD's argmin. MEASURED: the synthetic observations reproduce EXACTLY at (2.0, 0.25),
#: so the residual there is exactly zero -- the truth is the residual's global minimum. But alpha
#: and k_sink trade off along a nearly degenerate ridge (see
#: `test_t23_the_two_parameters_are_only_WEAKLY_identifiable`), so even a sigma_log=25 prior
#: centred at 1.0 slid the MAP to (2.24, 0.2775), where the objective is genuinely LOWER
#: (1.8719e-3 vs 1.9218e-3). The optimiser was right both times; the fixture was demanding MLE
#: behaviour from a MAP estimator.
#:
#: So the prior here is made negligible, and the prior's real influence is asserted separately by
#: `test_t23_an_informative_prior_SHOULD_move_the_map_off_the_truth` and
#: `test_t23_the_prior_actually_constrains`. Widening this tolerance instead would have hidden a
#: property of the model behind a looser number.
_PRIOR = None  # assigned below, after the helper

#: Three compounds differing only in P_app, which is what makes the pair identifiable.
_DRUG_PARAMS = {
    "SYNTHETIC-KEY-1": {"p_app_cm_s": 0.5, "f_u": 0.5, "k_sink": 0.0},
    "SYNTHETIC-KEY-2": {"p_app_cm_s": 1.0, "f_u": 0.5, "k_sink": 0.0},
    "SYNTHETIC-KEY-3": {"p_app_cm_s": 2.0, "f_u": 0.5, "k_sink": 0.0},
}


def _prior(mean_log: float = 0.0, sigma_log: float = 10_000.0) -> TransportPrior:
    """A TransportPrior built DIRECTLY, not loaded from a file.

    Direct construction is deliberate and mirrors the ThetaConfig fixtures: `configs/
    transport_prior.yaml` is human-owned (T28) and does not exist, so a test that loaded it would
    be testing T28's absence rather than the fit. `prior.py`'s own tests cover the file path.
    """
    return TransportPrior(
        entries={
            name: {
                "mean_log": mean_log,
                "sigma_log": sigma_log,
                "citation": None,
                "assumed": True,
            }
            for name in ("alpha_prior", "k_sink_prior")
        },
        source_path=Path("constructed-in-test.yaml"),
    )


_PRIOR = _prior()


def _theta(tmp_path: Path, **overrides) -> ThetaConfig:
    body = {
        name: {
            "value": overrides.get(name, value),
            "unit": unit,
            "citation": None,
            "assumed": True,
        }
        for name, (value, unit) in _SYNTHETIC.items()
    }
    tmp_path.mkdir(parents=True, exist_ok=True)
    path = tmp_path / "theta.yaml"
    path.write_text(yaml.safe_dump({"theta": body}), encoding="utf-8")
    return load_theta_priors(path)


def _reference(theta: ThetaConfig, keys=None) -> pd.DataFrame:
    """Observations GENERATED BY THE FORWARD MODEL at the true pair — so the fit has a
    known-recoverable answer, which is precisely what done-when 1 asks for."""
    rows = []
    for key in keys if keys is not None else sorted(_DRUG_PARAMS):
        rows.append(
            {
                "canonical_inchikey": key,
                "published_transport_value": predict_observable(
                    theta,
                    _DRUG_PARAMS[key],
                    _SCHEDULE,
                    _T,
                    alpha=_TRUE_ALPHA,
                    k_sink=_TRUE_K_SINK,
                ),
            }
        )
    return pd.DataFrame(rows)


def _fit(theta: ThetaConfig, reference: pd.DataFrame, **kwargs):
    return fit_transport_params(
        reference,
        theta,
        prior=kwargs.pop("prior", _PRIOR),
        drug_params_by_key=kwargs.pop("drug_params_by_key", _DRUG_PARAMS),
        schedule=_SCHEDULE,
        t=_T,
        **kwargs,
    )


def test_t23_recovers_a_known_pair(tmp_path):
    """Done-when 1, with the tolerance STATED: 2% on each parameter."""
    theta = _theta(tmp_path)
    result = _fit(theta, _reference(theta))

    assert result.converged, "the optimiser hit its iteration cap"
    assert result.alpha == pytest.approx(_TRUE_ALPHA, rel=0.02)
    assert result.k_sink == pytest.approx(_TRUE_K_SINK, rel=0.02)
    assert result.n_reference == 3


def test_t23_recovers_from_a_DIFFERENT_start(tmp_path):
    """The recovery must be a property of the objective, not of starting on the answer.

    Without this, a routine that returned its own start unchanged would pass done-when 1 whenever
    the start happened to be near the truth.
    """
    theta = _theta(tmp_path)
    far = _fit(theta, _reference(theta), start=(0.05, 5.0))

    assert far.alpha == pytest.approx(_TRUE_ALPHA, rel=0.05)
    assert far.k_sink == pytest.approx(_TRUE_K_SINK, rel=0.05)


def test_t23_raises_below_three_reference_rows(tmp_path):
    """Done-when 2 (A&D §1.3)."""
    theta = _theta(tmp_path)
    two_rows = _reference(theta, keys=["SYNTHETIC-KEY-1", "SYNTHETIC-KEY-2"])

    with pytest.raises(FitError, match=str(MIN_REFERENCE_ROWS)):
        _fit(theta, two_rows)


def test_t23_exactly_three_rows_is_ALLOWED(tmp_path):
    """The boundary, asserted in both directions: A&D §1.3 says fewer than three is meaningless,
    so three itself must fit. An off-by-one here would silently block the minimum viable T21."""
    theta = _theta(tmp_path)

    assert _fit(theta, _reference(theta)).n_reference == MIN_REFERENCE_ROWS


def test_t23_raises_on_a_silently_unsourced_theta_field(tmp_path):
    """Done-when 3 — and the ONLY way to reach this state is the constructor bypass.

    `load_theta` refuses such a file, so this theta is built directly. That is not a contrived
    setup: it is the exact door a caller walks through when it assembles a ThetaConfig by hand,
    and the fit's refusal exists to close it.
    """
    silent = ThetaConfig(
        entries={
            name: {
                "value": 1.0 if name != "coating" else "x",
                "unit": unit,
                "citation": None,
                # the offending field: a value, no citation, and NOT disclosed as assumed
                "assumed": name != "flow_ul_min",
            }
            for name, (_, unit) in _SYNTHETIC.items()
        },
        source_path=Path("constructed-directly.yaml"),
    )

    with pytest.raises(FitError, match="flow_ul_min"):
        _fit(silent, pd.DataFrame())


def test_t23_a_disclosed_gap_does_NOT_block_the_fit(tmp_path):
    """`assumed: true` is disclosure, not an error — the same posture T24 and T22 take.

    Without this, done-when 3 could be satisfied by refusing every uncited field, which would make
    the fit unusable until T20 runs and would push people toward inventing citations.
    """
    theta = _theta(tmp_path)
    assert all(theta.is_assumed(name) for name in _SYNTHETIC)

    assert _fit(theta, _reference(theta)).converged


def test_t23_theta_is_never_widened_into_the_free_set(tmp_path):
    """A&D §2 T3: only alpha and k_sink are free. Fitting must leave theta untouched.

    Asserted on the CONTAINER after the fit, because the failure this guards against is a routine
    that 'helpfully' tunes a theta field and reports a better objective for it.
    """
    theta = _theta(tmp_path)
    before = theta.entries

    _fit(theta, _reference(theta))

    assert theta.entries == before
    assert not hasattr(_fit(theta, _reference(theta)), "membrane_um")


def test_t23_is_deterministic(tmp_path):
    """Two fits of identical inputs must agree exactly — the simplex start is fixed and the
    forward model is T22's. A seeded perturbation would make the reported MAP depend on a seed
    nobody recorded."""
    theta = _theta(tmp_path)
    reference = _reference(theta)

    first, second = _fit(theta, reference), _fit(theta, reference)

    assert (first.alpha, first.k_sink, first.objective) == (
        second.alpha,
        second.k_sink,
        second.objective,
    )


def test_t23_refuses_a_raw_dict_theta(tmp_path):
    """The ThetaConfig type IS the guarantee that every field was validated; a bare dict routes
    around T24 entirely.

    Added because mutation testing found this guard UNBOUND: deleting the isinstance check left
    the whole suite green. T22 had the equivalent test and T23 did not, which is exactly the kind
    of gap that survives review -- the code looked symmetric, the tests were not.
    """
    with pytest.raises(FitError, match="ThetaConfig"):
        fit_transport_params(
            pd.DataFrame(),
            {"flow_ul_min": 1.0},  # type: ignore[arg-type]
            prior=_PRIOR,
            drug_params_by_key=_DRUG_PARAMS,
            schedule=_SCHEDULE,
            t=_T,
        )


def test_t23_the_optimiser_finds_the_TRUE_optimum_on_the_shallow_ridge(tmp_path):
    """Convergence QUALITY, checked against an independent grid search rather than against itself.

    This test was written to bind the optimiser's simplex-size termination criterion, and IT DOES
    NOT: mutation testing shows the criterion can still be deleted with the suite staying green.
    That failure is recorded rather than hidden, because it corrects something I got wrong -- the
    alpha=2.218 result I first blamed on premature termination turned out to be the objective's
    actual optimum, so there was never a convergence bug for this test to catch.

    It is kept because what it DOES assert is worth asserting on its own: that the returned
    objective is no worse than the best point on a coarse grid, checked by an oracle outside the
    optimiser. That is a real convergence-quality guarantee even though it is not the one it was
    commissioned for.
    """
    theta = _theta(tmp_path)
    reference = _reference(theta)
    tilted = _prior(mean_log=float(np.log(1.0)), sigma_log=25.0)

    result = _fit(theta, reference, prior=tilted)

    observations = [
        (row.canonical_inchikey, float(row.published_transport_value))
        for row in reference.itertuples()
    ]
    grid_best = min(
        _negative_log_posterior(
            np.log([a, k]), theta, observations, _DRUG_PARAMS, _SCHEDULE, _T, tilted
        )
        for a in np.linspace(1.8, 2.8, 21)
        for k in np.linspace(0.20, 0.36, 21)
    )

    assert result.objective <= grid_best + 1e-9, (
        f"the optimiser stopped at {result.objective!r}, worse than a coarse grid's "
        f"{grid_best!r} — it terminated on a flat region of the ridge rather than at the optimum"
    )


def test_t23_raises_when_a_compound_has_no_drug_params(tmp_path):
    """T21's schema carries no ADME, so the mapping is required. A defaulted P_app would make the
    fit silently about a compound nobody described."""
    theta = _theta(tmp_path)
    partial = {k: v for k, v in _DRUG_PARAMS.items() if k != "SYNTHETIC-KEY-3"}

    with pytest.raises(FitError, match="SYNTHETIC-KEY-3"):
        _fit(theta, _reference(theta), drug_params_by_key=partial)


@pytest.mark.parametrize("bad", [0.0, -1.0])
def test_t23_refuses_non_positive_measurements(tmp_path, bad):
    """The fit is in LOG space; a non-positive published value cannot be compared and must not
    become a silent -inf."""
    theta = _theta(tmp_path)
    reference = _reference(theta)
    reference.loc[0, "published_transport_value"] = bad

    with pytest.raises(FitError, match="LOG space"):
        _fit(theta, reference)


def test_t23_refuses_duplicate_reference_keys(tmp_path):
    """A duplicated compound silently double-weights one measurement."""
    theta = _theta(tmp_path)
    reference = _reference(theta)
    reference.loc[2, "canonical_inchikey"] = reference.loc[1, "canonical_inchikey"]

    with pytest.raises(FitError, match="duplicate"):
        _fit(theta, reference)


def test_t23_refuses_a_missing_column(tmp_path):
    """T21 supplies the columns; a missing one is a malformed artifact, not a defaultable gap."""
    theta = _theta(tmp_path)
    reference = _reference(theta).drop(columns=["published_transport_value"])

    with pytest.raises(FitError, match="published_transport_value"):
        _fit(theta, reference)


def test_t23_result_reports_the_prior_it_was_pulled_toward(tmp_path):
    """A point estimate without its prior is not auditable — at three rows the prior does real
    work, and FitResult carries it so that is visible rather than implicit."""
    theta = _theta(tmp_path)
    result = _fit(theta, _reference(theta))

    assert result.prior is _PRIOR
    with pytest.raises(FrozenInstanceError):
        result.alpha = 1.0  # type: ignore[misc]


def test_t23_the_two_parameters_are_only_WEAKLY_identifiable(tmp_path):
    """A PROPERTY OF THE MODEL, measured and pinned rather than discovered again later.

    T21 supplies ONE scalar per compound, and alpha and k_sink influence that scalar through a
    nearly degenerate combination: raising alpha and raising k_sink together leaves the predicted
    exposure almost unchanged. So the residual valley is a long shallow ridge, and a prior with
    any real weight slides the estimate along it.

    This is not a defect -- it is why A&D §2 T3 specifies a MAP fit with a prior rather than a
    maximum-likelihood fit. It IS something a reader of `FitResult` must know, because it means
    the reported pair at three reference rows is substantially prior-determined.

    Asserted as: two points far apart in alpha have residuals that differ by less than the prior
    penalty a modest prior would impose.
    """
    theta = _theta(tmp_path)
    reference = _reference(theta)

    at_truth = _fit(theta, reference)
    assert at_truth.objective < 1e-6, (
        "with a negligible prior the objective at the optimum should be essentially pure residual"
    )

    nudged = _fit(
        theta,
        reference,
        prior=_prior(mean_log=float(np.log(1.0)), sigma_log=25.0),
    )
    assert nudged.alpha > at_truth.alpha * 1.05, (
        "a sigma_log=25 prior -- almost no prior at all -- failed to move the estimate, which "
        "would mean the ridge is NOT shallow and this docstring is wrong"
    )


def test_t23_an_informative_prior_SHOULD_move_the_map_off_the_truth(tmp_path):
    """MAP IS NOT MAXIMUM LIKELIHOOD, and this is the test that says so out loud.

    With an informative prior centred away from the data-generating pair, the MAP estimate must
    NOT equal that pair -- it is supposed to be pulled toward the prior, and at three reference
    rows (the A&D §1.3 minimum) the pull is large. This is the exact behaviour that read as a bug
    when the recovery fixture was accidentally informative: the estimate landed at alpha=2.58
    against a truth of 2.0, and the objective there was genuinely lower.

    Pinned here so nobody "fixes" it by widening the recovery tolerance until both pass.
    """
    theta = _theta(tmp_path)
    reference = _reference(theta)

    informative = _fit(
        theta,
        reference,
        prior=_prior(mean_log=float(np.log(1.0)), sigma_log=2.0),
    )
    weak = _fit(theta, reference)

    assert informative.alpha > _TRUE_ALPHA * 1.1, (
        "an informative prior centred above the truth did not pull the estimate up"
    )
    assert abs(weak.alpha - _TRUE_ALPHA) < abs(informative.alpha - _TRUE_ALPHA), (
        "weakening the prior did not move the MAP closer to the data-generating value"
    )


def test_t23_the_prior_actually_constrains(tmp_path):
    """The prior must be load-bearing, not decorative.

    A prior tightly centred away from the truth must pull the estimate away from it. Without this,
    `penalty()` could return a constant and every other test here would still pass.
    """
    theta = _theta(tmp_path)
    reference = _reference(theta)
    pulled = _fit(
        theta,
        reference,
        prior=TransportPrior(
            entries={
                "alpha_prior": {
                    "mean_log": float(np.log(0.01)),
                    "sigma_log": 0.01,
                    "citation": None,
                    "assumed": True,
                },
                "k_sink_prior": {
                    "mean_log": 0.0,
                    "sigma_log": 2.0,
                    "citation": None,
                    "assumed": True,
                },
            },
            source_path=Path("constructed-in-test.yaml"),
        ),
    )

    assert pulled.alpha < _TRUE_ALPHA * 0.5, "a tight, distant prior did not move the estimate"


def test_t23_refuses_a_prior_that_is_a_disclosed_gap(tmp_path):
    """S14's scaffold LOADS (it is a stated gap) but must not silently fit as uninformative.

    Finding E is the reason this is an error rather than a shrug: at three reference rows the
    prior does real work on the reported pair, so an unspecified prior quietly treated as flat
    would invent the width AND move the answer.
    """
    theta = _theta(tmp_path)
    scaffolded = TransportPrior(
        entries={
            name: {
                "mean_log": None,
                "sigma_log": None,
                "citation": None,
                "assumed": True,
            }
            for name in ("alpha_prior", "k_sink_prior")
        },
        source_path=Path("transport_prior.scaffold.yaml"),
    )

    with pytest.raises(FitError, match="DISCLOSED GAP"):
        _fit(theta, _reference(theta), prior=scaffolded)


def test_t23_refuses_a_prior_that_is_not_a_TransportPrior(tmp_path):
    """The container is the guarantee; a bare tuple or dict routes around S14/T28's validator."""
    theta = _theta(tmp_path)

    with pytest.raises(FitError, match="TransportPrior"):
        _fit(theta, _reference(theta), prior={"alpha_prior": (0.0, 1.0)})
