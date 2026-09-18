"""The DrugBank record-content guard — principal invariant (CTO #120 §1), scope and
exclusions ruled in #122 §3, #122 §5 and the CTO rulings of 2026-09-16.

**The invariant.** The project does not redistribute DrugBank RECORD CONTENT: real
accessions, DrugBank-coined titles, and above all the ASSOCIATION of either with a
structure. A bare canonical structure identifier is not record content.

**Scope: the whole repository.** The previous scan ran `git ls-files` from the PROJECT
root, so it had only ever seen `projects/lung-on-chipsim/` — `workstreams/` and `.claude/`
were never in scope, which is how a tracked merge report came to carry 89 real accessions.

**The complete exclusion set (nothing else):**
  - `.claude/usr/**/dispatches/` — coordination records; redacting a sent message falsifies
    the audit trail of the rulings it carries (#122 §3);
  - the sanctioned exclusion ledger pair (#120 §4) — which may carry accessions, but not an
    accession ASSOCIATED WITH A STRUCTURE.

**The approval log is IN scope.** It was excluded by name until the CTO reversed that
ruling (2026-09-16): a log row may be corrected in place when the correction is disclosed in
the row, so an exclusion would mean the guard takes a "corrected" claim on trust. It was
scanned clean before the exclusion was removed.

Accessions below are ASSEMBLED at runtime, never written literally: this file is itself in
scope, and a literal real accession would be a self-inflicted hit.
"""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

import pytest

from chipsim.guards.record_content import (
    THIS_PROJECT,
    _is_readable,
    failing_undeclared,
    path_owner,
    recognised_owners,
    undeclared_report,
    undecodable_unallowed,
)
from chipsim.guards.record_content import ContentPolicy as _rc_policy
from chipsim.guards.record_content import nothing_is_content_exempt as _rc_nothing_exempt
from chipsim.guards.record_content import nothing_is_waived as _rc_nothing_waived
from chipsim.ingest.drugbank_snapshot import (
    DRUGBANK_CONTENT_POLICY,
    DRUGBANK_ID_EXCLUDED_FILES,
    DRUGBANK_ID_LEDGER,
    accession_structure_tuples,
    is_accession_excluded,
    ledger_tuple_hits,
    real_accession_hits,
)

#: Most guard tests are not about DrugBank's waivers, so they say so explicitly rather than
#: inheriting a default that was fail-open in one direction (DES-1).
NOTHING_WAIVED = _rc_policy(
    readability_waived=_rc_nothing_waived, content_exempt=_rc_nothing_exempt
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = PROJECT_ROOT.parent.parent

# A shape-valid, NON-SYNTHETIC accession that denotes nothing: all zeros, deliberately not an
# assigned identifier. The scan checks SHAPE ONLY and holds no list of assigned accessions, so
# the positive detection path never needed a real one (measured, r2.29). The synthetic range is
# excluded by a negative lookahead, so it cannot serve here — hence non-synthetic, not real.
#
# STILL ASSEMBLED, and that half is load-bearing: this file is NOT accession-excluded, so a
# literal would be found by the guard scanning its own fixture and the live gate would go red.
# The assembly was never the problem; the value was.
REAL = "DB" + "00000"
SYNTHETIC = "DB90004"
STRUCTURE = "InChI=1S/C4H7NO4/c5-2(4(8)9)1-3(6)7/h2H,1,5H2,(H,6,7)(H,8,9)/t2-/m0/s1"

APPROVAL_LOG = "workstreams/lung-on-chipsim/plan/plan-approval-log.md"
BUILD_PLAN = "workstreams/lung-on-chipsim/plan/build-plan.md"


# --- exceptions resolve against the scan root ------------------------------------------


def test_every_named_exception_resolves_at_the_repo_root():
    """The exception keys move WITH the scan root. Project-relative keys under a repo-root
    walk would silently stop matching the ledger, and a scan that stops matching its own
    exceptions reports clean for the wrong reason."""
    for rel in sorted(DRUGBANK_ID_LEDGER | DRUGBANK_ID_EXCLUDED_FILES):
        assert (REPO_ROOT / rel).is_file(), f"exception {rel!r} does not exist at the repo root"


def test_the_exclusion_boundary_is_exactly_the_ruled_set():
    assert is_accession_excluded(".claude/usr/matthew-mo/cto/dispatches/directive-x.md")
    assert is_accession_excluded(".claude/usr/matthew-mo/lung-on-chipsim/dispatches/d.md")
    assert DRUGBANK_ID_LEDGER, (
        "an empty ledger makes this `all()` — and the one in the tuple-check test — pass over "
        "nothing; a loop with no iterations is the vacuity family in its plainest form"
    )
    assert all(is_accession_excluded(rel) for rel in DRUGBANK_ID_LEDGER)
    # In scope — the rulings keep these enforced, not excused:
    assert not is_accession_excluded(BUILD_PLAN)
    assert not is_accession_excluded(APPROVAL_LOG)  # reversed 2026-09-16: see module docstring
    assert not is_accession_excluded(".claude/usr/matthew-mo/lung-on-chipsim/handoff.md")
    assert not is_accession_excluded("workstreams/lung-on-chipsim/reports/x/merge_report.json")
    assert not is_accession_excluded("projects/lung-on-chipsim/README.md")


# --- falsification of the wider scope ----------------------------------------------------


def test_scope_falsification_plants_real_accessions_across_the_tree(tmp_path):
    """Plant a real accession in each place; exactly the in-scope ones must be caught.

    This is what proves the scope widened: the old project-rooted scan could not have seen
    `workstreams/` or `.claude/` at all."""
    planted = {
        "workstreams/lung-on-chipsim/notes.md": True,
        BUILD_PLAN: True,
        # The approval log IS caught (CTO reversal, 2026-09-16). RULE FOR ANYONE EDITING IT:
        # a row that corrects an accession must DESCRIBE the removal — e.g. "one DrugBank
        # accession removed from this row" — and must NEVER quote the accession to say what
        # was removed. Naming it re-introduces exactly what the row records the removal of,
        # and this guard will fail on it.
        APPROVAL_LOG: True,
        ".claude/usr/matthew-mo/cto/dispatches/directive.md": False,
        "projects/lung-on-chipsim/README.md": True,
    }
    for rel in planted:
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"see {REAL}\n")
    hits = {rel for rel, _ in real_accession_hits(tmp_path, list(planted))}
    assert hits == {rel for rel, expected in planted.items() if expected}


def test_synthetic_accessions_are_never_hits(tmp_path):
    (tmp_path / "a.md").write_text(f"fixture id {SYNTHETIC}\n")
    assert real_accession_hits(tmp_path, ["a.md"]) == []


# --- the live repository -----------------------------------------------------------------


def _tracked_paths() -> list[str]:
    """Every tracked path, repo-relative, submodule gitlinks removed.

    QG F-07: the previous `git ls-files` + `str.split()` broke any path containing whitespace
    into fragments that resolve to nothing, and the scan skips what does not resolve, so such
    a file was silently never scanned. NUL-separated output cannot be mis-split. Gitlinks
    (mode 160000) are skipped explicitly: they are another repository, not a file here.
    """
    raw = subprocess.run(
        ["git", "ls-files", "-z", "-s"], cwd=REPO_ROOT, capture_output=True, check=True
    ).stdout.decode("utf-8")
    paths = []
    for record in filter(None, raw.split("\0")):
        meta, rel = record.split("\t", 1)
        if meta.split()[0] != "160000":
            paths.append(rel)
    return paths


def test_the_live_scan_sees_every_tracked_file():
    """Anti-vacuity for the live scan: a scan over the wrong or an empty list reports clean."""
    tracked = _tracked_paths()
    assert len(tracked) > 100
    assert "projects/lung-on-chipsim/tests/test_record_content_guard.py" in tracked
    assert APPROVAL_LOG in tracked and BUILD_PLAN in tracked
    unresolvable = [rel for rel in tracked if not (REPO_ROOT / rel).is_file()]
    assert unresolvable == [], (
        f"tracked paths that do not resolve to a file, so the scan would skip them: {unresolvable[:5]}"
    )


def test_no_real_drugbank_accession_is_tracked_anywhere_in_the_repo_outside_the_exclusions():
    tracked = _tracked_paths()
    hits = real_accession_hits(REPO_ROOT, tracked)
    assert hits == [], f"real DrugBank accessions tracked outside the ruled exclusions: {hits}"


# --- the tuple half: an accession ASSOCIATED WITH a structure --------------------------------


def test_tuple_detector_catches_an_accession_beside_a_structure_across_lines():
    text = f"# {REAL}'s full string, for instance, is\n# `{STRUCTURE}` — intact\n"
    assert [(accession, line) for line, accession, _ in accession_structure_tuples(text)] == [
        (REAL, 1)
    ]


def test_tuple_detector_ignores_a_structure_with_no_accession_nearby():
    assert accession_structure_tuples(f'GOOD = "{STRUCTURE}"\n') == []


def test_tuple_detector_ignores_an_accession_with_no_structure_nearby():
    assert accession_structure_tuples(f"- {REAL}\n- another entry\n") == []


def test_tuple_detector_ignores_synthetic_accessions():
    assert accession_structure_tuples(f"{SYNTHETIC} {STRUCTURE}\n") == []


def test_tuple_detector_window_is_two_lines_each_way():
    """QG F-08: pin the window edge in both directions, so widening or narrowing it is a
    deliberate, visible change."""
    assert accession_structure_tuples(f"{REAL} {STRUCTURE}\n")  # distance 0: same line
    for distance, caught in [(1, True), (2, True), (3, False)]:
        filler = "\n" * (distance - 1)  # `distance` lines apart
        after = f"{REAL}\n{filler}{STRUCTURE}\n"
        before = f"{STRUCTURE}\n{filler}{REAL}\n"
        assert bool(accession_structure_tuples(after)) is caught, ("after", distance)
        assert bool(accession_structure_tuples(before)) is caught, ("before", distance)


def test_tuple_detector_treats_an_inchikey_as_a_structure():
    """A key beside an accession identifies the molecule as surely as the full string."""
    key = "CKLJMWTZIZZHCS-REOHCLBHSA-N"  # PubChem CID 5960 (L-aspartic acid)
    assert [a for _, a, _ in accession_structure_tuples(f"{REAL}: {key}\n")] == [REAL]


def _plant(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def test_the_ledger_tuple_check_catches_a_planted_tuple_in_each_ledger_file(tmp_path):
    """QG F-08: the live ledger check passes on a clean ledger, which proves nothing about
    whether it can fail. Plant a tuple in each ledger file; each must be reported."""
    for rel in DRUGBANK_ID_LEDGER:
        _plant(tmp_path, rel, f"# {REAL}\n# {STRUCTURE}\n")
    hits = ledger_tuple_hits(tmp_path)
    assert sorted(rel for rel, _, _ in hits) == sorted(DRUGBANK_ID_LEDGER)
    assert all(line == 1 and accession == REAL for _, line, accession in hits)


def test_the_ledger_tuple_check_does_not_scan_outside_the_ledger(tmp_path):
    """The tuple check is the ledger's rule. Everywhere else a real accession is already a hit
    on its own (`real_accession_hits`), with or without a structure."""
    for rel in DRUGBANK_ID_LEDGER:
        _plant(tmp_path, rel, "# clean\n")
    _plant(tmp_path, "projects/lung-on-chipsim/README.md", f"{REAL}\n{STRUCTURE}\n")
    assert ledger_tuple_hits(tmp_path) == []
    assert real_accession_hits(tmp_path, ["projects/lung-on-chipsim/README.md"]) != []


def test_the_ledger_carries_no_accession_structure_tuple():
    """The ledger may keep its accessions but not a structure associated with one (#120 §4).
    A plain "no InChI in the ledger" rule would be wrong — the ledger's tests hold an aspirin
    structure and an invalid sentinel that belong to no accession."""
    hits = ledger_tuple_hits(REPO_ROOT)
    assert hits == [], (
        f"accession/structure tuples in the sanctioned ledger: {hits}. Drop the structure "
        "strings, keep the accessions (#120 §4)."
    )


# --- E-3: a skipped file is an UNCHECKED file (CTO ruling, QG §5) --------------------------


def test_a_parquet_carrying_record_content_is_scanned_not_skipped(tmp_path):
    """The guard read files as UTF-8 text and skipped whatever failed, so a tracked parquet
    holding an accession beside a name and a structure — the complete record — returned NO hits,
    while the same content in a CSV was caught. Measured by the §5 security review.
    """
    import pandas as pd

    frame = pd.DataFrame({"drugbank_id": [REAL], "name": ["a compound name"], "inchi": [STRUCTURE]})
    frame.to_parquet(tmp_path / "compounds.parquet", engine="pyarrow")
    assert [a for _, a in real_accession_hits(tmp_path, ["compounds.parquet"])] == [REAL]


def test_a_parquet_without_record_content_is_clean(tmp_path):
    import pandas as pd

    pd.DataFrame({"canonical_inchikey": ["FIXTURECMPDAAA-FIXTUREKEY-N"]}).to_parquet(
        tmp_path / "clean.parquet", engine="pyarrow"
    )
    assert real_accession_hits(tmp_path, ["clean.parquet"]) == []


def test_a_parquet_that_cannot_be_READ_is_undecodable_not_clean(tmp_path):
    """A corrupt or truncated parquet must report as UNREADABLE, never as "no hits". Treating a
    failed read as clean is the same false-clean in a new costume — and it survived the first
    version of these tests, which is how it was found."""
    (tmp_path / "broken.parquet").write_bytes(b"PAR1 truncated garbage not really parquet")
    assert undecodable_unallowed(
        _surfaced(tmp_path, ["broken.parquet"]), NOTHING_WAIVED, _surface_of(tmp_path)
    ) == ["broken.parquet"]
    assert real_accession_hits(tmp_path, ["broken.parquet"]) == []


def test_an_undecodable_file_is_reported_unless_it_is_declared(tmp_path):
    """Fail-closed on the unknown: a new binary must be DECLARED before the scan passes, so
    "no hits" can never mean "never read". The declaration is by exact path, not by suffix —
    a suffix rule would silently admit the next .pdf nobody looked at."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "figure.pdf").write_bytes(b"\x89PNG\x00\xff\xfe not utf-8")
    assert undecodable_unallowed(
        _surfaced(tmp_path, ["docs/figure.pdf"]), NOTHING_WAIVED, _surface_of(tmp_path)
    ) == ["docs/figure.pdf"]


def test_a_declared_binary_file_is_not_reported(tmp_path):
    """The declaration surface is empty in this repo, so the mechanism is exercised with a real
    declaration FILE owned by this project — which is what a real entry would have to be.

    The version this replaces monkeypatched a constant the reader no longer consults, and was
    vacuous even before that: its fixture wrote b"\\xff\\xfe not utf-8", which decodes as UTF-16, so
    the file was READABLE and the assertion held with or without a declaration. Hence the first
    assertion below — prove the fixture is undecodable, then prove the declaration is what clears
    it."""
    import chipsim.guards.record_content as rc

    declared = f"projects/{THIS_PROJECT}/docs/figure.pdf"
    digest = _write(tmp_path, declared, b"%PDF-1.4\x00\xfe\xff\x80\x81 binary")

    bare = _decl_fixture(tmp_path) + [declared]
    assert rc.undecodable_unallowed(bare, NOTHING_WAIVED, _surface_of(tmp_path)) == [declared], (
        "the fixture must be genuinely undecodable, or declaring it proves nothing"
    )

    listing = _decl_fixture(
        tmp_path,
        project_entries=[{"path": declared, "sha256": digest, "why": "rendered figure"}],
    ) + [declared]
    assert rc.undecodable_unallowed(listing, NOTHING_WAIVED, _surface_of(tmp_path)) == []


def test_every_undecodable_tracked_file_in_this_repo_is_declared():
    """SUPERSEDED IN SCOPE BY r2.22 E6-1b, deliberately kept rather than deleted.

    Until E6-1b this asserted the repo-wide list was EMPTY, which is what forced 23 of another
    team's paths to be declared inside this module. The failure is now scoped to the files this
    project owns (plus any file no project owns); the repo-wide LISTING is asserted by
    `test_the_live_report_is_not_vacuous_and_this_gate_is_green`, because listing is what may never
    be skipped and failing is what is scoped.
    """
    undeclared = failing_undeclared(_tracked_paths(), NOTHING_WAIVED, _surface_of(REPO_ROOT))
    assert undeclared == [], (
        f"{len(undeclared)} tracked file(s) this project owns (or that no project owns) cannot be "
        f"decoded and are not declared: {undeclared[:5]}"
    )


def test_the_declaration_surface_is_not_a_blanket():
    """The shape rules bind every entry in the SHIPPED data. Empty is the correct state today, so
    this loop runs zero times — which is honest rather than reassuring, and is why the live
    anti-rot test below asserts against the validator instead of against a count."""
    import chipsim.guards.record_content as rc

    for rel, _entry, _surface in rc._declaration_entries(REPO_ROOT):
        assert not rel.endswith("/"), f"{rel} waves through a whole directory"
        assert "*" not in rel, f"{rel} is a glob, not a declared file"
        assert Path(rel).suffix, f"{rel} has no extension — is it really a binary artifact?"


# --- §6: what four reviewers proved these tests could NOT catch -----------------------------


def _parquet(tmp_path: Path, frame, name: str = "c.parquet") -> Path:
    path = tmp_path / name
    frame.to_parquet(path, engine="pyarrow")
    return path


def test_a_parquet_hiding_the_record_in_its_footer_metadata_is_caught(tmp_path):
    """§6, the HIGH that blocked release. A table whose SCHEMA METADATA carries the accession, the
    coined name and the structure scanned as ",harmless\n0,1\n": the complete record in the file,
    absent from the scanned text, and reported by NEITHER half — so the guard's own green tests
    certified it clean. `pq.write_table(..., metadata=...)` is ordinary, and DuckDB/Spark/Polars
    stamp metadata by default."""
    import pyarrow as pa
    import pyarrow.parquet as pq

    table = pa.table({"harmless": [1, 2, 3]}).replace_schema_metadata(
        {b"provenance": f'{{"drugbank_id": "{REAL}", "inchi": "{STRUCTURE}"}}'.encode()}
    )
    path = tmp_path / "kv.parquet"
    pq.write_table(table, path)
    assert [a for _, a in real_accession_hits(tmp_path, ["kv.parquet"])] == [REAL]


def test_a_parquet_hiding_the_record_in_per_field_metadata_is_caught(tmp_path):
    import pyarrow as pa
    import pyarrow.parquet as pq

    field = pa.field("harmless", pa.int64(), metadata={b"src": REAL.encode()})
    path = tmp_path / "fieldmeta.parquet"
    pq.write_table(pa.table([pa.array([1])], schema=pa.schema([field])), path)
    assert [a for _, a in real_accession_hits(tmp_path, ["fieldmeta.parquet"])] == [REAL]


def test_a_long_list_cell_is_scanned_whole_not_elided(tmp_path):
    """numpy's repr ELIDES above 1000 elements, so an accession at position 1500 of a `groups`
    list vanished and the file scanned clean. `write_compounds` persists `groups` and `atc_codes`
    as list columns — this is the project's own shape, not a contrived one."""
    import pandas as pd

    ids = ["DB90001"] * 2000
    ids[1500] = REAL
    path = _parquet(tmp_path, pd.DataFrame({"groups": [ids]}), "lists.parquet")
    assert [a for _, a in real_accession_hits(tmp_path, [path.name])] == [REAL]


def test_a_deep_row_and_a_middle_column_are_scanned(tmp_path):
    """A truncating stringifier (`str(frame)`, `.head(1)`) survived every earlier test because the
    fixture was a ONE-ROW frame. `write_compounds` persists thousands of rows and the accession
    will almost never be in row 0."""
    import pandas as pd

    rows = 500
    frame = pd.DataFrame(
        {
            "a": ["DB90001"] * rows,
            "middle": ["DB90002"] * rows,
            "z": ["DB90003"] * rows,
        }
    )
    frame.loc[rows - 1, "middle"] = REAL
    path = _parquet(tmp_path, frame, "deep.parquet")
    assert [a for _, a in real_accession_hits(tmp_path, [path.name])] == [REAL]


def test_the_parquet_index_is_scanned(tmp_path):
    import pandas as pd

    frame = pd.DataFrame({"a": [1]}, index=pd.Index([REAL], name="idx"))
    path = _parquet(tmp_path, frame, "index.parquet")
    assert [a for _, a in real_accession_hits(tmp_path, [path.name])] == [REAL]


def test_a_parquet_is_recognised_by_its_MAGIC_not_its_name(tmp_path):
    """This repo closed a case-sensitivity bypass three commits ago (84ce8e0) and the same shape
    came back: `.PARQUET`, `.pq` and an extensionless blob fell through to "cannot be decoded",
    whose remedy — declare it — would make a fully readable record carrier permanently invisible."""
    import pandas as pd

    frame = pd.DataFrame({"drugbank_id": [REAL], "inchi": [STRUCTURE]})
    for name in ("UP.PARQUET", "data.pq", "blob"):
        path = _parquet(tmp_path, frame, name)
        assert [a for _, a in real_accession_hits(tmp_path, [path.name])] == [REAL], name
        assert (
            undecodable_unallowed(
                _surfaced(tmp_path, [path.name]), NOTHING_WAIVED, _surface_of(tmp_path)
            )
            == []
        ), name


def test_text_in_other_encodings_is_scanned_not_declared_away(tmp_path):
    """A latin-1 or UTF-16 document carrying an accession was classified "undecodable", and the
    only exit offered was the allow-list — which would make a PLAIN-TEXT carrier invisible for
    good. UTF-16 is a routine artifact of Windows-authored files."""
    (tmp_path / "latin1.md").write_bytes(("caf\xe9 " + REAL).encode("latin-1"))
    (tmp_path / "utf16.md").write_bytes(("x " + REAL).encode("utf-16"))
    hits = {rel for rel, _ in real_accession_hits(tmp_path, ["latin1.md", "utf16.md"])}
    assert hits == {"latin1.md", "utf16.md"}
    assert (
        undecodable_unallowed(
            _surfaced(tmp_path, ["latin1.md", "utf16.md"]),
            NOTHING_WAIVED,
            _surface_of(tmp_path),
        )
        == []
    )


def test_genuine_binary_is_still_reported_not_decoded_into_mojibake(tmp_path):
    """The other side of the lenient decode: latin-1 decodes ANY bytes, so it must not become an
    unconditional last resort — a binary that "decodes" is a binary that scans clean."""
    (tmp_path / "real.png").write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00")
    assert undecodable_unallowed(
        _surfaced(tmp_path, ["real.png"]), NOTHING_WAIVED, _surface_of(tmp_path)
    ) == ["real.png"]


def test_the_allowlist_is_matched_by_EXACT_path_not_by_suffix_or_basename(tmp_path, monkeypatch):
    """Both a path-suffix match and a basename match survived every earlier test, so
    `vendor/<declared path>` or any file sharing a declared BASENAME would have been silently
    exempted. The docstring claimed "exact path"; nothing checked it."""
    import chipsim.guards.record_content as rc

    declared = f"projects/{THIS_PROJECT}/docs/figure.pdf"
    digest = _write(tmp_path, declared, b"%PDF-1.4\x00\xfe\xff\x80 binary")
    entry = {"path": declared, "sha256": digest, "why": "rendered figure"}

    for rel in (f"vendor/{declared}", f"some/other/dir/{Path(declared).name}"):
        _write(tmp_path, rel, b"\x00\xff\x80\x81 not text")
        listing = _decl_fixture(tmp_path, project_entries=[entry]) + [declared, rel]
        assert rel in rc.undecodable_unallowed(listing, NOTHING_WAIVED, _surface_of(tmp_path)), rel
        assert declared not in rc.undecodable_unallowed(
            listing, NOTHING_WAIVED, _surface_of(tmp_path)
        ), (
            "the declared path itself must still be cleared, or this test would pass on a "
            "declaration mechanism that simply does not work"
        )


def test_a_declared_path_is_still_scanned_when_its_bytes_are_readable(tmp_path, monkeypatch):
    """The allow-list declares that a file cannot be READ — never that its content is exempt.
    Adding `or rel in RENDERED_ARTIFACT_DECLARATIONS` to the accession scan survived the whole suite, which
    would have turned "somebody looked at this artifact once" into a blanket content waiver."""

    declared = f"projects/{THIS_PROJECT}/docs/figure.pdf"
    target = tmp_path / declared
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(f"see {REAL}\n")
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    listing = _decl_fixture(
        tmp_path,
        project_entries=[{"path": declared, "sha256": digest, "why": "claims to be unreadable"}],
    ) + [declared]

    # The content scan is untouched by any declaration: a declaration says a file cannot be READ,
    # never that its content is exempt.
    assert [a for _, a in real_accession_hits(tmp_path, listing)] == [REAL]

    # ...and declaring a file the scan CAN read is itself a defect: it exempts nothing and hides
    # everything, which is the shape the live shipped-data test has always asserted.
    defects = _defects(tmp_path, listing)
    assert declared in defects and "readable" in defects[declared].lower()


def test_undecodable_reporting_is_not_limited_to_familiar_extensions(tmp_path):
    """Limiting the REPORT to known binary suffixes survived — the exact bypass the exact-path
    rule exists to prevent, rebuilt on the reporting side."""
    for name in ("weird.bin", "notes.md", "blob_no_ext"):
        (tmp_path / name).write_bytes(b"\x00\xff\xfe\x00 not text at all")
    assert undecodable_unallowed(
        _surfaced(tmp_path, ["weird.bin", "notes.md", "blob_no_ext"]),
        NOTHING_WAIVED,
        _surface_of(tmp_path),
    ) == [
        "blob_no_ext",
        "notes.md",
        "weird.bin",
    ]


def test_an_empty_file_is_read_not_reported(tmp_path):
    """Pinned only BY ACCIDENT before: the `is None` vs falsy distinction was covered only because
    the repo happens to track six empty .gitkeep files."""
    import pandas as pd

    (tmp_path / "empty.md").write_text("")
    _parquet(tmp_path, pd.DataFrame({"drugbank_id": pd.Series([], dtype=str)}), "zero.parquet")
    assert (
        undecodable_unallowed(
            _surfaced(tmp_path, ["empty.md", "zero.parquet"]),
            NOTHING_WAIVED,
            _surface_of(tmp_path),
        )
        == []
    )
    assert real_accession_hits(tmp_path, ["empty.md", "zero.parquet"]) == []


def test_the_report_is_sorted_so_a_failure_reads_the_same_way_twice(tmp_path):
    for rel in ("z/c.bin", "m/a.bin", "a/b.bin"):
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"\x00\xff")
    assert undecodable_unallowed(
        _surfaced(tmp_path, ["z/c.bin", "m/a.bin", "a/b.bin"]),
        NOTHING_WAIVED,
        _surface_of(tmp_path),
    ) == [
        "a/b.bin",
        "m/a.bin",
        "z/c.bin",
    ]


