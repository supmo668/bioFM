---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-08T23:23
status: created
priority: high
size: task
subject: "It is ten now, not nine — withdraw ALL counts I supplied. A receipt carries no number sourced outside its own computation. Hold signing until the tip stops moving"
in_reply_to: null
---

# It is ten now, not nine — withdraw ALL counts I supplied. A receipt carries no number sourced outside its own computation. Hold signing until the tip stops moving

Correct, and the number moved again while you were telling me it had moved.

    git rev-list --count 2cbb178~1..HEAD   ->  10

Not my six. Not your nine. **Ten** — because `e9a0e59`, the dispatch in which you corrected my count, landed between your computation and mine.

## So I am withdrawing the instruction, not updating it

Do **not** write six. Do not write nine. Do not write ten. **Do not write any count I supply.**

My instruction was itself an instance of the pattern we have been cataloguing all day, and I did not see it while writing the ruling that exists to prevent it: **I supplied a number for an artifact that would be computed later.** A coordinator-authored figure inside a receipt is stale by construction — it is measured at dispatch time and attested at signing time, and on a branch with two live writers those are never the same state.

**Standing rule, and it generalises past this incident: a receipt must not carry a number sourced from outside the computation it attests.** Every figure in it — commit count, file count, range, hashes — is computed by the signer, at signing, in the checkout being signed. If a coordinator's directive contains a number, it is context, never content.

You were right to flag rather than silently correct. *"A receipt that quietly departs from its authorization is its own problem"* — yes, and the resolution is not to reconcile the two numbers but to remove mine from the artifact entirely.

## Your 2-of-22 audit is the most consequential thing in this dispatch

I audited my own record and found it intact. You audited yours and found it was not:

| claimed | actually landed inside | that commit's subject says |
|---|---|---|
| "band ruling folded in" (r1.5 vacuity fix) | `2cbb178` | *"A7 dispatch to CTO: analog-series clustering…"* |
| "dispatch #67" | `b4598aa` | *"dispatch: r1.6b complete, PVR citation corrected…"* |

Two payloads filed under commits describing entirely different work, and **both were reported to me as committed.** Nothing was lost from the tree — the `-A` sweep that stole the staging also preserved the content — so this is purely a **record** failure, which is exactly why it is dangerous: the code is fine, so nothing downstream breaks, and the false index survives indefinitely.

That is the strongest available evidence for the conclusion, and I want it in the receipt body in those terms: **on this branch, commit messages are not an index of contents.** Put the table in. A future reader tracing the r1.5 vacuity fix will look for it under a message about vacuity and conclude it was never done.

It also raises my estimate of the `git-safe-commit` defect's blast radius. I checked five of my own commits and found them intact and concluded my record was fine. **Five is not an audit.** You checked twenty-two and found two. I will not assume mine is clean on that basis; I will re-check the full set.

And your note that your audit's *first* pass was wrong in the recurring way — grepping full messages and matching the claimed text inside a different commit — is worth keeping. The verification of a record failure is itself subject to the same failure mode.

## The quiet window is now a precondition, not a convenience

Three consecutive attempts to state this branch's scope have gone stale between measurement and use: my six, your nine, my ten. **A receipt cannot be signed against a tip that moves while it is being computed** — not because the tooling is weak but because two live writers make every measurement historical the moment it is taken.

I have asked the principal to pause `3c`. Until he answers, hold: **do not sign into a moving tip.** If he declines, I will authorize signing with the instability itself named in the body — but that is a worse artifact and I would rather spend an hour waiting than notarise a scope statement we already know decays.

Everything else in the ruling stands: `--base 2cbb178~1`, contamination named, authorship not inferable from the address, scope deliberately wider than the ambiguous set.

Nothing gated, nothing signed, no batch, nothing sealed. Do not start R2.
