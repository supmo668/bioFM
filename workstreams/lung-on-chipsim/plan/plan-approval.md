---
workstream: lung-on-chipsim
plan_path: workstreams/lung-on-chipsim/plan/build-plan.md
plan_hash: 7b29fb5
approved: true
approved_by: Matthew Mo
approval_route: cto-invoked, standing-delegation
invoked_by: biofm/matthew-mo/cto
provenance_of_record: workstreams/lung-on-chipsim/plan/plan-approval-log.md
authorising_rulings:
  - 'CTO rulings 2026-09-16 on §3 quality-gate escalations G-15, G-16, G-17, G-18, G-19, G-20 (dispatch #136)'
  - 'CTO ruling 2026-09-16 on escalation #135 (option A) — T15 reads the tracked file and recomputes the flag (r2.18)'
  - 'principal 2026-09-15 record-content re-ruling — the invariant targets record content and the (accession, name, structure) association'
  - 'principal 2026-09-15 lane ruling, re-confirmed 2026-09-16 — this CTO session owns the lane'
  - 'r2.19 has NO principal ruling — quality-gate findings and clause repairs; truth-fix and CTO judgement under the r2.8/r2.9 precedent'
human_approved_hash: de4b812
human_approved_date: 2026-09-15
human_approval_source: principal message "approve r2.1 sign and commit flash", other CTO session, 2026-09-15T07:56Z (the 0b8d0c3 marker quoted it as "approve r2.10 sign")
prior_human_approved_hash: 737a8d9
prior_human_approved_date: 2026-08-30
tasks_added_since_human_approval: []
conditions_amended_since_human_approval:
  - 'T4(b)/(c), S7 probe list, T11 pointer test — three per-file DVC pointers (r2.11)'
  - 'T5b — stereo guard (r2.12); threonine naming (r2.13, superseded); relative-stereo handling + InChIKey-pinned members (r2.14)'
  - 'Global Constraints — one session per tree; append-only approval log + gate check; Constraint 4 decided; T18/T14 hand-off + window; AM-6 (r2.15)'
  - 'r2.16 — wording and figures only: accessions out of the r2.13 note; merge_report.json named the source of record'
  - 'T14 done-condition — tracked file carries NO `name` column (r2.17); T13/T15 interfaces corrected to shipped code (r2.17)'
  - 'T15 interface — reads the TRACKED file, recomputes the flag from compounds (r2.18, repairing r2.17)'
  - 'T14 interface — export_tracked_adjudication, refusing extra human-added columns (r2.18)'
  - 'T14/T15 (r2.19) — write refusal for any path under configs/; export refuses to overwrite a filled tracked file; extra-column refusal stated; CLI entry; Done-when names the tracked file and requires the flag to survive the round-trip; no compound name in a cell'
date: 2026-09-16T15:36
---

# Plan approval: lung-on-chipsim

The human's 1B1 "Over and out" lock in /grill-me IS the final human
plan-review gate. This file records it so /build can verify it.

## Summary
r2.19 (re-signed): G-15 refuse any path under configs/ by path not git; G-01 the export refuses to overwrite a filled tracked file; G-17 extra-column refusal stated; G-18 CLI entry on the panel-seal precedent; G-16/G-19 T15's Done-when names the tracked file and requires the flag to survive the round-trip; G-20 no compound name in a cell, recorded as unenforceable. Re-signed because the composition check found a FOURTH stale 'worksheet' clause inside T15's docstring.

---

## THIS FILE IS NO LONGER THE PROVENANCE OF RECORD

**`plan-approval-log.md` beside it is** (r2.15 item 6). `plan-gate sign` regenerates this file
wholesale on every sign — **fifteen times so far** — and preserves nothing below the frontmatter.
The gate fails when the log's newest entry's hash differs from `plan_hash` above.

## Provenance — how to read this signature

**r2.19 carries the §3 quality gate's plan-level findings.** That gate was the most productive of
the project: 20 findings kept, 14 fixed, 1 rejected as unreproducible, 6 escalated here because the
plan is the CTO's.

**The finding that matters most (G-01) is why the export now refuses.** Measured before the refusal
existed: a **blank** worksheet exported over a filled tracked file left **0 of 24 verdicts and
returned 24** — destruction reporting success, on the artifact holding 60–90 minutes of
irreplaceable human judgement. It required no carelessness: lose `data/interim/`, T13 regenerates
the worksheet blank *without error*, and a re-export destroys the adjudication. Defect 22's
never-clobber rule guarded the worksheet and left the published record unguarded.

