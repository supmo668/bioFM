"""T22 — the two-compartment transport core.

Done-when, per build-plan T22:
  1. a smoke fixture integrates to a fixed point without raising;
  2. two calls with identical inputs return bit-identical arrays (A&D §2B determinism);
  3. increasing schedule dose strictly increases cumulative C_free AUC.

ON THETA VALUES IN THIS FILE. Every theta here is built in `tmp_path` and NONE is committed. The
numbers are transparently synthetic -- unit-scale round figures chosen so the system is well
conditioned, not device measurements, and the module docstring for `_synthetic_theta` says so at
the point of use. That is deliberate: T22's done-condition (1) says "literature-typical theta",
and whether ANY fixture may carry plausible device values is Finding B, open with the CTO and not
answered here by choosing. All three done-conditions are about STRUCTURE (does it settle, is it
deterministic, does dose move AUC the right way) and none needs literature-accurate magnitudes,
so nothing here depends on B's ruling. The word "literature-typical" in clause (1) is the one
part of T22 that remains unmet, and it is unmet on purpose.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import yaml

from chipsim.transport.ode import TransportError, transport_ode
from chipsim.transport.theta import ThetaConfig, load_theta_priors

#: Transparently synthetic, unit-scale. NOT device parameters, NOT literature values, and not
#: committed anywhere -- see the module docstring. Chosen only so the linear system is well
#: conditioned over the integration window.
_SYNTHETIC = {
    "flow_ul_min": (1.0, "uL/min"),
    "membrane_um": (10.0, "um"),
    "porosity": (0.5, "fraction"),
    "strain_pct": (5.0, "percent"),
    "area_mm2": (1.0, "mm^2"),
    "coating": ("synthetic-placeholder", "categorical"),
}

_DRUG = {"p_app_cm_s": 1.0, "f_u": 0.5, "k_sink": 0.1}
_SCHEDULE = {
    "dose_nmol": 10.0,
    "duration_min": 1000.0,  # longer than the default window, so infusion is effectively constant
    "v_apical_ul": 100.0,
    "v_basolateral_ul": 100.0,
}

#: For the steady-state test only: infusion must outlast the LONG window, or the "fixed point"
#: would really be the post-infusion decay toward zero.
_LONG_SCHEDULE = {**_SCHEDULE, "duration_min": 100_000.0}


def _theta(tmp_path: Path, **overrides):
    body = {}
    for name, (value, unit) in _SYNTHETIC.items():
        body[name] = {
            "value": overrides.get(name, value),
            "unit": unit,
            "citation": None,
            "assumed": True,  # a STATED gap: these are placeholders, and they say so
        }
    tmp_path.mkdir(parents=True, exist_ok=True)
    path = tmp_path / "theta.yaml"
    path.write_text(yaml.safe_dump({"theta": body}), encoding="utf-8")
    return load_theta_priors(path)


def _run(theta, *, schedule=None, drug=None, t=None):
    return transport_ode(
        theta,
        dict(drug or _DRUG),
        dict(schedule or _SCHEDULE),
        np.linspace(0.0, 120.0, 61) if t is None else t,
    )


def _auc(curve, t=None):
    times = np.linspace(0.0, 120.0, 61) if t is None else t
    return float(np.trapezoid(curve, times))


def _analytic_steady_state() -> float:
    """The fixed point of the two-compartment system under constant infusion, derived BY HAND
    from the equations rather than by calling the module.

    Setting both derivatives to zero:
        0 = R - k_ab(Ca - Cb) - k_flow*Ca
        0 = k_ba(Ca - Cb) - k_sink*Cb
    The second gives Ca = Cb(1 + k_sink/k_ba); substituting into the first and solving for Cb:
        Cb* = R / [ k_ab*k_sink/k_ba + k_flow*(1 + k_sink/k_ba) ]
    and C_free* = f_u * Cb*.

    This is an INDEPENDENT oracle. Asserting only that the curve stopped moving would pass for a
    solver that converged confidently to the wrong number -- flatness is not correctness.
    """
    permeability = (
        1.0
        * _DRUG["p_app_cm_s"]
        * (_SYNTHETIC["area_mm2"][0] * _SYNTHETIC["porosity"][0])
        / _SYNTHETIC["membrane_um"][0]
    )
    v_a, v_b = _SCHEDULE["v_apical_ul"], _SCHEDULE["v_basolateral_ul"]
    k_ab, k_ba = permeability / v_a, permeability / v_b
    k_flow = _SYNTHETIC["flow_ul_min"][0] / v_a
    k_sink = _DRUG["k_sink"]
    rate = (_LONG_SCHEDULE["dose_nmol"] / _LONG_SCHEDULE["duration_min"]) / v_a

    c_b = rate / (k_ab * k_sink / k_ba + k_flow * (1.0 + k_sink / k_ba))
    return _DRUG["f_u"] * c_b


def test_t22_integrates_to_a_fixed_point(tmp_path):
    """Done-when 1, asserted against an independently derived fixed point.

    The slowest mode here has a time constant of ~1/k_flow = 100 min, so the window runs to 3000
    (~30 tau). An earlier version of this test stopped at 600 and asserted only that the curve had
    flattened; it failed because at 6 tau the system is still visibly settling. Extending the
    window fixes that, but the real repair was replacing "stopped moving" with "arrived at the
    right place" -- the first is satisfied by any solver that converges, including a wrong one.
    """
    t = np.linspace(0.0, 3000.0, 601)
    curve = _run(_theta(tmp_path), schedule=_LONG_SCHEDULE, t=t)

    assert np.all(np.isfinite(curve)), "the solve produced non-finite concentrations"
    assert np.all(curve >= 0.0), "concentration went negative"
    assert np.all(np.diff(curve) >= 0.0), "C_free is not monotone under constant infusion"

    assert curve[-1] == pytest.approx(_analytic_steady_state(), rel=1e-6), (
        "the solve settled somewhere other than the algebraic fixed point"
    )


def test_t22_two_identical_calls_are_BIT_identical(tmp_path):
    """Done-when 2 (A&D §2B). Asserted with array_equal, NOT allclose: a tolerance would pass
    against exactly the nondeterminism this condition exists to forbid."""
    theta = _theta(tmp_path)
    first, second = _run(theta), _run(theta)

    assert np.array_equal(first, second), "two identical calls disagreed"
    assert first.dtype == second.dtype == np.float64


def test_t22_determinism_survives_a_reloaded_theta(tmp_path):
    """The stronger form of done-when 2: equality must not depend on reusing the SAME object.

    Passing the identical instance twice would also pass against a solver that cached on `id()`,
    so the second run reloads theta from the same file into a fresh container.
    """
    assert np.array_equal(_run(_theta(tmp_path / "a")), _run(_theta(tmp_path / "b")))


@pytest.mark.parametrize("bigger", [10.5, 20.0, 100.0])
def test_t22_more_dose_strictly_increases_auc(tmp_path, bigger):
    """Done-when 3 — the sanity floor T26 exercises for real."""
    theta = _theta(tmp_path)
    base = _auc(_run(theta))
    raised = _auc(_run(theta, schedule={**_SCHEDULE, "dose_nmol": bigger}))

    assert raised > base, f"dose {bigger} did not raise AUC above dose {_SCHEDULE['dose_nmol']}"


def test_t22_zero_dose_gives_no_exposure(tmp_path):
    """The floor under done-when 3. An undosed chip must deliver nothing; a solver that leaked a
    baseline would still pass the monotonicity test above."""
    curve = _run(_theta(tmp_path), schedule={**_SCHEDULE, "dose_nmol": 0.0})

    assert np.array_equal(curve, np.zeros_like(curve))


def test_t22_higher_flow_lowers_exposure(tmp_path):
    """A&D §2 objective T7's first sign: higher flow -> lower cumulative flux. Not a T22
    done-condition, asserted here because it is the cheapest possible check that theta's flow
    field is wired to the equations AT ALL, and a sign error would otherwise reach T26."""
    slow = _auc(_run(_theta(tmp_path / "slow", flow_ul_min=1.0)))
    fast = _auc(_run(_theta(tmp_path / "fast", flow_ul_min=50.0)))

    assert fast < slow, "raising perfusion did not reduce exposure"


def test_t22_thicker_membrane_lowers_exposure(tmp_path):
    """T7's second sign: thicker membrane -> lower flux."""
    thin = _auc(_run(_theta(tmp_path / "thin", membrane_um=10.0)))
    thick = _auc(_run(_theta(tmp_path / "thick", membrane_um=100.0)))

    assert thick < thin, "thickening the membrane did not reduce exposure"


