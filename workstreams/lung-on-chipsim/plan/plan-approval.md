---
workstream: lung-on-chipsim
plan_path: workstreams/lung-on-chipsim/plan/build-plan.md
plan_hash: 07fd0f6
approved: true
approved_by: Matthew Mo
approval_route: cto-invoked, standing-delegation
invoked_by: biofm/matthew-mo/cto
provenance_of_record: workstreams/lung-on-chipsim/plan/plan-approval-log.md
authorising_rulings:
  - 'CTO rulings 2026-09-16 on §5 quality-gate escalations E-1 to E-6 (dispatch #138)'
  - 'CTO rulings 2026-09-16 on §3 escalations G-15/G-17/G-18/G-20 (r2.19) — E-1 supersedes G-15''s shape'
  - 'principal 2026-09-15 record-content re-ruling — the invariant targets record content and the (accession, name, structure) association'
  - 'principal 2026-09-15 lane ruling, re-confirmed 2026-09-16 — this CTO session owns the lane'
  - 'r2.20 has NO principal ruling — quality-gate findings and a shape correction to the CTO''s own r2.19 clause; r2.8/r2.9 precedent'
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
  - 'T15 interface — reads the TRACKED file, recomputes the flag from compounds (r2.18); T14 interface — export_tracked_adjudication (r2.18)'
  - 'T14/T15 (r2.19) — configs/ write refusal; export refuses to overwrite a filled tracked file; extra-column refusal stated; CLI entry; Done-when names the tracked file; no compound name in a cell'
  - 'Global Constraints (r2.20) — record-bearing writers validate destinations against an ALLOW-LIST via one shared helper; the repo guard may not skip an undecodable file silently'
  - 'T5a interface (r2.20) — write_compounds validates its destination; the CLI inherits the refusal rather than adding a second check'
  - 'T14 Files (r2.20) — publish via `chipsim adjudication-export`, not a hand-move; fail-closed journalling stated rather than inherited'
date: 2026-09-16T18:28
---

# Plan approval: lung-on-chipsim

The human's 1B1 "Over and out" lock in /grill-me IS the final human
plan-review gate. This file records it so /build can verify it.

## Summary
r2.20: E-1/E-2 — record-bearing writers (worksheet AND write_compounds) validate destinations against an ALLOW-LIST of untracked roots via one shared helper, checked on literal and resolved paths, case-insensitively, refusing symlinks, by containment; a registry test stops a new writer opting out. E-3 — the repo guard may not skip an undecodable file silently; parquet is read and scanned. E-4 — the export's fail-closed journalling is now stated, not inherited. E-5 — T14 publishes via the CLI, not a hand-move.

---

## THIS FILE IS NO LONGER THE PROVENANCE OF RECORD

**`plan-approval-log.md` beside it is** (r2.15 item 6). `plan-gate sign` regenerates this file
wholesale on every sign — **sixteen times so far** — preserving nothing below the frontmatter.

## Provenance — how to read this signature

**r2.20 corrects the SHAPE of the CTO's own r2.19 clause, on evidence the §5 reviewers executed.**
r2.19 told the code to refuse writes to a directory named `configs/`. The full roster then executed
**three** bypasses of that refusal:

1. **Case.** `configs/` refused, `CONFIGS/` allowed — and on a case-insensitive volume the
   name-bearing worksheet landed in the **real** `configs/` directory. Two reviewers reproduced it
   independently, and so did the agent. One shifted keystroke, and git would show it as
   `configs/pgp_adjudication.csv`, committable, `name` at position 2.
2. **Symlinked directory.** `resolve()` erased the `configs` component and the write went through
   the link — the resolving documented as the *strengthening* is what defeated this case.
3. **Check one object, write another.** The check resolved; the write used the literal path; and
   `os.replace` swapped a destination symlink for a real name-bearing file inside the tracked
   directory.

It was **simultaneously too broad**: any `configs` component anywhere in an absolute path refused
every worksheet write, including the recovery path.

**So the rule now names where writing IS allowed.** One shared helper, an allow-list of untracked
roots, both literal and resolved paths, case-insensitive, symlinked destinations and ancestors
refused, containment rather than substring — and a **registry test** so a new writer cannot opt out.
*A deny-list can only enumerate the attacks someone thought of.*

**E-2 is the same defect with a worse payload, and it was not in r2.19's scope at all.**
`write_compounds` persists accession + name + InChI + InChIKey **on one row** — the complete
DrugBank record, not merely the association — and `chipsim write --out` reached it with no
destination validation. Writing into `configs/` was measured. The CLI inherits the refusal through
the function rather than getting its own check, because two checks drift and the second becomes the
one people trust.

**E-3: the repo-wide guard was silently blind to parquet.** A tracked parquet carrying accession +
name + InChI returned **no hits**, against a CSV control that did. It now lists and fails on any
file it cannot decode, and reads parquet as a frame. *A skipped file is an unchecked file.*

**E-6, ruled and recorded:** the project's real invocation journal holds test-written export records.
They are **kept**, with a note stating which window is test-generated. Deleting audit-trail entries
to make a trail look pristine is a worse defect than an honest trail containing them — and both
reviewers, and the agent, declined to delete them on their own authority.

**Process, third occurrence, now structural.** A reviewer mutated the shared working tree mid-gate
again; the agent caught `.resolve()` stripped from the live file while two reviewers were still
running, after a third had filed a HIGH finding against a state no commit contained. Nothing was
compromised — Hash A came from the committed state and byte-identity was verified before hashing.
Written protocol failed three times, so it is now a **mechanism**: reviewers work on a throwaway
copy, and the gate asserts a clean `git status --porcelain` and empty `git diff` immediately before
Hash A and after the last reviewer exits. The agent's own rule — *never hash, never commit, never
push while a reviewer is live* — is adopted.

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
8. **Composition must be verified, not just the parts** (2026-09-16). Check at the call site, not
   only in the function; read clauses amended in one revision against each other; sweep the whole
   task for any term a revision redefines.
9. **A rule that protects a NAME cannot protect an INVARIANT** (2026-09-16, from r2.20). State where
   an operation IS permitted, not which spellings are forbidden — three executed bypasses of a
   name-based refusal, each trivial, is what a deny-list buys.

## Incident — `plan-gate sign` destroys this disclosure. SIXTEEN occurrences.

**2026-09-03 02:08** · **2026-09-14 13:28 (r2.9)** · **15:24 (r2.10)** · **2026-09-15 01:01
(`0b8d0c3`, second CTO session)** · **01:40 (r2.11)** · **11:19 (r2.12)** · **12:43 (r2.13)** ·
**15:16 (r2.14)** · **16:15 (r2.15)** · **2026-09-16 14:04 (r2.16, third CTO session — restored
from a stale capture, regressing the hash)** · **14:08 (r2.16 re-sign)** · **15:00 (r2.17)** ·
**15:04 (r2.18)** · **15:36 (r2.19)** · **15:38 (r2.19 re-sign)** · **18:28 (r2.20)**.

**Standing procedure:** capture before every sign; restore after; restore onto the **post-sign**
hash; restore as **valid YAML**; verify the parse, not just the gate; **append the log entry**.

**For readers:** if the disclosure fields are absent, do not read `approved: true` as a human
approval. Read it as unknown, check the log, and escalate.
