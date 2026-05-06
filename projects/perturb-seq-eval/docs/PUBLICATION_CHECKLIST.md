# Publication Checklist & Repo Organization

> Roadmap from "supplement ready" to "submission out." Parallel checklist
> to [`REVIEWER_CRITIQUE.md`](REVIEWER_CRITIQUE.md); read that file first
> for blocker-level revision requirements.

> **Status sync with [`INTERNAL_FOLLOWUP.md`](INTERNAL_FOLLOWUP.md) §2 is
> authoritative.** This file mirrors the publication-track view; any
> conflict → defer to INTERNAL_FOLLOWUP.md for the canonical status.
>
> Last synced: 2026-04-22 after the revision pass (MC1 + MC2 + MC3a +
> mc5 + mc6 + mc7 + mc8 + mc9 closed, MC3b / MC4 / mc10 remain open).

## 0. Current state (2026-04-22)

| Deliverable | State | Location |
|---|---|---|
| Thesis | ✅ drafted | [`docs/THESIS.md`](THESIS.md) |
| Engineering design | ✅ drafted | [`docs/DESIGN.md`](DESIGN.md) |
| Supplement design | ✅ drafted | [`docs/SUPPLEMENT_DESIGN.md`](SUPPLEMENT_DESIGN.md) |
| Supplement results | ✅ populated + revised with CIs / γ_T / reframes | [`docs/SUPPLEMENT.md`](SUPPLEMENT.md) |
| Reviewer critique | ✅ written + referenced throughout supplement | [`docs/REVIEWER_CRITIQUE.md`](REVIEWER_CRITIQUE.md) |
| Revision artefacts (CIs + γ_T) | ✅ landed 2026-04-22 | [`artifacts/modal_run/revision/revision_stats.json`](../artifacts/modal_run/revision/revision_stats.json) |
| Paper LaTeX | ⚠️ prior version renders; numbers need revision-sync (see §6.4 of [`PUBLISHING_RUNBOOK`](../../../research/PUBLISHING_RUNBOOK.md)) | [`paper/paper.pdf`](../paper/paper.pdf) |
| Code + tests | ✅ 92/92 pytest green incl. new per-seed + cum-regret surface | [`src/`](../src/), [`tests/`](../tests/) |
| Modal artifacts | ✅ downloaded | [`artifacts/modal_run/`](../artifacts/modal_run/) |
| Figures (PNG + PDF + HTML) | ✅ regenerated with Wong palette + CI bands | [`artifacts/modal_run/figures/`](../artifacts/modal_run/figures/) |
| Publishing infra (script + runbook + yaml + .env template) | ✅ ready | [`scripts/publish/submit_to_venues.py`](../scripts/publish/submit_to_venues.py), [`publish.yml`](../publish.yml), [`research/PUBLISHING_RUNBOOK.md`](../../../research/PUBLISHING_RUNBOOK.md) |

## 1. Blocker revisions (must land before submission)

From [`REVIEWER_CRITIQUE.md`](REVIEWER_CRITIQUE.md) §MC1–MC3. Closed items
link to the evidence; INTERNAL_FOLLOWUP.md §2 carries the canonical
status + owner/date columns.

- [x] **MC1** — per-seed E3 trajectories + bootstrap 95 % CIs on all headline numbers ☑ 2026-04-22
  - `OptimizerTrajectory` gained `per_seed_trajectories` and `cum_regret_per_iter` fields → [`src/perturb_eval/experiments/common.py`](../src/perturb_eval/experiments/common.py)
  - `run_e3_optimizer_comparison` now populates both via `_collect_per_seed_trajectories` → [`src/perturb_eval/experiments/e3_optimizer_comparison.py`](../src/perturb_eval/experiments/e3_optimizer_comparison.py)
  - Bootstrap analysis (n_boot = 2 000 over task × seed) → [`scripts/local/bootstrap_and_analyze.py`](../scripts/local/bootstrap_and_analyze.py)
  - Revision stats landed in [`artifacts/modal_run/revision/revision_stats.json`](../artifacts/modal_run/revision/revision_stats.json)
  - Figs 2/3/4 regenerated with shaded CI bands → [`artifacts/modal_run/figures/`](../artifacts/modal_run/figures/)
  - **Outcome:** Adamson contextual-vs-CMA-ES CIs *overlap*; the earlier 2.6 % "edge" point estimate sits inside the noise floor and has been retracted.
