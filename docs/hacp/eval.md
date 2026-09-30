# §eval — bioFM

<!-- HACP L1 · local source; the Notion row "bioFM · eval" mirrors this file. -->

**Tag:** `§eval` · **Layer:** L1 · **Holds:** what proves it works — gates, receipts, sealed suites, run records · **Reaches:** each workstream's `qgr/` directory and approval log

**TL;DR** — Two workstreams have verifiable receipts; the third has none by design. Every number below says whether it was measured for a receipt, carried forward, or reported.

## Evidence, by workstream

| Workstream | Claim | Value | Kind | Artifact |
|---|---|---|---|---|
| aviary-biosim | F08 pr-prep receipt verifies against `origin/main` | Hash E `4217902` | **measured** 2026-09-26, re-verified 2026-09-28 under airdlc 0.71.0 | `workstreams/aviary-biosim/qgr/…-4217902.md` |
| aviary-biosim | science suite green in default order, importlib mode and each file alone | 328 passed; 445 across the loop | **measured** 2026-09-26 | same receipt |
| aviary-biosim | deliberately broken copies of the guard caught | 48 live killed + 1 retired (the re-gate added 13; catalogue holds 49 entries) | **measured** 2026-09-26 | same receipt (`4217902`); the 36 + 1 figure was the 2026-09-25 gate, superseded |
| aviary-biosim | white paper evidence files exist (drain-1 rerun, timeline, science from a hash-recorded input, agent run, taxonomy, plugin/repo tests) | 10 files under `paper/evidence/` | **present, not yet reviewed** — CTO rigour review begins after Task 13 and the A7 claims check | Aviary-BioSim branch `whitepaper` |
| perturb-seq-eval | test suite after amendment-2 fixes | 925 passed | **measured** 2026-09-27 | commit `4840f0d`; QG receipt pending at the next boundary |
| perturb-seq-eval | pre-registration amendment 2 locked | `3bf2a9a` | **recorded** | pre-registration file + approval log |
| perturb-seq-eval | v0.6.0 pre-registered gates | 4 / 5 PASS (H5 FAIL, ρ = 0.286); 123/123 runs, 0 fallbacks / refusals / mismatches; $8.93 | **measured** 2026-09-29, landed PR #8 (`5a45d4a`) + PR #12 (`5637497`) | [result review (Notion)](https://app.notion.com/p/3eb749bd250d8112a6aeca8ae015149c) · `workstreams/perturb-seq-eval/qa/_adhoc/v060-result-review.md` |
| lung-on-chipsim | results | none | **absent by design** — `fit.py` refuses to run without sourced priors; evaluator not yet frozen (M0c) | `workstreams/lung-on-chipsim/paper/2026-09-26-stage1-registered-report-design.md` §1 |
| lung-on-chipsim | content-guard gates run on E-22/E-23 | 9 gates; gates 6, 7, 8 and 9 FAIL accepted — gate 9 (2026-09-29): 6 defects / 19 findings / 5 readers, all invisible to 1,257 tests; E-23 CLOSED at the scope reached, no receipt | **measured**, each survivor paired with why nothing saw it | `workstreams/lung-on-chipsim/qgr/`, approval-log rows 47–55 |

## What the gate can and cannot see

The recurring finding across all three workstreams has one shape: **a mechanism reports success while the property it exists to guarantee is absent.** The gates catch a task that fails its test every time; they are blind to a task that passes for the wrong reason. Every hardening pass on record (aviary-biosim's five, lung-on-chipsim's seven gates, the perturb-seq-eval estimator re-check) is of the second kind and was caught by measurement, not by the gate.

## Read the source

- `workstreams/<ws>/qgr/` — signed receipts per workstream
- `workstreams/<ws>/plan/plan-approval-log.md` — the append-only record of what was approved, by which route, and what was later corrected
