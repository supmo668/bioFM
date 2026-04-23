# Running the pipeline against real data and a real LLM

This document covers the "non-synthetic" path:

- **Real data**: Adamson et al. 2016 Perturb-seq (K562 cells, UPR screen).
  Fetched via `scripts/fetch_adamson.py` from the Zenodo-hosted scPerturb
  mirror (record 13350497), which is the authoritative community-curated
  redistribution of GEO series [GSE90546].
- **Real LLM**: `nvidia/nemotron-3-super-120b-a12b:free` via OpenRouter.
  Verified live on 2026-04-18.

The framework tests in `tests/` never touch the network and remain valid with
or without a live run.

## 1. Secrets and environment

1. `cp .env.example .env` (already-tracked example lives at repo root).
2. Fill in `OPENROUTER_API_KEY`. The file `.env` is gitignored globally; do
   not commit it.
3. Export into your shell *or* rely on the pipeline to load `.env` at the
   top of the CLI entrypoints (see `src/perturb_eval/_env.py`).

Required variables:

| Variable | Purpose | Default |
|---|---|---|
| `OPENROUTER_API_KEY` | secret — required | — |
| `OPENROUTER_MODEL` | model slug | `nvidia/nemotron-3-super-120b-a12b:free` |
| `OPENROUTER_BASE_URL` | API root | `https://openrouter.ai/api/v1` |
| `OPENROUTER_REFERER` | site-attribution header required by OpenRouter | `https://example.invalid` |
| `OPENROUTER_APP_TITLE` | shown in your dashboard | `perturb-seq-eval` |

## 2. Fetch the real Perturb-seq data

```bash
cd projects/perturb-seq-eval
python3 scripts/fetch_adamson.py                 # downloads ~34 MB
# optional: larger subsets (~140 MB, ~470 MB)
python3 scripts/fetch_adamson.py --subset 10X005
```

Output:

```
data/Adamson2016_pilot.h5ad            33 MB  (GSM2406675, pilot TF screen)
```

Verify it parses:

```bash
python3 -c "from perturb_eval.adamson_loader import load_adamson_h5ad; print(load_adamson_h5ad('data/Adamson2016_pilot.h5ad'))"
```

Expected output: `AdamsonQC(n_cells=5768, n_genes=35635, perturbation_names=('62(mod)_pBA581', '*', 'BHLHE40_pDS258', 'CREB1_pDS269', 'DDIT3_pDS263', 'EP300_pDS268', 'SNAI1_pDS266', 'SPI1_pDS255', 'ZNF326_pDS262'), …)`.

### Dataset provenance

The scPerturb Zenodo record documents the processing pipeline (QC thresholds,
guide-RNA assignment, doublet filtering). The original experiment is:

> Adamson, B. et al. *A Multiplexed Single-Cell CRISPR Screening Platform
> Enables Systematic Dissection of the Unfolded Protein Response.* Cell
> 167, 1867–1882 (2016). doi:10.1016/j.cell.2016.11.048

## 3. Configuration

All runtime configuration lives in `configs/live.yaml`. Key knobs:

- `llm.model` — model slug.
- `llm.max_tokens` / `llm.temperature` — cap the rater cost.
- `data.perturbations` — which perturbations become "tasks". Empty list = all non-controls.
- `rater.prompt_path` — severity rater prompt (the PR-ready one lives under
  `massgen_skill_draft/prompts/severity_rater.md`).
- `orchestration.synthesise_trace_if_missing` — when `true`, the smoke
  pipeline builds a minimal 5-agent, 2-round trace so the LLM rater can be
  exercised even without a real orchestrator.
- `logging.save_llm_traces` — every request+response logged to JSONL for
  auditability.

## 4. End-to-end smoke test

```bash
python3 scripts/live_smoke.py --config configs/live.yaml
```

This script:

1. Loads `.env` and validates the OpenRouter key.
2. Loads `data/Adamson2016_pilot.h5ad` via `adamson_loader`.
3. Turns each real perturbation into a task name (e.g. `DDIT3_pDS263` → `DDIT3 knockdown`).
4. Synthesises a minimal 5-agent, 2-round trace (the pilot is not a
   multi-agent simulation platform on its own).
5. For each of the `AgentVote.reason` strings in the synthetic trace, calls
   OpenRouter's `/chat/completions` with the severity prompt.
6. Projects the votes into a `RunTrace`.
7. Computes ACE, CSD, ΔACE, ΔC, WFR, TDI and prints them.
8. Appends a timestamped record to `artifacts/live/llm_calls.jsonl`.

Expected time: ~10 LLM calls × ~2 s/call = under a minute. Cost on
`:free` tier: $0 (quota permitting).

## 5. What the live run validates

It validates *end-to-end wiring*: configuration parsing, `.env` loading,
OpenRouter HTTP client, severity extraction, RunTrace projection, metric
rollup, artifact persistence. It does **not** validate that the metric
ranks real-world difficulty — that is a longer study outlined in
`docs/THESIS.md` §§6-8 and remains future work.

## 6. Costs, rate limits, and privacy

- OpenRouter `:free` models carry soft per-minute rate limits and daily
  quotas; the backend includes exponential-backoff retry (3 attempts,
  doubling delay) on 429/500/502/503/504.
- `logging.save_llm_traces` writes every prompt to disk. Inspect and scrub
  before sharing.
- The severity prompt contains only `AgentVote.reason` strings; no
  experimental counts or patient-level data are sent to the LLM.
