# Pre-registration — v0.6.0 sweep

**Paper:** *Does Agent Confidence Entropy Predict Task Difficulty? A Pre-registered, Provenance-Complete Test of
Agentic Hyperparameter Tuning for Perturb-seq Response Prediction*

**Status:** fixed before the v0.6.0 sweep runs. The sweep's provenance record (`git_sha`, `git_dirty` in record 0
of `trainer_runs.jsonl` / `lifecycle_runs.jsonl` and in `provenance.json`) identifies the revision of this file in
force when the sweep ran. No commit hash is written here; the orchestrator records it at run time. If `git_dirty`
is `true` for the run, this file's committed revision is not by itself proof of what was in force, and the paper
must say so.

This file contains no result values. The v0.5.0 values are superseded in full (manuscript appendix
"Corrections relative to v0.5.0", which maps each one to the register row that supersedes it).

## Why the title is a question

The title asks whether agent confidence entropy predicts task difficulty, and does not assert that it does,
so that a null answer is publishable as it stands. **A null or failed outcome on H4/H5 must not be traded back
into a claim-form title, abstract or contribution list.**

## Design (fixed)

| item | value |
|---|---|
| datasets | Adamson 2016 (K562, CRISPR interference; scPerturb subsets pilot, 10X005, 10X010) and Norman 2019 (K562, CRISPR activation; single and double perturbations), scPerturb repackaging, Zenodo record 13350497 |
| integrity | all four files SHA-256 pinned in `src/perturb_eval/data/download.py`, cross-checked against the Zenodo record's size + MD5; fetch fails closed on a missing pin or a mismatch |
| held-out tasks | **41** = 21 Adamson (3 quantile bins of mean \|Δlog1p\| on the target gene × 7, drawn from the structurally eligible single-gene constructs) + 20 Norman (15 singletons + 5 doublets) |
| task draw | deterministic: CRC32-derived strata (never the process-salted `hash`), sorted pools, `seed = 2026`; the sampler asserts every stratum is filled exactly, else the run is refused in preflight; the resolved plan (tasks, strata, eligible-pool sizes) is written to provenance |
| label contract | Adamson raw construct labels parsed structurally (plasmid suffix and `_only` stripped); one component → gene task; multi-gene constructs excluded; `neg_ctrl` constructs are controls; cells with a missing annotation excluded with counts. Norman: renamed symbols joined on Ensembl IDs; unresolvable labels excluded with a reason. Every exclusion is recorded in provenance (`tasks_excluded`, per-dataset `label_contract`) |
| trainer sweep | per task: backbones {linear, mlp, scgpt_small} × N ∈ {3,5} × R ∈ {1,2,3} × 3 seeds = 54 configurations; seed threaded to the trainer |
| lifecycle | per task: 3 seeds of the five-agent lifecycle; seed threaded to the trainer and to the LLM cache key |
| process | one sweep, one process: preflight → trainer sweep → lifecycle sweep; both JSONLs must carry the identical task set or the analyser refuses to summarise |

## Conventions the estimators depend on

1. **Features — HVG on training cells only.** For each held-out task, highly variable genes are selected on
   that task's training cells only, with the target gene(s) force-included. Models for different tasks
   therefore use different feature spaces; every cross-task median below is a median over models with
   differing inputs.
2. **Evaluation genes — top-20 DEGs.** The error metric is the mean squared deviation (MSD) between predicted
   and observed mean log-fold-change over the 20 genes with the largest absolute mean difference between the
   held-out perturbation's cells and control cells — the CPA/GEARS convention. These genes are selected using
   the held-out cells; this is the convention, stated, not changed.
3. **Best-of-54 is an oracle.** The per-task minimum over the 54 trainer configurations is selected on the same
   evaluation split it is scored on. It is an **attainable upper bound (oracle)**, never an estimate of held-out
   performance. There is no nested validation/test split in this design.
4. **LLM-sourced steps only.** Every lifecycle step is labelled `source ∈ {llm, fallback}` and, when `llm`,
   carries the serving `model_id`. **A run with any `fallback` step is invalid by construction**: the run is
   marked failed and the analyser refuses to summarise it. Agent-choice statistics are computed over
   `source == "llm"` steps only; steps without a `source` field are never assumed to be LLM-sourced.
5. **LLM condition.** A rotating pool of OpenRouter models with failover; the roster is recorded in provenance
   (`llm_pool`) and the serving model per step (`model_id`). Model identity is recorded, not controlled; H3 is
   evaluated over the pooled mixture, and a per-`model_id` breakdown is reported descriptively.

