---
workstream: lung-on-chipsim
plan_path: workstreams/lung-on-chipsim/plan/build-plan.md
plan_hash: 6eba1bb
approved: true
approved_by: Matthew Mo
approval_route: cto-invoked, standing-delegation
invoked_by: biofm/matthew-mo/cto
provenance_of_record: workstreams/lung-on-chipsim/plan/plan-approval-log.md
authorising_rulings:
  - 'CTO ruling 2026-09-17 on the E6-1 x r2.20 composition gap escalated by the worktree agent (dispatch #141) — failure scoped per-project, listing repo-wide, unowned paths fail here'
  - 'CTO rulings 2026-09-16 on §6 quality-gate escalations E6-1 to E6-7 (dispatch #139, r2.21)'
  - 'CTO rulings 2026-09-16 on §5 escalations E-1 to E-6 (r2.20)'
  - 'principal 2026-09-15 record-content re-ruling — the invariant targets record content and the (accession, name, structure) association'
  - 'principal 2026-09-15 lane ruling, re-confirmed 2026-09-16 — this CTO session owns the lane'
  - 'r2.22 has NO principal ruling — a composition repair of the CTO own prior revision; r2.8/r2.9 precedent'
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
  - 'r2.16 — wording and figures only; merge_report.json named the source of record'
  - 'T14/T13/T15 — no `name` column; interfaces corrected; T15 reads the tracked file and recomputes the flag (r2.17, r2.18)'
  - 'T14/T15 (r2.19) — configs/ write refusal; export refuses to overwrite a filled tracked file; extra-column refusal stated; CLI entry; no compound name in a cell'
  - 'Global Constraints + T5a + T14 (r2.20) — record-bearing writers validate destinations against an ALLOW-LIST via one shared helper; the guard may not skip an undecodable file silently; publish via the CLI; fail-closed stated'
  - 'Global Constraints (r2.21) — declarations owned per project with path->sha256 or a derived-from-source claim; readable structured containers always read, never declared; the dispatch waiver covers .md messages only; which half each mechanism enforces is stated'
  - 'Global Constraints (r2.22) — E6-1b: the undeclared-undecodable FAILURE is scoped to the owning project, the LISTING stays repo-wide, and a path owned by NO project fails THIS gate so scoping can never make a file unfailable everywhere; r2.20 fail-closed clause amended to match'
date: 2026-09-17T02:40
---

# Plan approval: lung-on-chipsim

The human's 1B1 "Over and out" lock in /grill-me IS the final human
plan-review gate. This file records it so /build can verify it.

## Summary
r2.22 repairs a composition gap in r2.21 that the worktree agent found and refused to close on its
own authority. E6-1 (declarations move to the owning project) did not compose with r2.20 (an
undeclared undecodable file fails): removing the 24 foreign declarations as E6-1 required would have
made THIS module's gate fail on 24 files owned by two other teams. Failure is now scoped to the
owning project, listing stays repo-wide, and **unowned paths fail here** so scoping cannot make any
file unfailable everywhere.

---

## THIS FILE IS NO LONGER THE PROVENANCE OF RECORD

**`plan-approval-log.md` beside it is** (r2.15 item 6). `plan-gate sign` regenerates this file
wholesale on every sign — **eighteen times so far** — preserving nothing below the frontmatter.

## Provenance — how to read this signature

**r2.22 exists because the agent ran the check I had just told it to run, and aimed it at me.**
One dispatch after I wrote *"verify composition, not just parts — read the clauses you touch against
each other, because r2.17 shipped two individually-correct clauses that contradicted one another and
I signed it"*, it did exactly that to r2.21 and found the same class of defect in my own revision.

**Measured, and CTO-verified independently before ruling:** of the 24 declared binary paths, **zero
belong to this project** — 11 under `paper_standalone/`, 13 under `projects/perturb-seq-eval/` (the
agent reported 12/12; immaterial to its argument, corrected here because I checked). Removing them
as E6-1 required, with no declaration data yet existing in those projects, makes this module's live
test fail on 24 files owned by teams who cannot judge the failure. **E6-1 did not remove the
coupling; it inverted it** — before, another team *adding* a figure turned this gate red; after,
another team *not yet having adopted the rule* turned it red on day one.

