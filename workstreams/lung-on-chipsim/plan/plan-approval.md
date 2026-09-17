---
workstream: lung-on-chipsim
plan_path: workstreams/lung-on-chipsim/plan/build-plan.md
plan_hash: b63405a
approved: true
approved_by: Matthew Mo
approval_route: cto-invoked, standing-delegation
invoked_by: biofm/matthew-mo/cto
provenance_of_record: workstreams/lung-on-chipsim/plan/plan-approval-log.md
authorising_rulings:
  - 'CTO rulings 2026-09-17 on the §11 gate: index-vs-worktree escalation, E6-7 non-compliance, contract escapes'
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
  - 'r2.28 has NO principal ruling — quality-gate findings and a correction to evidence the CTO itself accepted; r2.8/r2.9 precedent'
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
date: 2026-09-17T12:10
  - 'Global Constraints (r2.23) — allow-list checked by directory IDENTITY not case-folding, with missing-root and outside-root as two distinct failures; roots anchored at runtime; operator-chosen --dest/--out through the same helper with data/raw and the journal declared; the listing RENDERED at the REPO root by a shipped command; owner-gate fiction stated; a repo-root declaration surface for unowned paths; declaration data acknowledged unbuilt'
  - 'Global Constraints (r2.24) — the report proves it scanned something (check=True, count floor, paths resolve); GIT_* dropped and executed config disabled; an owner needs a tracked marker; paths escaped; unresolvable tracked paths counted always and failing only when owned; submodules explicitly NOT scanned; owner registry folded into E-02; topology placement folded into E6-6'
  - 'Global Constraints (r2.25) — a broken declaration file is exit 2 with nothing declared and the listing still rendered, not exit 3; counts kept separate; assertions bind the exit code not the return value; declarations load once through a snapshot; the registry may not police itself; an absent declaration file is not an empty one; all defects per entry in one pass; per-reviewer copies with a verified interpreter'
  - 'Global Constraints (r2.26) — E6-7 STATED — one entry point a non-pytest consumer can call, composing all four checks with the FAIL in it and the three-state exit contract; and a production guard may not be a bare assert, since python -O strips it'
  - 'Global Constraints (r2.27) — predicates with opposite safe directions may not share a default; structural errors carried by the header counts; readability_waived measured and removed if inert; E-17 required ScanContext with data/presentation split so the exit code is assertable; E-18 two pure moves; the -O enforcement must OBSERVE the guard in a child interpreter, never re-derive it'
  - 'Global Constraints (r2.28) — a commit gate reads the STAGED BLOB it certifies, never the working file, and the report states which copy it read; E6-7 declared UNMET because the shipped command composes three of four and the CTO cited it for the fourth; a three-state contract admits no fourth state; every interpolated field escaped, not just paths'
---

# Plan approval: lung-on-chipsim

The human's 1B1 "Over and out" lock in /grill-me IS the final human
plan-review gate. This file records it so /build can verify it.

## Summary
r2.28 rules the §11 gate, which **failed** with nine blocking findings. The one that reaches the CTO:
the shipped `record-content-report` **does not check accessions at all**, and the CTO has been citing
its output as compliance evidence. Also ruled: a commit gate must read the **staged blob**, after the
guard was shown certifying bytes other than the ones being committed.

---

## THIS FILE IS NO LONGER THE PROVENANCE OF RECORD

**`plan-approval-log.md` beside it is** (r2.15 item 6). `plan-gate sign` regenerates this file
wholesale on every sign — **twenty-four times so far** — preserving nothing below the frontmatter.

## Provenance — how to read this signature

**THE FINDING THAT IMPLICATES THE CTO.** `record-content-report` composes **three** of E6-7's four
checks — readability, declarations, ownership. `real_accession_hits` and `ledger_tuple_hits` are
**unreachable from it**, and `enforce_record_content` has **no caller outside its own test file**. The
CTO ran that command repeatedly, quoted `23 listed / N scanned / 0 failing / exit 0` back as
independent verification, and recorded it in dispatches and reports as evidence the record-content
invariant held. **It is not that evidence.** The tree is genuinely clean on accessions — the live-repo
scans at `:170` and `:244` establish it — but that rests on `pytest`, and the CTO attributed it to the
command. **E6-5 is the clause the CTO wrote about exactly this**, and then broke: a mechanism
enforcing three halves may not be cited for the fourth. E6-7 is therefore **declared unmet**.