def test_t22_higher_f_u_delivers_more_free_drug(tmp_path):
    """T7's third sign: higher f_u -> more delivered FREE drug."""
    theta = _theta(tmp_path)
    low = _auc(_run(theta, drug={**_DRUG, "f_u": 0.1}))
    high = _auc(_run(theta, drug={**_DRUG, "f_u": 0.9}))

    assert high > low, "raising the free fraction did not raise free exposure"


def test_t22_strain_and_coating_are_carried_but_NOT_coupled(tmp_path):
    """THE DELIBERATE ABSENCE, PINNED.

    No citation exists in this repo for how strain or coating change permeability, so wiring a
    coefficient would mean inventing the number that matters most and hiding it in code — where
    T24's validator, which exists precisely to refuse unsourced values, could never see it.

    If someone later couples these, this test fails and forces the question into the open rather
    than letting the coupling arrive silently. It is not asserting that strain does not matter; it
    is asserting that THIS MODULE does not claim to know how much.
    """
    quiet = _run(_theta(tmp_path / "q", strain_pct=0.0, coating="coating-a"))
    strained = _run(_theta(tmp_path / "s", strain_pct=30.0, coating="coating-b"))

    assert np.array_equal(quiet, strained), (
        "strain or coating changed the result — a coupling was added without a citation, or "
        "this test needs updating alongside the citation that justifies it"
    )


