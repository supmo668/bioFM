"""Two-compartment transport core — build-plan T22.

WHAT THIS IS. The apical (dosed) channel and the basolateral (tissue-face) channel of the chip,
separated by the porous membrane. `C_free(t)` at the tissue face is the ONLY value anything
downstream reads (A&D "the whole design in one picture"), so it is the only thing returned.

SIX PARAMETERS, TWO FREE (A&D §2 objective T3):

  | parameter        | source                         | free? |
  |------------------|--------------------------------|-------|
  | alpha            | fit (T23)                      | FREE  |
  | k_sink           | fit (T23)                      | FREE  |
  | P_app            | drug_params (P1 head in M2)    | fixed |
  | f_u              | drug_params (P2 head in M2)    | fixed |
  | A_eff / L        | theta geometry                 | fixed |
  | Q                | theta flow                     | fixed |

Every theta field is FIXED at its value; nothing here fits theta. That is what "only alpha and
the sink coefficient are genuinely free" means, and `fit_transport_params` (T23) must not widen it.

TWO DELIBERATE DEVIATIONS, FLAGGED RATHER THAN SILENT
=====================================================

**1. The integrator is a fixed-step RK4 written here, NOT SciPy `solve_ivp` or `torchdiffeq`,
which are the two the A&D §3 module table names.** Neither is installed, so this was a choice
either way and is recorded as one.

The reason is T22's own done-condition (2): two calls with identical inputs must return
BIT-IDENTICAL arrays. An adaptive solver satisfies that within one installed version while making
it quietly false across an upgrade, because the accepted step sequence is part of the library's
behaviour, not of this model. That is the same hazard `pyproject.toml` already pins `pyarrow` and
`rdkit` for, in its own words: bytes "not stable across versions" underneath a recorded sha256.
A fixed step grid has no such freedom — determinism here is a property of the code, not of a
dependency's release notes.

The cost is honest: RK4 at a fixed step is not adaptive, so a stiff parameterisation is less
accurate than `solve_ivp` would be, and this core is not differentiable the way `torchdiffeq`
would make it (M2 needs that for end-to-end gradients; M1 does not). `_integrate` is the single
seam — swapping it for a pinned `solve_ivp` is a local change behind an unchanged signature.

**2. `strain_pct` and `coating` are VALIDATED AND CARRIED BUT NOT COUPLED to permeability.**
They are required, they must be present and well-formed, and they do not enter the equations.

This is not an oversight and a test pins it. Membrane geometry enters through Fick's law, which is
a definition; perfusion enters as a clearance term, also a definition. But "how much does 10%
cyclic strain change barrier permeability" and "how much does a fibronectin coating change it" are
EMPIRICAL relationships, and no citation for them exists in this repo -- `configs/theta_priors.yaml`
does not exist yet and is human-owned (S6, Global Constraint 1). Writing a coupling coefficient
would mean inventing the number that matters most and burying it in code, where the theta
validator that exists precisely to catch unsourced values could never see it. An unsourced
coefficient in a config is refused by T24; the same coefficient hard-coded here would sail through.

So the dependence is ABSENT and LOUD rather than present and fabricated. Wiring it is a task for
whoever holds a citation.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from chipsim.transport.theta import ThetaConfig

#: Substeps taken between consecutive requested output times. Fixed, because it is part of the
#: determinism contract: changing it changes the returned array, so it is a constant of this
#: module rather than a tunable a caller could vary without noticing.
_SUBSTEPS_PER_INTERVAL = 8

#: Schedule keys with no default. A missing volume is the kind of value a helpful default would
#: silently invent, and this module refuses those on the same grounds T24 refuses an absent file.
_REQUIRED_SCHEDULE = ("dose_nmol", "duration_min", "v_apical_ul", "v_basolateral_ul")

#: drug_params keys with no default, for the same reason.
_REQUIRED_DRUG = ("p_app_cm_s", "f_u", "k_sink")


class TransportError(ValueError):
    """An input this core refuses to integrate."""


def _positive(value: Any, name: str, *, strict: bool = True) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError) as exc:
        raise TransportError(f"{name} must be a real number, got {value!r}") from exc
    if not np.isfinite(numeric):
        raise TransportError(f"{name} must be finite, got {numeric!r}")
    if strict and numeric <= 0:
        raise TransportError(f"{name} must be > 0, got {numeric!r}")
    if not strict and numeric < 0:
        raise TransportError(f"{name} must be >= 0, got {numeric!r}")
    return numeric


def _theta_value(theta: ThetaConfig, name: str, *, strict: bool = True) -> float:
    """Read one theta field as a number.

    A field carrying `value: None` is a DISCLOSED gap (T24 loads it deliberately), but it cannot be
    integrated against. The refusal names T20 so the reader learns where the value comes from
    rather than being told only that it is missing.
    """
    value = theta.value(name)
    if value is None:
        raise TransportError(
            f"theta field {name!r} has no value (assumed={theta.is_assumed(name)}). The solver cannot "
            f"integrate against a disclosed gap; a human supplies theta values via T20."
        )
    return _positive(value, f"theta[{name!r}]", strict=strict)


def _rates(theta: ThetaConfig, drug_params: dict, schedule: dict, alpha: float) -> dict:
    """Assemble the rate constants. Pure, so the integrator stays trivial to read."""
    area_mm2 = _theta_value(theta, "area_mm2")
    porosity = _theta_value(theta, "porosity")
    membrane_um = _theta_value(theta, "membrane_um")
    flow_ul_min = _theta_value(theta, "flow_ul_min")
    # Required and validated, deliberately NOT coupled -- see the module docstring. Strain may be
    # legitimately zero (an unstretched chip), so it is the one field allowed to be non-strict.
    _theta_value(theta, "strain_pct", strict=False)
    if not str(theta.value("coating") or "").strip():
        raise TransportError("theta field 'coating' must name a coating")

    if not 0 < porosity <= 1:
        raise TransportError(f"theta['porosity'] must lie in (0, 1], got {porosity!r}")

    p_app = _positive(drug_params["p_app_cm_s"], "drug_params['p_app_cm_s']")
    k_sink = _positive(drug_params["k_sink"], "drug_params['k_sink']", strict=False)
    f_u = _positive(drug_params["f_u"], "drug_params['f_u']")
    if not 0 < f_u <= 1:
        raise TransportError(f"drug_params['f_u'] must lie in (0, 1], got {f_u!r}")

    v_a = _positive(schedule["v_apical_ul"], "schedule['v_apical_ul']")
    v_b = _positive(schedule["v_basolateral_ul"], "schedule['v_basolateral_ul']")

    # Fick across the membrane. Thickness divides, porosity and area multiply -- geometry, not
    # biology. `alpha` is the single free scale the fit (T23) moves.
    permeability = alpha * p_app * (area_mm2 * porosity) / membrane_um
    return {
        "k_ab": permeability / v_a,  # apical -> basolateral, per apical volume
        "k_ba": permeability / v_b,  # the same flux seen by the basolateral volume
        "k_flow": flow_ul_min / v_a,  # perfusion clears the apical channel
        "k_sink": k_sink,
        "f_u": f_u,
    }


def _derivative(state: np.ndarray, dose_rate: float, r: dict) -> np.ndarray:
    c_a, c_b = state[0], state[1]
    gradient = c_a - c_b
    return np.array(
        [
            dose_rate - r["k_ab"] * gradient - r["k_flow"] * c_a,
            r["k_ba"] * gradient - r["k_sink"] * c_b,
        ],
        dtype=np.float64,
    )


def _dose_rate(time: float, dose_nmol: float, duration_min: float, v_a: float) -> float:
    """Constant-rate infusion over `duration_min`, zero after. A bolus is a small `duration_min`."""
    return (dose_nmol / duration_min) / v_a if time < duration_min else 0.0


def _integrate(
    t: np.ndarray, dose_nmol: float, duration_min: float, r: dict, v_a: float
) -> np.ndarray:
    """Fixed-step RK4. The single seam where a pinned `solve_ivp` would drop in."""
    state = np.zeros(2, dtype=np.float64)
    out = np.empty((t.size, 2), dtype=np.float64)
    out[0] = state
    for i in range(1, t.size):
        h = (t[i] - t[i - 1]) / _SUBSTEPS_PER_INTERVAL
        time = float(t[i - 1])
        for _ in range(_SUBSTEPS_PER_INTERVAL):
            k1 = _derivative(state, _dose_rate(time, dose_nmol, duration_min, v_a), r)
            k2 = _derivative(
                state + 0.5 * h * k1, _dose_rate(time + 0.5 * h, dose_nmol, duration_min, v_a), r
            )
            k3 = _derivative(
                state + 0.5 * h * k2, _dose_rate(time + 0.5 * h, dose_nmol, duration_min, v_a), r
            )
            k4 = _derivative(state + h * k3, _dose_rate(time + h, dose_nmol, duration_min, v_a), r)
            state = state + (h / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
            time += h
        out[i] = state
    return out


def transport_ode(
    theta: ThetaConfig,
    drug_params: dict,
    schedule: dict,
    t: np.ndarray,
    *,
    alpha: float = 1.0,
) -> np.ndarray:
    """Integrate the two-compartment core and return `C_free(t)` at the tissue face.

    Deterministic given `(theta, drug_params, schedule, t, alpha)`: no randomness, no adaptive
    stepping, no wall-clock, no dict-ordering dependence. Two calls return bit-identical arrays.

    `alpha` is keyword-only with a neutral default of 1.0 so that a caller who has NOT run the fit
    cannot pass an unfitted scale by positional accident; T23 supplies the fitted value explicitly.
    """
    if not isinstance(theta, ThetaConfig):
        raise TransportError(
            f"theta must be a validated ThetaConfig from load_theta, got {type(theta).__name__}. "
            f"The container is what guarantees every field is cited or disclosed."
        )
    for key in _REQUIRED_DRUG:
        if key not in drug_params:
            raise TransportError(f"drug_params is missing {key!r}")
    for key in _REQUIRED_SCHEDULE:
        if key not in schedule:
            raise TransportError(f"schedule is missing {key!r}")

    times = np.asarray(t, dtype=np.float64)
    if times.ndim != 1 or times.size < 2:
        raise TransportError("t must be a 1-D array of at least two times")
    if not np.all(np.diff(times) > 0):
        raise TransportError("t must be strictly increasing")
    if times[0] != 0.0:
        raise TransportError("t must start at 0.0 — the solve starts from an undosed chip")

    alpha_value = _positive(alpha, "alpha")
    rates = _rates(theta, drug_params, schedule, alpha_value)
    v_a = _positive(schedule["v_apical_ul"], "schedule['v_apical_ul']")
    dose_nmol = _positive(schedule["dose_nmol"], "schedule['dose_nmol']", strict=False)
    duration_min = _positive(schedule["duration_min"], "schedule['duration_min']")

    trajectory = _integrate(times, dose_nmol, duration_min, rates, v_a)
    c_free = rates["f_u"] * trajectory[:, 1]
    c_free.flags.writeable = False
    return c_free