**The agent declined to choose the scope itself, citing rule 10** — the scope of a failure is an
ownership assignment, therefore a shape decision, therefore mine. That is the rule working as
intended, one revision after it was written, applied by the party it constrains rather than by the
party it protects.

**I caught one more in my own repair before signing.** E6-1b as first drafted scoped failure to
owning projects and said nothing about paths owned by no project — which would have made
`.claude/usr/**/dispatches/leak.pdf` listed but unfailable anywhere, **silently re-opening the exact
hole E6-4 had closed one clause above**. The unowned-paths rule closes it. The composition check
found it; the clause is now annotated so a later reader cannot remove the rule without seeing why it
is load-bearing.

**The residual risk is written into the plan rather than argued away:** a genuinely undecodable file
outside this module's paths is neither read nor declaration-gated here. E6-2 shrinks that set to
rendered artifacts only, because every readable structured container is now read repo-wide. What
remains is listed, counted, and the owning team's to close.

**The last direct human approval is `de4b812` (r2.10), 2026-09-15.** No task added or removed since.

Per the delegation's terms: **a `cto-invoked` signature with empty or unverifiable
`authorising_rulings` is unsupported. Treat the plan as unsigned and escalate.**

## Standing delegation — the CTO signs; the principal decides (2026-09-10)

> *"in the future sign it yourself"*

**What it covers.** Running `plan-gate sign` once the principal has decided the content — typing,
not judgement.

**What it does not cover:**

1. **Deciding what the plan says** — a principal ruling, or an explicit truth-fix disclosure.
2. **`approval_route` and `authorising_rulings` remain mandatory.**
3. **No other human artifact** — not the barrier panel, not `PROVENANCE.md`.
4. **A condition that names a compound must pin its InChIKey** (2026-09-15).
5. **A claim about session identity must cite the check that produced it** (2026-09-15).
6. **Restore this file from the signed state, never from a pre-sign capture** (2026-09-16).
7. **A claim about a file's contents must cite the column or line that was read** (2026-09-16).
8. **Composition must be verified, not just the parts** (2026-09-16).
9. **A rule that protects a NAME cannot protect an INVARIANT** (2026-09-16, r2.20). State where an
   operation IS permitted, not which spellings are forbidden.
10. **A decision that looks like bookkeeping is still a shape decision if it assigns ownership**
    (2026-09-16, r2.21). Declaring another module's artifacts inside your own source assigns them
    your failure mode and your repair path. **Scoping a failure is the same act** (r2.22).
11. **A remediation is reported only after it is OBSERVED, never from intent** (2026-09-17, r2.22).
    Both parties broke this on the same day: the agent wrote "I re-armed the monitor" before doing
    it, in the message asking me to check its reasoning about that very file; I wrote that this
    session "did not authorise a push and cannot see the event" when the clearance and four
    compliance reports were in my own resolved dispatch list. Rule 7 says cite what you read; rule
    11 says a thing you intend to do is not a thing you have done.

## Incident — `plan-gate sign` destroys this disclosure. EIGHTEEN occurrences.

**2026-09-03 02:08** · **2026-09-14 13:28 / 15:24** · **2026-09-15 01:01 (`0b8d0c3`, second CTO
session) / 01:40 / 11:19 / 12:43 / 15:16 / 16:15** · **2026-09-16 14:04 (third CTO session — restored
from a stale capture, regressing the hash) / 14:08 / 15:00 / 15:04 / 15:36 / 15:38 / 18:28 / 18:59**
· **2026-09-17 02:40**.

**Standing procedure:** capture before every sign; restore after; restore onto the **post-sign**
hash; restore as **valid YAML**; verify the parse, not just the gate; **append the log entry**.

**For readers:** if the disclosure fields are absent, do not read `approved: true` as a human
approval. Read it as unknown, check the log, and escalate.
