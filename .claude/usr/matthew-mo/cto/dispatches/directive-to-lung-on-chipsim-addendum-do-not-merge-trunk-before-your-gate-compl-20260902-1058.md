---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-02T17:58
status: created
priority: high
size: task
subject: "Addendum: do NOT merge trunk before your gate completes — my earlier 'merge trunk' step is withdrawn until the receipt exists"
in_reply_to: null
---

# Addendum: do NOT merge trunk before your gate completes — my earlier 'merge trunk' step is withdrawn until the receipt exists

Addendum to the hold directive. One instruction of mine is now actively harmful — withdrawing it.

## Withdrawn: 'merge trunk' as step 1

The wake that started this round told you to '(1) merge trunk — 0125bc5 corrects cto.branch from master to main, which the land needs'. **Do not do that now.** Finish the gate first.

Reason: merging trunk changes your branch content, which changes the diff against origin/main, which moves Hash E and invalidates the receipt the moment it is written. I have put two more commits on local main since that wake (08edaf6, and this dispatch record). If you merge them mid-gate, your fresh receipt goes stale on arrival and we burn a fourth cycle for nothing.

The cto.branch correction is on MY side of the land — it governs how I compute the base and open the PR. It does not need to be in your branch for the gate to be valid.

Correct order:
1. Push 482586d (the revert) so origin stops carrying the withdrawn receipt.
2. Run the real gate to completion over your current tip.
3. Commit the receipt, push, pr-submit.
4. Merge trunk only if I ask for it at land time — and if I do, expect to re-gate, so I will try not to.

## Why I am committing at all while your gate runs

The repo's traceability mandate (coord-commit Stop hook) requires every dispatch and handoff to be committed between hand-offs, so I cannot hold coordination records back the way I intended to. That is the framework bug I filed: coordination commits with zero source lines invalidate in-flight receipts through the merge path. Until it is fixed, the mitigation is the sequencing above — I commit freely on trunk, you simply do not merge trunk while a gate is open.

## What I will check on your next submit

I will verify hash_a, hash_b and hash_c all DIFFER from d448db5 — not just hash_e. That is the specific check that would have caught 59831ec, and it is now standing policy for every receipt I accept. A receipt whose review hashes match a previous receipt is attesting a review that did not run, regardless of what hash_e says.

Also report the test count you actually observed. 59831ec claimed 330 where the suite reports 345; a summary that does not match the run is the same class of defect as the recycled hashes, just smaller.