def test_an_undecodable_ledger_file_is_reported_but_a_dispatch_payload_is_not(tmp_path):
    """The ledger's content IS still read (`ledger_tuple_hits` does a bare read_text), so its
    readability is exactly what this check is for — the exclusion exists for accession CONTENT,
    not for readability. A dispatch payload is waived by ruling and never scanned either way, so
    reporting it would be unactionable noise."""
    ledger = min(DRUGBANK_ID_LEDGER)
    dispatch = ".claude/usr/matthew-mo/lung-on-chipsim/dispatches/attachment.md"
    for rel in (ledger, dispatch):
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"\x00\xff not text")
    # BOTH are reported now: the ledger because its content is still read, and the dispatch payload
    # because a BINARY IS NOT A MESSAGE however it is named (E6-4 as repaired in §7). The waiver
    # below is what a real message looks like.
    assert undecodable_unallowed(
        _surfaced(tmp_path, [ledger, dispatch]), NOTHING_WAIVED, _surface_of(tmp_path)
    ) == sorted([ledger, dispatch])

    message = ".claude/usr/matthew-mo/lung-on-chipsim/dispatches/real.md"
    (tmp_path / message).write_text("a sent message\n")
    assert (
        undecodable_unallowed(
            _surfaced(tmp_path, [message]), DRUGBANK_CONTENT_POLICY, _surface_of(tmp_path)
        )
        == []
    )


def test_every_declared_path_exists_is_tracked_and_is_genuinely_unreadable():
    """A declaration for a file that does not exist PRE-AUTHORISES whatever later lands at that
    path, and a declaration for a DECODABLE file hides nothing the scan could not already read.
    Three junk entries — a deleted figure, a pre-declared `data/processed/compounds.parquet`, and
    README.md — passed every earlier test. The ledger sets already had this check (above); the new
    set was simply left out of it."""
    import chipsim.guards.record_content as rc

    tracked = set(_tracked_paths())
    for rel, _entry, _surface in rc._declaration_entries(REPO_ROOT):
        path = REPO_ROOT / rel
        assert path.is_file(), f"{rel} is declared but does not exist — a pre-granted exemption"
        assert rel in tracked, f"{rel} is declared but not tracked"
        assert not _is_readable(path), (
            f"{rel} IS readable, so declaring it exempts nothing and hides everything — "
            "declare only what the scan genuinely cannot read"
        )


def test_no_declared_path_is_also_content_excluded():
    """A path must never be exempted twice by two different mechanisms."""
    import chipsim.guards.record_content as rc

    declared = [rel for rel, _, _ in rc._declaration_entries(REPO_ROOT)]
    assert [rel for rel in declared if is_accession_excluded(rel)] == []


# --- r2.21 E6-2: a readable structured container is ALWAYS read, never declared -------------


def _hdf5(tmp_path: Path, name: str, datasets: dict, attrs: dict | None = None) -> Path:
    h5py = pytest.importorskip("h5py")
    path = tmp_path / name
    with h5py.File(path, "w") as handle:
        for key, values in datasets.items():
            handle.create_dataset(key, data=values)
        for key, value in (attrs or {}).items():
            handle.attrs[key] = value
    return path


def test_an_hdf5_string_dataset_carrying_an_accession_is_scanned(tmp_path):
    """r2.21 E6-2. HDF5/h5ad is a readable structured container, so it is READ — the same argument
    that made parquet's footer readable. It was the one entry in the declared list that was not a
    rendered artifact, filed among 24 figures where nobody would register it."""
    path = _hdf5(tmp_path, "matrix.h5ad", {"obs/perturbation": [REAL.encode(), b"control"]})
    assert [a for _, a in real_accession_hits(tmp_path, [path.name])] == [REAL]


def test_an_hdf5_ATTRIBUTE_carrying_an_accession_is_scanned(tmp_path):
    """Attributes are the HDF5 analogue of parquet's footer metadata — the placement that carried
    a whole record invisibly in §6."""
    path = _hdf5(tmp_path, "attrs.h5", {"x": [1, 2]}, attrs={"provenance": f"from {REAL}"})
    assert [a for _, a in real_accession_hits(tmp_path, [path.name])] == [REAL]


def test_a_clean_hdf5_container_is_neither_a_hit_nor_undecodable(tmp_path):
    path = _hdf5(tmp_path, "clean.h5ad", {"obs/cell": [b"FIXTURE-CELL"]})
    assert real_accession_hits(tmp_path, [path.name]) == []
    assert (
        undecodable_unallowed(
            _surfaced(tmp_path, [path.name]), NOTHING_WAIVED, _surface_of(tmp_path)
        )
        == []
    )


def test_no_readable_structured_container_is_declared():
    """E6-2: only RENDERED artifacts may be declared. A container in the list is the category
    collapse the clause forbids — and the h5ad was exactly that."""
    import chipsim.guards.record_content as rc

    containers = [
        rel
        for rel, _, _ in rc._declaration_entries(REPO_ROOT)
        if Path(rel).suffix.lower() in {".parquet", ".pq", ".h5", ".h5ad", ".hdf5", ".feather"}
    ]
    assert containers == [], (
        f"declared readable container(s): {containers}. A structured container is always read."
    )


def test_an_unreadable_container_fails_loudly_rather_than_inviting_a_declaration(tmp_path):
    """If the HDF5 reader is absent the file must NOT quietly become 'undecodable — declare it',
    because declaring a container is precisely what E6-2 forbids."""

    path = _hdf5(tmp_path, "x.h5ad", {"obs/p": [b"FIXTURE"]})
    with pytest.MonkeyPatch.context() as patch:
        # The reader moved to chipsim.guards.decoding in E-18; patch where the code READS it.
        import chipsim.guards.decoding as _decoding
        from chipsim.guards.decoding import MissingContainerReader

        patch.setattr(_decoding, "_HDF5_READER", None)

        # NOT RuntimeError: RecordContentScanError is one too, so the broad form would also pass
        # on an unrelated scan refusal whose message happened to mention h5py.
        with pytest.raises(MissingContainerReader, match="no reader is installed"):
            real_accession_hits(tmp_path, [path.name])


# --- r2.21 E6-4: the dispatch waiver covers MESSAGES, not bytes ------------------------------


def test_the_dispatch_waiver_covers_md_payloads_only():
    """#122 §3 waives dispatches because redacting a sent MESSAGE falsifies the audit trail. A PDF
    dropped in that directory is not a message whose text is being audited — and a tracked
    `dispatches/leak.pdf` carrying a real accession was double-exempt with the suite green."""
    base = ".claude/usr/matthew-mo/lung-on-chipsim/dispatches"
    assert is_accession_excluded(f"{base}/message.md")
    assert not is_accession_excluded(f"{base}/leak.pdf")
    assert not is_accession_excluded(f"{base}/leak.parquet")
    assert not is_accession_excluded(f"{base}/attachment.csv")


def test_a_non_md_file_in_a_dispatch_directory_is_scanned_and_reported(tmp_path):
    base = Path(".claude/usr/matthew-mo/lung-on-chipsim/dispatches")
    (tmp_path / base).mkdir(parents=True)
    (tmp_path / base / "leak.csv").write_text(f"see {REAL}\n")
    (tmp_path / base / "leak.pdf").write_bytes(b"%PDF-1.4\x00\xff not text")
    (tmp_path / base / "message.md").write_text(f"a message naming {REAL}\n")

    hits = {
        rel
        for rel, _ in real_accession_hits(
            tmp_path, [str(base / n) for n in ("leak.csv", "message.md")]
        )
    }
    assert hits == {str(base / "leak.csv")}, "the .md message stays waived; the .csv does not"
    assert undecodable_unallowed(
        _surfaced(tmp_path, [str(base / "leak.pdf")]),
        NOTHING_WAIVED,
        _surface_of(tmp_path),
    ) == [str(base / "leak.pdf")]


# --- r2.22 E6-1b: the FAILURE is scoped to the owner; the LISTING is not --------------------


@pytest.mark.parametrize(
    "rel, owner",
    [
        ("projects/lung-on-chipsim/data/x.bin", "lung-on-chipsim"),
        ("workstreams/lung-on-chipsim/reports/x.bin", "lung-on-chipsim"),
        ("projects/perturb-seq-eval/paper/fig.pdf", "perturb-seq-eval"),
        ("paper_standalone/figures/fig.pdf", "paper_standalone"),
        (".claude/usr/matthew-mo/lung-on-chipsim/dispatches/leak.pdf", None),
        ("README.md", None),
        ("config/monitor-pids.json", None),
    ],
    ids=["mine-project", "mine-workstream", "other-project", "paper", "dispatch", "root", "config"],
)
def test_ownership_is_read_from_an_explicit_map(rel, owner):
    """ "A path matching no owner is unowned BY DEFINITION, never 'somebody else's'." The dispatch
    directory is the case that matters: it belongs to no project."""
    assert path_owner(rel, recognised_owners(_tracked_paths(), _surface_of(REPO_ROOT))) == owner


def test_a_file_this_project_owns_fails_this_gate(tmp_path):
    rel = "projects/lung-on-chipsim/data/interim/mystery.bin"
    target = tmp_path / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"\x00\xff not text")
    assert failing_undeclared(
        _surfaced(tmp_path, [rel]), NOTHING_WAIVED, _surface_of(tmp_path)
    ) == [rel]


def test_a_file_another_project_owns_is_listed_but_does_not_fail_this_gate(tmp_path):
    """The whole point of E6-1b: another team not yet having adopted the rule must not turn THIS
    gate red — measured, that was 24 files on day one — while the file stays visible and counted."""
    rel = "projects/perturb-seq-eval/paper/figures/fig9.pdf"
    target = tmp_path / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"%PDF-1.4\x00\xff")
    # The marker is what makes perturb-seq-eval a REAL project rather than a name in a path: an
    # owner minted by mkdir listed as somebody else's problem and failed nobody's gate.
    listing = _surfaced(tmp_path, [rel, "projects/perturb-seq-eval/pyproject.toml"])
    assert failing_undeclared(listing, NOTHING_WAIVED, _surface_of(tmp_path)) == []
    assert undeclared_report(listing, NOTHING_WAIVED, _surface_of(tmp_path)) == [
        (rel, "perturb-seq-eval")
    ]


def test_a_path_owned_by_NO_project_fails_this_gate(tmp_path):
    """LOAD-BEARING FOR E6-4. `.claude/usr/**/dispatches/` belongs to no project, so a non-.md
    dispatch payload keeps failing here. Drafted without this rule, E6-1b would have made
    dispatches/leak.pdf listed and UNFAILABLE ANYWHERE — silently re-opening the hole E6-4 closed
    one clause above, in the same revision that closed it."""
    rel = ".claude/usr/matthew-mo/lung-on-chipsim/dispatches/leak.pdf"
    target = tmp_path / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"%PDF-1.4\x00\xff and a real accession " + REAL.encode())
    assert failing_undeclared(
        _surfaced(tmp_path, [rel]), NOTHING_WAIVED, _surface_of(tmp_path)
    ) == [rel]
    assert undeclared_report(_surfaced(tmp_path, [rel]), NOTHING_WAIVED, _surface_of(tmp_path)) == [
        (rel, None)
    ]


def test_the_report_names_the_owner_of_every_listed_file(tmp_path):
    """ "The LISTING stays repo-wide, with the owning project named." Listing is what may never be
    skipped; failing is what is scoped."""
    files = {
        "projects/perturb-seq-eval/a.pdf": "perturb-seq-eval",
        "paper_standalone/b.pdf": "paper_standalone",
        "projects/lung-on-chipsim/c.bin": "lung-on-chipsim",
        ".claude/d.bin": None,
    }
    for rel in files:
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"\x00\xff")
    # The markers that make those three owners real. They are listed but never written to disk, so
    # they are not readable and never appear in the report — exactly as an unreadable-file scan
    # should treat a path it cannot open.
    markers = [
        "projects/perturb-seq-eval/pyproject.toml",
        "paper_standalone/README.md",
        "projects/lung-on-chipsim/pyproject.toml",
    ]
    assert undeclared_report(
        _surfaced(tmp_path, [*files, *markers]), NOTHING_WAIVED, _surface_of(tmp_path)
    ) == sorted(files.items())


def test_the_accession_scan_does_not_shrink_with_the_failure_scope(tmp_path):
    """ "The accession scan itself stays repo-wide and does not shrink — this scopes only who a
    missing DECLARATION blocks." A readable file in another project's tree is still a hit."""
    rel = "projects/perturb-seq-eval/notes.md"
    target = tmp_path / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(f"see {REAL}\n")
    assert [a for _, a in real_accession_hits(tmp_path, [rel])] == [REAL]
    assert (
        failing_undeclared(_surfaced(tmp_path, [rel]), NOTHING_WAIVED, _surface_of(tmp_path)) == []
    )


def test_the_live_report_is_not_vacuous_and_this_gate_is_green():
    """The live half. Anti-vacuity moved from the declared list (now empty for this project, since
    none of the 24 was ever ours) to the REPORT: the other teams' artifacts must still be counted
    and named, not silently dropped by the scoping."""
    tracked = _tracked_paths()
    report = undeclared_report(tracked, NOTHING_WAIVED, _surface_of(REPO_ROOT))
    assert failing_undeclared(tracked, NOTHING_WAIVED, _surface_of(REPO_ROOT)) == [], (
        "this project owns an undeclared undecodable file (or one owned by nobody)"
    )
    assert len(report) >= 20, "the other teams' undeclared binaries must stay visible"
    owners = {owner for _, owner in report}
    assert owners == {"perturb-seq-eval", "paper_standalone"}, owners
    assert all(owner is not None for _, owner in report), "an unowned file would have to FAIL"


# --- r2.21 E6-5: each mechanism states which half it enforces, and neither claims the other ---


def test_each_mechanism_states_which_half_of_the_invariant_it_enforces():
    """The principal's invariant names "a NAME or accession with a structure". Two mechanisms split
    it: the repo-wide scan enforces the ACCESSION half, the r2.20 writer allow-list enforces the
    NAME half. A structure plus a name with no accession is invisible to the scan BY DESIGN — and
    an overclaim about what a guard sees is worse than the gap it hides, which is why I had to
    narrow my own §5 claim that "the format most likely to carry a whole record" was now visible.
    """
    import chipsim.guards.output_roots as writers
    import chipsim.ingest.drugbank_snapshot as scanner

    scan_doc = (scanner.real_accession_hits.__doc__ or "") + (scanner.__doc__ or "")
    writer_doc = (writers.__doc__ or "") + (
        writers.refuse_unless_declared_output_root.__doc__ or ""
    )

    assert "ACCESSION half" in scan_doc, "the scan must say which half it enforces"
    assert "NAME half" in writer_doc, "the writer allow-list must say which half it enforces"
    assert "NAME half" not in scan_doc, "the scan must not claim the name half"
    assert "ACCESSION half" not in writer_doc, "the writer must not claim the accession half"


# --- §7 Phase B: "always READ" was false for every real container ---------------------------


def test_a_long_hdf5_string_dataset_is_scanned_whole_not_elided(tmp_path):
    """§7 HIGH, measured on the LIVE artifact: the 34.6 MB h5ad scanned to 4,270 chars with THREE
    elision markers — var/gene_symbol (35,635), var/ensembl_id (35,635) and obs/cell_barcode
    (5,768) all elided, under 0.5% of its string content examined. `repr(array)` summarises above
    1,000 elements.

    This is the SAME defect `_parquet_chunks` fixed and pinned one clause earlier ("numpy's repr
    ELIDES above 1000 elements"), reintroduced in the reader written to close the container gap.
    And the 0.01s scan time I quoted as evidence the cost was fine was a measurement OF the elision.
    """
    h5py = pytest.importorskip("h5py")
    values = [b"FIXTURE-CELL"] * 2000
    values[1500] = REAL.encode()
    path = tmp_path / "big.h5ad"
    with h5py.File(path, "w") as handle:
        handle.create_dataset("obs/_index", data=values)
    assert [a for _, a in real_accession_hits(tmp_path, [path.name])] == [REAL]


def test_a_compound_dtype_dataset_is_scanned(tmp_path):
    """§7 HIGH. `dtype.kind == "V"` was skipped — the on-disk shape of every HDF5 table and of
    legacy AnnData obs/var recarrays. A compound dataset holding the whole record scanned to SEVEN
    CHARACTERS: hit [], reported []. The §6 parquet-footer pattern inside the reader added to close
    the §6 parquet-footer pattern."""
    import numpy as np

    h5py = pytest.importorskip("h5py")
    path = tmp_path / "compound.h5"
    data = np.array(
        [(REAL.encode(), b"a coined title", 1.0)],
        dtype=[("id", "S12"), ("name", "S32"), ("val", "f4")],
    )
    with h5py.File(path, "w") as handle:
        handle.create_dataset("records", data=data)
    assert [a for _, a in real_accession_hits(tmp_path, [path.name])] == [REAL]


def test_a_container_whose_dataset_cannot_be_read_is_reported_not_called_clean(
    tmp_path, monkeypatch
):
    """§7. An unreadable dataset was annotated `<unreadable>`, the file then counted as READ and
    scanned CLEAN, and nothing inspected the marker — reproduced with the exact error an h5ad
    written with hdf5plugin raises when the plugin is absent. "A skipped file is an UNCHECKED
    file" applies inside a container too."""
    h5py = pytest.importorskip("h5py")
    path = tmp_path / "broken_dataset.h5ad"
    with h5py.File(path, "w") as handle:
        handle.create_dataset("obs/_index", data=[b"FIXTURE"])

    def boom(self, *args, **kwargs):
        raise OSError("Can't read data (can't open directory: /usr/local/hdf5/lib/plugin)")

    monkeypatch.setattr(h5py.Dataset, "__getitem__", boom)
    assert undecodable_unallowed(
        _surfaced(tmp_path, [path.name]), NOTHING_WAIVED, _surface_of(tmp_path)
    ) == [path.name]


def test_a_container_holding_only_links_is_reported_not_called_read(tmp_path):
    """§7. `visititems` skips soft and external links, so a container whose only members are links
    produced an EMPTY chunk and was classified readable and clean. A container that yields ZERO
    content was never read."""
    h5py = pytest.importorskip("h5py")
    target = tmp_path / "elsewhere.h5"
    with h5py.File(target, "w") as handle:
        handle.create_dataset("secret", data=[REAL.encode()])
    path = tmp_path / "links_only.h5"
    with h5py.File(path, "w") as handle:
        handle["soft"] = h5py.SoftLink("/missing")
        handle["ext"] = h5py.ExternalLink(str(target), "/secret")
    assert undecodable_unallowed(
        _surfaced(tmp_path, [path.name]), NOTHING_WAIVED, _surface_of(tmp_path)
    ) == [path.name]


def test_a_parquet_struct_column_is_scanned_by_value_not_by_key(tmp_path):
    """§7. `_cell` iterated a dict, which yields KEYS: a top-level struct column scanned as
    `[accession,name,inchi]` while the record sat in the bytes. list<struct>, map, dictionary
    encoding and multi-row-group were all caught — this was the one remaining nested shape."""
    import pyarrow as pa
    import pyarrow.parquet as pq

    path = tmp_path / "struct.parquet"
    table = pa.table({"rec": pa.array([{"accession": REAL, "inchi": STRUCTURE}])})
    pq.write_table(table, path)
    assert [a for _, a in real_accession_hits(tmp_path, [path.name])] == [REAL]


def test_the_live_container_is_read_substantially_not_vacuously():
    """The anti-vacuity the elision hid: the repo's own 34.6 MB container must yield far more than
    a summary. Before the fix it produced 4,270 chars for ~41,000 identifiers."""
    import chipsim.guards.decoding as _decoding

    target = REPO_ROOT / "projects/perturb-seq-eval/data/Adamson2016_pilot.h5ad"
    if not target.is_file():
        pytest.skip("the AnnData artifact is not present in this checkout")
    chunks = _decoding.scan_chunks(target)
    assert chunks is not None
    text = "\n".join(chunks)
    assert "..." not in text, "an elision marker means the container was summarised, not read"
    assert len(text) > 500_000, f"only {len(text):,} chars scanned for ~41,000 identifiers"


# --- §7 Phase D: a message is TEXT, not a filename -------------------------------------------


def test_a_binary_named_md_in_a_dispatch_directory_is_not_waived(tmp_path):
    """§7 HIGH, EXECUTED by two reviewers. The waiver was decided by FILENAME, so the same binary
    blob that fails as `leak.pdf` was DOUBLE-EXEMPT as `leak.md` — waived from the accession scan
    AND skipped by the undecodable report, listed nowhere.

    #122 §3 waives a sent MESSAGE because redacting one falsifies the audit trail. A binary is not
    a message whatever it is named, and this module's own doctrine two functions away is "dispatch
    on the MAGIC, not on the name"."""
    base = Path(".claude/usr/matthew-mo/lung-on-chipsim/dispatches")
    (tmp_path / base).mkdir(parents=True)
    blob = b"\x00\xff binary payload carrying " + REAL.encode()
    (tmp_path / base / "leak.md").write_bytes(blob)
    (tmp_path / base / "message.md").write_text(f"a real message naming {REAL}\n")

    rel_binary = str(base / "leak.md")
    rel_message = str(base / "message.md")

    assert undecodable_unallowed(
        _surfaced(tmp_path, [rel_binary]), NOTHING_WAIVED, _surface_of(tmp_path)
    ) == [rel_binary]
    assert failing_undeclared(
        _surfaced(tmp_path, [rel_binary]), NOTHING_WAIVED, _surface_of(tmp_path)
    ) == [rel_binary], "unowned -> fails here"
    # The genuine message keeps its waiver: its text IS the audit trail.
    assert real_accession_hits(tmp_path, [rel_message]) == []
    assert (
        undecodable_unallowed(
            _surfaced(tmp_path, [rel_message]), NOTHING_WAIVED, _surface_of(tmp_path)
        )
        == []
    )


def test_the_waiver_is_anchored_so_leak_md_pdf_is_not_waived():
    """Dropping the `$` anchor would waive `leak.md.pdf` — the same double exemption in a new
    costume. No existing fixture tested the anchor, because they all fail the substring too."""
    base = ".claude/usr/matthew-mo/lung-on-chipsim/dispatches"
    assert is_accession_excluded(f"{base}/message.md")
    for name in ("leak.md.pdf", "notes.md.parquet", "x.md.bin"):
        assert not is_accession_excluded(f"{base}/{name}"), name


# --- §7 Phase D: declarations must be OWNED, and containers may not be declared --------------


def test_every_declaration_belongs_to_this_project():
    """E6-1's actual invariant, which nothing tested: re-adding all 23 foreign paths would have
    passed every existing test. The clause was enforced by the ABSENCE OF DATA, not by a rule."""
    import chipsim.guards.record_content as rc

    _recognised = recognised_owners(_tracked_paths(), _surface_of(REPO_ROOT))
    foreign = [
        rel
        for rel, _, surface in rc._declaration_entries(REPO_ROOT)
        if surface == "project" and path_owner(rel, _recognised) != THIS_PROJECT
    ]
    assert foreign == [], (
        f"declared here but owned elsewhere: {foreign}. Declarations live with the project that "
        "owns the artifact (E6-1); declaring another team's file assigns them this gate's failure."
    )


def test_a_container_cannot_be_declared_even_if_its_name_hides_it(tmp_path, monkeypatch):
    """The "no container declared" test filtered by SUFFIX — name-based dispatch, the anti-pattern
    this module condemns 170 lines earlier. A container named `blob.dat` passed."""
    import pandas as pd

    import chipsim.guards.record_content as rc

    declared = f"projects/{THIS_PROJECT}/docs/blob.dat"
    target = tmp_path / declared
    target.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"drugbank_id": [REAL]}).to_parquet(target, engine="pyarrow")
    digest = hashlib.sha256(target.read_bytes()).hexdigest()

    _decl_fixture(
        tmp_path,
        project_entries=[{"path": declared, "sha256": digest, "why": "named to look opaque"}],
    )
    with pytest.raises(rc.RecordContentScanError, match="declared readable container"):
        rc.assert_no_container_is_declared(tmp_path)


# --- §7 Phase D: the report reaches a human ---------------------------------------------------


def test_the_report_is_printed_by_a_command_a_human_can_run(tmp_path, monkeypatch, capsys):
    """The CTO's question at the §6 boundary: is `undeclared_report` ever CALLED somewhere a human
    sees it, or only asserted on in tests? "Listing that reaches no one is functionally a silent
    skip", which is the thing r2.20 forbade."""
    from chipsim import pipeline

    # No CHIPSIM_PROJECT_ROOT here. The command stopped reading it when the root became structural,
    # so setting it claimed a tmp_path scope this test never had — a reader would mis-file what it
    # covers. Its defeat is asserted for real in test_the_command_is_not_steered_by_the_directory...
    code = pipeline.main(["record-content-report"])
    printed = capsys.readouterr().out
    assert code == 0
    assert "undeclared" in printed.lower()
    # Every LISTED path names its owner, and unowned is spelled out rather than left blank.
    listed = [ln for ln in printed.splitlines() if "owner=" in ln]
    assert listed, printed
    for line in listed:
        assert "FAILS HERE" in line or "listed" in line


def test_the_report_command_exits_non_zero_when_this_gate_would_fail(tmp_path, monkeypatch, capsys):
    import chipsim.guards.record_content as rc
    from chipsim import pipeline

    rel = "projects/lung-on-chipsim/data/interim/mystery.bin"
    target = tmp_path / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"\x00\xff")

    # Steer the ROOT, not an environment variable: r2.23 E-08 makes the command derive the repo
    # root structurally, precisely so no ambient setting can narrow what it scans.
    listing = [rel, *_decl_fixture(tmp_path, owners=[THIS_PROJECT])]
    monkeypatch.setattr(rc, "repo_root", lambda: tmp_path)
    monkeypatch.setattr(rc, "_tracked_listing", lambda root: (listing, []))
    # This test fabricates a listing under tmp_path, which the witness check refuses BY DESIGN
    # (a listing must contain this module's own tracked file). Disabled here only, so that this
    # test can still say what it is about — the exit code for a file that fails the gate. The
    # witness check has its own tests above.
    monkeypatch.setattr(rc, "_refuse_a_scan_that_cannot_see_itself", lambda root, paths: None)
    code = pipeline.main(["record-content-report"])
    assert code == 2
    assert rel in capsys.readouterr().out


