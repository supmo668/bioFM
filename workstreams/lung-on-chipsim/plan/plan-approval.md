---
workstream: lung-on-chipsim
plan_path: workstreams/lung-on-chipsim/plan/build-plan.md
plan_hash: 16b0cc9
approved: true
approved_by: Matthew Mo
approval_route: cto-invoked, standing-delegation
invoked_by: biofm/matthew-mo/cto
authorising_rulings:
  - 'principal 2026-09-15 stereo-layer ruling — tetrahedral layers /t /m /s only, /b excluded (structured question, CTO session)'
  - 'QG-11 (worktree-agent finding: T5b carried no note of the ruling)'
human_approved_hash: de4b812
human_approved_date: 2026-09-15
human_approval_source: principal message "approve r2.1 sign and commit flash", other CTO session, 2026-09-15T07:56Z (the 0b8d0c3 marker quoted it as "approve r2.10 sign")
prior_human_approved_hash: 737a8d9
prior_human_approved_date: 2026-08-30
tasks_added_since_human_approval: []
conditions_amended_since_human_approval: [T4(b), T4(c), S7 ignore-probe path list, T11 test_dvc_pointer_is_tracked, T5b done-conditions (r2.12)]
date: 2026-09-15T11:19
---

# Plan approval: lung-on-chipsim

The human's 1B1 "Over and out" lock in /grill-me IS the final human
plan-review gate. This file records it so /build can verify it.

## Summary
r2.12: T5b gains the stereo-guard ruling ({t,m,s}, /b excluded) as an inline note plus three done-conditions (L/D-Thr distinct, benzimidazole merged, malate split asserted). Principal ruling 2026-09-15. QG-11. No task added or removed.

---

## Provenance — how to read this signature

**`approval_route: cto-invoked, standing-delegation`.** The principal did not sign r2.12 directly. He
ruled its content — the guard compares `/t`, `/m`, `/s` and not `/b` — and delegated the invocation.
The ruling was made on a measured per-layer table, after the CTO's first reading of "stereo" (four
layers, including `/b`) was refuted by that measurement.

**The last direct human approval is `de4b812` (r2.10), 2026-09-15**, given in a second CTO session;
the verbatim message is in `human_approval_source`, including the "r2.1" typo, which the context
makes unambiguous. That approval covers T7a and S12, so `tasks_added_since_human_approval` is empty.

**What has changed since that approval** is listed in `conditions_amended_since_human_approval`. No
task added or removed; five done-conditions/probes amended across r2.11 and r2.12, each tracing to a
ruling. The inline notes under T4 and T5b carry the reasoning.

Per the delegation's terms: **a `cto-invoked` signature with empty or unverifiable
`authorising_rulings` is unsupported. Treat the plan as unsigned and escalate.**

## Standing delegation — the CTO signs; the principal decides (2026-09-10)

> *"in the future sign it yourself"*

**What it covers.** Running `plan-gate sign` once the principal has decided the content. A
delegation of *typing*, not of *judgement*.

**What it does not cover:**

1. **Deciding what the plan says.** Every signature requires a real decision from the principal,
   traceable to a ruling.
2. **`approval_route` and `authorising_rulings` remain mandatory.** B4 was filed because this marker
   could not distinguish the principal's approval from a CTO re-sign. Routine CTO signing makes that
   distinction **more** load-bearing, not less. It is the only thing between a delegated
   transcription and a manufactured approval.
3. **It does not extend to any other human artifact.** Specifically **not** the barrier panel:
   `ratified`, `ratified_by`, `ratified_on` and `chipsim panel-seal` remain the human's, behind the
   TTY + confirmation gate. `load_ratified_panel` makes ratification-without-seal a hard failure, so
   the two acts are atomically coupled.

## Incident — `plan-gate sign` destroys this disclosure. SIX occurrences.

**2026-09-03 02:08.** An agent re-sign silently removed every disclosure field. `plan-gate verify`
passed throughout. This prompted restricting `plan-gate sign` to the gate owner.

**2026-09-14 13:28 (r2.9)** and **2026-09-14 15:24 (r2.10).** The CTO, the second time *having
captured this file beforehand specifically because of the first*.

**2026-09-15 01:01 (`0b8d0c3`).** A second CTO session recorded the principal's direct approval of
r2.10. The blocks were lost again, though that commit's message says "provenance trail restored".

**2026-09-15 01:40 (r2.11)** and **2026-09-15 11:19 (r2.12).** The CTO, captured beforehand both
times, restored by hand both times.

**This is the tool's normal behaviour, not misbehaviour by any actor.** `plan-gate sign` regenerates
the marker wholesale and preserves nothing below the frontmatter. Filed upstream; the report now
carries all six occurrences.

**Standing procedure:** capture this file before every `plan-gate sign`; restore these blocks after;
verify the restoration. **A green `plan-gate verify` is not evidence the approval record is intact.**
The gate binds the *plan*, not the *marker*.

**For readers:** if the disclosure fields are absent, do not read `approved: true` as a human
approval. Read it as unknown, and escalate. Their absence is itself the signal.
