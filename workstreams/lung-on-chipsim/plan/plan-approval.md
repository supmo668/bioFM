---
workstream: lung-on-chipsim
plan_path: workstreams/lung-on-chipsim/plan/build-plan.md
plan_hash: de4b812
approved: true
approved_by: Matthew Mo
approval_route: cto-initiated, standing-delegation
invoked_by: biofm/matthew-mo/cto
authorising_rulings: [dispatch #27 (seal reframe), principal 2026-09-12 "proceed" on the C4 uv-run fix, principal 2026-09-14 ruling on the organism label]
human_approved_hash: 737a8d9
human_approved_date: 2026-08-30
tasks_added_since_human_g4: [T7a, S12]
date: 2026-09-14T15:24
---

# Plan approval: lung-on-chipsim

The human's 1B1 "Over and out" lock in /grill-me IS the final human
plan-review gate. This file records it so /build can verify it.

## Summary
r2.10 (defect fix, NO scope change) — CTO-invoked under the standing delegation, on the principal's explicit ruling of 2026-09-14. T4's edge loader specified organism == 'Homo sapiens'. The pinned 2015 snapshot carries 16,299 rows saying 'Human' and ZERO saying 'Homo sapiens' (verified against the fetched TSV), so the loader as specified returned an EMPTY FRAME on the only data the study is permitted to use. Every fixture said 'Homo sapiens', so no test could have caught it. Principal ruled: accept BOTH labels rather than swapping — the fixtures are legitimately 'Homo sapiens' and preferring either silently would leave the next reader unable to tell which vocabulary the code trusts. Defect class: a done-condition evaluated against a fixture that does not share the real snapshot's vocabulary. No task added, removed or altered.

---

## Provenance — how to read this signature

**`approval_route: cto-initiated, standing-delegation` is NOT `principal-directed, cto-invoked`.**
The principal did not author this text. He delegated *invocation*; each signature exercises that
delegation only on corrections implementing rulings he already made, listed in
`authorising_rulings`.

**r2.10 was held back until he ruled.** The organism correction was drafted, the gate left blocked,
and the signature withheld — because accepting *both* labels rather than swapping to `Human` is a
judgement, not a typo fix, and the delegation's own terms forbid signing without a traceable
decision. He ruled on 2026-09-14; the signature followed.

Per those terms: **a signature with no traceable decision behind it is unsupported — treat the plan
as unsigned and escalate.** A future `cto-initiated` signature with empty or unverifiable
`authorising_rulings` should be treated as unsigned.

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

## Incident — `plan-gate sign` destroys this disclosure. THREE occurrences.

**2026-09-03 02:08** — an agent re-sign silently removed every disclosure field. `plan-gate verify`
passed throughout; the hash never moved, so the gate could not see it. This prompted restricting
`plan-gate sign` to the gate owner.

**2026-09-14 13:28** — happened again, to the CTO, signing r2.9.

**2026-09-14 (r2.10)** — happened a third time, to the CTO, *having captured this file beforehand
specifically because of the first two*.

**This is the tool's normal behaviour, not misbehaviour by any actor.** `plan-gate sign` regenerates
the marker wholesale and preserves nothing below the frontmatter. Restricting *who* may invoke it
does not address it. Filed upstream.

**Standing procedure:** capture this file before every `plan-gate sign`; restore these blocks after;
verify the restoration. **A green `plan-gate verify` is not evidence the approval record is intact**
— the gate binds the *plan*, not the *marker*.

**For readers:** if the disclosure fields are absent, do not read `approved: true` as a human
approval. Read it as unknown, and escalate. Their absence is itself the signal.
