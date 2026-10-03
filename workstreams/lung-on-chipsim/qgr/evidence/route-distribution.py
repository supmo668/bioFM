"""Measure the approval log's route distribution under a STATED normalisation rule, and WRITE it.

Why this exists (CTO rigour review pass 1, finding 2): the Stage 1 claims list reported "49 of 59
standing-delegation" and "4 principal-directed" in one sentence. The first used SUBSTRING matching,
the second used EXACT matching, and neither rule was stated. That is the recurring family --
a claim whose check is unstated and, here, not even self-consistent -- inside the sentence that
reports the family. The fix is not better prose: it is a stated rule, an auditable per-row mapping,
and a committed artifact the claim can cite.

THE RULE, stated once and applied mechanically:

  A row's route field is matched against the CATEGORY PATTERNS below IN ORDER, and the FIRST match
  wins. Order matters and is therefore part of the rule, not an implementation detail: a row reading
  "principal (AskUserQuestion ... verbatim option: ...) applied by the CTO" is PRINCIPAL-VERBATIM
  rather than standing-delegation, because the strongest evidence in the field decides the category.

  Every row is emitted with its raw field beside its assigned category, so the mapping is auditable
  rather than asserted. A row matching nothing is UNCLASSIFIED and is reported as such -- the count
  of unclassified rows is itself a datum, and a silent fallback would be the false-exclusion shape
  this project has hit repeatedly.

No value, identifier or name is read or written by this script: it reads one column of one file.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

#: evidence/ -> qgr/ -> lung-on-chipsim/ -> workstreams/ -> repo root. Derived, never hardcoded:
#: a hardcoded absolute path in a TRACKED file was a gate-9 finding against this very directory.
ROOT = Path(__file__).resolve().parents[4]
LOG = ROOT / "workstreams/lung-on-chipsim/plan/plan-approval-log.md"
EVIDENCE = Path(__file__).resolve().parent

#: Ordered. First match wins. The order IS part of the stated rule.
CATEGORY_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("inferred", re.compile(r"\binferred\b", re.IGNORECASE)),
    ("principal-verbatim", re.compile(r"verbatim option|verbatim:", re.IGNORECASE)),
    ("principal-askuserquestion", re.compile(r"askuserquestion", re.IGNORECASE)),
    ("standing-ruling-applied", re.compile(r"standing ruling applied", re.IGNORECASE)),
    ("principal-via-grill", re.compile(r"principal \(via /grill-me\)", re.IGNORECASE)),
    # NOTE: the first version required "cto " immediately followed by the word, and so MISSED
    # "CTO (route correction, principal-confirmed)". The UNCLASSIFIED bucket surfaced it instead of
    # a silent fallback absorbing it -- which is the whole reason the bucket exists.
    ("cto-correction", re.compile(r"cto[^)]*\b(correction|clarification)\b", re.IGNORECASE)),
    ("log-convention", re.compile(r"log convention", re.IGNORECASE)),
    ("human-direct", re.compile(r"human-direct", re.IGNORECASE)),
    ("principal-directed", re.compile(r"principal-directed", re.IGNORECASE)),
    ("standing-delegation", re.compile(r"standing-delegation", re.IGNORECASE)),
]


def categorise(raw: str) -> str:
    for name, pattern in CATEGORY_PATTERNS:
        if pattern.search(raw):
            return name
    return "UNCLASSIFIED"


def _is_structural(line: str) -> bool:
    """True for the table header row and the |---| separator -- structure, not data."""
    stripped = line.strip()
    if re.fullmatch(r'\|[\s:|-]+\|', stripped):
        return True
    cells = [c.strip().lower() for c in stripped.split('|')]
    return 'rev' in cells and 'route' in cells


def rows() -> tuple[list[tuple[str, str]], list[tuple[str, str]], list[str]]:
    """(numbered, non_numbered, rejected) -- rejected table lines are RETURNED, never dropped."""
    numbered: list[tuple[str, str]] = []
    non_numbered: list[tuple[str, str]] = []
    rejected: list[str] = []
    for line in LOG.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cols = [c.strip() for c in line.split("|")]
        if len(cols) < 5:
            continue
        # (iii) READ BOLDED LABELS, AND COUNT WHAT IS REJECTED.
        #
        # `re.fullmatch(r"\d+", label)` missed a row whose label is **bolded** -- already this
        # file's house style elsewhere. reviewer-test proved the consequence: appending a row
        # labelled `| **60** | ... | inferred | ...` produced BYTE-IDENTICAL output -- still 59
        # revisions, still 0 UNCLASSIFIED, still no `inferred` category. A row marked `inferred`
        # was invisible to the very instrument claim F6 cites to say none exists.
        #
        # Emphasis is stripped from the LABEL before matching, and every rejected table line is
        # recorded. The UNCLASSIFIED bucket only ever saw rows that survived extraction, so it
        # could not have caught this; a silent drop at ADMISSION needed its own count.
        label = re.sub(r"[*`_]", "", cols[1]).strip()
        if re.fullmatch(r"\d+", label):
            numbered.append((label, cols[4].replace("**", "").strip()))
        elif re.match(r"\d{4}-\d{2}-\d{2}", label):
            non_numbered.append((label, cols[2].replace("**", "").strip()))
        elif _is_structural(line):
            # the table header and its |---| separator are not data rows; skipping them is
            # correct, and saying so here keeps the rejected list meaning "a DATA row we failed
            # to admit" rather than "anything we did not parse".
            continue
        else:
            rejected.append(line.strip()[:120])
    return numbered, non_numbered, rejected


def head_sha() -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()


def main() -> int:
    numbered, non_numbered, rejected = rows()
    sha = head_sha()

    tally: dict[str, int] = {}
    mapping: list[dict[str, str]] = []
    for label, raw in numbered:
        cat = categorise(raw)
        tally[cat] = tally.get(cat, 0) + 1
        mapping.append({"row": label, "kind": "numbered", "category": cat, "raw": raw})

    non_tally: dict[str, int] = {}
    for label, raw in non_numbered:
        cat = categorise(raw)
        non_tally[cat] = non_tally.get(cat, 0) + 1
        mapping.append({"row": label, "kind": "non-numbered", "category": cat, "raw": raw})

    unclassified = tally.get("UNCLASSIFIED", 0) + non_tally.get("UNCLASSIFIED", 0)

    record = {
        "measured_at_commit": sha,
        "rule": (
            "route field matched against ordered CATEGORY_PATTERNS, FIRST MATCH WINS; "
            "order is part of the rule; unmatched rows are reported as UNCLASSIFIED"
        ),
        "numbered_revisions": len(numbered),
        "non_numbered_rows": len(non_numbered),
        "total_data_rows": len(numbered) + len(non_numbered),
        "numbered_by_category": dict(sorted(tally.items(), key=lambda kv: -kv[1])),
        "non_numbered_by_category": dict(sorted(non_tally.items(), key=lambda kv: -kv[1])),
        "unclassified_rows": unclassified,
        "rows_not_extracted": len(rejected),
        "mapping": mapping,
    }

    if rejected:
        for line in rejected:
            print(f"  REJECTED ROW  {line}")
        raise SystemExit(
            f"{len(rejected)} table row(s) were not extracted -- refusing to write a record that "
            "silently omits them (the write now happens only after this check, not before)."
        )
    out = EVIDENCE / f"route-distribution-{sha}.json"
    write = "--no-write" not in sys.argv
    if write:
        out.write_text(json.dumps(record, indent=2, sort_keys=False) + "\n", encoding="utf-8")

    print(f"measured at commit {sha}")
    print(f"numbered revisions : {len(numbered)}")
    print(f"non-numbered rows  : {len(non_numbered)}")
    print(f"total data rows    : {len(numbered) + len(non_numbered)}")
    print("\nNUMBERED, by category (first-match-wins over the ordered rule):")
    for cat, n in sorted(tally.items(), key=lambda kv: -kv[1]):
        print(f"  {n:3d}  {cat}")
    print("\nNON-NUMBERED, by category:")
    for cat, n in sorted(non_tally.items(), key=lambda kv: -kv[1]):
        print(f"  {n:3d}  {cat}")
    print(f"\nUNCLASSIFIED rows: {unclassified}  (a silent fallback would hide exactly this)")
    print(f"\nwrote {out.relative_to(ROOT)}" if write else "--no-write: nothing written")

    # THE REAL IDENTITY. The two asserts that used to live here were TAUTOLOGIES: `tally` is
    # incremented exactly once per element of `numbered`, so `sum(tally.values()) == len(numbered)`
    # is true for every possible input -- reviewer-test showed a `categorise()` returning a constant
    # passes them, and so does reversing the rule order. They also ran AFTER the record was written.
    #
    # What can actually fail is whether every data row in the file was ADMITTED. That is checked
    # here, before the write, and a rejected row is named.
    if rejected:
        for line in rejected:
            print(f"  REJECTED ROW  {line}")
        raise SystemExit(
            f"{len(rejected)} table row(s) were not extracted. A row the extractor drops is "
            "invisible to every category count, including the `inferred` count F6 cites. Refusing "
            "to write a record that silently omits them."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
