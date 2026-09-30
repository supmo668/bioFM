# Build Plan — perturb-seq-eval: v0.6.0 regeneration (fixes first, one sweep)

**Workstream:** `perturb-seq-eval` · **A&D:** `workstreams/perturb-seq-eval/AND.md` (APPROVED 2026-09-24, D1–D5)
**Authority:** CTO #202 (principal-authorised). **Status:** r3 — grilled 2026-09-24. r2 added T8b (CTO #227 ruling (ii)); r3 records the /grill-me decisions G1–G3 below.
**Project root for every path below:** `projects/perturb-seq-eval/` unless prefixed `workstreams/`.

## Goal
Make the artifact set provably the output of one process — deterministic task draw, a seed that reaches
the trainer and the LLM cache, no silent target substitution, an analyser that refuses mismatched files,
a provenance record that identifies the run — then run the sweep once, into `artifacts/v0.6.0/`, and report.

## Global constraints (from #202 + A&D)
- Order is the point: P1 → P2 → P3 → P4 land and are green **before** P5 runs anything on Modal.
- Every task: **files → failing test → minimal impl → verify → commit**. No stubs, no TODOs.
- Nothing is tuned to preserve 0.147 / 0.131 / 0.36. A gate that flips to FAIL is reported as FAIL.
- Out of scope: paper prose, language pass, TDI correlations, the seven leads (verified/not only — done),
  #203/#204 (queued/held).
- Commit path: `git-safe-commit` only; `--boundary iteration` at each phase's last commit after `/iteration-complete`.
- Guardrail `tests/test_no_synthetic_generators.py`: no file may combine `default_rng(` + DGP wording + gene vocab.
- Sealed-referee TDD: `tests.referee_command` is **unset** in `agency.yaml`, so no sealed suite can be refereed in
  this repo yet. `/build` uses visible tests + the reviewer agents. Flagged in the report (not fixed here — config
  is the CTO's).

## Grill decisions (principal, 2026-09-24)
- **G1 — env pin.** T0 pins a compatible `anndata`/`h5py` pair so `test_adamson_combined` is green locally; the same
  pins go into the Modal image in `app_v05.py`. Declares `pydantic` + `requests` in `pyproject` `dependencies`.
- **G2 — LLM key.** The CTO provisions `OPENROUTER_API_KEY` via the Infisical MCP (value never in a transcript).
  T23 checks presence only and refuses to launch without it. P1–P4 do not need it.
- **G3 — TDD mode.** Visible failing tests first + `/quality-gate` reviewer agents at every boundary; the unset
  `tests.referee_command` is reported to the CTO in T25, not fixed here.

## Tech stack / runner
Poetry is not installed on this machine; `uv` is. **T0** creates `.venv` (Python 3.12, gitignored) and records the
baseline. All `pytest` commands below mean `.venv/bin/python -m pytest`.

## Execution order
P0 (T0) → P1 (T1–T6) → P2 (T7–T11) → P3 (T12–T17) → P4 (T18–T21) → P5 (T22–T25). P5 is additionally gated on:
(g1) `plan-gate verify` = 0; (g2) the CTO's ruling on the lead-4 escalation — **satisfied by #227: (ii), fix in this build → T8b**; (g3) `OPENROUTER_API_KEY` present in
the environment (presence check only) and `modal profile current` succeeds; (g4) T23's cost estimate ≤ $8.

---

## P0 · Scaffold

### T0 · Runner + baseline — **3 min + install time**
- **Files:** none committed (`.venv/` is gitignored). `workstreams/perturb-seq-eval/plan/baseline.md` (new).
- **Do:** `uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -e . pytest pytest-cov pydantic anndata scanpy h5py scipy scikit-learn cma`
  (**`pydantic` is imported by `src/` but undeclared in `pyproject` `dependencies` — T0 also adds it there, one-line fix**); then
  `pytest -q`. Record pass/skip/fail counts and the known pre-existing failure
  (`test_architect_dispatch_v05::test_alias_scgpt_to_scgpt_small`, per commit 84fb70f) in `baseline.md`.
- **Also (G1):** find the newest `anndata`/`h5py` pair under which `tests/test_adamson_combined.py` passes; pin both
  in `pyproject` (`scgpt` group) and in the Modal `image` pip list; add `pydantic` and `requests` to `dependencies`.
- **Measured baseline before T0's fixes:** 209 passed, 3 failed — `test_alias_scgpt_to_scgpt_small` (pre-existing,
  84fb70f) and 2× `test_adamson_combined` (`h5py TypeError: Accessing a group is done with bytes or str`).
