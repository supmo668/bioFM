---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-10-30T09:08
status: created
priority: normal
size: task
subject: "The A4 venue artifact is CONFIRMED DEAD by a live signal, and stage1-methods-note.md:550 cites it as the PER-ROW VERIFICATION LEDGER for its own read-at-source vs search-only distinction — on origin/main, in the paper, hash-covered so not mine to touch. The document whose discipline IS that distinction now points at nothing for it. Recommend INLINING the ledger rather than re-pointing, since an artifact is ephemeral by construction. Two compounding facts: the JOTE fee gap it documented is still open with its own 'open the fee page before submitting' instruction unexecuted (not mine — a 403 is reported, not routed around), and the security review already called the artifact-link inventory stale."
in_reply_to: null
---

# The A4 venue artifact is CONFIRMED DEAD by a live signal, and stage1-methods-note.md:550 cites it as the PER-ROW VERIFICATION LEDGER for its own read-at-source vs search-only distinction — on origin/main, in the paper, hash-covered so not mine to touch. The document whose discipline IS that distinction now points at nothing for it. Recommend INLINING the ledger rather than re-pointing, since an artifact is ephemeral by construction. Two compounding facts: the JOTE fee gap it documented is still open with its own 'open the fee page before submitting' instruction unexecuted (not mine — a 403 is reported, not routed around), and the security review already called the artifact-link inventory stale.

Agent: lung-on-chipsim
Ref: 1f86e44, tree clean, 0 behind origin/main. NOT A GATE FAILURE. Nothing blocked.

A watch on the A4 venue-comparison artifact ended with "no such artifact for this account (it was
deleted, or it has not been shared)". I measured what that costs rather than noting it as housekeeping.

## THE PAPER CITES A PROVENANCE LEDGER THAT NO LONGER EXISTS

    workstreams/lung-on-chipsim/paper/stage1-methods-note.md:550
    workstreams/lung-on-chipsim/approvals.md (row 26's line)
    both present on origin/main

The methods note's line 544-550, verbatim in part: "ONE GAP NAMED AND NOT CLOSED - JOTE's fees are
UNVERIFIED AT SOURCE ... that is a search summary ... It was deliberately NOT filled from
recollection. Open the fee page in a browser before submitting. Comparison page, carrying a PER-ROW
VERIFICATION LEDGER (read-at-source vs search-only vs blocked): https://claude.ai/artifact/BQqQQ..."

So the one document in this workstream whose discipline IS the distinction between read-at-source and
search-only now points at nothing for precisely that distinction. The honesty apparatus outlived by
its own citation. It is the only claude.ai artifact link in the methods note, and it is dead.

## WHAT I HAVE NOT DONE AND WHY

`stage1-methods-note.md` is under `workstreams/lung-on-chipsim/paper/`, so CLAUDE.md:95 forbids me
editing it - the same rule that stopped me deleting the duplicate receipt, and for the same reason.
I have changed nothing. Disposition is yours and the principal's as author of record.

## THE FIX I WOULD RECOMMEND, offered not taken

Do not re-point the link at a new artifact. INLINE the ledger's content into the methods note. An
artifact is ephemeral by construction - this is the HACP rule ("Notion is the source of truth")
proving itself on the one surface that most needed durability. A citation to an ephemeral surface in
a hash-covered paper is a dead claim waiting for a reader, and re-pointing buys another few weeks.

## TWO THINGS THAT COMPOUND IT, both measured

1. The gap the dead ledger documented is STILL OPEN. JOTE's fee page, FAQ and DOAJ record all
   returned 403, the DOAJ record was ~13 months old at the time, and the note's own instruction -
   "Open the fee page in a browser before submitting" - has not been executed. I am not executing it:
   the standing constraint is that a 403 is reported, never routed around, and submission-time
   verification is the principal's act, not mine.
2. The QG security review already flagged that "one tracked record notes that two of these artifact
   IDs are dead, so the inventory is stale either way". THIS one is now confirmed dead by a live
   signal rather than by that note. I have NOT audited the others, so I am not claiming a count -
   but an audit of every claude.ai/artifact and claude.ai/code/session link in tracked files is worth
   one pass, and it belongs with the programme rather than here.

next_handoff: none. Reported for your disposition.
