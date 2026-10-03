"""Design spec §6.2: every claim in the draft resolves to an artifact that EXISTS.

A claim whose artifact is missing FAILS the check rather than being footnoted. This runs that gate
mechanically instead of by reading, and writes its result so the check itself is citable.

Four checks:
  1. every claim id cited in a draft exists in the claims list;
  2. every artifact path named in the claims list exists on disk;
  3. no CUT claim is cited as support anywhere in a draft;
  4. the NOT CLAIMED list appears in BOTH granularities (§6.4), item for item.

No value, identifier or name is read or written.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

#: evidence/ -> qgr/ -> lung-on-chipsim/ -> workstreams/ -> repo root. Derived, never hardcoded.
ROOT = Path(__file__).resolve().parents[4]
PAPER = ROOT / "workstreams/lung-on-chipsim/paper"

CLAIMS = PAPER / "stage1-claims-list.md"
DRAFTS = {
    "long": PAPER / "stage1-methods.md",
    "short": PAPER / "stage1-short-form.md",
    "limitations": PAPER / "stage1-limitations.md",
}

CLAIM_ROW = re.compile(r"^\| ([A-H]\d+) \|(.*)$")
CLAIM_REF = re.compile(r"\[([A-H]\d+(?:\s*,\s*[A-H]\d+)*)[^\]]*\]")
BACKTICK_PATH = re.compile(r"`([A-Za-z0-9_./-]+\.(?:py|json|md|yaml))`")


def load_claims() -> tuple[dict[str, str], set[str], dict[str, str]]:
    """(status by id, cut ids, artifact column by id)."""
    status: dict[str, str] = {}
    cut: set[str] = set()
    artifacts: dict[str, str] = {}
    for line in CLAIMS.read_text(encoding="utf-8").splitlines():
        m = CLAIM_ROW.match(line)
        if not m:
            continue
        cid = m.group(1)
        cols = [c.strip() for c in line.split("|")]
        artifacts[cid] = cols[3] if len(cols) > 3 else ""
        st = cols[4] if len(cols) > 4 else ""
        status[cid] = st
        if "NOT MEASURED" in st or st.strip().startswith("CUT"):
            cut.add(cid)
    return status, cut, artifacts


def not_claimed_items(text: str) -> list[tuple[str, str]]:
    """(lead, full body) per item. The FULL body is what §6.4 "item for item" has to mean.

    Comparing only the text before the first period was a check narrower than its own docstring, and
    reviewer-test proved the consequence: rewriting a short-form item so its CONTINUATION asserted
    the OPPOSITE of the long form's ("also fully measured and clean" against "measured by nothing
    here") still reported 9/9 and PASS. A limitation could contradict its own long form and the gate
    signed it.

    The lead is kept, but only to PAIR items across the two granularities; the comparison is then
    over the whole normalised body. Continuation lines are joined, because an item's meaning does
    not stop at its first line break.
    """
    items: list[tuple[str, str]] = []
    inside = False
    current: list[str] | None = None

    def flush() -> None:
        if current:
            body = re.sub(r"\s+", " ", " ".join(current)).strip()
            plain = re.sub(r"[*`]", "", body)
            lead = plain.split(".")[0].strip().lower()
            items.append((lead, plain.strip().lower()))

    for line in text.splitlines():
        if re.match(r"^#+\s*NOT CLAIMED", line, re.IGNORECASE):
            inside = True
            continue
        if inside and line.startswith("#"):
            break
        if not inside:
            continue
        stripped = line.strip()
        if stripped.startswith("- "):
            flush()
            current = [stripped[2:]]
        elif current is not None and stripped and not stripped.startswith(("|", ">")):
            current.append(stripped)  # a continuation line belongs to the item above it
        elif current is not None and not stripped:
            flush()
            current = None
    flush()
    return items


def main() -> int:
    # --no-write: a reviewer re-running this gate in someone else's worktree should leave that tree
    # exactly as they found it. Asked for by the coordinator after pass 2, whose own run wrote a
    # record it then had to delete by hand.
    write = "--no-write" not in sys.argv
    status, cut, artifacts = load_claims()
    failures: list[str] = []
    notes: list[str] = []

    # 1 + 3: claim ids cited in drafts
    cited_total: set[str] = set()
    for name, path in DRAFTS.items():
        if not path.exists():
            failures.append(f"draft missing: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        cited: set[str] = set()
        for m in CLAIM_REF.finditer(text):
            for cid in re.split(r"\s*,\s*", m.group(1)):
                cited.add(cid)
        cited_total |= cited
        for cid in sorted(cited):
            if cid not in status:
                failures.append(f"{name}: cites {cid}, which is not in the claims list")
        # a CUT claim may be NAMED as cut, but must not be cited as support
        for cid in sorted(cited & cut):
            for line in text.splitlines():
                # CASE-INSENSITIVE, and this mattered: the first run flagged the short form for
                # citing G5 as support, when the line read "[G5 -- cut]" in lower case and was
                # naming it as cut exactly as required. A case-sensitive check made the draft look
                # wrong when the CHECK was wrong -- the same claim/check divergence, in the checker.
                upper = line.upper()
                if f"[{cid}" in line and "CUT" not in upper and "NOT MEASURED" not in upper:
                    failures.append(
                        f"{name}: cites CUT claim {cid} as support: {line.strip()[:90]}"
                    )
                    break

    # 2: artifact paths named in the claims list exist
    # The first version tried three fixed prefixes and reported five artifacts "not found" that all
    # exist -- `fit.py` is at chipsim/transport/fit.py, deeper than any prefix guessed. A resolver
    # that encodes where files are ASSUMED to live answers a different question from "does this
    # artifact exist". It searches now, and a path given in full still has to match in full.
    def resolves(rel: str) -> bool:
        direct = ROOT / rel
        if direct.exists():
            return True
        if "/" in rel:
            # a full-ish path must match as a suffix of something real, not merely by basename
            return any(
                str(p.relative_to(ROOT)).endswith(rel)
                for p in ROOT.rglob(Path(rel).name)
                if ".venv" not in p.parts and ".git" not in p.parts
            )
        return any(
            ".venv" not in p.parts and ".git" not in p.parts for p in ROOT.rglob(rel)
        )

    for cid, col in sorted(artifacts.items()):
        for rel in BACKTICK_PATH.findall(col):
            if not resolves(rel):
                failures.append(f"{cid}: artifact not found on disk: {rel}")

    # 4: the not-claimed list appears in both granularities, item for item
    long_items = not_claimed_items(DRAFTS["long"].read_text(encoding="utf-8"))
    short_items = not_claimed_items(DRAFTS["short"].read_text(encoding="utf-8"))
    if not long_items:
        failures.append("long form carries no NOT CLAIMED list")
    if not short_items:
        failures.append("short form carries no NOT CLAIMED list")

    long_by_lead = {lead: body for lead, body in long_items}
    short_by_lead = {lead: body for lead, body in short_items}

    for lead in long_by_lead:
        if lead not in short_by_lead:
            failures.append(f"NOT CLAIMED item in long form, MISSING from short form: {lead[:70]}")
    # SYMMETRIC now. An item invented in the short form -- present in neither the long form nor the
    # claims list -- used to be a NOTE, so the gate guarding §6.4 passed it.
    for lead in short_by_lead:
        if lead not in long_by_lead:
            failures.append(f"NOT CLAIMED item in SHORT form only (invented): {lead[:70]}")
    # And the body must agree, not merely the lead: this is the contradiction check.
    for lead, body in long_by_lead.items():
        other = short_by_lead.get(lead)
        if other is not None and other != body:
            failures.append(
                f"NOT CLAIMED item '{lead[:44]}' DIFFERS between granularities beyond its lead -- "
                "one of them says something the other does not"
            )
    if len(long_by_lead) != len(long_items) or len(short_by_lead) != len(short_items):
        failures.append(
            "two NOT CLAIMED items share a lead, so item-for-item pairing is ambiguous"
        )

    uncited = sorted(set(status) - cited_total)
    sha = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()

    record = {
        "measured_at_commit": sha,
        "claims_total": len(status),
        "claims_cut": sorted(cut),
        "claims_cited_in_drafts": sorted(cited_total),
        "claims_never_cited": uncited,
        "not_claimed_items_long": len(long_items),
        "not_claimed_bodies_compared": True,
        "not_claimed_items_short": len(short_items),
        "failures": failures,
        "notes": notes,
        "verdict": "PASS" if not failures else "FAIL",
    }
    out = Path(__file__).resolve().parent / f"traceability-{sha}.json"
    if write:
        out.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    print(f"measured at commit {sha}")
    print(f"claims                 : {len(status)}  (cut: {len(cut)})")
    print(f"cited across drafts    : {len(cited_total)}")
    print(f"NEVER cited            : {len(uncited)}  {uncited if uncited else ''}")
    print(f"NOT CLAIMED items      : long {len(long_items)} / short {len(short_items)}")
    print(f"\nfailures: {len(failures)}")
    for f in failures:
        print(f"  FAIL  {f}")
    for n in notes:
        print(f"  note  {n}")
    print(f"\nVERDICT: {record['verdict']}")
    print(f"wrote {out.relative_to(ROOT)}" if write else "--no-write: nothing written")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