- **Done when** `baseline.md` records both runs; after pinning, only `test_alias_scgpt_to_scgpt_small` fails.

## P1 · Determinism + seed (A6, A2)

### T1 · Deterministic stratum key — **10 min**
- **Files:** `src/perturb_eval/data/subsample.py` (edit: add `deterministic_stratum(label: str, k: int) -> int`
  = `zlib.crc32(label.encode()) % k`) · `tests/test_subsample.py` (new or extend).
- **Failing test:** `test_stratum_is_process_independent` — spawn two `subprocess` pythons with
  `PYTHONHASHSEED=1` and `=2`, each printing `[deterministic_stratum(s,3) for s in LABELS]`; outputs equal.
  Second test: `deterministic_stratum("CBL_UBASH3A",3)` equals a literal pinned value (regression pin).
- **Done when** both pass; `grep -n "hash(" src/perturb_eval/data/subsample.py` is empty.

### T2 · Task-list construction is a pure, tested function — **35 min**
- **Files:** `src/perturb_eval/experiments/v05_tasks.py` (new: `@dataclass TaskPlan`; `build_task_lists(adamson: dict[str, Dataset], norman: Dataset, *, norman_n_singletons, norman_n_doublets, adamson_n_per_bin, adamson_n_bins, seed, doublet_delim) -> TaskPlan`) · `scripts/modal/app_v05.py` (edit `:170-226`: call it; Adamson subsets iterated in `sorted(paths.items())` order) · `tests/test_v05_tasks.py` (new).
- **Failing test:** on a small synthetic-label fixture (labels only, no expression data — stays outside the
  guardrail triple), `build_task_lists` in two subprocesses with different `PYTHONHASHSEED` returns identical
  task lists; Adamson bin membership identical regardless of the dict insertion order of the inputs.
- **Done when** tests pass; `grep -n "hash(" scripts/modal/app_v05.py` empty; app_v05 still imports.

### T3 · One producer — **5 min**
- **Files:** `scripts/modal/app_v05_lifecycle_only.py` (**delete**) · `tests/test_single_producer.py` (new).
- **Failing test:** asserts the file does not exist and that exactly one file under `scripts/modal/` contains the
  string `lifecycle_runs.jsonl`.
- **Done when** passes; `docs/MODAL.md` / `LIVE_RUN.md` no longer mention the deleted script (grep empty).

### T4 · Seed reaches the LLM layer — **30 min**
- **Files:** `src/perturb_eval/llm/openrouter_client.py` (edit `:151-164` `_cache_key(..., seed: int)`; `:266`
  `chat_json(..., seed: int)`) · `src/perturb_eval/agentic_lifecycle/llm_agent_pool.py` (edit `:120` `propose(..., seed: int)`; the `AgentPool` Protocol likewise) · `tests/test_llm_cache_key.py` (new) · `tests/test_agentic_lifecycle.py` (extend).
- **Failing test:** `_cache_key` with identical `(task_id, round, role, prompt, model_id)` and `seed=1` vs `seed=2`
  differ; a stub client records the `seed` it received from `propose`.
- **Done when** passes; `seed` is a required keyword (no default) on all three.

### T5 · Seed reaches the trainer — **25 min**
- **Files:** `src/perturb_eval/agentic_lifecycle/trainer_exec.py` (edit `:14-28`: `execute_trainer(..., seed: int)`;
  `BackboneTrainConfig(seed=seed)`; remove `trainer_proposal.get("seed", 2026)`) ·
  `src/perturb_eval/agentic_lifecycle/loop.py` (edit `:99-111`: `run_agentic_lifecycle(..., seed: int)`; thread to
  `propose` and `execute_trainer`) · `tests/test_agentic_lifecycle.py` (extend).
- **Failing test:** `test_lifecycle_msd_differs_across_seeds` — fixture task, `mlp` backbone (numpy only), stub
  agent pool; `run_agentic_lifecycle(seed=2026)` vs `(seed=2027)` give different `final_msd_topk`.
