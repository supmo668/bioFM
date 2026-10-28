"""The sandbox: readiness, the interpretability contract, and the aviary environment.

The property under test throughout is the one the principal's 2026-10-14 instruction names:
a result must carry its interpretation, and a simulator with no admissible inputs must say so
precisely rather than produce a plausible number. So most of these tests assert a REFUSAL, and
the most important one asserts that the refusal names the artifacts and their owners.

`fhaviary` is an optional dependency, so the environment tests skip without it while the
readiness and contract tests always run.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from chipsim.sandbox import readiness
from chipsim.sandbox.interpretability import (
    Abstention,
    CoverageBasis,
    ParameterProvenance,
    Prediction,
    SupportingEvidence,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# --------------------------------------------------------------------------- #
# readiness — the validation barrier, stated as artifacts
# --------------------------------------------------------------------------- #


def test_the_live_project_is_not_ready_and_says_which_inputs_block_it():
    """The designed state today: human-owned inputs are absent, so nothing may be predicted."""
    report = readiness.assess(PROJECT_ROOT)
    assert not report.can_predict
    blocking = {s.key for s in report.blocking_absent}
    assert {"theta", "transport_prior", "reference_compounds"} <= blocking


def test_the_refusal_names_the_artifact_its_owner_and_what_it_blocks():
    """A refusal a reader cannot act on is just an error message."""
    text = readiness.assess(PROJECT_ROOT).refusal()
    assert "configs/theta_priors.yaml" in text
    assert "owner: principal" in text
    assert "T20" in text and "M0b" in text
    assert "Blocks:" in text


def test_a_present_but_invalid_theta_is_reported_as_refused_not_as_absent(tmp_path):
    """Present-and-rejected and absent are different states; blurring them hides a bad file."""
    (tmp_path / "configs").mkdir()
    (tmp_path / "configs" / "theta_priors.yaml").write_text(
        (PROJECT_ROOT / "tests" / "fixtures" / "theta_priors_unsourced.yaml").read_text()
    )
    status = next(s for s in readiness.assess(tmp_path).statuses if s.key == "theta")
    assert status.present and status.accepted is False
    assert "refused" in status.detail


def test_a_valid_theta_is_accepted_and_its_assumed_fields_are_reported(tmp_path):
    (tmp_path / "configs").mkdir()
    (tmp_path / "configs" / "theta_priors.yaml").write_text(
        (PROJECT_ROOT / "tests" / "fixtures" / "theta_priors_complete.yaml").read_text()
    )
    status = next(s for s in readiness.assess(tmp_path).statuses if s.key == "theta")
    assert status.accepted is True
    assert "assumed" in status.detail


def test_presence_without_a_validator_is_not_reported_as_accepted(tmp_path):
    """`accepted is None` for an unvalidated artifact: "the file is there" is a weaker claim."""
    (tmp_path / "configs").mkdir()
    (tmp_path / "configs" / "pgp_adjudication.csv").write_text("canonical_inchikey\n")
    status = next(s for s in readiness.assess(tmp_path).statuses if s.key == "adjudicated_labels")
    assert status.present and status.accepted is None
    assert "unverified" in status.detail


def test_readiness_is_not_cached_between_calls(tmp_path):
    """A sandbox that remembered it was ready would keep answering after a withdrawal."""
    (tmp_path / "configs").mkdir()
    target = tmp_path / "configs" / "theta_priors.yaml"
    target.write_text(
        (PROJECT_ROOT / "tests" / "fixtures" / "theta_priors_complete.yaml").read_text()
    )
    first = next(s for s in readiness.assess(tmp_path).statuses if s.key == "theta")
    target.unlink()
    second = next(s for s in readiness.assess(tmp_path).statuses if s.key == "theta")
    assert first.accepted is True and second.accepted is None


def test_refusal_raises_on_a_ready_report():
    """Calling refusal() on a ready sandbox is a caller bug, not an empty string."""
    report = readiness.ReadinessReport(statuses=(), project_root=Path("."))
    assert report.can_predict
    with pytest.raises(ValueError, match="ready sandbox"):
        report.refusal()


# --------------------------------------------------------------------------- #
# the interpretability contract
# --------------------------------------------------------------------------- #


def _basis(**kw):
    base = {
        "nominal": 0.9,
        "calibration_n": 20,
        "subgroup": "P-gp substrate",
        "method": "Mondrian conformal",
        "group_conditional": True,
    }
    base.update(kw)
    return CoverageBasis(**base)


def _param(**kw):
    base = {"name": "membrane_um", "provenance": "cited", "citation": "10.0000/fixture"}
    base.update(kw)
    return ParameterProvenance(**base)


def test_a_cited_parameter_without_a_citation_cannot_be_constructed():
    """Reporting provenance is pointless if the reader cannot resolve it."""
    with pytest.raises(ValueError, match="no citation"):
        ParameterProvenance(name="membrane_um", provenance="cited")


def test_an_assumed_parameter_needs_no_citation():
    p = ParameterProvenance(name="porosity", provenance="assumed", note="no lattice published")
    assert p.citation is None


def test_an_interval_with_no_calibration_points_is_refused():
    with pytest.raises(ValueError, match="not an interval"):
        _basis(calibration_n=0)


def test_the_coverage_caveat_states_n_and_whether_the_guarantee_is_conditional():
    assert "20 calibration point(s)" in _basis().caveat
    assert "conditional on P-gp substrate" in _basis().caveat
    assert "MARGINAL" in _basis(group_conditional=False).caveat


def test_a_prediction_with_no_declared_parameters_is_refused():
    with pytest.raises(ValueError, match="no declared parameters"):
        Prediction(
            quantity="exposure",
            unit="uM",
            point=1.0,
            interval_low=0.5,
            interval_high=2.0,
            coverage=_basis(),
            parameters=(),
            evidence=(),
            model_version="test",
        )


def test_a_point_outside_its_own_interval_is_refused():
    with pytest.raises(ValueError, match="outside its own interval"):
        Prediction(
            quantity="exposure",
            unit="uM",
            point=9.0,
            interval_low=0.5,
            interval_high=2.0,
            coverage=_basis(),
            parameters=(_param(),),
            evidence=(),
            model_version="test",
        )


def test_the_wire_form_materialises_the_caveat_and_the_assumed_list():
    """A client that forgot to call `caveat` would otherwise publish a bare interval."""
    pred = Prediction(
        quantity="exposure",
        unit="uM",
        point=1.0,
        interval_low=0.5,
        interval_high=2.0,
        coverage=_basis(),
        parameters=(_param(), _param(name="porosity", provenance="assumed", citation=None)),
        evidence=(SupportingEvidence("rec-1", "FIXTURE", "same P-gp group"),),
        model_version="test",
        reading="FIXTURE: carrier saturation is expected to dominate at this dose.",
    )
    wire = pred.as_dict()
    assert wire["coverage"]["caveat"].startswith("90% nominal coverage")
    assert wire["assumed_parameters"] == ["porosity"]
    assert "decision object" in wire["interpretability_contract"]


def test_an_abstention_carries_the_remedy_not_just_the_refusal():
    a = Abstention(reason="out of domain", what_would_change_it="a record in this subgroup")
    assert a.as_dict()["kind"] == "abstention"
    assert a.as_dict()["what_would_change_it"]


# --------------------------------------------------------------------------- #
# the aviary environment
# --------------------------------------------------------------------------- #

aviary = pytest.importorskip("aviary.core", reason="fhaviary is an optional dependency")


def _env(root=PROJECT_ROOT, **kw):
    from chipsim.sandbox.env import LungMembraneEnv

    return LungMembraneEnv("FIXTURE objective", project_root=root, **kw)


def _call(name, **arguments):
    return aviary.ToolRequestMessage(
        tool_calls=[{"id": "c1", "function": {"name": name, "arguments": arguments}}]
    )


@pytest.mark.asyncio
async def test_reset_offers_tools_built_from_their_docstrings():
    env = _env()
    obs, tools = await env.reset()
    names = {t.info.name for t in tools}
    assert names == {
        "readiness_report",
        "parameter_provenance",
        "predict_exposure",
        "declared_contract",
    }
    assert "NOT ready" in obs[0].content


@pytest.mark.asyncio
async def test_predict_exposure_abstains_with_structure_rather_than_returning_a_number():
    """The central behaviour: no number exists, so none is produced, and the reason is machine
    readable rather than prose a caller must parse."""
    env = _env()
    await env.reset()
    responses, reward, _done, _ = await env.step(
        _call("predict_exposure", compound_inchikey="FIXTUREKEY", dose_umol_per_l=1.0)
    )
    payload = json.loads(responses[0].content)
    assert payload["kind"] == "abstention"
    assert "T20" in payload["what_would_change_it"]
    assert payload["model_version"]
    # Nothing numeric was invented for the requested input.
    assert "point" not in payload and "interval_low" not in payload
    assert reward == 0.0


@pytest.mark.asyncio
async def test_reward_is_always_zero_and_never_fabricated():
    env = _env()
    await env.reset()
    _, reward, _, _ = await env.step(_call("declared_contract"))
    assert reward == 0.0


@pytest.mark.asyncio
async def test_an_unknown_tool_is_answered_not_crashed():
    env = _env()
    await env.reset()
    responses, _, _, _ = await env.step(_call("fabricate_number"))
    assert responses[0].content == "no such tool"


@pytest.mark.asyncio
async def test_a_non_tool_message_gets_the_standard_response():
    env = _env()
    await env.reset()
    out = await env.step(aviary.Message(content="let me just estimate it myself"))
    assert out == env.default_no_tool_calls_response


@pytest.mark.asyncio
async def test_the_frame_separates_refusals_from_results():
    """A rollout that spent every round being refused is a different outcome from one that
    produced results; transcript length alone would blur them."""
    env = _env()
    await env.reset()
    await env.step(_call("predict_exposure", compound_inchikey="K", dose_umol_per_l=1.0))
    await env.step(_call("readiness_report"))
    await env.step(_call("declared_contract"))
    frame = env.export_frame()
    assert frame.state["tool_calls"] == 3
    assert frame.state["readiness_refusals"] == 2
    assert frame.info["env_version"]


@pytest.mark.asyncio
async def test_the_rollout_truncates_at_max_rounds():
    env = _env(max_rounds=2)
    await env.reset()
    _, _, done1, trunc1 = await env.step(_call("declared_contract"))
    _, _, done2, trunc2 = await env.step(_call("declared_contract"))
    assert not done1 and not trunc1
    assert done2 and trunc2


@pytest.mark.asyncio
async def test_parameter_provenance_reports_the_absent_file_rather_than_defaults():
    env = _env()
    await env.reset()
    responses, _, _, _ = await env.step(_call("parameter_provenance"))
    text = responses[0].content
    assert "absent" in text
    assert "flow_ul_min" in text and "porosity" in text


@pytest.mark.asyncio
async def test_a_ready_sandbox_refuses_to_fake_a_prediction(tmp_path, monkeypatch):
    """With inputs satisfied, the environment must NOT invent a result: the surrogate is the
    next thing to build, and a shaped placeholder would be indistinguishable from a real
    number in every downstream artifact."""
    from chipsim.sandbox import readiness as rd

    monkeypatch.setattr(
        rd, "REQUIRED_ARTIFACTS", ()
    )  # no artifacts required -> the report is ready
    env = _env(root=tmp_path)
    await env.reset()
    responses, _, _, _ = await env.step(
        _call("predict_exposure", compound_inchikey="K", dose_umol_per_l=1.0)
    )
    assert "not implemented" in responses[0].content
    assert "do not return" in responses[0].content.lower()
