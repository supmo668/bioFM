"""T13's CLI entry point — the production caller `write_adjudication_worksheet` did not have.

The writer had roughly thirty call sites and every one was a test. T16's n8n export is descoped, so
the CLI is the only invocation path there was ever going to be, and it sits directly on the route to
the principal's 60-90 minute T14.

WHY THE ROSTER LOADER IS MONKEYPATCHED HERE, AND WHY THAT IS NOT A DODGE.

`load_poc_roster` enforces 20-40 entries. The fixture snapshot holds EIGHT compounds, so no roster
built from it can be valid, and a roster is `canonical_inchikey` + `name` + `evidence_doi` — a
NAME-BESIDE-STRUCTURE table, which is exactly what may not be committed. Editing the fixture TSVs is
barred too. So a tracked fixture that exercises the happy path cannot exist under the project's own
compliance rules.

What is under test here is the CLI WIRING — refuse without a roster, refuse when the roster and the
snapshot disagree, and emit exactly one row per roster entry. The roster VALIDATOR has its own tests
(`test_roster.py`), and substituting it keeps this file from depending on data it is forbidden to
fabricate. The keys used are read from the fixture snapshot at run time, never written down.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from chipsim import pipeline
from chipsim.ingest.drugbank_snapshot import load_compounds

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT_DIR = PROJECT_ROOT / "tests" / "fixtures" / "snapshot"
PANEL = PROJECT_ROOT / "configs" / "barrier_panel.yaml"
EXCLUSIONS = PROJECT_ROOT / "configs" / "unparseable_compounds.yaml"


def _fixture_keys() -> list[str]:
    """Canonical keys READ from the fixture snapshot, never hard-coded into this file."""
    from chipsim.harmonize.ids import add_canonical_identity_excluding

    compounds, _ = add_canonical_identity_excluding(
        load_compounds(SNAPSHOT_DIR, min_rows=0), preregistered=frozenset()
    )
    return list(compounds["canonical_inchikey"])


def _argv(tmp_path: Path, roster: Path, out: Path) -> list[str]:
    return [
        "adjudication-worksheet",
        "--raw-dir",
        str(SNAPSHOT_DIR),
        "--roster",
        str(roster),
        "--panel",
        str(PANEL),
        "--out",
        str(out),
        "--exclusions",
        str(EXCLUSIONS),
        "--yes",
    ]


def test_the_writer_now_has_a_production_caller():
    """The defect this entry point closes, asserted directly: a heavily-tested writer that a human
    cannot run is a mechanism with no caller, which is this project's signature failure."""
    assert "adjudication-worksheet" in pipeline._HANDLERS
    assert pipeline._HANDLERS["adjudication-worksheet"] is pipeline._cmd_adjudication_worksheet


def test_it_REFUSES_when_no_roster_exists(tmp_path, capsys):
    """The state the project is actually in: T18 is human-owned and no roster exists.

    Emitting a worksheet over whatever the snapshot happened to contain would hand the principal
    the WRONG ROWS to spend 60-90 minutes on — the cost T13's never-clobber rule already exists to
    protect.
    """
    out = tmp_path / "pgp_adjudication.csv"
    code = pipeline.main(_argv(tmp_path, tmp_path / "absent.csv", out))

    assert code == 2
    assert "no roster at" in capsys.readouterr().err
    assert not out.exists(), "nothing may be written when the row set is unratified"


def test_it_REFUSES_when_the_roster_names_a_key_the_snapshot_cannot_label(
    tmp_path, monkeypatch, capsys
):
    """The roster SELECTS; it never invents. A key the labeller did not produce is two
    human-ratified inputs disagreeing, and it must surface rather than silently shorten the sheet.
    """
    roster = tmp_path / "roster.csv"
    roster.write_text("canonical_inchikey,name,evidence_doi\n")
    ghost = "AAAAAAAAAAAAAA-BBBBBBBBBB-N"  # synthetic, in no snapshot
    monkeypatch.setattr(
        pipeline_roster_module(),
        "load_poc_roster",
        lambda *a, **k: pd.DataFrame({"canonical_inchikey": [*_fixture_keys()[:2], ghost]}),
    )

    out = tmp_path / "pgp_adjudication.csv"
    code = pipeline.main(_argv(tmp_path, roster, out))

    assert code == 2
    assert "no snapshot label" in capsys.readouterr().err
    assert not out.exists()


def test_it_emits_exactly_one_row_per_roster_entry(tmp_path, monkeypatch):
    """T13's done-condition, on the half that does not require a 20-40 roster: the sheet carries
    one row per roster entry and no more. The size rule belongs to `load_poc_roster` and is tested
    where it lives."""
    roster = tmp_path / "roster.csv"
    roster.write_text("canonical_inchikey,name,evidence_doi\n")
    chosen = _fixture_keys()[:3]
    monkeypatch.setattr(
        pipeline_roster_module(),
        "load_poc_roster",
        lambda *a, **k: pd.DataFrame({"canonical_inchikey": chosen}),
    )

    out = tmp_path / "pgp_adjudication.csv"
    assert pipeline.main(_argv(tmp_path, roster, out)) == 0

    sheet = pd.read_csv(out)
    assert len(sheet) == len(chosen)
    assert set(sheet["canonical_inchikey"]) == set(chosen)
    for column in ("adjudicated_label", "evidence_doi", "adjudicated_by", "adjudicated_on"):
        assert sheet[column].isna().all(), f"{column} must be empty for the human to fill"


@pytest.fixture(autouse=True)
def _fixture_sized_snapshot(monkeypatch):
    """The production row FLOOR (1000) is correct and must not gain a CLI override.

    `load_compounds` refuses a frame below the floor because "an almost-empty frame passes every
    column assertion" (defect 9). The fixture snapshot has eight rows, so exercising the CLI against
    it requires relaxing the floor HERE — never in the command, where a `--min-rows` flag would be
    exactly the escape the floor exists to prevent.
    """
    import chipsim.ingest.drugbank_snapshot as snapshot_module

    real_compounds = snapshot_module.load_compounds
    real_edges = snapshot_module.load_protein_edges
    monkeypatch.setattr(
        snapshot_module,
        "load_compounds",
        lambda path, min_rows=0: real_compounds(path, min_rows=0),
    )
    monkeypatch.setattr(
        snapshot_module,
        "load_protein_edges",
        lambda path, min_rows=0: real_edges(path, min_rows=0),
    )


def pipeline_roster_module():
    """The module object the handler imports `load_poc_roster` FROM.

    Patched at its source rather than on `pipeline`, because the handler imports it inside the
    function — patching a name the handler never reads is the shape of a test that cannot fail.
    """
    import chipsim.harmonize.roster as roster_module

    return roster_module
