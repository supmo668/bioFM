# CHANGELOG

All notable changes to the perturb-seq-eval supplement are documented here
in conventional-commits style. This file is the version-controlled mirror
of `docs/SUPPLEMENT.md` §9 Deviation Log.

## [Unreleased] — v0.6.0 regeneration (manuscript aligned; sweep not yet run)

### Changed (title and framing)

- **Title** (principal's choice), propagated to `paper/paper.tex`, `docs/THESIS.md`, `publish.yml`, `CITATION.cff`, `README.md`, `paper/README.md`: *Does Agent Confidence Entropy Predict Task Difficulty? A Pre-registered, Provenance-Complete Test of Agentic Hyperparameter Tuning for Perturb-seq Response Prediction*. The question form makes a null result publishable; a null answer is not to be traded back into a claim title.
- **`paper/PREREGISTRATION.md` added**: five hypotheses and gates (Adamson oracle median < 0.20, Norman < 0.30, Architect backbone entropy ≥ 0.5 nats over LLM-sourced steps, TDI ρ > 0.5 for ≥ 1 component, cross-dataset ρ > 0.4), estimators, and the analysis-plan conventions. H4/H5 have no analyser estimator yet (flagged in the file).
- **Results are placeholders.** Every result value in the manuscript is `\pending{...}`; `sections/v050_results_filled.tex` is no longer input. All v0.5.0 values are superseded; the new appendix `sections/corrections.tex` maps each to the register rows that supersede it (A1, A2, A3, A4, A7, DF-06, DF-07, DF-10, #227, R1–R3, R9).
- **Setup rewritten to the rebuilt experiment**: 41 tasks (21 Adamson = 3 bins × 7; Norman 15 singletons + 5 doublets) from one deterministic draw (CRC32 strata, seed 2026) in one process; structural Adamson label contract and Ensembl-ID Norman joins recorded in provenance; Norman described as CRISPR activation, Adamson as CRISPR interference; train-only HVG per task; top-20-DEG evaluation genes stated as the CPA/GEARS convention; best-of-54 relabelled an oracle; LLM condition stated as a rotating OpenRouter pool with per-step `model_id` and `source`, fallback runs invalid; `scgpt_small` described once as a from-scratch 2.1 M-parameter transformer.
- **Removed** from the manuscript: the real/synthetic framing and its LaTeX comments, "Nemotron-30B" and "for demonstration purposes", the byte-equivalence claim (now "re-run at the recorded SHA and configuration"), and the claim that pretrained SCFMs are configurable backbones.
- `docs/REVIEWER_CRITIQUE.md` re-scoped to v0.4.1 (retracted line); `README.md` / `paper/README.md` entry points corrected to `scripts/modal/app_v05.py` and the `e_v05_real_traces` analyser.

## [0.5.0+layout] — 2026-04-24 (post-publish housekeeping)

### Repository structure

- **`libs/` directory introduced at the repo root.** `cellforge-agents` and `test-time-compute` moved out of `projects/` into `libs/`. Rationale: only `perturb-seq-eval` is the paper-bearing research project; the other two are reusable libraries (cellforge is imported via `cellforge_pool.py`; test-time-compute is referenced as related work).
- Path-sensitive code (`scripts/modal/app_lifecycle.py`, `app_lifecycle_optimizer.py`, `app_biofm.py`, `scripts/local/collect_real_probes.py`) updated with a `libs/`-first lookup that falls back to the legacy `projects/cellforge-agents/` location for older checkouts.
- All doc + paper refs swept to `libs/cellforge-agents/` / `libs/test-time-compute/`.
- Re-published Zenodo v3 metadata + Figshare references with the corrected `https://github.com/supmo668/bioFM` URL (the v0.4.x records had `mm-bconscious/bioFM` which never existed). DOIs unchanged: Zenodo `10.5281/zenodo.19748260`, Figshare `10.6084/m9.figshare.32086920`.

## [0.5.0] — 2026-04-24 (real-data headline rewrite)

### Changed (headline)

- **All synthetic experiments retracted.** The headline synthetic DGP and E1–E5 synthetic runs that grounded v0.4.1 are removed from the paper entirely. Every reported number in v0.5.0 comes from real Perturb-seq data. Lines 296–298 of v0.4.1's `paper/paper.tex` ("Because real multi-agent perturb-seq runs with scGPT are outside our compute envelope for this paper…") are deleted.
- **Adamson 2016 now uses all three scPerturb subsets** (pilot + 10X005 + 10X010), concatenated via `load_adamson_combined` with target-gene-aware HVG. 97 TFs total, stratified by mean |Δlog1p| on the target gene into 3 quantile bins × 7 TFs = 21 held-out tasks (`seed=2026`).
- **Norman 2019 added** — 15 singletons + 5 doublets, stratified by guide-count quartile (`seed=2026`).
- **Agentic lifecycle now has genuine configuration freedom**. The Architect picks from a widened Pydantic schema (backbone, `n_agents ∈ [2,8]`, `n_rounds ∈ [1,5]`, HVG count, learning rate, ridge λ, epochs) instead of a one-field backbone string. The Validator returns a `StructuredCritique` with `which_genes_failed` and `suggested_next_config_delta` — Architect applies the delta in the next round, closing a true refinement loop.
- **Free-tier OpenRouter rotation pool** drives all LLM calls: Nemotron-3 Super 120B, Ling 1T MoE, Hermes-3 405B, GPT-OSS 120B, Qwen3-Next 80B, Llama 3.3 70B, Gemma-4 31B, Gemma-3 27B. Role-preferred selection, 60s cooldowns, sha256 disk cache. **$0** LLM cost.
- **Single-stage Modal A100 sweep** with hard-kill watchdog at $28. Atomic JSONL append per run for resume safety. Total Modal spend: **$4.04** (well under cap).

### Phase-3 pre-registered gate outcomes

- Adamson median best-config MSD = 0.147 < 0.20: **PASS**
- Norman  median best-config MSD = 0.131 < 0.30: **PASS**
- Architect backbone choice entropy = 0.356 nats ≥ 0.5: **FAIL** (agents converge on `scgpt_small` 91% of the time — sensible for unseen K562 perturbations; gap is a stated future-work item once the backbone pool widens to a pretrained SCFM).

### Added (software)

- `src/perturb_eval/data/{download,subsample}.py` — idempotent SHA256-gated fetchers (Adamson 3 subsets + Norman) with truncation guard; stratified sampler + `mean_abs_logfc_per_target`.
- `src/perturb_eval/experiments/norman.py`, `experiments/e2_adamson.py::load_adamson_combined`.
- `src/perturb_eval/agentic_lifecycle/proposal_schema.py` — Pydantic v2 schemas for all five agents.
- `src/perturb_eval/agentic_lifecycle/freedom_probe.py` — choice entropy probe.
- `src/perturb_eval/agentic_lifecycle/llm_agent_pool.py` — LLMAgentPool over free-tier OpenRouter.
- `src/perturb_eval/llm/openrouter_client.py` — rotation client with weight-inclusive pool.
- `src/perturb_eval/experiments/e_v05_real_traces.py` — replays E1–E5 analysis on real-trace JSONLs.
- `scripts/modal/app_v05.py` + `scripts/modal/app_v05_lifecycle_only.py` — Modal entrypoints.
- `scripts/paper/fill_v050_numbers.py` — templated paper-number substitution.
- `paper/sections/v050_experimental_setup.tex` + `v050_results.tex` (templated).

### DOIs

- **Zenodo v3** (new-version on concept DOI `10.5281/zenodo.19716140`): _to be assigned on publish_.
- **Figshare** (DOI `10.6084/m9.figshare.32086920`, unchanged): paper + supplement updated in place.
- **OSF** (project `wmeuy`): paper + supplement updated in place.

### Deviations from the plan

- OSF preprint subjects PATCH: still unresolved from v0.4.1; retried this release.
- `scgpt_small` is not the Cui 2024 pretrained scGPT; the paper now says so explicitly in §3.2. Pretrained SCFM backbone integration remains future work.
- First Modal sweep (v3) wasted ~30 min on a Norman 404 (filename was `NormanWeissman2019_filtered.h5ad`, not the bare `NormanWeissman2019.h5ad` I pinned) and a sparse-to-dense OOM in the Norman loader. Both fixed before the productive v5 run.
- First lifecycle sweep had every LLM call return HTTP 404 — every model id in the original DEFAULT_POOL had been retired from OpenRouter's free tier between planning and execution. Fixed by querying `/api/v1/models` for the live free-tier roster on 2026-04-24, then re-running lifecycle-only against the trainer JSONL (~$1).

## [0.4.1] — 2026-04-23 (late, authorship patch)

### Fixed

- `paper/paper.tex` `\author{}` block carried `Anonymous Authors / Syntropy Health / {anonymous}@syntropyhealth.bio` from the template. Replaced with `Mangyin Mo / Carnegie Mellon University / mangyinm@alumni.cmu.edu / ORCID 0009-0009-5233-3142`. Recompiled `paper.pdf` (md5 `e8eec5ba0a65531842fa14168b41b6b8`).
- Zenodo: created v2 record. Concept DOI `10.5281/zenodo.19716140` (canonical) now resolves to v2 `10.5281/zenodo.19721470`. v1 `10.5281/zenodo.19716141` retained for provenance.
- Figshare (DOI `10.6084/m9.figshare.32086920`, unchanged): replaced paper.pdf in place; still 3 files total.
- OSF (project `wmeuy`): replaced paper.pdf on the project's OSFStorage.

### Added

- Infisical secret `AUTHOR_EMAIL = mangyinm@alumni.cmu.edu` under `/research/perturb-seq-eval` in the SyntropyHealth GTM project (dev env).
- `research/PUBLICATION_EVIDENCE.md` → "Authorship patch" section with the root-cause + remediation + new grep for the pre-flight checklist.

### Root-cause note

The §2.6 coherence audit's placeholder grep only scanned Markdown and YAML tokens (`Last, First`, `REPO/PATH`, `0000-0000`), not LaTeX author blocks. Added `grep -rn "Anonymous\\|Syntropy Health" paper/` to the checklist.

## [0.4.0] — 2026-04-23

### Published

- **Zenodo DOI**: [10.5281/zenodo.19716141](https://doi.org/10.5281/zenodo.19716141) — primary archival DOI for paper + supplement + artefacts bundle.
- **Figshare DOI**: [10.6084/m9.figshare.32086920](https://doi.org/10.6084/m9.figshare.32086920) — mirror of the supplement + artefacts bundle.
- **OSF BioHackrXiv**: deferred. Project `wmeuy` / preprint `dhu4z_v1` exist but OSF's subjects PATCH endpoint returned 502 Bad Gateway at publish time. State file retains all IDs; a single `python scripts/publish/submit_to_venues.py osf` resumes cleanly when OSF recovers.

### Added

- New `src/perturb_eval/agentic_lifecycle/` package (8 files): types, five per-agent executors (data curator, literature, architect, trainer, validator), multi-round loop with `backbone_override` + `validator_threshold_override`, and `CellForgeAgentPool` that wires the live CellForge agents + BioFM tools (BioGPT, Geneformer).
- Modal apps `scripts/modal/app_lifecycle.py` (end-to-end lifecycle sweep) and `scripts/modal/app_lifecycle_optimizer.py` (contextual-BO over live lifecycle evaluation).
- Local `scripts/local/run_lifecycle_dryrun.py`, `scripts/local/analyze_lifecycle_results.py`, `scripts/local/render_fig6_lifecycle.py`.
- `CITATION.cff` with both DOIs + all upstream references.
- `publish.yml` + `scripts/publish/submit_to_venues.py` with OSF/Zenodo/Figshare submitters, live category resolution, and idempotent resume.

### Results (Modal)

- **T11 v2** (`ap-wlIETcuaNPkJin8nScWi94`, A10G): 63 / 63 finite lifecycle runs across 3 backbones × 7 Adamson perturbations × 3 seeds. Mean final MSD = **0.117 [0.089, 0.146]** (bootstrap 95 % CI, n_boot = 2000). Multi-round refinement triggered on 48 / 63 runs (validator threshold = 0.05).
- **T13** (`ap-qqqInu3Fa4r9djbz1I3TvL`, A10G): contextual-BO vs random over the live lifecycle. Both reach MSD 0.056 at iter 1 and tie at AULC 0.445 (ΔAULC = 0.0003). The 2× drop from single-path 0.117 → optimizer 0.056 is the empirical value of the optimization layer.

### Changed

- SUPPLEMENT.md §5.5 (end-to-end agentic lifecycle) added; §7 conclusion now lists seven items including the lifecycle + live optimizer; §8 artifact index extended with `fig6_*`, `adamson_lifecycle_runs.json`, `adamson_live_optimizer.json`, `revision_stats_lifecycle.json`; §9 deviation log extended with five 2026-04-23 rows.
- `publish.yml` abstract now describes four regimes (was three) — adds the end-to-end lifecycle as regime (iv).
- `OptimizerTrajectory` gained `per_seed_trajectories` + `cum_regret_per_iter` (MC1 + mc5).
- Renamed `CMAESOptimizer` → `OnePlusLambdaES` with alias (mc7).
- Wong colourblind-safe palette + CI bands on Figs 2 / 3 / 4 (mc9).

### Fixed

- `57bac5b` — DataCurator HVG filter must preserve every target-gene index; otherwise Linear.fit raised IndexError on every Adamson call. Re-injects missing target-gene indices after the HVG cut.
- `b3a3cdd` — Trainer-failure guard: if `execute_trainer` raised, the Validator now skips scoring (previously called `predict_logfc` on an unfit backbone → RuntimeError).
- `c136bdb` — `.claude/` scratch directory added to repo `.gitignore`.

### Retracted / reframed (per REVIEWER_CRITIQUE.md MC1 – MC3)

- "scgpt_small wins 5 / 7 Adamson tasks" (unstable across seeds; per-seed decomposition 5/1/1, 4/3/0, 3/2/2).
- "Contextual GP beats CMA-ES by 2.6 % on real Adamson" (CIs overlap at 95 %; noise floor swallows the gap).
- The Adamson probe-signature disclosure is now explicit: the §5.3 E3 experiment uses simulated probes (MC3a). Live probes are harvested in §5.3b and the end-to-end §5.5 lifecycle.

## [0.3.0] — 2026-04-22

### Added

- E1 – E4 on synthetic + Adamson grids with bootstrap 95 % CIs, cumulative regret, numerical γ_T (Krause–Singh–Guestrin 2008).
- Five Plotly figures with Wong palette + CI bands.

### Changed

- `TDI₂` dropped from headline metrics per pre-registered ρ ≥ 0.95 rule.

## [0.2.0] — 2026-04-21

### Added

- Metric extensions: `ace_d` (simplex entropy), `csd_star` (excess severity), `tdi2` (with interactions).
- Poetry migration.
- Backbones (`linear`, `mlp`, `scgpt_small`) + optimizers (`random`, `one_plus_lambda_es`, `contextual_gp`).

## [0.1.0] — 2026-04-20

### Added

- Initial paper draft with synthetic DGP and three-regime design.
