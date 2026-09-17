---
workstream: lung-on-chipsim
plan_path: workstreams/lung-on-chipsim/plan/build-plan.md
plan_hash: db3d598
approved: true
approved_by: Matthew Mo
approval_route: cto-invoked, standing-delegation
invoked_by: biofm/matthew-mo/cto
provenance_of_record: workstreams/lung-on-chipsim/plan/plan-approval-log.md
authorising_rulings:
  - 'CTO rulings 2026-09-17 on the §8 gate escalations E-09 to E-12 (dispatch #145)'
  - 'CTO rulings 2026-09-17 on the §7 gate escalations E-01 to E-07 plus CTO finding E-08 (dispatch #143)'
  - 'CTO ruling 2026-09-17 on the E6-1 x r2.20 composition gap escalated by the worktree agent (dispatch #141) — failure scoped per-project, listing repo-wide, unowned paths fail here'
  - 'CTO rulings 2026-09-16 on §6 quality-gate escalations E6-1 to E6-7 (dispatch #139, r2.21)'
  - 'CTO rulings 2026-09-16 on §5 escalations E-1 to E-6 (r2.20)'
  - 'principal 2026-09-15 record-content re-ruling — the invariant targets record content and the (accession, name, structure) association'
  - 'principal 2026-09-15 lane ruling, re-confirmed 2026-09-16 — this CTO session owns the lane'
  - 'r2.24 has NO principal ruling — quality-gate findings; r2.8/r2.9 precedent'
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
date: 2026-09-17T05:45
  - 'Global Constraints (r2.23) — allow-list checked by directory IDENTITY not case-folding, with missing-root and outside-root as two distinct failures; roots anchored at runtime; operator-chosen --dest/--out through the same helper with data/raw and the journal declared; the listing RENDERED at the REPO root by a shipped command; owner-gate fiction stated; a repo-root declaration surface for unowned paths; declaration data acknowledged unbuilt'
  - 'Global Constraints (r2.24) — the report proves it scanned something (check=True, count floor, paths resolve); GIT_* dropped and executed config disabled; an owner needs a tracked marker; paths escaped; unresolvable tracked paths counted always and failing only when owned; submodules explicitly NOT scanned; owner registry folded into E-02; topology placement folded into E6-6'
---

# Plan approval: lung-on-chipsim

The human's 1B1 "Over and out" lock in /grill-me IS the final human
plan-review gate. This file records it so /build can verify it.

## Summary
r2.24 folds the §8 gate, whose headline is that **the E-08 fix contained E-08**: the root SELECTION
was corrected while the root VALIDATION and the file LISTING kept failing silently, composing into
"0 files, exit 0" printed with the true repo root interpolated. Rulings E-09 to E-12. The anti-vacuity
guard for precisely this already existed **in the tests and not in the command**.

---

## THIS FILE IS NO LONGER THE PROVENANCE OF RECORD

**`plan-approval-log.md` beside it is** (r2.15 item 6). `plan-gate sign` regenerates this file
wholesale on every sign — **twenty times so far** — preserving nothing below the frontmatter.

## Provenance — how to read this signature

**Rule 12 demonstrated on itself, one revision after it was written.** E-08 was the CTO's finding
that the shipped report scanned the project root. The agent fixed the root *selection* and left the
root *validation* and the file *listing* able to fail silently — and they compose: no `.git` above
the package → silent fallback to the narrow root E-08 *is* → `git ls-files` fails → the listing
swallows it and returns `[]` → **"0 (failing this gate: 0)", exit 0, printed with the true repo root
interpolated.** Reproduced end-to-end through the shipped CLI by the agent and independently by all
four reviewers; reachable with no attacker. **The anti-vacuity guard for exactly this already existed
IN THE TESTS and not in the command** — `check=True`, a count floor, every path resolving, beneath a
test titled *"a scan over the wrong or an empty list reports clean"*. The CTO's own E-08 sentence,
one function below the fix for it.

**A test named after the regression could not detect it.** A reviewer reverted only the call site and
`test_the_report_scans_the_repo_root_not_the_project_root` stayed **green**: it passed `root`
explicitly, so it never exercised the default the fix installed, and its assertion was on a string
the same commit had deleted. Deleted rather than repaired, and replaced by an equality — the command
prints exactly what the function renders — which holds at 23 and at 0, instead of a `>=20` floor
under a number this mechanism exists to drive to **zero**.

**Three bypasses survived a correct root**, each executed: `GIT_DIR`/`GIT_INDEX_FILE` steering the
listing to a foreign index **while the printed root stayed correct** — more misleading than the bug
being fixed; `core.fsmonitor`, config the scanned tree supplies and git *executes*, running as the
invoking user (both halves of the `#44` B2 ruling now satisfied); and an owner **minted with
`mkdir`**, which under E-03 is better for an attacker than a real owner. The agent measured before
changing ownership semantics — both real projects carry markers — so the 23 live files and E6-1b's
scoping are unchanged.

**Evidence, not assertion:** 12 mutants applied one at a time in a throwaway clone, 11 killed on the
first pass; **M5 survived** and the gap was closed rather than reported as 11/12. M3 is worth
remembering — `is_dir()` for `exists()` is a **one-character** change that silently reinstates the
project-root scan **in every worktree**, which is where all this work happens.

**Five §7 assertions were satisfied by the fixture** — two proved by leaving the branch raising and
deleting only its message. Fourth through seventh in that family, now remedied mechanically rather
than by memory: strip the tmp path from the haystack, assert what the fixture cannot supply, and
assert the twin branch's message is **absent** so the test proves which check fired.

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

## Incident — `plan-gate sign` destroys this disclosure. TWENTY occurrences.

**2026-09-03 02:08** · **2026-09-14 13:28 / 15:24** · **2026-09-15 01:01 (`0b8d0c3`, second CTO
session) / 01:40 / 11:19 / 12:43 / 15:16 / 16:15** · **2026-09-16 14:04 (third CTO session — restored
from a stale capture, regressing the hash) / 14:08 / 15:00 / 15:04 / 15:36 / 15:38 / 18:28 / 18:59**
· **2026-09-17 02:40 / 04:55 / 05:45**.

**Standing procedure:** capture before every sign; restore after; restore onto the **post-sign**
hash; restore as **valid YAML**; verify the parse, not just the gate; **append the log entry**.

**For readers:** if the disclosure fields are absent, do not read `approved: true` as a human
approval. Read it as unknown, check the log, and escalate.
