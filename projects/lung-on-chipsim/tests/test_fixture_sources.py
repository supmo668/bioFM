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
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT_FIXTURES = PROJECT_ROOT / "tests" / "fixtures" / "snapshot"
SOURCES = SNAPSHOT_FIXTURES / "SOURCES.md"
CONFIGS = PROJECT_ROOT / "configs"

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


# --- configs/ · the same invariant, widened (principal ruling 2026-10-23) -----------
#
# #120 §1 permits a bare canonical structure identifier in a tracked file — it is a public
# identifier, not DrugBank record content — ON ONE CONDITION: each structure cites a public
# source. The snapshot gate above enforces that for `tests/fixtures/snapshot/*.tsv`. It was
# NARROWER THAN THE INVARIANT IT ENFORCES: the identifiers under `configs/` satisfied the
# condition by curation and were checked by nothing.
#
# Two deliberate choices, both of them rulings rather than taste:
#
# 1. NO SCOPE REGISTRY. A declared list of in-scope files is the shape E-23 closed on, so this
#    globs and asserts per structure instead. A file added to `configs/` is covered the moment
#    it lands; nobody has to remember to register it.
#
# 2. PARSE, NEVER GREP BY LINE. `poc_compounds.yaml` is inline flow style —
#    `- {canonical_inchikey: ..., name: ..., evidence_doi: ...}` — so EVERY key sits mid-line
#    and a line-anchored pattern matches nothing and reports zero, silently. Two agents
#    independently produced opposite wrong verdicts on this exact file that way: a false
#    violation and a false absence. `yaml.safe_load` is the fix, and this comment is the reason
#    it must stay.
#
# The two files cite differently on purpose — `evidence_doi` beside the key, or `*_pubchem_cid`
# paired to `*_inchikey` by prefix — so the gate accepts any of the mechanisms rather than
# assuming one vocabulary. It checks the public-source condition ONLY: pairing a name with a
# structure is permitted (principal-curated input, approvals row 33) and is not this gate's
# business.

_INCHIKEY = re.compile(r"^[A-Z]{14}-[A-Z]{10}-[A-Z]$")
#: Any one of these, in the mapping that carries the identifier, satisfies the condition.
_CITATION_KEYS = ("evidence_doi", "pubchem_cid", "citation", "source", "doi")


def _is_identifier(value: Any) -> bool:
    return isinstance(value, str) and bool(_INCHIKEY.match(value.strip()))


def _cites(mapping: dict, key: str) -> bool:
    """True when `key`'s structure has a public-source pointer in its own mapping.

    Prefix-aware first, so `l_inchikey` is satisfied by `l_pubchem_cid` and NOT by `d_pubchem_cid`
    — a citation keyed to the other enantiomer would vouch for the wrong molecule, which is the
    same trap the snapshot gate avoids by matching on the exact InChI rather than a key column.
    """
    stem = key[: -len("inchikey")] if key.endswith("inchikey") else ""
    if stem:
        for c in _CITATION_KEYS:
            if not _blankish(mapping.get(f"{stem}{c}")):
                return True
    return any(not _blankish(mapping.get(c)) for c in _CITATION_KEYS)


def _blankish(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def _uncited_structures() -> list[str]:
    """Every identifier under `configs/` whose own mapping carries no public-source pointer."""
    offenders: list[str] = []

    def walk(node: Any, where: str) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if _is_identifier(value) and not _cites(node, key):
                    offenders.append(f"{where}:{key}")
                walk(value, f"{where}.{key}")
        elif isinstance(node, list):
            for i, item in enumerate(node):
                walk(item, f"{where}[{i}]")

    for path in sorted(CONFIGS.rglob("*.yaml")):
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError:  # a malformed config is another test's business
            continue
        walk(doc, path.relative_to(PROJECT_ROOT).as_posix())
    return offenders


def _config_structure_count() -> int:
    total = 0

    def walk(node: Any) -> None:
        nonlocal total
        if isinstance(node, dict):
            for value in node.values():
                if _is_identifier(value):
                    total += 1
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    for path in sorted(CONFIGS.rglob("*.yaml")):
        try:
            walk(yaml.safe_load(path.read_text(encoding="utf-8")))
        except yaml.YAMLError:
            continue
    return total


def test_configs_actually_contain_structures():
    """Anti-vacuity, and it is the test that would have caught both agents' error.

    A line-anchored implementation of this gate returns zero here and every assertion below
    passes trivially. The count is asserted against the measured population so that a parser
    that sees nothing FAILS instead of reporting compliance.
    """
    assert _config_structure_count() >= 100, (
        "fewer structures found under configs/ than are known to be there (26 in the PoC roster, "
        "88 in the label-structure reference). A parser that cannot see inline flow style reports "
        "zero and makes this gate vacuous."
    )


def test_every_config_structure_cites_a_public_source():
    uncited = _uncited_structures()
    assert not uncited, (
        f"{len(uncited)} structure(s) under configs/ carry no public-source pointer in their own "
        f"mapping: {uncited[:10]}. #120 §1 permits a bare canonical identifier in a tracked file "
        "only when its provenance is checkable — add evidence_doi, or a prefix-matched "
        "*_pubchem_cid, beside the structure."
    )