- [x] **MC2** — reframe §5.2 / §6.2; retract "5/7 wins" headline ☑ 2026-04-22
  - [`docs/SUPPLEMENT.md`](SUPPLEMENT.md) §5.2 now quotes the per-seed decomposition (5/1/1, 4/3/0, 3/2/2) and states the three backbones are statistically indistinguishable within ±1 seed-SE on 5/7 Adamson tasks.
  - §6.2 retitled "The Adamson backbone result (revised per MC2)" and reframes the observation as "linear's synthetic dominance does not transfer" rather than an architectural win for `scgpt_small`.
  - Retraction is also logged in SUPPLEMENT.md §9 (Deviation log, 2026-04-22 row) and in [`docs/REVIEWER_CRITIQUE.md`](REVIEWER_CRITIQUE.md).
- [x] **MC3a** — probe-simulation disclosure in abstract and §5.3 preamble ☑ 2026-04-22
  - [`docs/SUPPLEMENT.md`](SUPPLEMENT.md) status block at top of the file now explicitly flags simulated probes; §5.3 leads with a dedicated disclosure quoteblock pointing at [`scripts/modal/app.py::_probe_for_task`](../scripts/modal/app.py) and [`scripts/local/bootstrap_and_analyze.py::synth_probe_contexts`](../scripts/local/bootstrap_and_analyze.py).
  - [`publish.yml`](../publish.yml) abstract rewritten to match — no standing "contextual GP routes on real Adamson" claim.
- [ ] **MC3b** — collect real CellForge traces on each Adamson task ⬜ **remaining blocker for the strong-accept bar**
  - Skeleton in place: [`scripts/modal/collect_traces.py`](../scripts/modal/collect_traces.py) defines the `OrchestratorClient` Protocol + `project_round_zero_to_probe` helper; end-to-end wiring pending.
  - Effort estimate: ~1 engineer-day, $0 on OpenRouter free tier.

## 2. Major revisions (strong-accept upgrade)

- [ ] **MC4** — Norman 2019 grid 🔄 **deferred-explicitly** 2026-04-22
  - SUPPLEMENT.md §7 Open Question #2 now carries the defer with a rationale (Adamson CI widths are n_tasks-limited, so Norman's ~200 perturbations is the mechanically-correct path to tighter CIs).
  - No code written yet; `load_adamson_matrix` → `load_norman_matrix` twin remains to be drafted.
- [x] **mc5** — cumulative regret Σ(y_t − y_min) as primary optimizer metric ☑ 2026-04-22
  - `cum_regret_per_iter` added to [`OptimizerTrajectory`](../src/perturb_eval/experiments/common.py); populated by `_collect_per_seed_trajectories`.
  - SUPPLEMENT.md §5.3 and §5.4 tables now report final regret alongside final MSD; AULC retained as secondary for continuity with the prior draft.
- [ ] **mc10** — fix `scgpt_small` vocab to a constant 2 000 across both grids ⬜
  - Documented as a known confound in SUPPLEMENT.md §7 Open Question #4.
  - Unblocks a fair-parameter backbone comparison but requires re-running E2-synthetic (~$2 Modal).

## 3. Polish (round-out) — all closed

- [x] **mc6** — tone down backbone-dominance prose ☑ 2026-04-22
  - Closed downstream of MC2. All "wins 5/7" occurrences in live prose (SUPPLEMENT.md §5.2 / §6.2 / §7) are either retracted, reframed, or explicitly tagged as retracted. Confirm via the `§2.6 check 5` grep in [`research/PUBLISHING_RUNBOOK.md`](../../../research/PUBLISHING_RUNBOOK.md).
- [x] **mc7** — rename `cma_es` → `one_plus_lambda_es` ☑ 2026-04-22
  - `OnePlusLambdaES` is the canonical class name in [`src/perturb_eval/optimizers/cma_es.py`](../src/perturb_eval/optimizers/cma_es.py); docstring now explains the Rechenberg one-fifth-success (1+λ) vs true CMA-ES distinction.
  - `CMAESOptimizer = OnePlusLambdaES` retained as a backwards-compat alias; registry dispatches on both `cma_es` and `one_plus_lambda_es` keys.
