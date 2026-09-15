---
workstream: lung-on-chipsim
plan_path: workstreams/lung-on-chipsim/plan/build-plan.md
plan_hash: 67a1897
approved: true
approved_by: Matthew Mo
approval_route: cto-invoked, standing-delegation
invoked_by: biofm/matthew-mo/cto
provenance_of_record: workstreams/lung-on-chipsim/plan/plan-approval-log.md
authorising_rulings:
  - 'principal 2026-09-15 structured grill (session biofm-14) — nine decisions; items 2,5,6,7,8,9 folded as ruled, item 3 folded as principle with its application recorded VOID'
  - 'principal 2026-09-15 PROVENANCE ruling — human-authored only; the grill item 1 proposal (CTO drafts, principal ratifies) was put with both readings stated and DECLINED'
  - 'principal 2026-09-15 lane ruling — this CTO session keeps the lung-on-chipsim lane; #127 and its close instruction are void'
  - 'principal 2026-09-15 stereo-layer ruling — tetrahedral layers /t /m /s only, /b excluded'
  - 'principal 2026-09-15 relative-stereo ruling — /s2 input keyed stereo-free with a stereo_is_relative flag'
  - 'QG-11 (worktree-agent finding: T5b carried no note of the ruling)'
  - 'r2.13 has NO principal ruling — CTO truth-fix under the r2.8/r2.9 precedent; superseded by r2.14 (iii)'
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
  - 'T5b threonine naming — L-threonine vs D-allothreonine (r2.13, superseded by r2.14 (iii))'
  - 'T5b relative-stereo handling, and members pinned by InChIKey rather than by name (r2.14)'
  - 'Global Constraints — one interactive session per tree; approval provenance in an append-only log with a gate check (r2.15)'
  - 'Constraint 4 — panel signing decided: minisign at the M1 re-ratification (r2.15)'
  - 'T18/T14 — hand-off on guarded keys, and the principal authoring window (r2.15)'
  - 'AM-6 pointer — resolved by ADR-0002, arithmetic re-checked at M0b (r2.15, editorial)'
date: 2026-09-15T16:15
---

# Plan approval: lung-on-chipsim

The human's 1B1 "Over and out" lock in /grill-me IS the final human
plan-review gate. This file records it so /build can verify it.

## Summary
r2.15: folds the principal's 2026-09-15 grill — minisign at M1 re-ratification (Constraint 4 decided), append-only plan-approval-log as the approval provenance with a gate check, one-interactive-session-per-tree as a Global Constraint with its 2026-09-15 application recorded VOID, T18/T14 hand-off milestone and authoring window, AM-6 editorial. PROVENANCE.md stays human-authored: the grill's CTO-drafts proposal was put to the principal and declined. No task added or removed.

---

## THIS FILE IS NO LONGER THE PROVENANCE OF RECORD

**`plan-approval-log.md` beside it is** (r2.15 item 6). `plan-gate sign` regenerates this file
wholesale on every sign and preserves nothing below the frontmatter — **nine times so far**. The log
is append-only, lives outside what the tool rewrites, and the quality gate fails when its newest
entry's hash differs from `plan_hash` above. If this section is missing, read the log and escalate.

## Provenance — how to read this signature

**`approval_route: cto-invoked, standing-delegation`.** The principal did not sign r2.15; he made
the decisions it folds, in a structured grill held in another session, and delegated invocation.

**What r2.15 folds, and one thing it declines.** Items 2, 5, 6, 7, 8 and 9 are folded as ruled.
**Item 1 is declined**: the grill proposed that the CTO draft `PROVENANCE.md` under the T8 pattern,
reasoning that the licence decision was already the principal's and recorded verbatim in
`provenance.yaml`. That proposal was put back to him with both readings stated, and he chose
**human-only**. The argument is preserved in the plan under T1 so a later reader sees it was
considered, not overlooked; the CTO-drafted draft was removed at `6557487`.

**Item 3 is folded as a principle with its application recorded VOID.** The rule — one interactive
session per tree, and a second session *is* the signing hold — is sound and kept. Its 2026-09-15
resolution directed closing pid `56186` (the worktree's sole writer) and pid `51059` (this session),
on a premise that each tree held a second bare session. Verified by `ps` and `ListAgents`: it did
not. The principal then ruled this session keeps the lane. **A constraint phrased as "close pid X"
inherits whatever the premise about X got wrong** — which is why identity claims in this workstream
must now cite the check that produced them.

**The last direct human approval is `de4b812` (r2.10), 2026-09-15.** Ten done-conditions and
constraints have been amended since, each listed above with its revision and each carrying an inline
note in the plan. No task has been added or removed since the human-direct sign.

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
   could not distinguish the principal's approval from a CTO re-sign.
3. **It does not extend to any other human artifact.** Not the barrier panel (`ratified`,
   `ratified_by`, `ratified_on`, `chipsim panel-seal`), and **not `PROVENANCE.md`**, which r2.15
   confirms is human-authored.
4. **A condition that names a compound must pin its InChIKey** (adopted 2026-09-15). This source
   mislabels at least 11 of its stereoisomers, so a name is annotation and the key is identity.
5. **A claim about session identity must cite the check that produced it** (adopted 2026-09-15,
   from the worktree agent's `ps` correction and the void resolution above).

## Incident — `plan-gate sign` destroys this disclosure. NINE occurrences.

**2026-09-03 02:08** (agent re-sign) · **2026-09-14 13:28 (r2.9)** · **2026-09-14 15:24 (r2.10)** ·
**2026-09-15 01:01 (`0b8d0c3`, second CTO session)** · **2026-09-15 01:40 (r2.11)** ·
**11:19 (r2.12)** · **12:43 (r2.13)** · **15:16 (r2.14)** · **16:15 (r2.15)**.

`plan-gate verify` passed throughout every one of them: the gate binds the *plan*, not the *marker*.

**This is the tool's normal behaviour, not misbehaviour by any actor.** Filed upstream, with the
follow-on defect that hand-restored frontmatter is unvalidated — r2.12's restoration put `{t,m,s}`
inside a flow sequence, producing invalid YAML that `plan-gate verify` accepted.

**Standing procedure:** capture before every sign; restore after; restore as **valid YAML**; verify
the parse, not just the gate; **append the log entry**. r2.15 makes the log the provenance of record
precisely so that a tenth wipe costs nothing.

**For readers:** if the disclosure fields are absent, do not read `approved: true` as a human
approval. Read it as unknown, check the log, and escalate.
