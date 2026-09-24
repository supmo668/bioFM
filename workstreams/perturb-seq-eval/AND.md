# A&D — perturb-seq-eval: v0.5.0 artifact regeneration (fixes-first, one process)

**Workstream:** `perturb-seq-eval`
**Status:** APPROVED by the principal — 1B1 grill closed "Over and out" 2026-09-24 (D1–D5 below)
**Requirements source:** CTO dispatch #202 (principal-authorised), on top of #201 (verified defects A1–A7) and
`qa/_adhoc/2026-09-23-publication-rigor-review.md` (§ Addendum). No PVR exists for this workstream — this is a
*refinement* of an existing surface, so the lifecycle routes straight to A&D. Recorded in Open questions.
**Scope lock (from #202):** no paper prose, no real/synthetic language pass, no TDI correlations, no action on the
seven unverified leads beyond verified/not. Numbers are expected to move; nothing is tuned to preserve them.

---

## 0. What is actually broken (ground truth, verified this session)

| id | mechanism | evidence |
|---|---|---|
| A1 | trainer & lifecycle JSONLs share 2 of 36 tasks | recomputed: intersection = {SRP72, SAMD1_ZBTB1}; adamson 1/21, norman 1/15 |
| A6 | `hash(s) % 3` strata (PYTHONHASHSEED-salted) **and** a second script | `app_v05.py:217,223`; `app_v05_lifecycle_only.py` re-stratifies in a fresh process and overwrites only `lifecycle_runs.jsonl`, then `prior \| summary` over `provenance.json` (`:118-128, :267-285`). Adamson (quantile strata, not hash) also diverged — the two scripts stack subsets in different orders (`fetch_adamson_all().values()` vs `sorted(glob)`) |
| A2 | seed has three dead ends | `run_agentic_lifecycle` has no `seed` (`loop.py:99-111`); `_cache_key` omits it (`openrouter_client.py:151-164`); `execute_trainer` reads `trainer_proposal.get("seed", 2026)` from a `TrainerProposal` schema with no `seed` field (`trainer_exec.py:23-28`, `proposal_schema.py:69-72`) → `BackboneTrainConfig.seed` is always 2026. 36/36 tasks byte-identical across seeds |
| A4 | random gene substituted as target | `norman.py:110` tests `"+"`, labels use `_` (8/15); `:118-120` `rng.integers(...)`; `app_v05.py:208` same delimiter → doublet stratum empty → 15+0 instead of 15+5. `e2_adamson.py:206-212` same fallback; `loop.py:222-227` index-0 fallback. Backbones consume `target_gene_idx[p]` as the on-target dip feature (`backbones/base.py:52-58`) — doublet tasks were scored against noise |
| A5 | backbone one-hot keyed on names no experiment uses | `optimizers/base.py:34`; real spaces in `bootstrap_and_analyze.py:171-175,293-297`, `rerun_e3_with_real_probes.py:176-181`; `tests/test_optimizers.py:22-26` uses the two names the dict knows |
| A7 | no digest pinned; `_fetch` trusts any existing file | `download.py:34`, `:148-159`; only `min_bytes` guards |
| prov | provenance records nothing that identifies the run | `app_v05.py:397-416`: timings/cost/3 counts/entropies only; sweep kwargs `n_sweep`, `r_sweep`, `backbones` hard-coded (`:110-112`) and unexposed; `total_gpu_seconds ≡ wall_clock_sec` in code but ≠ in the artifact (two-run merge) |
| model_id | served model is never surfaced | `chat_json` loops candidates internally; `propose()` returns `{content, rationale, confidence}` only (`llm_agent_pool.py:150-154`); `LifecycleStep` has no `model_id`/`source` field |

Operational facts: Modal app `perturb-eval-v050`, A100-40GB @ $1.32/h, 6 h timeout, `$28` soft in-loop kill (no
platform cap). Outputs go to volume `perturb-eval-data:/v0.5.0/`, pulled by hand with `modal volume get`. Only
`OPENROUTER_API_KEY` is injected. Prior spend $4.04 / 3.06 GPU-h for 1,944 trainer cells + ~$1 lifecycle rerun.
Tests: Poetry + pytest (~198 pass). Guardrail `tests/test_no_synthetic_generators.py` forbids `default_rng(` +
DGP wording + gene vocab in one file.

---

## 1. Approaches & decision

**Q: patch the two scripts, or collapse to one run path?**

| option | what | trade-off |
|---|---|---|
| A. patch both scripts | crc32 strata in both; keep `lifecycle_only` for cheap reruns | keeps the exact mechanism that produced A1 alive; provenance merge stays a blind `\|` |
| B. **one run path** (chosen) | `app_v05.py` is the only producer; `app_v05_lifecycle_only.py` deleted; strata + ordering deterministic; analyser refuses mismatched task sets | a lifecycle-only rerun becomes impossible by construction — that is the point (#202: "ONE sweep in ONE process") |
| C. new orchestrator | fresh `run_v06.py` | duplicates 400 lines for no gain; PoC-minimal says no |

**Q: seed threading — schema field or explicit parameter?** Explicit `seed: int` parameter through
`run_agentic_lifecycle → LLMAgentPool.propose → chat_json/_cache_key` and `execute_trainer(seed=…)`. The LLM is
not allowed to choose the seed (no `seed` in `TrainerProposal`); it is an experimental control, not a proposal.

**Q: missing target gene — raise where?** Raise at **preflight**, before any GPU work, with the full list of
offending tasks — never mid-sweep after money is spent, never substitute. Sampling draws only from perturbations
whose target genes are all in the HVG vocabulary (an *eligibility filter*, recorded in provenance), so the
stratum-count assertion is meaningful.

**Q: artifact destination?** → Open question D2 (new version dir recommended; never mutate `v0.5.0/`).

---

## 2. Components & interfaces (change surface)

| # | file | change |
|---|---|---|
| C1 | `scripts/modal/app_v05.py` | strata: `zlib.crc32(s.encode()) % k`; Adamson subset order `sorted(...)` by key; delimiter from config; eligibility filter + preflight validation; `assert` stratum counts == requested; sweep kwargs exposed as entrypoint args; provenance writer (C7); provenance as record 0 of each JSONL; write to `/<version>/` |
| C2 | `scripts/modal/app_v05_lifecycle_only.py` | **delete** |
| C3 | `src/perturb_eval/agentic_lifecycle/loop.py` | `run_agentic_lifecycle(..., seed: int)`; thread to pool + trainer; `held_out not in target_gene_idx` → raise (no index-0) |
| C4 | `src/perturb_eval/agentic_lifecycle/llm_agent_pool.py`, `src/perturb_eval/llm/openrouter_client.py` | `propose(..., seed)` → `chat_json(..., seed)`; `_cache_key` includes `seed`; `chat_json` returns `model_id` served; `propose` returns `model_id` + `source: "llm"\|"fallback"` |
| C5 | `src/perturb_eval/agentic_lifecycle/types.py`, `trainer_exec.py` | `LifecycleStep` gains `model_id: str \| None`, `source: Literal["llm","fallback"]`; `execute_trainer(..., seed)` sets `BackboneTrainConfig.seed = seed` |
| C6 | `src/perturb_eval/experiments/norman.py`, `e2_adamson.py`, `data/download.py` | delimiter param (`doublet_delim="_"`, default matches data); missing target → `raise ValueError` listing genes; doublet contract per D1; docstrings corrected |
| C7 | `src/perturb_eval/experiments/e_v05_real_traces.py` | `analyse_v05_run`: skip/validate record-0 provenance; **hard-fail** if `{r.task}` (trainer) ≠ `{r.task_id}` (lifecycle); report `n_tasks` per file; per-role entropy excluding `source=="fallback"` (see D4) |
| C8 | `src/perturb_eval/data/download.py` | pinned `sha256` on all four `DatasetSpec`s; `_fetch` raises when a cached file has no pin (opt-in `trust_unpinned=True` for tests only) |
| C9 | `src/perturb_eval/optimizers/base.py`, `cma_es.py`, `contextual_gp.py`, callers | `config_to_vec(phi, backbones)` with `backbones = tuple(sorted({c.backbone for c in space}))` computed once per optimizer; `nearest_config` threaded |
| C10 | `tests/` | regression tests per §5 |

Preflight (C1, CPU-only, runs first in the same process): fetch+verify digests → build task lists → validate
every target gene ∈ HVG vocab → assert stratum counts → write provenance record → only then start GPU loops.

---

## 3. Data & state

**Provenance record** (`provenance.json` and record 0 of both JSONLs, `{"record_type": "provenance", ...}`):
`schema_version`, `run_id`, `git_sha`, `git_dirty`, `started_at`, `finished_at`, `python`, `lib_versions`
(torch, numpy, scanpy/anndata, modal), `entrypoint_kwargs` (every resolved kwarg: `norman_n_singletons`,
`norman_n_doublets`, `adamson_n_per_bin`, `adamson_n_bins`, `seeds`, `n_top_hvg`, `max_cells_per_pert`,
`n_sweep`, `r_sweep`, `backbones`, `doublet_delim`, `cooldown_sec`, `temperature`), `datasets` (path, sha256,
n_cells, n_genes per file), `tasks` (resolved list per dataset with stratum + eligibility), `tasks_excluded`
(label + reason), `llm_pool` (model roster), `gpu`, `hourly_usd`, `budget_cap_usd`, and on completion
`wall_clock_sec`, `gpu_seconds`, `cost_usd_actual`, counts, entropies. **A new config copy per run:** the
resolved-kwargs block is also written to `configs/runs/<run_id>.json` and committed with the artifacts.

**Record schemas:** trainer row unchanged (`dataset, task, backbone, N, R, seed, msd_topk, wall_sec`).
Lifecycle row: `task_id → task` (aligned key name) — *or* analyser maps; `steps[*]` gain `model_id`, `source`.
Invariants: `set(trainer.task) == set(lifecycle.task)`; for each task, `final_msd_topk` differs across seeds
(not asserted at run time — it is a regression *test* on a fixture, and a report line on the real run).

**Digests:** the three Adamson subsets and Norman are not local. A `--print-digests` CPU preflight on the volume
computes them; they are pinned in `DATASETS` before the sweep; the sweep verifies fail-closed.

---

## 4. Failure handling

| condition | behaviour |
|---|---|
| any target gene not in HVG vocab (after eligibility filter — i.e. a bug) | preflight `ValueError` listing task, gene, vocab size; no GPU time spent |
| stratum count ≠ requested | preflight `AssertionError` with counts per stratum and the eligible pool size |
| cached dataset without pinned digest / digest mismatch | `ValueError`, no download-and-trust |
| task-set mismatch between JSONLs | analyser raises `ValueError` naming symmetric difference; `summary.json` not written |
| LLM call fails / schema invalid | fallback as today, but `source="fallback"`, `model_id=None`; analyser excludes from entropy; counts reported |
| budget cap hit | loop breaks as today; provenance records `budget_hit: true` and partial counts — a partial run is reported as partial |
| Modal timeout (6 h) | resume-safe append already exists; provenance `finished_at` absent ⇒ analyser refuses to summarise |

---

## 5. Per-requirement spec (behaviour + test criteria)

| req | behaviour | test (fails today / passes after) |
|---|---|---|
| W1 determinism (A6) | same kwargs ⇒ identical task lists across two fresh interpreters | subprocess test: run stratification twice with different `PYTHONHASHSEED`; task lists equal |
| W1b single producer | `app_v05_lifecycle_only.py` absent | `test_no_lifecycle_only_script` |
| W2 seed (A2) | `run_agentic_lifecycle(seed=a)` and `(seed=b)` on a fixture yield different `final_msd_topk`; cache keys differ for equal prompts with different seeds | unit on `_cache_key`; integration on fixture with mlp backbone |
| W3 target (A4) | `load_norman_matrix` with `_`-joined doublets classifies them as doublets; a singleton whose target is absent from vocab raises; `loop.py` raises on missing held-out target | `tests/test_norman_loader.py` extended; new `test_missing_target_raises` |
| W3b count | requesting 5 doublets from a pool that yields 0 ⇒ preflight assertion, not 15+0 | `test_stratum_count_assert` |
| W4 analyser | disjoint task sets ⇒ `ValueError`; equal ⇒ summary; record-0 provenance skipped | `test_analyser_rejects_mismatch` |
| W5 provenance | every field in §3 present and non-null (except completion fields pre-finish); record 0 of each JSONL equals `provenance.json` core | `test_provenance_schema` |
| W6 digests (A7) | all `DATASETS` have non-None `sha256`; cached unpinned file ⇒ raise | `test_raises_when_cached_file_has_no_sha_pin`; `test_all_specs_pinned` |
| W7 embedding (A5) | `len({tuple(config_to_vec(c, bb)) for c in space}) == len(space)` for `("linear","mlp","scgpt_small")` | `test_config_to_vec_distinguishes_all_backbones` |
| W8 model_id | each lifecycle step carries `model_id` when `source=="llm"` | `test_step_records_model_id` (client stub) |
| W9 the sweep | one `modal run`, one process, both JSONLs + provenance + config copy; actual spend and GPU-h reported; every gate old-vs-new; the seven leads verified/not | run report to CTO |

Decomposition into build tasks follows the A&D rule: files → failing test → minimal impl → verify → commit.
Sealed tests (test-author) are written from this table.

---

## 6. Decisions — locked by the principal (1B1, 2026-09-24)

| id | decision | consequence for the build |
|---|---|---|
| D1 | **Multi-target contract.** `target_gene_idx: dict[str, tuple[int, ...]]`; on-target dip = mean over the target columns; singletons are 1-tuples | `backbones/base.py` Protocol, `linear.py`, `mlp.py`, `scgpt_small.py`, `loop.py` remap; Norman keeps the pre-registered 15 + 5 design; 41 tasks not 36 |
| D2 | **New dir `artifacts/v0.6.0/`**; volume path `/v0.6.0/`; `configs/runs/<run_id>.json` committed with it; `v0.5.0/` untouched | version reconciliation (pyproject/CHANGELOG) is the CTO's at release, not this build |
| D3 | **Escalate lead 4 (HVG selected on held-out cells) to the CTO before the sweep.** Build of C1–C10 proceeds in parallel; the sweep waits for the ruling | escalation dispatch sent at this boundary; no run without the ruling |
| D4 | **Fold A3 in**: `source: Literal["llm","fallback"]` on `LifecycleStep`; analyser entropy per role over `source=="llm"` rows only, fallback counts reported | same call chain as `model_id` (C4, C5, C7) |
| D5 | **Requirements source accepted**: #202 + review Addendum; no PVR for this refinement | recorded here; `/define` not run |

Superseded open-question text retained below for the record.

### Open questions as grilled


- **D1 — doublet contract.** The backbone Protocol takes one `target_gene_idx: int` per perturbation. For a
  doublet: (a) `tuple[int, ...]` and the on-target dip = mean over both genes (generalises the contract; ~5
  files); (b) run this regeneration singletons-only (`norman_n_doublets=0`, asserted) and state that the
  pre-registered 15+5 design is deferred; (c) doublets get no on-target term (metric differs by stratum — not
  comparable). Recommendation: **(a)**.
- **D2 — artifact destination.** Regenerated files to a new `artifacts/v0.6.0/` (v0.5.0 kept as the retracted
  record) vs overwrite `v0.5.0/`. Recommendation: **new dir**; version label to be confirmed (pyproject says
  0.2.0, CHANGELOG stops at 0.5.0, releases 0.5.1/0.5.2 exist).
- **D3 — lead 4 (HVG selected on all cells incl. held-out) is VERIFIED and sits on the trainer path this sweep
  re-runs.** #202 says do not act on leads. Options: run as-is and report it as a known limitation of the
  regenerated numbers; or escalate to the CTO for a ruling before spending. Recommendation: **escalate first**
  (one dispatch, no run delay if the CTO answers within the build window).
- **D4 — fold A3's `source` field + fallback-excluded entropy in?** Same plumbing as `model_id`; ~30 lines.
  Recommendation: **yes** (the run should not have to happen twice).
- **D5 — no PVR.** Accept #202 + review Addendum as the requirements source for this refinement, recorded here.
