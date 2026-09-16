---
workstream: lung-on-chipsim
plan_path: workstreams/lung-on-chipsim/plan/build-plan.md
plan_hash: 0745f2f
approved: true
approved_by: Matthew Mo
approval_route: cto-invoked, standing-delegation
invoked_by: biofm/matthew-mo/cto
provenance_of_record: workstreams/lung-on-chipsim/plan/plan-approval-log.md
authorising_rulings:
  - 'CTO ruling 2026-09-16 on QG finding F-05 — the tracked adjudication file drops `name`; the untracked worksheet keeps it. Implements the principal''s 2026-09-15 record-content re-ruling.'
  - 'principal 2026-09-15 record-content re-ruling — the invariant targets record content and the (accession, name, structure) association, not canonical identifiers'
  - 'CTO ruling 2026-09-16 on #131 — accessions out of the plan (r2.16)'
  - 'principal 2026-09-15 lane ruling, re-confirmed 2026-09-16 — this CTO session owns the lung-on-chipsim lane'
  - 'r2.17 T13/T15 interface amendments have NO principal ruling — they correct interfaces that had drifted from shipped code; truth-fix under the r2.8/r2.9 precedent'
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
  - 'r2.16 — wording and figures only: accessions out of the r2.13 note; r2.12''s figures marked guard-only with merge_report.json as the source of record'
  - 'T14 done-condition — the tracked file carries NO `name` column (r2.17). A real condition change, not wording.'
  - 'T13/T15 interfaces — generated columns, tri-state label_disagrees_with_key, T15 legacy raise (r2.17, correcting drift from shipped code)'
date: 2026-09-16T15:00
---

# Plan approval: lung-on-chipsim

The human's 1B1 "Over and out" lock in /grill-me IS the final human
plan-review gate. This file records it so /build can verify it.

## Summary
r2.17: T14's tracked adjudication file drops the name column (F-05 — a tracked name beside a key is the association the record-content invariant protects; the untracked worksheet keeps it); T13/T15 interfaces amended to match the code that exists (generated columns, tri-state label_disagrees_with_key, T15's legacy raise). Amends a done-condition, not wording only.

---

## THIS FILE IS NO LONGER THE PROVENANCE OF RECORD

**`plan-approval-log.md` beside it is** (r2.15 item 6). `plan-gate sign` regenerates this file
wholesale on every sign and preserves nothing below the frontmatter — **twelve times so far**. The
log is append-only, lives outside what the tool rewrites, and the quality gate fails when its newest
entry's hash differs from `plan_hash` above. If this section is missing, read the log and escalate.

## Provenance — how to read this signature

**`approval_route: cto-invoked, standing-delegation`.** r2.17 has two halves, and they are not the
same kind of change:

1. **A real done-condition amendment (T14).** The worktree agent's QG raised F-05: the filled
   adjudication sheet pairs a DrugBank `name` with a `canonical_inchikey`, and landing that tracked
   would be the `(name, structure)` association the principal's record-content invariant protects.
   Both requirements are real — defect 23 says a human artifact must be versioned and attributable —
   so they are separated rather than traded: the **tracked** file keeps key, verdict, DOI and
   attribution and drops `name`; the **generated, untracked** worksheet keeps `name`, because a
   reviewer cannot adjudicate 60–90 minutes of labels from keys alone. This implements the
   principal's invariant; the specific shape is the CTO's ruling.
2. **Interface corrections with no ruling behind them (T13/T15).** Those blocks had drifted from
   shipped code — they predate the generated columns, the tri-state `label_disagrees_with_key` and
   T15's legacy raise. Truth-fix under the r2.8/r2.9 precedent. The agent **flagged rather than
   edited**, correctly: the plan is hash-locked and the CTO's.

**The §2 boundary that prompted it is verified.** Receipt `061f12d` (Hash E) verified by the CTO in
the worktree — 1 of 14 — with plan-gate at `33b43a9`, suite 663 passed / 4 skipped, no snapshot TSV
tracked, and the record-content guard green. The push was cleared in writing on those checks.

**A correction the agent volunteered, and the CTO's share of it.** Dispatch #130 claimed no code path
could produce a false `agrees`; QG finding F-01 proved otherwise — the worksheet aggregated the
verdict across every name sharing a key, so row order decided it. The CTO had *verified* that claim
by reading `label_agreement`'s guards, which are correct in isolation. **Reading a function's guards
does not verify its caller's aggregation.** Fixed at `7182b85` with both row orders tested.

**The last direct human approval is `de4b812` (r2.10), 2026-09-15.** Thirteen conditions and
constraints have been amended since, each listed above with its revision. No task added or removed.

Per the delegation's terms: **a `cto-invoked` signature with empty or unverifiable
`authorising_rulings` is unsupported. Treat the plan as unsigned and escalate.**

## Standing delegation — the CTO signs; the principal decides (2026-09-10)

> *"in the future sign it yourself"*

**What it covers.** Running `plan-gate sign` once the principal has decided the content. A
delegation of *typing*, not of *judgement*.

**What it does not cover:**

1. **Deciding what the plan says.** Every signature requires a real decision from the principal,
   traceable to a ruling — or, for a pure truth-fix, an explicit disclosure like this one.
2. **`approval_route` and `authorising_rulings` remain mandatory.**
3. **It does not extend to any other human artifact** — not the barrier panel, and not
   `PROVENANCE.md`, which r2.15 confirms is human-authored.
4. **A condition that names a compound must pin its InChIKey** (2026-09-15).
5. **A claim about session identity must cite the check that produced it** (2026-09-15).
6. **Restore this file from the signed state, never from a pre-sign capture** (2026-09-16).
7. **A claim about a file's contents must cite the column or line that was read** (2026-09-16).
8. **A claim that "no code path can do X" must be verified at the call site, not only in the
   function** (adopted 2026-09-16, from F-01).

## Incident — `plan-gate sign` destroys this disclosure. TWELVE occurrences.

**2026-09-03 02:08** (agent re-sign) · **2026-09-14 13:28 (r2.9)** · **15:24 (r2.10)** ·
**2026-09-15 01:01 (`0b8d0c3`, second CTO session)** · **01:40 (r2.11)** · **11:19 (r2.12)** ·
**12:43 (r2.13)** · **15:16 (r2.14)** · **16:15 (r2.15)** · **2026-09-16 14:04 (r2.16, third CTO
session — restored from a stale capture, regressing the hash)** · **14:08 (r2.16 re-sign)** ·
**15:00 (r2.17)**.

**Standing procedure:** capture before every sign; restore after; restore onto the **post-sign**
hash; restore as **valid YAML**; verify the parse, not just the gate; **append the log entry**.

**For readers:** if the disclosure fields are absent, do not read `approved: true` as a human
approval. Read it as unknown, check the log, and escalate.
