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


def test_s11a_rejects_an_empty_name(poc_roster_path, tmp_path):
    """`name` is the third member of ROSTER_COLUMNS and had no rejection test —
    narrowing the validation loop to skip it passed the whole suite."""
    doc = yaml.safe_load(poc_roster_path.read_text())
    doc["compounds"][0]["name"] = "  "
    path = tmp_path / "r.yaml"
    path.write_text(yaml.safe_dump(doc))
    with pytest.raises(RosterValidationError, match="empty `name`"):
        load_poc_roster(path)


def test_s11a_strips_whitespace_from_keys(poc_roster_path, tmp_path):
    """A key entered as ' AAA' must not evade the duplicate check against 'AAA'."""
    doc = yaml.safe_load(poc_roster_path.read_text())
    doc["compounds"][1]["canonical_inchikey"] = " " + doc["compounds"][0]["canonical_inchikey"]
    path = tmp_path / "r.yaml"
    path.write_text(yaml.safe_dump(doc))
    with pytest.raises(RosterValidationError, match="repeats canonical_inchikey"):
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


def test_t13_never_clobbers_a_partially_filled_worksheet(compounds_for_labels, tmp_path):
    """THE condition that protects T14's 60-90 minutes from a single ETL re-run
    (defect 22). Every non-empty human cell must survive a regeneration.

    The regeneration must ACTUALLY REGENERATE. An earlier version of this test drove
    it with `labels` derived from the same fixture already on disk, so a merge that
    did nothing at all — `if out.exists(): return len(existing)` — passed it:
    "preserved" and "never written" were indistinguishable. It now asserts the merge
    did real work: a NEW key must appear, and a CHANGED snapshot_label must win,
    while human cells survive.
    """
    out = tmp_path / "w.csv"
    partial = pd.read_csv(
        FIXTURES / "pgp_adjudication_partial.csv", dtype=str, keep_default_na=False
    )
    partial.to_csv(out, index=False)
    before = partial.set_index("canonical_inchikey")

    new_key = "FIXTURENEWKEYAA-FIXTUREKEY-N"
    changed_key = before.index[0]
    keys = [*before.index, new_key]
    values = ["unknown"] * len(before) + ["unknown"]
    # flip the first key's snapshot_label away from whatever is on disk
    values[0] = "yes" if before.loc[changed_key, "snapshot_label"] != "yes" else "unknown"
    labels = pd.Series(values, index=keys)
    labels.index.name = "canonical_inchikey"

    compounds = pd.DataFrame(
        {"canonical_inchikey": keys, "name": [f"n-{i}" for i in range(len(keys))]}
    )

    write_adjudication_worksheet(labels, compounds, out)
    after = pd.read_csv(out, dtype=str, keep_default_na=False).set_index("canonical_inchikey")

    # (a) the merge really ran — the new key is present with human cells blank
    assert set(after.index) == set(labels.index)
    for column in HUMAN_OWNED_COLUMNS:
        assert after.loc[new_key, column] == ""

    # (b) the refreshed snapshot_label wins over the stale on-disk one
    assert after.loc[changed_key, "snapshot_label"] == labels[changed_key]

    # (c) and every non-empty human cell still survived
    filled = before[before["adjudicated_label"].str.strip() != ""]
    assert not filled.empty, "fixture must carry some filled cells to be a real test"
    for key, row in filled.iterrows():
        for column in HUMAN_OWNED_COLUMNS:
            if str(row[column]).strip():
                assert after.loc[key, column] == row[column], f"{column} for {key} was clobbered"


def test_t13_preserves_a_row_whose_only_human_content_is_a_doi(tmp_path):
    """The mid-session state: DOIs and attribution collected first, verdicts last.

    A guard keyed on `adjudicated_label` alone treats this row as unadjudicated and
    silently drops it — destroying exactly the work the module exists to protect.
    """
    out = tmp_path / "w.csv"
    pd.DataFrame(
        [
            {
                "canonical_inchikey": "AAA",
                "name": "a",
                "snapshot_label": "yes",
                "adjudicated_label": "yes",
                "evidence_doi": "10.1/x",
                "adjudicated_by": "H",
                "adjudicated_on": "2026-08-30",
            },
            {
                "canonical_inchikey": "BBB",
                "name": "b",
                "snapshot_label": "unknown",
                "adjudicated_label": "",
                "evidence_doi": "10.1000/inprogress",
                "adjudicated_by": "H.Reviewer",
                "adjudicated_on": "2026-08-30",
            },
        ]
    ).to_csv(out, index=False)

    labels = pd.Series(["yes"], index=["AAA"])
    labels.index.name = "canonical_inchikey"
    compounds = pd.DataFrame({"canonical_inchikey": ["AAA"], "name": ["a"]})

    with pytest.raises(AdjudicationError, match="carrying human work"):
        write_adjudication_worksheet(labels, compounds, out)


