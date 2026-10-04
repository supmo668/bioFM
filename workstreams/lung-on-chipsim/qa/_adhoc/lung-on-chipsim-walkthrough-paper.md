---
type: walkthrough
cut: paper
workstream: lung-on-chipsim
branch: lung-on-chipsim (origin tip c04e701, 2026-09-20) · main 6d0d6c5
date: 2026-09-28
surface_local: docs/hacp/lung-on-chipsim/index.md
surface_notion: https://app.notion.com/p/b7c749bd250d83dab06201f85d61ee49
surface_notion_note: "ChipSim (bioFM) — Index, the HACP L1 subproject row; SOURCE OF TRUTH since 2026-10-03 (principal); the floor mirrors it"
surface_artifact_superseded: https://claude.ai/artifact/VL8WMBZERBehinw1z36yQm
surface_notion_draft_superseded: https://app.notion.com/p/3e9ac60c018c81618c71c5c6c192cb06
supersedes_counts_of: lung-on-chipsim-walkthrough-product.md (2026-09-19)
renewed: 2026-10-03 — Stage 1 closed and archived 2026-10-01; the index now carries the Stage 2 build-phase unblock ledger, timeline and kickoff checklist
---

# The rig is built; the experiment has not run — and the decision record is the result

**Paper cut.** Written for a referee deciding whether the methodology is sound before any result
exists, which is the genre the project chose on 2026-09-26 (a Stage 1 registered report). The
product cut of 2026-09-19 stands; this cut supersedes its counts, not its verdict.

The review surface is hierarchical and follows the HACP index tree: one entry page and six
section leaves, each intended as a row under the matching bioFM `§section`.

| Page | Holds |
|---|---|
| [index](../../../../docs/hacp/lung-on-chipsim/index.md) | verdict, where the work stops, status at a glance, eleven decisions taken, six decisions needed |
| [§vision](../../../../docs/hacp/lung-on-chipsim/vision.md) | the one claim under test, the minimum viable chip, the three controls |
| [§design](../../../../docs/hacp/lung-on-chipsim/design.md) | three rings, the five-call environment contract, the 53-revision decision record, eight divergences |
| [§build](../../../../docs/hacp/lung-on-chipsim/build.md) | artifacts measured on the branch, the human-owned ledger, what is in flight |
| [§eval](../../../../docs/hacp/lung-on-chipsim/eval.md) | the measured suite, nine receipts, the pre-registered commitments, the two power simulations |
| [§risk](../../../../docs/hacp/lung-on-chipsim/risk.md) | eleven known gaps |
| [§decision](../../../../docs/hacp/lung-on-chipsim/decision.md) | twelve items the principal owns |

## Objectives against the request

The request assumed project objectives were met. They are not, and the surface says so on its
first line rather than compiling around it: the one claim under test (Spearman ρ ≥ 0.6 on exposure
ordering, MoA targets in the top-10, 90% Mondrian coverage) cannot yet be evaluated because no
fit, no coverage, no frozen evaluator and no curated chip records exist. What *is* reviewable is
the methodology, its pre-registered commitments, and a contemporaneous, hash-locked record of how
the methodology was chosen, 45 of 53 revisions under a recorded delegation. That is the paper's
claim, and it is supported by artifacts a referee can open.

## Measured for this cut

| | |
|---|---|
| 1,013 passed / 3 failed / 9 skipped / 16 network tests deselected | offline suite on `c04e701`, fresh checkout, 2026-09-28 |
| 39 failed | the same suite in a checkout under `/tmp`: the output-roots guard refused the temp root because the project sat inside it — the r2.23 defence, working |
| 10,318 / 16,953 | source / test lines, 37 test modules |
| 53 | hash-locked plan revisions on `main`; 45 standing-delegation, 4 principal-directed, 2 human-direct, 2 mixed |
| 3 of 5 | slice-1 human inputs delivered (T2, T8, T18); T1 half; T14 absent |
| 0 | simulation, fit or evaluation runs |

## What this does not claim

- No biological result has been produced, reviewed or validated.
- The M1 transport code and the E-22/E-23 range are known from CTO records; they are not on the remote and were not measured here.
- The 6,802-compound count is the 2026-09-19 reading; the payload could not be re-read from this checkout.
- Nothing here writes a DrugBank accession or pairs an identifier with a substance.

## Placement in the HACP Index

The Notion HACP Index (database `3e5749bd…`, the CTO's `docs.notion.scopes.cto` target) is in a
workspace this session's Notion connection cannot reach; the pages were therefore created as
private drafts in the connected workspace for the principal to move, with the floor copies above
as the local source. Each section page should become a row with `Parent` = the matching bioFM
`§section`, and the index page a row under `bioFM — Index`, read back after placing.
