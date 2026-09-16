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
    pd.testing.assert_frame_equal(exported, pd.read_csv(_tracked("filled"), dtype=str, keep_default_na=False))


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
    with pytest.raises(AdjudicationError, match="export_tracked_adjudication"):
        adjudicate_pgp_labels(path, _compounds(_keys("filled")))


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
