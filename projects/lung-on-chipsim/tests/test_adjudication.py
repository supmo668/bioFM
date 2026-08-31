"""Adjudication worksheet + loader + roster + provenance block —
build-plan T13, T15, T17, S11a.

**T14 and T18 are human-owned and ABSENT.** Nothing here fabricates a verdict, a
DOI, or a roster entry: every assertion runs against tests/fixtures/, whose
contents are FIXTURE-prefixed sentinels.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
import yaml

from chipsim.eval.provenance_block import (
    format_source_version,
    label_counts,
    pgp_groups_usable,
    render_data_provenance,
)
from chipsim.harmonize.adjudication import (
    HUMAN_OWNED_COLUMNS,
    WORKSHEET_COLUMNS,
    AdjudicationError,
    adjudicate_pgp_labels,
    read_pgp_labels,
    write_adjudication_worksheet,
)
from chipsim.harmonize.roster import (
    MAX_ROSTER_ENTRIES,
    MIN_ROSTER_ENTRIES,
    RosterValidationError,
    load_poc_roster,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = PROJECT_ROOT / "tests" / "fixtures"


# --------------------------------------------------------------------------- #
# S11a · roster validator
# --------------------------------------------------------------------------- #


def test_s11a_accepts_the_happy_fixture(poc_roster_path):
    roster = load_poc_roster(poc_roster_path)
    assert MIN_ROSTER_ENTRIES <= len(roster) <= MAX_ROSTER_ENTRIES
    assert list(roster.columns) == ["canonical_inchikey", "name", "evidence_doi"]


def test_s11a_rejects_too_few_entries():
    with pytest.raises(RosterValidationError, match="entries; S11a requires"):
        load_poc_roster(FIXTURES / "poc_compounds_too_few.yaml")


def test_s11a_rejects_too_many_entries():
    with pytest.raises(RosterValidationError, match="entries; S11a requires"):
        load_poc_roster(FIXTURES / "poc_compounds_too_many.yaml")


def test_s11a_rejects_an_empty_evidence_doi():
    with pytest.raises(RosterValidationError, match="empty `evidence_doi`"):
        load_poc_roster(FIXTURES / "poc_compounds_missing_doi.yaml")


def test_s11a_rejects_an_empty_canonical_inchikey(poc_roster_path, tmp_path):
    doc = yaml.safe_load(poc_roster_path.read_text())
    doc["compounds"][0]["canonical_inchikey"] = "  "
    path = tmp_path / "r.yaml"
    path.write_text(yaml.safe_dump(doc))
    with pytest.raises(RosterValidationError, match="empty `canonical_inchikey`"):
        load_poc_roster(path)


def test_s11a_rejects_a_key_absent_from_the_snapshot(poc_roster_path):
    """The fourth rejection case — a roster naming a compound the snapshot does
    not contain cannot be joined and would silently shrink the PoC."""
    with pytest.raises(RosterValidationError, match="absent from the "):
        load_poc_roster(poc_roster_path, snapshot_keys={"SOMETHINGELSE-KEY-N"})


def test_s11a_accepts_when_every_key_resolves(poc_roster_path):
    keys = set(load_poc_roster(poc_roster_path)["canonical_inchikey"])
    assert len(load_poc_roster(poc_roster_path, snapshot_keys=keys)) == len(keys)


def test_s11a_rejects_a_duplicated_key(poc_roster_path, tmp_path):
    doc = yaml.safe_load(poc_roster_path.read_text())
    doc["compounds"][1]["canonical_inchikey"] = doc["compounds"][0]["canonical_inchikey"]
    path = tmp_path / "r.yaml"
    path.write_text(yaml.safe_dump(doc))
    with pytest.raises(RosterValidationError, match="repeats canonical_inchikey"):
        load_poc_roster(path)


# --------------------------------------------------------------------------- #
# T13 · worksheet, and the never-clobber guarantee
# --------------------------------------------------------------------------- #


@pytest.fixture
def labels() -> pd.Series:
    frame = pd.read_csv(FIXTURES / "pgp_adjudication_filled.csv", dtype=str)
    series = pd.Series(frame["snapshot_label"].to_numpy(), index=frame["canonical_inchikey"])
    series.index.name = "canonical_inchikey"
    return series


@pytest.fixture
def compounds_for_labels(labels) -> pd.DataFrame:
    frame = pd.read_csv(FIXTURES / "pgp_adjudication_filled.csv", dtype=str)
    return frame.loc[:, ["canonical_inchikey", "name"]]


def test_t13_writes_one_row_per_roster_entry(labels, compounds_for_labels, tmp_path):
    out = tmp_path / "pgp_adjudication.csv"
    count = write_adjudication_worksheet(labels, compounds_for_labels, out)
    assert count == len(labels)
    assert MIN_ROSTER_ENTRIES <= count <= MAX_ROSTER_ENTRIES


def test_t13_verdict_columns_start_empty(labels, compounds_for_labels, tmp_path):
    out = tmp_path / "w.csv"
    write_adjudication_worksheet(labels, compounds_for_labels, out)
    frame = pd.read_csv(out, dtype=str, keep_default_na=False)
    assert list(frame.columns) == list(WORKSHEET_COLUMNS)
    for column in HUMAN_OWNED_COLUMNS:
        assert (frame[column] == "").all()


def test_t13_never_clobbers_a_partially_filled_worksheet(labels, compounds_for_labels, tmp_path):
    """THE condition that protects T14's 60-90 minutes from a single ETL re-run
    (defect 22). Every non-empty human cell must survive a regeneration."""
    out = tmp_path / "w.csv"
    write_adjudication_worksheet(labels, compounds_for_labels, out)

    partial = pd.read_csv(
        FIXTURES / "pgp_adjudication_partial.csv", dtype=str, keep_default_na=False
    )
    partial.to_csv(out, index=False)
    before = pd.read_csv(out, dtype=str, keep_default_na=False).set_index("canonical_inchikey")

    write_adjudication_worksheet(labels, compounds_for_labels, out)
    after = pd.read_csv(out, dtype=str, keep_default_na=False).set_index("canonical_inchikey")

    filled = before[before["adjudicated_label"].str.strip() != ""]
    assert not filled.empty, "fixture must carry some filled cells to be a real test"
    for key, row in filled.iterrows():
        for column in HUMAN_OWNED_COLUMNS:
            if str(row[column]).strip():
                assert after.loc[key, column] == row[column], f"{column} for {key} was clobbered"


def test_t13_raises_if_an_adjudicated_key_disappears(labels, compounds_for_labels, tmp_path):
    out = tmp_path / "w.csv"
    filled = pd.read_csv(FIXTURES / "pgp_adjudication_filled.csv", dtype=str, keep_default_na=False)
    filled.to_csv(out, index=False)

    shrunk = labels.iloc[2:]
    with pytest.raises(AdjudicationError, match="previously-adjudicated"):
        write_adjudication_worksheet(shrunk, compounds_for_labels, out)


def test_t13_raises_if_a_label_index_is_missing_from_compounds(labels, tmp_path):
    with pytest.raises(AdjudicationError, match="missing from `compounds`"):
        write_adjudication_worksheet(
            labels,
            pd.DataFrame({"canonical_inchikey": ["NOPE-KEY-N"], "name": ["x"]}),
            tmp_path / "w.csv",
        )


# --------------------------------------------------------------------------- #
# T15 · adjudication loader
# --------------------------------------------------------------------------- #


def test_t15_wholly_blank_worksheet_raises():
    """r1 returned all-'unknown' here, which looked identical to a completed
    worksheet (defect 6)."""
    with pytest.raises(AdjudicationError, match="wholly unadjudicated"):
        adjudicate_pgp_labels(FIXTURES / "pgp_adjudication_blank.csv")


def test_t15_partially_filled_worksheet_raises():
    with pytest.raises(AdjudicationError, match="partially adjudicated"):
        adjudicate_pgp_labels(FIXTURES / "pgp_adjudication_partial.csv")


def test_t15_all_unknown_worksheet_raises():
    """Completed, in-domain, and still unusable: no 'yes' and no 'no' group."""
    with pytest.raises(AdjudicationError, match="empty 'yes' group"):
        adjudicate_pgp_labels(FIXTURES / "pgp_adjudication_all_unknown.csv")


def test_t15_single_populated_group_raises():
    """defect 24 — the M5 grouping variable is unusable with one group."""
    with pytest.raises(AdjudicationError, match="empty 'no' group"):
        adjudicate_pgp_labels(FIXTURES / "pgp_adjudication_single_group.csv")


def test_t15_verdict_without_a_doi_raises():
    with pytest.raises(AdjudicationError, match="empty `evidence_doi`"):
        adjudicate_pgp_labels(FIXTURES / "pgp_adjudication_no_missing_doi.csv")


def test_t15_out_of_domain_value_raises(tmp_path):
    frame = pd.read_csv(FIXTURES / "pgp_adjudication_filled.csv", dtype=str, keep_default_na=False)
    frame.loc[0, "adjudicated_label"] = "probably"
    path = tmp_path / "w.csv"
    frame.to_csv(path, index=False)
    with pytest.raises(AdjudicationError, match="outside"):
        adjudicate_pgp_labels(path)


def test_t15_verdict_without_an_adjudicator_raises(tmp_path):
    frame = pd.read_csv(FIXTURES / "pgp_adjudication_filled.csv", dtype=str, keep_default_na=False)
    frame.loc[0, "adjudicated_by"] = ""
    path = tmp_path / "w.csv"
    frame.to_csv(path, index=False)
    with pytest.raises(AdjudicationError, match="empty `adjudicated_by`"):
        adjudicate_pgp_labels(path)


def test_t15_fully_adjudicated_fixture_returns_the_domain():
    series = adjudicate_pgp_labels(FIXTURES / "pgp_adjudication_filled.csv")
    assert set(series) == {"yes", "no", "unknown"}
    assert series.index.name == "canonical_inchikey"


def test_t15_unknown_is_a_completed_verdict_not_a_blank():
    """An empty cell is INCOMPLETE; the literal 'unknown' is COMPLETE. The blank
    fixture raises while the filled one (which contains 'unknown' rows) does not —
    that asymmetry is the whole point."""
    series = adjudicate_pgp_labels(FIXTURES / "pgp_adjudication_filled.csv")
    assert (series == "unknown").sum() > 0


def test_t15_parquet_round_trips_to_an_identical_series(tmp_path):
    out = tmp_path / "pgp_labels.parquet"
    series = adjudicate_pgp_labels(FIXTURES / "pgp_adjudication_filled.csv", parquet_out=out)
    pd.testing.assert_series_equal(read_pgp_labels(out), series)


# --------------------------------------------------------------------------- #
# T17 · provenance block
# --------------------------------------------------------------------------- #


@pytest.fixture
def fixture_labels() -> pd.Series:
    return adjudicate_pgp_labels(FIXTURES / "pgp_adjudication_filled.csv")


def test_t17_renders_the_composed_version_string(provenance_fixture_path, fixture_labels):
    block = render_data_provenance(provenance_fixture_path, fixture_labels)
    assert "DrugBank 4.2 (2015-03-19 snapshot)" in block


def test_t17_renders_three_integer_counts(provenance_fixture_path, fixture_labels):
    block = render_data_provenance(provenance_fixture_path, fixture_labels)
    counts = label_counts(fixture_labels)
    assert f"- yes: {counts['yes']}" in block
    assert f"- no: {counts['no']}" in block
    assert f"- unknown: {counts['unknown']}" in block
    assert sum(counts.values()) == len(fixture_labels)


def test_t17_version_is_composed_not_hard_coded(provenance_fixture_path, fixture_labels, tmp_path):
    """THE assertion that proves the value is composed, not hard-coded (defect 14).
    A literal 'DrugBank 4.2 (2015-03-19 snapshot)' passes the previous test and
    fails this one."""
    doc = yaml.safe_load(provenance_fixture_path.read_text())
    doc["upstream_version"] = "5.1"
    path = tmp_path / "p.yaml"
    path.write_text(yaml.safe_dump(doc))

    changed = render_data_provenance(path, fixture_labels)
    assert "DrugBank 5.1 (2015-03-19 snapshot)" in changed
    assert "DrugBank 4.2" not in changed


def test_t17_snapshot_date_is_composed_too(provenance_fixture_path, fixture_labels, tmp_path):
    doc = yaml.safe_load(provenance_fixture_path.read_text())
    doc["snapshot_date"] = "2020-01-01"
    path = tmp_path / "p.yaml"
    path.write_text(yaml.safe_dump(doc))
    assert "DrugBank 4.2 (2020-01-01 snapshot)" in render_data_provenance(path, fixture_labels)


def test_t17_reports_groups_usable_from_the_counts(provenance_fixture_path, fixture_labels):
    block = render_data_provenance(provenance_fixture_path, fixture_labels)
    assert "- pgp_groups_usable: true" in block


def test_t17_groups_unusable_when_a_group_is_empty(provenance_fixture_path):
    """Computed from the counts, so the flag can never disagree with the numbers
    it is printed beside (defect 24)."""
    labels = pd.Series(["yes", "yes", "unknown"], index=["a", "b", "c"])
    block = render_data_provenance(provenance_fixture_path, labels)
    assert "- pgp_groups_usable: false" in block
    assert not pgp_groups_usable(label_counts(labels))


def test_t17_renders_the_substitution_rationale_when_commits_differ(fixture_labels):
    block = render_data_provenance(FIXTURES / "provenance_justified_swap.yaml", fixture_labels)
    assert "Audited commit" in block
    assert "Commit substitution rationale" in block


def test_t17_omits_the_rationale_when_commits_match(provenance_fixture_path, fixture_labels):
    block = render_data_provenance(provenance_fixture_path, fixture_labels)
    assert "Commit substitution rationale" not in block


def test_t17_rejects_a_provenance_file_that_violates_the_contract(fixture_labels):
    """T17 renders only from a document that passes the E-1 contract — a card that
    renders unverified provenance is worse than no card."""
    from chipsim.harmonize.contracts import ProvenanceContractError

    with pytest.raises(ProvenanceContractError):
        render_data_provenance(FIXTURES / "provenance_unjustified_swap.yaml", fixture_labels)


def test_t17_format_source_version_is_a_pure_composition():
    assert format_source_version("9.9", "1999-12-31") == "DrugBank 9.9 (1999-12-31 snapshot)"
