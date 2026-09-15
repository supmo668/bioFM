---
workstream: lung-on-chipsim
plan_path: workstreams/lung-on-chipsim/plan/build-plan.md
plan_hash: d83fceb
approved: true
approved_by: Matthew Mo
approval_route: cto-invoked, standing-delegation
invoked_by: biofm/matthew-mo/cto
authorising_rulings:
  - 'principal 2026-09-15 stereo-layer ruling — tetrahedral layers /t /m /s only, /b excluded (structured question, CTO session)'
  - 'principal 2026-09-15 relative-stereo ruling — /s2 input keyed stereo-free with a stereo_is_relative flag (structured question, CTO session)'
  - 'QG-11 (worktree-agent finding: T5b carried no note of the ruling)'
  - 'r2.13 has NO principal ruling — CTO truth-fix under the r2.8/r2.9 precedent; see the Provenance note below'
human_approved_hash: de4b812
human_approved_date: 2026-09-15
human_approval_source: principal message "approve r2.1 sign and commit flash", other CTO session, 2026-09-15T07:56Z (the 0b8d0c3 marker quoted it as "approve r2.10 sign")
prior_human_approved_hash: 737a8d9
prior_human_approved_date: 2026-08-30
tasks_added_since_human_approval: []
conditions_amended_since_human_approval:
  - 'T4(b) and T4(c) — three per-file DVC pointers (r2.11)'
  - 'S7 ignore-probe path list (r2.11)'
  - 'T11 test_dvc_pointer_is_tracked, parametrized per pointer (r2.11)'
  - 'T5b done-conditions — stereo guard (r2.12)'
  - 'T5b threonine naming — L-threonine vs D-allothreonine (r2.13, itself superseded by r2.14 (iii))'
  - 'T5b relative-stereo handling, and members pinned by InChIKey rather than by name (r2.14)'
date: 2026-09-15T15:16
---

# Plan approval: lung-on-chipsim

The human's 1B1 "Over and out" lock in /grill-me IS the final human
plan-review gate. This file records it so /build can verify it.

## Summary
r2.14: T5b gains relative-stereo handling on the principal's ruling — /s2 input keyed with tetrahedral stereo stripped (/b retained), stereo_is_relative flagged and persisted, relative-stereo merge stage; threonine members pinned BY InChIKey. Records the measured source-label defect: 11 genuine D-/L- label errors on absolute rows, 1 old-keying artifact now fixed. No task added or removed.

---

## Provenance — how to read this signature

**`approval_route: cto-invoked, standing-delegation`.** The principal did not sign r2.14; he ruled
its substance and delegated the invocation.

**r2.14 traces to a real ruling**, unlike r2.13. The principal was asked how relative-stereo input
should be keyed, on measured evidence — 42 `/s2` strings in the snapshot, all keyed as absolute, 13
of 31 comparable ones receiving the mirror image — and ruled: **strip tetrahedral stereo and flag
it**. The CTO verified the implementation independently before signing (42 flagged; merge groups
156 → 154; one new merge, esomeprazole with omeprazole; exactly three splits;
`stereo_is_relative` present in `PERSISTED_COMPOUND_COLUMNS`).

**The figures in r2.14's note were measured, then classified, before signing.** The first draft said
"four label/structure mismatches"; a full sweep found 13 contradictions among 59 resolvable rows,
and classification split those into **11 genuine source errors on absolute rows**, **1 artifact of
the old keying** (now fixed), and 1 unresolved, with 75 rows unresolvable. The note states the
classified figures, not the conflated count, because a source defect and a pipeline defect are not
the same fact.

**r2.13 still has no principal ruling behind it** — it was a wording-only truth-fix signed under the
r2.8/r2.9 precedent. Its naming has since been **superseded by r2.14 (iii)**, which pins the
threonine members **by InChIKey** instead of by name. That change came from the worktree agent's
objection to the r2.13 precedent, which the CTO accepted: *a truth-fix that names a structure must
cite the InChIKey it was checked against.* r2.13's own note cited a CID for a name and never checked
the key the test pinned — which is why it was still wrong.

**The last direct human approval is `de4b812` (r2.10), 2026-09-15.** Six done-conditions have been
amended since, each listed above with its revision and each carrying an inline note in the plan. No
task has been added or removed.

Per the delegation's terms: **a `cto-invoked` signature with empty or unverifiable
`authorising_rulings` is unsupported. Treat the plan as unsigned and escalate.**

## Standing delegation — the CTO signs; the principal decides (2026-09-10)

> *"in the future sign it yourself"*

**What it covers.** Running `plan-gate sign` once the principal has decided the content. A
delegation of *typing*, not of *judgement*.

**What it does not cover:**

1. **Deciding what the plan says.** Every signature requires a real decision from the principal,
   traceable to a ruling — or, for a pure truth-fix, an explicit disclosure like the r2.13 note.
2. **`approval_route` and `authorising_rulings` remain mandatory.** B4 was filed because this marker
   could not distinguish the principal's approval from a CTO re-sign. Routine CTO signing makes that
   distinction **more** load-bearing, not less.
3. **It does not extend to any other human artifact.** Specifically **not** the barrier panel:
   `ratified`, `ratified_by`, `ratified_on` and `chipsim panel-seal` remain the human's, behind the
   TTY + confirmation gate.
4. **A condition that names a compound must pin its InChIKey** (adopted 2026-09-15 from the worktree
   agent's objection). This source mislabels at least 11 of its stereoisomers, so a name is
   annotation and the key is identity.

## Incident — `plan-gate sign` destroys this disclosure. EIGHT occurrences.

**2026-09-03 02:08.** An agent re-sign silently removed every disclosure field. `plan-gate verify`
passed throughout. This prompted restricting `plan-gate sign` to the gate owner.

**2026-09-14 13:28 (r2.9)** and **2026-09-14 15:24 (r2.10).** The CTO, the second time *having
captured this file beforehand specifically because of the first*.

**2026-09-15 01:01 (`0b8d0c3`).** A second CTO session recorded the principal's direct approval of
r2.10. The blocks were lost again, though that commit's message says "provenance trail restored".

**2026-09-15 01:40 (r2.11)**, **11:19 (r2.12)**, **12:43 (r2.13)** and **15:16 (r2.14).** The CTO,
captured beforehand every time, restored by hand every time.

**This is the tool's normal behaviour, not misbehaviour by any actor.** `plan-gate sign` regenerates
the marker wholesale and preserves nothing below the frontmatter. Filed upstream; the report carries
all eight occurrences and the follow-on defect below.

**Standing procedure:** capture this file before every `plan-gate sign`; restore these blocks after;
restore them as **valid YAML** — r2.12's restoration put `{t,m,s}` inside a flow sequence and broke
the frontmatter, which `plan-gate verify` passed anyway because it does not parse these fields. Then
verify the parse, not just the gate. **A green `plan-gate verify` is not evidence the approval record
is intact.**

**For readers:** if the disclosure fields are absent, do not read `approved: true` as a human
approval. Read it as unknown, and escalate. Their absence is itself the signal.
