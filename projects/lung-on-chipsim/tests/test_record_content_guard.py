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

import subprocess
from pathlib import Path

import pytest

from chipsim.ingest.drugbank_snapshot import (
    DRUGBANK_ID_EXCLUDED_FILES,
    DRUGBANK_ID_LEDGER,
    RENDERED_ARTIFACT_DECLARATIONS,
    THIS_PROJECT,
    _is_readable,
    accession_structure_tuples,
    failing_undeclared,
    is_accession_excluded,
    ledger_tuple_hits,
    path_owner,
    real_accession_hits,
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


def test_a_declared_binary_file_is_not_reported(tmp_path, monkeypatch):
    """RENDERED_ARTIFACT_DECLARATIONS is EMPTY in this repo (E6-1: the foreign declarations left), so the
    mechanism is exercised with a synthetic declaration owned by THIS project — which is what a
    real entry here would have to be."""
    import chipsim.ingest.drugbank_snapshot as ds

    declared = "projects/lung-on-chipsim/docs/figure.pdf"
    monkeypatch.setattr(ds, "RENDERED_ARTIFACT_DECLARATIONS", frozenset({declared}))
    target = tmp_path / declared
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"\xff\xfe not utf-8")
    assert undecodable_unallowed(tmp_path, [declared]) == []


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


def test_the_binary_allowlist_is_not_a_blanket():
    """The shape rules still bind every entry, but EMPTY is now the correct state (E6-1): this
    project owns no undecodable tracked file, and the other teams' paths are listed by
    `undeclared_report` rather than declared here. Anti-vacuity moved to the report test, which
    asserts those files are still counted and named."""
    for rel in RENDERED_ARTIFACT_DECLARATIONS:
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

    declared = "projects/lung-on-chipsim/docs/figure.pdf"
    monkeypatch.setattr(ds, "RENDERED_ARTIFACT_DECLARATIONS", frozenset({declared}))
    for rel in (f"vendor/{declared}", f"some/other/dir/{Path(declared).name}"):
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"\x00\xff not text")
        assert undecodable_unallowed(tmp_path, [rel]) == [rel], rel


def test_a_declared_path_is_still_scanned_when_its_bytes_are_readable(tmp_path, monkeypatch):
    """The allow-list declares that a file cannot be READ — never that its content is exempt.
    Adding `or rel in RENDERED_ARTIFACT_DECLARATIONS` to the accession scan survived the whole suite, which
    would have turned "somebody looked at this artifact once" into a blanket content waiver."""
    import chipsim.ingest.drugbank_snapshot as ds

    declared = "projects/lung-on-chipsim/docs/figure.pdf"
    monkeypatch.setattr(ds, "RENDERED_ARTIFACT_DECLARATIONS", frozenset({declared}))
    target = tmp_path / declared
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(f"see {REAL}\n")
    assert [a for _, a in real_accession_hits(tmp_path, [declared])] == [REAL]
    assert undecodable_unallowed(tmp_path, [declared]) == []


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
    tracked = set(_tracked_paths())
    for rel in sorted(RENDERED_ARTIFACT_DECLARATIONS):
        path = REPO_ROOT / rel
        assert path.is_file(), f"{rel} is declared but does not exist — a pre-granted exemption"
        assert rel in tracked, f"{rel} is declared but not tracked"
        assert not _is_readable(path), (
            f"{rel} IS readable, so declaring it exempts nothing and hides everything — "
            "declare only what the scan genuinely cannot read"
        )


def test_no_declared_path_is_also_content_excluded():
    """A path must never be exempted twice by two different mechanisms."""
    assert [rel for rel in RENDERED_ARTIFACT_DECLARATIONS if is_accession_excluded(rel)] == []


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
    containers = [
        rel
        for rel in RENDERED_ARTIFACT_DECLARATIONS
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
    assert path_owner(rel) == owner


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
    assert failing_undeclared(tmp_path, [rel]) == []
    assert undeclared_report(tmp_path, [rel]) == [(rel, "perturb-seq-eval")]


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
    assert undeclared_report(tmp_path, list(files)) == sorted(files.items())


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
    foreign = [rel for rel in RENDERED_ARTIFACT_DECLARATIONS if path_owner(rel) != THIS_PROJECT]
    assert foreign == [], (
        f"declared here but owned elsewhere: {foreign}. Declarations live with the project that "
        "owns the artifact (E6-1); declaring another team's file assigns them this gate's failure."
    )


def test_a_container_cannot_be_declared_even_if_its_name_hides_it(tmp_path, monkeypatch):
    """The "no container declared" test filtered by SUFFIX — name-based dispatch, the anti-pattern
    this module condemns 170 lines earlier. A container named `blob.dat` passed."""
    import pandas as pd

    import chipsim.ingest.drugbank_snapshot as ds

    declared = "projects/lung-on-chipsim/docs/blob.dat"
    target = tmp_path / declared
    target.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"drugbank_id": [REAL]}).to_parquet(target, engine="pyarrow")

    monkeypatch.setattr(ds, "RENDERED_ARTIFACT_DECLARATIONS", frozenset({declared}))
    with pytest.raises(AssertionError):
        ds.assert_no_container_is_declared(tmp_path)


# --- §7 Phase D: the report reaches a human ---------------------------------------------------


def test_the_report_is_printed_by_a_command_a_human_can_run(tmp_path, monkeypatch, capsys):
    """The CTO's question at the §6 boundary: is `undeclared_report` ever CALLED somewhere a human
    sees it, or only asserted on in tests? "Listing that reaches no one is functionally a silent
    skip", which is the thing r2.20 forbade."""
    from chipsim import pipeline

    monkeypatch.setenv("CHIPSIM_PROJECT_ROOT", str(tmp_path))
    code = pipeline.main(["record-content-report"])
    printed = capsys.readouterr().out
    assert code == 0
    assert "undeclared" in printed.lower()
    # Every LISTED path names its owner, and unowned is spelled out rather than left blank.
    listed = [ln for ln in printed.splitlines() if ln.startswith("  ") and "(none" not in ln]
    for line in listed:
        assert "owner=" in line and ("FAILS HERE" in line or "listed" in line)


def test_the_report_command_exits_non_zero_when_this_gate_would_fail(tmp_path, monkeypatch, capsys):
    from chipsim import pipeline

    rel = "projects/lung-on-chipsim/data/interim/mystery.bin"
    target = tmp_path / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"\x00\xff")
    monkeypatch.setenv("CHIPSIM_PROJECT_ROOT", str(tmp_path))

    import chipsim.ingest.drugbank_snapshot as ds

    monkeypatch.setattr(ds, "_tracked_paths_for_report", lambda root: [rel])
    code = pipeline.main(["record-content-report"])
    assert code == 2
    assert rel in capsys.readouterr().out
