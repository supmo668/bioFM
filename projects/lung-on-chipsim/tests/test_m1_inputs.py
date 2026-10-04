"""M1 human-input contracts — build-plan S13, S14, T21, T24, T28.

**T20, T21 and T28 are human-owned and ABSENT.** Nothing here fabricates a θ value, a
transport prior or a published transport measurement: every assertion runs against
tests/fixtures/, whose contents are FIXTURE-prefixed sentinels with no physical meaning.

Each test below names the property it protects rather than the line of code that
happens to implement it. That is the Stage 1 closure's mechanism applied in advance: a
fix verified against the thing that was changed, instead of against the property the
claim names, is how nine defects arrived and six of them arrived through repair.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from chipsim.harmonize.reference_compounds import (
    MAX_REFERENCE_ENTRIES,
    MIN_REFERENCE_ENTRIES,
    REFERENCE_COLUMNS,
    ReferenceCompoundError,
    load_reference_compounds,
)
from chipsim.transport import prior as prior_mod
from chipsim.transport import theta as theta_mod
from chipsim.transport.prior import (
    PRIOR_NAMES,
    TransportPrior,
    TransportPriorError,
    TransportPriorSourceError,
)
from chipsim.transport.theta import (
    FIELD_NAMES,
    S6_FORBIDDEN_RELPATHS,
    ThetaConfig,
    ThetaError,
    ThetaSourceError,
    ThetaTemplateError,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = PROJECT_ROOT / "tests" / "fixtures"


# --------------------------------------------------------------------------- #
# T24 · θ container and validator
# --------------------------------------------------------------------------- #


def test_t24_loads_a_complete_fixture_with_every_field_accessible_by_name():
    cfg = ThetaConfig.load(FIXTURES / "theta_priors_complete.yaml")
    assert tuple(cfg.entries) == FIELD_NAMES
    for name in FIELD_NAMES:
        assert cfg.value(name) is not None
        assert cfg.unit(name) == theta_mod._BY_NAME[name].unit


def test_t24_load_is_idempotent():
    """Two loads of one file agree. The done-condition says idempotent, so assert it."""
    path = FIXTURES / "theta_priors_complete.yaml"
    first, second = ThetaConfig.load(path), ThetaConfig.load(path)
    assert {k: dict(v) for k, v in first.entries.items()} == {
        k: dict(v) for k, v in second.entries.items()
    }


def test_t24_raises_when_a_field_has_neither_citation_nor_assumed():
    """T24's central refusal, and the only reason this validator exists."""
    with pytest.raises(ThetaSourceError, match="strain_pct"):
        ThetaConfig.load(FIXTURES / "theta_priors_unsourced.yaml")


def test_t24_rejects_a_unit_the_schema_does_not_declare():
    with pytest.raises(ThetaError, match="declares unit 'mm'"):
        ThetaConfig.load(FIXTURES / "theta_priors_wrong_unit.yaml")


def test_t24_rejects_an_empty_value_even_when_flagged_assumed():
    """`assumed` states where a number came from; it does not excuse its absence."""
    with pytest.raises(ThetaError, match="empty `value`"):
        ThetaConfig.load(FIXTURES / "theta_priors_empty_value.yaml")


def test_t24_rejects_a_missing_field():
    with pytest.raises(ThetaError, match="missing θ field"):
        ThetaConfig.load(FIXTURES / "theta_priors_missing_field.yaml")


def test_t24_rejects_a_misspelled_key_rather_than_ignoring_it():
    """A permissive loader drops `citaton:` and reads the field as uncited-but-fine."""
    with pytest.raises(ThetaError, match="unknown key"):
        ThetaConfig.load(FIXTURES / "theta_priors_misspelled_key.yaml")


def test_t24_rejects_a_quoted_number():
    doc = yaml.safe_load((FIXTURES / "theta_priors_complete.yaml").read_text())
    doc["theta"]["membrane_um"]["value"] = "1.0"
    tmp = FIXTURES.parent / "_tmp_theta_quoted.yaml"
    tmp.write_text(yaml.safe_dump(doc))
    try:
        with pytest.raises(ThetaError, match="expects a number"):
            ThetaConfig.load(tmp)
    finally:
        tmp.unlink()


