# §risk — ChipSim (lung-on-chipsim)

<!-- HACP L2 leaf · local source; Parent = bioFM §risk. Compiled 2026-09-28. -->

**Tag:** `§risk` · **Layer:** L2 (leaf under [bioFM §risk](../risk.md)) · **Holds:** known gaps, proxies, anything unverified · **Reaches:** the approval log, the gate reports, the README's own open items

**TL;DR** — Eleven gaps are open. The one that costs the most is not technical: two weeks of effort
went into making the verification layer trustworthy rather than into moving the science forward,
and the CTO's own gate-7 diagnosis was "machinery growing faster than the evidence that any of it
works". The recurring defect family across the fleet also applies here: a check derives a
correctness-relevant answer from something adjacent to the thing it describes.

## Known gaps

| # | Gap | What it means for a reader | Status | Where recorded |
|---|---|---|---|---|
| 1 | **The verification layer is outgrowing its evidence.** E-21 to E-23 have been through seven gates on two clauses; gates 6 and 7 failed on claims wider than their checks and on axes that rejected nothing unique. | The content guard is real and has caught real faults, including two in the CTO's own instructions and one in the approval log itself, but the marginal gate is now expensive. | Open — r2.49 shrinks the tree; gate 8 carries a stopping rule that hands the decision to the principal | [approval log](../../../workstreams/lung-on-chipsim/plan/plan-approval-log.md) rows 41–53; [product walkthrough](../../../workstreams/lung-on-chipsim/qa/_adhoc/lung-on-chipsim-walkthrough-product.md) § The risk worth naming |
| 2 | **The panel seal detects edits, not ratification.** The digest is unkeyed over public content; the TTY gate turns an accident into a deliberate circumvention and nothing more; an editor who removes the seal line bypasses detection. | Nothing in the repository proves a human ratified the panel. Real signing against a human-held key is a v2 decision, deferred. | Open, stated at its real size | [README](../../../projects/lung-on-chipsim/README.md) § Known open items |
| 3 | **Half of T1 is owed.** `PROVENANCE.md`, the licence posture in the human's own words, has not been written; the CTO deliberately did not draft it. | The structured commitment exists; the prose the plan requires does not, so T11's live integration condition is still deferred. | Open — principal | `data/raw/drugbank/provenance.yaml` header on the branch |
| 4 | **T14 is absent, and stale labels redefine the groups.** The uncertainty stack conditions on P-gp substrate status; the 2015 snapshot's edges are old. | Until a human adjudicates against current literature, every coverage claim's conditioning groups are undefined. Genuinely uncertain compounds stay `unknown` and are excluded from both groups rather than guessed into one. | Open — principal | [build plan](../../../workstreams/lung-on-chipsim/plan/build-plan.md) T14; [§decision](decision.md) |
| 5 | **Coverage precision at n ≈ 20 per group.** The three-way allocation keeps the conformal bar valid but the estimate wide. | A coverage number quoted without its CI at this n reads a wide interval as a clean result. The reporting obligation is binding. | Accepted, with a binding obligation | [ADR-0002](../../../projects/lung-on-chipsim/docs/adr/0002-poc-conformal-calibration-at-20-per-group.md) |
| 6 | **The power figures are upper bounds.** Affinities are treated as noise-free; Murcko scaffolding is blind to acyclic analog series; ICC is not derivable from structure before Boltz-2 has run. | The audit can demonstrate a large moiety-sensitivity advantage and cannot rule out a modest one. | Recorded on the model-card obligations | [ADR-0003](../../../projects/lung-on-chipsim/docs/adr/0003-power-floor-and-stratified-roster.md), [ADR-0004](../../../projects/lung-on-chipsim/docs/adr/0004-pair-stratum-is-curated-not-discovered.md); `audit/series.py` |
| 7 | **The remote is eight days behind the worktree.** `origin/lung-on-chipsim` stops at `c04e701` (2026-09-20). The M1 transport code, E-22 and E-23 exist only in the principal's local worktree and are known here from CTO records. | Nothing after 2026-09-20 can be verified from the repository; this review's counts for that work are recorded, not measured. | Open — principal (push) | measured 2026-09-28; [bioFM §decision](../decision.md) item 2 |
| 8 | **The identifier constraint was breached twice by subagents.** The paper design names it as the principal's retroactivity item H. | Any Stage 1 draft must describe the *form* of an identifier and never pair a value with what it denotes; the shape-only guard cannot know what a value denotes. | Open — principal decides retroactive scope | [paper design](../../../workstreams/lung-on-chipsim/paper/2026-09-26-stage1-registered-report-design.md) §7 |
| 9 | **The module README is stale on both branches.** It still reports 284 tests and 0 of 5 human artifacts; the branch has T2, T8 and T18 delivered and roughly a thousand tests. | A reader of the README alone under-counts what exists. This index is the corrected count until the README is regenerated. | Open — a docs task for the worktree agent | [§build](build.md) |
| 10 | **A second writer on the tree.** The T18 iteration record says a second writer explains why the roster landed and its provenance did not; the one-session-per-tree rule exists because a moving tip voids receipts. | Receipts are only as good as the sole-writer premise; the plan records the 2026-09-15 mis-application of that rule as a lesson. | Recorded; the rule stands | branch tip commit `c04e701`; build plan global constraint (r2.15) |
| 11 | **One guard test encodes the host filesystem as a premise.** The case-conflation test constructs `Data.csv` and `data.csv` and expects the scan to refuse; on a case-sensitive volume they are two files and nothing conflates. | The suite is green only on APFS/NTFS-style hosts; on Linux CI it would report one failure that is not a defect in the guard. Skip on case-sensitive volumes, or construct the conflation explicitly. | Open — a test fix for the worktree agent, found 2026-09-28 | [§eval](eval.md), measured run |

## Also unverified, stated plainly

- The 6,802-compound count was read from the parquet on 2026-09-19; this review could not re-read it because the DVC payload lives on the principal's machine and only the digest is tracked.
- The M1 code volume (~920 lines) is the paper design's measurement of 2026-09-26, not this review's.
- No LBM has been run: no Boltz-2, no ESM-2, no atlas prior. The admission tests exist as text.

## Read the source

- [`plan/plan-approval-log.md`](../../../workstreams/lung-on-chipsim/plan/plan-approval-log.md) — the E-21 to E-23 range, rows 41–53
- [`projects/lung-on-chipsim/README.md`](../../../projects/lung-on-chipsim/README.md) § Known open items — the seal's residual limit stated at its real size
- [`grill-2026-09-15-r2.15-draft.md`](../../../workstreams/lung-on-chipsim/grill-2026-09-15-r2.15-draft.md) — the sole-writer rule and its mis-application

Back to the [index](index.md).
