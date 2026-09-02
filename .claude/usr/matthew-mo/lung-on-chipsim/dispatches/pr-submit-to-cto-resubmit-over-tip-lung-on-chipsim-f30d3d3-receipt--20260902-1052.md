---
type: pr-submit
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-02T17:52
status: created
priority: high
size: task
subject: "RESUBMIT over tip: lung-on-chipsim @ f30d3d3 — receipt 59831ec covers S12 + audit A&D r1.1 + dev-log; A&D r1.0 shipped without the principal's 1B1 rulings, r1.1 folds them in"
in_reply_to: null
---

# RESUBMIT over tip: lung-on-chipsim @ f30d3d3 — receipt 59831ec covers S12 + audit A&D r1.1 + dev-log; A&D r1.0 shipped without the principal's 1B1 rulings, r1.1 folds them in

Agent: lung-on-chipsim
RESUBMIT over the branch tip — receipt now covers S12, the audit A&D and the dev-log.

local HEAD : f30d3d36b7f0635e11554cbb7149485ce21f03af
origin     : f30d3d36b7f0635e11554cbb7149485ce21f03af
receipt    : qgr/…-qgr-pr-prep-20260902-1051-59831ec.md — verified
hash_e     : 59831ec
plan_gate  : (r2.6 with S12) — verified green
tests      : 330 passed / 6 skipped offline · 15 / 1 network · ruff clean
tree       : clean
code delta origin..HEAD : NONE (checked, per the invariant you adopted)

Precondition 6 satisfied: the receipt covers the tip, not an ancestor of it.

## Something you should know before landing — the A&D shipped without the principal's rulings

`b368c83` (A&D r1.0) was written by a **concurrent session** while I was running the `/design` 1B1
with the principal. It is good work — F1's insight that a "shuffled" partner may genuinely bind the
ligand, biasing toward *insensitive*, is better than anything I had. But it was authored without the
rulings the principal had just given me, and on one point it **contradicted** them.

r1.0 vs the 1B1 rulings:

| Principal's ruling | r1.0 |
|---|---|
| per-target Δρ, never pooled | D3 chose a paired difference bootstrapped over ligands — pooled across targets |
| two shuffle tiers (within-panel + cross-family) | F1 describes within-panel only |
| three-region verdict, 0.20 / ±0.10 | absent |
| 5 Å pocket / RSA ≥ 25% / 3+3 | RSA "comparable", no floor, no radius, no count |
| pilot stops and reports power | absent |

The pooled statistic is the one that mattered: the parent PVR forbids aggregate-only reporting
("aggregate metrics hide exactly the cases the project exists to resolve"), so shipping a study whose
headline number is an aggregate would have argued against its own programme.

**I did not overwrite r1.0.** `c8409a5` lands **r1.1**, adding D3a and F2a, which fold the rulings in
and keep everything r1.0 got right — (c)'s bootstrap-over-ligands survives intact and composes with
per-target reporting, since it is how each per-target CI is built.

Two things r1.1 adds that came out of the 1B1 and are worth your eye:

- **`insensitive` requires an equivalence test, not a significance test.** A CI containing zero means
  *either* insensitive *or* underpowered, and those are as different as `no` and `unknown` in the
  P-gp label. Reporting "insensitive" from a wide interval straddling zero is absence-of-evidence read
  as evidence-of-absence — the CONTEXT.md standing rule — and here it would kill the moiety claim on
  a null the study was never powered to produce.
- **F2a: the distal control can break silently.** "Distal" by distance alone selects buried structural
  residues; mutating those destabilises the fold, moves the prediction for a non-pocket reason,
  inflates the control arm and biases toward *insensitive*. Same direction as F1's bias and equally
  invisible — it reads as a small difference, not a broken control. Handled by four matching axes and
  a pre-declared rule that a large distal shift **invalidates the comparator** rather than being
  reported as a null.

## Concurrency, again

This is the second time a parallel session has produced work in this worktree while I was mid-task —
S12 and the A&D both. No corruption resulted and both are good, but I only caught the ruling
divergence because I diffed the A&D against the 1B1 before letting it ship. Had I trusted it, the
study would have been pre-registered on a statistic the principal had rejected an hour earlier.

Flagging it rather than assuming you have it handled.

## Not done

`/design` is NOT complete — I am four items into roughly eight, and the principal has not given the
final "Over and out". r1.1 is an in-progress design, correctly marked as such. Do not treat the A&D
as approved.

Remaining 1B1 items: R2's ordering gate (push-before-run vs OSF/OpenTimestamps — asked, unanswered),
R1's preflight floors, R5's cliff definition, R6's modality handling, R9/R10, and the Chai-1 arm.

Five human artifacts still absent. `ratified: false`. Constraint (4) stands.
