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
import subprocess
from pathlib import Path
from typing import Any

import pytest
import yaml

from chipsim.harmonize.roster import load_poc_roster

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


# --- configs/ · the invariant's CLASS, not one instance (principal rulings, rows 36 + 39) ------
#
# #120 §1 permits a bare canonical structure identifier in a tracked file — it is a public
# identifier, not DrugBank record content — ON ONE CONDITION: its provenance is CHECKABLE.
#
# This gate has now been narrower than that invariant TWICE, and both times along a different
# axis than the fix before it:
#   * it globbed one DIRECTORY (`tests/fixtures/snapshot/`), so `configs/` went unchecked;
#   * widened, it globbed one EXTENSION (`*.yaml`), so the first `.csv` to land went unchecked —
#     and the anti-vacuity count globbed `*.yaml` too, making the check that exists to prove the
#     gate is not vacuous blind to exactly what the gate was blind to.
#
# So the rule below is written as a PROPERTY and FAILS CLOSED, rather than as a list of places:
#
#   DISCOVERY     every TRACKED file under this project's configs/, asked of git rather than the
#                 filesystem, scanned as text for structure-shaped tokens.
#   FAIL CLOSED   a file that contains such a token and that the gate cannot STRUCTURALLY parse
#                 FAILS, naming the file and the missing parser. Unknown format is not compliant.
#                 Unparseable is not compliant. A missing reading is never an absence of
#                 structures (r2.34 two-predicate rule: the safe direction is INCLUDE).
#   ANTI-VACUITY  per file and DERIVED: wherever the text scan found tokens, the parser must find
#                 at least as many distinct identifiers IN THAT SAME FILE. No bare floor — a
#                 constant goes stale, and it cannot localise which parser went blind.
#   SATISFACTION  cite-by-reference, scoped: a structure is satisfied by a citation in its OWN
#                 mapping, or by the SAME identifier (exact equality) in another tracked file
#                 under THIS configs/ tree whose own mapping cites. Not repo-wide — repo-wide
#                 would let a test fixture vouch for production config.
#
# THE TEXT SCAN IS AN ALARM; THE PARSER IS THE INSTRUMENT. The scan says "look here" and never
# says "this is fine". Conflating them would re-create the defect one level up, so they are kept
# in separate functions deliberately and this comment is why.
#
# PARSE, NEVER GREP BY LINE. `poc_compounds.yaml` is inline flow style, so every key sits
# mid-line and a line-anchored pattern matches nothing and reports zero, silently. Two agents
# independently produced OPPOSITE wrong verdicts on that exact file that way — a false violation
# and a false absence.

_INCHIKEY = re.compile(r"[A-Z]{14}-[A-Z]{10}-[A-Z]")
_CITATION_KEYS = ("evidence_doi", "pubchem_cid", "citation", "source", "doi")