# --- r2.23 E-08: the report is rendered at the REPO root, and an unscannable tree is not clean ---
#
# The first E-08 fix moved the root SELECTION and left the root VALIDATION and the file LISTING
# able to fail silently, so every remaining way of getting the root wrong still printed
# "0 (failing this gate: 0)" and exit 0. These tests are about the failure MODE, not the happy
# path: each one asserts that a scan which cannot be performed is distinguishable from a clean one.


def _init_repo(path: Path) -> Path:
    """A REAL repository. A bare `.git` directory is not one: `repo_root()` asks git to resolve the
    candidate precisely so that a stray marker cannot pass as a root."""
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    return path


def test_repo_root_agrees_with_the_oracle_the_rest_of_this_file_uses():
    """Two independent definitions of "the repo root" exist: REPO_ROOT (positional, used by ten
    tests here) and `repo_root()` (the `.git` walk, used by the command). They agreed only by
    coincidence and nothing pinned them, so the suite and the command could each scan their own
    tree and each report clean — E-08's geometry one layer up."""
    from chipsim.guards.record_content import repo_root

    assert repo_root() == REPO_ROOT


def test_repo_root_walks_past_a_directory_that_merely_looks_like_a_repo_root(tmp_path, monkeypatch):
    """The marker is `.git`, not "a directory containing projects/".

    A mutant that stops at the first ancestor holding a `projects/` directory — never consulting
    `.git` at all — survived the whole previous suite, because in the live tree those two rules
    name the same directory. Only a fixture can tell them apart.
    """
    import chipsim.guards.record_content as rc
    import chipsim.guards.repo as _repo

    outer = _init_repo(tmp_path / "outer")
    package_parent = outer / "nested" / "projects" / "lung-on-chipsim"
    (package_parent / "chipsim").mkdir(parents=True)
    assert not (outer / "nested" / ".git").exists(), "the lookalike must NOT be a repository"

    monkeypatch.setattr(_repo, "source_root", lambda: package_parent)
    assert rc.repo_root() == outer.resolve()


@pytest.mark.parametrize("marker", ["directory", "worktree_file"])
def test_repo_root_accepts_a_worktree_git_file_not_only_a_git_directory(
    tmp_path, monkeypatch, marker
):
    """A worktree's `.git` is a FILE. `is_dir()` instead of `exists()` is a one-character change
    that silently reinstates the project-root scan IN EVERY WORKTREE — which is where this repo's
    work actually happens. The commit message claimed this property; nothing tested it, and the
    mutant survived."""
    import chipsim.guards.record_content as rc
    import chipsim.guards.repo as _repo

    main = _init_repo(tmp_path / "main")
    (main / "seed.txt").write_text("seed\n")
    subprocess.run(["git", "add", "seed.txt"], cwd=main, check=True)
    subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "seed"],
        cwd=main,
        check=True,
    )

    if marker == "directory":
        root = main
    else:
        root = tmp_path / "wt"
        subprocess.run(["git", "worktree", "add", "-q", str(root)], cwd=main, check=True)
        assert (root / ".git").is_file(), "a worktree's .git is a file, which is the whole point"

    package_parent = root / "projects" / "lung-on-chipsim"
    (package_parent / "chipsim").mkdir(parents=True)
    monkeypatch.setattr(_repo, "source_root", lambda: package_parent)
    assert rc.repo_root() == root.resolve()


def test_repo_root_refuses_a_broken_git_marker_rather_than_collapsing_to_the_project_root(
    tmp_path, monkeypatch
):
    """An aborted `git init`, a copied worktree stub or a half-done submodule conversion leaves a
    `.git` that git cannot open. Trusting the marker's existence alone collapsed the scan back to
    the project root and restored E-08 verbatim — and this repo DOES use submodules, so a sibling
    of this project is already one."""
    import chipsim.guards.record_content as rc
    import chipsim.guards.repo as _repo

    outer = _init_repo(tmp_path / "outer")
    package_parent = outer / "projects" / "lung-on-chipsim"
    (package_parent / "chipsim").mkdir(parents=True)
    (package_parent / ".git").write_text("gitdir: /nonexistent/.git/worktrees/gone\n")

    monkeypatch.setattr(_repo, "source_root", lambda: package_parent)
    with pytest.raises(rc.RecordContentScanError) as exc:
        rc.repo_root()
    message = str(exc.value).replace(str(tmp_path), "<tmp>")
    assert "git cannot open a repository" in message
    assert "clean" in message, "the refusal must say why an unscannable tree is not a clean one"


def test_repo_root_refuses_when_no_repository_exists_above_the_package(tmp_path, monkeypatch):
    """The fallback that shipped returned `source_root()` — the narrow root the finding is ABOUT.
    Composed with a listing that swallowed its own failure, a non-editable install printed a clean
    report over a tree it had never read. Reproduced end-to-end before this fix."""
    import chipsim.guards.record_content as rc
    import chipsim.guards.repo as _repo

    bare = tmp_path / "a" / "b"
    bare.mkdir(parents=True)
    if any((p / ".git").exists() for p in [bare, *bare.parents]):
        pytest.skip(
            "this temp directory sits inside a repository, so the no-repo case is untestable here"
        )

    monkeypatch.setattr(_repo, "source_root", lambda: bare)
    with pytest.raises(rc.RecordContentScanError) as exc:
        rc.repo_root()
    assert "no git repository" in str(exc.value)


def test_a_listing_that_could_not_be_produced_is_not_an_empty_one(tmp_path):
    """`_tracked_paths_for_report` returned `[]` when git failed, and the renderer printed that as
    "0 (failing this gate: 0)" with exit 0. The test-side twin of this function has used
    `check=True` since the day it was written, beneath a test titled "a scan over the wrong or an
    empty list reports clean" — the guard existed in the suite and not in the command."""
    import chipsim.guards.record_content as rc
    import chipsim.guards.repo as _repo

    not_a_checkout = tmp_path / "plain"
    not_a_checkout.mkdir()
    with pytest.raises(rc.RecordContentScanError) as exc:
        _repo.tracked_paths(not_a_checkout)
    assert "not an all-clear" in str(exc.value)


def test_a_git_failure_inside_a_real_checkout_is_not_an_empty_listing(tmp_path):
    """The harder half, and the one a mutant survived: the root IS a valid checkout and `ls-files`
    still fails — a corrupt or locked index, an unreadable object store, or git refusing the tree
    over `safe.directory` ownership, which is the ordinary case for a root-owned checkout under a
    non-root CI runner.

    `rev-parse` answers fine in every one of those, so the not-a-checkout guard never fires and this
    branch is the only thing standing between a broken repository and a clean report. The first
    version of this test used a directory that was not a checkout at all, so it exercised the guard
    above and left this one covered by nothing.
    """
    import chipsim.guards.record_content as rc
    import chipsim.guards.repo as _repo

    repo = _init_repo(tmp_path / "corrupt")
    (repo / ".git" / "index").write_bytes(b"this is not an index")
    assert _repo.toplevel_of(repo) == repo.resolve(), "the checkout itself must still resolve"

    with pytest.raises(rc.RecordContentScanError) as exc:
        _repo.tracked_paths(repo)
    message = str(exc.value)
    assert "git ls-files failed" in message
    # git's own diagnostic is what tells the operator WHICH failure this is; the old code captured
    # stderr and threw it away, so the one useful sentence never reached anybody.
    assert "no diagnostic" not in message


def test_an_emptied_listing_cannot_pass_as_a_scan_of_this_tree(monkeypatch):
    """The witness check: the listing must contain THIS module's own tracked file. One assertion
    covering an unrelated enclosing repository, an index read from elsewhere, and a listing emptied
    by any means at all."""
    import chipsim.guards.record_content as rc

    monkeypatch.setattr(rc, "_tracked_listing", lambda root: ([], []))
    with pytest.raises(rc.RecordContentScanError) as exc:
        rc.render_undeclared_report(NOTHING_WAIVED)
    assert "this module's own file" in str(exc.value)


def test_the_scan_refuses_a_repository_that_does_not_contain_this_package(tmp_path, monkeypatch):
    """An unrelated enclosing repository — a dotfiles `$HOME`, a wrapper monorepo — became the scan
    root and the gate reported on THAT repo, exiting on its files rather than ours."""
    import chipsim.guards.record_content as rc

    stranger = _init_repo(tmp_path / "stranger")
    with pytest.raises(rc.RecordContentScanError) as exc:
        rc._refuse_a_scan_that_cannot_see_itself(stranger, ["some/other/file.txt"])
    assert "does not contain this package" in str(exc.value)


