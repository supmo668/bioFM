---
workstream: lung-on-chipsim
plan_path: workstreams/lung-on-chipsim/plan/build-plan.md
plan_hash: 3ab0db9
approved: true
approved_by: Matthew Mo
approval_route: cto-invoked, standing-delegation
invoked_by: biofm/matthew-mo/cto
provenance_of_record: workstreams/lung-on-chipsim/plan/plan-approval-log.md
authorising_rulings:
  - 'CTO rulings 2026-09-17 on the §10 gate escalations E-17 to E-20 (dispatch #155)'
  - 'CTO ruling 2026-09-17 stating E6-7, which had been authorised verbally since r2.21 and written nowhere hash-locked (agent refusal to build an unstated clause)'
  - 'CTO rulings 2026-09-17 on the §9 gate escalations E-13 to E-16 (dispatch #149)'
  - 'CTO rulings 2026-09-17 on the §8 gate escalations E-09 to E-12 (dispatch #145)'
  - 'CTO rulings 2026-09-17 on the §7 gate escalations E-01 to E-07 plus CTO finding E-08 (dispatch #143)'
  - 'CTO ruling 2026-09-17 on the E6-1 x r2.20 composition gap escalated by the worktree agent (dispatch #141) — failure scoped per-project, listing repo-wide, unowned paths fail here'
  - 'CTO rulings 2026-09-16 on §6 quality-gate escalations E6-1 to E6-7 (dispatch #139, r2.21)'
  - 'CTO rulings 2026-09-16 on §5 escalations E-1 to E-6 (r2.20)'
  - 'principal 2026-09-15 record-content re-ruling — the invariant targets record content and the (accession, name, structure) association'
  - 'principal 2026-09-15 lane ruling, re-confirmed 2026-09-16 — this CTO session owns the lane'
  - 'r2.27 has NO principal ruling — quality-gate findings and a correction to the CTO own r2.26 enforcement; r2.8/r2.9 precedent'
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
date: 2026-09-17T10:35
  - 'Global Constraints (r2.23) — allow-list checked by directory IDENTITY not case-folding, with missing-root and outside-root as two distinct failures; roots anchored at runtime; operator-chosen --dest/--out through the same helper with data/raw and the journal declared; the listing RENDERED at the REPO root by a shipped command; owner-gate fiction stated; a repo-root declaration surface for unowned paths; declaration data acknowledged unbuilt'
  - 'Global Constraints (r2.24) — the report proves it scanned something (check=True, count floor, paths resolve); GIT_* dropped and executed config disabled; an owner needs a tracked marker; paths escaped; unresolvable tracked paths counted always and failing only when owned; submodules explicitly NOT scanned; owner registry folded into E-02; topology placement folded into E6-6'
  - 'Global Constraints (r2.25) — a broken declaration file is exit 2 with nothing declared and the listing still rendered, not exit 3; counts kept separate; assertions bind the exit code not the return value; declarations load once through a snapshot; the registry may not police itself; an absent declaration file is not an empty one; all defects per entry in one pass; per-reviewer copies with a verified interpreter'
  - 'Global Constraints (r2.26) — E6-7 STATED — one entry point a non-pytest consumer can call, composing all four checks with the FAIL in it and the three-state exit contract; and a production guard may not be a bare assert, since python -O strips it'
  - 'Global Constraints (r2.27) — predicates with opposite safe directions may not share a default; structural errors carried by the header counts; readability_waived measured and removed if inert; E-17 required ScanContext with data/presentation split so the exit code is assertable; E-18 two pure moves; the -O enforcement must OBSERVE the guard in a child interpreter, never re-derive it'
---

# Plan approval: lung-on-chipsim

The human's 1B1 "Over and out" lock in /grill-me IS the final human
plan-review gate. This file records it so /build can verify it.

## Summary
r2.27 folds the §10 gate, in which the E6-6 extraction itself was **clean** — an AST census over 98
definitions found nothing lost, duplicated or misordered — and **all the risk was in the behaviour
changes**. Two fail-open defects each shipped **under a sentence of the agent's asserting the
opposite**, in the iteration implementing rule 13. Rulings E-17 to E-20, plus a correction to r2.26's
own `-O` enforcement, which shipped vacuous.

---

## THIS FILE IS NO LONGER THE PROVENANCE OF RECORD

**`plan-approval-log.md` beside it is** (r2.15 item 6). `plan-gate sign` regenerates this file
wholesale on every sign — **twenty-three times so far** — preserving nothing below the frontmatter.

## Provenance — how to read this signature

**The move was clean; the behaviour changes were not.** A reviewer's AST census over 98 pre-move
definitions found nothing lost, nothing duplicated, nothing meaningfully reordered — 49/49 `ingest`
and 37/49 guard definitions byte-identical with all 12 differences accounted for, both predicates at
the right call sites, zero guard dependency on `ingest`, the live report byte-identical — and said so
**without hedging**. The named non-mechanical seam turned out to be **two** questions, not one.