- [x] **mc8** — compute γ_T numerically ☑ 2026-04-22
  - Greedy maximum-info-gain implementation (Krause–Singh–Guestrin 2008 §5.1, submodular greedy → (1−1/e)-optimal) in [`scripts/local/bootstrap_and_analyze.py::max_information_gain`](../scripts/local/bootstrap_and_analyze.py).
  - SUPPLEMENT.md §6.4 now quotes γ_T = 56.17 (synthetic), 63.10 (Adamson), 53.97 (task-conditional) at T=30, with an explicit "kernel sanity check, not performance predictor" caveat.
- [x] **mc9** — Wong colourblind-safe palette ☑ 2026-04-22
  - `WONG` palette dict in [`scripts/local/render_figures_revised.py`](../scripts/local/render_figures_revised.py) (`#999999 / #E69F00 / #56B4E9 / #009E73 / #F0E442 / #0072B2 / #CC79A7 / #D55E00`).
  - All five PNGs regenerated 2026-04-22; trajectory figures also added 12 %-opacity CI fill bands.

## 1b. Weakness-addressing summary — what the team did vs the critique

For every weakness flagged in [`REVIEWER_CRITIQUE.md`](REVIEWER_CRITIQUE.md), one row here: what the critique said, what we did, and where a reviewer can verify.

| Critique item | Said (short) | Did | Verify |
|---|---|---|---|
| MC1 | Zero CIs → headline claims fragile | Per-seed trajectories + n_boot=2000 percentile bootstrap over (task × seed); CIs reported in SUPPLEMENT §5.3 and §5.4 tables; CI bands drawn on Figs 2/3/4 | [`revision_stats.json`](../artifacts/modal_run/revision/revision_stats.json), SUPPLEMENT.md §5.3/§5.4 |
| MC2 | "5/7 wins" unstable across seeds | Per-seed decomposition documented (5/1/1, 4/3/0, 3/2/2); §5.2 and §6.2 reframed to "statistically indistinguishable"; retraction in §9 deviation log | SUPPLEMENT.md §5.2, §6.2, §9 |
| MC3a | Probe signatures simulated, not disclosed | Disclosure block in SUPPLEMENT status header and §5.3 preamble; abstract in publish.yml rewritten | SUPPLEMENT.md status block + §5.3, publish.yml `description` |
| MC3b | Real probe collection outstanding | Skeleton `OrchestratorClient` Protocol + `project_round_zero_to_probe` helper; wiring deferred | [`scripts/modal/collect_traces.py`](../scripts/modal/collect_traces.py), INTERNAL_FOLLOWUP.md §2 MC3b row |
| MC4 | 7 Adamson tasks too few for real claim | Deferred-explicitly with rationale in §7 Open Q #2; CI widths identified as n_tasks-limited | SUPPLEMENT.md §7 |
| mc5 | AULC odd for minimisation | Cumulative regret added to `OptimizerTrajectory`; tables updated; AULC kept as secondary | [`common.py`](../src/perturb_eval/experiments/common.py), SUPPLEMENT.md §5.3/§5.4 |
| mc6 | "wins 5/7" language leaks across docs | Retracted in every outbound doc; runbook §2.6 check 5 greps for leaks | grep on `docs/` + publish.yml |
| mc7 | `cma_es` is actually (1+λ)-ES | Class + registry renamed to `OnePlusLambdaES` with alias; docstring explains the Rechenberg vs CMA-ES distinction | [`cma_es.py`](../src/perturb_eval/optimizers/cma_es.py) |
| mc8 | γ_T interpretation was handwave | Numerical γ_T per regime (greedy max-info-gain); §6.4 rewritten with honest caveats | [`bootstrap_and_analyze.py::max_information_gain`](../scripts/local/bootstrap_and_analyze.py), SUPPLEMENT.md §6.4 |
| mc9 | Default palette not colourblind-safe | Wong palette across trajectory figures; all five figures regenerated | [`render_figures_revised.py`](../scripts/local/render_figures_revised.py), PNGs in [`figures/`](../artifacts/modal_run/figures/) |
| mc10 | Vocab confound between grids | Documented in §7 Open Q #4; fix requires E2-synthetic rerun (~$2); deferred | SUPPLEMENT.md §7 |