def _blankish(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def _tracked_config_files() -> list[Path]:
    """Every tracked file under this project's `configs/`. Asked of git, not of the filesystem.

    An untracked file publishes nothing, and a glob would also miss a tracked file whose name
    nobody predicted — which is how this gate was wrong twice.

    `git ls-files` is run WITH `cwd=PROJECT_ROOT`, so its output is relative to PROJECT_ROOT and
    is joined to it. Joining to the repo root instead silently produced paths that do not exist,
    and combined with a swallowed read error that made every file scan as EMPTY — the gate passed
    while asserting nothing. Hence `--full-name` is deliberately NOT used: one anchor, named here.
    """
    out = subprocess.run(
        ["git", "ls-files", "-z", "--", "configs"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    paths = [PROJECT_ROOT / rel for rel in out.split("\0") if rel]
    assert paths, "git ls-files found no tracked files under configs/ — discovery is broken"
    return paths


def _scanned_tokens(path: Path) -> set[str]:
    """DISCOVERY ONLY. Structure-shaped tokens in the raw bytes. Never evidence of compliance.

    RAISES rather than returning an empty set when the file cannot be read. An unreadable file is
    an unknown, and this gate's whole correction is that an unknown is NOT an absence: swallowing
    the error here is what made a wrong path look like a clean file and passed the suite while the
    gate asserted nothing at all.
    """
    return set(_INCHIKEY.findall(path.read_text(encoding="utf-8", errors="replace")))


def _parse_yaml(path: Path) -> list[tuple[str, dict, str]]:
    found: list[tuple[str, dict, str]] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if isinstance(value, str) and _INCHIKEY.fullmatch(value.strip()):
                    found.append((value.strip(), node, key))
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(yaml.safe_load(path.read_text(encoding="utf-8")))
    return found


def _parse_csv(path: Path) -> list[tuple[str, dict, str]]:
    found: list[tuple[str, dict, str]] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            for key, value in row.items():
                if isinstance(value, str) and _INCHIKEY.fullmatch(value.strip()):
                    found.append((value.strip(), dict(row), key))
    return found


#: Structural parsers by suffix. A suffix absent here FAILS CLOSED when tokens are present.
_PARSERS = {".yaml": _parse_yaml, ".yml": _parse_yaml, ".csv": _parse_csv}


def _cited_in_own_mapping(mapping: dict, key: str) -> bool:
    """Prefix-aware first: `l_inchikey` is satisfied by `l_pubchem_cid`, NEVER by `d_pubchem_cid`.

    A citation keyed to the other enantiomer would vouch for the wrong molecule — the same trap
    the snapshot gate avoids by matching the exact InChI rather than a key column.
    """
    stem = key[: -len("inchikey")] if key.endswith("inchikey") else ""
    if stem and any(not _blankish(mapping.get(f"{stem}{c}")) for c in _CITATION_KEYS):
        return True
    return any(not _blankish(mapping.get(c)) for c in _CITATION_KEYS)


def _survey() -> tuple[dict[Path, set[str]], dict[Path, list[tuple[str, dict, str]]], list[str]]:
    """(scanned tokens per file, parsed structures per file, fail-closed complaints)."""
    scanned: dict[Path, set[str]] = {}
    parsed: dict[Path, list[tuple[str, dict, str]]] = {}
    closed: list[str] = []
    for path in sorted(_tracked_config_files()):
        # FORMAT AND READABILITY ARE CHECKED BEFORE THE SCAN, AND THE SCAN GATES NOTHING
        # (approvals row 65). This loop used to open with `tokens = _scanned_tokens(path)` and
        # `if not tokens: continue`, so the parser only ever ran where the regex had already
        # fired — making the alarm the gate, in a file whose own header says "THE TEXT SCAN IS AN
        # ALARM; THE PARSER IS THE INSTRUMENT. The scan ... never says 'this is fine'." In practice
        # it said exactly that, by silence. Two measured escapes: a YAML line-continuation folded
        # an identifier past the line-anchored regex, and a tracked `.csv.gz` carrying every
        # identifier produced no token at all. Both reported 8 passed.
        # EXEMPT BY MEASURED EMPTINESS, never by name. A zero-byte file PROVABLY carries no
        # identifier, so this cannot become a hole: the moment anything is written into
        # `configs/.gitkeep` it stops being empty and falls through to the checks below. A name
        # allow-list would have exempted the file forever regardless of its contents, which is the
        # shape of exemption this gate has already been bitten by twice.
        try:
            if path.stat().st_size == 0:
                continue
        except OSError as exc:
            closed.append(f"{path.name}: cannot stat ({type(exc).__name__}) — NOT compliant")
            continue

        parser = _PARSERS.get(path.suffix.lower())
        if parser is None:
            closed.append(
                f"{path.name}: no structural parser for '{path.suffix}' — an unreadable format is "
                "NOT compliance, whether or not the text scan found anything in it"
            )
            continue
        try:
            # STRICT utf-8, no errors="replace": "cannot read this as text" must not decay into
            # "no structures here". That substitution is what let a gzip of the adjudication file
            # pass as clean.
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError) as exc:
            closed.append(
                f"{path.name}: not readable as UTF-8 text ({type(exc).__name__}) — cannot be "
                "checked, therefore NOT compliant"
            )
            continue
        # Recorded for EVERY parseable file, including an empty set, so the per-file anti-vacuity
        # comparison below covers files the scan is blind to rather than skipping them.
        scanned[path] = set(_INCHIKEY.findall(text))
        try:
            parsed[path] = parser(path)
        # BLE001 is exempted deliberately: breadth IS the requirement. Whatever a parser
        # raises, the file must FAIL and be NAMED — this records and fails, it never
        # swallows. A narrower clause would let an unanticipated error type escape as
        # something other than 'this file is unchecked', which is the defect being fixed.
        except Exception as exc:  # noqa: BLE001 — unparseable is NOT compliant
            closed.append(f"{path.name}: {type(exc).__name__} while parsing — {exc}"[:200])
    return scanned, parsed, closed


def test_every_structure_bearing_config_can_actually_be_parsed():
    """FAIL CLOSED. Unknown format is not compliant; unparseable is not compliant.

    Without this, the next format nobody listed is skipped silently and reported as compliance —
    which is exactly how a `.csv` carrying 26 identifiers landed under a gate that globbed
    `*.yaml` and still passed.
    """
    _, _, closed = _survey()
    assert not closed, (
        "structure-bearing config(s) the gate cannot read: "
        + "; ".join(closed)
        + ". Add a structural parser, or the gate is asserting nothing about them."
    )


def test_the_configs_gate_actually_covers_the_roster_it_governs():
    """ABSOLUTE anti-vacuity for the configs half (approvals row 65).

    The per-file check below is genuinely derived, but it degenerates silently to ZERO FILES:
    `scanned` empty => nothing compared => green. Measured: `git rm` the four structure-bearing
    configs and all eight tests passed. `_tracked_config_files`' own `assert paths` only proves
    *some* tracked file exists under `configs/`, not that any bears a structure.

    The floor is DERIVED from the roster rather than written as a constant, so it cannot go stale
    the way a bare `>= 100` would: every canonical key the PoC roster declares must be a structure
    this gate actually parsed. A renamed column, a moved roster or a format change now fails here
    instead of reporting compliance.
    """
    _, parsed, _ = _survey()
    seen = {structure for structures in parsed.values() for structure, _, _ in structures}
    frame = load_poc_roster(CONFIGS / "poc_compounds.yaml")
    assert "canonical_inchikey" in frame.columns, (
        "the roster loader returned no canonical_inchikey column — this floor would compare "
        "against an empty set and assert nothing, which is the defect it exists to close"
    )
    roster = {str(k).strip() for k in frame["canonical_inchikey"]}
    assert roster, "the PoC roster declares no keys — the floor itself would be vacuous"
    missing = roster - seen
    assert not missing, (
        f"{len(missing)} of the roster's {len(roster)} canonical keys are not covered by the "
        "configs identifier gate. The gate is asserting less than the project's own roster "
        "declares, which is the state 'all eight tests pass over zero files' produced."
    )


def test_the_parser_sees_every_structure_the_text_scan_found():
    """Anti-vacuity, DERIVED per file — the test that localises a blind parser.

    A bare floor (`>= 100`) goes stale when a file lands and hides per-file blindness in
    aggregate: one file's 88 identifiers would satisfy it while another contributed nothing.
    Comparing each file against its own scan is self-calibrating and names the culprit.
    """
    scanned, parsed, _ = _survey()
    blind = {
        path.name: (len(tokens), len({s for s, _, _ in parsed.get(path, [])}))
        for path, tokens in scanned.items()
        if len({s for s, _, _ in parsed.get(path, [])}) < len(tokens)
    }
    assert not blind, (
        f"parser(s) saw fewer distinct structures than the raw text scan did: {blind} "
        "(file: scanned, parsed). A parser that cannot see its own file's shape reports zero and "
        "makes this gate vacuous — inline flow style is the known case."
    )


def test_every_config_structure_has_checkable_provenance():
    """#120 §1: provenance must be CHECKABLE, not adjacent.

    Cite-by-reference, scoped to THIS `configs/` tree by exact identifier equality. Repo-wide
    resolution is refused on purpose: a test fixture must not vouch for production config.
    """
    _, parsed, _ = _survey()
    citing: set[str] = {
        structure
        for structures in parsed.values()
        for structure, mapping, key in structures
        if _cited_in_own_mapping(mapping, key)
    }
    uncited = sorted(
        f"{path.name}:{key}"
        for path, structures in parsed.items()
        for structure, mapping, key in structures
        if not _cited_in_own_mapping(mapping, key) and structure not in citing
    )
    assert not uncited, (
        f"{len(uncited)} structure(s) under configs/ have no checkable provenance — neither a "
        f"citation in their own mapping nor the same identifier cited in another tracked file "
        f"under configs/: {uncited[:10]}."
    )


def test_cite_by_reference_terminates_in_a_concrete_citation():
    """The chain must not be circular: a structure satisfied BY REFERENCE ends at a real citation.

    REWRITTEN (approvals row 65). The previous version could not fail. Both of its assertions were
    tautologies: it compared `parsed`'s keys against a set built from `_tracked_config_files()` —
    the same function `_survey` takes them from — and its inner assertion was implied by its own
    guard, because `_cited_in_own_mapping` returns True only via a branch that makes one of the
    disjuncts true. Blanking all 26 `evidence_doi` values in `poc_compounds.yaml` left it GREEN
    with zero citations anywhere under `configs/`, while the provenance test correctly failed.

    This asserts the property the docstring claimed instead: for every structure that is NOT cited
    in its own mapping, the file that vouches for it must be one this gate actually surveyed, and
    the vouching mapping must carry a concrete non-blank citation. The `key.endswith("inchikey")`
    escape hatch is gone — it was what made the old assertion unfalsifiable.
    """
    scanned, parsed, _ = _survey()

    #: structure -> the files whose own mapping cites it
    vouchers: dict[str, list[Path]] = {}
    for path, structures in parsed.items():
        for structure, mapping, key in structures:
            if _cited_in_own_mapping(mapping, key):
                vouchers.setdefault(structure, []).append(path)

    by_reference = [
        (path, structure, key)
        for path, structures in parsed.items()
        for structure, mapping, key in structures
        if not _cited_in_own_mapping(mapping, key) and structure in vouchers
    ]

    for path, structure, key in by_reference:
        for voucher in vouchers[structure]:
            assert voucher in scanned, (
                f"{path.name}:{key} is satisfied by {voucher.name}, which this gate never "
                "surveyed — a voucher outside the gate is an unchecked claim"
            )
            concrete = [
                (mapping, vkey)
                for vstructure, mapping, vkey in parsed[voucher]
                if vstructure == structure and _cited_in_own_mapping(mapping, vkey)
            ]
            assert concrete, f"{voucher.name} was recorded as vouching for {key} but carries no row"
            for mapping, vkey in concrete:
                stem = vkey[: -len("inchikey")] if vkey.endswith("inchikey") else ""
                keys = [f"{stem}{c}" for c in _CITATION_KEYS] + list(_CITATION_KEYS)
                assert any(not _blankish(mapping.get(c)) for c in keys), (
                    f"{voucher.name}:{vkey} vouches for {path.name}:{key} but cites nothing "
                    "concrete — the chain does not terminate"
                )

    # Anti-vacuity: if nothing is satisfied by reference the loop above asserted nothing, and this
    # test would pass on an empty tree exactly as its predecessor did.
    if not by_reference:
        pytest.skip(
            "no structure under configs/ is currently satisfied BY REFERENCE (every one is cited "
            "in its own mapping), so the chain property has nothing to check — reported as a skip "
            "rather than passed, because a silent pass is what the rewritten test exists to stop"
        )