- **Done when** passes; `grep -rn '"seed", 2026' src/` empty.

### T6 · The sweep passes the seed — **10 min**
- **Files:** `src/perturb_eval/experiments/v05_sweep.py` (new: `lifecycle_record(task, ds, seed, pool, **kw) -> dict`
  — the body of `app_v05.py:340-357`) · `scripts/modal/app_v05.py` (edit: call it) · `tests/test_v05_sweep.py` (new).
- **Failing test:** with a stub `run_agentic_lifecycle` (monkeypatched), `lifecycle_record(seed=7)` calls it with
  `seed=7` and the record's `seed` field is 7.
- **Done when** passes. **Phase boundary → `/iteration-complete`.**

## P2 · Target contract (A4 + D1)

### T7 · Perturbation label parsing — **15 min**
- **Files:** `src/perturb_eval/data/perturbations.py` (new: `parse_perturbation(label, delim="_") -> tuple[str, ...]`;
  `is_doublet(label, delim)`; `resolve_target_indices(perts, gene_to_idx, delim) -> dict[str, tuple[int, ...]]` —
  raises `ValueError` listing every `(label, missing_gene)`; never substitutes) · `tests/test_perturbations.py` (new).
- **Failing test:** `"CBL_UBASH3A"` → `("CBL","UBASH3A")`; `"BAK1"` → `("BAK1",)`; `delim="+"` honoured; a missing
  gene raises with the label and gene in the message; a control label (`"control"`/`"ctrl"`, per the loaders) is
  skipped not raised.
- **Done when** passes.

### T8 · Loaders use it; random fallback gone — **25 min**
- **Files:** `src/perturb_eval/experiments/norman.py` (edit `:100-121`, `:5-6`; `load_norman_matrix(..., doublet_delim="_")`) ·
  `src/perturb_eval/experiments/e2_adamson.py` (edit `:200-212`) · `src/perturb_eval/data/download.py` (edit `:227` docstring) ·
  `tests/test_norman_loader.py` (extend fixture with `_`-joined doublets) · `tests/test_adamson_combined.py` (extend).
- **Failing test:** Norman fixture with `JUN_FOS` → `target_gene_idx["JUN_FOS"]` is a 2-tuple of the right columns;
  a singleton whose gene is outside the HVG cut raises `ValueError`; static: `grep -n "rng.integers" norman.py e2_adamson.py` empty.
- **Done when** passes and the guardrail test still passes.

### T8b · HVG selected on training cells only, both loaders — **40 min** (CTO #227, ruling (ii))
- **Files:** `src/perturb_eval/experiments/e2_adamson.py` (edit `:183-186` + `:243-251`: gene variance computed
  over `train_mask` rows **per held-out task**; the globally-ranked cache at `:243` no longer holds a feature
  set, only the raw matrix) · `src/perturb_eval/experiments/norman.py` (same shape at its HVG block — lines
  confirmed in T8b's first step) · `src/perturb_eval/data/hvg.py` (new: `select_hvg_train_only(X, train_mask, n) -> np.ndarray`
  — the one function both loaders call) · `tests/test_hvg.py` (new) · `src/perturb_eval/experiments/provenance.py`
  (T13: `hvg_selection = {"mode": "train_only", "n_hvg_per_task": {...}, "params_per_task": {...}}`).
- **Failing test (condition 2 — pin the property, not the line):** fixture where held-out perturbation A has huge
  variance in gene g_A and B in g_B: `select_hvg_train_only(X, mask_excl_A, n)` does **not** contain g_A while
  `select_hvg_train_only(X, mask_excl_B, n)` does; and `gene_var` equals `X[train_mask].var(axis=0)` exactly.
  Second test: Adamson and Norman loaders both route through `select_hvg_train_only` (monkeypatch spy called once
  per held-out task).
- **Conditions carried:** (1) both loaders in one change; (3) provenance carries `n_hvg_per_task` +
  `hvg_selection.mode == "train_only"`; (4) the report states that per-task HVG means per-task feature spaces, so
  the cross-task median is a median over models with differing inputs; (5) `params_per_task` recorded for
  `scgpt_small` (vocabulary scales with HVG count). **Out of scope (CTO):** top-20 DEG evaluation genes from the
  held-out perturbation's own shift — unchanged, to be *stated* in the report's setup note, not altered.