def test_git_environment_variables_cannot_steer_the_scan(tmp_path, monkeypatch):
    """`subprocess.run` inherits the environment, so GIT_DIR/GIT_INDEX_FILE override `cwd` outright:
    the report printed the CORRECT root while having listed a different repository's index — more
    misleading than the bug being fixed. The docstring named four members of the ambient-state
    family and claimed immunity while leaving a fifth channel open."""
    import chipsim.guards.repo as _repo

    decoy = _init_repo(tmp_path / "decoy")
    monkeypatch.setenv("GIT_DIR", str(decoy / ".git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(decoy))
    monkeypatch.setenv("GIT_CONFIG_COUNT", "1")
    monkeypatch.setenv("GIT_CONFIG_KEY_0", "core.fsmonitor")
    monkeypatch.setenv("GIT_CONFIG_VALUE_0", "true")

    assert _repo.toplevel_of(REPO_ROOT) == REPO_ROOT, (
        "the scan resolved a different tree than the one it was pointed at"
    )
    assert "projects/lung-on-chipsim/chipsim/ingest/drugbank_snapshot.py" in _repo.tracked_paths(
        REPO_ROOT
    )


def test_the_scan_does_not_execute_configuration_from_the_repository_it_reads(tmp_path):
    """`core.fsmonitor` is a repo-local config value git EXECUTES. A planted one in an ancestor
    repository ran as the invoking user during `record-content-report`. The CTO's B2 ruling (#44)
    requires both that the path be validated as the expected repository and that the invocation not
    honour config from a tree we do not trust."""
    import chipsim.guards.repo as _repo

    hostile = _init_repo(tmp_path / "hostile")
    marker = tmp_path / "it-ran"
    hook = tmp_path / "hook.sh"
    hook.write_text(f"#!/bin/sh\ntouch {marker}\nexit 1\n")
    hook.chmod(0o755)
    subprocess.run(["git", "config", "core.fsmonitor", str(hook)], cwd=hostile, check=True)

    _repo.run_git(["ls-files"], cwd=hostile)
    assert not marker.exists(), "the scan executed a command configured by the repository it read"


def test_the_shipped_command_prints_exactly_what_the_function_renders(capsys):
    """The defect was command != function, so the assertion is that equality — at the file's own
    oracle, and immune to how many binaries other teams happen to track today.

    The count-based assertion this replaces (`>= 20`) was a floor under a number this whole
    mechanism exists to drive to ZERO: the moment perturb-seq-eval or paper_standalone declares its
    binaries, a correct implementation goes red.
    """
    from chipsim import pipeline
    from chipsim.guards.record_content import _render_for_root

    expected_text, expected_code = _render_for_root(REPO_ROOT, DRUGBANK_CONTENT_POLICY, "worktree")
    code = pipeline.main(["record-content-report"])
    printed = capsys.readouterr().out

    assert printed.rstrip("\n") == expected_text
    assert code == expected_code


def test_the_report_states_the_root_and_the_denominator_it_scanned(capsys):
    """Naming the root only in the all-clear branch left the harder falsehood undetectable: a
    wrong-but-nonempty root prints a plausible list with no root stated anywhere, and a count with
    no base reads the same whether 4,000 files were scanned or none."""
    from chipsim import pipeline

    pipeline.main(["record-content-report"])
    header = capsys.readouterr().out.splitlines()[0]
    assert str(REPO_ROOT) in header, header
    assert "scanned" in header and "tracked files" in header, header


def test_the_report_says_that_another_projects_files_are_gated_by_nobody(capsys):
    """E-03, stated where it is READ rather than only in the plan. `owner=x [listed]` reads to a
    human as "filed with the team who will fix it", and no other project implements this check."""
    from chipsim import pipeline

    pipeline.main(["record-content-report"])
    printed = capsys.readouterr().out
    assert "fail NO gate today" in printed
    assert "exit 2 when" in printed


def test_an_unscannable_tree_exits_differently_from_a_failing_one(tmp_path, monkeypatch, capsys):
    """Exit 2 means "files fail this gate". "I could not scan" is a different fact with a different
    remedy, and collapsing the two is how an unscannable tree came to read as a clean one."""
    import chipsim.guards.record_content as rc
    from chipsim import pipeline

    def refuse(*_args, **_kwargs):
        raise rc.RecordContentScanError("no repository found in this test")

    monkeypatch.setattr(rc, "repo_root", refuse)
    code = pipeline.main(["record-content-report"])
    captured = capsys.readouterr()

    assert code == 3, "not 2 (files fail the gate) and not 0 (clean)"
    assert "could not run" in captured.err
    assert "undeclared undecodable files: 0" not in captured.out


def test_the_command_is_not_steered_by_the_directory_it_is_run_from(tmp_path, monkeypatch, capsys):
    """The claim "verified from two directories" was made in a commit message and encoded nowhere.
    Defeating CHIPSIM_PROJECT_ROOT is the point of deriving the root structurally, so it is set
    here too."""
    from chipsim import pipeline

    pipeline.main(["record-content-report"])
    from_here = capsys.readouterr().out

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CHIPSIM_PROJECT_ROOT", str(tmp_path))
    pipeline.main(["record-content-report"])
    from_elsewhere = capsys.readouterr().out

    assert from_here == from_elsewhere


# --- r2.23 §8: three bypasses that survive a correct root ------------------------------------


def test_an_owner_cannot_be_minted_by_making_a_directory():
    """`libs/ghost-lib/payload.bin` reported `owner=ghost-lib [listed]` and exit 0, so a payload
    parked under a name nobody owns failed the only gate that exists. Directory existence proves
    nothing: the attacker's own file created the directory.

    Given E-03, an INVENTED owner is strictly better for an attacker than a real one — nobody is
    even nominally responsible.
    """
    from chipsim.guards.record_content import path_owner, recognised_owners

    tracked = _tracked_paths()
    recognised = recognised_owners(tracked, _surface_of(REPO_ROOT))

    assert "perturb-seq-eval" in recognised, "a project with a tracked pyproject.toml is real"
    assert "paper_standalone" in recognised
    assert THIS_PROJECT in recognised

    for invented in (
        "libs/ghost-lib/payload.bin",
        "projects/ghost-team/artifacts/payload.bin",
        "workstreams/ghost-ws/payload.bin",
    ):
        assert path_owner(invented, recognised) is None, (
            f"{invented} was attributed to a project that does not exist, so it fails nobody"
        )

    # ...while a real owner still resolves, or the fix would have gone too far the other way.
    assert path_owner("projects/perturb-seq-eval/x/y.bin", recognised) == "perturb-seq-eval"


def test_a_filename_cannot_forge_the_listing():
    """One filename was made to draw a complete fake clean report: a leading ESC[2J ESC[H cleared
    the terminal and the rest of the name printed a forged header and all-clear, with three
    payload-bearing files still listed below where no human would see them. A bare newline splits
    one real entry into two innocuous rows.

    With no CI consumer of the exit code, the printed listing IS the control.
    """
    from chipsim.guards.record_content import render_path

    forged = "docs/\x1b[2J\x1b[Hundeclared undecodable files: 0 (failing this gate: 0).png"
    rendered = render_path(forged)
    assert "\x1b" not in rendered and "\n" not in rendered
    assert "control characters" in rendered

    split = "workstreams/zz/notes.txt\n  docs/architecture-diagram.png"
    assert "\n" not in render_path(split)

    # An ordinary path must pass through untouched, or every line of the report becomes unreadable.
    assert render_path("projects/lung-on-chipsim/chipsim/pipeline.py") == (
        "projects/lung-on-chipsim/chipsim/pipeline.py"
    )


def test_the_report_states_which_submodules_it_did_not_scan(capsys):
    """Excluding a gitlink is correct — it is another repository, not a file here — but doing it
    silently is the skip this module condemns everywhere else. Six exist, one of them a sibling of
    this project, and a payload committed inside one is invisible to this report."""
    from chipsim import pipeline

    pipeline.main(["record-content-report"])
    printed = capsys.readouterr().out
    assert "submodule(s) NOT scanned" in printed
    assert "projects/aviary-biosim" in printed


def test_the_report_names_the_package_copy_it_ran_from(capsys):
    """Which tree gets audited follows the copy of `chipsim` that was imported, not where the
    operator is standing. In this review one clone's command reported on a DIFFERENT worktree's
    tree — a routine, silent audit-the-wrong-tree false clean in an org that uses worktrees."""
    import chipsim.guards.record_content as rc
    from chipsim import pipeline

    pipeline.main(["record-content-report"])
    printed = capsys.readouterr().out
    assert str(Path(rc.__file__).resolve()) in printed


# --- r2.24 E-10: a path the scan cannot reach is counted always, and fails only where we own it ---
#
# I shipped this FATAL in §8, on the reading that a scan which cannot see everything must not read
# as clean. The CTO ruled that one level too wide: it makes the report unrunnable in a legitimate
# sparse or partial checkout, and a control nobody can run is not a control. Counting is never
# scoped (scoping the count would be E-08 again); FAILING is scoped by ownership (that is E6-1b).


def _missing_tracked(tmp_path, rel, markers=()):
    """A listing that names `rel` while `rel` is absent from disk — skip-worktree, sparse checkout,
    or a partial clone that never fetched the blob. The payload is IN the repository, which is what
    the invariant protects; the worktree simply does not have it.

    The declaration surface is built too: a repository without one cannot be scanned at all
    (exit 3), so a fixture that omitted it was describing a tree the gate would refuse.
    """
    import chipsim.guards.record_content as rc

    witness = Path(rc.__file__).resolve()
    base = _decl_fixture(tmp_path, owners=[THIS_PROJECT, "perturb-seq-eval", "paper_standalone"])
    listing = [rel, *markers, *base]
    return listing, witness


def test_a_tracked_path_that_is_not_on_disk_is_counted_and_reported(tmp_path, monkeypatch, capsys):
    """The original sin was the silent drop: `if not target.is_file(): continue`. A payload
    committed in HEAD but absent from the worktree produced a report that said nothing at all."""
    import chipsim.guards.record_content as rc
    from chipsim import pipeline

    rel = "docs/ghost_payload.bin"
    listing, _ = _missing_tracked(tmp_path, rel)
    monkeypatch.setattr(rc, "repo_root", lambda: tmp_path)
    monkeypatch.setattr(rc, "_tracked_listing", lambda root: (listing, []))
    monkeypatch.setattr(rc, "_refuse_a_scan_that_cannot_see_itself", lambda root, paths: None)

    code = pipeline.main(["record-content-report"])
    printed = capsys.readouterr().out

    assert rel in printed, "a path the scan could not reach must never be silently dropped"
    # NOT `"not present on disk" in printed`: the header carries "N not present on disk"
    # unconditionally, so that substring is there even when the section is gone and N is 0. It
    # passed with the whole section deleted (MUT-8).
    assert "tracked but NOT PRESENT ON DISK" in printed
    assert ", 1 not present on disk" in printed.splitlines()[0]
    assert code == 2, "docs/ is owned by no project, and unowned fails here (E6-1b)"


def test_a_missing_path_another_project_owns_is_listed_but_does_not_fail_this_gate(
    tmp_path, monkeypatch, capsys
):
    """Scoping the FAILURE by ownership is E6-1b; scoping the COUNT would be E-08 again. Another
    team's un-materialised file is visible and counted here, and red on nobody's board but theirs."""
    import chipsim.guards.record_content as rc
    from chipsim import pipeline

    rel = "projects/perturb-seq-eval/paper/ghost.pdf"
    listing, _ = _missing_tracked(
        tmp_path, rel, markers=("projects/perturb-seq-eval/pyproject.toml",)
    )
    monkeypatch.setattr(rc, "repo_root", lambda: tmp_path)
    monkeypatch.setattr(rc, "_tracked_listing", lambda root: (listing, []))
    monkeypatch.setattr(rc, "_refuse_a_scan_that_cannot_see_itself", lambda root, paths: None)

    code = pipeline.main(["record-content-report"])
    printed = capsys.readouterr().out

    assert rel in printed
    assert "tracked but NOT PRESENT ON DISK" in printed  # the section, not the header fragment
    # 2, not 1: this fixture's OWNERSHIP MARKER is listed and also unmaterialised. Both are counted
    # repo-wide even though neither fails this gate — scoping the count would be E-08 again.
    assert ", 2 not present on disk" in printed.splitlines()[0]
    assert code == 0, "another project's missing file is counted here and fails only on their gate"


def test_a_missing_path_this_project_owns_fails_the_gate(tmp_path, monkeypatch, capsys):
    import chipsim.guards.record_content as rc
    from chipsim import pipeline

    rel = f"projects/{THIS_PROJECT}/data/processed/ghost.parquet"
    listing, _ = _missing_tracked(
        tmp_path, rel, markers=(f"projects/{THIS_PROJECT}/pyproject.toml",)
    )
    monkeypatch.setattr(rc, "repo_root", lambda: tmp_path)
    monkeypatch.setattr(rc, "_tracked_listing", lambda root: (listing, []))
    monkeypatch.setattr(rc, "_refuse_a_scan_that_cannot_see_itself", lambda root, paths: None)

    code = pipeline.main(["record-content-report"])
    assert rel in capsys.readouterr().out
    assert code == 2


def test_a_sparse_checkout_can_still_run_the_report(tmp_path, monkeypatch, capsys):
    """The reason the ruling went this way: fatal-always made the report unrunnable wherever a
    legitimate sparse or partial checkout is in use, and a control nobody can run is not a control.
    Exit 3 stays reserved for "could not scan AT ALL"."""
    import chipsim.guards.record_content as rc
    from chipsim import pipeline

    rel = "paper_standalone/figures/never_fetched.pdf"
    listing, _ = _missing_tracked(tmp_path, rel, markers=("paper_standalone/README.md",))
    monkeypatch.setattr(rc, "repo_root", lambda: tmp_path)
    monkeypatch.setattr(rc, "_tracked_listing", lambda root: (listing, []))
    monkeypatch.setattr(rc, "_refuse_a_scan_that_cannot_see_itself", lambda root, paths: None)

    code = pipeline.main(["record-content-report"])
    printed = capsys.readouterr().out

    assert code != 3, "a sparse checkout is not the same as being unable to scan"
    assert code == 0
    assert rel in printed


def test_the_witness_check_is_still_fatal(tmp_path):
    """E-10 relaxed the UNRESOLVABLE path, not the witness. A listing that is not a listing of this
    tree is still "could not scan at all" — exit 3, not a report."""
    import chipsim.guards.record_content as rc

    stranger = _init_repo(tmp_path / "stranger")
    with pytest.raises(rc.RecordContentScanError):
        rc._refuse_a_scan_that_cannot_see_itself(stranger, ["some/other/file.txt"])


# --- r2.24 E-02 / E6-1 / E6-3 / E-05 / E-11: the declaration surface ---------------------------
#
# The removal half shipped in r2.22 and the READ half never did: RENDERED_ARTIFACT_DECLARATIONS has
# been an empty frozenset that nothing populates, and E6-1b's scoping kept the suite green without
# it — which is precisely why it was easy to miss. I found it by re-reading the clause against the
# code, not by a failing test, so these tests exist to make the absence of the data VISIBLE rather
# than convenient.


def _defects(root, listing, policy=NOTHING_WAIVED):
    """{path: every reason reported for it}, joined.

    NOT `dict(declaration_defects(...))`: since r2.25 E-15 an entry may carry several defects, and a
    dict keeps only the last, so an assertion on a message would depend on check ORDER instead of on
    behaviour.
    """
    import chipsim.guards.record_content as _rc

    out: dict[str, str] = {}
    for path, why in _rc.declaration_defects(listing, policy, _surface_of(root)):
        out[path] = f"{out.get(path, '')} {why}".strip()
    return out


def _decl_fixture(tmp_path, project_entries=None, repo_entries=None, owners=None):
    """A repo-shaped fixture carrying both declaration files and the markers that make owners real."""
    import yaml

    import chipsim.guards.record_content as rc

    proj = tmp_path / "projects" / THIS_PROJECT
    (proj / "configs").mkdir(parents=True, exist_ok=True)
    (tmp_path / "config").mkdir(parents=True, exist_ok=True)

    # "1" as a STRING, mirroring the shipped files. The fixture wrote an int while the real data
    # wrote a string, and nothing pinned either — so the schema check was being exercised against a
    # format the repository does not use.
    project_doc = {"version": "1", "declarations": project_entries or []}
    repo_doc = {"version": "1", "declarations": repo_entries or []}
    if owners is not None:
        repo_doc["owners"] = owners

    (proj / "configs" / "record_content_declarations.yaml").write_text(yaml.safe_dump(project_doc))
    (tmp_path / "config" / "record_content_declarations.yaml").write_text(yaml.safe_dump(repo_doc))

    listing = [
        rc.PROJECT_DECLARATION_FILE,
        rc.REPO_DECLARATION_FILE,
        f"projects/{THIS_PROJECT}/pyproject.toml",
    ]
    (proj / "pyproject.toml").write_text("[project]\nname = 'x'\n")
    return listing


def _surfaced(tmp_path, paths):
    """`paths` plus the declaration surface every root needs.

    A repository with no declaration surface is one the gate refuses to speak for (DES-3): an absent
    file read as an empty one silently reverts the owner registry to marker-only, which is the
    WIDENING direction. A fixture without a surface was describing a tree that cannot pass.
    """
    return list(paths) + _decl_fixture(tmp_path)


def _surface_of(root):
    """The surface a caller must now pass explicitly.

    `require` rather than `read`, because that is what the deleted `surface=None` fallback built —
    so every existing test keeps the behaviour it was written against, and the argument is visible.
    """
    import chipsim.guards.record_content as _rc

    return _rc.DeclarationSurface.require(root)


def _write(tmp_path, rel, data: bytes):
    target = tmp_path / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def test_a_declaration_must_pin_the_content_not_just_the_path(tmp_path):
    """E6-3. Every declared file is a BUILD OUTPUT, so a path-keyed declaration goes silent forever
    the moment the artifact is regenerated with different content — the declaration would still be
    sitting there, matching by name, clearing a file nobody has looked at since."""
    import chipsim.guards.record_content as rc

    rel = f"projects/{THIS_PROJECT}/docs/render.bin"
    digest = _write(tmp_path, rel, b"\x00\xffOPAQUE")
    listing = _decl_fixture(
        tmp_path,
        project_entries=[
            {"path": rel, "sha256": digest, "why": "rendered figure, not a container"}
        ],
    ) + [rel]

    assert rel in rc.valid_declarations(listing, NOTHING_WAIVED, _surface_of(tmp_path))
    assert rc.declaration_defects(listing, NOTHING_WAIVED, _surface_of(tmp_path)) == []
    assert rc.undecodable_unallowed(listing, NOTHING_WAIVED, _surface_of(tmp_path)) == [], (
        "a validly declared file is cleared"
    )


def test_a_declaration_goes_STALE_when_the_artifact_is_regenerated(tmp_path):
    """The whole reason for E6-3. Regenerate the artifact; the declaration must stop clearing it and
    must SAY SO, rather than silently going on matching by path."""
    import chipsim.guards.record_content as rc

    rel = f"projects/{THIS_PROJECT}/docs/render.bin"
    digest = _write(tmp_path, rel, b"\x00\xffOPAQUE")
    listing = _decl_fixture(
        tmp_path, project_entries=[{"path": rel, "sha256": digest, "why": "rendered figure"}]
    ) + [rel]

    _write(tmp_path, rel, b"\x00\xffREGENERATED")  # same path, different content

    assert rel not in rc.valid_declarations(listing, NOTHING_WAIVED, _surface_of(tmp_path))
    defects = _defects(tmp_path, listing)
    # NOT `"stale" in ...lower()`: pytest names tmp_path after the test, so "STALE" is already in
    # this test's own directory name, and a reviewer proved the assertion passes with the whole
    # message replaced by the absolute path. Assert the sentence only this branch produces, and the
    # two digests, which the fixture cannot supply.
    assert len(defects) == 1, defects
    assert defects[rel].startswith("STALE declaration: pinned ")
    assert digest[:12] in defects[rel]
    assert hashlib.sha256((tmp_path / rel).read_bytes()).hexdigest()[:12] in defects[rel]
    assert rel in rc.undecodable_unallowed(listing, NOTHING_WAIVED, _surface_of(tmp_path)), (
        "a stale declaration clears nothing"
    )


def test_a_derived_from_claim_must_name_a_tracked_source_that_is_in_scope(tmp_path):
    """The self-maintaining alternative: "derived from tracked source S, and S is in scope" is a
    claim a reader can CHECK, unlike a comment saying "none of these is a DrugBank artifact"."""
    import chipsim.guards.record_content as rc

    rel = f"projects/{THIS_PROJECT}/docs/plot.bin"
    src = f"projects/{THIS_PROJECT}/docs/plot_source.csv"
    rel_digest = _write(tmp_path, rel, b"\x00\xffOPAQUE")
    _write(tmp_path, src, b"name,value\nalpha,1\n")
    listing = _decl_fixture(
        tmp_path,
        project_entries=[
            {
                "path": rel,
                "sha256": rel_digest,
                "derived_from": src,
                "why": "plotted from the tracked csv",
            }
        ],
    ) + [rel, src]

    assert rel in rc.valid_declarations(listing, NOTHING_WAIVED, _surface_of(tmp_path))

    # ...and the claim fails when the source is NOT tracked, which is what makes it self-maintaining.
    listing_without_source = [p for p in listing if p != src]
    assert rel not in rc.valid_declarations(
        listing_without_source, NOTHING_WAIVED, _surface_of(tmp_path)
    )
    defects = _defects(tmp_path, listing_without_source)
    assert "not tracked" in defects[rel].lower()


def test_this_project_may_not_declare_another_projects_artifacts(tmp_path):
    """E6-1, the clause's own "why": 24 paths belonging to perturb-seq-eval and paper_standalone were
    declared inside this module's source, so another team adding a figure turned THIS gate red and
    the repair landed in a file they neither own nor can judge."""
    import chipsim.guards.record_content as rc

    rel = "projects/perturb-seq-eval/paper/figure.pdf"
    digest = _write(tmp_path, rel, b"\x00\xffFOREIGN")
    listing = _decl_fixture(
        tmp_path, project_entries=[{"path": rel, "sha256": digest, "why": "not mine to declare"}]
    ) + [rel, "projects/perturb-seq-eval/pyproject.toml"]

    assert rel not in rc.valid_declarations(listing, NOTHING_WAIVED, _surface_of(tmp_path))
    defects = _defects(tmp_path, listing)
    assert "perturb-seq-eval" in defects[rel] and "owns" in defects[rel].lower()
    # The ownership branch is the FIRST check, so the assertion above holds for a fixture in any
    # state at all. The control makes ownership the only variable: byte-identical content, declared
    # under this project's own prefix, must be VALID.
    assert len(defects) == 1, defects
    mine = f"projects/{THIS_PROJECT}/paper/figure.pdf"
    mine_digest = _write(tmp_path, mine, b"\x00\xff\x80\x81FOREIGN")
    control = _decl_fixture(
        tmp_path, project_entries=[{"path": mine, "sha256": mine_digest, "why": "mine"}]
    ) + [mine]
    assert rc.declaration_defects(control, NOTHING_WAIVED, _surface_of(tmp_path)) == []
    assert mine in rc.valid_declarations(control, NOTHING_WAIVED, _surface_of(tmp_path))


def test_the_repo_root_surface_declares_UNOWNED_paths_and_only_those(tmp_path):
    """E-05. Unowned means every repo-root location, so a new docs/architecture.png from anyone fails
    THIS gate and E6-1's "do not re-declare on their behalf" left no legitimate way to clear it.
    Rule 9: state where declaring IS permitted rather than leaving the permitted case unreachable."""
    import chipsim.guards.record_content as rc

    unowned = "docs/architecture.png"
    digest = _write(tmp_path, unowned, b"\x89PNG\r\n\x1a\n\x00\xff")
    owned = f"projects/{THIS_PROJECT}/docs/mine.bin"
    owned_digest = _write(tmp_path, owned, b"\x00\xffMINE")

    listing = _decl_fixture(
        tmp_path,
        repo_entries=[
            {"path": unowned, "sha256": digest, "why": "architecture diagram, rendered"},
            {"path": owned, "sha256": owned_digest, "why": "wrong file for this one"},
        ],
    ) + [unowned, owned]

    assert unowned in rc.valid_declarations(listing, NOTHING_WAIVED, _surface_of(tmp_path))
    defects = _defects(tmp_path, listing)
    assert owned in defects, "an OWNED path does not belong in the repo-root surface"
    assert "repo-root" in defects[owned].lower()


def test_a_declaration_for_a_path_that_is_not_tracked_is_reported_as_rot(tmp_path):
    """A declaration nobody checks is rot: it accumulates, it reads as coverage, and it clears
    nothing. The file it named was deleted or renamed and the entry stayed behind."""
    import chipsim.guards.record_content as rc

    rel = f"projects/{THIS_PROJECT}/docs/deleted.bin"
    listing = _decl_fixture(
        tmp_path, project_entries=[{"path": rel, "sha256": "0" * 64, "why": "long gone"}]
    )

    defects = _defects(tmp_path, listing)
    assert rel in defects and "not tracked" in defects[rel].lower()
    assert len(defects) == 1, defects
    assert rel not in rc.valid_declarations(listing, NOTHING_WAIVED, _surface_of(tmp_path)), (
        "rot must clear nothing"
    )


def test_a_readable_container_can_never_be_declared(tmp_path):
    """E6-2, enforced against the DATA now that the data exists. Checked by MAGIC, not suffix: a
    suffix filter is name-based dispatch, and a container named blob.dat walks through it."""
    import chipsim.guards.record_content as rc

    rel = f"projects/{THIS_PROJECT}/data/processed/sneaky.dat"
    digest = _write(tmp_path, rel, b"PAR1" + b"\x00" * 32)
    listing = _decl_fixture(
        tmp_path, project_entries=[{"path": rel, "sha256": digest, "why": "claims to be opaque"}]
    ) + [rel]

    defects = _defects(tmp_path, listing)
    # NOT `"container" in ...`: it is already in this test's own tmp directory name. Assert the
    # clause reference and the MAGIC-derived kind, neither of which the test name contains.
    assert len(defects) == 1, defects
    assert "ALWAYS read, never declared (E6-2)" in defects[rel]
    assert "parquet" in defects[rel], "the kind must come from the magic, not from the suffix"
    assert rel not in rc.valid_declarations(listing, NOTHING_WAIVED, _surface_of(tmp_path))


def test_an_entry_with_NO_CONTENT_PIN_cannot_be_evaluated(tmp_path):
    """Malformed declaration DATA is a configuration error the gate cannot evaluate: refused when
    the surface is read, not reported as one broken claim among valid ones.

    THE RULE CHANGED IN r2.29 §12.6, and this test changed with it rather than being quietly
    relaxed. It used to assert that carrying BOTH `sha256` and `derived_from` was refused — "exactly
    one of" — and that rule is now gone, because the alternative it permitted was the defect: a
    `derived_from` entry never read the declared file, so it satisfied the form-level ban on a bare
    path while leaving the artifact's bytes completely unconstrained. E6-3's letter without its
    purpose.

    Carrying both is now NORMAL: the pin is mandatory and `derived_from` is provenance beside it.
    What is refused is an entry with no pin at all.
    """
    import chipsim.guards.record_content as rc

    rel = f"projects/{THIS_PROJECT}/docs/x.bin"
    digest = _write(tmp_path, rel, b"\x00\xff")

    unpinned = _decl_fixture(
        tmp_path,
        project_entries=[{"path": rel, "derived_from": "a.csv", "why": "?"}],
    ) + [rel]
    with pytest.raises(rc.RecordContentScanError, match="sha256"):
        rc.valid_declarations(unpinned, NOTHING_WAIVED, _surface_of(tmp_path))

    # ...and the pair that used to be refused is now the recommended shape, or this test would be
    # asserting a rule nobody holds.
    # A REAL tracked source owned by the same project: `a.csv` was never tracked, so the
    # provenance check failed for the right reason and the assertion would have proved nothing
    # about the pair being legal.
    src = f"projects/{THIS_PROJECT}/docs/source.csv"
    _write(tmp_path, src, b"name,value\nalpha,1\n")
    both = _decl_fixture(
        tmp_path,
        project_entries=[
            {"path": rel, "sha256": digest, "derived_from": src, "why": "provenance too"}
        ],
    ) + [rel, src]
    assert rel in rc.valid_declarations(both, NOTHING_WAIVED, _surface_of(tmp_path))


def test_the_owner_registry_is_declared_and_narrows_the_marker_heuristic(tmp_path):
    """E-11. A tracked marker is louder than mkdir but still addable by anyone who adds a
    pyproject.toml, so it is a MITIGATION, not proof. The declared registry is authoritative — and
    it NARROWS: an owner must be both declared AND carry its marker, so neither a declaration alone
    nor a file alone can mint one."""
    import chipsim.guards.record_content as rc

    listing = _decl_fixture(tmp_path, owners=[THIS_PROJECT, "perturb-seq-eval"]) + [
        "projects/perturb-seq-eval/pyproject.toml",
        "projects/undeclared-but-real/pyproject.toml",
        "projects/declared-but-absent/anything.txt",
    ]

    recognised = rc.recognised_owners(listing, _surface_of(tmp_path))
    assert THIS_PROJECT in recognised and "perturb-seq-eval" in recognised
    assert "undeclared-but-real" not in recognised, "a marker alone does not mint an owner"
    assert "declared-but-absent" not in recognised, "a declaration alone does not mint one either"


def test_the_report_states_how_many_declarations_it_read(tmp_path, monkeypatch, capsys):
    """The failure mode this whole clause is about is a mechanism that is easy to MISS because
    nothing exercises it. An empty declaration set is the correct state today — and it must be
    visible as a NUMBER rather than implied by silence.

    Asserting only the label was itself the failure: a reviewer hardcoded the count to 999 and the
    test passed. The count is asserted here on a fixture whose contents this test controls.
    """
    import chipsim.guards.record_content as rc
    from chipsim import pipeline

    mine = f"projects/{THIS_PROJECT}/docs/mine.bin"
    unowned = "docs/architecture.png"
    mine_digest = _write(tmp_path, mine, b"\x00\xff\x80\x81 MINE")
    unowned_digest = _write(tmp_path, unowned, b"\x89PNG\r\n\x1a\n\x00\xff\x80")
    listing = _decl_fixture(
        tmp_path,
        project_entries=[{"path": mine, "sha256": mine_digest, "why": "rendered"}],
        repo_entries=[{"path": unowned, "sha256": unowned_digest, "why": "diagram"}],
    ) + [mine, unowned]

    monkeypatch.setattr(rc, "repo_root", lambda: tmp_path)
    monkeypatch.setattr(rc, "_tracked_listing", lambda root: (listing, []))
    monkeypatch.setattr(rc, "_refuse_a_scan_that_cannot_see_itself", lambda root, paths: None)

    code = pipeline.main(["record-content-report"])
    printed = capsys.readouterr().out
    assert "declarations read: 2 " in printed, printed
    assert f"(1 from {rc.PROJECT_DECLARATION_FILE}, 1 from {rc.REPO_DECLARATION_FILE})" in printed
    assert "0 whose claim does not hold" in printed
    assert code == 0, printed


def test_the_shipped_declaration_files_hold():
    """ANTI-ROT over the live data. Every shape rule is enforced by the validator rather than by a
    test walking the list, so this one assertion covers a stale pin, a deleted path, a foreign path
    declared here, a readable file declared as unreadable, and a container declared at all.

    It is the assertion that stays meaningful when the surface stops being empty — the loops above
    run zero times today and will quietly keep passing however wrong a future entry is.
    """
    import chipsim.guards.record_content as rc

    assert (
        rc.declaration_defects(_tracked_paths(), DRUGBANK_CONTENT_POLICY, _surface_of(REPO_ROOT))
        == []
    )


def test_the_declared_owner_registry_covers_every_project_the_markers_support():
    """A registry that DROPS a real project does not fail loudly — that project's files silently
    become UNOWNED, and unowned fails THIS gate, so another team's artifacts would start turning
    this module red. The registry narrows by design; this is the check that the narrowing was
    deliberate rather than an omission.

    The oracle is derived here independently, by walking the tracked markers, rather than by asking
    the module — otherwise it would agree with the code by construction.
    """
    import chipsim.guards.record_content as rc

    tracked = set(_tracked_paths())
    oracle = set()
    for rel in tracked:
        parts = Path(rel).parts
        if len(parts) > 2 and parts[0] in {"projects", "libs"} and parts[2] == "pyproject.toml":
            oracle.add(parts[1])
        if len(parts) > 3 and parts[0] == "workstreams" and parts[2:4] == ("plan", "build-plan.md"):
            oracle.add(parts[1])
    if "paper_standalone/README.md" in tracked:
        oracle.add("paper_standalone")

    # Anti-vacuity for the oracle itself: a reviewer replaced the tracked listing with an empty
    # set and this test still passed, because an empty oracle trivially satisfies `oracle - declared`.
    assert {
        "lung-on-chipsim",
        "perturb-seq-eval",
        "paper_standalone",
        "cellforge-agents",
        "test-time-compute",
    } <= oracle, f"the oracle found {sorted(oracle)} — it is not reading the listing"

    declared = rc.declared_owner_registry(REPO_ROOT)
    assert declared is not None, "the repo-root surface must carry the registry"
    assert declared - oracle == set(), (
        f"declared owners with no tracked marker: {sorted(declared - oracle)}"
    )
    missing = oracle - declared
    assert missing == set(), (
        f"projects with a tracked marker that the registry omits: {sorted(missing)}. Their files "
        "would be treated as unowned, and unowned fails THIS gate."
    )


def test_the_owner_registry_narrows_rather_than_widens():
    """Declaring a project that has no marker must not mint it. The registry is an intersection, so
    a declaration alone is not evidence any more than a `mkdir` was."""
    import chipsim.guards.record_content as rc

    tracked = _tracked_paths()
    recognised = rc.recognised_owners(tracked, _surface_of(REPO_ROOT))
    declared = rc.declared_owner_registry(REPO_ROOT)

    # `recognised <= declared` is true BY CONSTRUCTION of the intersection — and true again if the
    # registry is ignored entirely, which a reviewer demonstrated. Pin it concretely instead: a name
    # in neither half must not appear, and adding a payload path must not mint its owner.
    assert recognised == rc.marker_backed_owners(tracked) & declared
    assert "ghost-lib" not in rc.recognised_owners(
        [*tracked, "libs/ghost-lib/payload.bin"], _surface_of(REPO_ROOT)
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("sha256", 12345),
        ("sha256", True),
        ("sha256", {"a": 1}),
        ("sha256", "NOTHEX" * 10),
        ("derived_from", ["a.csv"]),
        ("derived_from", 5),
        ("why", 7),
    ],
    ids=["sha-int", "sha-bool", "sha-dict", "sha-nonhex", "src-list", "src-int", "why-int"],
)
def test_a_declaration_field_of_the_wrong_TYPE_is_refused_with_a_diagnosis(tmp_path, field, value):
    """YAML hands over whatever was written. `sha256: 12345` is TRUTHY, so it passed the
    exactly-one-claim check and then crashed on `entry["sha256"][:12]` — an unhandled TypeError out
    of the shipped command, returncode 1, NO REPORT AT ALL.

    That is the same defect as the CLI traceback fixed in §7: a malformed input must produce a
    DIAGNOSIS, not a stack trace, because a traceback tells the operator nothing about which file or
    which entry to fix. A check written against the clause and not against the lesson that produced
    it (rule 12).
    """
    import chipsim.guards.record_content as rc

    rel = f"projects/{THIS_PROJECT}/docs/x.bin"
    _write(tmp_path, rel, b"\x00\xff\x80\x81")
    entry = {"path": rel, "why": "?"}
    entry.setdefault("sha256", "a" * 64)
    entry[field] = value
    if field == "derived_from":
        entry.pop("sha256")
    listing = _decl_fixture(tmp_path, project_entries=[entry]) + [rel]

    with pytest.raises(rc.RecordContentScanError) as exc:
        rc.valid_declarations(listing, NOTHING_WAIVED, _surface_of(tmp_path))
    message = str(exc.value)
    assert rel in message, "the refusal must name the entry the operator has to fix"
    assert field in message, "and the field that is wrong"


def test_a_malformed_declaration_exits_2_with_a_diagnosis_rather_than_crashing(
    tmp_path, monkeypatch, capsys
):
    """Through the SHIPPED command, not the function: before this, returncode 1 and a traceback."""
    import chipsim.guards.record_content as rc
    from chipsim import pipeline

    rel = f"projects/{THIS_PROJECT}/docs/x.bin"
    _write(tmp_path, rel, b"\x00\xff\x80\x81")
    listing = _decl_fixture(
        tmp_path, project_entries=[{"path": rel, "sha256": 12345, "why": "?"}]
    ) + [rel]

    monkeypatch.setattr(rc, "repo_root", lambda: tmp_path)
    monkeypatch.setattr(rc, "_tracked_listing", lambda root: (listing, []))
    monkeypatch.setattr(rc, "_refuse_a_scan_that_cannot_see_itself", lambda root, paths: None)

    code = pipeline.main(["record-content-report"])
    captured = capsys.readouterr()
    # r2.25 E-13 SUPERSEDED the exit 3 this test originally asserted. A broken declaration file is
    # not "could not scan at all" — the scan works, only the exemption data is unreadable — so it is
    # exit 2 with nothing declared and the listing still rendered. What this test still pins, and
    # what it was written for, is that a malformed field produces a DIAGNOSIS rather than a
    # traceback.
    assert code == 2, "not a crash, and not exit 3: the scan worked"
    assert "Traceback" not in captured.err + captured.out
    assert "sha256" in captured.err + captured.out


# --- r2.24 §9: two bypasses of the declaration surface itself ----------------------------------


def test_delisting_a_project_does_not_make_its_artifacts_declarable_here(tmp_path):
    """DES-1, EXECUTED by a reviewer. The placement rule was enforced against an owner set defined
    in the very file it polices: `declaration_defects` asked `path_owner(..., recognised_owners())`,
    and `recognised_owners` intersects with `owners:` from the repo-root file — the same file whose
    `declarations:` block was being checked.

    So delisting a project made its paths UNOWNED, and an unowned path may legally be declared at
    the repo root. One edit, one file, zero defects reported, and another team's artifacts cleared.
    That is the E6-1 violation this whole surface exists to prevent, reached through the registry
    instead of through source — and the diff for it looks like bookkeeping.

    The fix answers two DIFFERENT questions with two different sets: "whose gate does this FAIL?"
    uses the narrowed set, where narrowing is safe; "may this be declared HERE?" uses the
    MARKER-BACKED set, where widening is safe. Delisting then makes a project's files fail here —
    loud, and correct — without making them declarable.
    """
    import chipsim.guards.record_content as rc

    foreign = "projects/perturb-seq-eval/paper/paper.pdf"
    digest = _write(tmp_path, foreign, b"%PDF-1.4\x00\xfe\xff\x80 binary")
    _write(tmp_path, "projects/perturb-seq-eval/pyproject.toml", b"[project]\n")

    entry = {"path": foreign, "sha256": digest, "why": "delisted, so 'unowned'"}

    # THE INVARIANT: the answer must not depend on the registry at all. Both ways round.
    for owners in ([THIS_PROJECT], [THIS_PROJECT, "perturb-seq-eval"]):
        listing = _decl_fixture(tmp_path, repo_entries=[entry], owners=owners) + [
            foreign,
            "projects/perturb-seq-eval/pyproject.toml",
        ]
        defects = _defects(tmp_path, listing)
        assert foreign in defects, (
            f"with owners={owners}, delisting turned another team's artifact into a "
            f"repo-root-declarable path"
        )
        assert foreign not in rc.valid_declarations(listing, NOTHING_WAIVED, _surface_of(tmp_path))
        # A sentence only this branch produces — `projects/` is an ownership prefix whether or not
        # the project behind it is registered, which is what breaks the circle.
        assert "OWNERSHIP PREFIX" in defects[foreign]
        assert "belong to nobody" in defects[foreign]


def test_an_absent_declaration_surface_is_not_an_empty_one(tmp_path, monkeypatch):
    """DES-2. `_declaration_document` returned {} for a missing file, so deleting the repo-root
    surface silently reverted the owner registry to the marker-only mitigation — the pre-r2.24
    rule — with the same exit code as a healthy run.

    This module's own sentence is the argument: "an unreadable declaration file is not an empty
    one". An ABSENT one is not either. Otherwise "the surface exists" is exactly what "declared" was
    before this commit: a state the code can describe and cannot verify.
    """
    import chipsim.guards.record_content as rc

    _decl_fixture(tmp_path, owners=[THIS_PROJECT])
    (tmp_path / rc.REPO_DECLARATION_FILE).unlink()

    with pytest.raises(rc.RecordContentScanError) as exc:
        rc.refuse_an_absent_declaration_surface(tmp_path)
    assert rc.REPO_DECLARATION_FILE in str(exc.value)
    assert "absent" in str(exc.value).lower() or "missing" in str(exc.value).lower()


def test_a_pin_is_hashed_with_the_module_s_own_streaming_helper(tmp_path):
    """DES-4. The pin check slurped the whole file with read_bytes(), unlike every other reader in
    this guard, which is bounded. Declared files are by construction binaries — a pinned PDF or a
    rendered video is exactly the large-file case."""
    import chipsim.guards.record_content as rc

    rel = f"projects/{THIS_PROJECT}/docs/big.bin"
    data = b"\x00\xff\x80\x81" * 100_000
    digest = _write(tmp_path, rel, data)
    listing = _decl_fixture(
        tmp_path,
        project_entries=[{"path": rel, "sha256": digest, "why": "large rendered artifact"}],
    ) + [rel]

    calls = []
    real = rc._sha256
    ds_sha = lambda p: (calls.append(p), real(p))[1]
    import pytest as _pytest

    monkey = _pytest.MonkeyPatch()
    monkey.setattr(rc, "_sha256", ds_sha)
    try:
        assert rel in rc.valid_declarations(listing, NOTHING_WAIVED, _surface_of(tmp_path))
    finally:
        monkey.undo()
    assert calls, "the pin must go through the module's own bounded, streaming hash helper"


def test_a_derived_from_source_must_belong_to_the_same_owner(tmp_path):
    """DES-3. `derived_from` checked only that the named source was tracked and readable, so ANY
    tracked readable file satisfied it — `derived_from: README.md` passed for any artifact in the
    repo. That puts the actual claim entirely back into review, which is the position `sha256` was
    introduced to escape."""

    rel = f"projects/{THIS_PROJECT}/docs/plot.bin"
    rel_digest = _write(tmp_path, rel, b"\x00\xff\x80\x81")
    foreign_source = "projects/perturb-seq-eval/data.csv"
    _write(tmp_path, foreign_source, b"name,value\nalpha,1\n")
    _write(tmp_path, "projects/perturb-seq-eval/pyproject.toml", b"[project]\n")

    listing = _decl_fixture(
        tmp_path,
        project_entries=[
            {
                "path": rel,
                "sha256": rel_digest,
                "derived_from": foreign_source,
                "why": "cross-team pointer",
            }
        ],
        owners=[THIS_PROJECT, "perturb-seq-eval"],
    ) + [rel, foreign_source, "projects/perturb-seq-eval/pyproject.toml"]

    defects = _defects(tmp_path, listing)
    assert rel in defects and "owner" in defects[rel].lower()


# --- r2.24 §9: one test per surviving mutant --------------------------------------------------
#
# A reviewer ran 27 mutants against the validator; 12 survived the ENTIRE suite. Each survivor is a
# claim the commit message makes that nothing checked. The structural half — "each with its own
# message" — had no test at all, and neither did the headline: a broken claim fails this gate.


def _one_entry(tmp_path, entry, extra=(), owners=None):
    rel = entry.get("path")
    listing = _decl_fixture(tmp_path, project_entries=[entry], owners=owners or [THIS_PROJECT]) + [
        *extra
    ]
    return [rel, *listing] if rel else listing


def test_a_BARE_path_declaration_is_refused(tmp_path):
    """E6-3's entire point, and it was untested: the sibling test covers `both` claims only, while
    its name says "or neither". A bare path is the exact form the clause forbids, because every
    declared file is a build output."""
    import chipsim.guards.record_content as rc

    rel = f"projects/{THIS_PROJECT}/docs/bare.bin"
    _write(tmp_path, rel, b"\x00\xff\x80\x81 OPAQUE")
    listing = _one_entry(tmp_path, {"path": rel, "why": "bare"})
    # The rule CHANGED in r2.29 §12.6: `sha256` is required on every declaration, and
    # `derived_from` is optional provenance carried beside it. The old "exactly one of" rule let an
    # entry satisfy the ban on a bare path while leaving the declared file's bytes unconstrained —
    # E6-3's letter without its purpose. A bare path is still refused; the message names the pin.
    with pytest.raises(rc.RecordContentScanError, match="sha256"):
        rc.valid_declarations(listing, NOTHING_WAIVED, _surface_of(tmp_path))


def test_a_declared_owner_with_no_tracked_marker_is_not_recognised(tmp_path):
    """THE E-11 SECURITY CLAIM, and it was untested. The sibling test asserts
    "declared-but-absent" is not recognised — but its fixture never declares that name, so the
    assertion held because the name had NEITHER half. Returning the declared set instead of the
    intersection survived the whole suite: minting an owner by editing one YAML line, with no
    marker, was unchecked."""
    import chipsim.guards.record_content as rc

    listing = _decl_fixture(tmp_path, owners=[THIS_PROJECT, "ghost-lib"]) + [
        "libs/ghost-lib/payload.bin"  # note: libs/ghost-lib/pyproject.toml is NOT tracked
    ]
    recognised = rc.recognised_owners(listing, _surface_of(tmp_path))
    assert THIS_PROJECT in recognised
    assert "ghost-lib" not in recognised, "a registry entry alone must not mint an owner"
    assert rc.path_owner("libs/ghost-lib/payload.bin", recognised) is None


def test_a_broken_declaration_FAILS_the_gate_and_is_printed(tmp_path, monkeypatch, capsys):
    """The commit's headline claim — "a declaration whose claim does not hold fails this gate
    outright… there is no other gate for a broken claim to fall to (E-03)" — had NO test.

    The defect used here is a declared path that is not tracked: a defect and nothing else, so no
    other rule can be what fails it. (A stale pin would also be undecodable-and-unowned and fail
    anyway, which is why the first attempt at this test did not kill the mutant.)
    """
    import chipsim.guards.record_content as rc
    from chipsim import pipeline

    rel = f"projects/{THIS_PROJECT}/docs/deleted.bin"
    listing = _decl_fixture(
        tmp_path, project_entries=[{"path": rel, "sha256": "0" * 64, "why": "long gone"}]
    )
    monkeypatch.setattr(rc, "repo_root", lambda: tmp_path)
    monkeypatch.setattr(rc, "_tracked_listing", lambda root: (listing, []))
    monkeypatch.setattr(rc, "_refuse_a_scan_that_cannot_see_itself", lambda root, paths: None)
    monkeypatch.setattr(rc, "refuse_an_absent_declaration_surface", lambda root: None)

    code = pipeline.main(["record-content-report"])
    printed = capsys.readouterr().out
    assert code == 2, printed
    assert "1 whose claim does not hold" in printed
    assert "DECLARATIONS WHOSE CLAIM DOES NOT HOLD" in printed
    assert rel in printed


def test_an_unknown_schema_version_is_refused(tmp_path):
    """The commit says the version was "made load-bearing: an unknown version now raises rather
    than being read as this one". Nothing tested it."""
    import yaml

    import chipsim.guards.record_content as rc

    _decl_fixture(tmp_path)
    (tmp_path / rc.PROJECT_DECLARATION_FILE).write_text(
        yaml.safe_dump({"version": "2", "declarations": []})
    )
    with pytest.raises(rc.RecordContentScanError, match="unsupported declaration schema version"):
        rc._declaration_document(tmp_path, rc.PROJECT_DECLARATION_FILE)


@pytest.mark.parametrize("spelling", ["1", 1, 1.0, "01", "0x1", True, None])
def test_only_the_string_1_is_accepted_as_the_schema_version(tmp_path, spelling):
    """`str(version) != "1"` accepted YAML 1.1 integer spellings: 0x1 and 01 both stringify to
    something no reader would call version 1."""
    import yaml

    import chipsim.guards.record_content as rc

    _decl_fixture(tmp_path)
    doc = {"declarations": []}
    if spelling is not None:
        doc["version"] = spelling
    (tmp_path / rc.PROJECT_DECLARATION_FILE).write_text(yaml.safe_dump(doc))

    if spelling == "1" and isinstance(spelling, str):
        assert rc._declaration_document(tmp_path, rc.PROJECT_DECLARATION_FILE)["version"] == "1"
    else:
        with pytest.raises(rc.RecordContentScanError):
            rc._declaration_document(tmp_path, rc.PROJECT_DECLARATION_FILE)


def test_an_unparsable_declaration_file_is_not_an_empty_one(tmp_path):
    """FAIL-OPEN was the alternative, and it is the one the module's own comment refuses. With the
    repo-root file unparsable the registry would stop narrowing, so paths under unregistered names
    would become owned by marker-only names and stop failing this gate."""
    import chipsim.guards.record_content as rc

    listing = _decl_fixture(tmp_path)
    (tmp_path / rc.PROJECT_DECLARATION_FILE).write_text("declarations: [\n  - path: x\n")
    with pytest.raises(rc.RecordContentScanError, match="not an empty one"):
        rc.valid_declarations(listing, NOTHING_WAIVED, _surface_of(tmp_path))


def test_a_declaration_file_with_a_non_utf8_byte_is_refused(tmp_path):
    """One byte no UTF-8 decoder accepts produced a traceback out of the CLI — exit 1, no report —
    because read_text raises UnicodeDecodeError, which is a ValueError and not an OSError."""
    import chipsim.guards.record_content as rc

    _decl_fixture(tmp_path)
    (tmp_path / rc.REPO_DECLARATION_FILE).write_bytes(b'version: "1"\ndeclarations: []\n# \xff\n')
    with pytest.raises(rc.RecordContentScanError, match="not an empty one"):
        rc.declared_owner_registry(tmp_path)


def test_a_declarations_block_that_is_not_a_list_is_refused(tmp_path):
    """`declarations: 5` was iterated and crashed with an unhandled TypeError."""
    import yaml

    import chipsim.guards.record_content as rc

    _decl_fixture(tmp_path)
    (tmp_path / rc.PROJECT_DECLARATION_FILE).write_text(
        yaml.safe_dump({"version": "1", "declarations": 5})
    )
    with pytest.raises(rc.RecordContentScanError, match="must be a list"):
        rc._declaration_entries(tmp_path)


def test_an_entry_missing_its_why_is_refused(tmp_path):
    import chipsim.guards.record_content as rc

    rel = f"projects/{THIS_PROJECT}/docs/x.bin"
    digest = _write(tmp_path, rel, b"\x00\xff\x80\x81")
    listing = _one_entry(tmp_path, {"path": rel, "sha256": digest})
    with pytest.raises(rc.RecordContentScanError, match="needs a `why`"):
        rc.valid_declarations(listing, NOTHING_WAIVED, _surface_of(tmp_path))


def test_an_entry_missing_its_path_is_refused(tmp_path):
    import chipsim.guards.record_content as rc

    listing = _one_entry(tmp_path, {"sha256": "a" * 64, "why": "no path"})
    with pytest.raises(rc.RecordContentScanError, match="needs a `path`"):
        rc.valid_declarations(listing, NOTHING_WAIVED, _surface_of(tmp_path))


def test_an_unknown_declaration_key_is_refused(tmp_path):
    """A key the gate does not understand may be the one a reader believed was doing the work — an
    `expires:` that nothing honours, say."""
    import chipsim.guards.record_content as rc

    rel = f"projects/{THIS_PROJECT}/docs/x.bin"
    digest = _write(tmp_path, rel, b"\x00\xff\x80\x81")
    listing = _one_entry(
        tmp_path, {"path": rel, "sha256": digest, "why": "w", "expires": "2030-01-01"}
    )
    with pytest.raises(rc.RecordContentScanError, match="unknown declaration key"):
        rc.valid_declarations(listing, NOTHING_WAIVED, _surface_of(tmp_path))


def test_a_path_declared_on_BOTH_surfaces_is_refused(tmp_path):
    """Which claim governs is not something the gate may pick."""
    import chipsim.guards.record_content as rc

    rel = "docs/shared.bin"
    digest = _write(tmp_path, rel, b"\x00\xff\x80\x81")
    entry = {"path": rel, "sha256": digest, "why": "twice"}
    listing = _decl_fixture(tmp_path, project_entries=[entry], repo_entries=[entry]) + [rel]
    with pytest.raises(rc.RecordContentScanError, match="declared twice"):
        rc.valid_declarations(listing, NOTHING_WAIVED, _surface_of(tmp_path))


def test_an_owners_registry_of_the_wrong_shape_is_refused(tmp_path):
    import yaml

    import chipsim.guards.record_content as rc

    _decl_fixture(tmp_path)
    (tmp_path / rc.REPO_DECLARATION_FILE).write_text(
        yaml.safe_dump({"version": "1", "declarations": [], "owners": {"a": 1}})
    )
    with pytest.raises(rc.RecordContentScanError, match="list of project names"):
        rc.declared_owner_registry(tmp_path)


def test_a_pinned_path_absent_from_disk_is_a_defect(tmp_path):
    """Tracked, so not caught by the rot rule; absent, so the pin cannot be evaluated."""
    import chipsim.guards.record_content as rc

    rel = f"projects/{THIS_PROJECT}/docs/gone.bin"
    listing = _one_entry(tmp_path, {"path": rel, "sha256": "a" * 64, "why": "vanished"})
    defects = _defects(tmp_path, listing)
    assert rel in defects and "absent from disk" in defects[rel]
    assert rel not in rc.valid_declarations(listing, NOTHING_WAIVED, _surface_of(tmp_path))


def test_a_derived_from_source_that_cannot_be_READ_is_a_defect(tmp_path):
    """ "…and S is in scope" is the half that was untested: only the tracked half had a test."""
    import chipsim.guards.record_content as rc

    rel = f"projects/{THIS_PROJECT}/docs/plot.bin"
    src = f"projects/{THIS_PROJECT}/docs/source.bin"
    rel_digest = _write(tmp_path, rel, b"\x00\xff\x80\x81 OPAQUE")
    _write(tmp_path, src, b"\x00\xff\x80\x81 ALSO-OPAQUE")
    listing = _one_entry(
        tmp_path, {"path": rel, "sha256": rel_digest, "derived_from": src, "why": "w"}, extra=[src]
    )
    defects = _defects(tmp_path, listing)
    assert rel in defects and "cannot read" in defects[rel]
    assert rel not in rc.valid_declarations(listing, NOTHING_WAIVED, _surface_of(tmp_path))


def test_a_dispatch_payload_cannot_be_declared(tmp_path):
    """The one path class this module singles out as never-exemptible: `path_owner` returning None
    for dispatch payloads is what keeps a non-.md payload failing here (E6-4), and the repo-root
    surface made it declarable."""
    import chipsim.guards.record_content as rc

    rel = ".claude/usr/someone/dispatches/leak.pdf"
    digest = _write(tmp_path, rel, b"%PDF-1.4\x00\xfe\xff\x80")
    listing = _decl_fixture(
        tmp_path, repo_entries=[{"path": rel, "sha256": digest, "why": "cannot be read"}]
    ) + [rel]
    defects = _defects(tmp_path, listing)
    assert rel in defects and "DOUBLE-EXEMPT" in defects[rel]
    assert rel not in rc.valid_declarations(listing, NOTHING_WAIVED, _surface_of(tmp_path))


def test_a_declared_path_may_not_also_be_content_excluded(tmp_path):
    """A path must never be exempted twice by two different mechanisms. The test that claimed this
    iterated an empty declaration list against an empty exclusion set — vacuous on both sides."""
    import chipsim.guards.record_content as rc

    rel = min(DRUGBANK_ID_LEDGER)
    digest = _write(tmp_path, rel, b"\x00\xff\x80\x81 OPAQUE")
    surface = "project" if rc.path_owner(rel, frozenset({THIS_PROJECT})) == THIS_PROJECT else "repo"
    kwargs = (
        {"project_entries": [{"path": rel, "sha256": digest, "why": "w"}]}
        if surface == "project"
        else {"repo_entries": [{"path": rel, "sha256": digest, "why": "w"}]}
    )
    listing = _decl_fixture(tmp_path, **kwargs) + [rel]
    defects = _defects(tmp_path, listing, DRUGBANK_CONTENT_POLICY)
    assert rel in defects and "exempted twice" in defects[rel]
    assert rel not in rc.valid_declarations(listing, DRUGBANK_CONTENT_POLICY, _surface_of(tmp_path))


def test_a_derived_from_source_may_not_itself_be_declared(tmp_path):
    """An exemption may not rest on a file this same report may be calling a broken claim."""

    a = f"projects/{THIS_PROJECT}/docs/a.bin"
    b = f"projects/{THIS_PROJECT}/docs/b.bin"
    a_digest = _write(tmp_path, a, b"\x00\xff\x80\x81 A")
    b_digest = _write(tmp_path, b, b"\x00\xff\x80\x81 B")
    listing = _decl_fixture(
        tmp_path,
        project_entries=[
            {
                "path": a,
                "sha256": a_digest,
                "derived_from": b,
                "why": "derived from a declared file",
            },
            {"path": b, "sha256": b_digest, "why": "also declared"},
        ],
    ) + [a, b]
    defects = _defects(tmp_path, listing)
    assert a in defects and "ITSELF declared" in defects[a]


def test_an_OWNED_payload_cannot_be_cleared_at_the_repo_root_surface_by_delisting(tmp_path):
    """SECURITY, demonstrated end-to-end against the shipped command before the fix: plant an
    undecodable payload under this project, drop this project from `owners:`, declare the payload at
    the repo-root surface in the same edit — and the report went from exit 2 to exit 0 with the
    payload gone from the listing.

    Both halves live in the same file, so it was one edit. The ownership-prefix rule closes it: a
    path under `projects/` belongs to a project whether or not that project is registered.
    """
    import chipsim.guards.record_content as rc

    rel = f"projects/{THIS_PROJECT}/docs/figures/payload.pdf"
    digest = _write(tmp_path, rel, b"\x00\xff\x80\x81 DB90000\tFakine\tInChI=1S/C4H7NO4")
    entry = {"path": rel, "sha256": digest, "why": "cleared?"}

    for owners in ([THIS_PROJECT], []):
        listing = _decl_fixture(tmp_path, repo_entries=[entry], owners=owners) + [rel]
        assert rel not in rc.valid_declarations(listing, NOTHING_WAIVED, _surface_of(tmp_path)), (
            f"cleared with owners={owners}"
        )
        assert rel in rc.undecodable_unallowed(listing, NOTHING_WAIVED, _surface_of(tmp_path)), (
            "and it stays reported"
        )


def test_a_fabricated_project_directory_is_not_declarable_at_the_repo_root(tmp_path):
    """The variant that needs no registry edit at all, so the CI coverage oracle cannot see it:
    `projects/ghostproj/` has no marker, so it was 'unowned' and therefore repo-root declarable."""
    import chipsim.guards.record_content as rc

    ghost = "projects/ghostproj/data/blob.pdf"
    digest = _write(tmp_path, ghost, b"\x00\xff\x80\x81 DB90000")
    listing = _decl_fixture(
        tmp_path, repo_entries=[{"path": ghost, "sha256": digest, "why": "no such project"}]
    ) + [ghost]

    defects = _defects(tmp_path, listing)
    assert ghost in defects and "OWNERSHIP PREFIX" in defects[ghost]
    assert ghost not in rc.valid_declarations(listing, NOTHING_WAIVED, _surface_of(tmp_path))


def test_a_declaration_file_larger_than_the_bound_is_refused(tmp_path):
    """`yaml.safe_load` is safe against arbitrary object construction but not against alias
    expansion or a huge document, and a declaration file nobody can parse holds the gate
    permanently un-runnable."""
    import chipsim.guards.record_content as rc

    _decl_fixture(tmp_path)
    padding = "# " + ("x" * 80) + "\n"
    (tmp_path / rc.PROJECT_DECLARATION_FILE).write_text(
        'version: "1"\ndeclarations: []\n' + padding * 20_000
    )
    with pytest.raises(rc.RecordContentScanError, match="bound for declaration data"):
        rc._declaration_document(tmp_path, rc.PROJECT_DECLARATION_FILE)


def test_the_declaration_files_do_not_overclaim_what_derived_from_verifies():
    """Finding 2 is a DOCUMENTATION defect, and the dangerous kind: prose implying verification the
    tool does not perform invites the over-trust the mechanism exists to remove. The gate checks the
    source is tracked, readable, same-owner and not itself declared — NOT that the file derives
    from it."""
    repo_doc = (REPO_ROOT / "config/record_content_declarations.yaml").read_text()
    assert "does NOT verify that the declared file derives from" in repo_doc
    assert "a claim a reader can check" not in repo_doc, "the retired over-claim is back"

    project_doc = (PROJECT_ROOT / "configs/record_content_declarations.yaml").read_text()
    assert "does not check that this file actually derives from that source" in project_doc


# --- r2.25 E-13/E-13b/E-14/E-15 ----------------------------------------------------------------


def _report(tmp_path, monkeypatch, capsys, listing, policy=None):
    """Run the SHIPPED command against a fixture root and return (exit code, stdout, stderr).

    E-13b: assertions bind the observable a consumer sees. Every defect test before this asserted
    on the validator's return value, and 12 mutants walked through the whole suite as a result.
    """
    import chipsim.guards.record_content as rc
    from chipsim import pipeline
    from chipsim.ingest.drugbank_snapshot import DRUGBANK_CONTENT_POLICY

    monkeypatch.setattr(rc, "repo_root", lambda: tmp_path)
    monkeypatch.setattr(rc, "_tracked_listing", lambda root: (listing, []))
    monkeypatch.setattr(rc, "_refuse_a_scan_that_cannot_see_itself", lambda root, paths: None)
    monkeypatch.setattr(
        pipeline, "_record_content_policy", lambda: policy or DRUGBANK_CONTENT_POLICY
    )
    code = pipeline.main(["record-content-report"])
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def test_a_broken_declaration_file_still_renders_the_listing_and_exits_2(
    tmp_path, monkeypatch, capsys
):
    """E-13. Turning the whole gate to exit 3 hid WHICH file failed. The scan works; only the
    exemption data is unreadable, so: treat nothing as declared (fail-closed — more files fail,
    never fewer), still render the listing, exit 2, and name the file that is broken."""
    import chipsim.guards.record_content as rc

    payload = "docs/payload.bin"
    _write(tmp_path, payload, b"\x00\xff\x80\x81 OPAQUE")
    listing = _decl_fixture(tmp_path, owners=[THIS_PROJECT]) + [payload]
    (tmp_path / rc.PROJECT_DECLARATION_FILE).write_text("declarations: [\n  - path: x\n")

    code, out, err = _report(tmp_path, monkeypatch, capsys, listing)

    assert code == 2, f"not 3 — the scan worked; only the declaration data is broken\n{out}{err}"
    assert payload in out, "the listing must still be rendered, or the broken data hides it"
    assert rc.PROJECT_DECLARATION_FILE in out + err, "the broken FILE must be named"
    assert "nothing is declared" in (out + err).lower()


def test_an_absent_declaration_file_also_renders_and_exits_2(tmp_path, monkeypatch, capsys):
    """Absent is still not EMPTY — it produces a structural error and nothing declared, where an
    empty `declarations: []` produces a clean zero-count report. The difference is visible; what
    changed is that it no longer costs the operator the listing."""
    import chipsim.guards.record_content as rc

    payload = "docs/payload.bin"
    _write(tmp_path, payload, b"\x00\xff\x80\x81 OPAQUE")
    listing = _decl_fixture(tmp_path, owners=[THIS_PROJECT]) + [payload]
    (tmp_path / rc.REPO_DECLARATION_FILE).unlink()

    code, out, err = _report(tmp_path, monkeypatch, capsys, listing)
    assert code == 2
    assert payload in out
    assert rc.REPO_DECLARATION_FILE in out + err


def test_the_header_counts_declaration_defects_SEPARATELY(tmp_path, monkeypatch, capsys):
    """E-13. Mixing two categories into one `failing` number makes the summary wrong exactly where
    a reader checks first: every listed row read `[listed]` while the header claimed one failing."""
    rel = f"projects/{THIS_PROJECT}/docs/deleted.bin"
    listing = _decl_fixture(
        tmp_path,
        project_entries=[{"path": rel, "sha256": "0" * 64, "why": "long gone"}],
        owners=[THIS_PROJECT],
    )
    code, out, _err = _report(tmp_path, monkeypatch, capsys, listing)

    header = out.splitlines()[0]
    assert "undeclared undecodable files: 0" in header, header

    # THIS ASSERTION USED TO READ `"failing this gate: 0" in header`, with the justification "no
    # UNDECODABLE file fails here" — and it was PINNING THE DEFECT (r2.27 §11 QG). The number was
    # scoped to undecodable+missing rows, so a broken declaration failed the gate while the one
    # line a human reads first said nothing was failing. Two reviewers found it independently, and
    # the test named after the header's counts is what had made it look intended.
    #
    # The leading count stays scoped — it is "undeclared undecodable files" and it is 0 here. The
    # parenthetical is now the TOTAL failing, because that is the question a reader is asking when
    # they read a line beside a non-zero exit code.
    assert "failing this gate: 1" in header, (
        "the broken declaration fails this gate, so the header must say 1 — a header reading 0 "
        "beside exit 2 is the defect, not the contract"
    )
    assert "1 whose claim does not hold" in out
    assert code == 2, "and the exit code agrees with the number beside the word FAILING"


def test_every_defect_in_an_entry_is_reported_in_one_pass(tmp_path, monkeypatch, capsys):
    """E-15. A reader who learns their entry's next problem one gate run at a time is being made to
    bisect their own data.

    The fixture is wrong in TWO reportable ways, not three: the stale pin is never reached, because
    the container branch still short-circuits — deliberately, since a container IS a readable file
    and reporting both would print the same fact twice. `>= 2` was the weakest predicate that could
    still pass and could not have failed if the count regressed, so it is an equality now.
    """
    import chipsim.guards.record_content as rc

    monkeypatch.setattr(rc, "_refuse_a_scan_that_cannot_see_itself", lambda root, paths: None)
    rel = "projects/perturb-seq-eval/paper/fig.parquet"
    _write(tmp_path, rel, b"PAR1" + b"\x00" * 32)
    _write(tmp_path, "projects/perturb-seq-eval/pyproject.toml", b"[project]\n")
    listing = _decl_fixture(
        tmp_path,
        project_entries=[{"path": rel, "sha256": "b" * 64, "why": "wrong in several ways"}],
        owners=[THIS_PROJECT, "perturb-seq-eval"],
    ) + [rel, "projects/perturb-seq-eval/pyproject.toml"]

    reasons = [
        why
        for path, why in rc.declaration_defects(listing, NOTHING_WAIVED, _surface_of(tmp_path))
        if path == rel
    ]
    assert len(reasons) == 2, f"expected placement + container, got: {reasons}"
    joined = " ".join(reasons)
    assert "owns it" in joined, "the placement problem"
    assert "container" in joined, "and the container problem, in the SAME pass"


def test_the_declaration_surface_is_read_once_per_report(tmp_path, monkeypatch, capsys):
    """E-14, on the half that is CORRECTNESS rather than speed: with no snapshot, a concurrent edit
    yields a self-contradictory single report — rows marked FAILS HERE under an owner the footer
    says fails nobody. Reading once makes that impossible rather than unlikely."""
    import chipsim.guards.record_content as rc

    listing = _decl_fixture(tmp_path, owners=[THIS_PROJECT])
    reads: list[str] = []
    real = rc._declaration_document

    def counting(root, rel):
        reads.append(rel)
        return real(root, rel)

    monkeypatch.setattr(rc, "_declaration_document", counting)
    _report(tmp_path, monkeypatch, capsys, listing)

    assert len(reads) == 2, f"the two surfaces must be read exactly once each, got {reads}"


def test_no_guard_refusal_is_written_as_a_bare_assert():
    """`python -O` STRIPS assert statements. A guard written as `assert` does not weaken under
    optimisation — it VANISHES, and the file it was refusing is cleared in silence.

    This is the FAIL living in the API rather than in a test: the module's refusals must be
    statements the interpreter cannot remove.
    """
    import ast
    import inspect

    import chipsim.guards.record_content as rc

    source = inspect.getsource(rc)
    asserts = [node.lineno for node in ast.walk(ast.parse(source)) if isinstance(node, ast.Assert)]
    assert asserts == [], (
        f"bare assert(s) in the guard at line(s) {asserts} — `python -O` removes them, so the "
        "refusal disappears rather than weakening"
    )


def test_the_container_refusal_survives_python_O(tmp_path):
    """Call the REAL guard under -O and watch it refuse.

    The previous version of this test raised a RecordContentScanError it had constructed itself and
    then re-parsed the module source with `ast` — and `ast.parse` yields Assert nodes identically
    under -O, so that check was a byte-for-byte duplicate of the shape test with a subprocess
    wrapped around it. A mutant guarding the refusal with `not sys.flags.optimize` made it vanish
    EXACTLY AND ONLY under -O, and all three container/assert tests passed.
    """
    import subprocess
    import sys
    import textwrap

    script = textwrap.dedent(
        f"""
        import sys
        sys.path.insert(0, {str(PROJECT_ROOT)!r})
        import pathlib, yaml
        import chipsim.guards.record_content as rc

        root = pathlib.Path({str(tmp_path)!r})
        blob = root / "projects" / rc.THIS_PROJECT / "docs" / "blob.dat"
        blob.parent.mkdir(parents=True, exist_ok=True)
        blob.write_bytes(b"PAR1" + b"\\x00" * 32)
        (root / "config").mkdir(parents=True, exist_ok=True)
        (root / "projects" / rc.THIS_PROJECT / "configs").mkdir(parents=True, exist_ok=True)
        (root / rc.PROJECT_DECLARATION_FILE).write_text(yaml.safe_dump({{
            "version": "1",
            "declarations": [{{
                "path": f"projects/{{rc.THIS_PROJECT}}/docs/blob.dat",
                "sha256": "0" * 64,
                "why": "claims to be opaque",
            }}],
        }}))
        (root / rc.REPO_DECLARATION_FILE).write_text(yaml.safe_dump(
            {{"version": "1", "declarations": []}}
        ))

        print("OPTIMIZE", sys.flags.optimize)
        try:
            rc.assert_no_container_is_declared(root)
        except rc.RecordContentScanError as exc:
            print("REFUSED:", exc)
        else:
            print("CLEARED-IN-SILENCE")
        """
    )
    out = subprocess.run(
        [sys.executable, "-O", "-c", script], capture_output=True, text=True, check=False
    )
    assert "OPTIMIZE 1" in out.stdout, (
        f"the child must really be optimised, or this test degrades to the ordinary case\n{out.stderr}"
    )
    assert "REFUSED:" in out.stdout, out.stdout + out.stderr
    assert "declared readable container" in out.stdout


def test_the_content_policy_has_no_default_because_one_half_would_be_fail_open():
    """DES-1, measured by a reviewer rather than argued.

    The module used to default both predicates to "refuse nothing" and claim in its own docstring
    that the result was fail-closed. It is fail-closed for `readability_waived` — waive nothing and
    the scan reads MORE. It is fail-OPEN for `content_exempt`: exempt nothing and the "declared AND
    content-excluded" defect never fires, so the declaration HOLDS and its file is CLEARED.

    Two predicates with opposite safe directions cannot share a default, and a docstring covering
    both can only be half true. So there is no default, and this test says why in a form that fails
    if someone reintroduces one.
    """
    import inspect

    import chipsim.guards.record_content as rc

    for name in (
        "declaration_defects",
        "valid_declarations",
        "undecodable_unallowed",
        "undeclared_report",
        "failing_undeclared",
        "render_undeclared_report",
    ):
        parameter = inspect.signature(getattr(rc, name)).parameters["policy"]
        assert parameter.default is inspect.Parameter.empty, (
            f"{name}() defaults its policy again — `content_exempt` defaulting to 'exempt nothing' "
            "CLEARS a file the real policy fails"
        )


def test_exempting_nothing_is_the_QUIETER_direction(tmp_path):
    """The measurement itself, so the asymmetry is recorded as behaviour and not only as prose."""
    import chipsim.guards.record_content as rc
    from chipsim.ingest.drugbank_snapshot import DRUGBANK_CONTENT_POLICY

    rel = min(DRUGBANK_ID_LEDGER)
    digest = _write(tmp_path, rel, b"\x00\xff\x80\x81 OPAQUE")
    listing = _decl_fixture(
        tmp_path, project_entries=[{"path": rel, "sha256": digest, "why": "w"}]
    ) + [rel]
    if rc.path_owner(rel, frozenset({THIS_PROJECT})) != THIS_PROJECT:
        pytest.skip(
            "this ledger entry is not owned by this project, so the fixture cannot declare it"
        )

    lenient = rc.undecodable_unallowed(listing, NOTHING_WAIVED, _surface_of(tmp_path))
    strict = rc.undecodable_unallowed(listing, DRUGBANK_CONTENT_POLICY, _surface_of(tmp_path))
    assert rel not in lenient, "exempting nothing CLEARS it — the quieter direction"
    assert rel in strict, "the real policy reports it"


def test_a_BROKEN_registry_narrows_to_nothing_rather_than_widening(tmp_path, monkeypatch, capsys):
    """CODE-1, and the banner was mine. A broken declaration file set `registry=None`, which
    `recognised_owners` read as "no registry yet" and answered with the WIDER marker-backed set — so
    a path under an unregistered owner stopped being unowned and stopped failing, while the banner
    printed directly above it asserted "more files fail, never fewer".

    UNKNOWN is not ABSENT. A registry that cannot be read narrows to nothing: every path is unowned,
    and unowned fails HERE.
    """
    import chipsim.guards.record_content as rc
    from chipsim import pipeline
    from chipsim.ingest.drugbank_snapshot import DRUGBANK_CONTENT_POLICY

    payload = "libs/ghost-lib/payload.bin"
    _write(tmp_path, payload, b"\x00\xff\x80\x81 OPAQUE")
    _write(tmp_path, "libs/ghost-lib/pyproject.toml", b"[project]\n")
    listing = _decl_fixture(tmp_path, owners=[THIS_PROJECT]) + [
        payload,
        "libs/ghost-lib/pyproject.toml",
    ]

    monkeypatch.setattr(rc, "repo_root", lambda: tmp_path)
    monkeypatch.setattr(rc, "_tracked_listing", lambda root: (listing, []))
    monkeypatch.setattr(rc, "_refuse_a_scan_that_cannot_see_itself", lambda root, paths: None)
    monkeypatch.setattr(pipeline, "_record_content_policy", lambda: DRUGBANK_CONTENT_POLICY)

    healthy = pipeline.main(["record-content-report"])
    healthy_out = capsys.readouterr().out
    assert "[FAILS HERE]" in healthy_out and healthy == 2

    # The ONLY change: the repo-root declaration file stops parsing.
    (tmp_path / rc.REPO_DECLARATION_FILE).write_text("owners: [\n")
    broken = pipeline.main(["record-content-report"])
    broken_out = capsys.readouterr().out

    assert broken == 2
    assert "owner=ghost-lib" not in broken_out, (
        "a broken registry attributed the payload to an unregistered owner and marked it [listed]"
    )
    assert "[FAILS HERE]" in broken_out, "the banner promises more files fail, never fewer"


def test_the_verdicts_are_adjudicated_once_per_report(tmp_path, monkeypatch, capsys):
    """CODE-2. The YAML was snapshotted; the VERDICTS were not. `declaration_defects` ran three
    times per report and re-read the filesystem each time, so a pinned artifact was hashed three
    times and an artifact rebuilt between passes produced a single report that disagreed with
    itself — E-14's failure surviving inside the fix for E-14."""
    import chipsim.guards.record_content as rc
    from chipsim import pipeline
    from chipsim.ingest.drugbank_snapshot import DRUGBANK_CONTENT_POLICY

    rel = f"projects/{THIS_PROJECT}/art.bin"
    digest = _write(tmp_path, rel, b"\x00\xff\x80\x81 ART")
    listing = _decl_fixture(
        tmp_path,
        project_entries=[{"path": rel, "sha256": digest, "why": "pinned"}],
        owners=[THIS_PROJECT],
    ) + [rel]

    hashed: list[str] = []
    real = rc._sha256
    monkeypatch.setattr(rc, "_sha256", lambda p: (hashed.append(str(p)), real(p))[1])
    monkeypatch.setattr(rc, "repo_root", lambda: tmp_path)
    monkeypatch.setattr(rc, "_tracked_listing", lambda root: (listing, []))
    monkeypatch.setattr(rc, "_refuse_a_scan_that_cannot_see_itself", lambda root, paths: None)
    monkeypatch.setattr(pipeline, "_record_content_policy", lambda: DRUGBANK_CONTENT_POLICY)

    pipeline.main(["record-content-report"])
    capsys.readouterr()
    assert hashed.count(str(tmp_path / rel)) == 1, (
        f"the pinned artifact was hashed {hashed.count(str(tmp_path / rel))} times; three passes "
        "over the filesystem is how one report comes to disagree with itself"
    )


def test_the_header_counts_DECLARATIONS_not_defects(tmp_path, monkeypatch, capsys):
    """CODE-6. E-15 made defects multi-valued per entry while the header still called them
    declarations, so ONE bad declaration reported "3 whose claim does not hold"."""
    import chipsim.guards.record_content as rc
    from chipsim import pipeline
    from chipsim.ingest.drugbank_snapshot import DRUGBANK_CONTENT_POLICY

    rel = "projects/other/gone.bin"
    listing = _decl_fixture(
        tmp_path,
        repo_entries=[{"path": rel, "sha256": "0" * 64, "why": "wrong in several ways"}],
        owners=[THIS_PROJECT],
    )
    monkeypatch.setattr(rc, "repo_root", lambda: tmp_path)
    monkeypatch.setattr(rc, "_tracked_listing", lambda root: (listing, []))
    monkeypatch.setattr(rc, "_refuse_a_scan_that_cannot_see_itself", lambda root, paths: None)
    monkeypatch.setattr(pipeline, "_record_content_policy", lambda: DRUGBANK_CONTENT_POLICY)

    pipeline.main(["record-content-report"])
    out = capsys.readouterr().out
    assert "1 whose claim does not hold" in out, out.splitlines()[1]


# --- r2.26 §10: one test per mutant that survived the whole suite ------------------------------


def test_a_broken_declaration_file_ALONE_is_still_exit_2(tmp_path, monkeypatch, capsys):
    """MUT-5, and it is the r2.25 ruling itself left unpinned.

    `2 if failing or surface.structural_error else 0` degrades to `2 if failing else 0` with the
    whole suite green, because every existing broken-declaration fixture ALSO plants a failing
    payload — so `failing` is non-empty and the structural term is redundant in every one of them.
    This fixture has nothing else wrong with it, which is the only way the term can be observed.
    """
    import chipsim.guards.record_content as rc

    listing = _decl_fixture(tmp_path, owners=[THIS_PROJECT])
    (tmp_path / rc.PROJECT_DECLARATION_FILE).write_text("declarations: [\n  - path: x\n")

    code, out, _err = _report(tmp_path, monkeypatch, capsys, listing)
    header = out.splitlines()[0]
    assert "undeclared undecodable files: 0" in header, header
    # r2.27 §11 DESIGN-5: this line now reads UNREADABLE rather than "0", because a count of zero
    # and a count that could not be taken must not print the same glyph.
    assert "declarations read: UNREADABLE" in out, out
    assert code == 2, "a broken declaration file ALONE must still be exit 2"
    # r2.27 E-20: the structural error is carried by the HEADER, not left in a paragraph below.
    # Without this the two numbers a reader checks first both read clean while the process exits 2.
    assert "DECLARATION DATA UNREADABLE" in header, header


def test_an_absent_surface_is_DISTINGUISHABLE_from_an_empty_one(tmp_path, monkeypatch, capsys):
    """MUT-18. The existing absent-file test was vacuous: with the refusal deleted it still passed,
    because the unlinked file was in the listing (so it counted as unresolvable-and-failing) and the
    footer mentions that path unconditionally. Neither assertion could tell "absent" from "empty",
    which is the one distinction the function exists for."""
    import chipsim.guards.record_content as rc

    listing = _decl_fixture(tmp_path, owners=[THIS_PROJECT])
    (tmp_path / rc.REPO_DECLARATION_FILE).unlink()

    code, out, _err = _report(tmp_path, monkeypatch, capsys, listing)
    assert "is ABSENT" in out, out
    assert "NOTHING IS DECLARED" in out
    assert code == 2


def test_the_command_passes_THIS_PROJECTS_policy_not_the_guards_default(
    tmp_path, monkeypatch, capsys
):
    """MUT-16 and MUT-17. Nothing bound the policy seam at the report level: the CLI calling
    `render_undeclared_report()` with no policy, and `_render_for_root` discarding the policy it was
    handed, each passed all 895 tests — because on the live tree the two render byte-identical
    output (zero declarations, and the excluded-files set is empty).

    A ledger path, declared and READABLE, separates them: under this project's policy it is exempt
    by the content mechanism, so declaring it too is a double exemption.
    """
    rel = min(DRUGBANK_ID_LEDGER)
    _write(tmp_path, rel, b"readable: yes\n")
    listing = _decl_fixture(
        tmp_path,
        project_entries=[{"path": rel, "sha256": "a" * 64, "why": "x"}],
        owners=[THIS_PROJECT],
    ) + [rel]

    code, out, _err = _report(tmp_path, monkeypatch, capsys, listing)
    assert "exempted twice" in out, (
        "the command must pass THIS project's policy; the guard's own default exempts nothing"
    )
    assert "1 whose claim does not hold (2 defect(s))" in out
    assert code == 2


def test_the_readability_waiver_is_consulted_and_obeyed(tmp_path):
    """MUT-22. The waiver half of the policy seam — the thing the whole extraction docstring is
    about — was never consulted by any test, and the DrugBank predicate cannot demonstrate it: a
    dispatch message is waived only when it DECODES, which is exactly when it would not have been
    reported anyway. Bind the predicate directly instead of through DrugBank."""
    import chipsim.guards.record_content as rc

    rel = "docs/opaque.bin"
    _write(tmp_path, rel, b"\x00\xff\x80\x81 OPAQUE")
    listing = _surfaced(tmp_path, [rel])

    seen: list[str] = []

    def waive(root, candidate):
        seen.append(candidate)
        return candidate == rel

    waiving = rc.ContentPolicy(
        readability_waived=waive, content_exempt=rc.nothing_is_content_exempt
    )
    assert rc.undecodable_unallowed(listing, NOTHING_WAIVED, _surface_of(tmp_path)) == [rel], (
        "unwaived: reported"
    )
    assert rc.undecodable_unallowed(listing, waiving, _surface_of(tmp_path)) == [], (
        "waived: not reported"
    )
    assert rel in seen, "the waiver must actually be consulted, not merely accepted"


def test_the_ledger_is_not_readability_waived_and_a_binary_is_not_a_message(tmp_path):
    """The boundary the DrugBank waiver actually draws, asserted through the policy rather than
    around it. Swapping the two predicates silently waives the ledger — whose content IS read, so
    its readability is exactly what the check is for."""
    ledger = min(DRUGBANK_ID_LEDGER)
    payload = ".claude/usr/matthew-mo/lung-on-chipsim/dispatches/leak.pdf"
    for rel in (ledger, payload):
        _write(tmp_path, rel, b"\x00\xff not text")
    listing = _surfaced(tmp_path, [ledger, payload])

    assert undecodable_unallowed(listing, DRUGBANK_CONTENT_POLICY, _surface_of(tmp_path)) == sorted(
        [ledger, payload]
    ), "the ledger is NOT readability-waived, and a binary at a dispatch path is not a message"


def test_three_defects_for_one_entry_are_all_reported(tmp_path, monkeypatch, capsys):
    """MUT-8 and MUT-9: two of the removed short-circuits were unbound, because every defect test
    asserts "this reason appears" — satisfied by any ONE defect — and the count it checks is of
    PATHS, not defects. The header count is the observable that distinguishes them."""
    rel = "projects/perturb-seq-eval/paper/fig.pdf"  # declared, never written, never tracked
    _write(tmp_path, "projects/perturb-seq-eval/pyproject.toml", b"[project]\n")
    listing = _decl_fixture(
        tmp_path,
        repo_entries=[{"path": rel, "sha256": "a" * 64, "why": "x"}],
        owners=[THIS_PROJECT, "perturb-seq-eval"],
    ) + ["projects/perturb-seq-eval/pyproject.toml"]

    code, out, _err = _report(tmp_path, monkeypatch, capsys, listing)
    assert "1 whose claim does not hold (3 defect(s))" in out, out
    assert code == 2


def test_a_declared_dispatch_payload_reports_both_of_its_defects(tmp_path, monkeypatch, capsys):
    """MUT-10: the dispatch short-circuit was unbound."""
    rel = ".claude/usr/matthew-mo/lung-on-chipsim/dispatches/leak.pdf"
    _write(tmp_path, rel, b"plain readable text\n")
    listing = _decl_fixture(
        tmp_path,
        repo_entries=[{"path": rel, "sha256": "a" * 64, "why": "x"}],
        owners=[THIS_PROJECT],
    ) + [rel]

    code, out, _err = _report(tmp_path, monkeypatch, capsys, listing)
    assert "1 whose claim does not hold (2 defect(s))" in out, out
    assert "DOUBLE-EXEMPT" in out and "scan CAN read it" in out
    assert code == 2


def test_the_guard_does_not_import_anything_from_ingest():
    """The extraction's entire premise, asserted rather than assumed. One
    `from chipsim.ingest.drugbank_snapshot import ...` would re-merge the modules with the suite
    green, and the dependency direction is the only thing keeping the guard generic."""
    import ast
    import inspect

    import chipsim.guards.record_content as rc

    modules: list[str] = []
    for node in ast.walk(ast.parse(inspect.getsource(rc))):
        if isinstance(node, ast.Import):
            modules += [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
    offenders = [m for m in modules if "ingest" in m or "drugbank" in m]
    assert offenders == [], f"the guard must not know about DrugBank: {offenders}"


def test_no_shipped_module_writes_a_refusal_as_a_bare_assert():
    """Widened from one module to the whole package: `python -O` strips asserts everywhere, and
    `output_roots` and `pipeline` both carry refusals today."""
    import ast
    import pathlib

    import chipsim

    offenders: list[str] = []
    for path in sorted(pathlib.Path(chipsim.__file__).parent.rglob("*.py")):
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Assert):
                offenders.append(f"{path.name}:{node.lineno}")
    assert offenders == [], (
        f"bare assert(s) in shipped code at {offenders} — python -O removes them"
    )


# --- r2.27 §11 test review: the kept half of the waiver was bound by nothing --------------------


def test_the_readability_waiver_actually_waives_when_the_set_is_not_empty(tmp_path, monkeypatch):
    """D1, and the most serious finding of the review. E-19 deleted the dispatch clause and left
    `rel in DRUGBANK_ID_EXCLUDED_FILES`. Replacing that whole surviving body with `return False`
    passed every test in the suite — the mechanism I kept was held in place by nothing.

    It is inert today only because the set is EMPTY, which is a fact about the data, not the code:
    the docstring says "an undecodable file added to it would genuinely be waived here", and that
    sentence was the only thing asserting it.

    MY FIRST ATTEMPT AT THIS TEST WAS ITSELF VACUOUS, and the mutant caught it. Patching the set
    also flips `_content_exempt`, which reads the SAME set (a declaration on top of a content
    exclusion is the double-exemption defect), so the file was cleared by the content half while the
    waiver returned False — the test passed against the mutant it was written to kill. The two
    halves cannot be told apart through the set, so the waiver is paired here with a content half
    that exempts NOTHING: then the only route to a cleared file is the waiver itself.
    """
    import chipsim.guards.record_content as rc
    import chipsim.ingest.drugbank_snapshot as ds

    rel = f"projects/{THIS_PROJECT}/docs/opaque.bin"
    other = f"projects/{THIS_PROJECT}/docs/other.bin"
    _write(tmp_path, rel, b"\x00\xff\x80\x81 not text")
    _write(tmp_path, other, b"\x00\xff\x80\x81 also not text")
    listing = _surfaced(tmp_path, [rel, other])
    surface = _surface_of(tmp_path)

    assert ds.DRUGBANK_ID_EXCLUDED_FILES == frozenset(), (
        "this test is about what happens when the set is NOT empty; if it has grown, the fixture "
        "below needs to account for the real entries"
    )

    # The REAL waiver, and a content half that exempts nothing — so nothing but the waiver can
    # clear a file here.
    waiver_only = _rc_policy(
        readability_waived=ds._readability_waived, content_exempt=_rc_nothing_exempt
    )

    # Empty set, the live configuration: both files are reported.
    assert rc.undecodable_unallowed(listing, waiver_only, surface) == [rel, other]

    # Non-empty set: the configuration the surviving branch exists to serve. `rel` is waived and
    # `other` is not, so the waiver is shown to fire AND to stay a path list rather than a blanket.
    monkeypatch.setattr(ds, "DRUGBANK_ID_EXCLUDED_FILES", frozenset({rel}))
    assert rc.undecodable_unallowed(listing, waiver_only, surface) == [other], (
        "the waiver did not waive — the kept half of `_readability_waived` is inert and `return "
        "False` is an exact replacement for it"
    )


# --- r2.27 §11 quality gate: the link refusal guarded ONE level --------------------------------


def test_a_link_hides_content_at_ANY_depth_not_only_at_the_top(tmp_path):
    """S11-20, and it is a TRUE FALSE CLEAN — the worst outcome this guard has.

    `for name in handle:` iterates the ROOT GROUP ONLY, while `visititems` silently skips links at
    every depth. So the identical link is refused at the top level and invisible one group down:
    the container is READ, is never listed as undecodable, and yields zero accession hits, while
    part of its graph was never visited. Measured before the fix:

        link at TOP level    -> chunks=None      readable=False
        link NESTED in /uns  -> chunks=['uns']   readable=True

    The comment above that loop states the exact hazard — "a container whose only members were
    links produced an empty chunk and passed as 'read'" — and then guards one level. That is this
    iteration's recurring shape: a mechanism stopping one layer short of where the defect lives.
    """
    h5py = pytest.importorskip("h5py")
    from chipsim.guards.decoding import _is_readable, _scan_chunks

    secret = tmp_path / "secret.h5"
    with h5py.File(secret, "w") as handle:
        handle.create_dataset("payload", data=[f"{REAL} {STRUCTURE}".encode()])

    cases = {
        "top-level": ("top.h5ad", ""),
        "nested": ("nested.h5ad", "uns"),
        "deeply nested": ("deep.h5ad", "a/b/c"),
    }
    for label, (filename, group) in cases.items():
        container = tmp_path / filename
        with h5py.File(container, "w") as handle:
            parent = handle.create_group(group) if group else handle
            parent["ext"] = h5py.ExternalLink(str(secret), "payload")
        assert _scan_chunks(container) is None, (
            f"{label}: the container was READ while a link hid part of its graph"
        )
        assert not _is_readable(container), (
            f"{label}: an unfollowed link must make the container UNREADABLE, so it is reported "
            "and cannot be cleared without a human looking at it"
        )


def test_a_soft_link_nested_in_the_same_file_is_still_refused(tmp_path):
    """The narrower half. A SoftLink hides nothing today — `visititems` reaches the target by its
    real path — so refusing it is a fail-CLOSED choice rather than a correctness fix, and it must
    be stated as such rather than implied to be closing a hole."""
    h5py = pytest.importorskip("h5py")
    from chipsim.guards.decoding import _scan_chunks

    path = tmp_path / "soft.h5ad"
    with h5py.File(path, "w") as handle:
        handle.create_dataset("obs/real", data=[REAL.encode()])
        handle.create_group("uns")["alias"] = h5py.SoftLink("/obs/real")

    assert _scan_chunks(path) is None, "a nested soft link must be refused like a top-level one"


def test_a_container_of_plain_nested_groups_is_still_read(tmp_path):
    """The anti-overcorrection half: refusing links must not refuse ordinary nesting. Without this,
    "refuse every group" would pass the test above and break every real h5ad."""
    from chipsim.guards.decoding import _is_readable, _scan_chunks

    path = _hdf5(tmp_path, "nested_ok.h5ad", {"uns/deep/obs/perturbation": [REAL.encode()]})
    chunks = _scan_chunks(path)
    assert chunks, "a normally-nested container must still be READ"
    assert REAL in "\n".join(chunks)
    assert _is_readable(path)


# --- r2.28 E6-7: the SHIPPED COMMAND answers the accession question ----------------------------


def test_the_shipped_command_fails_on_a_real_accession_in_tracked_content(
    tmp_path, monkeypatch, capsys
):
    """r2.28. E6-7 was DECLARED UNMET: `record-content-report` composed readability, declarations
    and ownership, and `real_accession_hits` / `ledger_tuple_hits` were unreachable from it, while
    `enforce_record_content` had no caller outside its own test file. So the accession half was
    enforced by pytest and by nothing a consumer runs — E6-7's own stated defect, surviving inside
    the fix for it.

    That was not merely a coverage gap. This command's exit 0 was quoted UPWARD as evidence that
    the record-content invariant held: by this agent in dispatches and commit bodies, and by the
    CTO as independent verification. A mechanism enforcing three halves may not be cited for the
    fourth.

    So the binding assertion is on the COMMAND, not on the composition root: a readable, decodable,
    perfectly ordinary text file carrying a real accession. Nothing in the other three halves can
    see it — it decodes, it is not declared, and it is owned — so if this exits 0 the accession
    half is not running.
    """
    rel = f"projects/{THIS_PROJECT}/docs/leak.txt"
    _plant(tmp_path, rel, f"see {REAL} for details\n")
    listing = _decl_fixture(tmp_path, owners=[THIS_PROJECT]) + [rel]

    code, out, _err = _report(tmp_path, monkeypatch, capsys, listing)

    assert code == 2, (
        "the shipped command exited clean over a tracked file carrying a real accession — the "
        "accession half is not wired into it, which is E6-7 unmet"
    )
    assert "REAL ACCESSIONS IN TRACKED CONTENT:" in out
    assert rel in out
    # The file is readable and undeclared-but-owned, so the OTHER three halves clear it. If this
    # assertion ever fails the fixture has stopped isolating the accession half and the test above
    # would pass for the wrong reason.
    assert "undeclared undecodable files: 0" in out.splitlines()[0], (
        "the fixture must be clean on the other three halves, or exit 2 proves nothing about "
        "which half produced it"
    )


def test_the_shipped_command_reports_a_LEDGER_tuple_hit_too(tmp_path, monkeypatch, capsys):
    """The narrower half of the same clause, and the one a mutant deleted with the suite green:
    `ledger_tuple_hits` could be replaced with `[]` and nothing noticed, because the only entry-
    point test exercised `real_accession_hits` alone.

    The ledger branch is distinguishable in the output by the LINE NUMBER it emits, which the
    content branch does not — so this cannot pass on the other half's work.
    """
    from chipsim.ingest.drugbank_snapshot import DRUGBANK_ID_LEDGER

    ledger_rel = min(DRUGBANK_ID_LEDGER)  # deterministic pick from a frozenset
    _plant(tmp_path, ledger_rel, f"# {REAL}\n# {STRUCTURE}\n")
    listing = _decl_fixture(tmp_path, owners=[THIS_PROJECT]) + [ledger_rel]

    # Precondition: the ledger half genuinely fires on this fixture. Without this the assertions
    # below could pass over an empty ledger — the vacuity family this suite keeps counting.
    assert ledger_tuple_hits(tmp_path), "the fixture does not exercise the ledger half at all"

    code, out, _err = _report(tmp_path, monkeypatch, capsys, listing)

    assert code == 2
    assert f"{ledger_rel}:1 " in out, (
        "the ledger branch emits a LINE NUMBER; its absence means the report came from the "
        "content branch and the ledger half is unbound"
    )


# --- r2.28 §11 QG: every bound in decoding.py was inert -----------------------------------------


def test_the_scan_size_ceiling_reports_rather_than_reads(tmp_path, monkeypatch):
    """Every ceiling in `decoding.py` survived mutation to 1<<60 with the suite green, under a
    module docstring saying "every bound in this module was set by a measurement, not a guess".
    A bound no test can feel is a bound that reads as coverage.

    Pinned in BOTH directions, because a one-sided test passes against "refuse everything".
    """
    import chipsim.guards.decoding as _decoding

    target = tmp_path / "plain.txt"
    target.write_text("x" * 100)  # readable UTF-8: only the ceiling can make it unreadable

    monkeypatch.setattr(_decoding, "_MAX_SCAN_BYTES", 16)
    _decoding._READABILITY_CACHE.clear()
    assert _decoding._scan_chunks(target) is None, "the size ceiling did not refuse the file"
    assert not _decoding._is_readable(target)

    monkeypatch.setattr(_decoding, "_MAX_SCAN_BYTES", 1024)
    _decoding._READABILITY_CACHE.clear()
    assert _decoding._is_readable(target), (
        "the same file must be readable under a ceiling above its size, or this test would pass "
        "against an implementation that refuses everything"
    )


def test_a_variable_length_dataset_is_bounded_by_what_it_MATERIALISES(tmp_path, monkeypatch):
    """S11-6. `node.nbytes` is `size * dtype.itemsize`, and `np.dtype("O").itemsize` is 8 — a
    POINTER width — so a vlen-string dataset reported 8 bytes per element however long its strings
    were. Measured: 1,000 x 1 KiB strings report 8,000 bytes and materialise 1,024,000, a 128x
    understatement, so the 64 MiB ceiling admitted ~8.6 GB. h5ad obs/var are exactly this dtype —
    the datasets this reader exists to read.
    """
    h5py = pytest.importorskip("h5py")
    import numpy as np

    import chipsim.guards.decoding as _decoding

    path = tmp_path / "vlen.h5ad"
    with h5py.File(path, "w") as handle:
        vlen = h5py.special_dtype(vlen=str)
        node = handle.create_dataset("obs/p", (200,), dtype=vlen)
        node[:] = ["Y" * 512] * 200

    with h5py.File(path, "r") as handle:
        reported = handle["obs/p"].nbytes
    materialised = 200 * 512
    assert np.dtype("O").itemsize == 8
    assert reported < materialised, (
        "the fixture does not reproduce the understatement, so this test proves nothing"
    )

    # A ceiling ABOVE what it reports but BELOW what it materialises. The old check compared
    # against `nbytes` and would have let this straight through.
    monkeypatch.setattr(_decoding, "_MAX_DATASET_BYTES", (reported + materialised) // 2)
    _decoding._READABILITY_CACHE.clear()
    assert _decoding._scan_chunks(path) is None, (
        "the dataset was read despite materialising past the ceiling — the bound is still being "
        "taken on pointer widths"
    )

    monkeypatch.setattr(_decoding, "_MAX_DATASET_BYTES", materialised * 4)
    _decoding._READABILITY_CACHE.clear()
    chunks = _decoding._scan_chunks(path)
    assert chunks and "Y" * 512 in "\n".join(chunks), (
        "and under a sufficient ceiling the content must still be READ and scannable"
    )


def test_the_container_total_is_bounded_not_just_each_dataset(tmp_path, monkeypatch):
    """S11-7. `_scan_chunks` did `list(...)` over the chunk generator, so `_PARQUET_BATCH_ROWS`
    bounded one batch and nothing else, and the per-dataset HDF5 ceiling was applied N times with
    no cap on N. Measured by the reviewer: a 4,140-byte parquet yielded 11 chunks totalling
    20,588,497 bytes held simultaneously.

    The aggregate refusal must be REPORTED, never a crash and never a declaration-shaped remedy.
    """
    h5py = pytest.importorskip("h5py")
    import chipsim.guards.decoding as _decoding

    path = tmp_path / "many.h5ad"
    with h5py.File(path, "w") as handle:
        for i in range(12):
            handle.create_dataset(f"g{i}/d", data=[("Z" * 400).encode()])

    # Each dataset is far below the per-dataset ceiling; only the TOTAL exceeds this.
    monkeypatch.setattr(_decoding, "_MAX_CONTAINER_BYTES", 1200)
    _decoding._READABILITY_CACHE.clear()
    assert _decoding._scan_chunks(path) is None, (
        "the container total is unbounded — the per-dataset ceiling is applied N times with no "
        "cap on N"
    )

    monkeypatch.setattr(_decoding, "_MAX_CONTAINER_BYTES", 1 << 30)
    _decoding._READABILITY_CACHE.clear()
    assert _decoding._scan_chunks(path), "under a sufficient total the container must still read"


def test_the_shipped_ceilings_are_actually_ceilings():
    """The three tests above bind the MECHANISM by monkeypatching the constants — and that is
    exactly why they are not enough. I ran the reviewer's mutation against them and ALL THREE
    SURVIVED with every ceiling raised to `1 << 60`, because a test that patches the constant
    cannot feel the shipped one. Proving a ceiling is enforced is not proving the ceiling is a
    bound, and I only learned the difference by running the mutant rather than by reasoning.

    So this pins the VALUES. A ceiling larger than any machine's memory is not a ceiling, and the
    module docstring says each was "set by a measurement, not a guess" — a claim nothing checked.
    The upper bounds are deliberately loose (these are DoS ceilings, not correctness constants);
    what they exclude is the mutant, and anything else effectively infinite.
    """
    import chipsim.guards.decoding as _decoding

    ceilings = {
        "_MAX_SCAN_BYTES": _decoding._MAX_SCAN_BYTES,
        "_MAX_DATASET_BYTES": _decoding._MAX_DATASET_BYTES,
        "_MAX_CONTAINER_BYTES": _decoding._MAX_CONTAINER_BYTES,
    }
    for name, value in ceilings.items():
        assert 0 < value <= 2 * 1024**3, (
            f"{name} is {value}, which is not a bound any machine can be protected by. A guard "
            f"that OOMs produces no verdict at all."
        )
    assert _decoding._MAX_DATASET_BYTES <= _decoding._MAX_CONTAINER_BYTES, (
        "a per-dataset ceiling above the whole-container ceiling makes the aggregate unreachable"
    )
    assert 0 < _decoding._PARQUET_BATCH_ROWS <= 1_000_000, (
        "the batch size is what keeps one conversion peak bounded; unbounded, the batching is "
        "decorative"
    )
    assert 0 < _decoding._VLEN_SLICE_ELEMENTS <= 1_000_000


def test_a_NUL_FREE_binary_is_still_reported_not_decoded_into_mojibake(tmp_path):
    """The printable-ratio floor was inert: `printable / len(text) >= 0.9` mutated to `>= 0.0`
    SURVIVED the whole suite. Code correct, nothing bound it.

    The NUL half is well covered, and that is exactly why the ratio half was not: the one fixture
    for it is a PNG header, which contains NUL bytes and dies on the earlier branch. A NUL-free
    binary — a raw deflate stream, an encrypted blob, a PDF object stream — decodes to mojibake
    under latin-1, `_is_readable` returns True, the accession regex finds nothing, and the file is
    never listed. That is a false clean.
    """
    import chipsim.guards.decoding as _decoding

    data = bytes(b for b in range(1, 256) if b != 0) * 40
    text = data.decode("latin-1")
    printable = sum(ch.isprintable() or ch in "\r\n\t" for ch in text)

    # The fixture's own preconditions. Without these the test could pass for the NUL reason, which
    # is the branch it is NOT about.
    assert b"\x00" not in data, "this fixture must not be caught by the NUL branch"
    assert printable / len(text) < 0.9, "and it must genuinely be below the ratio floor"

    assert _decoding._decode_text(data) is None, (
        "a NUL-free binary decoded into mojibake — it would scan clean and never be listed"
    )

    rel = "docs/blob.bin"
    _write(tmp_path, rel, data)
    assert undecodable_unallowed(
        _surfaced(tmp_path, [rel]), NOTHING_WAIVED, _surface_of(tmp_path)
    ) == [rel]

    # The positive control: a mostly-printable latin-1 document must STILL decode, or this test
    # would pass against an implementation that refuses every latin-1 file.
    readable = ("caf\xe9 " * 200).encode("latin-1")
    assert _decoding._decode_text(readable) is not None, (
        "the ratio floor must not reject ordinary latin-1 text"
    )


# --- §12.5 (r2.28): A COMMIT GATE READS THE BYTES IT CERTIFIES ---------------------------------


def _diverged_repo(tmp_path, rel, staged: bytes, on_disk: bytes):
    """A real repo whose INDEX and WORKTREE disagree about one tracked file."""
    root = _init_repo(tmp_path)
    for surface_rel in (
        "config/record_content_declarations.yaml",
        f"projects/{THIS_PROJECT}/configs/record_content_declarations.yaml",
    ):
        target = root / surface_rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text('version: "1"\ndeclarations: []\n')
    marker = root / f"projects/{THIS_PROJECT}/pyproject.toml"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text("[project]\nname = 'x'\n")

    payload = root / rel
    payload.parent.mkdir(parents=True, exist_ok=True)
    payload.write_bytes(staged)
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
    payload.write_bytes(on_disk)  # ...and the working copy now says something else
    return root


def test_the_gate_reads_the_STAGED_bytes_not_the_working_file(tmp_path, monkeypatch):
    """r2.28. The guard listed `git ls-files -s` — THE INDEX — and read `root/rel` from the
    WORKTREE. Reproduced end-to-end before the fix: the index held a payload, the disk held clean
    text, the guard read clean, and the commit would have carried the payload. A gate certifying
    bytes other than the ones being committed is not a gate.

    Divergence is deliberately NOT a refusal — that would break ordinary in-progress development,
    and a control people must disable is not a control. The gate reads the copy it certifies.
    """
    import chipsim.guards.record_content as rc

    # The witness refuses a tmp tree because it does not contain this package — correct, and
    # not what these tests are about. Patched exactly as the rest of the suite does.
    monkeypatch.setattr(rc, "_refuse_a_scan_that_cannot_see_itself", lambda root, paths: None)

    rel = f"projects/{THIS_PROJECT}/docs/payload.txt"
    root = _diverged_repo(
        tmp_path,
        rel,
        staged=f"see {REAL} for details\n".encode(),
        on_disk=b"clean text, nothing to see\n",
    )

    with rc.scan_context(root, DRUGBANK_CONTENT_POLICY, "staged") as staged_ctx:
        staged_hits = {
            r for r, _ in real_accession_hits(staged_ctx.read_root, list(staged_ctx.paths))
        }
    with rc.scan_context(root, DRUGBANK_CONTENT_POLICY, "worktree") as work_ctx:
        worktree_hits = {
            r for r, _ in real_accession_hits(work_ctx.read_root, list(work_ctx.paths))
        }

    assert rel in staged_hits, (
        "the staged mode read the WORKING FILE and cleared an accession the commit WOULD carry"
    )
    assert rel not in worktree_hits, (
        "the fixture no longer reproduces the divergence, so the assertion above proves nothing"
    )


def test_the_report_says_WHICH_COPY_it_read(tmp_path, monkeypatch):
    """E6-5 applied to WHICH BYTES rather than WHICH HALF: the report may still inspect the
    worktree, but a reader cannot check a verdict without knowing what was verified."""
    import chipsim.guards.record_content as rc

    monkeypatch.setattr(rc, "_refuse_a_scan_that_cannot_see_itself", lambda root, paths: None)
    rel = f"projects/{THIS_PROJECT}/docs/payload.txt"
    root = _diverged_repo(tmp_path, rel, staged=b"a\n", on_disk=b"b\n")

    rendered = {}
    for source in ("staged", "worktree"):
        with rc.scan_context(root, NOTHING_WAIVED, source) as context:
            rendered[source], _ = rc.render_scan(rc.scan_record_content(context))

    assert "STAGED" in rendered["staged"].upper()
    assert "WORKTREE" in rendered["worktree"].upper()
    assert rendered["staged"] != rendered["worktree"], (
        "both modes render identically — a reader cannot tell which copy was certified"
    )
    # And the report still NAMES the repository, not the temporary tree it read from.
    assert str(root) in rendered["staged"]


def test_the_staged_mode_reports_the_repository_not_the_temporary_tree(tmp_path, monkeypatch):
    """`root` is what the report names; `read_root` is where bytes came from. They differ in staged
    mode, and leaking the temp path into the report would make every run's output different and
    name a directory that no longer exists by the time anyone reads it."""
    import chipsim.guards.record_content as rc

    monkeypatch.setattr(rc, "_refuse_a_scan_that_cannot_see_itself", lambda root, paths: None)
    root = _diverged_repo(tmp_path, f"projects/{THIS_PROJECT}/docs/p.txt", b"a\n", b"b\n")
    with rc.scan_context(root, NOTHING_WAIVED, "staged") as context:
        assert context.read_root != context.root
        scan = rc.scan_record_content(context)
        text, _ = rc.render_scan(scan)

    assert scan.root == root.resolve()
    assert "chipsim-staged-" not in text, "the temporary tree leaked into the report"


def test_a_byte_source_that_is_neither_is_refused(tmp_path, monkeypatch):
    """Which copy the gate certifies must not be resolvable by omission OR by typo."""
    import chipsim.guards.record_content as rc
    from chipsim.guards.errors import GuardInvariantViolated

    root = _diverged_repo(tmp_path, f"projects/{THIS_PROJECT}/docs/p.txt", b"a\n", b"b\n")
    with pytest.raises(GuardInvariantViolated), rc.scan_context(root, NOTHING_WAIVED, "whatever"):
        pass


def test_E10_missing_on_disk_belongs_to_worktree_mode_only(tmp_path, monkeypatch):
    """r2.28's composition note, stated so it is not rediscovered: a STAGED BLOB ALWAYS EXISTS, so
    "tracked but not present on disk" is not a state the staged mode can produce. The two modes have
    different failure sets and neither inherits the other's."""
    import chipsim.guards.record_content as rc

    monkeypatch.setattr(rc, "_refuse_a_scan_that_cannot_see_itself", lambda root, paths: None)
    rel = f"projects/{THIS_PROJECT}/docs/vanished.txt"
    root = _diverged_repo(tmp_path, rel, staged=b"content\n", on_disk=b"content\n")
    (root / rel).unlink()  # staged, but gone from the worktree

    with rc.scan_context(root, NOTHING_WAIVED, "worktree") as context:
        worktree_scan = rc.scan_record_content(context)
    with rc.scan_context(root, NOTHING_WAIVED, "staged") as context:
        staged_scan = rc.scan_record_content(context)

    missing_in_worktree = [r.path for r in worktree_scan.rows if r.category == "missing-on-disk"]
    missing_in_staged = [r.path for r in staged_scan.rows if r.category == "missing-on-disk"]

    assert rel in missing_in_worktree, "the worktree mode must still report an absent file (E-10)"
    assert missing_in_staged == [], (
        "the staged mode reported a file as missing — a staged blob always exists, so this is "
        "worktree-mode's failure set leaking into a mode that cannot produce it"
    )


# --- §12.6 (r2.29): `derived_from` must PIN THE DECLARED FILE'S BYTES ---------------------------


def test_a_derived_from_declaration_must_also_pin_the_declared_files_bytes(tmp_path):
    """r2.29, E6-3's SUBSTANCE. The form-level ban on a bare path was satisfied and the substance
    was not.

    `derived_from` verified the SOURCE — tracked, readable, same owner, not itself declared — and
    never read the DECLARED file at all. So the declaration cleared that path FOREVER, across
    arbitrary content changes: declare `artifact.bin` as derived from a plausible source, then
    replace it with any undecodable payload, and the gate stays clean while the file is skipped by
    both halves. That is exactly what E6-3 says a path-keyed declaration does, reached through the
    form E6-3 offers as the self-maintaining alternative.

    A clause of the CTO's whose letter was implemented and whose purpose was not.
    """
    import chipsim.guards.record_content as rc

    declared = f"projects/{THIS_PROJECT}/docs/artifact.bin"
    source = f"projects/{THIS_PROJECT}/pyproject.toml"
    _write(tmp_path, source, b"[project]\nname = 'x'\n")
    _write(tmp_path, declared, b"\x00\xff\x80\x81 the artifact as declared")

    entry = {"path": declared, "derived_from": source, "why": "rendered from the manifest"}
    listing = _decl_fixture(tmp_path, project_entries=[entry], owners=[THIS_PROJECT]) + [
        declared,
        source,
    ]

    # REFUSED AT PARSE TIME, not reported as a per-entry defect — and that is the right channel:
    # a missing required key is a SCHEMA violation, handled exactly as a missing `path` or `why`
    # is. It reaches the operator as "declaration data unusable" (exit 2, nothing declared, listing
    # still rendered) rather than as one broken claim among valid ones. My first version of this
    # test asserted a defect; the implementation was right and the expectation was wrong.
    from chipsim.guards.errors import DeclarationDataUnusable

    with pytest.raises(DeclarationDataUnusable, match="sha256"):
        rc.declaration_defects(listing, NOTHING_WAIVED, _surface_of(tmp_path))


def test_a_derived_from_declaration_WITH_a_pin_still_holds(tmp_path):
    """The other direction, or the test above would pass against "reject every derived_from".
    `derived_from` remains the self-maintaining provenance claim; it is now carried BESIDE a content
    pin rather than instead of one."""
    import chipsim.guards.record_content as rc

    declared = f"projects/{THIS_PROJECT}/docs/artifact.bin"
    source = f"projects/{THIS_PROJECT}/pyproject.toml"
    _write(tmp_path, source, b"[project]\nname = 'x'\n")
    digest = _write(tmp_path, declared, b"\x00\xff\x80\x81 the artifact as declared")

    entry = {
        "path": declared,
        "sha256": digest,
        "derived_from": source,
        "why": "rendered from the manifest",
    }
    listing = _decl_fixture(tmp_path, project_entries=[entry], owners=[THIS_PROJECT]) + [
        declared,
        source,
    ]

    assert dict(rc.declaration_defects(listing, NOTHING_WAIVED, _surface_of(tmp_path))) == {}
    assert declared in rc.valid_declarations(listing, NOTHING_WAIVED, _surface_of(tmp_path))

    # ...and the pin is LOAD-BEARING: change the artifact and the claim stops holding.
    _write(tmp_path, declared, b"\x00\xff\x80\x81 REGENERATED, nobody looked")
    stale = dict(rc.declaration_defects(listing, NOTHING_WAIVED, _surface_of(tmp_path)))
    assert declared in stale, (
        "the artifact changed and the declaration still held — the pin is decorative"
    )


# --- §12.7: the four findings carried out of §11 -----------------------------------------------


def test_the_readability_verdict_is_not_kept_across_a_same_size_rewrite(tmp_path):
    """S11-22. `_READABILITY_CACHE` was keyed `(path, st_mtime_ns, st_size)`, process-global, never
    invalidated and never bounded. A same-size rewrite that PRESERVES mtime — `cp -p`, `tar -x`,
    `rsync -t`, a `git checkout` of a same-size blob, or any `os.utime` — keeps the stale verdict.

    The dangerous direction is a stale UNREADABLE: a `derived_from`-declared file that has become
    readable would clear adjudication and then be skipped, so its content is never scanned. (That
    particular route is narrower since §12.6 made the content pin mandatory, but the cache is what
    should not lie.)
    """
    import os

    import chipsim.guards.decoding as _decoding

    target = tmp_path / "blob.bin"
    target.write_bytes(b"\x00\xff\x80\x81\xfd")  # 5 bytes, undecodable
    stat_before = target.stat()
    assert not _decoding._is_readable(target)

    target.write_bytes(b"hello")  # 5 bytes, perfectly readable
    os.utime(target, ns=(stat_before.st_atime_ns, stat_before.st_mtime_ns))
    assert target.stat().st_size == stat_before.st_size
    assert target.stat().st_mtime_ns == stat_before.st_mtime_ns

    assert _decoding._is_readable(target), (
        "the cache returned a STALE verdict: same size, same mtime, completely different bytes"
    )


def test_de_duplication_alone_was_the_wrong_answer_to_a_conflicted_index(tmp_path):
    """S11-23, SUPERSEDED BY §12.9 — and the supersession is the point.

    The observation was right: `git ls-files -s` emits THREE records per path during an unresolved
    merge, so `tracked_count` was inflated by 2 per conflicted file and the minimum-tracked floor
    got easier to clear. I fixed it by DE-DUPLICATING, which fixed the number and nothing else.

    That made the conflicted state SURVIVABLE BY THE LISTING while it remained FATAL TO THE
    MATERIALISATION: `git checkout-index --all` silently skips unmerged entries and returns 0. The
    two halves then disagreed about what exists, and staged mode reported CLEAN over a file it had
    never read. A number that is right about a tree the scan cannot actually read is not an
    improvement.

    So the listing REFUSES an unmerged index now. `tracked_count` cannot be inflated by stages
    because a tree with stages is not scanned at all — which is the same property, established by
    construction rather than by arithmetic.
    """
    from chipsim.guards.errors import ScanNotPerformed
    from chipsim.guards.repo import _tracked_listing

    root = _init_repo(tmp_path)
    clean = root / "ok.txt"
    clean.write_text("fine\n")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)

    # A clean index still lists, so this test cannot pass by refusing everything.
    paths, _ = _tracked_listing(root)
    assert paths == ["ok.txt"]

    conflicted = root / "f.txt"
    conflicted.write_text("base\n")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "b"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "checkout", "-qb", "other"], cwd=root, check=True, capture_output=True)
    conflicted.write_text("theirs\n")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "t"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "checkout", "-q", "-"], cwd=root, check=True, capture_output=True)
    conflicted.write_text("ours\n")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "o"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "merge", "other"], cwd=root, capture_output=True, check=False)

    raw = subprocess.run(
        ["git", "ls-files", "-s"], cwd=root, capture_output=True, text=True, check=True
    ).stdout
    assert raw.count("f.txt") == 3, "the fixture did not produce an unresolved merge"

    with pytest.raises(ScanNotPerformed, match="UNMERGED"):
        _tracked_listing(root)