def test_t22_a_disclosed_gap_cannot_be_integrated():
    """A theta field with no value must not silently integrate as zero — the failure would be a
    plausible-looking curve built on a parameter nobody supplied.

    PORTED: Stage 1's loader admitted `assumed: true` with `value: null` as a stated gap, so this
    test built one through it. HEAD's loader refuses an empty value outright ("An absent value is
    incomplete, not a default"), so that door is closed and the gap is unreachable via
    `load_theta_priors`. The refusal in `ode.py` is still a standing constraint, and it is still
    reachable: `ThetaConfig(entries=..., source_path=...)` constructs one directly, which is the
    same bypass `require_sourced_theta` is called twice for. That is the door exercised here.
    """
    theta = ThetaConfig(
        entries={
            name: {
                "value": None if name == "membrane_um" else value,
                "unit": unit,
                "citation": None,
                "assumed": True,
            }
            for name, (value, unit) in _SYNTHETIC.items()
        },
        source_path=Path("constructed-directly.yaml"),
    )

    with pytest.raises(TransportError, match="no value"):
        _run(theta)


def test_t22_refuses_a_raw_dict_theta(tmp_path):
    """The ThetaConfig type IS the guarantee that every field was validated. Accepting a bare dict
    would route around T24 entirely."""
    with pytest.raises(TransportError, match="ThetaConfig"):
        transport_ode(
            {"flow_ul_min": 1.0},  # type: ignore[arg-type]
            dict(_DRUG),
            dict(_SCHEDULE),
            np.linspace(0.0, 10.0, 11),
        )


@pytest.mark.parametrize(
    "missing", ["dose_nmol", "duration_min", "v_apical_ul", "v_basolateral_ul"]
)
def test_t22_schedule_keys_have_no_defaults(tmp_path, missing):
    """A defaulted volume is an invented number. Same posture as T24's absent-file refusal."""
    schedule = {k: v for k, v in _SCHEDULE.items() if k != missing}

    with pytest.raises(TransportError, match=missing):
        _run(_theta(tmp_path), schedule=schedule)


def test_t22_the_returned_curve_is_read_only(tmp_path):
    """A caller that mutates the returned exposure in place makes the determinism guarantee
    unverifiable for everyone downstream of it."""
    curve = _run(_theta(tmp_path))

    with pytest.raises(ValueError):
        curve[0] = 1.0
