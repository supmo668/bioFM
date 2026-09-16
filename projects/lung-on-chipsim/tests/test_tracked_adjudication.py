"""The TRACKED adjudication file — build-plan r2.18, T14 export helper and T15 loader.

The principal's record-content invariant forbids a tracked (name, structure) association. The
reviewer still needs names to work, so the two halves are split (r2.17, F-05):

  - the generated, UNTRACKED worksheet keeps `name` beside the evidence;
  - the TRACKED `configs/pgp_adjudication.csv` carries exactly five columns and no `name`.

r2.17 amended T14's file and T15's raise in one revision without reading them together: T15
raised when the WORKSHEET lacked `stereo_is_relative`, and the five-column tracked file has no
such column, so T15 would have raised on every valid input. r2.18 repairs it: T15 reads the
tracked file and RECOMPUTES the flag from `compounds`, and `export_tracked_adjudication` produces
the tracked file so that "move to configs/" is never a human deleting columns by hand.

All keys, DOIs and attributions are FIXTURE sentinels; the tracked fixtures are projections of
the committed worksheet fixtures of the same case, with no value invented.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from chipsim.harmonize.adjudication import (
    TRACKED_COLUMNS,
    AdjudicationError,
    adjudicate_pgp_labels,
    export_tracked_adjudication,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = PROJECT_ROOT / "tests" / "fixtures"

FIVE = (
    "canonical_inchikey",
    "adjudicated_label",
    "evidence_doi",
    "adjudicated_by",
    "adjudicated_on",
)


def _compounds(keys, relative=None) -> pd.DataFrame:
    keys = list(keys)
    return pd.DataFrame(
        {
            "canonical_inchikey": keys,
            "name": [f"FIXTURE-NAME-{i:02d}" for i in range(len(keys))],
            "stereo_is_relative": relative if relative is not None else [False] * len(keys),
        }
    )


def _tracked(case: str) -> Path:
    return FIXTURES / f"pgp_adjudication_tracked_{case}.csv"


def _keys(case: str) -> list[str]:
    return pd.read_csv(_tracked(case), dtype=str)["canonical_inchikey"].tolist()


# --- the tracked shape -----------------------------------------------------------------


def test_tracked_columns_are_exactly_the_five_the_plan_names_in_order():
    assert TRACKED_COLUMNS == FIVE
    assert "name" not in TRACKED_COLUMNS


@pytest.mark.parametrize(
    "case", ["filled", "blank", "partial", "all_unknown", "no_missing_doi", "single_group"]
)
def test_tracked_fixtures_are_projections_of_their_worksheet_fixtures(case):
    """The tracked fixtures invent nothing: each is the worksheet fixture of the same case,
    reduced to the five columns, row for row."""
    tracked = pd.read_csv(_tracked(case), dtype=str, keep_default_na=False)
    worksheet = pd.read_csv(
        FIXTURES / f"pgp_adjudication_{case}.csv", dtype=str, keep_default_na=False
    )
    assert tuple(tracked.columns) == FIVE
    pd.testing.assert_frame_equal(tracked, worksheet.loc[:, list(FIVE)])


# --- T14 export helper -------------------------------------------------------------------


def _worksheet(tmp_path: Path, **extra) -> Path:
    frame = pd.read_csv(FIXTURES / "pgp_adjudication_filled.csv", dtype=str, keep_default_na=False)
    frame.insert(3, "stereo_is_relative", "False")
    frame.insert(4, "label_disagrees_with_key", "unresolved")
    for column, value in extra.items():
        frame[column] = value
    path = tmp_path / "worksheet.csv"
    frame.to_csv(path, index=False)
    return path


def test_export_writes_exactly_the_five_columns_and_returns_the_row_count(tmp_path):
    out = tmp_path / "configs" / "pgp_adjudication.csv"
    written = export_tracked_adjudication(_worksheet(tmp_path), out)
    frame = pd.read_csv(out, dtype=str, keep_default_na=False)
    assert tuple(frame.columns) == FIVE
    assert written == len(frame) == 24


def test_export_preserves_every_verdict_doi_and_attribution_row_for_row(tmp_path):
    out = tmp_path / "pgp_adjudication.csv"
    export_tracked_adjudication(_worksheet(tmp_path), out)
    exported = pd.read_csv(out, dtype=str, keep_default_na=False)
    pd.testing.assert_frame_equal(
        exported, pd.read_csv(_tracked("filled"), dtype=str, keep_default_na=False)
    )


def test_export_drops_name_and_every_generated_column_by_design(tmp_path):
    out = tmp_path / "pgp_adjudication.csv"
    export_tracked_adjudication(_worksheet(tmp_path), out)
    header = out.read_text().splitlines()[0].split(",")
    for dropped in ("name", "snapshot_label", "stereo_is_relative", "label_disagrees_with_key"):
        assert dropped not in header


def test_export_names_the_columns_it_drops_so_the_omission_is_legible():
    doc = export_tracked_adjudication.__doc__ or ""
    for dropped in ("name", "snapshot_label", "stereo_is_relative", "label_disagrees_with_key"):
        assert f"`{dropped}`" in doc


def test_export_refuses_a_human_added_column_rather_than_dropping_it(tmp_path):
    out = tmp_path / "pgp_adjudication.csv"
    with pytest.raises(AdjudicationError, match="notes"):
        export_tracked_adjudication(_worksheet(tmp_path, notes="checked twice"), out)
    assert not out.exists(), "a refused export must not leave a partial tracked file"


def test_export_refuses_a_human_added_column_even_when_it_is_empty(tmp_path):
    """Emptiness today is not intent: the column exists because a reviewer made it."""
    with pytest.raises(AdjudicationError, match="pmid"):
        export_tracked_adjudication(_worksheet(tmp_path, pmid=""), tmp_path / "out.csv")


def test_export_leaves_no_temporary_file_behind(tmp_path):
    out = tmp_path / "pgp_adjudication.csv"
    export_tracked_adjudication(_worksheet(tmp_path), out)
    assert sorted(p.name for p in tmp_path.iterdir()) == ["pgp_adjudication.csv", "worksheet.csv"]


def test_exported_file_loads_through_t15(tmp_path):
    """The composition the r2.17 contradiction broke: T14's output must be T15's input."""
    out = tmp_path / "pgp_adjudication.csv"
    export_tracked_adjudication(_worksheet(tmp_path), out)
    series = adjudicate_pgp_labels(out, _compounds(_keys("filled")))
    assert set(series) == {"yes", "no", "unknown"}


# --- T15 reads the tracked file and recomputes the flag ----------------------------------------


def test_t15_refuses_compounds_without_the_flag():
    with pytest.raises(AdjudicationError, match="stereo_is_relative"):
        adjudicate_pgp_labels(
            _tracked("filled"), _compounds(_keys("filled")).drop(columns="stereo_is_relative")
        )


def test_t15_refuses_an_adjudicated_key_absent_from_compounds():
    keys = _keys("filled")
    with pytest.raises(AdjudicationError, match=keys[-1]):
        adjudicate_pgp_labels(_tracked("filled"), _compounds(keys[:-1]))


def test_t15_refuses_a_tracked_file_carrying_a_name_column(tmp_path):
    """The file the invariant protects: a name beside a structure key, tracked. T15 is the one
    reader of that file, so it must not accept the association silently."""
    frame = pd.read_csv(_tracked("filled"), dtype=str, keep_default_na=False)
    frame.insert(1, "name", "FIXTURE-NAME")
    path = tmp_path / "pgp_adjudication.csv"
    frame.to_csv(path, index=False)
    # Branch-specific (QG G-12): "export_tracked_adjudication" appears in BOTH refusal messages,
    # so a refusal with the WRONG diagnosis would otherwise pass and send the reviewer astray.
    with pytest.raises(AdjudicationError, match="outside the tracked schema") as exc:
        adjudicate_pgp_labels(path, _compounds(_keys("filled")))
    assert "'name'" in str(exc.value)


def test_t15_refuses_a_tracked_file_missing_a_required_column(tmp_path):
    frame = pd.read_csv(_tracked("filled"), dtype=str, keep_default_na=False)
    path = tmp_path / "pgp_adjudication.csv"
    frame.drop(columns="adjudicated_on").to_csv(path, index=False)
    with pytest.raises(AdjudicationError, match="adjudicated_on"):
        adjudicate_pgp_labels(path, _compounds(_keys("filled")))


def test_t15_recomputes_the_flag_per_key_true_if_any_member_is_flagged(tmp_path):
    keys = _keys("filled")
    # Two compound rows share keys[0]; only the SECOND is flagged. keys[1] is flagged alone.
    compounds = pd.concat(
        [
            _compounds(keys),
            _compounds([keys[0]], relative=[True]),
        ],
        ignore_index=True,
    )
    compounds.loc[1, "stereo_is_relative"] = True
    out = tmp_path / "pgp_labels.parquet"
    adjudicate_pgp_labels(_tracked("filled"), compounds, parquet_out=out)
    raw = pd.read_parquet(out, engine="pyarrow")
    assert raw["stereo_is_relative"].dtype == bool
    assert raw.loc[keys[0], "stereo_is_relative"]
    assert raw.loc[keys[1], "stereo_is_relative"]
    assert not raw.loc[keys[2:], "stereo_is_relative"].any()


def test_t15_flag_comes_from_compounds_not_from_any_column_in_the_file(tmp_path):
    """A stale flag column smuggled into the tracked file must not be read: the flag is
    generated, never carried. (The file is refused outright, which also guarantees this.)"""
    frame = pd.read_csv(_tracked("filled"), dtype=str, keep_default_na=False)
    frame["stereo_is_relative"] = "True"
    path = tmp_path / "pgp_adjudication.csv"
    frame.to_csv(path, index=False)
    with pytest.raises(AdjudicationError, match="stereo_is_relative"):
        adjudicate_pgp_labels(path, _compounds(_keys("filled")))


# --- QG §3 findings ------------------------------------------------------------------------


def test_export_refuses_to_blank_a_verdict_an_existing_tracked_file_already_carries(tmp_path):
    """QG CODE-2/SEC-8. Measured before the fix: a BLANK worksheet exported over a filled tracked
    file left 0 of 24 verdicts and returned 24, which reads as success.

    Reachable without anyone being careless: the git-ignored worksheet under data/interim/ is lost
    (clean checkout, DVC re-pull, new machine); T13 regenerates it blank WITHOUT error, because its
    vanished-key guard only fires when the prior worksheet carried human content; the reviewer
    re-exports "to refresh configs/" and 60-90 minutes of adjudication becomes 24 empty rows. This
    module exists to prevent exactly that (defect 22); the tracked file was the copy the rule did
    not cover.
    """
    tracked = tmp_path / "pgp_adjudication.csv"
    export_tracked_adjudication(_worksheet(tmp_path), tracked)
    before = tracked.read_bytes()

    blank = pd.read_csv(FIXTURES / "pgp_adjudication_blank.csv", dtype=str, keep_default_na=False)
    blank.insert(3, "stereo_is_relative", "False")
    blank.insert(4, "label_disagrees_with_key", "unresolved")
    stale = tmp_path / "stale_worksheet.csv"
    blank.to_csv(stale, index=False)

    with pytest.raises(AdjudicationError, match="24"):
        export_tracked_adjudication(stale, tracked)
    assert tracked.read_bytes() == before, "tracked verdicts must survive a refused export"


def test_export_still_writes_when_the_projection_only_adds_verdicts(tmp_path):
    """The refusal must not freeze the file: filling MORE rows is the normal second export."""
    tracked = tmp_path / "pgp_adjudication.csv"
    partial = pd.read_csv(
        FIXTURES / "pgp_adjudication_partial.csv", dtype=str, keep_default_na=False
    )
    partial.insert(3, "stereo_is_relative", "False")
    first = tmp_path / "first.csv"
    partial.to_csv(first, index=False)
    export_tracked_adjudication(first, tracked)

    written = export_tracked_adjudication(_worksheet(tmp_path), tracked)
    after = pd.read_csv(tracked, dtype=str, keep_default_na=False)
    assert written == 24
    assert (after["adjudicated_label"] != "").all()


def test_the_flag_follows_the_key_not_the_row_position(tmp_path):
    """QG CODE-3/DES-9. Every tracked fixture is already in sorted key order and groupby returns
    sorted keys, so positional and key-based assignment agree in every other test: deleting the
    `.reindex(...)` would keep the suite green while attaching each row the WRONG key's flag on a
    real, re-sorted tracked file. Here the file is reversed and the flagged key is neither first
    nor last in either ordering.
    """
    frame = pd.read_csv(_tracked("filled"), dtype=str, keep_default_na=False).iloc[::-1]
    path = tmp_path / "pgp_adjudication.csv"
    frame.to_csv(path, index=False)

    keys = _keys("filled")
    flagged = keys[3]
    compounds = _compounds(keys, relative=[k == flagged for k in keys])
    out = tmp_path / "pgp_labels.parquet"
    adjudicate_pgp_labels(path, compounds, parquet_out=out)

    raw = pd.read_parquet(out, engine="pyarrow")
    assert raw.index.tolist() == list(frame["canonical_inchikey"]), "file row order must survive"
    assert raw.loc[flagged, "stereo_is_relative"]
    assert raw["stereo_is_relative"].sum() == 1


def test_a_non_boolean_flag_column_is_refused_rather_than_coerced():
    """QG OWN-1/CODE-5. `.astype(bool)` makes every non-empty string True, so a compounds frame
    read back from CSV (dtype=str is this project's own convention) reported 24 of 24 compounds as
    relative-stereo: a false flag handed to T17 as fact, with no error anywhere."""
    keys = _keys("filled")
    compounds = _compounds(keys)
    compounds["stereo_is_relative"] = ["True"] + ["False"] * (len(keys) - 1)
    with pytest.raises(AdjudicationError, match="stereo_is_relative"):
        adjudicate_pgp_labels(_tracked("filled"), compounds)


def test_t15_names_a_missing_canonical_inchikey_column_as_t13_does():
    """QG CODE-6/DES-6: the same mistake raised a clear AdjudicationError in T13 and a bare
    KeyError here, so a caller could not catch one error type and be done."""
    keys = _keys("filled")
    compounds = _compounds(keys).rename(columns={"canonical_inchikey": "inchikey"})
    with pytest.raises(AdjudicationError, match="canonical_inchikey"):
        adjudicate_pgp_labels(_tracked("filled"), compounds)


def test_the_export_projection_and_its_docstring_cannot_drift_apart():
    """QG DES-3. The refusal tests membership of WRITTEN_COLUMNS while the real drop set is
    WRITTEN_COLUMNS - TRACKED_COLUMNS, so a column added to either class would be dropped silently
    instead of refused — the very loss the helper exists to prevent — and the docstring's named
    list would quietly stop being the truth."""
    from chipsim.harmonize.adjudication import HUMAN_OWNED_COLUMNS, WRITTEN_COLUMNS

    assert TRACKED_COLUMNS == ("canonical_inchikey", *HUMAN_OWNED_COLUMNS)
    dropped = tuple(c for c in WRITTEN_COLUMNS if c not in TRACKED_COLUMNS)
    assert dropped == ("name", "snapshot_label", "stereo_is_relative", "label_disagrees_with_key")
    doc = export_tracked_adjudication.__doc__ or ""
    for column in dropped:
        assert f"`{column}`" in doc, f"{column} is dropped but not named in the docstring"


def test_the_real_t13_worksheet_exports_and_loads(tmp_path):
    """QG DES-10. Elsewhere the export's input is a hand-built proxy for T13's output, so the
    T13 -> T14 leg was pinned against a shape rather than against T13 itself."""
    from chipsim.harmonize.adjudication import write_adjudication_worksheet

    keys = _keys("filled")
    labels = pd.Series(["yes"] * len(keys), index=keys)
    labels.index.name = "canonical_inchikey"
    worksheet = tmp_path / "worksheet.csv"
    write_adjudication_worksheet(labels, _compounds(keys), worksheet)

    filled = pd.read_csv(worksheet, dtype=str, keep_default_na=False)
    filled["adjudicated_label"] = "yes"
    filled.loc[0, "adjudicated_label"] = "no"
    filled["evidence_doi"] = "10.0000/fixture"
    filled["adjudicated_by"] = "FIXTURE-ADJUDICATOR"
    filled["adjudicated_on"] = "1970-01-01"
    filled.to_csv(worksheet, index=False)

    tracked = tmp_path / "pgp_adjudication.csv"
    assert export_tracked_adjudication(worksheet, tracked) == len(keys)
    series = adjudicate_pgp_labels(tracked, _compounds(keys))
    assert set(series) == {"yes", "no"}


def test_exporting_an_already_tracked_file_says_so_instead_of_asking_for_a_name_column(tmp_path):
    """QG DES-7. Re-running the export on its own output failed with "missing column(s):
    ['name', 'snapshot_label']" — telling the human to add `name` to the one file whose entire
    design point is that it must never carry `name`."""
    tracked = tmp_path / "pgp_adjudication.csv"
    export_tracked_adjudication(_worksheet(tmp_path), tracked)
    with pytest.raises(AdjudicationError) as exc:
        export_tracked_adjudication(tracked, tmp_path / "again.csv")
    message = str(exc.value)
    # Assert the SENTENCE, not the word: pytest names tmp_path after the test, so this file's
    # own path contains "already" and an `"already" in message` check passed vacuously (QG G-08).
    assert "is already the tracked five-column projection" in message
    assert "missing column" not in message, "must not ask the human to add a `name` column"


def test_a_failed_export_leaves_an_existing_tracked_file_byte_identical(tmp_path, monkeypatch):
    """QG G-04/TEST-2. Replacing the tmp+os.replace block with a plain to_csv kept the whole suite
    green, because the only atomicity test asserted the RESIDUE (no leftover .tmp) rather than the
    mechanism — and a non-atomic write leaves no residue either. T13 already had this test
    (test_t13_writes_atomically); the tracked file, which is the published record, did not."""
    tracked = tmp_path / "pgp_adjudication.csv"
    worksheet = _worksheet(tmp_path)  # built BEFORE the patch — see below
    export_tracked_adjudication(worksheet, tracked)
    original = tracked.read_bytes()

    real_to_csv = pd.DataFrame.to_csv

    def half_written(self, path_or_buf=None, *args, **kwargs):
        """Write PART of the file, then fail — a disk filling up, not a clean no-op.

        Two ways this test can pass while proving nothing, both measured against the non-atomic
        mutant (`to_csv(out)` with no tmp + os.replace), which SURVIVED each:
          1. raising BEFORE writing anything — a direct write then leaves the file intact too;
          2. building the worksheet INSIDE the patched call — `_worksheet` itself calls to_csv,
             so the OSError fires while writing the WORKSHEET and the export never runs at all.
        Hence: a partial write, and the worksheet prepared before the patch.
        """
        Path(path_or_buf).write_text("canonical_inchikey,adjudicated_label\nFIXTURECMP")
        raise OSError("no space left on device")

    monkeypatch.setattr(pd.DataFrame, "to_csv", half_written)
    with pytest.raises(OSError):
        export_tracked_adjudication(worksheet, tracked)
    monkeypatch.setattr(pd.DataFrame, "to_csv", real_to_csv)

    assert tracked.read_bytes() == original, "a failed write must not truncate the tracked file"
    assert not (tracked.parent / (tracked.name + ".tmp")).exists()


def test_compounds_may_cover_more_keys_than_the_adjudication_file(tmp_path):
    """QG G-07/TEST-3. `compounds` is the whole snapshot; the adjudication file is the 20-40
    roster. Only the opposite direction was checked, so injecting a refusal for surplus compound
    keys kept the suite green — it would have broken the normal pipeline shape."""
    keys = _keys("filled")
    surplus = "FIXTUREEXTRA-FIXTUREKEY-N"
    compounds = _compounds(keys + [surplus], relative=[False] * len(keys) + [True])
    out = tmp_path / "pgp_labels.parquet"
    series = adjudicate_pgp_labels(_tracked("filled"), compounds, parquet_out=out)

    assert len(series) == len(keys)
    assert surplus not in series.index
    raw = pd.read_parquet(out, engine="pyarrow")
    assert len(raw) == len(keys)
    assert not raw["stereo_is_relative"].any(), "a surplus key's flag must not leak onto a row"


def test_a_header_only_tracked_file_raises_rather_than_returning_nothing(tmp_path):
    """QG G-13/TEST-6. Empty any() / value_counts() / groupby are classic pandas edges, and an
    empty result here would look like a completed load with no verdicts."""
    path = tmp_path / "pgp_adjudication.csv"
    path.write_text(",".join(TRACKED_COLUMNS) + "\n")
    empty = pd.DataFrame(
        {"canonical_inchikey": [], "name": [], "stereo_is_relative": pd.Series([], dtype=bool)}
    )
    with pytest.raises(AdjudicationError, match="wholly unadjudicated"):
        adjudicate_pgp_labels(path, empty)


def test_exporting_a_zero_row_worksheet_writes_a_header_and_returns_zero(tmp_path):
    """QG G-13: the count must be honest rather than the write being skipped."""
    frame = pd.read_csv(FIXTURES / "pgp_adjudication_filled.csv", dtype=str, keep_default_na=False)
    frame.insert(3, "stereo_is_relative", "False")
    frame.insert(4, "label_disagrees_with_key", "unresolved")
    empty_sheet = tmp_path / "worksheet.csv"
    frame.iloc[0:0].to_csv(empty_sheet, index=False)

    out = tmp_path / "pgp_adjudication.csv"
    assert export_tracked_adjudication(empty_sheet, out) == 0
    assert tuple(pd.read_csv(out, dtype=str).columns) == FIVE


def test_every_adjudication_fixture_key_is_a_fixture_sentinel():
    """QG G-05/DES-11. S5 exempts CSV fixtures from the sentinel banner because they are "covered
    by digest + key namespace" — but nothing asserted the namespace for these. The tracked
    fixtures are the first fixtures SCHEMA-IDENTICAL to the real tracked artifact, so a `cp` plus
    a one-cell edit would install a synthetic adjudication as the genuine human artifact, on the
    plan's most load-bearing human input (defect 23)."""
    seen = 0
    for path in sorted(FIXTURES.glob("pgp_adjudication*.csv")):
        keys = pd.read_csv(path, dtype=str, keep_default_na=False)["canonical_inchikey"]
        assert len(keys) > 0, path.name
        for key in keys:
            assert key.startswith("FIXTURE"), f"{path.name} carries a non-sentinel key: {key}"
        seen += 1
    assert seen >= 12, f"expected both fixture families (worksheet + tracked), found {seen}"


def test_the_real_tracked_adjudication_file_if_present_carries_no_name_column():
    """QG G-06/SEC-2. FAIL-CLOSED, and the only check that runs without anyone loading the file.
    The five-column rule is otherwise enforced only when T15 reads it, and the repo-wide
    record-content guard has no name detection at all — so a human who did T14 the manual way
    ("move to configs/") could commit a worksheet-shaped file carrying `name` beside the
    structure key and the entire suite would stay green."""
    real = PROJECT_ROOT / "configs" / "pgp_adjudication.csv"
    if not real.exists():
        pytest.skip("T14 is human-owned and absent; the check arms itself when the file lands")
    header = tuple(pd.read_csv(real, nrows=0).columns)
    assert header == TRACKED_COLUMNS, (
        f"{real} must carry exactly {list(TRACKED_COLUMNS)}; found {list(header)}. Produce it "
        "with export_tracked_adjudication(), never by hand."
    )


def test_the_module_reader_carries_the_flag_through_the_parquet(tmp_path):
    """QG G-19 (CTO ruling). T15 writes the flag "so T17 receives it"; before this, the module's
    own reader dropped it and a caller had to bypass the module to get it back."""
    from chipsim.harmonize.adjudication import read_pgp_label_frame, read_pgp_labels

    keys = _keys("filled")
    flagged = keys[2]
    compounds = _compounds(keys, relative=[k == flagged for k in keys])
    out = tmp_path / "pgp_labels.parquet"
    series = adjudicate_pgp_labels(_tracked("filled"), compounds, parquet_out=out)

    frame = read_pgp_label_frame(out)
    assert frame["stereo_is_relative"].dtype == bool
    assert frame.loc[flagged, "stereo_is_relative"]
    assert frame["stereo_is_relative"].sum() == 1
    assert frame.index.name == "canonical_inchikey"
    pd.testing.assert_series_equal(frame["adjudicated_label"], series)
    pd.testing.assert_series_equal(read_pgp_labels(out), series)


def test_a_label_parquet_without_the_flag_is_refused_by_the_frame_reader(tmp_path):
    """A pre-re-key label set must not read as "nothing is relative-stereo"."""
    from chipsim.harmonize.adjudication import read_pgp_label_frame

    legacy = pd.DataFrame({"adjudicated_label": ["yes"]}, index=["FIXTURECMPDAAA-FIXTUREKEY-N"])
    legacy.index.name = "canonical_inchikey"
    path = tmp_path / "legacy.parquet"
    legacy.to_parquet(path, engine="pyarrow")
    with pytest.raises(AdjudicationError, match="stereo_is_relative"):
        read_pgp_label_frame(path)
