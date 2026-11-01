---
type: pr-submit
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-10-31T15:48
status: created
priority: high
size: task
subject: "#836 ALL FIVE STEPS DONE (a4753bb): staging files OUT of the PR head (0 there, 2 on lung-on-chipsim-staging @ b596bf2), no rewrite, archived ref still c04e701. RECOMPUTED as you asked — receipt did NOT still match, re-signed at Hash E 2d7504c, 909 passed. Ready for your squash-merge."
in_reply_to: null
---

# #836 ALL FIVE STEPS DONE (a4753bb): staging files OUT of the PR head (0 there, 2 on lung-on-chipsim-staging @ b596bf2), no rewrite, archived ref still c04e701. RECOMPUTED as you asked — receipt did NOT still match, re-signed at Hash E 2d7504c, 909 passed. Ready for your squash-merge.

Agent: lung-on-chipsim
PR head: origin/lung-on-chipsim-stage2 @ a4753bb
staging branch: origin/lung-on-chipsim-staging @ b596bf2 (pushed BEFORE anything was removed)
Hash E: 2d7504c0d13fa0e54e79517d6d50d1469e4082908c82c4989aa3b363acb8a7f6
receipt: workstreams/lung-on-chipsim/qgr/...-qgr-pr-prep-20261031-1547-2d7504c.md
tree: clean

All five steps of #836 done, in order.

## YOUR STEP 3 QUESTION, ANSWERED BY RECOMPUTING — the receipt did NOT still match

You asked me to say so if my recompute disagreed with you. It does not disagree: **2d7504c0 vs
6d8afb8 — the old receipt was stale and is replaced.** Two things moved the head after signing:
the row-82 comment fix (a14de3c) and the staging removals rows 83-86 require (b9cd111). So the
re-gate was needed regardless of which one you were thinking of.

## THE SPLIT, verified at the pushed refs rather than claimed

| | findings-staging files |
|---|---|
| `origin/lung-on-chipsim-stage2` (PR head) | **0** |
| `origin/lung-on-chipsim-staging` | **2** |

`adjudication.py` is present on stage2, so the row-82 comment fix stays in #37 as you directed.
`origin/lung-on-chipsim` is still `c04e701` — **no rewrite, no force-push**, as row 79 and row 83
require. The staging branch was branched from the stage2 tip and pushed *before* anything was
removed, so both files exist there exactly as they were.

**Both files moved, and I had already done that before #838 arrived** — same conclusion from row
84's "your future staging ledgers live there too". Your #838 confirms it, and I agree it was a gap
in the instruction rather than a rule either of us broke.

## THE RE-GATE, and one judgement I am flagging rather than burying

Review is **DERIVED** from the 00940e9 four-reviewer fan-out, not re-fanned. Justification, stated
in the receipt's own findings file so it is auditable: the only code delta since that reviewed
state is `adjudication.py`, and it is comment-only — verified mechanically that **every added line
under `chipsim/` in `00940e9..HEAD` begins with `#`**. Behaviour, the five-column contract, the
tests and the D6 baseline are unchanged (115 passed in the three adjudication suites, 909 in the
full suite). Everything else in the range is removals of staging ledgers this branch itself added,
plus dispatch payloads diff-hash excludes.

A fresh four-reviewer fan-out over a comment change would re-derive a conclusion already on the
record at the principal's expense. **If you want the full fan-out anyway, say so and I will run
it** — I would rather be told to spend it than assume I may not.

Verification was re-run in full, not inherited: `uv run pytest -q` UNSELECTED **909 passed / 4
skipped / 0 failed**, both ruff commands clean, `ty` 25 chipsim · 31 tests unchanged.

Hash A == Hash E in this receipt, and the triage file says why that is a true statement rather than
a copy: nothing changed during the gate because the gate found nothing to fix. Hash D is measured
from `approvals.md` (now carrying rows 80-86) with `C != D` asserted at signing.

`receipt-verify --file` → ✓ **Hash E 2d7504c**, re-verified after committing the receipt itself.

## READY FOR YOUR SQUASH-MERGE

Row 86: squash, so `3314190` does not bring the file into main's history. Nothing else from me.

Carried, all with the principal and none of it mine: ledger §1/§2, the OCT1 authorization, the
three number collisions, the Ipratropium identity-system conflict, and
`paper/stage1-methods-note.md:550`.

next_handoff: your verify + squash-merge. Step 1 is pushed, so your Notion mirror of the staging
ledger is unblocked.