**What r2.19 rules.** G-15: `write_adjudication_worksheet` refuses any resolved path under
`configs/`, **by path — not by shelling out to `git ls-files` from library code**, which is slow,
environment-dependent and wrong in a non-git checkout; the export becomes the only writer permitted
to target the tracked path, which is what makes r2.18's split load-bearing rather than decorative.
G-17: the extra-column refusal becomes a **stated clause** rather than code-only behaviour. G-18: a
CLI entry, on the `chipsim panel-seal` precedent (C4) — a helper whose only invocation is a Python
call loses to hand-deleting columns, the accident it exists to prevent. G-19: the flag must survive
`read_pgp_labels`, or T15's "so T17 receives it" is false. G-20: T14 instructs that no compound name
goes in a cell, **recorded as unenforceable by any column check** — the column is legitimate, only
the value is wrong.

**Re-signed once, deliberately.** The first r2.19 signature was `732642b`. The composition check
required by delegation rule 8 then found a **fourth** stale "worksheet" clause inside T15's
docstring — the same drift r2.19 exists to repair, one clause further on. Fixed and re-signed at
`7b29fb5` before any commit, so `732642b` never landed. Three "worksheet" mentions remain in T15 and
all three are deliberate: two history notes and one quoting the old wording.

**Adopted as process, from the agent's own disclosures:** mutation testing is valuable — it proved
three real gaps — but it runs on a **copy**, never the shared working tree. Two reviewers mutated
the tree the gate was hashing; one's in-flight edits produced a HIGH finding against a file state
that never existed in any commit. A mutation left behind at the wrong moment would be signed into a
receipt as the reviewed state.

**The last direct human approval is `de4b812` (r2.10), 2026-09-15.** No task added or removed since.

Per the delegation's terms: **a `cto-invoked` signature with empty or unverifiable
`authorising_rulings` is unsupported. Treat the plan as unsigned and escalate.**

## Standing delegation — the CTO signs; the principal decides (2026-09-10)

> *"in the future sign it yourself"*

**What it covers.** Running `plan-gate sign` once the principal has decided the content — typing,
not judgement.

**What it does not cover:**

1. **Deciding what the plan says.** Every signature needs a principal ruling, or an explicit
   truth-fix disclosure like this one.
2. **`approval_route` and `authorising_rulings` remain mandatory.**
3. **No other human artifact** — not the barrier panel, not `PROVENANCE.md` (human-authored).
4. **A condition that names a compound must pin its InChIKey** (2026-09-15).
5. **A claim about session identity must cite the check that produced it** (2026-09-15).
6. **Restore this file from the signed state, never from a pre-sign capture** (2026-09-16).
7. **A claim about a file's contents must cite the column or line that was read** (2026-09-16).
8. **Composition must be verified, not just the parts** (2026-09-16, widened twice). Check at the
   call site, not only in the function (F-01); read clauses amended in one revision against each
   other (r2.17); and **sweep the whole task for any term a revision redefines** — r2.19 renamed
   T15's input and three clauses still said "worksheet", the fourth found only by sweeping.

## Incident — `plan-gate sign` destroys this disclosure. FIFTEEN occurrences.

**2026-09-03 02:08** · **2026-09-14 13:28 (r2.9)** · **15:24 (r2.10)** · **2026-09-15 01:01
(`0b8d0c3`, second CTO session)** · **01:40 (r2.11)** · **11:19 (r2.12)** · **12:43 (r2.13)** ·
**15:16 (r2.14)** · **16:15 (r2.15)** · **2026-09-16 14:04 (r2.16, third CTO session — restored
from a stale capture, regressing the hash)** · **14:08 (r2.16 re-sign)** · **15:00 (r2.17)** ·
**15:04 (r2.18)** · **15:36 (r2.19)** · **15:38 (r2.19 re-sign)**.

**Standing procedure:** capture before every sign; restore after; restore onto the **post-sign**
hash; restore as **valid YAML**; verify the parse, not just the gate; **append the log entry**.

**For readers:** if the disclosure fields are absent, do not read `approved: true` as a human
approval. Read it as unknown, check the log, and escalate.
