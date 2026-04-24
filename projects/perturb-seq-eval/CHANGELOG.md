# CHANGELOG

All notable changes to the perturb-seq-eval supplement are documented here
in conventional-commits style. This file is the version-controlled mirror
of `docs/SUPPLEMENT.md` §9 Deviation Log.

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
