# perturb-seq-eval v0.6.0 — result review

<!-- HACP Presentation · Project=bioFM · Section=eval · local source; the Notion row (CTO-written, https://app.notion.com/p/3eb749bd250d8112a6aeca8ae015149c) mirrors this file.
     Written by the CTO 2026-09-29 from the landed tree (bioFM main @ 5a45d4a, PR #8) and the run artifacts of
     20260929T035447Z-ce5f237 (prereg_version v0.6.0-a4). Every number below is read from summary.json /
     provenance.json through the manuscript's generated macros, never typed. -->

**Paper:** *Does Agent Confidence Entropy Predict Task Difficulty? A Pre-registered, Provenance-Complete Test of Agentic Hyperparameter Tuning for Perturb-seq* — manuscript at `projects/perturb-seq-eval/paper/paper.tex` (compiles: 15 pages), filled from `artifacts/v0.6.0/summary.json` via `scripts/paper/fill_v060_numbers.py` (`--check` matches the artifacts).

## Abstract (as in the manuscript, numbers resolved)

Multi-agent group-generation systems spend test-time compute uniformly across tasks. We ask whether the agents' own confidence-and-critique trace predicts how hard a task is, which would let the compute be allocated adaptively. Taking as testbed a five-agent orchestrator for Perturb-seq response prediction inspired by CellForge and operated via MassGen, we define four compute-free trace metrics — Agent Confidence Entropy (ACE), Critique Severity Dispersion (CSD), a convergence signal (ΔC), and a Winner Flip Rate (WFR) — and their composite, the Task Difficulty Index (TDI). We pre-register five hypotheses with gates: attainable error on Adamson 2016 (CRISPR interference) and Norman 2019 (CRISPR activation), the Architect agent's backbone-choice entropy, the rank correlation of each TDI component with held-out error within each dataset, and the transfer of an Adamson-fitted TDI to Norman. *(Full abstract text continues in the manuscript; the result sentences are summarised in the table below rather than paraphrased.)*

## Pre-registered gates — the result

| Gate | Pre-registered test | Value | Verdict |
|---|---|---|---|
| H1 | Adamson trainer-oracle median MSD@top-20-DEG < 0.20 | 0.1315 (CI 0.111–0.149, n = 21) | **PASS** |
| H2 | Norman median MSD < 0.30 | 0.1842 (CI 0.092–0.395, n = 20; doublets median 0.517) | **PASS** |
| H3 | Architect backbone-choice entropy ≥ 0.5 nats | 0.859 nats (Miller–Madow 0.862, descriptive) | **PASS** |
| H4 | any of six within-dataset Spearman ρ > 0.5 | 4 of 6 pass — carried by 1−ΔC and TDI_lifecycle in both datasets (ρ 0.66–0.70) | **PASS** |
| H5 | Adamson-fitted TDI transferred to Norman, ρ > 0.4 | ρ = 0.286 (n = 20; CI −0.244–0.726) | **FAIL** |

Tally 4 / 5, exactly as pre-registered. **ACE correlates negatively with held-out error in both datasets** (ρ −0.63 Adamson, −0.38 Norman) — opposite to the pre-registered direction; reported as a result, any reading of the sign is exploratory, and a test of it is a new pre-registration.

## Validity of the run (why the numbers can be trusted)

- 123/123 lifecycle runs, 1845 LLM steps, **0 fallback steps, 0 cache hits, 0 refusals, 0 served-model mismatches** (1846 calls; one `max_tokens` retry that succeeded).
- Roster pinned by model id (Haiku 4.5 × 4 roles, Sonnet 5.5 Validator on a different tier); every call records `stop_reason`, served model, usage; no `fallbacks` parameter ever sent.
- Spend **$8.93** total (LLM $3.52 + GPU $4.05 + prior $1.35) against the pre-registered $12 stop / $28 kill / $30 ceiling — no line reached. Projection was $7.19; GPU wall-clock ran longer than modelled.
- Amendment 4 locked before any data (`a48ae5f` → `535cb68` → `00fae29`); the run manifest is hashed (`323af965…`); the AnthropicClient gated with a receipt (`36b0e1d`, derived `47e2523`) before the relaunch; the land receipt `d154d52` verified at PR #8.

## What this does not claim

Single model family (no cross-family generality); same-family judge on a different tier, residual bias acknowledged; n = 21/20 with bootstrap CIs; H5 failed and stays failed; the ACE sign is a finding to test next, not a claim.

## Where to read

PR #8 · run report `workstreams/perturb-seq-eval/qgr/v060-run-report-20260929T035447Z-ce5f237.md` · pre-registration `projects/perturb-seq-eval/paper/PREREGISTRATION.md` (amendments 2–4) · artifacts `projects/perturb-seq-eval/artifacts/v0.6.0/`.