- **Done when** tests pass; `grep -n "var(axis=0)" e2_adamson.py norman.py` shows no whole-matrix variance.

### T9 · Backbones accept multi-target — **35 min**
- **Files:** `src/perturb_eval/backbones/base.py` (edit `:52-58`: `target_gene_idx: Mapping[str, tuple[int, ...]]`;
  on-target dip = `lfc[list(idx)].mean()`) · `linear.py` (`:52`, `:73-81`) · `mlp.py` (`:69`) · `scgpt_small.py` (`:99`) ·
  `tests/test_backbones.py` (extend).
- **Failing test:** linear + mlp on a fixture where perturbation `A_B` has targets `(3, 5)`: fit succeeds and
  `predict_logfc` writes the predicted dip into both columns; a 1-tuple reproduces today's single-gene numbers
  exactly (regression pin against a stored value). scGPT-small test skipped when torch absent (existing pattern).
- **Done when** passes.

### T10 · Held-out remap raises — **10 min**
- **Files:** `src/perturb_eval/agentic_lifecycle/loop.py` (edit `:220-227`: remap every index of the tuple; missing
  held-out → `ValueError`) · `tests/test_agentic_lifecycle.py` (extend).
- **Failing test:** held-out label absent from `target_gene_idx` raises; a 2-tuple remaps to two HVG-subset columns.
- **Done when** passes.

### T11 · Stratum-count assertion — **10 min**
- **Files:** `src/perturb_eval/experiments/v05_tasks.py` (edit: `is_doublet` via T7; after sampling,
  `assert len(chosen_doublets) == norman_n_doublets and len(chosen_singletons) == norman_n_singletons`, message
  includes eligible-pool sizes) · `tests/test_v05_tasks.py` (extend).
- **Failing test:** pool with `+`-delimited labels and `doublet_delim="_"` requesting 5 doublets raises
  `AssertionError` mentioning `eligible doublets: 0`; the same pool with `delim="+"` returns 5.
- **Done when** passes. **Phase boundary → `/iteration-complete`.**

## P3 · Provenance, analyser, model_id/source (A3 via D4)

### T12 · `model_id` + `source` on every step — **35 min**
- **Files:** `src/perturb_eval/llm/openrouter_client.py` (edit `chat_json` → returns `ChatResult(content: dict, model_id: str)`;
  update every caller found by `grep -rn chat_json`) · `src/perturb_eval/agentic_lifecycle/llm_agent_pool.py`
  (edit `:132-154`: return `model_id`, `source="llm"`; fallback path `source="fallback", model_id=None`) ·
  `src/perturb_eval/agentic_lifecycle/types.py` (edit `LifecycleStep`: `model_id: str | None = None`,
  `source: Literal["llm","fallback"] = "llm"`) · `loop.py` (write them) · `tests/test_agentic_lifecycle.py` (extend).
- **Failing test:** stub transport returning `model_id="x/y"` → step has `model_id=="x/y"`, `source=="llm"`; stub
  raising → `source=="fallback"`, `model_id is None`, `proposal_content` equals the schema default.
- **Done when** passes; JSONL round-trips the two fields.

### T13 · Provenance builder — **30 min**
- **Files:** `src/perturb_eval/experiments/provenance.py` (new: `build_provenance(*, run_id, git_sha, git_dirty,
  entrypoint_kwargs, datasets, task_plan, llm_pool, gpu, hourly_usd, budget_cap_usd, lib_versions) -> dict`;
  `finalize_provenance(prov, *, finished_at, gpu_seconds, cost_usd_actual, counts, entropies, budget_hit)`;
  `REQUIRED_KEYS`) · `tests/test_provenance.py` (new).
- **Failing test:** every key in A&D §3 present; `git_sha` is 40 hex; `entrypoint_kwargs` contains all 13 names;
  `finalize` refuses a record whose `started_at` is missing.
- **Note:** the Modal container has no `.git`. `git_sha`/`git_dirty` are captured in `local_entrypoint` (host side)
  and passed as kwargs — test that `entrypoint` computes them (subprocess `git rev-parse HEAD` in a temp repo).
