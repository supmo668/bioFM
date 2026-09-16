"""Downstream honouring of `stereo_is_relative` — principal ruling 2026-09-15 (CTO #122 §0).

The ruling: /s2 (relative-stereo) input is keyed stereo-free and flagged, and "the flag
is not decoration" — downstream selection must be able to act on it. This file pins the
parts that do not touch human-owned artefacts:

  - `relative_stereo_keys` — which canonical keys carry at least one relative-stereo
    member, refusing a frame that predates the re-key rather than reporting "none";
  - T18 roster validation — a human-written roster naming a flagged key is REJECTED
    loudly (never silently filtered), unless the caller explicitly allows it: "a
    diversity stratum cannot rest on identities the source leaves unspecified";
  - T5a persistence — the persisted column tuple is pinned as a LITERAL. The previous
    test compared against the tuple's own symbol, so adding `stereo_is_relative` broke
    nothing; that is how a silently-dropped flag would also have passed.

All keys and DOIs below are SYNTHETIC — no compound data.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from chipsim.harmonize.ids import relative_stereo_keys
from chipsim.harmonize.roster import RosterValidationError, load_poc_roster
from chipsim.ingest.drugbank_snapshot import PERSISTED_COMPOUND_COLUMNS


def _synthetic_key(i: int) -> str:
    return f"SYNTHETIC{i:05d}AA-UHFFFAOYSA-N"


def _roster(tmp_path: Path, n: int = 20) -> tuple[Path, list[str]]:
    keys = [_synthetic_key(i) for i in range(n)]
    lines = ["compounds:"]
    for i, key in enumerate(keys):
        lines += [
            f"  - canonical_inchikey: {key}",
            f"    name: synthetic compound {i}",
            f"    evidence_doi: 10.0000/synthetic.{i}",
        ]
    path = tmp_path / "poc_compounds.yaml"
    path.write_text("\n".join(lines) + "\n")
    return path, keys


# --- relative_stereo_keys ------------------------------------------------------------


def test_relative_stereo_keys_returns_keys_with_any_flagged_member():
    frame = pd.DataFrame(
        {
            "canonical_inchikey": ["K-A", "K-A", "K-B", "K-C"],
            "stereo_is_relative": [False, True, False, False],
        }
    )
    assert relative_stereo_keys(frame) == frozenset({"K-A"})


def test_relative_stereo_keys_refuses_a_frame_without_the_flag():
    """A frame from before the re-key must not read as 'no relative-stereo compounds'."""
    with pytest.raises(ValueError, match="stereo_is_relative"):
        relative_stereo_keys(pd.DataFrame({"canonical_inchikey": ["K-A"]}))


# --- T18 roster ------------------------------------------------------------------------


def test_roster_naming_a_relative_stereo_key_is_rejected(tmp_path):
    path, keys = _roster(tmp_path)
    with pytest.raises(RosterValidationError, match="relative") as exc:
        load_poc_roster(path, relative_stereo_keys={keys[3], "NOT-IN-ROSTER-N"})
    assert keys[3] in str(exc.value)
    assert "NOT-IN-ROSTER-N" not in str(exc.value)


def test_roster_relative_stereo_rejection_is_overridable_explicitly(tmp_path):
    path, keys = _roster(tmp_path)
    frame = load_poc_roster(path, relative_stereo_keys={keys[3]}, allow_relative_stereo=True)
    assert len(frame) == 20


def test_roster_without_relative_stereo_keys_is_unchanged(tmp_path):
    path, _ = _roster(tmp_path)
    assert len(load_poc_roster(path)) == 20


# --- T18 roster REPORTS label disagreements (CTO #126 §3; QG F-06) -------------------------


def test_roster_reports_entries_whose_label_contradicts_their_key(tmp_path):
    """#126 §3: unlike a relative-stereo key, a label disagreement does not make the identity
    wrong — the key is right and the name is wrong — so the roster REPORTS it (listing) and does
    NOT reject. A T18 roster naming "D-Proline" on an L structure must surface, not pass silently.
    """
    from chipsim.harmonize.label_reference import load_label_reference
    from chipsim.harmonize.roster import roster_label_disagreements

    l_key, d_key = "FIXTUREPROLINE-LFORMKEYAA-N", "FIXTUREPROLINE-DFORMKEYAA-N"
    ref = tmp_path / "ref.yaml"
    ref.write_text(
        "retrieved_on: '2026-09-16'\nsource: synthetic\nentries:\n"
        f"- base_name: proline\n  l_inchikey: {l_key}\n  d_inchikey: {d_key}\n"
    )
    frame = pd.DataFrame(
        {
            "canonical_inchikey": [l_key, d_key, "SYNTHETIC00001AA-UHFFFAOYSA-N"],
            "name": ["D-Proline", "D-Proline", "synthetic compound"],
            "evidence_doi": ["10.0/a", "10.0/b", "10.0/c"],
        }
    )
    report = roster_label_disagreements(frame, load_label_reference(ref))
    assert report == [(l_key, "D-Proline")]


def test_roster_label_report_without_a_reference_reports_nothing_rather_than_guessing():
    from chipsim.harmonize.roster import roster_label_disagreements

    frame = pd.DataFrame(
        {"canonical_inchikey": ["K-N"], "name": ["D-Proline"], "evidence_doi": ["10.0/a"]}
    )
    assert roster_label_disagreements(frame, None) == []


# --- T5a persisted schema, pinned as a literal -------------------------------------------


def test_persisted_compound_columns_are_pinned_literally():
    assert PERSISTED_COMPOUND_COLUMNS == (
        "canonical_inchikey",
        "stereo_is_relative",
        "drugbank_id",
        "name",
        "type",
        "groups",
        "atc_codes",
        "inchi",
        "inchikey",
    )
