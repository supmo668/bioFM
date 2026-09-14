---
workstream: lung-on-chipsim
plan_path: workstreams/lung-on-chipsim/plan/build-plan.md
plan_hash: db3d10b
approved: true
approved_by: Matthew Mo
approval_route: cto-initiated, standing-delegation
invoked_by: biofm/matthew-mo/cto
authorising_rulings: [dispatch #27 (seal reframe), principal 2026-09-12 "proceed" on the C4 uv-run fix]
human_approved_hash: 737a8d9
human_approved_date: 2026-08-30
tasks_added_since_human_g4: [T7a, S12]
date: 2026-09-14T13:28
---

# Plan approval: lung-on-chipsim

The human's 1B1 "Over and out" lock in /grill-me IS the final human
plan-review gate. This file records it so /build can verify it.

## Summary
r2.9 (wording only, truth-reducing, NO scope change) — CTO-INITIATED under the standing delegation; the principal did not author or review this text. Two corrections, each implementing a ruling he already made. (1) TENTH survivor of the dispatch-#27 reframe, at build-plan:503 — 'the seal is the act of attestation', the exact retracted claim, missed for two weeks because the phrase is SPLIT ACROSS A HARD LINE BREAK and line-oriented grep cannot see wrapped phrases. Found by a wrap-aware sweep. (2) C4 recurrence: T8's documented command is now 'uv run chipsim panel-seal' from projects/lung-on-chipsim — the bare form fails with 'command not found' because chipsim is a console script inside the project venv, which the principal hit on 2026-09-12. No task added, removed or altered.

---

## Provenance — how to read this signature

**`approval_route: cto-initiated, standing-delegation` is NOT the same as `principal-directed,
cto-invoked`, and the difference is the point.** The principal neither authored nor reviewed the
r2.9 text. He delegated *invocation*; this signature exercises that delegation on two corrections
that each implement a ruling he had already made — dispatch #27's retraction, and his "proceed" on
the C4 `uv run` fix he personally hit. Both are listed in `authorising_rulings`.

Per the delegation's own terms: **a signature with no traceable decision behind it is unsupported —
treat the plan as unsigned and escalate.** These two are traceable. A future `cto-initiated`
signature whose `authorising_rulings` are empty or unverifiable should be treated as unsigned.

`human_approved_hash: 737a8d9` remains the only plan the principal approved *directly*, at G4 on
2026-08-30. `T7a` and `S12` entered after it and were ratified by him on 2026-09-02.

## Standing delegation — the CTO signs; the principal decides (2026-09-10)

> *"in the future sign it yourself"*

**What it covers.** Running `plan-gate sign` once the principal has decided the content. A
delegation of *typing*, not of *judgement*.

**What it does not cover:**

1. **Deciding what the plan says.** Every signature requires a real decision from the principal,
   traceable to a ruling.
2. **`approval_route` and `authorising_rulings` remain mandatory.** B4 was filed because this marker
   could not distinguish the principal's approval from a CTO re-sign. Routine CTO signing makes that
   distinction **more** load-bearing, not less — it is the only thing between a delegated
   transcription and a manufactured approval.
3. **It does not extend to any other human artifact.** Specifically **not** the barrier panel:
   `ratified`, `ratified_by`, `ratified_on` and `chipsim panel-seal` remain the human's, behind the
   TTY + confirmation gate. That is not merely a rule — `load_ratified_panel` makes
   ratification-without-seal a hard failure, so the two acts are atomically coupled.

## Incident — `plan-gate sign` strips this disclosure, CONFIRMED TWICE

**2026-09-03, 02:08.** An agent-run re-sign rewrote this marker and silently removed every
disclosure field. `plan-gate verify` passed before, during and after — the hash never moved, so the
gate could not see it. That is why `plan-gate sign` was restricted to the gate owner.

**2026-09-14, 13:28 — it happened again, to the CTO.** Signing r2.9 stripped all four blocks a
second time. **This is not an incident, it is the tool's normal behaviour:** `plan-gate sign`
regenerates the marker wholesale and preserves nothing below the frontmatter.

**Standing consequence.** Anyone invoking `plan-gate sign` on this workstream must capture this file
first and restore these blocks afterwards, and verify the restoration. **A green
`plan-gate verify` is not evidence the approval record is intact** — the gate binds the *plan*, not
the *marker*. Filed upstream.

**For readers:** if the disclosure fields are absent, do not read `approved: true` as a human
approval. Read it as unknown, and escalate. Their absence is itself a signal.
