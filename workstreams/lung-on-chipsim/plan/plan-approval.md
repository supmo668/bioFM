---
workstream: lung-on-chipsim
plan_path: workstreams/lung-on-chipsim/plan/build-plan.md
plan_hash: 8be2e69
approved: true
approved_by: Matthew Mo
approval_route: cto-invoked, standing-delegation
invoked_by: biofm/matthew-mo/cto
provenance_of_record: workstreams/lung-on-chipsim/plan/plan-approval-log.md
authorising_rulings:
  - 'CTO rulings 2026-09-16 on §6 quality-gate escalations E6-1 to E6-7 (dispatch #139)'
  - 'CTO rulings 2026-09-16 on §5 escalations E-1 to E-6 (r2.20)'
  - 'principal 2026-09-15 record-content re-ruling — the invariant targets record content and the (accession, name, structure) association'
  - 'principal 2026-09-15 lane ruling, re-confirmed 2026-09-16 — this CTO session owns the lane'
  - 'r2.21 has NO principal ruling — quality-gate findings; r2.8/r2.9 precedent'
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
date: 2026-09-16T18:59
---

# Plan approval: lung-on-chipsim

The human's 1B1 "Over and out" lock in /grill-me IS the final human
plan-review gate. This file records it so /build can verify it.

## Summary
r2.21: E6-1 declarations move to per-project data with path->sha256 or a derived-from-tracked-source claim (24 other-module paths were declared inside this module); E6-2 readable structured containers are always read, never declared, parquet including footer metadata after it carried a whole record invisibly; E6-4 the dispatch waiver covers .md messages only, not arbitrary bytes; E6-5 the scan enforces the accession half and the r2.20 writer helper the name half, neither claiming the other's coverage. E6-6/E6-7 (module extraction, combined entry point with the FAIL in the API) authorised to the agent.

---

## THIS FILE IS NO LONGER THE PROVENANCE OF RECORD

**`plan-approval-log.md` beside it is** (r2.15 item 6). `plan-gate sign` regenerates this file
wholesale on every sign — **seventeen times so far** — preserving nothing below the frontmatter.

## Provenance — how to read this signature

**The finding that drove r2.21 is a false-clean rebuilt one layer beneath the fix for false-cleans.**
A parquet's **footer metadata** carried accession + coined name + structure while the file itself
scanned as `",harmless\n0,1\n"` — the complete record present, absent from the scanned text, reported
by neither half, and certified clean by the guard's own green tests. Metadata stamping is ordinary
and several engines do it by default. Four more of the same character were measured: numpy eliding
list cells past 1000 (an accession at position 1500 of a `groups` list vanished, and `write_compounds`
persists list columns); latin-1 and UTF-16 text classified "undecodable" so a **plain-text** carrier
would have needed a declaration; parquet dispatched on the **filename**, so `UP.PARQUET` and an
extensionless blob fell through — the same case-sensitivity shape the agent had closed three commits
earlier; and a 30 KiB input expanding to 186.9 MiB with `MemoryError` reclassified as "declare it".

**E6-1 is the ruling that matters structurally.** 24 paths belonging to `perturb-seq-eval` and
`paper_standalone` were declared inside *this* module's source, so another team adding a figure turns
this gate red and the repair lands in a file they neither own nor can judge. Declarations now live
with the project that owns the artifact, keyed `path -> sha256` or asserting "derived from tracked
source S, and S is in scope" — a claim a reader can check, where the previous comment only asserted
that none of them was a DrugBank artifact.

**The agent escalated this exact class one dispatch earlier and then decided it unilaterally here**,
and said so unprompted. The rule is now in the plan: *a decision that looks like bookkeeping is still
a shape decision if it assigns ownership.*

**E6-2 removes the `h5ad` from declare-and-skip.** It was the only readable, structured, record-shaped
container in a list of rendered figures — the CTO's own argument for reading parquet applied to it
verbatim. Security scanned it (46 nodes, every string dataset and attribute): zero hits, so the change
is clean rather than urgent. Readable structured containers are now always read.

**E6-5 narrows a CTO-accepted claim.** The §5 report said the format most likely to carry a whole
record was now visible; that is true only for the **accession** half. The plan now states the split:
the scan covers accessions, the r2.20 writer helper covers names, and neither claims the other.

**The process change was vindicated.** Reviewers worked on a throwaway copy; four reviewers, 21
mutants in one review, and all four independently confirmed the real worktree ended byte-identical.
Three rounds of written protocol had failed. *When a rule fails repeatedly against competent people,
it needs a mechanism, not more emphasis.*

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
    your failure mode and your repair path.

## Incident — `plan-gate sign` destroys this disclosure. SEVENTEEN occurrences.

**2026-09-03 02:08** · **2026-09-14 13:28 / 15:24** · **2026-09-15 01:01 (`0b8d0c3`, second CTO
session) / 01:40 / 11:19 / 12:43 / 15:16 / 16:15** · **2026-09-16 14:04 (third CTO session — restored
from a stale capture, regressing the hash) / 14:08 / 15:00 / 15:04 / 15:36 / 15:38 / 18:28 / 18:59**.

**Standing procedure:** capture before every sign; restore after; restore onto the **post-sign**
hash; restore as **valid YAML**; verify the parse, not just the gate; **append the log entry**.

**For readers:** if the disclosure fields are absent, do not read `approved: true` as a human
approval. Read it as unknown, check the log, and escalate.
