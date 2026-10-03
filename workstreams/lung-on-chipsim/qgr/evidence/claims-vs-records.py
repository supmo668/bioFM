#!/usr/bin/env python3
"""Bind the paper's TYPED numbers to the evidence records they cite.

Why this exists
---------------
`traceability-check.py` binds claims to DRAFTS: every claim is cited somewhere, no CUT claim is used
as support. It never compares a claim's numbers to the measurement the claim cites. So the standing
rule *"counts are regenerated, never typed"* was enforced for nothing in the paper, and two stale
numbers (471 shapes / 21 files, superseded by 445 / 20) sat in all four documents while the record
measuring the correct values sat uncited in the same directory.

The invariant this does NOT try to enforce
------------------------------------------
"the cited record measured the commit being gated" is **unsatisfiable**: committing a record changes
the tree, so no record can have measured the commit that contains it. A check that can never pass is
worse than no check, because it gets disabled. Instead this enforces *materially current*:

  1. NEWEST      — the cited record is the newest present for its instrument. A strictly newer
                   record existing and uncited is a FAILURE (that was the live defect).
  2. AGREEMENT   — every number in the citing claim's text matches SOME value of the cited record
                   (including nested values and each dict's length/sum, since "62 sites in 14 files"
                   is a sum and a length). This is deliberately a WEAK arm: it catches a number that
                   matches NOTHING in the record, not a number that matches the WRONG field. A stale
                   count that happens to equal some other value in the same record passes it. The
                   strong guarantee comes from arm 1 plus regenerating the record; arm 2 is the net
                   under it, and is documented as such rather than oversold.
  3. COVERAGE    — every scalar field of the cited record is asserted by some claim, or is listed in
                   NOT_ASSERTED with a reason. Without this arm the check silently ignores a field
                   nobody claims, which is false exclusion: a number drifts and no claim covers it.
  4. CUT SET     — the claims-list summary's counts AND its explicit CUT id list match the table.

Arms 2 and 3 are deliberately mutual: 2 catches a claim whose number no record supports, 3 catches a
record field no claim asserts. Either alone leaves a hole.

Run from the repo root. `--no-write` is the default; there is no write mode.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PAPER = ROOT / "workstreams/lung-on-chipsim/paper"
EVIDENCE = ROOT / "workstreams/lung-on-chipsim/qgr/evidence"

DOCS = ["stage1-claims-list.md", "stage1-methods.md", "stage1-limitations.md", "stage1-short-form.md"]

#: instrument prefix -> the record family it writes
INSTRUMENTS = ["scan-artifacts", "r250-classify"]

#: record field -> why no claim asserts it. A field absent from BOTH a claim and this map FAILS,
#: so adding a field to a record forces a decision here rather than silently going unchecked.
NOT_ASSERTED: dict[str, str] = {
    "in_scope_unclassified": "asserted as the complement of in_scope_classified, not as its own number",
    "could_not_scan_files": "asserted in prose as 'could-not-scan 0' inside the bucket line",
    "files_unreadable": "asserted in prose as '0 unreadable' inside the H4 sentence",
}

CITATION_RE = re.compile(r"(" + "|".join(INSTRUMENTS) + r")-([0-9a-f]{7,40})\.json")
NUM_RE = re.compile(r"\b\d{1,7}\b")


def records_present() -> dict[str, list[Path]]:
    """instrument -> records on disk, oldest-first by mtime (ties broken by name for determinism)."""
    out: dict[str, list[Path]] = {}
    for inst in INSTRUMENTS:
        paths = sorted(EVIDENCE.glob(f"{inst}-*.json"), key=lambda p: (p.stat().st_mtime, p.name))
        out[inst] = paths
    return out


def scalars(rec: dict) -> dict[str, int]:
    """Top-level int fields -- what ARM 3 demands a claim assert."""
    return {k: v for k, v in rec.items() if isinstance(v, int) and not isinstance(v, bool)}


def citable_values(node, out: set[int] | None = None) -> set[int]:
    """Every value a claim may legitimately state from this record.

    Includes nested ints (bucket counts live in sub-dicts), and for every dict its LENGTH and the SUM
    of its int values -- because "62 sites in 14 files" is the sum and the length of
    `needs_curation_by_file`, and a check that knew only top-level scalars would call both of those
    stale. Being generous here is deliberate: ARM 2 exists to catch a number matching NOTHING, and a
    false FAIL on a correct aggregate would get the arm switched off.
    """
    if out is None:
        out = set()
    if isinstance(node, bool):
        return out
    if isinstance(node, int):
        out.add(node)
    elif isinstance(node, dict):
        ints = [v for v in node.values() if isinstance(v, int) and not isinstance(v, bool)]
        out.add(len(node))
        if ints:
            out.add(sum(ints))
        for v in node.values():
            citable_values(v, out)
    elif isinstance(node, list):
        out.add(len(node))
        for v in node:
            citable_values(v, out)
    return out


def citing_units(text: str) -> list[tuple[int, str, str]]:
    """(line number, cited record filename, the text unit that cites it).

    The unit is the table ROW for a table citation, else the PARAGRAPH, because a claim's numbers and
    its citation must be read together. Splitting on lines would cut a wrapped sentence in half and
    make a real number look absent — a false pass.
    """
    units: list[tuple[int, str, str]] = []
    lines = text.splitlines()
    # paragraph index so a non-table citation gets its whole paragraph
    para_of: dict[int, tuple[int, str]] = {}
    start = 0
    buf: list[str] = []
    for i, line in enumerate(lines):
        if line.strip() == "":
            if buf:
                for j in range(start, i):
                    para_of[j] = (start + 1, "\n".join(buf))
            buf, start = [], i + 1
        else:
            buf.append(line)
    if buf:
        for j in range(start, len(lines)):
            para_of[j] = (start + 1, "\n".join(buf))

    for i, line in enumerate(lines):
        for m in CITATION_RE.finditer(line):
            name = m.group(0)
            if line.lstrip().startswith("|"):
                units.append((i + 1, name, line))
            else:
                ln, para = para_of.get(i, (i + 1, line))
                units.append((ln, name, para))
    return units


def check_claims_summary(failures: list[str]) -> None:
    """Arm 4: the summary line's counts and CUT id set must match the table it summarises."""
    p = PAPER / "stage1-claims-list.md"
    text = p.read_text(encoding="utf-8")
    rows = [l for l in text.splitlines() if re.match(r"^\|\s*[A-H]\d+\s*\|", l)]
    cut: list[str] = []
    for line in rows:
        cols = [c.strip() for c in line.strip("|").split("|")]
        status = cols[-1].upper()
        if "NOT MEASURED" in status or status.startswith("CUT"):
            cut.append(cols[0])
    measured = {"rows": len(rows), "cut": len(cut), "supported": len(rows) - len(cut)}

    m = re.search(
        r"\*\*(\d+) claim rows: (\d+) SUPPORTED, (\d+) NOT MEASURED / CUT\*\* \(([^)]*)\)", text
    )
    if not m:
        failures.append(
            "stage1-claims-list.md: the claim-count summary line is absent or its wording changed, "
            "so arm 4 asserted NOTHING. Restore it or update this check -- a summary that cannot be "
            "found must FAIL, never silently pass."
        )
        return
    stated = {"rows": int(m.group(1)), "supported": int(m.group(2)), "cut": int(m.group(3))}
    stated_ids = sorted(x.strip() for x in m.group(4).split(",") if x.strip())

    for key in ("rows", "supported", "cut"):
        if stated[key] != measured[key]:
            failures.append(
                f"stage1-claims-list.md: summary says {key}={stated[key]}, table measures "
                f"{measured[key]}"
            )
    if stated_ids != sorted(cut):
        failures.append(
            f"stage1-claims-list.md: summary names CUT {stated_ids}, table measures {sorted(cut)}"
        )
    if stated["rows"] != stated["supported"] + stated["cut"]:
        failures.append(
            f"stage1-claims-list.md: summary is not self-consistent: "
            f"{stated['rows']} != {stated['supported']} + {stated['cut']}"
        )