- **Done when** passes.

### T14 · Record 0 of each JSONL — **15 min**
- **Files:** `scripts/modal/app_v05.py` (edit `_append` path `:157-163`: write `{"record_type":"provenance", ...}` first) ·
  `src/perturb_eval/experiments/e_v05_real_traces.py` (edit `_read_jsonl` `:43-59` → returns `(provenance | None, rows)`) ·
  `tests/test_e_v05_real_traces.py` (extend).
- **Failing test:** a JSONL whose first line is a provenance record reads back as `(prov, rows)` with the record
  excluded from `rows`; a file without one gives `(None, rows)` and the analyser **warns** it is legacy.
- **Done when** passes.

### T15 · Analyser hard-fail — **15 min**
- **Files:** `src/perturb_eval/experiments/e_v05_real_traces.py` (edit `analyse_v05_run` `:194-197`: task key
  normalised via `row.get("task", row.get("task_id"))`; `if trainer_tasks != lifecycle_tasks: raise ValueError(f"task sets differ: only-trainer={…} only-lifecycle={…}")` **before** any computation) · tests (extend).
- **Failing test:** fixtures with disjoint sets raise and name both differences; equal sets produce a summary whose
  `n_tasks_trainer == n_tasks_lifecycle`. Regression: feeding the committed `artifacts/v0.5.0/` files raises.
- **Done when** passes.

### T16 · Entropy over LLM-sourced rows, per role — **20 min**
- **Files:** `e_v05_real_traces.py` (edit `:220-223`: filter `source=="llm"`; emit `entropy_by_role`,
  `n_steps_llm`, `n_steps_fallback`, `n_lifecycle_runs_unique_tasks`) · tests (extend).
- **Failing test:** steps all `fallback` → entropy fields are `null` and `n_steps_fallback` counts them; mixed →
  entropy computed only over the llm rows (hand-computed expected value).
- **Done when** passes.

### T17 · New config copy per run — **10 min**
- **Files:** `scripts/modal/app_v05.py` (`local_entrypoint`: write `configs/runs/<run_id>.json` = resolved kwargs +
  git SHA; `run_id = <utc-stamp>-<sha7>`) · `src/perturb_eval/experiments/provenance.py` (`write_run_config`) · tests.
- **Failing test:** `write_run_config` writes a file whose contents equal the provenance `entrypoint_kwargs` block;
  a second call with the same kwargs writes a **new** file (no mutation).
- **Done when** passes. **Phase boundary → `/iteration-complete`.**

## P4 · Fold-ins (A5, A7)

### T18 · Backbone one-hot from the space — **25 min**
- **Files:** `src/perturb_eval/optimizers/base.py` (edit `:26-47`: `config_to_vec(phi, backbones: tuple[str, ...])`,
  `nearest_config(..., backbones)`) · `cma_es.py` (`:41,49,69,73`: `self._backbones = tuple(sorted({c.backbone for c in space}))`) ·
  `contextual_gp.py` (`:46,58,67`) · `scripts/local/rerun_e3_with_real_probes.py:138` · `scripts/local/bootstrap_and_analyze.py:114` ·
  `tests/test_optimizers.py` (edit `:22-26`: add a `("linear","mlp","scgpt_small")` space).
- **Failing test:** `len({tuple(config_to_vec(c, bb)) for c in space}) == len(space)` for the real backbone set
  (fails today: 27 → 9); `nearest_config` can return `mlp`.
- **Done when** passes; existing optimizer tests unchanged in outcome.

### T19 · `_fetch` fails closed — **15 min**
- **Files:** `src/perturb_eval/data/download.py` (edit `:148-159`: unpinned cached file → `ValueError` unless
  `trust_unpinned=True`, default False; the `fetch_*` wrappers expose it) · `tests/test_data_download.py` (extend).
- **Failing test:** `test_raises_when_cached_file_has_no_sha_pin` (A&D §5 W6); `trust_unpinned=True` returns the path
  with a logged warning.
- **Done when** passes.

### T20 · Print digests (CPU, on Modal) — **15 min + run**
- **Files:** `scripts/modal/app_v05.py` (edit: `--print-digests` entrypoint flag → CPU-only function that fetches
  if absent and prints `name, path, bytes, sha256` for the four datasets from the `perturb-eval-data` volume).
