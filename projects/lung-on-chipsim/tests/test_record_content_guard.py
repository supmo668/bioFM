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

from chipsim.ingest.drugbank_snapshot import (
    DRUGBANK_ID_EXCLUDED_FILES,
    DRUGBANK_ID_LEDGER,
    THIS_PROJECT,
    _is_readable,
    accession_structure_tuples,
    failing_undeclared,
    is_accession_excluded,
    ledger_tuple_hits,
    path_owner,
    real_accession_hits,
    recognised_owners,
    undeclared_report,
    undecodable_unallowed,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = PROJECT_ROOT.parent.parent

REAL = "DB" + "00128"  # assembled: a literal would be a self-inflicted hit
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
    assert undecodable_unallowed(tmp_path, ["broken.parquet"]) == ["broken.parquet"]
    assert real_accession_hits(tmp_path, ["broken.parquet"]) == []


def test_an_undecodable_file_is_reported_unless_it_is_declared(tmp_path):
    """Fail-closed on the unknown: a new binary must be DECLARED before the scan passes, so
    "no hits" can never mean "never read". The declaration is by exact path, not by suffix —
    a suffix rule would silently admit the next .pdf nobody looked at."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "figure.pdf").write_bytes(b"\x89PNG\x00\xff\xfe not utf-8")
    assert undecodable_unallowed(tmp_path, ["docs/figure.pdf"]) == ["docs/figure.pdf"]


def test_a_declared_binary_file_is_not_reported(tmp_path):
    """The declaration surface is empty in this repo, so the mechanism is exercised with a real
    declaration FILE owned by this project — which is what a real entry would have to be.

    The version this replaces monkeypatched a constant the reader no longer consults, and was
    vacuous even before that: its fixture wrote b"\\xff\\xfe not utf-8", which decodes as UTF-16, so
    the file was READABLE and the assertion held with or without a declaration. Hence the first
    assertion below — prove the fixture is undecodable, then prove the declaration is what clears
    it."""
    import chipsim.ingest.drugbank_snapshot as ds

    declared = f"projects/{THIS_PROJECT}/docs/figure.pdf"
    digest = _write(tmp_path, declared, b"%PDF-1.4\x00\xfe\xff\x80\x81 binary")

    bare = _decl_fixture(tmp_path) + [declared]
    assert ds.undecodable_unallowed(tmp_path, bare) == [declared], (
        "the fixture must be genuinely undecodable, or declaring it proves nothing"
    )

    listing = _decl_fixture(
        tmp_path,
        project_entries=[{"path": declared, "sha256": digest, "why": "rendered figure"}],
    ) + [declared]
    assert ds.undecodable_unallowed(tmp_path, listing) == []


def test_every_undecodable_tracked_file_in_this_repo_is_declared():
    """SUPERSEDED IN SCOPE BY r2.22 E6-1b, deliberately kept rather than deleted.

    Until E6-1b this asserted the repo-wide list was EMPTY, which is what forced 23 of another
    team's paths to be declared inside this module. The failure is now scoped to the files this
    project owns (plus any file no project owns); the repo-wide LISTING is asserted by
    `test_the_live_report_is_not_vacuous_and_this_gate_is_green`, because listing is what may never
    be skipped and failing is what is scoped.
    """
    undeclared = failing_undeclared(REPO_ROOT, _tracked_paths())
    assert undeclared == [], (
        f"{len(undeclared)} tracked file(s) this project owns (or that no project owns) cannot be "
        f"decoded and are not declared: {undeclared[:5]}"
    )


def test_the_declaration_surface_is_not_a_blanket():
    """The shape rules bind every entry in the SHIPPED data. Empty is the correct state today, so
    this loop runs zero times — which is honest rather than reassuring, and is why the live
    anti-rot test below asserts against the validator instead of against a count."""
    import chipsim.ingest.drugbank_snapshot as ds

    for rel, _entry, _surface in ds._declaration_entries(REPO_ROOT):
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
        assert undecodable_unallowed(tmp_path, [path.name]) == [], name


def test_text_in_other_encodings_is_scanned_not_declared_away(tmp_path):
    """A latin-1 or UTF-16 document carrying an accession was classified "undecodable", and the
    only exit offered was the allow-list — which would make a PLAIN-TEXT carrier invisible for
    good. UTF-16 is a routine artifact of Windows-authored files."""
    (tmp_path / "latin1.md").write_bytes(("caf\xe9 " + REAL).encode("latin-1"))
    (tmp_path / "utf16.md").write_bytes(("x " + REAL).encode("utf-16"))
    hits = {rel for rel, _ in real_accession_hits(tmp_path, ["latin1.md", "utf16.md"])}
    assert hits == {"latin1.md", "utf16.md"}
    assert undecodable_unallowed(tmp_path, ["latin1.md", "utf16.md"]) == []


def test_genuine_binary_is_still_reported_not_decoded_into_mojibake(tmp_path):
    """The other side of the lenient decode: latin-1 decodes ANY bytes, so it must not become an
    unconditional last resort — a binary that "decodes" is a binary that scans clean."""
    (tmp_path / "real.png").write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00")
    assert undecodable_unallowed(tmp_path, ["real.png"]) == ["real.png"]


def test_the_allowlist_is_matched_by_EXACT_path_not_by_suffix_or_basename(tmp_path, monkeypatch):
    """Both a path-suffix match and a basename match survived every earlier test, so
    `vendor/<declared path>` or any file sharing a declared BASENAME would have been silently
    exempted. The docstring claimed "exact path"; nothing checked it."""
    import chipsim.ingest.drugbank_snapshot as ds

    declared = f"projects/{THIS_PROJECT}/docs/figure.pdf"
    digest = _write(tmp_path, declared, b"%PDF-1.4\x00\xfe\xff\x80 binary")
    entry = {"path": declared, "sha256": digest, "why": "rendered figure"}

    for rel in (f"vendor/{declared}", f"some/other/dir/{Path(declared).name}"):
        _write(tmp_path, rel, b"\x00\xff\x80\x81 not text")
        listing = _decl_fixture(tmp_path, project_entries=[entry]) + [declared, rel]
        assert rel in ds.undecodable_unallowed(tmp_path, listing), rel
        assert declared not in ds.undecodable_unallowed(tmp_path, listing), (
            "the declared path itself must still be cleared, or this test would pass on a "
            "declaration mechanism that simply does not work"
        )


def test_a_declared_path_is_still_scanned_when_its_bytes_are_readable(tmp_path, monkeypatch):
    """The allow-list declares that a file cannot be READ — never that its content is exempt.
    Adding `or rel in RENDERED_ARTIFACT_DECLARATIONS` to the accession scan survived the whole suite, which
    would have turned "somebody looked at this artifact once" into a blanket content waiver."""
    import chipsim.ingest.drugbank_snapshot as ds

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
    defects = dict(ds.declaration_defects(tmp_path, listing))
    assert declared in defects and "readable" in defects[declared].lower()


def test_undecodable_reporting_is_not_limited_to_familiar_extensions(tmp_path):
    """Limiting the REPORT to known binary suffixes survived — the exact bypass the exact-path
    rule exists to prevent, rebuilt on the reporting side."""
    for name in ("weird.bin", "notes.md", "blob_no_ext"):
        (tmp_path / name).write_bytes(b"\x00\xff\xfe\x00 not text at all")
    assert undecodable_unallowed(tmp_path, ["weird.bin", "notes.md", "blob_no_ext"]) == [
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
    assert undecodable_unallowed(tmp_path, ["empty.md", "zero.parquet"]) == []
    assert real_accession_hits(tmp_path, ["empty.md", "zero.parquet"]) == []


def test_the_report_is_sorted_so_a_failure_reads_the_same_way_twice(tmp_path):
    for rel in ("z/c.bin", "m/a.bin", "a/b.bin"):
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"\x00\xff")
    assert undecodable_unallowed(tmp_path, ["z/c.bin", "m/a.bin", "a/b.bin"]) == [
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
    assert undecodable_unallowed(tmp_path, [ledger, dispatch]) == sorted([ledger, dispatch])

    message = ".claude/usr/matthew-mo/lung-on-chipsim/dispatches/real.md"
    (tmp_path / message).write_text("a sent message\n")
    assert undecodable_unallowed(tmp_path, [message]) == []


def test_every_declared_path_exists_is_tracked_and_is_genuinely_unreadable():
    """A declaration for a file that does not exist PRE-AUTHORISES whatever later lands at that
    path, and a declaration for a DECODABLE file hides nothing the scan could not already read.
    Three junk entries — a deleted figure, a pre-declared `data/processed/compounds.parquet`, and
    README.md — passed every earlier test. The ledger sets already had this check (above); the new
    set was simply left out of it."""
    import chipsim.ingest.drugbank_snapshot as ds

    tracked = set(_tracked_paths())
    for rel, _entry, _surface in ds._declaration_entries(REPO_ROOT):
        path = REPO_ROOT / rel
        assert path.is_file(), f"{rel} is declared but does not exist — a pre-granted exemption"
        assert rel in tracked, f"{rel} is declared but not tracked"
        assert not _is_readable(path), (
            f"{rel} IS readable, so declaring it exempts nothing and hides everything — "
            "declare only what the scan genuinely cannot read"
        )


def test_no_declared_path_is_also_content_excluded():
    """A path must never be exempted twice by two different mechanisms."""
    import chipsim.ingest.drugbank_snapshot as ds

    declared = [rel for rel, _, _ in ds._declaration_entries(REPO_ROOT)]
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
    assert undecodable_unallowed(tmp_path, [path.name]) == []


def test_no_readable_structured_container_is_declared():
    """E6-2: only RENDERED artifacts may be declared. A container in the list is the category
    collapse the clause forbids — and the h5ad was exactly that."""
    import chipsim.ingest.drugbank_snapshot as ds

    containers = [
        rel
        for rel, _, _ in ds._declaration_entries(REPO_ROOT)
        if Path(rel).suffix.lower() in {".parquet", ".pq", ".h5", ".h5ad", ".hdf5", ".feather"}
    ]
    assert containers == [], (
        f"declared readable container(s): {containers}. A structured container is always read."
    )


def test_an_unreadable_container_fails_loudly_rather_than_inviting_a_declaration(tmp_path):
    """If the HDF5 reader is absent the file must NOT quietly become 'undecodable — declare it',
    because declaring a container is precisely what E6-2 forbids."""
    import chipsim.ingest.drugbank_snapshot as ds

    path = _hdf5(tmp_path, "x.h5ad", {"obs/p": [b"FIXTURE"]})
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(ds, "_HDF5_READER", None)
        with pytest.raises(RuntimeError, match="h5py"):
            ds.real_accession_hits(tmp_path, [path.name])


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
    assert undecodable_unallowed(tmp_path, [str(base / "leak.pdf")]) == [str(base / "leak.pdf")]


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
    assert path_owner(rel, recognised_owners(REPO_ROOT, _tracked_paths())) == owner


def test_a_file_this_project_owns_fails_this_gate(tmp_path):
    rel = "projects/lung-on-chipsim/data/interim/mystery.bin"
    target = tmp_path / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"\x00\xff not text")
    assert failing_undeclared(tmp_path, [rel]) == [rel]


def test_a_file_another_project_owns_is_listed_but_does_not_fail_this_gate(tmp_path):
    """The whole point of E6-1b: another team not yet having adopted the rule must not turn THIS
    gate red — measured, that was 24 files on day one — while the file stays visible and counted."""
    rel = "projects/perturb-seq-eval/paper/figures/fig9.pdf"
    target = tmp_path / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"%PDF-1.4\x00\xff")
    # The marker is what makes perturb-seq-eval a REAL project rather than a name in a path: an
    # owner minted by mkdir listed as somebody else's problem and failed nobody's gate.
    listing = [rel, "projects/perturb-seq-eval/pyproject.toml"]
    assert failing_undeclared(tmp_path, listing) == []
    assert undeclared_report(tmp_path, listing) == [(rel, "perturb-seq-eval")]


def test_a_path_owned_by_NO_project_fails_this_gate(tmp_path):
    """LOAD-BEARING FOR E6-4. `.claude/usr/**/dispatches/` belongs to no project, so a non-.md
    dispatch payload keeps failing here. Drafted without this rule, E6-1b would have made
    dispatches/leak.pdf listed and UNFAILABLE ANYWHERE — silently re-opening the hole E6-4 closed
    one clause above, in the same revision that closed it."""
    rel = ".claude/usr/matthew-mo/lung-on-chipsim/dispatches/leak.pdf"
    target = tmp_path / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"%PDF-1.4\x00\xff and a real accession " + REAL.encode())
    assert failing_undeclared(tmp_path, [rel]) == [rel]
    assert undeclared_report(tmp_path, [rel]) == [(rel, None)]


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
    assert undeclared_report(tmp_path, [*files, *markers]) == sorted(files.items())


def test_the_accession_scan_does_not_shrink_with_the_failure_scope(tmp_path):
    """ "The accession scan itself stays repo-wide and does not shrink — this scopes only who a
    missing DECLARATION blocks." A readable file in another project's tree is still a hit."""
    rel = "projects/perturb-seq-eval/notes.md"
    target = tmp_path / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(f"see {REAL}\n")
    assert [a for _, a in real_accession_hits(tmp_path, [rel])] == [REAL]
    assert failing_undeclared(tmp_path, [rel]) == []


def test_the_live_report_is_not_vacuous_and_this_gate_is_green():
    """The live half. Anti-vacuity moved from the declared list (now empty for this project, since
    none of the 24 was ever ours) to the REPORT: the other teams' artifacts must still be counted
    and named, not silently dropped by the scoping."""
    tracked = _tracked_paths()
    report = undeclared_report(REPO_ROOT, tracked)
    assert failing_undeclared(REPO_ROOT, tracked) == [], (
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
    assert undecodable_unallowed(tmp_path, [path.name]) == [path.name]


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
    assert undecodable_unallowed(tmp_path, [path.name]) == [path.name]


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
    import chipsim.ingest.drugbank_snapshot as ds

    target = REPO_ROOT / "projects/perturb-seq-eval/data/Adamson2016_pilot.h5ad"
    if not target.is_file():
        pytest.skip("the AnnData artifact is not present in this checkout")
    chunks = ds._scan_chunks(target)
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

    assert undecodable_unallowed(tmp_path, [rel_binary]) == [rel_binary]
    assert failing_undeclared(tmp_path, [rel_binary]) == [rel_binary], "unowned -> fails here"
    # The genuine message keeps its waiver: its text IS the audit trail.
    assert real_accession_hits(tmp_path, [rel_message]) == []
    assert undecodable_unallowed(tmp_path, [rel_message]) == []


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
    import chipsim.ingest.drugbank_snapshot as ds

    _recognised = recognised_owners(REPO_ROOT, _tracked_paths())
    foreign = [
        rel
        for rel, _, surface in ds._declaration_entries(REPO_ROOT)
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

    import chipsim.ingest.drugbank_snapshot as ds

    declared = f"projects/{THIS_PROJECT}/docs/blob.dat"
    target = tmp_path / declared
    target.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"drugbank_id": [REAL]}).to_parquet(target, engine="pyarrow")
    digest = hashlib.sha256(target.read_bytes()).hexdigest()

    _decl_fixture(
        tmp_path,
        project_entries=[{"path": declared, "sha256": digest, "why": "named to look opaque"}],
    )
    with pytest.raises(AssertionError):
        ds.assert_no_container_is_declared(tmp_path)


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
    import chipsim.ingest.drugbank_snapshot as ds
    from chipsim import pipeline

    rel = "projects/lung-on-chipsim/data/interim/mystery.bin"
    target = tmp_path / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"\x00\xff")

    # Steer the ROOT, not an environment variable: r2.23 E-08 makes the command derive the repo
    # root structurally, precisely so no ambient setting can narrow what it scans.
    monkeypatch.setattr(ds, "repo_root", lambda: tmp_path)
    monkeypatch.setattr(ds, "_tracked_listing", lambda root: ([rel], []))
    # This test fabricates a listing under tmp_path, which the witness check refuses BY DESIGN
    # (a listing must contain this module's own tracked file). Disabled here only, so that this
    # test can still say what it is about — the exit code for a file that fails the gate. The
    # witness check has its own tests above.
    monkeypatch.setattr(ds, "_refuse_a_scan_that_cannot_see_itself", lambda root, paths: None)
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
    from chipsim.ingest.drugbank_snapshot import repo_root

    assert repo_root() == REPO_ROOT