Net: **8 of 10 critique items closed (MC1 + MC2 + MC3a + mc5 + mc6 + mc7 + mc8 + mc9). Two items remain (MC3b real-trace collection and mc10 vocab fix); MC4 deferred-explicitly with rationale.** Full audit trail including owner + date in [`INTERNAL_FOLLOWUP.md §2`](INTERNAL_FOLLOWUP.md).

## 4. Publication targets — in priority order

### 4.1 Preprint + MassGen contribution (immediate)

- [ ] upload SUPPLEMENT.md + code + artifacts to bioRxiv and arXiv cs.LG
- [ ] open a PR against [`tools/MassGen`](../../../tools/MassGen/) exposing the evaluation as a skill; draft already committed under [`massgen_skill_draft/`](../massgen_skill_draft/)
- [ ] submit PR to [`libs/cellforge-agents`](../../../libs/cellforge-agents/) for the preflight CLI hook
- Scope: what we can ship today, revisions or not.

### 4.2 *Nature Methods* Brief Communications (after §1, §2 revisions)

- [ ] 3-page Brief Communications draft using the supplement §5 numbers
- [ ] Single headline figure: three-panel (E3 / E3-Adamson / E3b) with regret curves
- [ ] Supplementary = current SUPPLEMENT.md
- Target: 6–8 week review cycle, revisions likely

### 4.3 ICLR 2027 Agent workshop (after §1, §2, §3 revisions)

- [ ] 8-page short paper emphasising the contextual-BO framing and γ_T analysis
- [ ] Required: real trace collection (MC3(b)) — ML audience won't accept simulated probes

## 5. Proposed repository organization for publication

The current layout is monorepo-ish. For the public release, split into two artifacts:

### 5.1 Public repo — `perturb-seq-eval`

```
perturb-seq-eval/
├── README.md                    ← 1-page overview + pip install + example
├── pyproject.toml               ← already Poetry-packaged
├── LICENSE                      ← Apache-2.0
├── CITATION.cff                 ← ADD
├── docs/
│   ├── THESIS.md
│   ├── DESIGN.md
│   ├── SUPPLEMENT_DESIGN.md
│   ├── SUPPLEMENT.md            ← reviewer-facing reproduction doc
│   ├── REVIEWER_CRITIQUE.md     ← transparency — "here's what we know is weak"
│   ├── PUBLICATION_CHECKLIST.md ← this file
│   └── figures/                 ← symlink or copy of artifacts/modal_run/figures/
├── src/perturb_eval/            ← library code
├── tests/                       ← 92 unit tests
├── scripts/
│   ├── fetch_adamson.py         ← one-command data download
│   ├── modal/app.py             ← Modal reproduction entrypoint
│   └── local/                   ← CPU-only debug + render scripts
├── paper/                       ← LaTeX for Brief Communications draft
└── artifacts/
    └── modal_run/               ← frozen artifacts snapshot (JSON/JSONL + PNG/PDF/HTML)
```

ADD at repo root:

- [ ] `CITATION.cff` with BibTeX entries for THESIS + SUPPLEMENT + upstream refs (Snell, Archon, Krause–Ong, Cui-scGPT, Lotfollahi-CPA, Roohani-GEARS, Adamson)
- [ ] `CHANGELOG.md` tracking the deviation log from SUPPLEMENT.md §9
- [ ] `.github/workflows/tests.yml` running pytest on PRs (CI already green locally; just wire it)
- [ ] `CONTRIBUTING.md` pointing at the metric-drop and optimizer-addition extension points
- [ ] `README.md` upgrade to lead with the three-regime plot and the "what does this reproduce" verification ladder

### 5.2 Data repo — `perturb-seq-eval-artifacts`

The `artifacts/modal_run/` tree is 22 MB of figures + 272 KB of JSON. Two options:

- **Zenodo DOI**. Upload the `modal_run/` tree to Zenodo with a DOI. Link from README.md + CITATION.cff. Standard for bio supplements. Required if we want the data citable from the paper.
- **git-lfs**. Keep artifacts in the repo under git-lfs. Simpler for reviewers but bloats clones.

Recommendation: **Zenodo DOI** for final artefacts; `artifacts/modal_run/` becomes a git-lfs-tracked mirror so the `jq`-it-yourself workflow still works from the git clone.

### 5.3 What to prune before making the repo public