def test_t24_rejects_a_truthy_string_as_the_assumed_flag(tmp_path):
    """`assumed: "yes"` is truthy in Python and would silence the guard everywhere."""
    doc = yaml.safe_load((FIXTURES / "theta_priors_unsourced.yaml").read_text())
    doc["theta"]["strain_pct"]["assumed"] = "yes"
    path = tmp_path / "theta.yaml"
    path.write_text(yaml.safe_dump(doc))
    with pytest.raises(ThetaError, match="must be true or false"):
        ThetaConfig.load(path)


def test_t24_counts_cited_and_assumed_fields_without_asserting_a_ratio():
    """Two of six assumed is a stated limitation, not a failure. Report, never gate."""
    cfg = ThetaConfig.load(FIXTURES / "theta_priors_complete.yaml")
    assert cfg.cited_count + cfg.assumed_count == len(FIELD_NAMES)
    assert set(cfg.assumed_fields()) <= set(FIELD_NAMES)


def test_t24_config_is_frozen_and_its_entries_are_read_only():
    """The fit must not be able to adjust the prior it was handed."""
    cfg = ThetaConfig.load(FIXTURES / "theta_priors_complete.yaml")
    with pytest.raises(TypeError):
        cfg.entries["membrane_um"]["value"] = 999  # type: ignore[index]
    assert cfg.value("membrane_um") != 999


def test_the_guard_the_decision_ledger_cites_exists_under_that_name():
    """The HACP ledger and the Stage 1 paper both cite `_require_sourced_theta`.

    A rule cited by a published document and absent from the code is the pinning defect
    the Stage 1 closure is about, so the name is asserted here, not assumed.
    """
    assert callable(theta_mod._require_sourced_theta)
    assert theta_mod.require_sourced_theta is theta_mod._require_sourced_theta


# --------------------------------------------------------------------------- #
# S13 · θ scaffold
# --------------------------------------------------------------------------- #


def test_s13_scaffold_parses_with_exactly_the_six_fields_empty_and_assumed():
    doc = yaml.safe_load((PROJECT_ROOT / theta_mod.SCAFFOLD_RELPATH).read_text())
    assert tuple(doc["theta"]) == FIELD_NAMES
    for name, entry in doc["theta"].items():
        assert entry["value"] is None, f"{name} ships a value"
        assert entry["citation"] is None, f"{name} ships a citation"
        assert entry["assumed"] is True, f"{name} does not start assumed"


@pytest.mark.parametrize("relpath", [p.as_posix() for p in S6_FORBIDDEN_RELPATHS])
def test_s13_reasserts_the_s6_invariant(relpath):
    """Asserted at the task that could cause the regression, not only at S6's own test."""
    assert not (PROJECT_ROOT / relpath).exists(), (
        f"{relpath} exists — it is human-owned and no agent may create it"
    )


def test_s13_writer_refuses_the_path_s6_guards(tmp_path):
    target = tmp_path / "configs" / "theta_priors.yaml"
    with pytest.raises(ThetaTemplateError, match="human-owned"):
        theta_mod.write_scaffold(target)
    assert not target.exists()


def test_s13_writer_refuses_to_blank_a_filled_file(tmp_path):
    """Defect 22's failure mode: a re-emit that destroys human work with no error."""
    target = tmp_path / "theta_priors.yaml"
    target.write_text((FIXTURES / "theta_priors_complete.yaml").read_text())
    before = target.read_text()
    with pytest.raises(ThetaTemplateError, match="already carries filled"):
        theta_mod.write_scaffold(target)
    assert target.read_text() == before


def test_s13_writer_overwrites_an_untouched_scaffold():
    """The legitimate case: regenerating a template nobody has started."""
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        target = Path(d) / "scaffold.yaml"
        theta_mod.write_scaffold(target)
        theta_mod.write_scaffold(target)  # no force needed: nothing was filled
        assert yaml.safe_load(target.read_text())["theta"]["porosity"]["value"] is None


def test_s13_scaffold_carries_no_number_at_all():
    """An agent-written number in a θ file is prohibition (1). Check the bytes."""
    text = theta_mod.scaffold_text()
    body = "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("#"))
    doc = yaml.safe_load(body)

    def numeric_leaves(node):
        if isinstance(node, dict):
            for v in node.values():
                yield from numeric_leaves(v)
        elif isinstance(node, list):
            for v in node:
                yield from numeric_leaves(v)
        elif isinstance(node, (int, float)) and not isinstance(node, bool):
            yield node

    assert list(numeric_leaves(doc)) == []


