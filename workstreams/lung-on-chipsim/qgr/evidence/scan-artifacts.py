"""Scan the report's own artifacts for shaped content, and WRITE the result.

Why this exists (CTO rigour review pass 1, finding 3): Stage 1 claims H1 and H4 said the artifacts
"were scanned before commit" and "checked against the gate-9 citation defect". Both were bound to an
ACTION I took, not to an artifact a referee can open. An action leaves no evidence; §6.2 says that
fails rather than gets footnoted. So the scan records itself.

Three checks per file, and the third is the one gate 9 earned:

  1. accession shapes  -- unaccounted count from the production-backed scanner
  2. structure shapes  -- likewise
  3. reads-as-cited    -- whether the file satisfies `_carries_a_citation`, the predicate gate 9
                          showed can be satisfied by PROSE EXPLAINING IT. A report ABOUT that defect
                          that itself trips the predicate would be the defect one level up, so every
                          artifact is checked and the verdict recorded rather than assumed.

Counts and booleans only. No value, no identifier, no name is ever written.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

#: evidence/ -> qgr/ -> lung-on-chipsim/ -> workstreams/ -> repo root. Derived, never hardcoded.
ROOT = Path(__file__).resolve().parents[4]
PROJ = ROOT / "projects/lung-on-chipsim"
sys.path.insert(0, str(PROJ))

from tests.shape_scan import (  # noqa: E402
    _carries_a_citation,
    classify_sites,
    scan_accession_shapes,
    scan_structure_shapes,
)

#: The artifacts this report is responsible for. Globs, so a new one cannot be silently omitted --
#: a hand-maintained list is the defect this project has hit repeatedly.
PATTERNS = [
    # RECURSIVE, and widened to the whole published surface (pr-prep blocker 1).
    #
    # The principal ruled that `.claude/usr/**` PUBLISHES -- the audit chain IS the paper's
    # evidence, as it was for PR #7 -- on the CONDITION that the artifact scan actually covers it.
    # It did not: the previous four patterns reached 14 files and missed 130 dispatch records, the
    # deferred register, every `qgr/evidence/*.md`, and every JSON record. A landed surface that no
    # scan covers is precisely the gap this gate flagged.
    #
    # Non-recursive, name-shaped globs were also how `gate6-findings.md` escaped: same naming
    # family, one directory deeper. `**` fixes the class, not the instance.
    "workstreams/lung-on-chipsim/paper/**/*.md",
    "workstreams/lung-on-chipsim/qgr/**/*.md",
    "workstreams/lung-on-chipsim/qgr/**/*.py",
    "workstreams/lung-on-chipsim/qgr/**/*.json",
    # The audit surface is markdown today; there is no JSON under .claude/usr. A pattern for
    # a filetype that does not exist there would sit permanently empty, and the empty-pattern
    # check below cannot distinguish "never matched" from "STOPPED matching" without a
    # baseline -- so a speculative pattern would train a real signal to be ignored. If a new
    # filetype appears on that surface it needs a pattern, and the absence of one is the gap
    # a future scan should close with a recorded baseline rather than a guess.
    # THE CLASSIFIED ROOTS. Round 2 CRITICAL C-1: `CLASSIFIED_ROOTS` below names
    # `projects/lung-on-chipsim/` and `workstreams/lung-on-chipsim/`, but no pattern reached the
    # first one AT ALL and the second only via paper/** and qgr/**. So
    # `files_that_read_as_cited_in_classified_scope` was computed over a partial intersection and
    # could only be ~0 -- and H4 published that zero as a property OF THE SCOPE. 88 of 277 files.
    #
    # That is round 1's finding at a larger radius: the previous version was "true of the 10 files
    # the globs reached, false of every artifact". Widening the radius without making the SURFACE
    # equal the SCOPE only moves the same defect outward. The surface is now the union of the audit
    # surface, the paper artifacts, and both classified roots -- and `surface_vs_scope` REPORTS
    # reached/in-scope per root every run, so the next mismatch appears in the record instead of
    # being rediscovered by a reviewer.
    #
    # The classified roots are enumerated by `git ls-files` (see _classified_files), NOT by a glob.
    # The first attempt at this fix DID use globs and swept 26,623 files -- the virtualenv and
    # thousands of untracked per-run journal config copies -- because a filesystem glob and
    # `git ls-files` are two different enumerations of "the scope". Two enumerations that must agree
    # and are never compared is exactly the defect C-1 is, so the repair uses ONE corpus: the same
    # `git ls-files` list r250-classify.py classifies.
]

#: Extensions the scan reads inside the classified roots. Binary and data files are not prose.
CLASSIFIED_SUFFIXES = (".py", ".md", ".yaml", ".yml", ".json")

#: The roots whose properties the verdict and H4 talk about.
CLASSIFIED_ROOTS = ("projects/lung-on-chipsim/", "workstreams/lung-on-chipsim/")

#: The published audit chain. NOT a classified root: no classifier covers it, so a shaped token here
#: is fatal rather than deferred to the buckets.
AUDIT_SURFACE = (".claude/usr/",)


#: Not a glob. Named so the per-pattern tally and the empty-pattern check still see the classified
#: surface as a source, rather than it arriving from nowhere.
_CLASSIFIED_PSEUDO_PATTERN = "<git ls-files: classified roots>"
_AUDIT_PSEUDO_PATTERN = "<git ls-files: audit surface>"


def _is_guard_enforced(rel: str) -> bool:
    """Does r250-classify place this file's sites in the W/F/C/N buckets at all?

    It scopes OUT by PROPERTY, not by path -- configs are citation-governed (P5), fixtures and
    generated output are excluded (P4). Approximating that here by suffix and directory is a
    deliberate, stated APPROXIMATION so the published comparison is like-for-like; it is not a
    re-implementation of the classifier's rule, and where the two disagree the classifier's record
    governs. Recorded per file so a reader can check the split rather than trust it.
    """
    if not rel.endswith(".py"):
        return False
    return "/tests/fixtures/" not in rel


def _audit_surface_files() -> list[Path]:
    """TRACKED markdown on the published audit chain.

    `git ls-files` rather than `ROOT.glob(".claude/usr/**/*.md")`: the glob reached 3 untracked,
    `.gitignore`-covered handoff-history files and made them fatal, although the ruling that placed
    `.claude/usr` in scope is about what PUBLISHES. Tracked is what publishes.
    """
    tracked = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", ".claude/usr"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()
    return sorted(ROOT / rel for rel in tracked if rel.endswith(".md"))


def _classified_files() -> list[Path]:
    """Tracked files in the classified roots, from the corpus the CLASSIFIER uses.

    `git ls-files` rather than `ROOT.glob` deliberately: the glob form swept the virtualenv and the
    untracked per-run journal copies, and more importantly it was a SECOND enumeration of a scope the
    classifier already enumerates. Two enumerations that must agree, and that nothing compares, is
    the defect this function exists to close.
    """
    out: list[Path] = []
    for root_prefix in CLASSIFIED_ROOTS:
        tracked = subprocess.run(
            ["git", "-C", str(ROOT), "ls-files", root_prefix],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.split()
        for rel in tracked:
            if rel.endswith(CLASSIFIED_SUFFIXES):
                out.append(ROOT / rel)
    return sorted(set(out))


def main() -> int:
    # --no-write: a reviewer re-running this in someone else's worktree must leave it
    # exactly as found. Three of the four evidence scripts lacked this and could void a
    # bracket just by being re-run.
    write = "--no-write" not in sys.argv
    sha = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    results = []
    matched_per_pattern: dict[str, int] = {}
    seen: set[Path] = set()
    classified = _classified_files()
    audit = _audit_surface_files()
    for pattern in PATTERNS + [_CLASSIFIED_PSEUDO_PATTERN, _AUDIT_PSEUDO_PATTERN]:
        if pattern == _CLASSIFIED_PSEUDO_PATTERN:
            hits = classified
        elif pattern == _AUDIT_PSEUDO_PATTERN:
            hits = audit
        else:
            hits = sorted(ROOT.glob(pattern))
        matched_per_pattern[pattern] = len(hits)
        for path in hits:
            # The classified-root patterns OVERLAP paper/** and qgr/**. Scanning a file twice would
            # inflate files_scanned and double-count a cited file, so the per-pattern tally above
            # keeps its RAW hit count (that is what the empty-pattern check measures) while the
            # results below are deduplicated by path. A widening that corrupted the counts it exists
            # to fix would be the family again.
            if path in seen:
                continue
            seen.add(path)
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as exc:
                results.append(
                    {
                        "file": str(path.relative_to(ROOT)),
                        "could_not_read": type(exc).__name__,
                    }
                )
                continue
            acc = scan_accession_shapes(text)
            sha_r = scan_structure_shapes(text)
            results.append(
                {
                    "file": str(path.relative_to(ROOT)),
                    "accession_unaccounted": acc.unaccounted,
                    "structure_unaccounted": sha_r.unaccounted,
                    "reads_as_cited": _carries_a_citation(text),
                    # Ruling #455: a scan that could not look certifies nothing, and could-not-scan
                    # FAILS rather than passes. Both scanners measured this and the row discarded
                    # it, so the state that must be fatal never reached the verdict.
                    "could_not_scan": acc.could_not_scan or sha_r.could_not_scan,
                }
            )

    unaccounted = [
        r for r in results if r.get("accession_unaccounted") or r.get("structure_unaccounted")
    ]
    cited = [r for r in results if r.get("reads_as_cited")]
    unread = [r for r in results if "could_not_read" in r]
    cited_in_scope_rows = [r for r in cited if r["file"].startswith(CLASSIFIED_ROOTS)]

    # CTO #540 (1b), principal-confirmed. Two instruments own two properties, so there are two
    # dispositions, and which is which is STATED rather than left to the reader.
    #
    # REPORTED, never fatal:
    #   - unaccounted shapes INSIDE the classified roots: the classifier's business under r2.50c;
    #     they land in W/F/C/N and clause (i) governs constructed probes. The scan does not re-judge.
    #   - reads-as-cited INSIDE the classified roots: the citation predicate IS the gate-9 defect,
    #     bound by row 58 and explicitly NOT repaired. A scan failing on it would force a repair the
    #     plan forbids.
    # FATAL:
    #   - unreadable, and could-not-scan (ruling #455: failing to look certifies nothing)
    #   - a shaped token on the AUDIT SURFACE, which no classifier covers
    #   - an empty pattern: a glob matching nothing has stopped measuring whatever it named
    #
    # AMENDED 2026-09-30 (principal, extending CTO #540 (1b)): reads-as-cited OUTSIDE the classified
    # roots is REPORTED, not fatal. The original rationale was "where nothing else reports it"; no
    # classifier covers dispatch records, so a cited dispatch swallows no site and the harm model does
    # not apply, and the scan now names each one by path.
    #
    # The sequence is recorded because it is the sequence that warrants suspicion: the rule was
    # relaxed AFTER it blocked this gate, on evidence surfaced by the author, who had an interest in
    # the gate passing. It is stated here, in limitations, and in the approval trail rather than
    # living only in a diff. The three files it covers are tracked dispatch records, and editing
    # committed audit evidence is the principal's -- which is why the alternative to amending was
    # closing Stage 1, not a quiet fix.
    fatal = {
        "unreadable": len(unread),
        "could_not_scan": len([r for r in results if r.get("could_not_scan")]),
        "shapes_on_audit_surface": len(
            [r for r in unaccounted if r["file"].startswith(AUDIT_SURFACE)]
        ),
        "empty_patterns": 0,  # filled in below, once matched_per_pattern is final
    }
    reported_not_fatal = {
        "shapes_inside_classified_roots": len(
            [r for r in unaccounted if r["file"].startswith(CLASSIFIED_ROOTS)]
        ),
        "cited_inside_classified_roots": len(cited_in_scope_rows),
        # Amended 2026-09-30 from fatal to reported -- see the note above, including why the
        # amendment's timing is recorded rather than smoothed over.
        "cited_outside_classified_roots": len(
            [r for r in cited if not r["file"].startswith(CLASSIFIED_ROOTS)]
        ),
    }

    # Reached vs tracked, per classified root. `git ls-files` is the denominator because it is the
    # same corpus r250-classify.py classifies; comparing against anything else would compare two
    # different populations and then call the difference a result.
    reached = {r["file"] for r in results}
    surface_vs_scope = {}
    for root_prefix in CLASSIFIED_ROOTS:
        tracked = subprocess.run(
            ["git", "-C", str(ROOT), "ls-files", root_prefix],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.split()
        eligible = [f for f in tracked if f.endswith(CLASSIFIED_SUFFIXES)]
        hit = [f for f in eligible if f in reached]
        surface_vs_scope[root_prefix] = {
            "tracked_in_scope": len(tracked),
            # Only the suffixes the scan reads. Counting a .tsv fixture as "not reached" would be a
            # false alarm, and a gate that cries wolf gets ignored exactly like one that stays quiet.
            "eligible_by_suffix": len(eligible),
            "reached_by_scan": len(hit),
            "not_reached": len(eligible) - len(hit),
        }

    record = {
        "measured_at_commit": sha,
        "files_scanned": len(results) - len(unread),
        "files_unreadable": len(unread),
        "files_with_unaccounted_shapes": len(unaccounted),
        "files_that_read_as_cited": len(cited),
        "note": (
            "reads_as_cited is checked because gate 9 showed the predicate can be satisfied by "
            "prose explaining it; a report about that defect tripping it would be the defect one "
            "level up"
        ),
        "matched_per_pattern": matched_per_pattern,
        "empty_patterns": [p for p, n in matched_per_pattern.items() if n == 0],
        "verdict_note": (
            "CTO #540 (1b): shapes and reads-as-cited INSIDE the classified roots are REPORTED "
            "(classifier's business under r2.50c; the citation predicate is bound by row 58, not "
            "repaired). FATAL: unreadable, could-not-scan, shapes on the audit surface, empty "
            "pattern. AMENDED 2026-09-30 (principal): reads-as-cited OUTSIDE the classified roots "
            "is REPORTED, not fatal -- no classifier covers those files, so no site is swallowed. "
            "The amendment followed the rule blocking this gate; that sequence is recorded in "
            "limitations rather than left in a diff."
        ),
        "fatal_counts": fatal,
        "reported_not_fatal_counts": reported_not_fatal,
        "files_that_read_as_cited_in_classified_scope": len(cited_in_scope_rows),
        # The SITES each in-scope cited file accounts into bucket F, so the claim can state the
        # consequence rather than only the count (CTO #540 (1b)).
        #
        # `comparable_to_bucket_F` marks the subset that r250-classify actually places in F --
        # guard-enforced Python/prose. The others (a config, snapshot fixtures) are scoped OUT by
        # property, so their sites are NOT in bucket F. Summing all of them gives 143 against a
        # bucket F of 48, which is two populations, not a disagreement. The comparable subset is the
        # only figure that may be published as an instrument disagreement.
        "cited_in_classified_scope": [
            {
                "file": r["file"],
                "sites_into_F": classify_sites((ROOT / r["file"]).read_text(encoding="utf-8"))["F"],
                "comparable_to_bucket_F": _is_guard_enforced(r["file"]),
            }
            for r in cited_in_scope_rows
        ],
        "cited_in_scope_sites_comparable_to_bucket_F": sum(
            classify_sites((ROOT / r["file"]).read_text(encoding="utf-8"))["F"]
            for r in cited_in_scope_rows
            if _is_guard_enforced(r["file"])
        ),
        # SURFACE vs SCOPE, per root, every run. The absence of this field is what let C-1 live.
        "surface_vs_scope": surface_vs_scope,
        "per_file": results,
    }

    out = Path(__file__).resolve().parent / f"scan-artifacts-{sha}.json"
    if write:
        out.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    print(f"measured at commit {sha}")
    print(f"files scanned                : {record['files_scanned']}")
    print(f"files unreadable             : {record['files_unreadable']}")
    print(f"files with unaccounted shapes: {record['files_with_unaccounted_shapes']}")
    print(
        f"files that READ AS CITED     : {record['files_that_read_as_cited']}"
        f"  (in classified scope, i.e. able to swallow a site: "
        f"{record['files_that_read_as_cited_in_classified_scope']})"
    )
    for r in unaccounted:
        print(
            f"  SHAPES  {r['file']}  acc={r['accession_unaccounted']} str={r['structure_unaccounted']}"
        )
    for r in cited:
        print(f"  CITED   {r['file']}")
    print(f"\nwrote {out.relative_to(ROOT)}" if write else "--no-write: nothing written")

    # A pattern that matches nothing is a COVERAGE failure, not a smaller count -- the docstring
    # claims a glob means "a new one cannot be silently omitted", and an empty glob is exactly how
    # that claim would quietly stop being true.
    empty = [p for p, n in matched_per_pattern.items() if n == 0]
    for p in empty:
        print(f"  EMPTY PATTERN  {p}")

    # The script must be able to FAIL. It previously returned 0 unconditionally, so a file that
    # read as cited, or one that could not be read, was printed and then certified clean anyway.
    # READS-AS-CITED FAILS ONLY WHERE IT CAN DO HARM, and the boundary is not a judgement call:
    # r250-classify.py classifies `projects/lung-on-chipsim` and `workstreams/lung-on-chipsim`
    # ONLY (its ls-files call). A file reading as cited INSIDE that set has all its sites swallowed
    # into bucket F -- the defect gate 9 found, where a predicate was satisfied by the prose
    # explaining it. A file OUTSIDE that set is never classified at all, so the predicate firing
    # there changes no bucket and removes no site from scrutiny.
    #
    # Failing on it anyway would be a claim wider than its own rationale -- the family, in the
    # verdict of the instrument written against the family. Every cited file is still REPORTED,
    # in or out of scope; only the VERDICT is scoped.
    fatal["empty_patterns"] = len(empty)
    bad = sum(fatal.values())

    print("\nREPORTED, not fatal (classifier's business / bound by row 58):")
    for k, v in reported_not_fatal.items():
        print(f"  {k:34} {v}")
    print("FATAL conditions:")
    for k, v in fatal.items():
        print(f"  {k:34} {v}")
    print(f"\nVERDICT: {'FAIL' if bad else 'PASS'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