def test_t13_preserves_a_column_the_human_added(tmp_path):
    """A reviewer's `notes` column must survive regeneration."""
    out = tmp_path / "w.csv"
    frame = pd.read_csv(FIXTURES / "pgp_adjudication_filled.csv", dtype=str, keep_default_na=False)
    frame["notes"] = [f"note-{i}" for i in range(len(frame))]
    frame.to_csv(out, index=False)

    labels = pd.Series(list(frame["snapshot_label"]), index=list(frame["canonical_inchikey"]))
    labels.index.name = "canonical_inchikey"

    write_adjudication_worksheet(labels, frame.loc[:, ["canonical_inchikey", "name"]], out)
    after = pd.read_csv(out, dtype=str, keep_default_na=False).set_index("canonical_inchikey")
    assert "notes" in after.columns
    assert after.loc[frame["canonical_inchikey"].iloc[0], "notes"] == "note-0"


def test_t13_writes_atomically(tmp_path, monkeypatch):
    """`out` holds irreplaceable human work; a truncating in-place write means a
    failure during serialization destroys it."""
    out = tmp_path / "w.csv"
    frame = pd.read_csv(FIXTURES / "pgp_adjudication_filled.csv", dtype=str, keep_default_na=False)
    frame.to_csv(out, index=False)
    original = out.read_text()

    labels = pd.Series(list(frame["snapshot_label"]), index=list(frame["canonical_inchikey"]))
    labels.index.name = "canonical_inchikey"

    def boom(self, *a, **k):
        raise OSError("no space left on device")

    monkeypatch.setattr(pd.DataFrame, "to_csv", boom)
    with pytest.raises(OSError):
        write_adjudication_worksheet(labels, frame.loc[:, ["canonical_inchikey", "name"]], out)

    assert out.read_text() == original, "the human worksheet was damaged by a failed write"


def test_t13_raises_if_an_adjudicated_key_disappears(labels, compounds_for_labels, tmp_path):
    out = tmp_path / "w.csv"
    filled = pd.read_csv(FIXTURES / "pgp_adjudication_filled.csv", dtype=str, keep_default_na=False)
    filled.to_csv(out, index=False)

    shrunk = labels.iloc[2:]
    with pytest.raises(AdjudicationError, match="carrying human work"):
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


def test_t15_maps_each_compound_to_ITS_OWN_verdict():
    """The mapping, not just the shape (verdicts were freely permutable).

    Asserting only `set(series)` and a count accepts an implementation that reverses
    the verdict column — every compound receives a DIFFERENT compound's verdict, the
    aggregate is identical, and the whole suite passes. Same defect class as r1's
    constant-'unknown' label: right shape, wrong mapping.
    """
    series = adjudicate_pgp_labels(FIXTURES / "pgp_adjudication_filled.csv")

    assert series["FIXTURECMPDAAA-FIXTUREKEY-N"] == "yes"
    assert series["FIXTURECMPDAAB-FIXTUREKEY-N"] == "no"
    assert series["FIXTURECMPDAAC-FIXTUREKEY-N"] == "unknown"
    assert series.index.is_unique

    frame = pd.read_csv(FIXTURES / "pgp_adjudication_filled.csv", dtype=str, keep_default_na=False)
    for _, row in frame.iterrows():
        assert series[row["canonical_inchikey"]] == row["adjudicated_label"]


def test_t15_rejects_a_duplicated_canonical_inchikey(tmp_path):
    """Two contradictory verdicts for one compound must not be accepted silently."""
    frame = pd.read_csv(FIXTURES / "pgp_adjudication_filled.csv", dtype=str, keep_default_na=False)
    frame = pd.concat([frame, frame.iloc[[0]]], ignore_index=True)
    path = tmp_path / "dup.csv"
    frame.to_csv(path, index=False)

    with pytest.raises(AdjudicationError, match="repeats canonical_inchikey"):
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


def test_t15_parquet_preserves_index_metadata_without_normalization(tmp_path):
    """Read the file RAW, not through read_pgp_labels.

    `read_pgp_labels` unconditionally reassigns `index.name`, so it manufactures the
    very property the round-trip asserts — dropping the index name on write still
    passed. This checks what is actually on disk.
    """
    out = tmp_path / "pgp_labels.parquet"
    series = adjudicate_pgp_labels(FIXTURES / "pgp_adjudication_filled.csv", parquet_out=out)

    raw = pd.read_parquet(out, engine="pyarrow")
    assert raw.index.name == "canonical_inchikey"
    assert raw.index.tolist() == series.index.tolist()
    assert raw["adjudicated_label"].tolist() == series.tolist()


