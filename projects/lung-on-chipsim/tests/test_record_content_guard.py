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
    BINARY_ALLOWLIST,
    DRUGBANK_ID_EXCLUDED_FILES,
    DRUGBANK_ID_LEDGER,
    _is_readable,
    accession_structure_tuples,
    is_accession_excluded,
    ledger_tuple_hits,
    real_accession_hits,
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
    declared = next(iter(BINARY_ALLOWLIST))
    target = tmp_path / declared
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"\xff\xfe not utf-8")
    assert undecodable_unallowed(tmp_path, [declared]) == []


def test_every_undecodable_tracked_file_in_this_repo_is_declared():
    """The live half. A new binary lands -> this fails -> someone looks at it and declares it.
    24 files were being skipped in silence when this was written (17 .pdf, 5 .png, .dvi, .h5ad)."""
    undeclared = undecodable_unallowed(REPO_ROOT, _tracked_paths())
    assert undeclared == [], (
        f"{len(undeclared)} tracked file(s) cannot be decoded and are not declared in "
        f"BINARY_ALLOWLIST, so the scan never read them: {undeclared[:5]}"
    )


def test_the_binary_allowlist_is_not_a_blanket():
    """Anti-vacuity: the allow-list must name paths, not wave through a suffix or a directory."""
    assert BINARY_ALLOWLIST, "an empty allow-list would make the declaration test vacuous"
    for rel in BINARY_ALLOWLIST:
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


def test_the_allowlist_is_matched_by_EXACT_path_not_by_suffix_or_basename(tmp_path):
    """Both a path-suffix match and a basename match survived every earlier test, so
    `vendor/<declared path>` or any file sharing a declared BASENAME would have been silently
    exempted. The docstring claimed "exact path"; nothing checked it."""
    declared = min(BINARY_ALLOWLIST)
    for rel in (f"vendor/{declared}", f"some/other/dir/{Path(declared).name}"):
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"\x00\xff not text")
        assert undecodable_unallowed(tmp_path, [rel]) == [rel], rel


def test_a_declared_path_is_still_scanned_when_its_bytes_are_readable(tmp_path):
    """The allow-list declares that a file cannot be READ — never that its content is exempt.
    Adding `or rel in BINARY_ALLOWLIST` to the accession scan survived the whole suite, which
    would have turned "somebody looked at this artifact once" into a blanket content waiver."""
    declared = min(BINARY_ALLOWLIST)
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
    assert undecodable_unallowed(tmp_path, [ledger, dispatch]) == [ledger]


def test_every_declared_path_exists_is_tracked_and_is_genuinely_unreadable():
    """A declaration for a file that does not exist PRE-AUTHORISES whatever later lands at that
    path, and a declaration for a DECODABLE file hides nothing the scan could not already read.
    Three junk entries — a deleted figure, a pre-declared `data/processed/compounds.parquet`, and
    README.md — passed every earlier test. The ledger sets already had this check (above); the new
    set was simply left out of it."""
    tracked = set(_tracked_paths())
    for rel in sorted(BINARY_ALLOWLIST):
        path = REPO_ROOT / rel
        assert path.is_file(), f"{rel} is declared but does not exist — a pre-granted exemption"
        assert rel in tracked, f"{rel} is declared but not tracked"
        assert not _is_readable(path), (
            f"{rel} IS readable, so declaring it exempts nothing and hides everything — "
            "declare only what the scan genuinely cannot read"
        )


def test_no_declared_path_is_also_content_excluded():
    """A path must never be exempted twice by two different mechanisms."""
    assert [rel for rel in BINARY_ALLOWLIST if is_accession_excluded(rel)] == []


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
        for rel in BINARY_ALLOWLIST
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
