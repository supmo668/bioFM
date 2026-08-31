"""Barrier-panel accession verification — build-plan T19.

T8's r1 done-condition was pure attestation ("you have personally opened seven
UniProt pages"), which left the barrier panel's only control unverifiable
(defect 19). This module is T8's checkable surrogate: for every entry it asserts
that the accession resolves at UniProt, that the organism is human (taxonId
9606), and that the primary gene name equals the entry's `symbol`.

Marked `network`. Deselect with `-m "not network"`; CI runs it explicitly.

**This does not ratify anything.** Passing here means the accessions denote the
human proteins they claim to. Whether the panel is the RIGHT panel for airway
epithelium is a biological claim, and stays human-owned in T8.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.network

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_DIR = PROJECT_ROOT / "tests" / "fixtures"
LIVE_PANEL = PROJECT_ROOT / "configs" / "barrier_panel.yaml"

UNIPROT_URL = "https://rest.uniprot.org/uniprotkb/{acc}.json"
HUMAN_TAXON_ID = 9606
REQUEST_TIMEOUT = 30


def _load_panel(path: Path) -> list[dict]:
    return yaml.safe_load(path.read_text())["panel"]


def _fetch(acc: str) -> dict:
    import requests

    response = requests.get(UNIPROT_URL.format(acc=acc), timeout=REQUEST_TIMEOUT)
    assert response.status_code == 200, (
        f"UniProt accession {acc} did not resolve (HTTP {response.status_code})"
    )
    return response.json()


def _primary_gene_symbol(record: dict) -> str | None:
    """UniProt's primary gene name, or None if the record carries no gene block."""
    genes = record.get("genes") or []
    if not genes:
        return None
    return (genes[0].get("geneName") or {}).get("value")


def _check_entry(entry: dict) -> None:
    record = _fetch(entry["uniprot"])

    taxon = (record.get("organism") or {}).get("taxonId")
    assert taxon == HUMAN_TAXON_ID, (
        f"{entry['symbol']} ({entry['uniprot']}) is taxonId {taxon}, not human "
        f"({HUMAN_TAXON_ID}). A non-human accession silently empties the join."
    )

    symbol = _primary_gene_symbol(record)
    assert symbol == entry["symbol"], (
        f"accession {entry['uniprot']} is gene {symbol!r}, but the panel calls it "
        f"{entry['symbol']!r} — the panel names a different protein than it thinks."
    )


@pytest.mark.parametrize(
    "entry",
    _load_panel(FIXTURE_DIR / "barrier_panel_ratified.yaml"),
    ids=lambda e: e["symbol"],
)
def test_t19_fixture_panel_accessions_are_correct(entry):
    """T19's done-condition, first half: passes against the ratified fixture."""
    _check_entry(entry)


def test_t19_detects_a_valid_but_wrong_human_accession():
    """T19's done-condition, second half: FAILS when one accession is mutated to a
    valid-but-wrong HUMAN accession.

    This is the falsification that matters. A malformed accession would be caught
    by a 404 — but the real hazard is a well-formed human accession for the wrong
    protein, which resolves cleanly and silently empties the downstream join.
    P04637 (TP53) is human and real, so only the gene-symbol assertion can catch it.
    """
    wrong = {
        "symbol": "ABCB1",
        "uniprot": "P04637",  # real, human, and definitively NOT ABCB1
        "alias": "deliberately wrong",
        "face": "apical",
    }
    with pytest.raises(AssertionError, match="different protein"):
        _check_entry(wrong)


@pytest.mark.skipif(not LIVE_PANEL.exists(), reason="configs/barrier_panel.yaml absent")
@pytest.mark.parametrize(
    "entry",
    _load_panel(LIVE_PANEL) if LIVE_PANEL.exists() else [],
    ids=lambda e: e["symbol"],
)
def test_t19_live_panel_accessions_are_correct(entry):
    """The same check against the live config — this is what T8 must pass.

    It runs against the DRAFT too, so a bad accession is caught before a human
    spends T8's ten minutes on it.
    """
    _check_entry(entry)
