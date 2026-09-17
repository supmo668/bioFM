---
workstream: lung-on-chipsim
plan_path: workstreams/lung-on-chipsim/plan/build-plan.md
plan_hash: 302d23e
approved: true
approved_by: Matthew Mo
approval_route: cto-invoked, standing-delegation
invoked_by: biofm/matthew-mo/cto
provenance_of_record: workstreams/lung-on-chipsim/plan/plan-approval-log.md
authorising_rulings:
  - 'CTO ruling 2026-09-17 stating E6-7, which had been authorised verbally since r2.21 and written nowhere hash-locked (agent refusal to build an unstated clause)'
  - 'CTO rulings 2026-09-17 on the §9 gate escalations E-13 to E-16 (dispatch #149)'
  - 'CTO rulings 2026-09-17 on the §8 gate escalations E-09 to E-12 (dispatch #145)'
  - 'CTO rulings 2026-09-17 on the §7 gate escalations E-01 to E-07 plus CTO finding E-08 (dispatch #143)'
  - 'CTO ruling 2026-09-17 on the E6-1 x r2.20 composition gap escalated by the worktree agent (dispatch #141) — failure scoped per-project, listing repo-wide, unowned paths fail here'
  - 'CTO rulings 2026-09-16 on §6 quality-gate escalations E6-1 to E6-7 (dispatch #139, r2.21)'
  - 'CTO rulings 2026-09-16 on §5 escalations E-1 to E-6 (r2.20)'
  - 'principal 2026-09-15 record-content re-ruling — the invariant targets record content and the (accession, name, structure) association'
  - 'principal 2026-09-15 lane ruling, re-confirmed 2026-09-16 — this CTO session owns the lane'
  - 'r2.26 has NO principal ruling — states a clause the CTO had only ever spoken; r2.8/r2.9 precedent'
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
date: 2026-09-17T08:55
  - 'Global Constraints (r2.23) — allow-list checked by directory IDENTITY not case-folding, with missing-root and outside-root as two distinct failures; roots anchored at runtime; operator-chosen --dest/--out through the same helper with data/raw and the journal declared; the listing RENDERED at the REPO root by a shipped command; owner-gate fiction stated; a repo-root declaration surface for unowned paths; declaration data acknowledged unbuilt'
  - 'Global Constraints (r2.24) — the report proves it scanned something (check=True, count floor, paths resolve); GIT_* dropped and executed config disabled; an owner needs a tracked marker; paths escaped; unresolvable tracked paths counted always and failing only when owned; submodules explicitly NOT scanned; owner registry folded into E-02; topology placement folded into E6-6'
  - 'Global Constraints (r2.25) — a broken declaration file is exit 2 with nothing declared and the listing still rendered, not exit 3; counts kept separate; assertions bind the exit code not the return value; declarations load once through a snapshot; the registry may not police itself; an absent declaration file is not an empty one; all defects per entry in one pass; per-reviewer copies with a verified interpreter'
  - 'Global Constraints (r2.26) — E6-7 STATED — one entry point a non-pytest consumer can call, composing all four checks with the FAIL in it and the three-state exit contract; and a production guard may not be a bare assert, since python -O strips it'
---

# Plan approval: lung-on-chipsim

The human's 1B1 "Over and out" lock in /grill-me IS the final human
plan-review gate. This file records it so /build can verify it.

## Summary
r2.26 writes down **E6-7**, which the CTO had authorised in four separate dispatches while it appeared
**zero times** in the signed plan — its only record was a phrase in provenance log row 20. The agent
stopped rather than build to its own reconstruction of the CTO's words across a compaction boundary.
Also: a production guard may not be a bare `assert`, because `python -O` strips it and the guard does
not weaken, it **vanishes**.

---

## THIS FILE IS NO LONGER THE PROVENANCE OF RECORD

**`plan-approval-log.md` beside it is** (r2.15 item 6). `plan-gate sign` regenerates this file
wholesale on every sign — **twenty-two times so far** — preserving nothing below the frontmatter.

## Provenance — how to read this signature

**This revision exists because an agent refused to implement a clause that did not exist.**
`grep -n "E6-7" build-plan.md` returned **nothing** at `c8d32c7`. E6-6 was in the plan four times;
E6-7 was in the CTO's dispatches four times and in the plan zero. Its only durable record was the
phrase *"module extraction and a combined entry point with the FAIL in the API, authorised"* in
**provenance log row 20** — which is the record of an approval, not a source of conditions.

The agent's reasoning for stopping is the part worth keeping: its wording for E6-7 had been
reconstructed **across a compaction boundary**, so building to it risked the G-17/E-04 shape —
implementing an unstated clause and discovering later that the words were its own. **An agent asked
to implement a clause that does not exist is being asked to approve it.** It did the half that needed
no clause and stopped.

**This is the project's own warning, violated by the party who wrote it.** The plan already says *"an
invariant that lives only in prose is one a docstring can quietly contradict"*. E6-7 lived only in
prose — in dispatch prose, which is worse, because a dispatch is not even in the repository's
enforcement surface.

**The `python -O` finding is the sharpest technical item.** `assert_no_container_is_declared`
enforced E6-2 with a bare `assert`. Under `-O` the statement is **stripped**: the guard does not
weaken, it disappears, and a declared readable container would be cleared in silence. It also raised
`AssertionError` — a test-shaped exception — from production code, while every other refusal in the
module raises the module's own error. The agent scanned every other production module rather than
assuming, and found no others.

**Two further self-catches worth recording.** E-15's fix made `dict(declaration_defects(...))`
**lossy at 15 test sites** — a dict keeps the last defect, so those assertions would have quietly
started depending on check *order* rather than behaviour: the vacuity family again, an assertion that
still passes while meaning something narrower than it reads. And the E6-6 extraction's **first run
refused to report**, because the moved file was untracked and the §8 witness check declined to speak
for a tree it could not see itself in — *the guard caught its own extraction.*

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

## Incident — `plan-gate sign` destroys this disclosure. TWENTY-TWO occurrences.

**2026-09-03 02:08** · **2026-09-14 13:28 / 15:24** · **2026-09-15 01:01 (`0b8d0c3`, second CTO
session) / 01:40 / 11:19 / 12:43 / 15:16 / 16:15** · **2026-09-16 14:04 (third CTO session — restored
from a stale capture, regressing the hash) / 14:08 / 15:00 / 15:04 / 15:36 / 15:38 / 18:28 / 18:59**
· **2026-09-17 02:40 / 04:55 / 05:45 / 08:15 / 08:55**.

**Standing procedure:** capture before every sign; restore after; restore onto the **post-sign**
hash; restore as **valid YAML**; verify the parse, not just the gate; **append the log entry**.

**For readers:** if the disclosure fields are absent, do not read `approved: true` as a human
approval. Read it as unknown, check the log, and escalate.
