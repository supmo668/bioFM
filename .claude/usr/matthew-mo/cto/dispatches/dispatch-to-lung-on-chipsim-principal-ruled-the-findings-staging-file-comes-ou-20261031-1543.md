---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-10-31T15:43
status: created
priority: high
size: task
subject: "PRINCIPAL RULED: the findings-staging file comes OUT of PR #37 (rows 83-86). Remove it by a new commit, move it to a dedicated staging branch, re-run /pr-prep, re-submit; #37 then squash-merges"
in_reply_to: null
---

# PRINCIPAL RULED: the findings-staging file comes OUT of PR #37 (rows 83-86). Remove it by a new commit, move it to a dedicated staging branch, re-run /pr-prep, re-submit; #37 then squash-merges

# PR #37 is unblocked once the staging file is out of it. Four rulings, rows 83-86.

The principal ruled directly, 2026-10-31, on four structured questions after a /grill-with-res evidence pass. Recorded as **lung approvals rows 83-86** (route: principal). CLAUDE.md now carries the rule.

## What you do, in order
1. **Create the staging branch.** `lung-on-chipsim-staging`, from the stage2 tip, carrying `workstreams/lung-on-chipsim/findings-staging/2026-10-30-evidence-assembly.md` exactly as it is. Push it. **It is never the head of a PR to main** (row 84). Your future staging ledgers live there too.
2. **Remove the file from `lung-on-chipsim-stage2` by a NEW commit** (`git rm`). **No rewrite and no force-push of the stage2 remote**: row 79, it alone holds 3 payload blobs (row 83).
3. **Re-run `/pr-prep`.** The `findings-staging/` path is inside Hash E (`diff-hash` excludes only qgr/rgr, plan-approval, gate reports, dev-log and dispatch trees), so receipt `6d8afb8` no longer matches. I read the exclusion list but didn't recompute the hash. If your recompute says the receipt still matches, say so and don't re-sign for nothing.
4. **Push, then `/pr-submit`** with the new Hash E. I verify with the signing toolchain and **squash-merge** (row 86: a merge commit would bring `3314190`, which adds the file, into main's history).
5. Keep the three dispatches that cite the staging path as they are. They are records, and the path still resolves on the staging branch.

## What I do
- Mirror the staging ledger to a Notion row under the lung index as the principal's ratification surface (row 84), citing `lung-on-chipsim-staging` at its pushed SHA. I need step 1 pushed first.
- MYB-8 (the CI guard, row 85) is ticketed. It isn't yours and isn't in #37.

## Recorded, not hidden
The file has been readable on public `origin/lung-on-chipsim-stage2` since `3314190` (2026-10-30 11:38). That can't be withdrawn without rewriting a load-bearing remote, and row 83 states that plainly.

## Unchanged
§1, §2, OCT1 and the three number collisions still wait for the principal. Moving the file doesn't ratify or reject anything in it. Your #841-era roster provenance task (rows 80-82) is independent of this one.
