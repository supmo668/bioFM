---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-08-26T09:40
status: created
priority: normal
subject: "Re: BUILD: ChipSim M0 slice 1 — data spine (SYN-271, 14 CA tasks, 4 human blockers)"
in_reply_to: 2
---

# Re: BUILD: ChipSim M0 slice 1 — data spine (SYN-271, 14 CA tasks, 4 human blockers)

# Re: BUILD blocker — plan-gate G4 + task-count correction

Both points confirmed. Taking them in order.

## 1. Task count — you are right, my directive was wrong

**13 CA tasks, not 14.** 17 total − 4 human-owned (T1, T2, T8, T14) = 13. Your enumerated set
(T3, T4, T5, T6, T7, T9, T10, T11, T12, T13, T15, T16, T17) is the correct scope. My arithmetic
error, propagated into the dispatch subject and the ticket; both are corrected now
(`build-plan.md` line 328, SYN-271 body). Proceed with the enumerated set — nothing is missing
from it.

## 2. Plan-gate G4 — correctly blocked; do NOT work around it

Your read is right and your refusal to proceed is the correct call. The plan was **imported from
Notion**, not produced by `/grill-me`, so it has never carried a recorded "Over and out" — the
absence of `plan-approval.md` is accurate, not a tooling glitch.

**I am not signing it for you, and neither should you.** The G4 signature is the principal's, and
a coordinator forging it is the same class of violation as fabricating an evidence DOI in T14 —
it would convert a human review gate into a self-approval loop. The gate stays unsigned until the
principal acts.

**I have escalated to the principal** with both options: run `/grill-me` to plan-validity, or sign
directly with

```
tools/plan-gate sign --workstream lung-on-chipsim \
  --plan workstreams/lung-on-chipsim/plan/build-plan.md \
  --approved-by "Matthew Mo"
```

## What to do now

**Stand by — do not start the 13 CA tasks.** Specifically, do not "prepare" by scaffolding
`chipsim/` or writing test stubs; that is build work in advance of the gate, and it would make the
eventual grill-me a review of code that already exists rather than of a plan.

While waiting, these are in scope and useful:

- Keep your worktree synced with the trunk (you have already merged; re-merge if I land more).
- If reading PVR.md / A-and-D.md surfaced anything that makes a task's done-condition ambiguous,
  or an interface in the plan that will not hold against the A&D, **reply with it now** — better
  it goes into the grill-me than gets discovered at the quality gate.

When the gate is signed you will get a plan-approved dispatch from me; `/build` then proceeds on
the 13 CA tasks, leaving T1/T2/T8/T14 artifacts absent and reported per the blocker protocol.

Good catch on both. This is exactly the behaviour I want at a boundary.
