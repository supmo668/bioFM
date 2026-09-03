---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-08-31T18:13
status: created
priority: high
size: task
subject: "Plan-gate RE-SIGNED at b79a5e4 — merge trunk; do not amend build-plan.md unilaterally"
in_reply_to: null
---

# Plan-gate RE-SIGNED at b79a5e4 — merge trunk; do not amend build-plan.md unilaterally

# Plan-gate RE-SIGNED at b79a5e4 — my error, fixed. Merge trunk before your next gate check.

E-4 and E-5 both verified applied on your branch — DVC remote now resolves to
`/Users/mo/.aiadlc/biofm/dvc-storage`, outside every git tree, and `test_scaffold.py` carries the
nested probes. Good.

## What I got wrong

I told you to amend `build-plan.md` (S9 wording, E-1…E-4 corrections) **while it was hash-locked to
the G4 signature.** That is precisely the trap you reported to me one iteration earlier as framework
friction — appending to the plan breaks `plan-gate` — and I walked us straight into it by
instructing an amendment without re-signing. Your branch's plan no longer matched `737a8d9`, so your
next `plan-gate verify` would have exited 2 and blocked `/build`, through no fault of yours.

## Fixed

r2.1 landed on trunk at `1f43759` and **re-signed: `plan-gate verify` now exits 0 at `b79a5e4`.**

Before re-signing I verified the amendments carry **no scope change** — 34 task headings on both
sides, identical task set, human-blocker count unchanged at five. The principal's approval covers
the plan's substance, and its substance did not move; only defect corrections I ruled did.

**Merge trunk before your next gate check** so your branch and the signature agree.

## Standing rule from here

`build-plan.md` is hash-locked. **Do not amend it on your own initiative.** If a ruling of mine
requires a plan amendment, make the change and say so in your next dispatch — I land it on trunk and
re-sign in the same move, so the signature always attaches to the plan actually being built. Never
let the two diverge, and never work around a red gate by editing the plan back.

Continue: T4a, T4, T5, T5a, T5b, T6, T7, T9, T10, T11, T12, T13, T15, T16, T17, T19, S11a against
committed fixtures. Five human artifacts stay absent.
