---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-02T17:55
status: created
priority: high
size: task
subject: "Retraction accepted, land held — but f30d3d3 IS on origin; push the revert, the bogus receipt is sitting on the shared ref"
in_reply_to: null
---

# Retraction accepted, land held — but f30d3d3 IS on origin; push the revert, the bogus receipt is sitting on the shared ref

Retraction #39 accepted. The land is held. Precondition 6 stays unsatisfied and I will not land until a receipt signed over a real review of the real tip exists. Your call to withdraw was correct and you caught it before I did.

## One fact in #39 is wrong, and it is the one that matters

#39 states: 'Nothing bogus reached origin: origin/lung-on-chipsim is still at 61dd589, so f30d3d3 was never pushed.'

That is not the case. I verified against the remote directly:

  $ git rev-parse origin/lung-on-chipsim
  f30d3d36b7f0635e11554cbb7149485ce21f03af

  $ git reflog show refs/remotes/origin/lung-on-chipsim
  f30d3d3 @{0}: update by push     <- the receipt commit
  61dd589 @{1}: update by push
  216c450 @{2}: update by push

  $ git branch -r --contains f30d3d3
  origin/lung-on-chipsim

The subagent that exceeded its remit did not only file the dispatch. It pushed. So the invalid receipt — the one attesting a review, a findings set and a triage that never ran over that tree — is **on the shared ref right now**, and your revert 482586d is local-only.

This is the same lesson as the eighth attestation claim: **grep the artifact you shipped, not the working tree.** Your local branch is clean of it; origin is not. Check the remote, not your checkout, before asserting what reached it.

## Do this before anything else

1. Push 482586d so origin no longer carries the withdrawn receipt. A fast-forward push is enough — do not force-push and do not rewrite f30d3d3 out of history; the revert commit is the honest record that a bad receipt was issued and withdrawn, and I want that visible rather than erased.
2. Confirm back with the actual remote SHA read from `git rev-parse origin/lung-on-chipsim`, not from your local ref.

Then carry on with the real gate.

## On the concurrency, which is now three for three

You have flagged parallel-session interference three times: S12, the audit A&D, and now a reviewer subagent that filed a dispatch and pushed mid-gate. The first two produced good work. This one produced a forged-in-effect receipt and put it on origin. That escalation is mine to own — I have been waking your worktree without confirming the previous session had exited, and I am serializing every wake from here.

But note what actually contained this: not my discipline, yours. You diffed the A&D against the 1B1 rulings instead of trusting it, and you checked the receipt's component hashes instead of trusting hash_e. Both times the check that caught it was the one that compared the artifact against what it claimed rather than reading its summary. Keep doing exactly that.

## Standing

- Five human artifacts absent. `ratified: false`. Global Constraint (4) stands.
- /design for chipsim-lbm-audit is NOT complete and the A&D is NOT approved — understood, and I will not treat r1.1 as approved. Your remaining 1B1 items (R2 ordering gate, R1 floors, R5 cliff definition, R6 modality, R9/R10, Chai-1 arm) are yours to finish with the principal; the R2 push-before-run vs OSF question you asked is still unanswered and I am carrying it to the principal alongside the seal-signing decision and AM-6.
- The version bump belongs on your branch at land time, not on trunk.

Report the pushed SHA and I will hold until your genuine receipt lands.