def test_the_frozen_scan_types_can_be_hashed(tmp_path, monkeypatch):
    """S11-24. `DeclarationSurface` and `ScanContext` are `frozen=True` with `eq=True`, so Python
    generates `__hash__` over the compared fields — and `entries` is a tuple containing DICTS, which
    are unhashable, so hashing either raises TypeError.

    A trap rather than a live defect, and it sits directly beside `_adjudicate_once`, which DOES
    hash the policy and uses the surface as its memo store."""
    import chipsim.guards.record_content as rc

    # The anti-vacuity witness refuses a tmp root — correct, and not what this test is about.
    monkeypatch.setattr(rc, "_refuse_a_scan_that_cannot_see_itself", lambda root, paths: None)

    surface = rc.DeclarationSurface(
        root=tmp_path,
        entries=(("docs/x.bin", {"path": "docs/x.bin"}, "project"),),
        registry=None,
        structural_error=None,
    )
    hash(surface)  # must not raise

    context = rc.ScanContext(
        root=tmp_path,
        read_root=tmp_path,
        byte_source="worktree",
        paths=("a",),
        submodules=(),
        policy=NOTHING_WAIVED,
        surface=surface,
    )
    hash(context)


# --- §12.8: a tracked SYMLINK's committed bytes are its TARGET STRING ---------------------------