# --------------------------------------------------------------------------- #
# T28 · transport prior
# --------------------------------------------------------------------------- #


def test_t28_loads_a_complete_fixture():
    p = TransportPrior.load(FIXTURES / "transport_prior_complete.yaml")
    assert tuple(p.entries) == PRIOR_NAMES
    assert p.is_assumed("k_sink_prior") and not p.is_assumed("alpha_prior")


def test_t28_raises_when_an_entry_is_neither_cited_nor_assumed():
    with pytest.raises(TransportPriorSourceError, match="k_sink_prior"):
        TransportPrior.load(FIXTURES / "transport_prior_unsourced.yaml")


def test_t28_rejects_a_zero_width_prior():
    """sigma_log = 0 fixes the parameter instead of prioring it."""
    with pytest.raises(TransportPriorError, match="must be positive"):
        TransportPrior.load(FIXTURES / "transport_prior_zero_width.yaml")


def test_t28_rejects_a_file_carrying_only_one_prior(tmp_path):
    doc = yaml.safe_load((FIXTURES / "transport_prior_complete.yaml").read_text())
    del doc["k_sink_prior"]
    path = tmp_path / "prior.yaml"
    path.write_text(yaml.safe_dump(doc))
    with pytest.raises(TransportPriorError, match="missing"):
        TransportPrior.load(path)


def test_s14_scaffold_parses_with_exactly_two_entries_both_assumed():
    doc = yaml.safe_load((PROJECT_ROOT / prior_mod.SCAFFOLD_RELPATH).read_text())
    assert tuple(doc) == PRIOR_NAMES
    for name, entry in doc.items():
        assert entry["mean_log"] is None and entry["sigma_log"] is None, name
        assert entry["assumed"] is True, name


# --------------------------------------------------------------------------- #
# T21 · M1 reference compounds
# --------------------------------------------------------------------------- #


def test_t21_accepts_the_happy_fixture():
    frame = load_reference_compounds(FIXTURES / "m1_reference_compounds.yaml")
    assert MIN_REFERENCE_ENTRIES <= len(frame) <= MAX_REFERENCE_ENTRIES
    assert list(frame.columns) == list(REFERENCE_COLUMNS)


def test_t21_rejects_too_few_entries():
    with pytest.raises(ReferenceCompoundError, match="T21 requires"):
        load_reference_compounds(FIXTURES / "m1_reference_compounds_too_few.yaml")


def test_t21_rejects_a_duplicate_key():
    with pytest.raises(ReferenceCompoundError, match="repeats canonical_inchikey"):
        load_reference_compounds(FIXTURES / "m1_reference_compounds_duplicate_key.yaml")


def test_t21_rejects_an_empty_evidence_doi():
    with pytest.raises(ReferenceCompoundError, match="empty `evidence_doi`"):
        load_reference_compounds(FIXTURES / "m1_reference_compounds_missing_doi.yaml")


def test_t21_does_not_require_roster_membership_by_default():
    """The plan's scope note: T21 is an INDEPENDENT yardstick, not a roster subset.

    Requiring membership would quietly make the M1 gate check the model against a
    subset of the thing being tested.
    """
    frame = load_reference_compounds(FIXTURES / "m1_reference_compounds.yaml", roster_keys=set())
    assert frame["in_roster"].eq(False).all()


def test_t21_enforces_roster_membership_only_when_asked():
    with pytest.raises(ReferenceCompoundError, match="outside T18's roster"):
        load_reference_compounds(
            FIXTURES / "m1_reference_compounds.yaml",
            roster_keys=set(),
            require_in_roster=True,
        )


def test_t21_strips_before_the_duplicate_check(tmp_path):
    """S11a's lesson: validating the stripped form while keying on the raw one lets
    " AAA" evade a duplicate check against "AAA" and then fail every join."""
    doc = yaml.safe_load((FIXTURES / "m1_reference_compounds.yaml").read_text())
    doc["compounds"][1]["canonical_inchikey"] = (
        "  " + doc["compounds"][0]["canonical_inchikey"] + "  "
    )
    path = tmp_path / "ref.yaml"
    path.write_text(yaml.safe_dump(doc))
    with pytest.raises(ReferenceCompoundError, match="repeats canonical_inchikey"):
        load_reference_compounds(path)