def test_repo_root_walks_past_a_directory_that_merely_looks_like_a_repo_root(tmp_path, monkeypatch):
    """The marker is `.git`, not "a directory containing projects/".

    A mutant that stops at the first ancestor holding a `projects/` directory — never consulting
    `.git` at all — survived the whole previous suite, because in the live tree those two rules
    name the same directory. Only a fixture can tell them apart.
    """
    import chipsim.ingest.drugbank_snapshot as ds

    outer = _init_repo(tmp_path / "outer")
    package_parent = outer / "nested" / "projects" / "lung-on-chipsim"
    (package_parent / "chipsim").mkdir(parents=True)
    assert not (outer / "nested" / ".git").exists(), "the lookalike must NOT be a repository"

    monkeypatch.setattr(ds, "source_root", lambda: package_parent)
    assert ds.repo_root() == outer.resolve()


@pytest.mark.parametrize("marker", ["directory", "worktree_file"])
def test_repo_root_accepts_a_worktree_git_file_not_only_a_git_directory(
    tmp_path, monkeypatch, marker
):
    """A worktree's `.git` is a FILE. `is_dir()` instead of `exists()` is a one-character change
    that silently reinstates the project-root scan IN EVERY WORKTREE — which is where this repo's
    work actually happens. The commit message claimed this property; nothing tested it, and the
    mutant survived."""
    import chipsim.ingest.drugbank_snapshot as ds

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
    monkeypatch.setattr(ds, "source_root", lambda: package_parent)
    assert ds.repo_root() == root.resolve()


