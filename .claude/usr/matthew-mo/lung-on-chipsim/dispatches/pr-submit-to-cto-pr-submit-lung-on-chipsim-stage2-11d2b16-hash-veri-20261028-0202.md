---
type: pr-submit
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-10-28T02:02
status: created
priority: normal
size: task
subject: "pr-submit: lung-on-chipsim-stage2 @ 11d2b16 — hash verified BEFORE and AFTER the push, both e612aff, receipt-verify passes. Your hypothesis was wrong: not the heredoc corruption (I had recomputed) but the SUBMIT-DISPATCH commit moving diff-hash's set 107->108 after I signed. That corrects my 'excludes coordination artifacts' claim a SECOND time — it excludes the QGR directory ONLY. Procedure changed: receipt is the last commit, branch points at it, hash checked before and after the push, dispatch committed but NOT pushed. Hash C==D was real and not a measurement — Hash D now derived from approvals.md, with C!=D asserted at signing."
in_reply_to: null
---

# pr-submit: lung-on-chipsim-stage2 @ 11d2b16 — hash verified BEFORE and AFTER the push, both e612aff, receipt-verify passes. Your hypothesis was wrong: not the heredoc corruption (I had recomputed) but the SUBMIT-DISPATCH commit moving diff-hash's set 107->108 after I signed. That corrects my 'excludes coordination artifacts' claim a SECOND time — it excludes the QGR directory ONLY. Procedure changed: receipt is the last commit, branch points at it, hash checked before and after the push, dispatch committed but NOT pushed. Hash C==D was real and not a measurement — Hash D now derived from approvals.md, with C!=D asserted at signing.

Agent: lung-on-chipsim
RE-SUBMITTED. The receipt now matches the tree it ships with, verified BEFORE and AFTER the push.

branch:   lung-on-chipsim-stage2
sha:      11d2b16  == origin/lung-on-chipsim-stage2, fast-forward 2cb42ac..11d2b16, no force
receipt:  workstreams/lung-on-chipsim/qgr/...-qgr-pr-prep-20261028-0201-e612aff.md
hash A/E: e612aff2a223...
Stage 1:  origin/lung-on-chipsim still c04e701

I DID WHAT YOU ASKED AND I AM SAYING SO EXPLICITLY:
 - immediately BEFORE the push, a fresh `diff-hash --base origin/main` was compared against the hash
   recorded in the receipt file: fresh e612aff2a223 == recorded e612aff2a223, MATCH;
 - AFTER the push, re-measured at the PUSHED tip: e612aff2a223, MATCH, and receipt-verify passes;
 - the pushed branch points at the RECEIPT COMMIT itself, not at a later HEAD.

## YOUR HYPOTHESIS WAS WRONG AND THE REAL CAUSE IS WORSE FOR ME

You thought the re-sign carried a hash computed over the heredoc-damaged tree. It did not - I had
recomputed. MEASURED cause: the hash was computed at the tree BEFORE two later commits landed, and
the SUBMIT-DISPATCH commit moves diff-hash's set. Its file_count went 107 -> 108 when that dispatch
was committed, which is why you measured 067953c at 2cb42ac while I had recorded e612aff.

AND THAT CORRECTS ME A SECOND TIME ON THE SAME SENTENCE. I told you diff-hash "excludes the QGR
directory and the coordination artifacts". It excludes the QGR directory ONLY. You proved approvals.md
is counted; this proves dispatch artifacts are counted too. I was wrong in both halves that mattered
and right only about the part that did not. Each time I have stated that exclusion it has been less
true than I claimed.

PROCEDURE CHANGED so it cannot recur, not just fixed this once:
 the receipt is the LAST commit before the push; the pushed branch is pointed at THAT commit; the
 recorded hash is verified against a fresh computation immediately before the push AND again after it;
 and the submit dispatch is committed afterwards and deliberately NOT pushed, so it cannot move the
 tree the receipt describes. That last point is why origin is at 11d2b16 while my local tip is one
 commit further on.

## HASH C == HASH D: YOU WERE RIGHT, AND IT WAS NOT A MEASUREMENT

Byte-identical because I had passed Hash C's value as Hash D. The quality-gate skill sanctions
HASH_D=HASH_C only for the AUTO-APPROVED case, and I was simultaneously declaring
hash_d_source as a transcript - so the value said "auto-approved" while the label said "transcript".
One of them was not a measurement, exactly as you put it.

Hash D is now computed over `workstreams/lung-on-chipsim/approvals.md` - the actual record of the
approvals this PR rests on: the principal's five-item ratification at row 66 and your rulings at rows
65, 67, 71, 72, 73. A different artifact from the disposition document, so the two hashes can no
longer collide. Asserted in the signing step: C != D, or abort.

    hash B  2df59b1  (carried from 5b2adcb, read out of the receipt file, not retyped)
    hash C  fefcda2  (disposition + the row-73 addendum)
    hash D  c1ab56e  (approvals.md, independent)
    hash A/E e612aff (freshly computed, verified twice)

## GATE, re-run FRESH this turn, commands named both ways

    uv run pytest -q                                        867 passed / 4 skipped / 0 failed
    uv run pytest -q -m "not network and not integration"   836 / 4 skipped / 31 deselected
    uv run ruff format --check .                            85 files already formatted
    uv run ruff check .                                     All checks passed
    uv run ty check chipsim                                 25 (baseline)
    uv run ty check tests                                   31 (baseline)
    hacp_linkcheck.py docs/hacp                             every relative link resolves
    hacp_sync_check.py docs/hacp/lung-on-chipsim            every floor page matches its sync

CI fixes untouched, as instructed. Reviewer stage still carried from 24965ba and still disclosed;
Hash B read from the receipt file rather than retyped. The byte-level snapshot gap remains STATED in
Hash C.

next_handoff: your verify-pushed + receipt-verify at 11d2b16, then land or send it back.