## Hypotheses, gates and estimators

Estimator code: `src/perturb_eval/experiments/preregistered.py` (module `perturb_eval.experiments.preregistered`),
called from `analyse_v05_run` in `src/perturb_eval/experiments/e_v05_real_traces.py`, which writes the results
to `summary.json` under `preregistered` (H1–H5 and the tally) next to `preregistration` (the pin copied from
record 0, naming the commit that fixed this plan). The function named in each row is the estimator.

| id | hypothesis | gate | estimator |
|---|---|---|---|
| H1 | The trainer sweep attains low error on Adamson | median < **0.20** | per Adamson task, min over the 54 configurations of MSD@top-20-DEG (oracle, convention 3); median over the 21 tasks. Non-finite (error) records are excluded from the minimum. `preregistered.h1_h2_stats` |
| H2 | The trainer sweep attains low error on Norman | median < **0.30** | as H1 over the 20 Norman tasks, also split singleton / doublet. `preregistered.h1_h2_stats` |
| H3 | The Architect exercises its backbone choice | entropy ≥ **0.5 nats** | Shannon entropy (natural log) of the empirical distribution of `backbone` over all Architect steps with `source == "llm"`, pooled across tasks, seeds and rounds; ceiling ln 3. Entropy from `analyse_v05_run` (T16), gate by `preregistered.h3` |
| H4 | A trace-derived difficulty feature ranks tasks by held-out error | Spearman ρ > **0.5** for ≥ 1 of {ACE_norm, 1−ΔC, TDI_lifecycle} within Adamson **or** within Norman (6 tests) | unit = task; per task, each component (definitions below) and the lifecycle's final MSD@top-20-DEG are each the median over the task's three seeds; Spearman ρ over the tasks of ONE dataset (21 Adamson; 20 Norman), default weights, no in-sample calibration. All six ρ are reported, with n and a bootstrap CI over tasks. The ρ pooled over all 41 tasks is reported as **descriptive only and never gates**. `preregistered.h4` |
| H5 | The calibrated two-component TDI transfers across datasets | Spearman ρ > **0.4** | TDI weights over {ACE_norm, 1−ΔC} fitted by ridge regression (α = 1.0) on the Adamson tasks (target: per-task lifecycle MSD), then applied unchanged to the Norman tasks; Spearman ρ between Norman TDI and Norman MSD, with n and a bootstrap CI over Norman tasks. `preregistered.h5` |

Five gates. Each is reported as PASS, FAIL, or UNEVALUATED with the reason; the tally is always stated out of
five. An unevaluated gate is never dropped from the denominator.

## H4/H5 definitions (principal-ratified 2026-09-24: D-H4, D-EST, D-WHEN)

Decided and implemented, with tests, before any v0.6.0 sweep data exists (D-WHEN).

**TDI_lifecycle is not the published TDI.** The published Task Difficulty Index (manuscript §Metrics,
equation `eq:tdi`) combines four components: ACE_norm, CSD (variance of the critique matrix), 1−ΔC and WFR
(winner flip rate). CSD and WFR are **structurally undefined** for the five-role agentic lifecycle: it records
no critique matrix and has no per-round winner. The four-component TDI was therefore never computable on this
testbed and **is not evaluated**. This is stated here, up front; CSD and WFR are not "reported later as n/a".
H4 and H5 use only the components computable from lifecycle traces, and **TDI_lifecycle, the two-component
combination defined below, is a different quantity from the four-component TDI. Its ρ must not be compared with
the v0.4.1 TDI ρ = 0.92** (review A2-6).

**Per-run components** (`preregistered.per_run_components`; semantics taken from `src/perturb_eval/metrics.py`):

- Round r's confidence vector C(r) is the `llm_confidence` of the run's steps with `round_index == r` and
  `source == "llm"`. Fallback, mock and unlabelled steps are excluded. A run's rounds are the distinct
  `round_index` values of its steps; *first* and *last* are the minimum and maximum.
- **ACE_norm** = `metrics.ace_norm(C(last))`: the Shannon entropy of softmax(C(last)) at τ = 1, divided by
  ln N. This is the final-round value that `metrics.tdi` reads as `last.ace_norm`.
- **ΔC** = `metrics.delta_mean_confidence`: mean C(last) − mean C(first), for a run with **at least two rounds**.
  For a one-round run (the Validator accepted in round 0), ΔC — and so 1−ΔC and TDI_lifecycle — is
  **undefined** (reason `single-round run: ΔC requires >= 2 rounds`). ACE_norm is unaffected. See
  "Single-round runs" below.