def test_a_tracked_symlinks_own_bytes_are_scanned_not_its_targets(tmp_path):
    """A FALSE CLEAN, found while probing the staged-blob work, and it is r2.28's own property
    failing for a file type nobody considered.

    What git commits for a symlink is THE TARGET PATH STRING — that is the blob. The guard called
    `open()` on the path, which FOLLOWS the link and reads the target's content instead. So:

      * a symlink whose target path carries an accession is committed WITH that accession and the
        scan never sees it (measured: hits == [] with the accession in the blob);
      * a dangling link reads as UNREADABLE — a wrong reason that then invites a declaration;
      * a link pointing outside the repository made the scan read a file that is not in the tree at
        all, so the verdict covered bytes the commit does not carry.

    "A commit gate reads the bytes it certifies" (r2.28) has to hold for every entry in the index,
    not only the regular files.
    """
    import chipsim.guards.decoding as _decoding

    accession_in_target = f"./notes-{REAL}-summary.txt"
    link = tmp_path / "ref"
    link.symlink_to(accession_in_target)
    assert not link.exists(), "the fixture's link must dangle, as a committed one often does"

    assert _decoding._is_readable(link), (
        "a symlink's own bytes are its target string and are perfectly readable — reporting it "
        "unreadable is a wrong reason that invites a declaration"
    )
    chunks = _decoding._scan_chunks(link)
    assert chunks is not None and accession_in_target in "\n".join(chunks), (
        "the scan did not read the link's OWN bytes"
    )
    assert [a for _, a in real_accession_hits(tmp_path, ["ref"])] == [REAL], (
        "the accession is in the COMMITTED bytes and the scan missed it"
    )


