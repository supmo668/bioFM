"""Every structure in the snapshot fixtures cites a public source — CTO ruling 2026-09-16.

The principal invariant (#120 §1) permits bare canonical structure identifiers in tracked
files — they are public identifiers, not DrugBank record content — on one condition: each
structure cites a public source, so its provenance is checkable rather than assumed.

The snapshot fixture TSVs are pinned to the dhimmel/drugbank schema and cannot carry an
inline citation, so the citations live in a sidecar, `tests/fixtures/snapshot/SOURCES.md`.

**The sidecar is only worth having if it cannot silently fall behind.** A citation file
that drifts the first time someone adds a fixture row is worse than none: it looks complete.
So this test extracts every InChI actually present in the fixture TSVs and asserts each one
appears in SOURCES.md with a PubChem CID and a retrieval date.

Matching is on the EXACT InChI string, not on the TSVs' own `inchikey` column: a new row
could carry a precomputed key that does not match its structure, and a citation keyed on
that column would vouch for the wrong molecule.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT_FIXTURES = PROJECT_ROOT / "tests" / "fixtures" / "snapshot"
SOURCES = SNAPSHOT_FIXTURES / "SOURCES.md"

#: One citation row: `| <exact InChI> | <PubChem CID> | <YYYY-MM-DD> |`, InChI in backticks.
_ROW = re.compile(r"^\|\s*`(InChI=[^`]+)`\s*\|\s*(\d+)\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|")


def _fixture_inchis() -> set[str]:
    found: set[str] = set()
    for tsv in sorted(SNAPSHOT_FIXTURES.glob("*.tsv")):
        with tsv.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle, delimiter="\t"):
                value = (row.get("inchi") or "").strip()
                if value:
                    found.add(value)
    return found


def _cited() -> dict[str, tuple[str, str]]:
    cited: dict[str, tuple[str, str]] = {}
    for line in SOURCES.read_text(encoding="utf-8").splitlines():
        match = _ROW.match(line.strip())
        if match:
            inchi, cid, retrieved = match.groups()
            cited[inchi] = (cid, retrieved)
    return cited


def test_the_fixtures_actually_contain_structures():
    """Anti-vacuity: an empty extraction would make the coverage test pass trivially."""
    assert len(_fixture_inchis()) >= 8


def test_every_fixture_structure_is_cited_with_a_pubchem_cid_and_date():
    missing = sorted(_fixture_inchis() - set(_cited()))
    assert not missing, (
        f"{len(missing)} fixture structure(s) have no entry in {SOURCES.name}: {missing}. "
        "Add each with its PubChem CID (looked up by exact InChI) and retrieval date."
    )


def test_every_citation_row_is_complete():
    cited = _cited()
    assert cited, f"{SOURCES.name} has no parseable citation rows"
    for inchi, (cid, retrieved) in cited.items():
        assert int(cid) > 0, f"non-positive CID for {inchi}"
        assert retrieved, f"no retrieval date for {inchi}"


def test_the_sidecar_cites_nothing_that_is_not_in_the_fixtures():
    """The reverse direction: a stale citation for a removed row is also drift."""
    stale = sorted(set(_cited()) - _fixture_inchis())
    assert not stale, f"{SOURCES.name} cites structures no fixture carries: {stale}"
