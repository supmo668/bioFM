---
workstream: lung-on-chipsim
plan_path: workstreams/lung-on-chipsim/plan/build-plan.md
plan_hash: ebc5542
approved: true
approved_by: Matthew Mo
approval_route: cto-invoked, standing-delegation
invoked_by: biofm/matthew-mo/cto
authorising_rulings:
  - 'principal 2026-09-15 stereo-layer ruling — tetrahedral layers /t /m /s only, /b excluded (structured question, CTO session)'
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
  - 'T5b threonine naming — L-threonine vs D-allothreonine (r2.13)'
date: 2026-09-15T12:43
---

# Plan approval: lung-on-chipsim

The human's 1B1 "Over and out" lock in /grill-me IS the final human
plan-review gate. This file records it so /build can verify it.

## Summary
r2.13: T5b's done-condition corrected to name L-threonine vs D-allothreonine — DrugBank mislabels DB03700 (its structure is byte-identical to PubChem D-allothreonine, CTO-verified). Wording/naming only; guard behaviour and every measured figure unchanged. No task added or removed.

---

## Provenance — how to read this signature

**`approval_route: cto-invoked, standing-delegation`.** The principal did not sign r2.13.

**r2.13 has no principal ruling behind it, and that is a real gap in the disclosure — read this
before trusting the signature.** The delegation's terms require every signature to trace to a
decision the principal made. r2.13 traces instead to a **fact**: DrugBank's `DB03700`, labelled
*D-Threonine*, has a structure byte-identical to PubChem's **D-allothreonine** (CID 90624), while
true D-threonine (CID 69435) matches no snapshot row. The CTO wrote "L-/D-threonine" into r2.12's
done-condition from the agent's naming without checking the label against the structure; the agent
found the error and the CTO verified it against PubChem PUG REST. The correction names the compound
actually tested. It changes no scope, no task, no measured figure and no code behaviour.

This is the **r2.8/r2.9 precedent**: a wording-only, truth-reducing fix, signed under the delegation
without waiting for a ruling, because waiting would leave a knowingly false condition hash-locked.
**A reader who thinks that precedent is wrong should treat r2.13 as unsigned and escalate** — the
point of recording it this way is that the judgement is visible rather than buried.

**The last direct human approval is `de4b812` (r2.10), 2026-09-15**, given in a second CTO session;
the verbatim message is in `human_approval_source`. That approval covers T7a and S12, so
`tasks_added_since_human_approval` is empty. Five done-conditions have been amended since, each
listed with its revision, and each carrying an inline note in the plan.

Per the delegation's terms: **a `cto-invoked` signature with empty or unverifiable
`authorising_rulings` is unsupported. Treat the plan as unsigned and escalate.**

## Standing delegation — the CTO signs; the principal decides (2026-09-10)

> *"in the future sign it yourself"*

**What it covers.** Running `plan-gate sign` once the principal has decided the content. A
delegation of *typing*, not of *judgement*.

**What it does not cover:**

1. **Deciding what the plan says.** Every signature requires a real decision from the principal,
   traceable to a ruling — or, for a pure truth-fix, an explicit disclosure like the r2.13 note
   above.
2. **`approval_route` and `authorising_rulings` remain mandatory.** B4 was filed because this marker
   could not distinguish the principal's approval from a CTO re-sign. Routine CTO signing makes that
   distinction **more** load-bearing, not less. It is the only thing between a delegated
   transcription and a manufactured approval.
3. **It does not extend to any other human artifact.** Specifically **not** the barrier panel:
   `ratified`, `ratified_by`, `ratified_on` and `chipsim panel-seal` remain the human's, behind the
   TTY + confirmation gate. `load_ratified_panel` makes ratification-without-seal a hard failure, so
   the two acts are atomically coupled.

## Incident — `plan-gate sign` destroys this disclosure. SEVEN occurrences.

**2026-09-03 02:08.** An agent re-sign silently removed every disclosure field. `plan-gate verify`
passed throughout. This prompted restricting `plan-gate sign` to the gate owner.

**2026-09-14 13:28 (r2.9)** and **2026-09-14 15:24 (r2.10).** The CTO, the second time *having
captured this file beforehand specifically because of the first*.

**2026-09-15 01:01 (`0b8d0c3`).** A second CTO session recorded the principal's direct approval of
r2.10. The blocks were lost again, though that commit's message says "provenance trail restored".

**2026-09-15 01:40 (r2.11)**, **11:19 (r2.12)** and **12:43 (r2.13).** The CTO, captured beforehand
every time, restored by hand every time.

**This is the tool's normal behaviour, not misbehaviour by any actor.** `plan-gate sign` regenerates
the marker wholesale and preserves nothing below the frontmatter. Filed upstream; the report carries
all seven occurrences.

**Standing procedure:** capture this file before every `plan-gate sign`; restore these blocks after;
restore them as **valid YAML** — r2.12's restoration put `{t,m,s}` inside a flow sequence and broke
the frontmatter, which `plan-gate verify` passed anyway because it does not parse these fields. Then
verify the parse, not just the gate. **A green `plan-gate verify` is not evidence the approval record
is intact.**

**For readers:** if the disclosure fields are absent, do not read `approved: true` as a human
approval. Read it as unknown, and escalate. Their absence is itself the signal.