def test_a_symlink_is_not_followed_out_of_the_tree(tmp_path):
    """The other half. Following a link meant the verdict could cover a file that is not in the
    repository at all — and, in staged mode, one the commit certainly does not carry."""
    import chipsim.guards.decoding as _decoding

    outside = tmp_path / "outside.txt"
    outside.write_text(f"{REAL} lives here\n")
    inside = tmp_path / "tree"
    inside.mkdir()
    (inside / "ref").symlink_to(outside)

    chunks = _decoding._scan_chunks(inside / "ref")
    text = "\n".join(chunks or [])
    assert REAL not in text, (
        "the scan followed the link and read a file OUTSIDE the tree — the verdict covers bytes "
        "the repository does not contain"
    )
    assert str(outside) in text or "outside.txt" in text, (
        "it should have read the link's own bytes, which are the target PATH"
    )


def test_a_symlinks_digest_is_of_its_own_bytes(tmp_path):
    """`sha256` pins a declaration to content. For a symlink, hashing the TARGET would pin a file
    that is not in the index — and would raise outright when the link dangles."""
    import chipsim.guards.decoding as _decoding

    link = tmp_path / "ref"
    link.symlink_to("./nowhere.txt")
    digest = _decoding._sha256(link)  # must not raise on a dangling link
    import hashlib

    assert digest == hashlib.sha256(b"./nowhere.txt").hexdigest()


