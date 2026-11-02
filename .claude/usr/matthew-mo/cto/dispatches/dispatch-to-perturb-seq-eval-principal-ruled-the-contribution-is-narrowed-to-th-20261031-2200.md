---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-10-31T22:00
status: created
priority: high
size: task
subject: "PRINCIPAL RULED: the contribution is NARROWED to the multi-agent case (perturb-seq approvals row 11). Draft the narrowed contribution statement on a staging branch; nothing reaches paper/ until ratified"
in_reply_to: null
---

# PRINCIPAL RULED: the contribution is NARROWED to the multi-agent case (perturb-seq approvals row 11). Draft the narrowed contribution statement on a staging branch; nothing reaches paper/ until ratified

# The framing three-way is ruled: option 2, narrow to the multi-agent case.

Principal, 2026-10-31, verbatim: *"approve to narrow the contribution to multi-agent case"*. Recorded as **perturb-seq-eval approvals row 11** (route: principal).

## What the ruling means
- **Claimed as ours:** a *multi-agent group's* confidence/critique distribution used as an explicit *item-difficulty* signal for allocating test-time compute.
- **Not claimed:** that an internal confidence/vote distribution can steer test-time compute at all. CATTS (`lee2026catts`, arXiv:2602.12276, primary **cs.AI**) does it and reports it working. Say so plainly.
- **Differentiation rests only on** CATTS's stated scope ("we assume a fixed base agent") and its single-model, per-step vote distribution. The #814 limits all still hold: no claim that CATTS fails or underperforms, and nothing about what its authors think of multi-agent methods.
- Rejected alternatives, for your note: (1) keep the framing with a softened claim, and (3) a negative replication reframe.

## What you draft, all marked drafted, all UNRATIFIED
1. The narrowed **contribution statement** (abstract sentence + the intro contribution bullet) for the principal to ratify.
2. A sweep of `paper/`: list every sentence that claims the general case or implies we were first to use confidence for compute allocation, each with its line and a proposed narrowed replacement. **List them. Don't edit `paper/`.**
3. Check (b″) and (b″-D) against the narrowed claim. Keep them if consistent, flag them if not.
4. Title: say whether the current title over-claims under the narrowing. The title fork itself stays with the principal.

## Where it lives — the rule ruled today (CLAUDE.md, lung rows 83-86, applies to every workstream)
Unratified drafts live on a **dedicated `perturb-seq-eval-staging` branch that is never a PR head**. Your two existing drafts (`qa/_adhoc/2026-10-30-paper-framing-drafts.md`, `qa/_adhoc/2026-10-31-catts-full-text-read.md`) are on `origin/perturb-seq-eval`, which has no open PR. **Move them there before you next open a PR from your working branch**, by a normal new commit (no force-push). I mirror the staging ledger to a Notion row for ratification once that branch is pushed.

## Still carrying nothing
The me-only facts from #813 §5: CATTS has no pre-registration or directional hypothesis, the Fisher test, the binned analysis, the Table 3 figures. None of them carries a sentence until one of us has it at the ref. The narrowing makes the pre-registration contrast *more* tempting, which is exactly why the rule holds.

## Noted, not ruled
`arxiv.toml` declares primary `cs.LG`, and the nearest prior art is cs.AI. That's a venue question for the principal. Don't change it. No arXiv submission is on record, so this is a pre-submission change, not a revision.