def main() -> int:
    failures: list[str] = []
    present = records_present()
    for inst, paths in present.items():
        if not paths:
            failures.append(f"no {inst}-*.json record present; every claim citing one is unsupported")

    cited_names: set[str] = set()
    asserted_fields: dict[str, set[str]] = {}

    for doc in DOCS:
        p = PAPER / doc
        if not p.exists():
            failures.append(f"{doc}: missing")
            continue
        text = p.read_text(encoding="utf-8")
        for lineno, name, unit in citing_units(text):
            cited_names.add(name)
            rec_path = EVIDENCE / name
            if not rec_path.exists():
                failures.append(f"{doc}:{lineno}: cites {name}, which does not exist")
                continue
            inst = CITATION_RE.match(name).group(1)

            # ARM 1 -- newest record for this instrument
            newest = present[inst][-1].name if present[inst] else None
            if newest and name != newest:
                failures.append(
                    f"{doc}:{lineno}: cites SUPERSEDED {name}; {newest} is newer and present. "
                    f"A superseded citation is how a stale number survives a passing gate."
                )

            rec = json.loads(rec_path.read_text(encoding="utf-8"))
            fields = scalars(rec)
            values = citable_values(rec)

            # ARM 2 -- every number in the citing unit matches some value of the record.
            # Strip what is NOT a measurement, by category, each for a stated reason:
            probe = unit
            probe = re.sub(r"`[^`]*`", " ", probe)          # backticked: paths, and by convention
            #                                                any deliberately-quoted SUPERSEDED number
            probe = re.sub(r"#\d+", " ", probe)             # ruling / dispatch references
            probe = re.sub(r"\u00a7+\s*\d+(\.\d+)?", " ", probe)  # section references
            probe = re.sub(r"\b20\d{2}-\d{2}-\d{2}\b", " ", probe)  # dates
            probe = re.sub(r"\b20\d{2}\b", " ", probe)      # bare years
            probe = re.sub(r"\b[A-H]\d+\b", " ", probe)     # claim ids (A4, G5)
            probe = re.sub(r"\bD-\d+\b", " ", probe)        # deferral ids
            probe = re.sub(r"\br2\.\d+[a-z]?\b", " ", probe)  # revision ids
            probe = re.sub(r"\bgates?[-\s]+\d+\b", " ", probe, flags=re.I)  # gate numbers, "gate 9" or "gate-9"
            # "1,031" must become one number. Without this the thousands comma splits it and the
            # fragment "031" is read as 31 -- a fabricated number that matches nothing, i.e. a
            # FALSE FAIL invented by the checker's own tokenizer.
            probe = re.sub(r"(?<=\d),(?=\d{3}\b)", "", probe)
            nums = {int(n) for n in NUM_RE.findall(probe)}
            unmatched = sorted(n for n in nums if n not in values)
            if unmatched:
                failures.append(
                    f"{doc}:{lineno}: cites {name} but states number(s) {unmatched} matching NO "
                    f"field of that record (fields: {sorted(values)})"
                )

            # ARM 3 bookkeeping -- which fields some claim asserts
            hit = asserted_fields.setdefault(name, set())
            for k, v in fields.items():
                if v in nums:
                    hit.add(k)
            del fields

    # ARM 3 -- every scalar field of every cited record is asserted somewhere, or excused by name
    for name in sorted(cited_names):
        rec_path = EVIDENCE / name
        if not rec_path.exists():
            continue
        fields = scalars(json.loads(rec_path.read_text(encoding="utf-8")))
        hit = asserted_fields.get(name, set())
        for k in sorted(fields):
            if k not in hit and k not in NOT_ASSERTED:
                failures.append(
                    f"{name}: field '{k}' ({fields[k]}) is asserted by no claim and is not listed in "
                    f"NOT_ASSERTED. An unasserted field drifts silently -- decide explicitly."
                )

    check_claims_summary(failures)

    print(f"records present        : " + ", ".join(f"{k}={len(v)}" for k, v in present.items()))
    print(f"records cited          : {len(cited_names)}")
    for name in sorted(cited_names):
        print(f"  {name}")
    print(f"\nfailures: {len(failures)}")
    for f in failures:
        print(f"  FAIL {f}")
    print("\nVERDICT: " + ("PASS" if not failures else "FAIL"))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