**Two fail-open defects, each under a sentence of the agent's asserting the opposite**, in the
iteration implementing the clause about prose that implies a check the tool does not perform:
`ContentPolicy`'s *"both defaults refuse nothing, so a caller who forgets them gets a noisier gate"*
was **false of `content_exempt`** — exempt nothing and the double-exemption defect never fires, the
declaration holds, the file is **cleared**, measured against the shipped policy. And the
structural-error banner read *"more files fail, never fewer"* while directly beneath it a broken
declaration file turned `owner=<unowned> [FAILS HERE]` into `owner=ghost-lib [listed]`, because
`registry=None` was read as "no registry yet" and answered with the **wider** set. **One YAML syntax
error was the only difference between the two runs** — inside the E-13 fix whose entire subject is
what a broken declaration file may cost.

**r2.26's `-O` enforcement shipped vacuous, and the clause was mine.**
`test_the_container_refusal_survives_python_O` **did not test `-O`**: it raised an exception it had
constructed itself and re-parsed the source with `ast`, which yields `Assert` nodes identically under
`-O`. A mutant that made the refusal vanish **exactly and only under `-O`** passed all three related
tests. The clause now says the test must **start a child interpreter with `-O` and observe the guard
refusing** — *observe the behaviour, never re-derive it.*

**The snapshot covered the YAML and not the verdicts.** `declaration_defects` ran **three times** per
report, re-adjudicating against the filesystem, so an artifact rebuilt between passes produced **a
single report that disagreed with itself** — the listing clearing a path the defects section called
STALE in the same run. E-14's failure surviving inside the fix for E-14.

**The agent's own worst catch was a mutation run it nearly reported.** It read "no survivors" from a
clone whose **baseline was already 8-failed**, every mutant "killed" by the same already-failing
test. Re-run clean: baseline 178 passed, all ten killed, each by its own test. That is rule 15.

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
15. **A mutation result is evidence ONLY if the baseline was green** (2026-09-17, r2.27). A clone
    whose suite already fails "kills" every mutant with the same failing test and reports no
    survivors — the vacuity family wearing a different hat, and it nearly reached a CTO report.
    State the baseline count beside the mutant count, or the number means nothing.
14. **A condition an agent is expected to build must exist in the SIGNED PLAN** (2026-09-17, r2.26),
    not only in a dispatch, a handoff, or the provenance log. The approval log records that a
    decision was made; it is not where conditions live. Saying "E6-6/E6-7 remain yours" four times
    does not create E6-7. *An agent asked to implement a clause that does not exist is being asked
    to approve it* — and after a compaction boundary it cannot even tell whose words it is holding.
13. **Prose that implies a check the tool does not perform is a false claim** (2026-09-17, r2.25).
    It survives review *because* it reads as reassurance. Two instances in one day: `derived_from`
    "a claim a reader can check" (never verified), and `BioSimEnv`'s "every model call is metered by
    a component an independent sealed test proved correct" (component proven, use absent). State
    what is actually verified — E6-5 applied to documentation.
12. **Implementing a clause is where that clause's own lesson gets rebuilt** (2026-09-17, r2.23).
    The agent's summary of its own gate: *nearly every defect was the lesson of the clause directly
    above it, one level down in my implementation of that clause.* Case-sensitivity closed in
    `84ce8e0` and rebuilt in the `.md` waiver; numpy elision closed for parquet and rebuilt for
    HDF5; name-based dispatch condemned in one function and used in the next; identity-from-ambient-
    state flagged by the CTO and then written by the agent an hour later; and the CTO's own E6-1b
    rebuilt the scoping hole it was written to close. **Check new code against the lesson that
    produced the clause it implements, not only against the clause.** Test-level instance, adopted
    from the agent: *never assert on a string the fixture also produces* — three name-collision
    vacuities this session ("already", "configs", "symlink").
11. **A remediation is reported only after it is OBSERVED, never from intent** (2026-09-17, r2.22).
    Both parties broke this on the same day: the agent wrote "I re-armed the monitor" before doing
    it, in the message asking me to check its reasoning about that very file; I wrote that this
    session "did not authorise a push and cannot see the event" when the clearance and four
    compliance reports were in my own resolved dispatch list. Rule 7 says cite what you read; rule
    11 says a thing you intend to do is not a thing you have done.

## Incident — `plan-gate sign` destroys this disclosure. TWENTY-THREE occurrences.

**2026-09-03 02:08** · **2026-09-14 13:28 / 15:24** · **2026-09-15 01:01 (`0b8d0c3`, second CTO
session) / 01:40 / 11:19 / 12:43 / 15:16 / 16:15** · **2026-09-16 14:04 (third CTO session — restored
from a stale capture, regressing the hash) / 14:08 / 15:00 / 15:04 / 15:36 / 15:38 / 18:28 / 18:59**
· **2026-09-17 02:40 / 04:55 / 05:45 / 08:15 / 08:55 / 10:35**.

**Standing procedure:** capture before every sign; restore after; restore onto the **post-sign**
hash; restore as **valid YAML**; verify the parse, not just the gate; **append the log entry**.

**For readers:** if the disclosure fields are absent, do not read `approved: true` as a human
approval. Read it as unknown, check the log, and escalate.