- **1−ΔC** is the normalisation `metrics.tdi` applies: 1 − min(max(ΔC, 0), 1).
- **TDI_lifecycle** = clip₀₁( (7/12)·ACE_norm + (5/12)·(1−ΔC) ). These are the hand-set default weights in
  `metrics.DEFAULT_TDI_COEFFS`: α = 0.35 on ACE_norm and γ = 0.25 on 1−ΔC, renormalised over the two
  (0.35/0.60 and 0.25/0.60).
- **Undefined, not imputed.** A component is undefined for a run when a round it reads has fewer than two
  LLM-sourced steps or a non-finite confidence, and 1−ΔC and TDI_lifecycle are also undefined for a one-round
  run. ACE_norm reads *last*; 1−ΔC reads *first* and *last*;
  TDI_lifecycle is undefined if either input is. The value is `None` with a reason, and it is left out of the
  seed median. The per-task table records how many seeds entered each median and why any were left out. A task
  with no defined value for a component after exclusion drops out of that component's ρ, and is counted. The H4
  result reports, per dataset and component, the runs left undefined, how many of those were single-round, and
  the tasks dropped (`exclusions`).

**Single-round runs (principal-ratified 2026-09-24/25).** `metrics.delta_mean_confidence` returns ΔC = 0 for a
run with fewer than two rounds, which makes 1−ΔC = 1, the maximum "lack of convergence" value. Under that
convention, immediate convergence — the Validator accepting in round 0, which is what an easy task looks like —
would score as maximal difficulty. That is a built-in bias against H4. The pre-registered estimator therefore
does **not** use the metrics.py convention for this case: ΔC requires at least two rounds, and a one-round run's
1−ΔC and TDI_lifecycle are undefined, excluded from the seed median and counted. The code still calls
`metrics.delta_mean_confidence`, but only when there are two or more rounds.

One property of these pinned definitions is stated now, so that it is not discovered later: at τ = 1, the softmax of confidences in [0, 1] is close to uniform, so ACE_norm occupies a narrow band just
   below 1. The rank statistics are unaffected, but the range is narrow.

**Estimators (D-EST).**

- The unit is the task. Per task, each component and the lifecycle's final MSD@top-20-DEG are each the
  **median over the task's three seeds** (`preregistered.per_task_table`). This presupposes the A2 fix, which
  threads the seed into `run_agentic_lifecycle`. On pre-fix artifacts the three seeds were identical runs and the
  median would have been the median of three identical values.
- Spearman ρ uses average ranks for ties (`preregistered.spearman_with_ci`). ρ is undefined for n < 3 or for
  constant input. **Minimum n (principal-ratified 2026-09-24/25): every gate — and, for H4, every
  per-dataset test — needs at least 3 tasks**; below that it is not evaluable. **An unevaluable gate reports
  `pass = None`, never FAIL by default.** H4 is FAIL only if all six per-dataset tests are evaluable and none
  exceeds 0.5.
- **Bootstrap:** a percentile bootstrap over TASKS. There are B = 10 000 resamples of task indices, drawn with
  replacement using `numpy.random.default_rng(2026)`, and the 95% interval is taken from the 2.5th and 97.5th
  percentiles. Resamples with constant ranks are dropped and counted (`n_boot_valid`). The same specification
  gives the CI of the median for H1/H2.
- **H5 ridge:** closed-form ridge (`preregistered.fit_ridge`) on the two features, each standardised with the
  **Adamson** mean and population s.d., with the target centred and the intercept unpenalised. The ridge
  parameter is **α = 1.0**, fixed now and never tuned, on Norman or anywhere else. Standardising makes the
  penalty independent of scale, which matters because ACE_norm's range is narrow. With about 21 Adamson tasks,
  α = 1 is mild shrinkage: the diagonal of Z'Z equals n. Norman TDI = Σ_k w_k (x_k − mean_k^Adamson) /
  sd_k^Adamson. The intercept is left out because it does not change ranks.

**What these estimator choices close** (so that they cannot be loosened later):

- *No in-sample calibration for H4* closes F12. There, the oracle weights were fitted and scored on the same
  traces.
- *Ridge weights fitted on Adamson and applied unchanged to Norman* make H5 genuinely out-of-sample. No Norman
  value enters the fit, and a test asserts this.
