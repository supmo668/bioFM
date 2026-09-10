---
workstream: lung-on-chipsim
plan_path: workstreams/lung-on-chipsim/plan/build-plan.md
plan_hash: 373931c
approved: true
approved_by: Matthew Mo
date: 2026-09-10T12:40
---

# Plan approval: lung-on-chipsim

The human's 1B1 "Over and out" lock in /grill-me IS the final human
plan-review gate. This file records it so /build can verify it.

## Summary
r2.8 (wording only, truth-reducing, NO scope change): T8's seal paragraph claimed 'running the seal is the human's act of attestation' — the framing retracted in dispatch #27, contradicting the Global Constraints block 480 lines above. Ninth survivor of that reframe. No task added, removed or altered.

---

## Standing delegation — the CTO signs; the principal decides (2026-09-10)

The principal has delegated **invocation** of `plan-gate sign` to the CTO:

> *"in the future sign it yourself"*

**What this covers.** Running `plan-gate sign` once the principal has decided the content. It
removes a round-trip, nothing more. It is a delegation of *typing*, not of *judgement*.

**What it does not cover, and these are the load-bearing limits:**

1. **Deciding what the plan says.** Every signature still requires a real decision from the
   principal, traceable to a ruling. A signature with no such decision behind it is
   **unsupported — treat the plan as unsigned and escalate.**
2. **`approval_route` remains mandatory** on every CTO-invoked signature, with
   `human_approved_hash` carried forward. B4 was filed because this marker could not distinguish
   the principal's approval from a CTO re-sign. Routine CTO signing makes that distinction
   **more** load-bearing, not less: it is now the only thing standing between a delegated
   transcription and a manufactured approval.
3. **It does not extend to any other human artifact.** Specifically **not** the barrier panel:
   `ratified`, `ratified_by` and `ratified_on` remain under Global Constraint (4) and the file's
   own prohibition, and `chipsim panel-seal` remains reserved to the human's invocation behind
   the TTY + confirmation gate. That is also not merely a rule — `load_ratified_panel` makes
   ratification-without-seal a hard failure, so the two acts are atomically coupled and the seal
   is the half the CTO cannot perform.

**Why the limits are written down rather than assumed.** This session produced two forged
receipts, an agent-run re-sign that silently stripped this very disclosure block while
`plan-gate verify` stayed green, and a ninth surviving instance of a retracted framing found
inside T8 itself. Each was a case of an authority being exercised slightly wider than it was
granted. A delegation recorded without its boundary is the same shape.