def test_repo_root_refuses_a_broken_git_marker_rather_than_collapsing_to_the_project_root(
    tmp_path, monkeypatch
):
    """An aborted `git init`, a copied worktree stub or a half-done submodule conversion leaves a
    `.git` that git cannot open. Trusting the marker's existence alone collapsed the scan back to
    the project root and restored E-08 verbatim — and this repo DOES use submodules, so a sibling
    of this project is already one."""
    import chipsim.ingest.drugbank_snapshot as ds

    outer = _init_repo(tmp_path / "outer")
    package_parent = outer / "projects" / "lung-on-chipsim"
    (package_parent / "chipsim").mkdir(parents=True)
    (package_parent / ".git").write_text("gitdir: /nonexistent/.git/worktrees/gone\n")

    monkeypatch.setattr(ds, "source_root", lambda: package_parent)
    with pytest.raises(ds.RecordContentScanError) as exc:
        ds.repo_root()
    message = str(exc.value).replace(str(tmp_path), "<tmp>")
    assert "git cannot open a repository" in message
    assert "clean" in message, "the refusal must say why an unscannable tree is not a clean one"


def test_repo_root_refuses_when_no_repository_exists_above_the_package(tmp_path, monkeypatch):
    """The fallback that shipped returned `source_root()` — the narrow root the finding is ABOUT.
    Composed with a listing that swallowed its own failure, a non-editable install printed a clean
    report over a tree it had never read. Reproduced end-to-end before this fix."""
    import chipsim.ingest.drugbank_snapshot as ds

    bare = tmp_path / "a" / "b"
    bare.mkdir(parents=True)
    if any((p / ".git").exists() for p in [bare, *bare.parents]):
        pytest.skip(
            "this temp directory sits inside a repository, so the no-repo case is untestable here"
        )

    monkeypatch.setattr(ds, "source_root", lambda: bare)
    with pytest.raises(ds.RecordContentScanError) as exc:
        ds.repo_root()
    assert "no git repository" in str(exc.value)