- *Bootstrap over tasks, not runs or seeds*, closes F8, the defect of treating pseudo-replicates as i.i.d.

**H4 gate and its multiplicity (principal-ratified 2026-09-24/25).** H4 is evaluated **within each dataset
separately**: ρ for each of ACE_norm, 1−ΔC and TDI_lifecycle within Adamson and within Norman. That makes **six
tests (3 quantities × 2 datasets)**. The gate passes if **any** of the six exceeds ρ = 0.5. The ρ pooled over all
41 tasks is reported as descriptive only and never gates. Pooling would mix two screens with different MSD
scales, so a between-dataset difference could produce a ranking with no within-dataset signal.

The six tests are not independent. Within a dataset, TDI_lifecycle is a fixed, hand-weighted sum of the other
two quantities, so each dataset contributes closer to two effective tests than three. Across datasets the tests
use disjoint tasks. Let **p** denote the probability, under the null (no association), that a single test's ρ̂ exceeds 0.5 — the gate thresholds the **statistic**, not a p-value. Measured by permutation **through the pre-registered estimator itself** (`preregistered._rho`, average-rank Spearman; `scripts/local/prereg_null_fwer.py`, seed 2026, 200,000 permutations; amendment 2026-09-25, CTO #269):

| quantity | null false-positive rate |
|---|---|
| one test, n = 20 (Norman) | p = 1.32 % |
| one test, n = 21 (Adamson) | p = 1.07 % |
| **the pre-registered six-test gate** (Monte Carlo of the whole gate, 100,000 draws; TDI_lifecycle built from the other two exactly as in the estimator) | **2.35 % – 5.81 %** |
| a single pooled test, n = 41 | 0.0475 % |

The gate's range is bracketed, not estimated: 5.81 % if ACE_norm and 1−ΔC are independent under the null, 2.35 % if their ranks are identical; the true value lies between and depends on their unknown dependence. The gate therefore carries a false-positive rate roughly **50× to 120× that of a single pooled test** — the price of testing within datasets at n ≈ 20, which we accept because a pooled ρ can be produced by the between-dataset difference alone (the committed fixture in `tests/test_preregistered.py`: pooled ρ = 0.543 while every within-dataset ρ = −1, gate FAIL). **No multiplicity correction was pre-registered.** Instead, **all six ρ are reported with their n regardless of outcome — pass, fail or undefined** (`h4(...)["all_six"]`, always six rows, with `n_tests_passing`), so a PASS carried by a single test is self-evident from the table and selective reporting is structurally impossible rather than discouraged.

### Required alongside each gate

- H1/H2: n per dataset, median, IQR, max, fraction of tasks above the threshold, a percentile bootstrap CI over
  tasks, and the Norman figures split by singleton/doublet stratum. The median is the gate; the dispersion is
  reported regardless of the gate outcome.
- H3: pick counts per backbone, number of LLM-sourced Architect steps, number of distinct `model_id`s, per-role
  distinct-proposal counts.
- H4/H5: n, ρ, and a bootstrap CI over tasks for each of ACE_norm, 1−ΔC and TDI_lifecycle within each dataset,
  plus the pooled (descriptive) ρ and the exclusion counts (H4), and for the
  transferred TDI (H5, with the fitted weights and the Adamson standardisation); per-seed undefined components
  are reported with the reason, never imputed. CSD and WFR are structurally undefined (above), not "not computable".
- Run record: actual spend (not the cap), GPU-hours, `git_sha` / `git_dirty`, fallback-step count (must be 0).

## Implementation (estimator code paths)

- H1–H5 are computed by `src/perturb_eval/experiments/preregistered.py`, called from `analyse_v05_run`
  (`src/perturb_eval/experiments/e_v05_real_traces.py`), and tested on hand-built fixtures in
  `tests/test_preregistered.py`. The earlier, uncalled `tdi_vs_held_out_msd` has been removed.
- The dispersion and bootstrap figures listed under "Required alongside each gate" are computed for H1, H2, H4
  and H5. The H3 figures are pick counts, the number of LLM-sourced Architect steps and the number of distinct
  `model_id`s.
- **Flagged, not implemented (principal-ratified 2026-09-24/25):** the H3 per-`model_id` breakdown and the
  per-role distinct-proposal counts. Both are descriptive and do not gate. They are not computed by the
  analyser (`entropy_by_role` is). If they are not implemented before the sweep, they are reported as not
  computed.
- A diagnostic summary (fallback or partial run) sets every gate to `pass = None` with the reason.