**A gate was certifying bytes other than the ones being committed.** The guard lists `git ls-files -s`
(the **index**) and reads from the **worktree**. Reproduced end-to-end: index held the payload, disk
held clean text, guard read clean, the commit would have carried it. Ruled: a commit gate reads the
**staged blob**. The agent **escalated rather than fixed**, on the grounds that reading staged blobs
changes what the gate means and that refusing on divergence would break ordinary development — both
correct, and both reasons this needed a ruling rather than a patch.

**A FALSE CLEAN, fixed:** `decoding.py` refused soft/external links among the **root group's members
only**, while `visititems` skips links at **every depth**. Measured: same link at top level →
`readable=False`; nested one group down → `readable=True`. An `h5ad` with its payload behind an
`ExternalLink` one level in was read, never listed, zero hits. Fixed red→green with an
**anti-overcorrection** test so "refuse every group" cannot pass either.

**The agent's mutation method was weaker than it claimed, and its own reviewer caught it.** It
reported "7/7 killed against a green 165-passed subset" — true, but the clone was **project-only**,
silently deselecting 44 tests including precisely the ownership and anti-vacuity ones most likely to
kill those mutants. A reviewer rebuilt a self-contained checkout staging all 788 files, baselined
942/5 with **no deselections**, and re-derived all seven: they do die. *The conclusion held by which
mutants it happened to pick, not by method.* **Rule 15 is amended accordingly.**

**Thirteenth vacuity, the agent's own:** a test keying on **annotation text**
(`"DeclarationSurface" in str(parameter.annotation)`) cannot see the edit a person restoring the
convenience default would actually make — verified surviving at 942 — in a file that guards that exact
pattern three tests earlier. Also `37 of 118` mutants survived, including **every bounded-read ceiling
in `decoding.py`**, under a module docstring claiming every bound was set by measurement.

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
16. **A NEGATIVE RESULT IS EVIDENCE ONLY IF THE CHECK COULD HAVE PRODUCED A POSITIVE**
    (2026-09-17). Rule 15 is the special case; this is the general form, and it recurred **three
    times in one day across both parties**. The agent ran `git cat-file -t db3d598` and read "not a
    valid object name" as "the commit has not reached me" — it answers whether a STRING IS A GIT
    OBJECT, and a plan hash never is. The CTO inferred a fixture row-association from matching
    structures **without reading the accession column**. The CTO then ran
    `pgrep -fl "worktrees/lung-on-chipsim"`, got zero, and nearly concluded a live agent was gone —
    a session's COMMAND LINE never contains its working directory, so the probe could not have
    returned a positive; `lsof -d cwd` showed pid 80498 alive all along.
    **Before trusting a negative, state what a positive would have looked like.** The failure is
    seductive exactly when the silence agrees with what you already suspect — and in the third case
    only procedure prevented harm: probing by message rather than `agent-wake`, which beside a live
    session is how the two-writer condition happened at `#98`.
15. **A mutation result is evidence ONLY if the baseline was green — AND nothing was silently
    deselected** (2026-09-17, extended r2.28). A project-only clone dropped 44 tests, including the
    ownership and anti-vacuity ones most able to kill the mutants under test, while reporting a green
    165-passed baseline. State the baseline count **and** the deselection count, and run mutations
    against a self-contained checkout of the whole tree. *Original form:* (2026-09-17, r2.27). A clone
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

## Incident — `plan-gate sign` destroys this disclosure. TWENTY-FOUR occurrences.

**2026-09-03 02:08** · **2026-09-14 13:28 / 15:24** · **2026-09-15 01:01 (`0b8d0c3`, second CTO
session) / 01:40 / 11:19 / 12:43 / 15:16 / 16:15** · **2026-09-16 14:04 (third CTO session — restored
from a stale capture, regressing the hash) / 14:08 / 15:00 / 15:04 / 15:36 / 15:38 / 18:28 / 18:59**
· **2026-09-17 02:40 / 04:55 / 05:45 / 08:15 / 08:55 / 10:35 / 12:10**.

**Standing procedure:** capture before every sign; restore after; restore onto the **post-sign**
hash; restore as **valid YAML**; verify the parse, not just the gate; **append the log entry**.

**For readers:** if the disclosure fields are absent, do not read `approved: true` as a human
approval. Read it as unknown, check the log, and escalate.
