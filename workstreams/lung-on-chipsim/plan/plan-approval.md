---
workstream: lung-on-chipsim
plan_path: workstreams/lung-on-chipsim/plan/build-plan.md
plan_hash: 33b43a9
approved: true
approved_by: Matthew Mo
approval_route: cto-invoked, standing-delegation
invoked_by: biofm/matthew-mo/cto
provenance_of_record: workstreams/lung-on-chipsim/plan/plan-approval-log.md
authorising_rulings:
  - 'CTO ruling 2026-09-16 on dispatch #131 — accessions out of the plan, under the principal''s 2026-09-15 record-content re-ruling and the #122 §3 no-accessions-in-coordination-records rule'
  - 'principal 2026-09-15 record-content re-ruling — the invariant targets DrugBank record content and the (accession, name, structure) association, not canonical identifiers'
  - 'r2.16 has NO principal ruling of its own — wording and figures only, under the r2.8/r2.9 truth-fix precedent'
  - 'principal 2026-09-15 lane ruling — this CTO session owns the lung-on-chipsim lane'
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
  - 'r2.16 — wording and figures only: accessions out of the r2.13 note; r2.12''s figures marked guard-only with merge_report.json named as the source of record. No condition changed.'
date: 2026-09-16T14:08
---

# Plan approval: lung-on-chipsim

The human's 1B1 "Over and out" lock in /grill-me IS the final human
plan-review gate. This file records it so /build can verify it.

## Summary
r2.16 (re-signed at the true hash): DrugBank accessions removed from the T5b r2.13 note and log row 11, compounds named by title and pinned by InChIKey — CTO ruling 2026-09-16 on #131; PLUS the figures correction, recording that r2.12's 1,599/191->156/41 are the guard-only state and the committed merge_report.json is the source of record (1,576/192->154/43 with the re-key). Wording and figures only; no condition or task changed. Re-signed because a concurrent CTO session's r2.16 sign (24e3a52) never reached a commit and its marker restore regressed plan_hash to r2.15's.

---

## THIS FILE IS NO LONGER THE PROVENANCE OF RECORD

**`plan-approval-log.md` beside it is** (r2.15 item 6). `plan-gate sign` regenerates this file
wholesale on every sign and preserves nothing below the frontmatter — **eleven times so far**. The
log is append-only, lives outside what the tool rewrites, and the quality gate fails when its newest
entry's hash differs from `plan_hash` above. If this section is missing, read the log and escalate.

## Provenance — how to read this signature

**`approval_route: cto-invoked, standing-delegation`.** r2.16 carries no principal ruling of its own:
wording and figures only, under the r2.8/r2.9 truth-fix precedent, implementing the CTO's 2026-09-16
ruling on dispatch #131 — itself downstream of the principal's 2026-09-15 record-content re-ruling.

**What r2.16 changes.** (i) The r2.13 note named two DrugBank accessions beside their record titles
and structures — the `(accession, name, structure)` association the invariant protects — in the very
note that tells done-conditions to pin keys rather than names. Rows are now named by title and
pinned by PubChem InChIKey; one accession in log row 11 is corrected in place with the correction
disclosed, on the row-12 precedent. (ii) The r2.12 figures are marked **guard-only, pre-re-key**, and
`reports/2026-09-15-stereo-guard-tms/merge_report.json` is named the source of record — because
r2.14 and r2.15 presented 1,599/191→156/41 as current after the re-key had changed them to
1,576/192→154/43. **The worktree agent found stale numbers inside hash-locked text**; the plan now
cites the report rather than restating it.

**Two writers touched this revision, disclosed rather than smoothed over.** A second CTO session
(`9f83b99d`, pid 6489) independently made the accession fix and signed r2.16 at `24e3a52` while this
session was adding the figures correction. **`24e3a52` never reached a commit.** Its marker restore
then copied back a capture taken *before* its own sign, regressing `plan_hash` to r2.15's `67a1897`
— the first time the capture-and-restore workaround produced a **hash regression** rather than a
content loss. The state was briefly three-way inconsistent (marker `67a1897`, log row 14 `24e3a52`,
plan `33b43a9`). That session confirmed it is out of this lane, holds no instruction to the
contrary, and its substance is kept in full. This revision is the reconciliation, signed at the hash
the plan actually has.

**The last direct human approval is `de4b812` (r2.10), 2026-09-15.** Eleven conditions and
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
4. **A condition that names a compound must pin its InChIKey** (adopted 2026-09-15). This source
   mislabels at least 11 of its stereoisomers, so a name is annotation and the key is identity.
5. **A claim about session identity must cite the check that produced it** (adopted 2026-09-15).
6. **Restore this file from the signed state, never from a pre-sign capture** (adopted 2026-09-16,
   from the `24e3a52` hash regression). Re-read `plan_hash` after signing and restore onto *that*.
7. **A claim about a file's contents must cite the column or line that was read** (adopted
   2026-09-16). #120 §3 ordered a fixture rewrite on the CTO's inference that fixture rows carried a
   DrugBank `(accession, name, structure)` association. They never did: the IDs are `DB90001`–
   `DB90009` and the names `Fixture-*`, **from the fixture's first commit**. The inference came from
   the structures matching the snapshot; the ID column was never read. The worktree agent measured
   before editing and stopped a false line from reaching `PROVENANCE.md`, a sealed human artifact.

## Incident — `plan-gate sign` destroys this disclosure. ELEVEN occurrences.

**2026-09-03 02:08** (agent re-sign) · **2026-09-14 13:28 (r2.9)** · **15:24 (r2.10)** ·
**2026-09-15 01:01 (`0b8d0c3`, second CTO session)** · **01:40 (r2.11)** · **11:19 (r2.12)** ·
**12:43 (r2.13)** · **15:16 (r2.14)** · **16:15 (r2.15)** · **2026-09-16 14:04 (r2.16, second CTO
session — restored from a stale capture, regressing the hash)** · **14:08 (r2.16 re-sign)**.

`plan-gate verify` passed throughout every occurrence where the hash happened to match: the gate
binds the *plan*, not the *marker*. Occurrence ten is the instructive one — the workaround itself
produced a wrong hash, caught only because the plan had also moved.

**Standing procedure:** capture before every sign; restore after; restore onto the **post-sign**
hash; restore as **valid YAML**; verify the parse, not just the gate; **append the log entry**.

**For readers:** if the disclosure fields are absent, do not read `approved: true` as a human
approval. Read it as unknown, check the log, and escalate.
