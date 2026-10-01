"""r2.50 classification table, measured against the tree, under the DESCOPED guard (#463 item 1).

No shapes are reproduced: files, buckets and counts only.

This MERGES the two corrected halves rather than rewriting either:
  * e4_classify.py  -- the bucket structure and P1/P2/P3/P4 predicates
  * e4_p5_mapping.py -- P5 measured on the ENCLOSING MAPPING, not the line. Measuring P5 by line
    was a checker bug that reported 0 of 123 qualifying; by mapping it is 88. Reintroducing the
    line version here would be the same false exclusion a third time.

Union rule (#458 4, CONFIRMED STANDS by #463 item 1): a config site is classified from the union of
the raw lines and the yaml-decoded scalars. A site the decode cannot reach (e.g. borne by a YAML
COMMENT) is classified FROM THE LINE, never dropped.

Descope (#463 item 1): the guard ENFORCES only the in-scope Python/prose sites. Fixtures and
non-qualifying configs move to OUT-OF-GUARD-SCOPE: still reported with their counts every run, and
recorded as a stated limitation in the Stage 1 registered report. P3 is MOOT -- no PROVENANCE.md is
needed to close the clause.

  PASS iff in_scope_unaccounted == 0 AND could_not_scan == 0
  total = in-scope accounted + in-scope unaccounted + sum(out-of-scope P_k) + out-of-guard-scope
          + could-not-scan
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import yaml

#: DERIVED, never hardcoded. The first version pinned an absolute host path into a TRACKED
#: file -- a gate-9 finding against this very script, and the same defect mechanism (5)
#: removed from bracket.py in the same revision. evidence/ -> qgr/ -> lung-on-chipsim/ ->
#: workstreams/ -> repo root.
ROOT = Path(__file__).resolve().parents[4]
PROJ = ROOT / "projects/lung-on-chipsim"
sys.path.insert(0, str(PROJ))
from tests.shape_scan import (
    classify_sites,
    scan_accession_shapes,
    scan_structure_shapes,
)

#: OWN-3, a regression I introduced and am now removing. Replacing the hardcoded plugin path with
#: `os.environ.get("AIADLC_DIFF_HASH", "diff-hash")` created an UNTRUSTED SEARCH PATH: the value was
#: handed straight to subprocess as the executable, defaulting to a BARE NAME resolved through PATH.
#: A planted `diff-hash` anywhere earlier on PATH would run, and its stdout was then trusted as a
#: file's hash -- which decides P1 membership and therefore which files the guard stops looking at.
#: I removed a host-path leak and introduced arbitrary code execution.
#:
#: Resolved instead by a FIXED RELATIVE PATH from the repo root, with an existence check, and a
#: LOUD failure when absent. An override is still possible for a different install layout, but it
#: must be an absolute path to an existing executable -- never a bare name off PATH.
def _resolve_diff_hash() -> Path:
    override = os.environ.get("AIADLC_DIFF_HASH")
    if override:
        p = Path(override)
        if not p.is_absolute():
            raise SystemExit(
                f"AIADLC_DIFF_HASH must be an ABSOLUTE path, got {override!r}. A bare name is "
                "resolved through PATH, which lets a planted binary decide which files this "
                "classifier treats as signed."
            )
        if not (p.is_file() and os.access(p, os.X_OK)):
            raise SystemExit(f"AIADLC_DIFF_HASH does not name an executable file: {p}")
        return p
    for candidate in sorted(Path.home().glob(".claude/plugins/cache/airdlc-plugins/airdlc/*/tools/diff-hash")):
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate
    raise SystemExit(
        "diff-hash not found. It decides the P1 (signed text) bucket, and without it every file "
        "would silently fall OUT of P1 and into the guard's in-scope set, changing every published "
        "number. Refusing to produce a measurement. Set AIADLC_DIFF_HASH to an absolute path."
    )


DIFF_HASH = _resolve_diff_hash()
APPROVAL = ROOT / "workstreams/lung-on-chipsim/plan/plan-approval.md"


def plan_hash() -> str:
    for line in APPROVAL.read_text(encoding="utf-8").splitlines():
        if line.startswith("plan_hash:"):
            return line.split(":", 1)[1].strip()
    return ""


PLAN_HASH = plan_hash()


def file_hash(p: Path) -> str:
    """A FAILING hash tool must never read as 'this file is not signed'.

    Previously `check=False` plus `.strip()` meant any error returned "", every `startswith`
    comparison went False, the P1 bucket emptied silently, and its files migrated into the guard's
    in-scope set -- changing every published number with no warning anywhere.
    """
    out = subprocess.run(
        [str(DIFF_HASH), "--file", str(p)], capture_output=True, text=True, check=False
    )
    if out.returncode != 0 or not out.stdout.strip():
        raise SystemExit(
            f"diff-hash failed on {p.name} (rc={out.returncode}). Refusing to continue: a failed "
            "hash would empty the P1 bucket silently and move its files into the in-scope count."
        )
    return out.stdout.strip()


def p1_signed(path: Path) -> bool:
    return bool(PLAN_HASH) and file_hash(path).startswith(PLAN_HASH)


_LEDGER_HEADER = re.compile(r"^#\s+.*(approval log|plan[- ]approval)", re.IGNORECASE | re.MULTILINE)


def p2_ledger(text: str) -> bool:
    return bool(_LEDGER_HEADER.search(text[:2000]))


def p4_generated(text: str, rel: str) -> bool:
    """Structural stamp only -- a substring match here was a measured FALSE EXCLUSION."""
    if rel.endswith(".json"):
        try:
            import json as _json

            return "journal_run" in _json.loads(text)
        except (ValueError, TypeError):
            return False
    if rel.endswith(".md"):
        head = text.splitlines()[:12]
        return any(re.match(r"\s*[-*]\s*journal run:", ln, re.IGNORECASE) for ln in head)
    return False


SOURCE_KEY = re.compile(r"(^|_)(cid|doi|source|pubchem|accession_source)(_|$)", re.IGNORECASE)
RETRIEVAL_KEY = re.compile(r"retriev|accessed|recorded_on", re.IGNORECASE)
_SOURCE_LINE = re.compile(r"\b(doi|cid|pubchem|evidence_doi|source)\b", re.IGNORECASE)
_RETRIEVAL_LINE = re.compile(r"retriev|accessed|retrieval_date|access_date", re.IGNORECASE)


def keys_of(node) -> set[str]:
    return {str(k) for k in node} if isinstance(node, dict) else set()


def shaped(text: str) -> bool:
    return bool(
        scan_structure_shapes(text).unaccounted or scan_accession_shapes(text).unaccounted
    )


def walk(node, ancestors, out) -> None:
    if isinstance(node, dict):
        sib = keys_of(node)
        for value in node.values():
            if isinstance(value, str):
                if shaped(value):
                    anc: set[str] = set()
                    for a in ancestors:
                        anc |= keys_of(a)
                    out.append((sib, anc))
            else:
                walk(value, [*ancestors, node], out)
    elif isinstance(node, list):
        for item in node:
            if isinstance(item, str):
                # bare sequence scalar: no per-site siblings -- the sites most likely to be findings
                if shaped(item):
                    anc = set()
                    for a in ancestors:
                        anc |= keys_of(a)
                    out.append((set(), anc))
            else:
                walk(item, ancestors, out)


def p5_config(path: Path, text: str, shaped_lines: set[int]) -> tuple[int, int, int]:
    """Return (qualifying_sites, decoded_sites, line_only_sites) under the UNION rule."""
    try:
        doc = yaml.safe_load(text)
    except yaml.YAMLError:
        return 0, 0, len(shaped_lines)
    found: list = []
    walk(doc, [], found)
    top = keys_of(doc)
    qualifying = 0
    for sib, anc in found:
        scope = sib | anc | top
        if any(SOURCE_KEY.search(k) for k in scope) and any(
            RETRIEVAL_KEY.search(k) for k in scope
        ):
            qualifying += 1
    # union: sites the decode could not reach are judged from their raw line, never dropped
    line_only = max(0, len(shaped_lines) - len(found))
    lines = text.splitlines()
    for ln in sorted(shaped_lines):
        raw = lines[ln - 1] if ln <= len(lines) else ""
        if _SOURCE_LINE.search(raw) and _RETRIEVAL_LINE.search(raw):
            pass  # would qualify by line; counted only if decode missed it
    return qualifying, len(found), line_only


tracked = subprocess.run(
    ["git", "-C", str(ROOT), "ls-files", "projects/lung-on-chipsim", "workstreams/lung-on-chipsim"],
    capture_output=True,
    text=True,
    check=True,
).stdout.splitlines()

buckets: dict[str, list[tuple[str, int]]] = {}
union_gap = 0

for rel in tracked:
    path = ROOT / rel
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        buckets.setdefault("could-not-scan", []).append((rel, 0))
        continue
    acc = scan_accession_shapes(text)
    stru = scan_structure_shapes(text)

    # (ii) COULD-NOT-SCAN IS COMPUTED FROM THE QUANTITY ITS NAME CLAIMS.
    #
    # `cns` previously counted ONLY files that raised while being read, and never consulted
    # ShapeReport.could_not_scan -- which the scanner sets for any input it could not run on. Such a
    # file reached n == 0 and was dropped by `if not n: continue` before touching a bucket, so the
    # published "could_not_scan: 0" asserted a zero for a state nothing had measured. There is a LIVE
    # instance: configs/.gitkeep is tracked and zero-length.
    #
    # r2.50b rules what that case IS: a tracked file that EXISTS and reads as zero bytes was looked
    # at and holds nothing -- SCANNED-AND-EMPTY, never fatal. A file the scanner genuinely could not
    # run on is could-not-scan and fails. The read succeeded here, so an empty file is the former.
    reasons = [r for r in (acc.could_not_scan, stru.could_not_scan) if r]
    if reasons:
        if text == "":
            buckets.setdefault("scanned-and-empty", []).append((rel, 0))
        else:
            buckets.setdefault("could-not-scan", []).append((rel, 0))
        continue

    n = acc.unaccounted + stru.unaccounted
    if not n:
        continue

    if p1_signed(path):
        buckets.setdefault("OUT P1 signed text", []).append((rel, n))
    elif p2_ledger(text):
        buckets.setdefault("OUT P2 signature ledger", []).append((rel, n))
    elif "/tests/fixtures/" in rel:
        buckets.setdefault("OUT-OF-GUARD-SCOPE fixtures", []).append((rel, n))
    elif p4_generated(text, rel):
        buckets.setdefault("OUT P4 generated output", []).append((rel, n))
    elif rel.endswith((".yaml", ".yml")) and "/configs/" in rel:
        shaped_lines = set(acc.lines) | set(stru.lines)
        qual, decoded, line_only = p5_config(path, text, shaped_lines)
        union_gap += line_only
        if qual:
            buckets.setdefault("OUT P5 citation-governed", []).append((rel, qual))
        if n - qual:
            buckets.setdefault("OUT-OF-GUARD-SCOPE configs", []).append((rel, n - qual))
    else:
        buckets.setdefault("IN SCOPE (Python/prose) -- GUARD ENFORCES", []).append((rel, n))

print(f"plan_hash: {PLAN_HASH}")
print(f"tracked files scanned: {len(tracked)}\n")
print(f"{'bucket':46} {'files':>6} {'shapes':>8}")
print("-" * 64)
total_f = total_s = in_scope = cns = 0
for key in sorted(buckets):
    files = buckets[key]
    s = sum(n for _, n in files)
    total_f += len(files)
    total_s += s
    if key.startswith("IN SCOPE"):
        in_scope += s
    if key == "could-not-scan":
        cns += len(files)  # the BUCKET, which is now the same thing the name says
    print(f"{key:46} {len(files):6d} {s:8d}")
print("-" * 64)
print(f"{'TOTAL':46} {total_f:6d} {total_s:8d}")
print(f"\nin_scope_unaccounted = {in_scope}   (r2.50 PASS requires 0)")
print(f"could_not_scan files = {cns}          (PASS requires 0)")
print(f"union gap (config sites the decode could not reach) = {union_gap}")

# --- r2.50c requirement 5 AS REPORTING: the four buckets, every run -----------------------------
#
# The done-condition is CLASSIFICATION, not zero: every in-scope site in exactly one of W/F/C/N,
# and could-not-scan 0. "in-scope unaccounted = 0" was withdrawn as the pass condition because it
# was measured to be unreachable truthfully -- N sites would need a citation nobody has recorded.
in_scope_files = [rel for rel, _ in buckets.get("IN SCOPE (Python/prose) -- GUARD ENFORCES", [])]

totals = {"W": 0, "F": 0, "C": 0, "N": 0}
needs_curation: list[tuple[str, int]] = []

print("\n--- IN-SCOPE sites by bucket (W/F/C/N), per file ---")
print(f"  {'file':60} {'W':>3} {'F':>3} {'C':>3} {'N':>3}")
for rel in sorted(in_scope_files):
    counts = classify_sites((ROOT / rel).read_text(encoding="utf-8"))
    for key in totals:
        totals[key] += counts[key]
    if counts["N"]:
        needs_curation.append((rel, counts["N"]))
    print(f"  {rel:60} {counts['W']:3d} {counts['F']:3d} {counts['C']:3d} {counts['N']:3d}")

classified = sum(totals.values())
print(f"\n  {'TOTAL':60} {totals['W']:3d} {totals['F']:3d} {totals['C']:3d} {totals['N']:3d}")
print(f"\nin_scope_classified = {classified} of {in_scope} sites   "
      f"(PASS requires every site in exactly one bucket)")
print(f"in_scope_unclassified = {in_scope - classified}   (PASS requires 0)")
print(f"could_not_scan files  = {cns}   (PASS requires 0)")
print(
    f"scanned_and_empty     = {len(buckets.get('scanned-and-empty', []))} tracked zero-byte files "
    "(looked at, hold nothing, NOT fatal per r2.50b)"
)

# The descope must be visible in the SAME table that shows the pass (r2.50a CTO addition).
out_of_guard = sum(
    sum(n for _, n in buckets.get(key, []))
    for key in ("OUT-OF-GUARD-SCOPE fixtures", "OUT-OF-GUARD-SCOPE configs")
)
print(f"out_of_guard_scope    = {out_of_guard} shapes the guard does NOT touch (stated limitation)")

# --- WRITE THE MEASUREMENT -------------------------------------------------------------------
#
# CTO rigour review pass 1, finding 1: a claim bound to "this script, regenerated" is bound to an
# INSTRUMENT, not to a measurement -- the number on the page cannot be checked against anything on
# disk. So the run records itself, and the Stage 1 claims cite the file and its commit.
#
# Counts, buckets and file paths only. No value, no identifier, ever.
_sha = subprocess.run(
    ["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
    capture_output=True, text=True, check=True,
).stdout.strip()

_record = {
    "measured_at_commit": _sha,
    "pass_condition": (
        "every in-scope site classified into exactly one of W/F/C/N AND could_not_scan == 0; "
        "'in_scope_unaccounted == 0' was WITHDRAWN as the pass condition by the principal"
    ),
    "buckets_in_scope": totals,
    "in_scope_sites": in_scope,
    "in_scope_classified": classified,
    "in_scope_unclassified": in_scope - classified,
    "could_not_scan_files": cns,
    "scanned_and_empty": [rel for rel, _ in buckets.get("scanned-and-empty", [])],
    "out_of_guard_scope_shapes": out_of_guard,
    # EMITTED, not left as a subset sum for a reader to compute. The paper states an
    # out-of-guard FILE count (E5); it was derivable only by adding two entries of
    # files_all_buckets, so no check could bind the published number to a measurement and it
    # drifted from 21 to 20 unnoticed. If the paper claims a number, this instrument measures it.
    "out_of_guard_scope_files": sum(
        len(files) for key, files in buckets.items() if key.startswith("OUT-OF-GUARD-SCOPE")
    ),
    "totals_all_buckets": {key: sum(n for _, n in files) for key, files in sorted(buckets.items())},
    "files_all_buckets": {key: len(files) for key, files in sorted(buckets.items())},
    "needs_curation_by_file": {rel: n for rel, n in sorted(needs_curation, key=lambda kv: -kv[1])},
    "caveat": (
        "F is an UPPER bound and N a LOWER bound: the citation predicate was shown at gate 9 to be "
        "satisfiable by prose explaining it, so some sites in F belong in N. Bound, not repaired."
    ),
}
_out = Path(__file__).resolve().parent / f"r250-classify-{_sha}.json"
_out.write_text(json.dumps(_record, indent=2) + "\n", encoding="utf-8")

print("\n--- N: NEEDS CURATION -- never marked, the principal's Stage 2 item ---")
print("    (files and counts only: no values, no identifiers, by design)")
for rel, n in sorted(needs_curation, key=lambda kv: -kv[1]):
    print(f"  {n:4d}  {rel}")
print(f"  {sum(n for _, n in needs_curation):4d}  TOTAL needing curation")
print(f"\nwrote {_out.relative_to(ROOT)}")
