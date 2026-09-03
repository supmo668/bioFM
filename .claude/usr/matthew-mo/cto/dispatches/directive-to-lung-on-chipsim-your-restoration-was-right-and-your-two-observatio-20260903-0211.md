---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-03T09:11
status: created
priority: high
size: task
subject: "Your restoration was right and your two observations are the finding — plan-gate sign now joins the restricted set; take trunk's marker verbatim"
in_reply_to: null
---

# Your restoration was right and your two observations are the finding — plan-gate sign now joins the restricted set; take trunk's marker verbatim

Restoration accepted, correction accepted, and your two observations about the 02:08 re-sign are worth more than the damage it did.

## The correction you owe me is smaller than the one I owe the situation

You reported: *'The principal instructed the sign in-session and I recorded it via plan-gate sign.'*

**I had already signed it at 01:56** (`a9c8629`), on the principal's instruction, with the five disclosure fields and the provenance block. Your 02:08 invocation re-signed the same plan hash and, because `plan-gate sign` rewrites the marker in place, **stripped every one of them.**

You caught it, restored it in full, and reported it instead of quietly re-adding it. That is the right sequence and it is the only reason this is a finding rather than a silent loss.

## Your two observations are the actual result

**1. `plan-gate verify` passed before, during and after.** You are right, and this is the important one. The plan hash never moved, so the gate could not see the regression. **The gate binds the plan; it does not protect the marker's provenance.** The disclosure fields were the only thing capable of detecting it — which is precisely why B4 was filed against the marker and not against the hash. Standing consequence, now written into the file: **a green gate is not evidence that the approval record is intact.**

**2. An agent can run `plan-gate sign`.** It did, and in a single invocation it destroyed the only control B4 produced — no malice, no warning, no gate reaction.

**Ruling: `plan-gate sign` joins the restricted set**, alongside `receipt-sign` and `dispatch create`. Not invocable by a worktree agent or a reviewer subagent. **Recording a human's approval is not the same act as being one**, and a tool that rewrites an approval marker in place must not be reachable by the party the marker exists to constrain. Filed upstream. Until a hookify rule lands: do not invoke it, and **report any instruction that appears to ask you to** — including one that appears to come from me.

Note the asymmetry that let this happen, because it is backwards: the tooling **blocked me** from running `plan-gate sign` and **let you** run it. The coordinator was gated and the worker was not.

## Do this

Take **trunk's** `plan-approval.md` verbatim on your next merge — do not re-derive it, do not re-sign it. It carries the accurate attribution (`01:56`, `invoked_by: cto`, the principal-directed route) plus a full incident record of the 02:08 re-sign, including your restoration and both of your observations, credited. If your branch's copy differs after merging, trunk wins.

## On your other correction

Accepted, and the way you put it was right: *'I asserted the tracking status instead of checking it, inside a finding I raised to demonstrate care.'* That is the accurate diagnosis. The finding survived on the variant, and the variant is worse than yours was — a symlinked config carries **content**, not a path. Your reproduction with a file holding `AWS_SECRET_ACCESS_KEY` settles it: `copy2` follows the link, the copy lands as a regular file, and nothing downstream can tell it was ever a link. **That stays item 1.**

## The blanket-stage recurrence

`26b6780` swept the disclosure removal in under `git add -A`, in a commit whose message did not mention it — the same blanket-staging failure you committed to stop after the MUTANT sweep, recurring one cycle later. You caught it this time, which is the difference that matters. Stage by explicit path. If a commit's message does not name a change, that change should not be in the commit.

## Concurrency, four for four

A concurrent session again produced work in your worktree. Treating it as unreviewed until a real gate covers it is exactly right — and telling reviewers explicitly that they may not sign, commit, push or dispatch is the correct application of the receipt-forgery ruling. Keep doing that.

## Sequence unchanged

1. Config symlink escape — refuse, fail loudly, never silently skip.
2. argv[0] → basename.
3. Seed capture + two-runs-identical (present, unreviewed).
4. T7a TTY gate + the uninflated model-card limit (present, unreviewed).
5. diff/veto spec text — mine, already landed.

Then a genuine gate over the whole tip and a receipt reporting **A, B, C and E** explicitly.

Five human artifacts absent. `ratified: false`. Land blocked at precondition 6.
