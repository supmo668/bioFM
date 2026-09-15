"""Generated worksheet columns, label/structure agreement, and flag honouring —
CTO #125 (T13/T15/T10 rulings) and #126 (label_disagrees_with_key).

**Generated columns are a third column class** (#125 §1), distinct from the declared
schema and from human-owned verdicts:

  - adding them to the required schema would lock a reviewer out of an existing sheet;
  - writing them as undeclared extras would let the never-clobber merge PRESERVE A STALE
    value, because undeclared columns are treated as human-added;

so they are recomputed on every write, NEVER carried from the prior sheet, and OPTIONAL
on read.

**`label_disagrees_with_key` is tri-state** (#126 §2): disagrees / agrees / unresolved.
Two-state would force every unresolvable row into a false "agrees". It is computed from a
committed reference table, never a live call, and it gates nothing.

**T15 raises on a legacy sheet** without `stereo_is_relative` (#125 §2), and says how to fix
it. **T10 refuses a frame without the flag** (#125 §3).

Every key, name and DOI below is SYNTHETIC, in the FIXTURE-sentinel style of the existing
adjudication fixtures.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
import yaml

from chipsim.harmonize.adjudication import (
    GENERATED_COLUMNS,
    HUMAN_OWNED_COLUMNS,
    WORKSHEET_COLUMNS,
    WRITTEN_COLUMNS,
    AdjudicationError,
    _read_worksheet,
    adjudicate_pgp_labels,
    write_adjudication_worksheet,
)
from chipsim.harmonize.label_reference import (
    LABEL_AGREEMENT,
    LabelReferenceError,
    label_agreement,
    load_label_reference,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = PROJECT_ROOT / "tests" / "fixtures"

L_KEY = "FIXTUREPROLINE-LFORMKEYAA-N"
D_KEY = "FIXTUREPROLINE-DFORMKEYAA-N"


def _reference_file(tmp_path: Path, **overrides) -> Path:
    doc = {
        "schema_version": 1,
        "source": "synthetic fixture",
        "retrieved_on": "2026-09-15",
        "entries": [
            {
                "base_name": "proline",
                "l_inchikey": L_KEY,
                "l_pubchem_cid": 1,
                "d_inchikey": D_KEY,
                "d_pubchem_cid": 2,
            }
        ],
    }
    doc.update(overrides)
    path = tmp_path / "label_reference.yaml"
    path.write_text(yaml.safe_dump(doc))
    return path


# --- label agreement: tri-state --------------------------------------------------------


def test_label_agreement_domain_is_tri_state():
    assert LABEL_AGREEMENT == ("disagrees", "agrees", "unresolved")


@pytest.mark.parametrize(
    "name,key,expected",
    [
        ("D-Proline", L_KEY, "disagrees"),  # labelled D, structure is L — the measured defect
        ("L-Proline", D_KEY, "disagrees"),
        ("D-Proline", D_KEY, "agrees"),
        ("L-Proline", L_KEY, "agrees"),
        ("d-proline", L_KEY, "disagrees"),  # prefix and base name are case-insensitive
        ("Proline", L_KEY, "unresolved"),  # no D-/L- prefix: the label asserts nothing
        ("D-Unlisted", L_KEY, "unresolved"),  # base name not in the reference
        ("D-Proline", "FIXTURENEITHER-NOTAKEYAA-N", "unresolved"),  # key matches neither
    ],
)
def test_label_agreement(tmp_path, name, key, expected):
    reference = load_label_reference(_reference_file(tmp_path))
    assert label_agreement(name, key, reference) == expected


def test_label_agreement_without_a_reference_is_unresolved_never_agrees():
    assert label_agreement("D-Proline", L_KEY, None) == "unresolved"


def test_reference_without_a_retrieval_date_is_rejected(tmp_path):
    with pytest.raises(LabelReferenceError, match="retrieved_on"):
        load_label_reference(_reference_file(tmp_path, retrieved_on=""))


def test_reference_entry_missing_a_key_is_rejected(tmp_path):
    path = _reference_file(tmp_path, entries=[{"base_name": "proline", "l_inchikey": L_KEY}])
    with pytest.raises(LabelReferenceError, match="d_inchikey"):
        load_label_reference(path)


# --- T13: generated columns --------------------------------------------------------------


def _labels_and_compounds(flags=(False, True, False)):
    keys = ["FIXTURECMPDAAA-FIXTUREKEY-N", "FIXTURECMPDAAB-FIXTUREKEY-N", L_KEY]
    labels = pd.Series(["yes", "unknown", "unknown"], index=keys)
    labels.index.name = "canonical_inchikey"
    compounds = pd.DataFrame(
        {
            "canonical_inchikey": keys,
            "name": ["Fixture Alpha", "Fixture Beta", "D-Proline"],
            "stereo_is_relative": list(flags),
        }
    )
    return labels, compounds


def test_generated_columns_follow_snapshot_label_in_the_written_sheet(tmp_path):
    assert GENERATED_COLUMNS == ("stereo_is_relative", "label_disagrees_with_key")
    labels, compounds = _labels_and_compounds()
    out = tmp_path / "w.csv"
    write_adjudication_worksheet(labels, compounds, out, label_reference=load_label_reference(_reference_file(tmp_path)))
    frame = pd.read_csv(out, dtype=str, keep_default_na=False)
    assert list(frame.columns) == list(WRITTEN_COLUMNS)
    assert list(WRITTEN_COLUMNS) == [
        "canonical_inchikey", "name", "snapshot_label",
        "stereo_is_relative", "label_disagrees_with_key",
        "adjudicated_label", "evidence_doi", "adjudicated_by", "adjudicated_on",
    ]
    by_key = frame.set_index("canonical_inchikey")
    assert by_key.loc["FIXTURECMPDAAB-FIXTUREKEY-N", "stereo_is_relative"] == "True"
    assert by_key.loc[L_KEY, "label_disagrees_with_key"] == "disagrees"
    assert by_key.loc["FIXTURECMPDAAA-FIXTUREKEY-N", "label_disagrees_with_key"] == "unresolved"


def test_a_stale_generated_value_is_overwritten_not_carried(tmp_path):
    """The falsification of the undeclared-column failure: a regenerated flag must win."""
    labels, compounds = _labels_and_compounds(flags=(False, False, False))
    out = tmp_path / "w.csv"
    write_adjudication_worksheet(labels, compounds, out)
    stale = pd.read_csv(out, dtype=str, keep_default_na=False)
    stale.loc[:, "stereo_is_relative"] = "True"  # stale: every row wrongly flagged on disk
    stale.loc[:, "label_disagrees_with_key"] = "disagrees"
    stale.loc[0, "adjudicated_label"] = "yes"  # human work that MUST survive
    stale.loc[0, "evidence_doi"] = "10.0000/fixture"
    stale.loc[0, "adjudicated_by"] = "FIXTURE"
    stale.to_csv(out, index=False)

    write_adjudication_worksheet(labels, compounds, out)
    after = pd.read_csv(out, dtype=str, keep_default_na=False)
    assert (after["stereo_is_relative"] == "False").all()
    assert (after["label_disagrees_with_key"] == "unresolved").all()
    for column in HUMAN_OWNED_COLUMNS[:3]:
        assert after.loc[0, column] == stale.loc[0, column], f"{column} was clobbered"


def test_a_legacy_sheet_without_generated_columns_loads_and_merges(tmp_path):
    labels, compounds = _labels_and_compounds()
    out = tmp_path / "w.csv"
    legacy = pd.DataFrame(
        {
            "canonical_inchikey": list(labels.index),
            "name": list(compounds["name"]),
            "snapshot_label": list(labels),
            "adjudicated_label": ["yes", "", ""],
            "evidence_doi": ["10.0000/fixture", "", ""],
            "adjudicated_by": ["FIXTURE", "", ""],
            "adjudicated_on": ["2026-09-15", "", ""],
        }
    )
    assert list(legacy.columns) == list(WORKSHEET_COLUMNS)
    legacy.to_csv(out, index=False)
    _read_worksheet(out)  # must not raise: generated columns are optional on read

    write_adjudication_worksheet(labels, compounds, out)
    after = pd.read_csv(out, dtype=str, keep_default_na=False)
    assert list(after.columns) == list(WRITTEN_COLUMNS)
    assert after.loc[0, "adjudicated_label"] == "yes"


def test_a_regenerated_sheet_round_trips_through_read_worksheet_unchanged(tmp_path):
    labels, compounds = _labels_and_compounds()
    out = tmp_path / "w.csv"
    write_adjudication_worksheet(labels, compounds, out)
    first = out.read_bytes()
    reread = _read_worksheet(out)
    assert list(reread.columns) == list(WRITTEN_COLUMNS)
    write_adjudication_worksheet(labels, compounds, out)
    assert out.read_bytes() == first


def test_t13_refuses_compounds_without_the_flag(tmp_path):
    labels, compounds = _labels_and_compounds()
    with pytest.raises(AdjudicationError, match="stereo_is_relative"):
        write_adjudication_worksheet(labels, compounds.drop(columns="stereo_is_relative"), tmp_path / "w.csv")


# --- T15: raise on a legacy sheet; carry the flag ----------------------------------------


def test_t15_raises_on_a_legacy_sheet_and_says_how_to_fix_it():
    """The committed fixture CSVs predate the flag, so they ARE legacy sheets."""
    with pytest.raises(AdjudicationError) as exc:
        adjudicate_pgp_labels(FIXTURES / "pgp_adjudication_filled.csv")
    message = str(exc.value)
    assert "stereo_is_relative" in message
    assert "write_adjudication_worksheet" in message
    # Case-insensitive: the assertion is about what the message TELLS the reviewer, not
    # how it is capitalised. The message says "PRESERVES every verdict, DOI and attribution".
    assert "preserv" in message.lower()


def test_t15_writes_the_flag_into_the_label_parquet(tmp_path):
    frame = pd.read_csv(FIXTURES / "pgp_adjudication_filled.csv", dtype=str, keep_default_na=False)
    frame.insert(3, "stereo_is_relative", ["True"] + ["False"] * (len(frame) - 1))
    sheet = tmp_path / "w.csv"
    frame.to_csv(sheet, index=False)
    out = tmp_path / "pgp_labels.parquet"
    adjudicate_pgp_labels(sheet, parquet_out=out)
    raw = pd.read_parquet(out, engine="pyarrow")
    assert raw["stereo_is_relative"].dtype == bool
    assert raw["stereo_is_relative"].tolist() == [True] + [False] * (len(frame) - 1)


# --- T10: refuse an unflagged frame ------------------------------------------------------


def test_t10_refuses_a_compounds_frame_without_the_flag(panel_ratified_path, fixture_dir):
    from chipsim.harmonize.ids import add_canonical_identity
    from chipsim.harmonize.pgp_label import barrier_panel_edges, pgp_substrate_label
    from chipsim.ingest.drugbank_snapshot import load_compounds, load_protein_edges

    snapshot = PROJECT_ROOT / "tests" / "fixtures" / "snapshot"
    compounds = add_canonical_identity(load_compounds(snapshot, min_rows=0))
    edges = barrier_panel_edges(load_protein_edges(snapshot, min_rows=0), panel_ratified_path)
    with pytest.raises(ValueError, match="stereo_is_relative"):
        pgp_substrate_label(compounds.drop(columns="stereo_is_relative"), edges, panel_ratified_path)
