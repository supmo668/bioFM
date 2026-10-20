"""T24 — the θ container and its one refusal.

Done-when, per build-plan T24:
  1. loading a fixture with a field missing both citation and `assumed: true` RAISES;
  2. loading a complete fixture succeeds with every field accessible by name;
  3. loading is idempotent.

EVERY FIXTURE HERE IS BUILT IN `tmp_path`, NOT COMMITTED, and carries no biological claim. The
structural fixtures use `value: null` throughout, so nothing in this file is a number standing in
for a device parameter. Where a test must exercise the refusal — which by definition needs a value
present — it uses an obvious placeholder and says so, because the refusal is about PROVENANCE and
is indifferent to the magnitude.

Whether a *committed* fixture may carry synthetic θ values is a Global Constraint question raised
with the CTO and deliberately not answered here by choosing.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest
import yaml

from chipsim.transport.theta import (
    REQUIRED_FIELDS,
    ThetaConfig,
    ThetaConfigError,
    load_theta,
)


def _write(path: Path, theta: dict) -> Path:
    path.write_text(yaml.safe_dump({"theta": theta}), encoding="utf-8")
    return path


def _scaffold_entry(unit: str = "unit") -> dict:
    """A field in its STARTING state: no value, no citation, disclosed as assumed."""
    return {"value": None, "unit": unit, "citation": None, "assumed": True}


def _complete(**overrides) -> dict:
    theta = {name: _scaffold_entry() for name in sorted(REQUIRED_FIELDS)}
    theta.update(overrides)
    return theta


def test_t24_a_value_with_no_citation_and_not_assumed_RAISES(tmp_path):
    """Done-when 1 — the refusal this container exists for.

    A number with no citation that nobody marked `assumed: true` is a value no one has claimed
    responsibility for, about to be used as a prior. The placeholder magnitude is irrelevant: the
    refusal is about provenance.
    """
    theta = _complete(
        flow_ul_min={"value": 1, "unit": "uL/min", "citation": None, "assumed": False}
    )
    path = _write(tmp_path / "theta.yaml", theta)

    with pytest.raises(ThetaConfigError) as caught:
        load_theta(path)

    message = str(caught.value)
    assert "flow_ul_min" in message, "the refusal must name the offending field"
    assert "assumed" in message and "citation" in message, "and must say what would fix it"


def test_t24_a_cited_value_loads(tmp_path):
    """Cited is the sourced state — loads, and reports itself as sourced."""
    theta = _complete(
        flow_ul_min={
            "value": 1,
            "unit": "uL/min",
            "citation": "10.1000/placeholder",
            "assumed": False,
        }
    )
    config = load_theta(_write(tmp_path / "theta.yaml", theta))

    assert config["flow_ul_min"].is_sourced
    assert "flow_ul_min" not in config.assumed_fields


def test_t24_an_assumed_field_is_a_STATED_GAP_not_an_error(tmp_path):
    """`assumed: true` must LOAD. It is disclosure, the same posture T14's `unknown` carries —
    treating it as an error would push people toward inventing a citation."""
    config = load_theta(_write(tmp_path / "theta.yaml", _complete()))

    assert set(config.assumed_fields) == REQUIRED_FIELDS
    assert not any(f.is_sourced for f in config.fields)


def test_t24_every_field_is_accessible_by_name(tmp_path):
    """Done-when 2."""
    config = load_theta(_write(tmp_path / "theta.yaml", _complete()))

    for name in REQUIRED_FIELDS:
        assert config[name].name == name
    with pytest.raises(KeyError):
        config["not_a_theta_field"]


def test_t24_loading_is_idempotent(tmp_path):
    """Done-when 3 — two loads of one unchanged file agree in full.

    Asserted on the FIELDS rather than on object identity: identity would pass against a cache
    that never re-read the file, which is the opposite of what idempotence is claiming here.
    """
    path = _write(tmp_path / "theta.yaml", _complete())

    assert load_theta(path).fields == load_theta(path).fields


@pytest.mark.parametrize(
    "theta, because",
    [
        (
            {name: _scaffold_entry() for name in sorted(REQUIRED_FIELDS - {"coating"})},
            "a missing field is a prior the solver will silently reach for",
        ),
        (
            {
                **{name: _scaffold_entry() for name in sorted(REQUIRED_FIELDS)},
                "extra_param": _scaffold_entry(),
            },
            "an unexpected field is a parameter nobody sourced",
        ),
    ],
)
def test_t24_the_field_set_is_EQUALITY_not_containment(tmp_path, theta, because):
    """Both directions fail, and the message says which. A containment check passes the superset,
    which is the direction that admits an unsourced parameter."""
    with pytest.raises(ThetaConfigError) as caught:
        load_theta(_write(tmp_path / "theta.yaml", theta))
    assert "exactly" in str(caught.value), because


def test_t24_a_field_with_no_unit_RAISES(tmp_path):
    """A bare number with no unit is the failure the container exists to make impossible."""
    theta = _complete(porosity={"value": None, "unit": "", "citation": None, "assumed": True})

    with pytest.raises(ThetaConfigError, match="unit"):
        load_theta(_write(tmp_path / "theta.yaml", theta))


def test_t24_a_truthy_string_does_not_satisfy_assumed(tmp_path):
    """`assumed: "yes"` is truthy in Python and would silently satisfy a naive check, letting an
    uncited value through the one refusal this module has."""
    theta = _complete(strain_pct={"value": 1, "unit": "%", "citation": None, "assumed": "yes"})

    with pytest.raises(ThetaConfigError, match="real boolean"):
        load_theta(_write(tmp_path / "theta.yaml", theta))


def test_t24_an_absent_file_RAISES_rather_than_yielding_an_empty_theta(tmp_path):
    """`configs/theta_priors.yaml` does not exist until a human runs T20. An absent file must not
    degrade into an empty θ that a fit routine would happily consume."""
    with pytest.raises(ThetaConfigError, match="does not exist"):
        load_theta(tmp_path / "never_written.yaml")


def test_t24_has_NO_default_path():
    """The validator must not reach for `configs/theta_priors.yaml` on its own.

    S6 asserts that path's ABSENCE as the mechanical form of Global Constraint 1 — a default here
    would put this module's fingerprints on it and turn "the human hasn't filled it in" into a
    load error at a distance.
    """
    import inspect

    signature = inspect.signature(load_theta)
    assert signature.parameters["path"].default is inspect.Parameter.empty, (
        "load_theta must require an explicit path"
    )

    source = inspect.getsource(load_theta)
    assert "configs/theta_priors.yaml" not in source.replace("`configs/theta_priors.yaml`", ""), (
        "load_theta must not name the human-owned path as a value"
    )


def test_t24_the_container_is_frozen(tmp_path):
    """A fit routine that can mutate its own priors mid-run produces a result no replay can
    reproduce — the determinism requirement A&D §2B states and T25 must demonstrate."""
    config = load_theta(_write(tmp_path / "theta.yaml", _complete()))

    with pytest.raises(FrozenInstanceError):
        config.fields = ()  # type: ignore[misc]
    assert isinstance(config, ThetaConfig)
