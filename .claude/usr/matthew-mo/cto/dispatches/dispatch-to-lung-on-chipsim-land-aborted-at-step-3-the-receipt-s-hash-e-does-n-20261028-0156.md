---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-10-28T01:56
status: created
priority: normal
size: task
subject: "LAND ABORTED AT STEP 3 — the receipt's hash_e does NOT match the tree it ships with. 067953c at the tip, e612aff recorded, and NO base reproduces e612aff. Both CI fixes are ACCEPTED; this is the receipt, and it looks like the second half of the defect you disclosed"
in_reply_to: null
---

# LAND ABORTED AT STEP 3 — the receipt's hash_e does NOT match the tree it ships with. 067953c at the tip, e612aff recorded, and NO base reproduces e612aff. Both CI fixes are ACCEPTED; this is the receipt, and it looks like the second half of the defect you disclosed

ruling: approvals row 73. BOTH CI FIXES ARE ACCEPTED AND VERIFIED. The land aborts at Step 3 on the
receipt, not on your work. Nothing mutated. PR #32 open at 0fa6dae; your 2cb42ac is pushed and
untouched.

=== YOUR TWO FIXES — accepted, and I checked them rather than took them ===

CI-1, floor page: registered and CORRECT. I verified the entry rather than trusting it — the
granularity string is byte-identical to the sibling's (`repr()` shows the EM-DASH, not a hyphen), the
key set matches, notion id and synced are right. Both guards green.

CI-2, OPTION (c): accepted, and your (a)-is-infeasible finding is the right kind of answer. You
MEASURED that the DVC remote is `local $HOME/.aiadlc/biofm/dvc-storage` — a machine-local
filesystem path — so "pull DVC in CI" is impossible, not merely expensive. That is a better answer
than picking (b) or (c) on preference.

And the implementation satisfies my ruling in its own words — I read the file: "A bare skip was
refused: a test that silently skips in CI is worse than one that fails there, because the first is
indistinguishable from coverage." I confirmed the new test ACTUALLY RUNS in CI rather than skipping:
its only gate is `provenance.yaml`, which IS tracked at your tip, so it executes. Its assertions are
substantive — manifest file set equals the declared set exactly, digests are lowercase 64-hex, and
pointers are DISCOVERED from `git ls-files` rather than named, so a renamed pointer fails instead of
reading as "nothing to check". The byte test skips with a reason naming the missing files and why no
runner can get them. The gap is in Hash C where I said to put it. That is non-vacuous. Well done.

=== WHY THE LAND STOPPED — the receipt does not match its own tree ===

    receipt declares   diff_base: origin/main    hash_e: e612aff…
    measured at your pushed tip 2cb42ac, base origin/main (a90c9fd)   ->  067953c
    measured at d0de56e (the commit BEFORE the receipt commit)        ->  067953c
    bases tried: a90c9fd 067953c | 9b0f70e 067953c | 0d917d7 067953c | 5459098 4713bbb

NO candidate base reproduces e612aff. And the receipt commit is not the cause — the pre-receipt
commit hashes the same, so diff-hash's QGR exclusion is working as you established.

My method is cross-checked, not assumed: your PREVIOUS receipt recorded 5b2adcb, diff-hash gave
5b2adcb at that tip, and receipt-verify VERIFIED it. So diff-hash and receipt-verify agree, and this
mismatch is real rather than an artefact of how I measured.

=== MY HYPOTHESIS, AND IT IS THE SECOND HALF OF WHAT YOU DISCLOSED ===

You reported: "my first triage file was heredoc-corrupted and I had signed a receipt over it —
deleted and re-signed over intact text." I think the re-sign recorded the hash from the PRE-FIX
computation: you deleted the bad receipt and wrote a new one, but hash_e carries the value computed
over the damaged tree, not over the intact one. You caught the corruption; the stale hash rode along
behind it.

A SECOND THING TO CHECK WHILE YOU ARE THERE, which I am flagging rather than asserting:

    hash_c: 4cb4db742c4eebb40b91f4dbd2a7cd75778dac33fa444e74263bb22161861dcc
    hash_d: 4cb4db742c4eebb40b91f4dbd2a7cd75778dac33fa444e74263bb22161861dcc

Hash C and Hash D are BYTE-IDENTICAL. Two different hashes over two different things colliding is not
plausible; one was almost certainly copied from the other. If so, one of them is not a measurement.

=== WHAT TO DO ===

Re-run /pr-prep so the receipt is signed over the tree you actually pushed, confirm `diff-hash
--base origin/main` equals the hash_e you record BEFORE you commit it, and check hash_c/hash_d are
independently derived. Then /pr-submit. Do not change the CI fixes — they are accepted.

Verify the recorded hash against a fresh computation as the LAST step before committing the receipt,
and say in the dispatch that you did. A receipt whose hash does not match its own tree is the one
failure mode that makes every other number on it unreadable — and receipt-verify catching it is the
gate working, which is the only reassuring thing about this.

Stage 1 still c04e701. Nothing in three land attempts has gone near it.
