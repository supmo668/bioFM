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

from chipsim.ingest.drugbank_snapshot import (
    DRUGBANK_ID_EXCLUDED_FILES,
    DRUGBANK_ID_LEDGER,
    accession_structure_tuples,
    is_accession_excluded,
    ledger_tuple_hits,
    real_accession_hits,
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