def test_a_listing_that_could_not_be_produced_is_not_an_empty_one(tmp_path):
    """`_tracked_paths_for_report` returned `[]` when git failed, and the renderer printed that as
    "0 (failing this gate: 0)" with exit 0. The test-side twin of this function has used
    `check=True` since the day it was written, beneath a test titled "a scan over the wrong or an
    empty list reports clean" — the guard existed in the suite and not in the command."""
    import chipsim.ingest.drugbank_snapshot as ds

    not_a_checkout = tmp_path / "plain"
    not_a_checkout.mkdir()
    with pytest.raises(ds.RecordContentScanError) as exc:
        ds._tracked_paths_for_report(not_a_checkout)
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
    import chipsim.ingest.drugbank_snapshot as ds

    repo = _init_repo(tmp_path / "corrupt")
    (repo / ".git" / "index").write_bytes(b"this is not an index")
    assert ds._toplevel_of(repo) == repo.resolve(), "the checkout itself must still resolve"

    with pytest.raises(ds.RecordContentScanError) as exc:
        ds._tracked_paths_for_report(repo)
    message = str(exc.value)
    assert "git ls-files failed" in message
    # git's own diagnostic is what tells the operator WHICH failure this is; the old code captured
    # stderr and threw it away, so the one useful sentence never reached anybody.
    assert "no diagnostic" not in message


def test_an_emptied_listing_cannot_pass_as_a_scan_of_this_tree(monkeypatch):
    """The witness check: the listing must contain THIS module's own tracked file. One assertion
    covering an unrelated enclosing repository, an index read from elsewhere, and a listing emptied
    by any means at all."""
    import chipsim.ingest.drugbank_snapshot as ds

    monkeypatch.setattr(ds, "_tracked_listing", lambda root: ([], []))
    with pytest.raises(ds.RecordContentScanError) as exc:
        ds.render_undeclared_report()
    assert "this module's own file" in str(exc.value)