# --- §12.9: the §12 gate's findings ------------------------------------------------------------


def test_an_unmerged_index_is_REFUSED_rather_than_scanned_around(tmp_path):
    """THE CRITICAL FINDING, reached independently by two reviewers and reproduced end-to-end.

    `git checkout-index --all` SILENTLY SKIPS UNMERGED ENTRIES AND RETURNS 0. So in staged mode a
    conflicted path was listed (the stage records de-duplicate into `paths`, §12.7), never
    materialised, and then skipped by every reader — `undecodable_unallowed` and the accession scan
    both `continue` on a path that is not there. Measured on a real conflicted repo:

        worktree -> files-fail exit=2   (the accession was found)
        staged   -> CLEAN     exit=0    scanned=794

    The header said 794 files were scanned in a scan that read 793. For a path THIS project owns the
    row at least fails; for a path another project owns it is merely "listed", and the gate exits 0
    having never read the bytes.

    REFUSED, not scanned around. A tree mid-merge is not a tree the report can speak for, and the
    listing already parses the stage number and throws it away.
    """
    from chipsim.guards.errors import ScanNotPerformed
    from chipsim.guards.repo import _tracked_listing

    root = _init_repo(tmp_path)
    conflicted = root / "f.txt"
    conflicted.write_text("base\n")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "b"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "checkout", "-qb", "other"], cwd=root, check=True, capture_output=True)
    conflicted.write_text("theirs\n")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "t"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "checkout", "-q", "-"], cwd=root, check=True, capture_output=True)
    conflicted.write_text("ours\n")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "o"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "merge", "other"], cwd=root, capture_output=True, check=False)

    raw = subprocess.run(
        ["git", "ls-files", "-s"], cwd=root, capture_output=True, text=True, check=True
    ).stdout
    assert raw.count("f.txt") == 3, "the fixture did not produce an unresolved merge"

    with pytest.raises(ScanNotPerformed, match="unmerged"):
        _tracked_listing(root)


def test_the_ledger_read_survives_a_dangling_symlink(tmp_path):
    """A REGRESSION I INTRODUCED IN §12.8 AND SHIPPED.

    `entry_exists()` correctly made a dangling symlink count as PRESENT — but `ledger_tuple_hits`
    then calls `read_text()` on it, which raises `FileNotFoundError`. That is not a
    `RecordContentScanError`, so it escapes `enforce_record_content` as an exit-1 traceback: the
    FOURTH STATE, which is the defect §12.2 exists to prevent, reintroduced by my own fix for a
    different one. I checked the sites my test touched, not the sites my change reached.
    """
    import chipsim.ingest.drugbank_snapshot as ds

    ledger_rel = min(ds.DRUGBANK_ID_LEDGER)
    (tmp_path / ledger_rel).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / ledger_rel).symlink_to("./nowhere.txt")

    hits = ds.ledger_tuple_hits(tmp_path)  # must not raise
    assert hits == [], "a dangling ledger path carries no tuples"


def test_a_declared_dangling_symlink_gets_ONE_answer_not_two(tmp_path):
    """The other half of the same incomplete fix. Declaration adjudication still gated on
    `target.is_file()`, which FOLLOWS the link — so a declared dangling symlink was simultaneously
    "present" to `unresolvable_tracked` (via `entry_exists`) and "absent from disk" to the
    adjudicator. One report, two answers about one path."""
    import chipsim.guards.record_content as rc
    from chipsim.guards.decoding import _sha256

    rel = f"projects/{THIS_PROJECT}/docs/link.bin"
    (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / rel).symlink_to("./nowhere.bin")

    entry = {"path": rel, "sha256": _sha256(tmp_path / rel), "why": "a tracked link"}
    listing = _decl_fixture(tmp_path, project_entries=[entry], owners=[THIS_PROJECT]) + [rel]

    assert rc.unresolvable_tracked(tmp_path, listing) == [], (
        "a dangling symlink is PRESENT — it is in the index and a commit carries it"
    )
    defects = dict(rc.declaration_defects(listing, NOTHING_WAIVED, _surface_of(tmp_path)))
    # It IS a defect — but for ONE coherent reason. A symlink's own bytes are its target string and
    # those are perfectly readable, so declaring it is refused by the rule that a declaration says a
    # file CANNOT be read. What must not happen is the adjudicator calling it "absent from disk"
    # while `unresolvable_tracked` calls it present: one report, two answers about one path.
    assert "absent from disk" not in defects.get(rel, ""), (
        f"the adjudicator called it absent while unresolvable_tracked called it present: "
        f"{defects.get(rel)!r}"
    )
    assert "CAN read it" in defects[rel], (
        "the refusal should be the readable-file rule, which is the true statement about a link"
    )


def test_a_numeric_dtype_dataset_carrying_a_record_is_scanned(tmp_path):
    """A FALSE CLEAN found by the security reviewer, and the dtype filter's comment is the tell.

    `readable = dtype.kind in {"O","S","U","V"}` returns before any read for every other dtype,
    justified by "a 14.7M-element expression matrix cannot carry a compound name" — TRUE OF
    EXPRESSION MATRICES, FALSE OF uint8. The comment reasons about one dataset shape; the code
    applies to all dtypes.

    Measured before the fix: the accession sat in the file's raw bytes, the scanned text was
    structure names only, and `_is_readable` returned True — so the container was certified as fully
    READ and needed no declaration, with the record invisible to both halves.
    """
    h5py = pytest.importorskip("h5py")
    import numpy as np

    from chipsim.guards.decoding import _is_readable, _scan_chunks

    record = f"{REAL},SomeCoinedTitle,{STRUCTURE}"
    path = tmp_path / "matrix.h5ad"
    with h5py.File(path, "w") as handle:
        handle.create_dataset("obs/_index", data=[b"cell1"])
        handle.create_dataset("uns/blob", data=np.frombuffer(record.encode(), dtype=np.uint8))

    assert REAL.encode() in path.read_bytes(), "the fixture must put the record in the file"
    assert _is_readable(path), "the container is readable either way; that is what makes it a trap"
    assert REAL in "\n".join(_scan_chunks(path) or []), (
        "a record stored as a numeric buffer was invisible while the container scanned CLEAN"
    )


# --- §12.10: the staged path, bound by VERDICTS rather than by a header string ------------------


def _two_tree_repo(tmp_path):
    """A repo whose INDEX and WORKTREE disagree about the declaration surface AND the artifact.

    The existing staged fixtures use `staged=b"a\n"` / `on_disk=b"b\n"` — both readable, so the two
    modes produce IDENTICAL verdicts and only the header string differs. That is why five mutants
    against the staged path survived: nothing made the modes disagree about an OUTCOME.
    """
    root = _init_repo(tmp_path)
    marker = root / f"projects/{THIS_PROJECT}/pyproject.toml"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text("[project]\nname = 'x'\n")

    artifact = f"projects/{THIS_PROJECT}/docs/artifact.bin"
    (root / artifact).parent.mkdir(parents=True, exist_ok=True)
    (root / artifact).write_bytes(b"\x00\xff\x80\x81 STAGED COPY")

    repo_surface = root / "config/record_content_declarations.yaml"
    repo_surface.parent.mkdir(parents=True, exist_ok=True)
    repo_surface.write_text(f'version: "1"\nowners: [{THIS_PROJECT}]\ndeclarations: []\n')
    project_surface = root / f"projects/{THIS_PROJECT}/configs/record_content_declarations.yaml"
    project_surface.parent.mkdir(parents=True, exist_ok=True)
    project_surface.write_text('version: "1"\ndeclarations: []\n')

    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)

    # NOW the worktree diverges: a different artifact, and a declaration pinning THAT copy.
    worktree_bytes = b"\x00\xff\x80\x81 WORKTREE COPY"
    (root / artifact).write_bytes(worktree_bytes)
    digest = hashlib.sha256(worktree_bytes).hexdigest()
    project_surface.write_text(
        'version: "1"\ndeclarations:\n'
        f"  - path: {artifact}\n    sha256: {digest}\n    why: rendered artifact\n"
    )
    return root, artifact


def test_staged_mode_adjudicates_against_the_STAGED_declaration_surface(tmp_path, monkeypatch):
    """THE MOST SERIOUS SURVIVING MUTANT: `DeclarationSurface.read(read_root)` -> `read(root)`
    turned a staged-mode EXIT 2 INTO EXIT 0 with the whole suite green.

    A declaration that was never staged, pinning bytes that were never staged, cleared the bytes a
    commit WOULD carry. The existing staged tests could not see it: one calls `real_accession_hits`
    itself and never touches `scan_record_content`, and the other compares two readable files whose
    verdicts are identical, so its inequality assertion is carried entirely by the header string.

    Both directions are asserted, so this cannot pass against "always read the worktree" either.
    """
    import chipsim.guards.record_content as rc

    # The witness refuses a tmp tree because it does not contain this package. That property has
    # its own live-repository test now (staged AND worktree), so patching it here is not hiding it.
    monkeypatch.setattr(rc, "_refuse_a_scan_that_cannot_see_itself", lambda root, paths: None)

    root, artifact = _two_tree_repo(tmp_path)

    with rc.scan_context(root, NOTHING_WAIVED, "staged") as ctx:
        assert Path(ctx.surface.root) == Path(ctx.read_root), (
            "the surface is bound to the wrong tree"
        )
        assert Path(ctx.surface.root) != Path(ctx.root), "staged must not read the worktree surface"
        assert [p for p, _e, _s in ctx.surface.entries] == [], (
            "the STAGED surface declares nothing — the declaration exists only in the worktree"
        )
        staged = rc.scan_record_content(ctx)

    with rc.scan_context(root, NOTHING_WAIVED, "worktree") as ctx:
        assert Path(ctx.surface.root) == Path(ctx.root)
        worktree = rc.scan_record_content(ctx)

    assert staged.exit_code == 2, (
        "the staged scan was cleared by a declaration that was never staged, pinned to bytes that "
        "were never staged — exit 2 became exit 0"
    )
    assert artifact in [r.path for r in staged.rows if r.disposition == "FAILS HERE"]
    assert worktree.exit_code == 0, (
        "the worktree copy IS declared and IS pinned, so that mode must clear it — otherwise this "
        "test would pass against an implementation that always reads the staged tree"
    )


def test_the_entry_point_reads_the_byte_source_it_was_given(tmp_path, monkeypatch):
    """`enforce_record_content` gained `byte_source` in this diff and NO TEST EVER PASSED "staged".

    So two mutants survived: the accession half taking `context.root` instead of `context.read_root`,
    and the same for the ledger half alone — which is the split-evidence shape E6-5 names, with one
    half certifying the index while the other certifies the working files. The comment promising
    they read the SAME copy was unbound.
    """
    import chipsim.guards.record_content as guard
    import chipsim.record_content as cr

    root = _init_repo(tmp_path)
    marker = root / f"projects/{THIS_PROJECT}/pyproject.toml"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text("[project]\nname = 'x'\n")
    for rel in (
        "config/record_content_declarations.yaml",
        f"projects/{THIS_PROJECT}/configs/record_content_declarations.yaml",
    ):
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text('version: "1"\ndeclarations: []\n')

    leak = f"projects/{THIS_PROJECT}/docs/leak.txt"
    (root / leak).parent.mkdir(parents=True, exist_ok=True)
    (root / leak).write_text(f"see {REAL} for details\n")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
    (root / leak).write_text("clean text, nothing to see\n")  # worktree is innocent

    monkeypatch.setattr(guard, "repo_root", lambda: root)
    monkeypatch.setattr(guard, "_refuse_a_scan_that_cannot_see_itself", lambda r, p: None)

    with pytest.raises(cr.RecordContentViolation) as exc:
        cr.enforce_record_content(DRUGBANK_CONTENT_POLICY, byte_source="staged")
    assert "REAL ACCESSIONS" in exc.value.report, (
        "the accession half read the WORKING FILE — the half that certifies and the half that "
        "reports are looking at different trees"
    )

    result = cr.enforce_record_content(DRUGBANK_CONTENT_POLICY, byte_source="worktree")
    assert result.status == "clean", (
        "the worktree copy is clean; if this failed too, the test above would prove nothing about "
        "WHICH copy was read"
    )


def test_the_live_repository_scans_clean_in_STAGED_mode_too(tmp_path):
    """THE WITNESS AND THE STAGED PATH HAD NEVER MET.

    Every staged test patches `_refuse_a_scan_that_cannot_see_itself` away, so a mutant pointing the
    witness at `read_root` — which makes EVERY staged scan raise, i.e. the commit gate becomes
    unrunnable — survived the whole suite. This runs the real thing against the real repository with
    nothing patched out, the mirror of the worktree-mode live test.
    """
    import chipsim.guards.record_content as rc
    from chipsim.ingest.drugbank_snapshot import DRUGBANK_CONTENT_POLICY as POLICY

    with rc.scan_context(REPO_ROOT, POLICY, "staged") as context:
        scan = rc.scan_record_content(context)

    assert scan.byte_source == "staged"
    assert scan.root == REPO_ROOT, "the report names the repository, not the temporary tree"
    assert scan.tracked_count > 100, "a scan of nothing is not a pass"
    assert [r.path for r in scan.rows if r.disposition == "FAILS HERE"] == []
    assert scan.exit_code == 0


def test_the_shipped_human_report_certifies_the_WORKTREE(tmp_path):
    """`render_undeclared_report` passing "staged" instead of "worktree" survived the suite — the
    human-facing listing silently materialising and certifying the INDEX, while its docstring says
    it "describes the files as they sit on disk". The one shipped call site of the distinction this
    whole section exists to make was unpinned."""
    import chipsim.guards.record_content as rc

    text, _code = rc.render_undeclared_report(NOTHING_WAIVED)
    assert "WORKTREE bytes (the files as they sit on disk)" in text
    assert "STAGED bytes" not in text


def test_a_scan_cannot_carry_a_byte_source_that_is_neither(tmp_path):
    """The third `__post_init__` invariant, added in this diff and never tested — unlike its two
    siblings (`disposition`, `exit_code`), each of which has a dedicated test. Disabling it survived.
    """
    import chipsim.guards.record_content as rc
    from chipsim.guards.errors import GuardInvariantViolated

    for bad in ("stage", "", "WORKTREE"):
        with pytest.raises(GuardInvariantViolated, match="byte_source"):
            rc.RecordContentScan(
                root=tmp_path,
                package=tmp_path / "p.py",
                tracked_count=500,
                failing_count=0,
                rows=(),
                declaration_counts=(0, 0, 0),
                defect_count=0,
                submodules=(),
                declaration_files=("a", "b"),
                byte_source=bad,
                registry_state="declared",
                structural_error=None,
                exit_code=0,
            )


def test_the_LEDGER_half_also_reads_the_byte_source_it_was_given(tmp_path, monkeypatch):
    """The reviewer said to parametrise over WHICH HALF carries the hit, so neither can be reverted
    alone. I did not, and the mutant that reverts ONLY `ledger_tuple_hits(read_root)` survived my
    first version of this test — because it asserts on the CONTENT half's output, which still found
    the accession.

    That is the split-evidence shape E6-5 names, in the test written to prevent it: one half
    certifying the index while the other certifies the working files, invisible because the
    assertion could be satisfied by either.
    """
    import chipsim.guards.record_content as guard
    import chipsim.ingest.drugbank_snapshot as ds
    import chipsim.record_content as cr

    root = _init_repo(tmp_path)
    marker = root / f"projects/{THIS_PROJECT}/pyproject.toml"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text("[project]\nname = 'x'\n")
    for rel in (
        "config/record_content_declarations.yaml",
        f"projects/{THIS_PROJECT}/configs/record_content_declarations.yaml",
    ):
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text('version: "1"\ndeclarations: []\n')

    # ONLY the ledger half can see this: a tuple in a LEDGER file, and nothing else anywhere.
    ledger_rel = min(ds.DRUGBANK_ID_LEDGER)
    (root / ledger_rel).parent.mkdir(parents=True, exist_ok=True)
    (root / ledger_rel).write_text(f"# {REAL}\n# {STRUCTURE}\n")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
    (root / ledger_rel).write_text("# nothing here\n")  # the worktree copy is innocent

    monkeypatch.setattr(guard, "repo_root", lambda: root)
    monkeypatch.setattr(guard, "_refuse_a_scan_that_cannot_see_itself", lambda r, p: None)

    # Precondition: the ledger half genuinely fires on the STAGED copy and not on the worktree one,
    # or neither assertion below proves which tree was read.
    assert ds.ledger_tuple_hits(root) == [], "the worktree copy must be clean for this fixture"

    with pytest.raises(cr.RecordContentViolation) as exc:
        cr.enforce_record_content(DRUGBANK_CONTENT_POLICY, byte_source="staged")
    assert f"{ledger_rel}:1 " in exc.value.report, (
        "the LEDGER half read the working file — it emits a LINE NUMBER, which the content half "
        "does not, so this cannot be satisfied by the other half's work"
    )

    assert cr.enforce_record_content(DRUGBANK_CONTENT_POLICY, byte_source="worktree").status == (
        "clean"
    )


# --- §12.11: r2.28's ruling has a CALLER -------------------------------------------------------


def test_a_shipped_command_certifies_the_STAGED_bytes(tmp_path, monkeypatch, capsys):
    """r2.28 ruled that A COMMIT GATE READS THE BYTES IT CERTIFIES. §12.5 built the capability and
    NOTHING INVOKED IT: every staged call site was a test, there is no hook, and the only subcommand
    passed "worktree". A ruling implemented as a mechanism with no reader is E6-7's defect —
    "enforced for whoever runs pytest, and for nobody else" — ONE ITERATION AFTER I FIXED IT, and it
    is the "an inert mechanism reads as coverage" rule I have been applying to everyone else.

    `record-content-gate` is that caller. A separate command rather than a flag, for the same reason
    `for_staged` is a separate constructor: which copy is certified is carried by the NAME.
    """
    import chipsim.guards.record_content as rc
    from chipsim import pipeline

    root = _init_repo(tmp_path)
    marker = root / f"projects/{THIS_PROJECT}/pyproject.toml"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text("[project]\nname = 'x'\n")
    for rel in (
        "config/record_content_declarations.yaml",
        f"projects/{THIS_PROJECT}/configs/record_content_declarations.yaml",
    ):
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text('version: "1"\ndeclarations: []\n')

    leak = f"projects/{THIS_PROJECT}/docs/leak.txt"
    (root / leak).parent.mkdir(parents=True, exist_ok=True)
    (root / leak).write_text(f"see {REAL} for details\n")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
    (root / leak).write_text("clean text, nothing to see\n")  # the worktree is innocent

    monkeypatch.setattr(rc, "repo_root", lambda: root)
    monkeypatch.setattr(rc, "_refuse_a_scan_that_cannot_see_itself", lambda r, p: None)
    monkeypatch.setattr(pipeline, "_record_content_policy", lambda: DRUGBANK_CONTENT_POLICY)

    gate_code = pipeline.main(["record-content-gate"])
    gate_out = capsys.readouterr().out
    report_code = pipeline.main(["record-content-report"])
    report_out = capsys.readouterr().out

    assert gate_code == 2, (
        "the COMMIT GATE cleared a staged accession — it is reading the working file, which is the "
        "defect r2.28 exists to close"
    )
    assert "REAL ACCESSIONS" in gate_out
    assert "STAGED bytes (what a commit would carry)" in gate_out

    assert report_code == 0, (
        "the human report describes the WORKTREE, which is clean here — if this failed too, the "
        "assertion above would not show WHICH copy the gate read"
    )
    assert "WORKTREE bytes (the files as they sit on disk)" in report_out


def test_the_entry_point_will_not_choose_the_byte_source_for_you():
    """`enforce_record_content` was the one defaulted decision left on this path — at the one door a
    non-pytest consumer uses, defaulting to the copy r2.28 ruled is NOT what a commit carries.
    `ScanContext` refuses that default in three places; the rule stopped one layer short of the
    public API, which is the shape MUT-24/25 named ("a shape check that inspects one class cannot
    see the constructors around it"), one layer up."""
    import inspect

    import chipsim.record_content as cr

    parameter = inspect.signature(cr.enforce_record_content).parameters["byte_source"]
    assert parameter.default is inspect.Parameter.empty, (
        "byte_source acquired a default — a consumer can now certify the working files by omission"
    )
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY, (
        "keyword-only, so it cannot be passed positionally by accident either"
    )


def test_an_hdf5_container_is_metered_INCREMENTALLY_not_after_the_fact(tmp_path, monkeypatch):
    """`_hdf5_chunks` accumulates every dataset into one list and yields ONCE, so
    `_collect_bounded` — which meters chunk by chunk — sees a single chunk and can only raise AFTER
    the whole expansion is already resident. Measured by the reviewer: a 3.4 MB container drove
    1,574 MB peak RSS, ~455x on disk, and growth is linear in dataset count with no cap.

    `datasets_seen` was incremented and never read: the "per-dataset bound applied N times with no
    cap on N" that `_MAX_CONTAINER_BYTES` says it fixed was fixed on the parquet path only.

    A guard that OOMs produces no verdict — this module's own false-clean-in-a-new-costume.
    """
    h5py = pytest.importorskip("h5py")
    import chipsim.guards.decoding as _decoding

    path = tmp_path / "many.h5ad"
    with h5py.File(path, "w") as handle:
        for i in range(12):
            handle.create_dataset(f"g{i}/d", data=[("Z" * 4000).encode()])

    # A budget that ONE dataset fits inside but the container as a whole does not.
    monkeypatch.setattr(_decoding, "_MAX_CONTAINER_BYTES", 12_000)
    _decoding._READABILITY_CACHE.clear()

    yielded = []
    real = _decoding._hdf5_chunks

    def counting(target):
        for chunk in real(target):
            yielded.append(len(chunk))
            yield chunk

    monkeypatch.setattr(_decoding, "_hdf5_chunks", counting)
    assert _decoding._scan_chunks(path) is None, "the container total is not bounded"
    assert len(yielded) > 1, (
        f"the reader yielded {len(yielded)} chunk(s) — it accumulates everything and yields once, "
        "so the aggregate budget can only fire AFTER the memory is already allocated"
    )


def test_the_adjudication_memo_is_keyed_on_the_LISTING_too(tmp_path):
    """Both halves of `(policy, tuple(paths))` were inert — dropping either survived the suite. The
    dangerous direction is dropping `paths`: two different listings against ONE surface would share
    a verdict, which is precisely the "one report that disagrees with itself" E-14 exists to
    prevent, reachable through the public `declaration_defects(paths, policy, surface)`.
    """
    import chipsim.guards.record_content as rc

    declared = f"projects/{THIS_PROJECT}/docs/artifact.bin"
    digest = _write(tmp_path, declared, b"\x00\xff\x80\x81 OPAQUE")
    entry = {"path": declared, "sha256": digest, "why": "rendered artifact"}

    with_declared = _decl_fixture(tmp_path, project_entries=[entry], owners=[THIS_PROJECT]) + [
        declared
    ]
    without_declared = [p for p in with_declared if p != declared]

    surface = _surface_of(tmp_path)  # ONE surface, deliberately shared between the two calls
    tracked = dict(rc.declaration_defects(with_declared, NOTHING_WAIVED, surface))
    untracked = dict(rc.declaration_defects(without_declared, NOTHING_WAIVED, surface))

    assert tracked == {}, "the declared path IS tracked in this listing, so the claim holds"
    assert declared in untracked, (
        "the same surface with a listing that does NOT track the declared path returned the first "
        "listing's verdict — the memo is keyed on the policy alone, so one surface answers two "
        "different questions with one answer"
    )
    assert "not tracked" in untracked[declared]


def test_the_package_charter_names_every_module_it_has():
    """The charter has gone stale THREE times, each time because the diff that invalidated it did
    not open it. A count is the cheapest thing that cannot drift silently: if a module is added or
    removed and nobody touches the charter, this fails."""
    import re
    from pathlib import Path as _Path

    from chipsim import guards

    modules = {p.stem for p in _Path(guards.__file__).parent.glob("*.py") if p.stem != "__init__"}
    charter = guards.__doc__ or ""

    missing = sorted(m for m in modules if not re.search(rf"\b{re.escape(m)}\b", charter))
    assert not missing, f"the charter does not mention {missing} — it has gone stale again"

    words = {
        "ONE": 1,
        "TWO": 2,
        "THREE": 3,
        "FOUR": 4,
        "FIVE": 5,
        "SIX": 6,
        "SEVEN": 7,
        "EIGHT": 8,
        "NINE": 9,
        "TEN": 10,
    }
    claimed = [words[w] for w in re.findall(r"\b([A-Z]+) modules live here", charter) if w in words]
    assert claimed, "the charter no longer states how many modules live here"
    assert claimed[0] == len(modules), (
        f"the charter says {claimed[0]} modules and there are {len(modules)}: {sorted(modules)}"
    )


def test_the_memo_distinguishes_two_POLICIES_over_one_surface(tmp_path):
    """The other inert half of `(policy, tuple(paths))`. Dropping `policy` survived the suite: two
    different policies against one surface and one listing would share a verdict.

    `content_exempt` is the half that changes an adjudication — a path already exempt by the content
    mechanism may not ALSO be declared, because that would exempt it twice and make it invisible to
    both halves of the guard. So two policies differing only there must produce different defects.
    """
    import chipsim.guards.record_content as rc

    declared = f"projects/{THIS_PROJECT}/docs/artifact.bin"
    digest = _write(tmp_path, declared, b"\x00\xff\x80\x81 OPAQUE")
    listing = _decl_fixture(
        tmp_path,
        project_entries=[{"path": declared, "sha256": digest, "why": "rendered artifact"}],
        owners=[THIS_PROJECT],
    ) + [declared]

    surface = _surface_of(tmp_path)  # ONE surface, shared deliberately
    lenient = _rc_policy(readability_waived=_rc_nothing_waived, content_exempt=_rc_nothing_exempt)
    strict = _rc_policy(
        readability_waived=_rc_nothing_waived, content_exempt=lambda rel: rel == declared
    )

    under_lenient = dict(rc.declaration_defects(listing, lenient, surface))
    under_strict = dict(rc.declaration_defects(listing, strict, surface))

    assert under_lenient == {}, "nothing is content-exempt, so the declaration holds"
    assert declared in under_strict, (
        "the same surface and listing under a DIFFERENT policy returned the first policy's verdict "
        "— the memo is keyed on the listing alone"
    )
