"""The DrugBank record-content guard — principal invariant (CTO #120 §1), scope and
exclusions ruled in #122 §3, #122 §5 and the CTO ruling of 2026-09-16.

**The invariant.** The project does not redistribute DrugBank RECORD CONTENT: real
accessions, DrugBank-coined titles, and above all the ASSOCIATION of either with a
structure. A bare canonical structure identifier is not record content.

**Scope: the whole repository.** The previous scan ran `git ls-files` from the PROJECT
root, so it had only ever seen `projects/lung-on-chipsim/` — `workstreams/` and `.claude/`
were never in scope, which is how a tracked merge report came to carry 89 real accessions.

**The complete exclusion set (nothing else):**
  - `.claude/usr/**/dispatches/` — coordination records; redacting a sent message falsifies
    the audit trail of the rulings it carries (#122 §3);
  - `workstreams/lung-on-chipsim/plan/plan-approval-log.md` — append-only; rewriting a log to
    satisfy a scan falsifies the record the log exists to keep. The FILE, not a pattern over
    `plan/`: `build-plan.md` stays in scope so its fix is enforced rather than excused;
  - the sanctioned exclusion ledger pair (#120 §4) — which may carry accessions, but not an
    accession ASSOCIATED WITH A STRUCTURE.

**Two tests here are born failing, by ruling, and say so in their messages:**
  - the repo-wide scan, on `build-plan.md`, until r2.16 replaces its accessions with InChIKeys
    ("a test that fails because my file is wrong is the test working");
  - the ledger tuple check, on a comment pairing an accession with its full InChI, until the
    ledger drops its structure strings.

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
    assert is_accession_excluded(APPROVAL_LOG)
    assert all(is_accession_excluded(rel) for rel in DRUGBANK_ID_LEDGER)
    # In scope — the ruling keeps these enforced, not excused:
    assert not is_accession_excluded(BUILD_PLAN)
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
        APPROVAL_LOG: False,
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


def test_no_real_drugbank_accession_is_tracked_anywhere_in_the_repo_outside_the_exclusions():
    """BORN FAILING BY RULING until r2.16 lands: `build-plan.md` carries three accessions in
    its r2.13 note, and it is deliberately NOT excluded."""
    tracked = subprocess.run(
        ["git", "ls-files"], cwd=REPO_ROOT, capture_output=True, text=True, check=True
    ).stdout.split()
    hits = real_accession_hits(REPO_ROOT, tracked)
    assert hits == [], (
        f"real DrugBank accessions tracked outside the ruled exclusions: {hits}. If the only "
        f"hit is {BUILD_PLAN}, that is the r2.16 fix still pending (CTO ruling 2026-09-16)."
    )


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


def test_the_ledger_carries_no_accession_structure_tuple():
    """BORN FAILING BY RULING until the ledger change (#120 §4): the ledger may keep its
    accessions but not a structure associated with one. A plain "no InChI in the ledger"
    rule would be wrong — the ledger's tests hold an aspirin structure and an invalid
    sentinel that belong to no accession."""
    hits = ledger_tuple_hits(REPO_ROOT)
    assert hits == [], (
        f"accession/structure tuples in the sanctioned ledger: {hits}. Drop the structure "
        "strings, keep the accessions (#120 §4)."
    )