- `artifacts/dry_run/` — supersceded by `modal_run/`. Either archive or delete.
- `paper/paper.aux`, `paper/paper.log`, `paper/paper.bbl`, `paper/paper.blg`, `paper/paper.out` — LaTeX build artefacts; add to `.gitignore` and remove from tracked history.
- `.ruff_cache/`, `.pytest_cache/`, `__pycache__/` — already-gitignored most places; audit.
- `massgen_skill_draft/` — keep, it's shipped intentionally.

## 6. Pre-submission checklist (final sweep) — updated 2026-04-22

| Item | Status | Evidence / what's still needed |
|---|---|---|
| 92/92 pytest green | ✅ | post-revision count still 92; `pytest -q` exit 0 |
| `poetry build` clean wheel | ✅ | `dist/perturb_eval-0.2.0-py3-none-any.whl` builds from Poetry |
| `modal deploy … && modal run … --step all` reproduces every number | ✅ | full 2026-04-21 Modal run; revision-pass rerun uses cached grids ($0) |
| Figures render inline in GitHub markdown | ✅ | PNG + Wong palette + CI bands; grep-verified in runbook §2.6 |
| Regret/CI revision (MC1) | ✅ | `revision_stats.json` + CI bands on Figs 2/3/4 |
| Backbone-tie reframe (MC2) | ✅ | §5.2 / §6.2 / §7 updated; retraction in §9 |
| Probe disclosure (MC3a) | ✅ | SUPPLEMENT.md status block + §5.3 preamble |
| Supplement bundle config (publish.yml) | ✅ | 3 files (paper + docs + modal_run); abstract aligned to §7 |
| Publishing runbook (scripted + manual + coherence audit) | ✅ | `research/PUBLISHING_RUNBOOK.md` §0/§2.5/§2.6/§6.1–6.4 |
| `.env.example` with all publishing-token slots | ✅ | repo-root `.env.example` + runbook §1.4 |
| Probe collection — real traces (MC3b) | ⬜ | skeleton in `scripts/modal/collect_traces.py`; 1 engineer-day to wire |
| Adamson SHA-256 recorded in README | ⬜ | run `sha256sum data/Adamson2016_pilot.h5ad` + paste into top-level README |
| Zenodo DOI minted for artifacts | ⬜ | run `submit_to_venues.py all` once blockers closed (PUBLISHING_RUNBOOK §5) |
| `CITATION.cff` at repo root with BibTeX for every cited paper | ⬜ | must include Snell 2024, Archon/Saad-Falcon 2024, Krause & Ong 2011, Krause-Singh-Guestrin 2008, Hansen 2016, Rechenberg 1973, Cui scGPT 2024, Lotfollahi CPA 2023, Roohani GEARS 2024, Adamson 2016, Lakshminarayanan et al. 2017, Du et al. 2023, Wang et al. 2022 |
| CHANGELOG.md entry at repo root for `v0.3.0-supplement` | ⬜ | mirror SUPPLEMENT.md §9 deviation log into a versioned CHANGELOG |
| README quick-start renders on GitHub | ⬜ | lead with three-regime plot + `modal run --step all` one-liner |
| No TODO / FIXME / XXX in shipped code | ⬜ audit | `grep -rnE "TODO\|FIXME\|XXX" src/ scripts/ --include='*.py'` |
| License headers in every source file | ⬜ audit | add `# SPDX-License-Identifier: Apache-2.0` to src/scripts modules |
| `pip install perturb-eval` works on a clean venv | ⬜ | `python -m venv .venv && .venv/bin/pip install dist/perturb_eval-*.whl && python -c "import perturb_eval"` |

**What's left before bioRxiv submission:** the four items marked ⬜ in
the bottom half of this table. Roughly half a day of admin work
(SHA-256, CITATION.cff, CHANGELOG, README lead) plus the token-holder's
wall time to run the scripted pipeline. Everything else is closed.

**What's left before ICLR-workshop submission:** the above **plus** MC3b
(real-trace collection, ~1 day) and mc10 (vocab fix + E2-synthetic rerun
on Modal, ~$2). See §7 for the integrated effort estimate.

## 7. Estimated time to submission-ready

- With only MC1 + MC2 + MC3(a) done: **2 engineer-days + $1 Modal** → bioRxiv preprint ready, Brief Communications draft startable.
- With MC1–MC4 + mc5 + mc10 + MC3(b) (real traces): **5 engineer-days + $12 Modal** → ICLR-workshop-ready short paper.

Either path fits inside the remaining Hackathon budget.
