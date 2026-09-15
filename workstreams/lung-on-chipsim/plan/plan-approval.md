---
workstream: lung-on-chipsim
plan_path: workstreams/lung-on-chipsim/plan/build-plan.md
plan_hash: 26b7a4f
approved: true
approved_by: Matthew Mo
approval_route: cto-invoked, standing-delegation
invoked_by: biofm/matthew-mo/cto
authorising_rulings: [principal 2026-09-15 ruling "Amend (b)/(c) to three per-file pointers" (CTO session, structured question)]
human_approved_hash: de4b812
human_approved_date: 2026-09-15
human_approval_source: principal message "approve r2.1 sign and commit flash", other CTO session, 2026-09-15T07:56Z (the 0b8d0c3 marker quoted it as "approve r2.10 sign")
prior_human_approved_hash: 737a8d9
prior_human_approved_date: 2026-08-30
tasks_added_since_human_approval: []
conditions_amended_since_human_approval: [T4(b), T4(c), S7 ignore-probe path list, T11 test_dvc_pointer_is_tracked]
date: 2026-09-15T01:40
---

# Plan approval: lung-on-chipsim

The human's 1B1 "Over and out" lock in /grill-me IS the final human
plan-review gate. This file records it so /build can verify it.

## Summary
r2.11: T4(b)/(c) amended to three per-file DVC pointers (a directory pointer is unsatisfiable while git-tracked files live inside it); S7 probe and T11 test follow. Principal ruling 2026-09-15. No task added or removed.

---

## Provenance — how to read this signature

**`approval_route: cto-invoked, standing-delegation`.** The principal did not sign r2.11 directly.
He ruled on its content — one DVC pointer per TSV — and delegated the invocation.

**The last direct human approval is `de4b812` (r2.10), 2026-09-15.** It was given in a second CTO
session. The verbatim message is recorded in `human_approval_source`, including the "r2.1" typo, which
the context makes unambiguous: that session had just reported the r2.10 sign as pending. That
approval covers T7a and S12, so `tasks_added_since_human_approval` is now empty.

**What changed since that approval** is listed in `conditions_amended_since_human_approval`: no
task added or removed, and four done-conditions/probes changed to track the new pointer paths. The
r2.11 note under T4 in the plan explains why the signed condition was unsatisfiable.

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
   TTY + confirmation gate. `load_ratified_panel` makes ratification-without-seal a hard failure,
   so the two acts are atomically coupled.

## Incident — `plan-gate sign` destroys this disclosure. FIVE occurrences.

**2026-09-03 02:08.** An agent re-sign silently removed every disclosure field. `plan-gate verify`
passed throughout. This prompted restricting `plan-gate sign` to the gate owner.

**2026-09-14 13:28 (r2.9)** and **2026-09-14 15:24 (r2.10).** The CTO, the second time *having
captured this file beforehand specifically because of the first*.

**2026-09-15 01:01 (`0b8d0c3`).** A second CTO session recorded the principal's direct approval of
r2.10. The blocks were lost again, though that commit's message says "provenance trail restored".

**2026-09-15 01:40 (r2.11).** The CTO, captured beforehand, restored here.

**This is the tool's normal behaviour, not misbehaviour by any actor.** `plan-gate sign` regenerates
the marker wholesale and preserves nothing below the frontmatter. Filed upstream.

**Standing procedure:** capture this file before every `plan-gate sign`; restore these blocks after;
verify the restoration. **A green `plan-gate verify` is not evidence the approval record is intact.**
The gate binds the *plan*, not the *marker*.

**For readers:** if the disclosure fields are absent, do not read `approved: true` as a human
approval. Read it as unknown, and escalate. Their absence is itself the signal.
