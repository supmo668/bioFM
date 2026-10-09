# §build — bioFM

<!-- HACP L1 · local source; the Notion row "bioFM · build" mirrors this file. -->

**Tag:** `§build` · **Layer:** L1 · **Holds:** phases, branches, what is in flight · **Reaches:** each workstream's build plan and worktree branch

**TL;DR** — Three workstreams in flight. The aviary-biosim white paper is a draft PR under the CTO's A7 rigour review; perturb-seq-eval v0.6.0 has landed and its deposit is prepared but held for the principal's go; lung-on-chipsim's Stage 1 closed at a failed final gate and was archived; its Stage 2 build phase is under way on a separate, unmerged branch.

## In flight

```mermaid
flowchart LR
  classDef done fill:#f1f5f9,stroke:#94a3b8,color:#334155
  classDef live fill:#fef9c3,stroke:#ca8a04,color:#713f12
  classDef wait fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
  A1["aviary-biosim F08<br/><small>landed · 301e7fc6</small>"]:::done
  A2["aviary-biosim #272<br/><small>white paper · draft PR #2 · A7 review</small>"]:::live
  L1["lung-on-chipsim E-23<br/><small>CLOSED at gate 9 FAIL</small>"]:::done
  L2["lung-on-chipsim Stage 1<br/><small>final gate FAIL · archived</small>"]:::done
  L3["lung-on-chipsim Stage 2<br/><small>M1 input contracts · unmerged branch</small>"]:::live
  Q1["perturb-seq-eval v0.6.0<br/><small>landed · 4/5 gates</small>"]:::done
  Q2["perturb-seq-eval deposit<br/><small>prepared · HELD for the principal's go</small>"]:::wait
  A1 -->|"main merged into"| A2
  L1 -->|"time box"| L2
  L2 -->|"12 rulings 2026-10-04"| L3
  Q1 -->|"deposit-prep 5407606"| Q2
```
*Red waits on the principal; yellow is in progress; grey is closed (landed or archived).*

| Workstream | Branch / plan | State | Next boundary |
|---|---|---|---|
| aviary-biosim | `whitepaper` @ `c66e64c` **pushed**; draft PR [Aviary-BioSim#2](https://github.com/supmo668/Aviary-BioSim/pull/2); receipt `2a9b966` CTO-verified | #272 Tasks 0–13 complete; pr-prep gate closed (76 raw → 13 fixed, 7 routed to the CTO); suites at `c66e64c` 328/42/17/122, mutants 48/48+1 | **CTO A7 rigour review** — principal go 2026-10-09, in progress; the draft does not merge until it closes. Then the CTO-owned routed findings D1, D9, D15/D16, D17 and D18 prep |
| lung-on-chipsim | **ARCHIVED 2026-10-01** — branch unlanded, unpushed; record preserved on main · `lung-on-chipsim` @ `8face11`; plan r2.50c (`ae894db`) | **E-23 CLOSED** at gate 9 FAIL (same family; no receipt; no r2.51) under the principal's time box; five mechanisms in, requirement 5 descoped to W/F/C/N reporting; findings → Stage 1 limitations | Stage 1: none — closed at a failed final gate (2026-10-01, no receipt). **Stage 2** build phase (twelve principal rulings 2026-10-04): M1 input contracts built on `claude/inspiring-archimedes-h0we1b` (9 commits not on main, last 2026-10-08); what remains is human-written scientific input, one signature and the CTO's branch cut — see [ChipSim (bioFM) — Index](https://app.notion.com/p/b7c749bd250d83dab06201f85d61ee49) |
| perturb-seq-eval | v0.6.0 landed (PR #8 `5a45d4a`, PR #12 `5637497`, no release); deposit-prep `5407606` | sweep valid ($8.93; H1–H4 PASS, H5 FAIL); deposit metadata generated from and tested against the manuscript and run evidence, 1183 tests green, nothing submitted | apply the S1 ruling (remove `llm_key_source` everywhere, amend the manifest hash) → deposit **held** for the principal's explicit go |
| cellforge-agents | — | not surfaced this cycle | — |

## Presentations

| Workstream | Kind | What it shows | Surface | Written |
|---|---|---|---|---|
| perturb-seq-eval | Presentation (result review) | the v0.6.0 abstract with resolved numbers, the five pre-registered gates (H1–H4 PASS, H5 FAIL, tally 4/5 as pre-registered), run validity (0 fallbacks / refusals / mismatches, $8.93), what is not claimed | [HACP row (Notion)](https://app.notion.com/p/3eb749bd250d8112a6aeca8ae015149c) — Presentation · §eval · indexed by *bioFM · eval*. Source: `workstreams/perturb-seq-eval/qa/_adhoc/v060-result-review.md` | 2026-09-29 / 2026-09-30 |
| aviary-biosim | Presentation (walkthrough + product cut) | the v2r loop and `BioSimEnv` placed in the system, the five decisions taken, the six HACP sections at `ab8f6f5`, and what is done / owed / undecided at the end of the workstream | [HACP row (Notion)](https://app.notion.com/p/3eb749bd250d810abd55ffd606eae42b) — Presentation · §build · indexed by the subproject row [*aviary-biosim (bioFM) — Index*](https://app.notion.com/p/3ec749bd250d81a9acc5eb3fef50c4aa) (re-indexed 2026-10-01 on the principal's direction; local source `docs/hacp/aviary-biosim/index.md`), written 2026-09-30 (the interim web Artifact is superseded). Source: `workstreams/_adhoc/aviary-biosim-walkthrough.md`, `…-walkthrough-product.md` | 2026-09-28 |
| lung-on-chipsim | Presentation (product cut) | the rig is built, the experiment has not run: the 6,802-compound reference table and every downstream step waiting on a human-owned input; state re-measured 2026-09-29 (T18 delivered, T14 0/26, no runs) | [HACP row (Notion)](https://app.notion.com/p/3eb749bd250d81daa9f9f674cde3c60f) — Presentation · §build · indexed by the subproject row *ChipSim (bioFM) — Index* (moved from *bioFM · build* 2026-10-01, matching aviary-biosim), written 2026-09-30 (the two web Artifacts are superseded). Source: `workstreams/lung-on-chipsim/qa/_adhoc/lung-on-chipsim-walkthrough-product.md` | 2026-09-19 / 2026-09-29 |

## Convention

No boundary is claimed without a receipt a third party can verify; no plan runs unsigned; a plan whose text changes is re-signed, never patched. Merges only — the fleet's merge-bases are never rewritten.
