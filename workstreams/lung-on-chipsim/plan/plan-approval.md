---
workstream: lung-on-chipsim
plan_path: workstreams/lung-on-chipsim/plan/build-plan.md
plan_hash: 2325057
approved: true
approved_by: Matthew Mo
approval_route: cto-invoked, standing-delegation
invoked_by: biofm/matthew-mo/cto
provenance_of_record: workstreams/lung-on-chipsim/plan/plan-approval-log.md
authorising_rulings:
  - 'CTO ruling 2026-09-16 on escalation #135 (option A) — T15 reads the tracked five-column file and recomputes stereo_is_relative from compounds; T14 gains an export helper'
  - 'CTO ruling 2026-09-16 on QG finding F-05 — the tracked adjudication file drops `name` (r2.17)'
  - 'principal 2026-09-15 record-content re-ruling — the invariant targets record content and the (accession, name, structure) association'
  - 'principal 2026-09-15 lane ruling, re-confirmed 2026-09-16 — this CTO session owns the lane'
  - 'r2.18 has NO principal ruling — it repairs a contradiction the CTO introduced in r2.17; truth-fix under the r2.8/r2.9 precedent'
human_approved_hash: de4b812
human_approved_date: 2026-09-15
human_approval_source: principal message "approve r2.1 sign and commit flash", other CTO session, 2026-09-15T07:56Z (the 0b8d0c3 marker quoted it as "approve r2.10 sign")
prior_human_approved_hash: 737a8d9
prior_human_approved_date: 2026-08-30
tasks_added_since_human_approval: []
conditions_amended_since_human_approval:
  - 'T4(b)/(c), S7 probe list, T11 pointer test — three per-file DVC pointers (r2.11)'
  - 'T5b done-conditions — stereo guard (r2.12); threonine naming (r2.13, superseded); relative-stereo handling + InChIKey-pinned members (r2.14)'
  - 'Global Constraints — one session per tree; append-only approval log with a gate check; Constraint 4 decided (minisign at M1); T18/T14 hand-off + window; AM-6 editorial (r2.15)'
  - 'r2.16 — wording and figures only: accessions out of the r2.13 note; r2.12 figures marked guard-only, merge_report.json named the source of record'
  - 'T14 done-condition — tracked file carries NO `name` column (r2.17)'
  - 'T13/T15 interfaces — generated columns, tri-state label_disagrees_with_key, T15 legacy raise (r2.17)'
  - 'T15 interface — reads the TRACKED file, recomputes the flag from compounds, raises on a missing flag or an unknown key (r2.18, repairing r2.17)'
  - 'T14 interface — export_tracked_adjudication projects the worksheet and refuses extra human-added columns (r2.18)'
date: 2026-09-16T15:04
---

# Plan approval: lung-on-chipsim

The human's 1B1 "Over and out" lock in /grill-me IS the final human
plan-review gate. This file records it so /build can verify it.

## Summary
r2.18: resolves a contradiction r2.17 introduced — T15 now reads the TRACKED five-column file and RECOMPUTES stereo_is_relative from compounds (generated, never carried), raising if compounds lacks the flag or a tracked key is unknown; T14 gains export_tracked_adjudication, which projects the worksheet to the five columns and refuses extra human-added columns. Caught by the worktree agent before any code was written.

---

## THIS FILE IS NO LONGER THE PROVENANCE OF RECORD

**`plan-approval-log.md` beside it is** (r2.15 item 6). `plan-gate sign` regenerates this file
wholesale on every sign — **thirteen times so far** — and preserves nothing below the frontmatter.
The gate fails when the log's newest entry's hash differs from `plan_hash` above. If this section is
missing, read the log and escalate.

## Provenance — how to read this signature

**r2.18 repairs a contradiction the CTO introduced one revision earlier, and that is the point of
the entry.** r2.17 amended T14 (the tracked file has five columns, no `name`) and T15 (raise if the
*worksheet* lacks `stereo_is_relative`) **in the same revision**, without checking that T15 reads the
file T14 defines. The five-column file has no such column, so T15 would have raised on every
well-formed input. Nothing was wired into the pipeline yet, so no runtime breakage — but two signed
clauses contradicted each other.

**This is the plan-level form of QG finding F-01**, which the same agent had reported hours earlier:
there, a verdict was correct in the function and wrong in its caller's aggregation; here, two clauses
were each correct alone and wrong in composition. Delegation rule 8 is therefore widened below:
composition must be checked for *plan clauses*, not only code paths.

**What r2.18 rules (escalation #135, option A, as the agent recommended).** T15 reads the **tracked**
file and **recomputes** `stereo_is_relative` from `compounds` — a generated column, never carried,
therefore never stale — raising if `compounds` lacks the flag or if an adjudicated key is unknown to
it. T14 gains `export_tracked_adjudication`, which projects the reviewer's worksheet to the five
columns and **refuses** extra human-added columns rather than dropping them silently. The rejected
options are recorded in the plan: reading the untracked worksheet would unversion the source of truth
(defect 23 again); tracking `stereo_is_relative` would track a generated column, the staleness the
third column class exists to prevent.

**The agent held all code until this was ruled**, having found that every candidate edit depended on
which file T15 reads. That is the correct response to an ambiguous signed clause.

**The last direct human approval is `de4b812` (r2.10), 2026-09-15.** No task added or removed since.

Per the delegation's terms: **a `cto-invoked` signature with empty or unverifiable
`authorising_rulings` is unsupported. Treat the plan as unsigned and escalate.**

## Standing delegation — the CTO signs; the principal decides (2026-09-10)

> *"in the future sign it yourself"*

**What it covers.** Running `plan-gate sign` once the principal has decided the content — typing, not
judgement.

**What it does not cover:**

1. **Deciding what the plan says.** Every signature needs a principal ruling, or an explicit
   truth-fix disclosure like this one.
2. **`approval_route` and `authorising_rulings` remain mandatory.**
3. **No other human artifact** — not the barrier panel, not `PROVENANCE.md` (human-authored, r2.15).
4. **A condition that names a compound must pin its InChIKey** (2026-09-15).
5. **A claim about session identity must cite the check that produced it** (2026-09-15).
6. **Restore this file from the signed state, never from a pre-sign capture** (2026-09-16).
7. **A claim about a file's contents must cite the column or line that was read** (2026-09-16).
8. **Composition must be verified, not just the parts** (2026-09-16, widened by r2.18). A claim that
   "no code path can do X" must be checked at the call site, not only in the function — and **two
   clauses amended in one revision must be read against each other before signing.** Both failures
   happened today, one in code (F-01) and one in this plan (r2.17).

## Incident — `plan-gate sign` destroys this disclosure. THIRTEEN occurrences.

**2026-09-03 02:08** (agent re-sign) · **2026-09-14 13:28 (r2.9)** · **15:24 (r2.10)** ·
**2026-09-15 01:01 (`0b8d0c3`, second CTO session)** · **01:40 (r2.11)** · **11:19 (r2.12)** ·
**12:43 (r2.13)** · **15:16 (r2.14)** · **16:15 (r2.15)** · **2026-09-16 14:04 (r2.16, third CTO
session — restored from a stale capture, regressing the hash)** · **14:08 (r2.16 re-sign)** ·
**15:00 (r2.17)** · **15:04 (r2.18)**.

**Standing procedure:** capture before every sign; restore after; restore onto the **post-sign**
hash; restore as **valid YAML**; verify the parse, not just the gate; **append the log entry**.

**For readers:** if the disclosure fields are absent, do not read `approved: true` as a human
approval. Read it as unknown, check the log, and escalate.