- **Gate:** Modal auth only; no GPU; cost ≈ cents. This is the first Modal touch and is inside #202's authority
  (fetching is part of the regeneration).
- **Done when** four digests are printed and pasted into T21.

### T21 · Pin digests — **10 min**
- **Files:** `src/perturb_eval/data/download.py` (`DATASETS` `:42-82`: `sha256=` on all four) · `tests/test_data_download.py`
  (`test_all_specs_pinned`: every `DATASETS` entry has a 64-hex `sha256`).
- **Done when** passes. **Phase boundary → `/iteration-complete`.**

## P5 · Preflight + the sweep (gated: g1–g4)

### T22 · Preflight in-process — **30 min**
- **Files:** `src/perturb_eval/experiments/v05_preflight.py` (new: `preflight(kwargs) -> tuple[TaskPlan, dict]` —
  verify digests (T19/T21), `build_task_lists` (T2/T11), `resolve_target_indices` for every task (T7), build
  provenance (T13); any failure raises **before** the GPU loops) · `scripts/modal/app_v05.py` (call first thing in
  `run_v05_sweep`; `timeout=28800`; output dir `/<version>/`, `--version v0.6.0`) · `tests/test_v05_preflight.py`.
- **Failing test:** a fixture with one bad target raises with the task named and **no** trainer call made (stub counts).
- **Done when** passes.

### T23 · Resource + cost check — **10 min**
- **Do (no code):** `modal profile current`; `modal volume list` shows `perturb-eval-data` + `biofm-cache`;
  `[ -n "$OPENROUTER_API_KEY" ]` (presence only, never echoed; provisioned by the CTO via Infisical — G2); estimate = 41 tasks × 54 configs × 3 seeds trainer
  cells (2214, +14% on 1944) + 123 lifecycle runs ≈ **4 GPU-h ≈ $5–6** at $1.32/h against the $28 cap, timeout 8 h.
- **Done when** all four are green and the estimate is written into `workstreams/perturb-seq-eval/plan/run-precheck.md`.

### T24 · The sweep — **~4 h wall, unattended**
- **Gate:** g1 + g2 (lead-4 ruling incorporated or explicitly deferred by the CTO) + g3 + g4.
- **Do:** `modal run scripts/modal/app_v05.py::entrypoint --version v0.6.0 --norman-n-singletons 15 --norman-n-doublets 5 --seeds 3`
  (one invocation, one process). Then `modal volume get perturb-eval-data /v0.6.0/ artifacts/v0.6.0/`;
  `python -m perturb_eval.experiments.e_v05_real_traces artifacts/v0.6.0` → `summary.json`; commit
  `artifacts/v0.6.0/*`, `configs/runs/<run_id>.json`.
- **Done when** the analyser accepts the files (task sets equal), `provenance.json` has every required key, and
  `git status` is clean after the commit.

### T25 · Report to the CTO — **20 min**
- **Body:** regenerated `summary.json`; the provenance record; actual `cost_usd_actual` + GPU-h; every gate
  old → new (Adamson MSD, Norman MSD, entropy — and any gate the fixes make evaluable); `n_tasks` per file;
  fallback vs llm step counts; the seven leads verified/not (done); the `tests.referee_command` gap; the unpushed
  `main`. Then **stop** — the next decision is the CTO's and the principal's. `/pr-prep` + `/pr-submit` after.

---

## Risks (named, not hedged)
- **R-timeout:** 6 h → 8 h raised in T22; the loop is resume-safe (append + commit) so a timeout yields a partial
  file that the analyser will refuse (no `finished_at`) — reported as partial, not summarised.
- **R-hvg-leak:** resolved — CTO #227 ruled (ii); T8b is in P2. Per-task feature spaces are a stated methodological
  consequence in T25's report, not a caveat.
- **R-credential:** `OPENROUTER_API_KEY` is absent locally; the sweep cannot start until the CTO configures it.
  The lifecycle phase silently falls back to schema defaults on any LLM failure — with T12 this is now *visible*,
  and T23 refuses to launch without the key.
- **R-torch:** `scgpt_small` tests need torch; local runner may skip them (existing pattern). Modal image has torch.