# --------------------------------------------------------------------------- #
# T17 · provenance block
# --------------------------------------------------------------------------- #


@pytest.fixture
def fixture_labels() -> pd.Series:
    return adjudicate_pgp_labels(FIXTURES / "pgp_adjudication_filled.csv")


def test_t17_renders_the_composed_version_string(provenance_fixture_path, fixture_labels):
    block = render_data_provenance(provenance_fixture_path, fixture_labels, panel=None)
    assert "DrugBank 4.2 (2015-03-19 snapshot)" in block


def test_t17_label_counts_are_not_permutable():
    """Hard-coded integers on an ASYMMETRIC series.

    Computing the expectation by calling `label_counts` — the function under test —
    can only confirm the renderer and the counter agree with each other. And the
    filled fixture used to be 8/8/8, so ANY permutation of the three counts was
    invisible even to a hand-written expectation.
    """
    labels = pd.Series(["yes", "yes", "yes", "no", "unknown", "unknown"], index=list("abcdef"))
    assert label_counts(labels) == {"yes": 3, "no": 1, "unknown": 2}


def test_t17_renders_the_counts_it_was_given(provenance_fixture_path):
    labels = pd.Series(["yes", "yes", "yes", "no", "unknown", "unknown"], index=list("abcdef"))
    block = render_data_provenance(provenance_fixture_path, labels, panel=None)
    assert "- yes: 3" in block
    assert "- no: 1" in block
    assert "- unknown: 2" in block


def test_t17_label_counts_rejects_out_of_domain_values():
    with pytest.raises(ValueError, match="outside"):
        label_counts(pd.Series(["yes", "no", "Yes", "substrate"], index=list("abcd")))


def test_t17_label_counts_rejects_nulls():
    with pytest.raises(ValueError, match="null"):
        label_counts(pd.Series(["yes", "no", None], index=list("abc")))


def test_t17_renders_three_integer_counts(provenance_fixture_path, fixture_labels):
    block = render_data_provenance(provenance_fixture_path, fixture_labels, panel=None)
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

    changed = render_data_provenance(path, fixture_labels, panel=None)
    assert "DrugBank 5.1 (2015-03-19 snapshot)" in changed
    assert "DrugBank 4.2" not in changed


def test_t17_snapshot_date_is_composed_too(provenance_fixture_path, fixture_labels, tmp_path):
    doc = yaml.safe_load(provenance_fixture_path.read_text())
    doc["snapshot_date"] = "2020-01-01"
    path = tmp_path / "p.yaml"
    path.write_text(yaml.safe_dump(doc))
    assert "DrugBank 4.2 (2020-01-01 snapshot)" in render_data_provenance(
        path, fixture_labels, panel=None
    )


def test_t17_reports_groups_usable_from_the_counts(provenance_fixture_path, fixture_labels):
    block = render_data_provenance(provenance_fixture_path, fixture_labels, panel=None)
    assert "- pgp_groups_usable: true" in block


def test_t17_groups_unusable_when_a_group_is_empty(provenance_fixture_path):
    """Computed from the counts, so the flag can never disagree with the numbers
    it is printed beside (defect 24)."""
    labels = pd.Series(["yes", "yes", "unknown"], index=["a", "b", "c"])
    block = render_data_provenance(provenance_fixture_path, labels, panel=None)
    assert "- pgp_groups_usable: false" in block
    assert not pgp_groups_usable(label_counts(labels))


def test_t17_renders_the_substitution_rationale_when_commits_differ(fixture_labels):
    block = render_data_provenance(
        FIXTURES / "provenance_justified_swap.yaml", fixture_labels, panel=None
    )
    assert "Audited commit" in block
    assert "Commit substitution rationale" in block


def test_t17_omits_the_rationale_when_commits_match(provenance_fixture_path, fixture_labels):
    block = render_data_provenance(provenance_fixture_path, fixture_labels, panel=None)
    assert "Commit substitution rationale" not in block


def test_t17_rejects_a_provenance_file_that_violates_the_contract(fixture_labels):
    """T17 renders only from a document that passes the E-1 contract — a card that
    renders unverified provenance is worse than no card."""
    from chipsim.harmonize.contracts import ProvenanceContractError

    with pytest.raises(ProvenanceContractError):
        render_data_provenance(
            FIXTURES / "provenance_unjustified_swap.yaml", fixture_labels, panel=None
        )


def test_t17_format_source_version_is_a_pure_composition():
    assert format_source_version("9.9", "1999-12-31") == "DrugBank 9.9 (1999-12-31 snapshot)"