def test_the_scan_refuses_a_repository_that_does_not_contain_this_package(tmp_path, monkeypatch):
    """An unrelated enclosing repository — a dotfiles `$HOME`, a wrapper monorepo — became the scan
    root and the gate reported on THAT repo, exiting on its files rather than ours."""
    import chipsim.ingest.drugbank_snapshot as ds

    stranger = _init_repo(tmp_path / "stranger")
    with pytest.raises(ds.RecordContentScanError) as exc:
        ds._refuse_a_scan_that_cannot_see_itself(stranger, ["some/other/file.txt"])
    assert "does not contain this package" in str(exc.value)


def test_git_environment_variables_cannot_steer_the_scan(tmp_path, monkeypatch):
    """`subprocess.run` inherits the environment, so GIT_DIR/GIT_INDEX_FILE override `cwd` outright:
    the report printed the CORRECT root while having listed a different repository's index — more
    misleading than the bug being fixed. The docstring named four members of the ambient-state
    family and claimed immunity while leaving a fifth channel open."""
    import chipsim.ingest.drugbank_snapshot as ds

    decoy = _init_repo(tmp_path / "decoy")
    monkeypatch.setenv("GIT_DIR", str(decoy / ".git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(decoy))
    monkeypatch.setenv("GIT_CONFIG_COUNT", "1")
    monkeypatch.setenv("GIT_CONFIG_KEY_0", "core.fsmonitor")
    monkeypatch.setenv("GIT_CONFIG_VALUE_0", "true")

    assert ds._toplevel_of(REPO_ROOT) == REPO_ROOT, (
        "the scan resolved a different tree than the one it was pointed at"
    )
    assert (
        "projects/lung-on-chipsim/chipsim/ingest/drugbank_snapshot.py"
        in ds._tracked_paths_for_report(REPO_ROOT)
    )


def test_the_scan_does_not_execute_configuration_from_the_repository_it_reads(tmp_path):
    """`core.fsmonitor` is a repo-local config value git EXECUTES. A planted one in an ancestor
    repository ran as the invoking user during `record-content-report`. The CTO's B2 ruling (#44)
    requires both that the path be validated as the expected repository and that the invocation not
    honour config from a tree we do not trust."""
    import chipsim.ingest.drugbank_snapshot as ds

    hostile = _init_repo(tmp_path / "hostile")
    marker = tmp_path / "it-ran"
    hook = tmp_path / "hook.sh"
    hook.write_text(f"#!/bin/sh\ntouch {marker}\nexit 1\n")
    hook.chmod(0o755)
    subprocess.run(["git", "config", "core.fsmonitor", str(hook)], cwd=hostile, check=True)

    ds._git(["ls-files"], cwd=hostile)
    assert not marker.exists(), "the scan executed a command configured by the repository it read"


def test_the_shipped_command_prints_exactly_what_the_function_renders(capsys):
    """The defect was command != function, so the assertion is that equality — at the file's own
    oracle, and immune to how many binaries other teams happen to track today.

    The count-based assertion this replaces (`>= 20`) was a floor under a number this whole
    mechanism exists to drive to ZERO: the moment perturb-seq-eval or paper_standalone declares its
    binaries, a correct implementation goes red.
    """
    from chipsim import pipeline
    from chipsim.ingest.drugbank_snapshot import _render_for_root

    expected_text, expected_code = _render_for_root(REPO_ROOT)
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
    import chipsim.ingest.drugbank_snapshot as ds
    from chipsim import pipeline

    def refuse(*_args, **_kwargs):
        raise ds.RecordContentScanError("no repository found in this test")

    monkeypatch.setattr(ds, "repo_root", refuse)
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
    from chipsim.ingest.drugbank_snapshot import path_owner, recognised_owners

    tracked = _tracked_paths()
    recognised = recognised_owners(REPO_ROOT, tracked)

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
    from chipsim.ingest.drugbank_snapshot import render_path

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
    import chipsim.ingest.drugbank_snapshot as ds
    from chipsim import pipeline

    pipeline.main(["record-content-report"])
    printed = capsys.readouterr().out
    assert str(Path(ds.__file__).resolve()) in printed


# --- r2.24 E-10: a path the scan cannot reach is counted always, and fails only where we own it ---
#
# I shipped this FATAL in §8, on the reading that a scan which cannot see everything must not read
# as clean. The CTO ruled that one level too wide: it makes the report unrunnable in a legitimate
# sparse or partial checkout, and a control nobody can run is not a control. Counting is never
# scoped (scoping the count would be E-08 again); FAILING is scoped by ownership (that is E6-1b).


def _missing_tracked(tmp_path, rel, markers=()):
    """A listing that names `rel` while `rel` is absent from disk — skip-worktree, sparse checkout,
    or a partial clone that never fetched the blob. The payload is IN the repository, which is what
    the invariant protects; the worktree simply does not have it."""
    import chipsim.ingest.drugbank_snapshot as ds

    witness = Path(ds.__file__).resolve()
    listing = [rel, *markers]
    return listing, witness


def test_a_tracked_path_that_is_not_on_disk_is_counted_and_reported(tmp_path, monkeypatch, capsys):
    """The original sin was the silent drop: `if not target.is_file(): continue`. A payload
    committed in HEAD but absent from the worktree produced a report that said nothing at all."""
    import chipsim.ingest.drugbank_snapshot as ds
    from chipsim import pipeline

    rel = "docs/ghost_payload.bin"
    listing, _ = _missing_tracked(tmp_path, rel)
    monkeypatch.setattr(ds, "repo_root", lambda: tmp_path)
    monkeypatch.setattr(ds, "_tracked_listing", lambda root: (listing, []))
    monkeypatch.setattr(ds, "_refuse_a_scan_that_cannot_see_itself", lambda root, paths: None)

    code = pipeline.main(["record-content-report"])
    printed = capsys.readouterr().out

    assert rel in printed, "a path the scan could not reach must never be silently dropped"
    assert "not present on disk" in printed
    assert code == 2, "docs/ is owned by no project, and unowned fails here (E6-1b)"


def test_a_missing_path_another_project_owns_is_listed_but_does_not_fail_this_gate(
    tmp_path, monkeypatch, capsys
):
    """Scoping the FAILURE by ownership is E6-1b; scoping the COUNT would be E-08 again. Another
    team's un-materialised file is visible and counted here, and red on nobody's board but theirs."""
    import chipsim.ingest.drugbank_snapshot as ds
    from chipsim import pipeline

    rel = "projects/perturb-seq-eval/paper/ghost.pdf"
    listing, _ = _missing_tracked(
        tmp_path, rel, markers=("projects/perturb-seq-eval/pyproject.toml",)
    )
    monkeypatch.setattr(ds, "repo_root", lambda: tmp_path)
    monkeypatch.setattr(ds, "_tracked_listing", lambda root: (listing, []))
    monkeypatch.setattr(ds, "_refuse_a_scan_that_cannot_see_itself", lambda root, paths: None)

    code = pipeline.main(["record-content-report"])
    printed = capsys.readouterr().out

    assert rel in printed and "not present on disk" in printed
    assert code == 0, "another project's missing file is counted here and fails only on their gate"


def test_a_missing_path_this_project_owns_fails_the_gate(tmp_path, monkeypatch, capsys):
    import chipsim.ingest.drugbank_snapshot as ds
    from chipsim import pipeline

    rel = f"projects/{THIS_PROJECT}/data/processed/ghost.parquet"
    listing, _ = _missing_tracked(
        tmp_path, rel, markers=(f"projects/{THIS_PROJECT}/pyproject.toml",)
    )
    monkeypatch.setattr(ds, "repo_root", lambda: tmp_path)
    monkeypatch.setattr(ds, "_tracked_listing", lambda root: (listing, []))
    monkeypatch.setattr(ds, "_refuse_a_scan_that_cannot_see_itself", lambda root, paths: None)

    code = pipeline.main(["record-content-report"])
    assert rel in capsys.readouterr().out
    assert code == 2


def test_a_sparse_checkout_can_still_run_the_report(tmp_path, monkeypatch, capsys):
    """The reason the ruling went this way: fatal-always made the report unrunnable wherever a
    legitimate sparse or partial checkout is in use, and a control nobody can run is not a control.
    Exit 3 stays reserved for "could not scan AT ALL"."""
    import chipsim.ingest.drugbank_snapshot as ds
    from chipsim import pipeline

    rel = "paper_standalone/figures/never_fetched.pdf"
    listing, _ = _missing_tracked(tmp_path, rel, markers=("paper_standalone/README.md",))
    monkeypatch.setattr(ds, "repo_root", lambda: tmp_path)
    monkeypatch.setattr(ds, "_tracked_listing", lambda root: (listing, []))
    monkeypatch.setattr(ds, "_refuse_a_scan_that_cannot_see_itself", lambda root, paths: None)

    code = pipeline.main(["record-content-report"])
    printed = capsys.readouterr().out

    assert code != 3, "a sparse checkout is not the same as being unable to scan"
    assert code == 0
    assert rel in printed


def test_the_witness_check_is_still_fatal(tmp_path):
    """E-10 relaxed the UNRESOLVABLE path, not the witness. A listing that is not a listing of this
    tree is still "could not scan at all" — exit 3, not a report."""
    import chipsim.ingest.drugbank_snapshot as ds

    stranger = _init_repo(tmp_path / "stranger")
    with pytest.raises(ds.RecordContentScanError):
        ds._refuse_a_scan_that_cannot_see_itself(stranger, ["some/other/file.txt"])


# --- r2.24 E-02 / E6-1 / E6-3 / E-05 / E-11: the declaration surface ---------------------------
#
# The removal half shipped in r2.22 and the READ half never did: RENDERED_ARTIFACT_DECLARATIONS has
# been an empty frozenset that nothing populates, and E6-1b's scoping kept the suite green without
# it — which is precisely why it was easy to miss. I found it by re-reading the clause against the
# code, not by a failing test, so these tests exist to make the absence of the data VISIBLE rather
# than convenient.


def _decl_fixture(tmp_path, project_entries=None, repo_entries=None, owners=None):
    """A repo-shaped fixture carrying both declaration files and the markers that make owners real."""
    import yaml

    import chipsim.ingest.drugbank_snapshot as ds

    proj = tmp_path / "projects" / THIS_PROJECT
    (proj / "configs").mkdir(parents=True, exist_ok=True)
    (tmp_path / "config").mkdir(parents=True, exist_ok=True)

    project_doc = {"version": 1, "declarations": project_entries or []}
    repo_doc = {"version": 1, "declarations": repo_entries or []}
    if owners is not None:
        repo_doc["owners"] = owners

    (proj / "configs" / "record_content_declarations.yaml").write_text(yaml.safe_dump(project_doc))
    (tmp_path / "config" / "record_content_declarations.yaml").write_text(yaml.safe_dump(repo_doc))

    listing = [
        ds.PROJECT_DECLARATION_FILE,
        ds.REPO_DECLARATION_FILE,
        f"projects/{THIS_PROJECT}/pyproject.toml",
    ]
    (proj / "pyproject.toml").write_text("[project]\nname = 'x'\n")
    return listing


def _write(tmp_path, rel, data: bytes):
    target = tmp_path / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def test_a_declaration_must_pin_the_content_not_just_the_path(tmp_path):
    """E6-3. Every declared file is a BUILD OUTPUT, so a path-keyed declaration goes silent forever
    the moment the artifact is regenerated with different content — the declaration would still be
    sitting there, matching by name, clearing a file nobody has looked at since."""
    import chipsim.ingest.drugbank_snapshot as ds

    rel = f"projects/{THIS_PROJECT}/docs/render.bin"
    digest = _write(tmp_path, rel, b"\x00\xffOPAQUE")
    listing = _decl_fixture(
        tmp_path,
        project_entries=[
            {"path": rel, "sha256": digest, "why": "rendered figure, not a container"}
        ],
    ) + [rel]

    assert rel in ds.valid_declarations(tmp_path, listing)
    assert ds.declaration_defects(tmp_path, listing) == []
    assert ds.undecodable_unallowed(tmp_path, listing) == [], "a validly declared file is cleared"


def test_a_declaration_goes_STALE_when_the_artifact_is_regenerated(tmp_path):
    """The whole reason for E6-3. Regenerate the artifact; the declaration must stop clearing it and
    must SAY SO, rather than silently going on matching by path."""
    import chipsim.ingest.drugbank_snapshot as ds

    rel = f"projects/{THIS_PROJECT}/docs/render.bin"
    digest = _write(tmp_path, rel, b"\x00\xffOPAQUE")
    listing = _decl_fixture(
        tmp_path, project_entries=[{"path": rel, "sha256": digest, "why": "rendered figure"}]
    ) + [rel]

    _write(tmp_path, rel, b"\x00\xffREGENERATED")  # same path, different content

    assert rel not in ds.valid_declarations(tmp_path, listing)
    defects = dict(ds.declaration_defects(tmp_path, listing))
    assert rel in defects and "stale" in defects[rel].lower()
    assert rel in ds.undecodable_unallowed(tmp_path, listing), "a stale declaration clears nothing"


def test_a_derived_from_claim_must_name_a_tracked_source_that_is_in_scope(tmp_path):
    """The self-maintaining alternative: "derived from tracked source S, and S is in scope" is a
    claim a reader can CHECK, unlike a comment saying "none of these is a DrugBank artifact"."""
    import chipsim.ingest.drugbank_snapshot as ds

    rel = f"projects/{THIS_PROJECT}/docs/plot.bin"
    src = f"projects/{THIS_PROJECT}/docs/plot_source.csv"
    _write(tmp_path, rel, b"\x00\xffOPAQUE")
    _write(tmp_path, src, b"name,value\nalpha,1\n")
    listing = _decl_fixture(
        tmp_path,
        project_entries=[{"path": rel, "derived_from": src, "why": "plotted from the tracked csv"}],
    ) + [rel, src]

    assert rel in ds.valid_declarations(tmp_path, listing)

    # ...and the claim fails when the source is NOT tracked, which is what makes it self-maintaining.
    listing_without_source = [p for p in listing if p != src]
    assert rel not in ds.valid_declarations(tmp_path, listing_without_source)
    defects = dict(ds.declaration_defects(tmp_path, listing_without_source))
    assert "not tracked" in defects[rel].lower()


def test_this_project_may_not_declare_another_projects_artifacts(tmp_path):
    """E6-1, the clause's own "why": 24 paths belonging to perturb-seq-eval and paper_standalone were
    declared inside this module's source, so another team adding a figure turned THIS gate red and
    the repair landed in a file they neither own nor can judge."""
    import chipsim.ingest.drugbank_snapshot as ds

    rel = "projects/perturb-seq-eval/paper/figure.pdf"
    digest = _write(tmp_path, rel, b"\x00\xffFOREIGN")
    listing = _decl_fixture(
        tmp_path, project_entries=[{"path": rel, "sha256": digest, "why": "not mine to declare"}]
    ) + [rel, "projects/perturb-seq-eval/pyproject.toml"]

    assert rel not in ds.valid_declarations(tmp_path, listing)
    defects = dict(ds.declaration_defects(tmp_path, listing))
    assert "perturb-seq-eval" in defects[rel] and "owns" in defects[rel].lower()


def test_the_repo_root_surface_declares_UNOWNED_paths_and_only_those(tmp_path):
    """E-05. Unowned means every repo-root location, so a new docs/architecture.png from anyone fails
    THIS gate and E6-1's "do not re-declare on their behalf" left no legitimate way to clear it.
    Rule 9: state where declaring IS permitted rather than leaving the permitted case unreachable."""
    import chipsim.ingest.drugbank_snapshot as ds

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

    assert unowned in ds.valid_declarations(tmp_path, listing)
    defects = dict(ds.declaration_defects(tmp_path, listing))
    assert owned in defects, "an OWNED path does not belong in the repo-root surface"
    assert "repo-root" in defects[owned].lower()


def test_a_declaration_for_a_path_that_is_not_tracked_is_reported_as_rot(tmp_path):
    """A declaration nobody checks is rot: it accumulates, it reads as coverage, and it clears
    nothing. The file it named was deleted or renamed and the entry stayed behind."""
    import chipsim.ingest.drugbank_snapshot as ds

    rel = f"projects/{THIS_PROJECT}/docs/deleted.bin"
    listing = _decl_fixture(
        tmp_path, project_entries=[{"path": rel, "sha256": "0" * 64, "why": "long gone"}]
    )

    defects = dict(ds.declaration_defects(tmp_path, listing))
    assert rel in defects and "not tracked" in defects[rel].lower()


def test_a_readable_container_can_never_be_declared(tmp_path):
    """E6-2, enforced against the DATA now that the data exists. Checked by MAGIC, not suffix: a
    suffix filter is name-based dispatch, and a container named blob.dat walks through it."""
    import chipsim.ingest.drugbank_snapshot as ds

    rel = f"projects/{THIS_PROJECT}/data/processed/sneaky.dat"
    digest = _write(tmp_path, rel, b"PAR1" + b"\x00" * 32)
    listing = _decl_fixture(
        tmp_path, project_entries=[{"path": rel, "sha256": digest, "why": "claims to be opaque"}]
    ) + [rel]

    defects = dict(ds.declaration_defects(tmp_path, listing))
    assert rel in defects and "container" in defects[rel].lower()
    assert rel not in ds.valid_declarations(tmp_path, listing)


def test_an_entry_with_both_claims_or_neither_cannot_be_evaluated(tmp_path):
    """Malformed declaration DATA is a configuration error the gate cannot evaluate, so it is exit 3
    (could not scan), not exit 2 (files fail) and certainly not a pass."""
    import chipsim.ingest.drugbank_snapshot as ds

    rel = f"projects/{THIS_PROJECT}/docs/x.bin"
    digest = _write(tmp_path, rel, b"\x00\xff")

    both = _decl_fixture(
        tmp_path,
        project_entries=[{"path": rel, "sha256": digest, "derived_from": "a.csv", "why": "?"}],
    ) + [rel]
    with pytest.raises(ds.RecordContentScanError, match="exactly one"):
        ds.valid_declarations(tmp_path, both)


def test_the_owner_registry_is_declared_and_narrows_the_marker_heuristic(tmp_path):
    """E-11. A tracked marker is louder than mkdir but still addable by anyone who adds a
    pyproject.toml, so it is a MITIGATION, not proof. The declared registry is authoritative — and
    it NARROWS: an owner must be both declared AND carry its marker, so neither a declaration alone
    nor a file alone can mint one."""
    import chipsim.ingest.drugbank_snapshot as ds

    listing = _decl_fixture(tmp_path, owners=[THIS_PROJECT, "perturb-seq-eval"]) + [
        "projects/perturb-seq-eval/pyproject.toml",
        "projects/undeclared-but-real/pyproject.toml",
        "projects/declared-but-absent/anything.txt",
    ]

    recognised = ds.recognised_owners(tmp_path, listing)
    assert THIS_PROJECT in recognised and "perturb-seq-eval" in recognised
    assert "undeclared-but-real" not in recognised, "a marker alone does not mint an owner"
    assert "declared-but-absent" not in recognised, "a declaration alone does not mint one either"


def test_the_report_states_how_many_declarations_it_read(capsys):
    """The failure mode this whole clause is about is a mechanism that is easy to MISS because
    nothing exercises it. An empty declaration set is the correct state today — and it must be
    visible as a number rather than implied by silence."""
    from chipsim import pipeline

    pipeline.main(["record-content-report"])
    printed = capsys.readouterr().out
    assert "declarations read:" in printed


def test_the_shipped_declaration_files_hold():
    """ANTI-ROT over the live data. Every shape rule is enforced by the validator rather than by a
    test walking the list, so this one assertion covers a stale pin, a deleted path, a foreign path
    declared here, a readable file declared as unreadable, and a container declared at all.

    It is the assertion that stays meaningful when the surface stops being empty — the loops above
    run zero times today and will quietly keep passing however wrong a future entry is.
    """
    import chipsim.ingest.drugbank_snapshot as ds

    assert ds.declaration_defects(REPO_ROOT, _tracked_paths()) == []


def test_the_declared_owner_registry_covers_every_project_the_markers_support():
    """A registry that DROPS a real project does not fail loudly — that project's files silently
    become UNOWNED, and unowned fails THIS gate, so another team's artifacts would start turning
    this module red. The registry narrows by design; this is the check that the narrowing was
    deliberate rather than an omission.

    The oracle is derived here independently, by walking the tracked markers, rather than by asking
    the module — otherwise it would agree with the code by construction.
    """
    import chipsim.ingest.drugbank_snapshot as ds

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

    declared = ds.declared_owner_registry(REPO_ROOT)
    assert declared is not None, "the repo-root surface must carry the registry"
    missing = oracle - declared
    assert missing == set(), (
        f"projects with a tracked marker that the registry omits: {sorted(missing)}. Their files "
        "would be treated as unowned, and unowned fails THIS gate."
    )


def test_the_owner_registry_narrows_rather_than_widens():
    """Declaring a project that has no marker must not mint it. The registry is an intersection, so
    a declaration alone is not evidence any more than a `mkdir` was."""
    import chipsim.ingest.drugbank_snapshot as ds

    recognised = ds.recognised_owners(REPO_ROOT, _tracked_paths())
    declared = ds.declared_owner_registry(REPO_ROOT)
    assert recognised <= declared, "an owner was recognised that the registry does not declare"
