---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-18T18:03
status: created
priority: normal
size: task
subject: "Iteration 13.3 - Ruling 1 done, gitlink half of Ruling 2 done, plan half carried back to you"
in_reply_to: null
---

# Iteration 13.3 - Ruling 1 done, gitlink half of Ruling 2 done, plan half carried back to you

event: iteration-complete
workstream: lung-on-chipsim
iteration: "§13.3"
branch: lung-on-chipsim
commit_hash: e35c982
qgr_receipt: workstreams/lung-on-chipsim/qgr/bioFM-matthew-mo-lung-on-chipsim-lung-on-chipsim-bioFM-qgr-iteration-complete-20260918-1102-1db3373.md
hashes: "A == E == 1db3373, base 773e64d, 2 files, --project bioFM"
remote_refs_observed:
  origin/lung-on-chipsim: e35c9825c40a01f1742d5591da5fb7702f5ac66f
  origin/main: df89f5039be4449aa3f7246ee496b28edb708cfe (untouched)

hash_a_equals_hash_e_on_purpose: |
  This diff answers two rulings, not a review-and-fix cycle. There is no distinct "artifact
  entering review", and manufacturing one would be a hash attesting to a stage that did not happen.
  Stated in the receipt summary rather than left for you to notice.

ruling_1: DONE
  refusal: |
    A staged root resolving inside the scanned working tree, or under a declared output root, is
    REFUSED. Resolved on both sides, never prefix-matched — a staged root reaching the tree through
    a symlink shares no string prefix with it, and there is a separate test for that route which
    the string-comparison mutant dies on. `$TMPDIR` test as ruled.
  my_first_version_was_wrong: |
    I reused `declared_output_roots()`, which under pytest APPENDS a `$TMPDIR` grant so
    record-bearing writers can write to tmp during tests — so the new refusal rejected every staged
    tree the suite builds. The suite caught it on the first run. The grant answers a different
    question than this check does; it now reads DECLARED_OUTPUT_ROOTS resolved against the project,
    with no environment-dependent additions.
  residual: |
    ACCEPTED and documented, not swept, with no sweeper installed. The case you asked be named is
    recorded with it: when the gate FAILS, the residual holds the record-bearing blob being
    refused — not an escalation, since that blob is in the index either way, which is what is being
    refused, but stated rather than left to be discovered.

ruling_2:
  gitlink_half: DONE
    Pinned by a test, because you verified it by hand and it should not depend on anyone
    re-deriving it. A gitlink names a COMMIT, never a blob, so it stays outside the now-owner-blind
    fatal predicate; submodules are DISCLOSED as "N not scanned" rather than dropped. The mutant
    that stops excluding `160000` dies on the new test. Your point stands on its own: six
    repositories unscanned inside a confident "798 tracked" header would be this guard's own
    failure mode.
  plan_half: CARRIED BACK TO YOU — please rule
    I have NOT written the plan revision. Every revision since r2.25 has arrived on local `main`
    from you and been merged from there, and the same dispatch restates "nothing outside
    projects/lung-on-chipsim/" as a hard constraint — which the plan tree is. So writing it myself
    would break a constraint you restated in the message that asked for it.
    Tell me which you want: (a) you issue the revision, and I merge it as usual — my default
    assumption; or (b) you want me to draft the text and send it for you to land. I can supply the
    two items you asked be recorded alongside it verbatim: the two-`ls-files` race as the carried
    refactor's REASON TO EXIST, so nobody later deletes it as unmotivated, and the gitlink domain.

your_correction_to_your_own_instruction: |
  Noted, and I would rather have this in the record than not: you told me to delete the symlink
  special case, I deleted it for staged, measured it load-bearing for worktree, and reported the
  difference. You called the error what it was — a conclusion generalised from the mode you were
  reasoning about to a mode you were not, which is the same "edit computed against one shape and
  applied to another" family. I did the identical thing twice in this section: once moving the
  write to `Path.open` and once fixing the detector for it at args[1:]. It is not a failure mode
  that respects seniority, and the instruction to keep reporting deviations exactly that way is
  taken.

standing_instruction_adopted: |
  Every reviewer I spawn from here states whether it ran the suite, and reports baseline and
  deselection counts or says plainly that it ran none. Recorded in the triage as a standing rule,
  not just this round. Your framing is the operative part: an unstated "I didn't run it" is
  indistinguishable from "it passed".

verification:
  suite: "baseline 1010 -> 1013 passed / 5 skipped, 0 DESELECTED (delta = the 3 tests added)"
  mutation: "3/3 killed BY ASSERTION this round — none by timeout — module restored byte-for-byte"
  gates: "record-content-gate (STAGED) exit 0 and record-content-report (WORKTREE) exit 0, 798 tracked, BOTH run immediately before the push"
  format_lint: "read AFTER the last edit"

carried_unchanged:
  - one enumeration threaded through both the listing and the materialisation (now carried WITH its reason, per your ruling)
  - THIS_PROJECT resolving from the import location; ContentPolicy holding two of seven policy decisions; one path printing two owners; _MINIMUM_PLAUSIBLE_TRACKED and the toplevel check unpinned
  - r2.28's property remains AVAILABLE, NOT ENFORCED; hook/CI activation sits with the principal as item 2d

next_handoff: cto rule on Ruling 2's plan half — (a) you issue the revision, or (b) I draft the text for you to land
