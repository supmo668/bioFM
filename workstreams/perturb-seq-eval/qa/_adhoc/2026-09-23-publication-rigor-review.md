---
type: review
scope: projects/perturb-seq-eval — paper/ + experimental workflow
reviewer: bioFM/matthew-mo/cto
date: 2026-09-23
artifact_under_review: paper/paper.tex @ v0.5.0 + artifacts/v0.5.0/
verdict: NOT SUBMITTABLE — two blocking defects invalidate the headline claim
---

# Publication-rigour review — perturb-seq-eval v0.5.0

Reviewed as a methods referee at a venue that checks artifacts against prose.
Every finding below was verified against committed files; the evidence is cited
so none of it has to be re-derived.

## Verdict

The engineering substrate is genuinely strong — frozen trace schema, SHA-gated
fetchers, atomic resume-safe JSONL, 209 tests, $4.04 of compute for 1,944
trainer cells. That part is publication-grade.

The **empirical argument is not**. The paper's title claim is unevaluated, and
the one experimental condition that would let a reader interpret the headline
number is neither correctly stated nor recorded. Two blocking defects, then a
set of major ones.

---

## BLOCKING

### R1 — The central claim has no reported result, and the gate tally omits it

`paper/sections/v050_results_filled.tex:58–74` (Table `tab:tdi-real`) reports
`n/a` for the Spearman ρ of **every** TDI component against held-out MSD — ACE,
1−ΔC, CSD, WFR, and the calibrated TDI sum. §4.4 cross-dataset transfer
likewise reports `ρ = n/a`.

So the paper titled *"Agent Confidence Entropy as a … Difficulty Oracle"*
reports no measurement of whether agent confidence entropy predicts difficulty.

Verified: `artifacts/v0.5.0/summary.json` contains no correlation key at all.
`src/perturb_eval/experiments/e_v05_real_traces.py:158–159` returns
`{"spearman": nan}` when fewer than three feature values are extractable, and
the filler renders that NaN as `n/a`. The correlations were never computed.

Two consequences compound it:

1. **§6 Discussion asserts a result the table does not contain.** It states the
   ΔC signal "ranks tasks by held-out MSD with the trace-feature correlations
   reported in Table~\ref{tab:tdi-real}" — a forward reference to an empty
   table. §4.2 similarly claims the backbone-choice difference "correlates with
   task difficulty (Section~\ref{sec:tdi-real})", where §4.3 contains no
   correlation. A referee who follows one cross-reference finds the paper
   citing absent evidence for its thesis.
2. **The abstract's gate tally silently drops the unevaluated gates.** It says
   "Two of three pre-registered gates pass." Five gates are pre-registered in
   the text: Adamson MSD < 0.20, Norman MSD < 0.30, Architect entropy ≥ 0.5
   nats, TDI ρ > 0.5 for ≥ 1 component (§4.3), cross-dataset ρ > 0.4 (§4.4).
   The two that could not be evaluated are excluded from the denominator rather
   than reported as unevaluated. Honest form: "two of five pass, one fails, two
   are unevaluated."

**Smallest fix:** compute the correlations from the 108 committed lifecycle
traces and report them with n and a CI — or, if the traces cannot support them,
retract the oracle claim from the title, abstract, contribution list and
Discussion, and reframe the paper as the infrastructure + agentic-lifecycle
result it currently is. The second option is publishable. The present draft is
neither.

### R2 — The experimental condition is misstated in the paper and unrecorded in the artifact

The paper states a single model four times: "we use \textsc{Nemotron-30B}
throughout" (abstract), "we drive every agent with \textsc{Nemotron-30B}"
(§3.4), and twice more in §8.3 and the conclusion.

Three independent contradictions:

- `CHANGELOG.md` §[0.5.0] states all LLM calls ran through a **rotating
  free-tier pool of eight heterogeneous models** (Nemotron-3 Super 120B, Ling
  1T MoE, Hermes-3 405B, GPT-OSS 120B, Qwen3-Next 80B, Llama 3.3 70B, Gemma-4
  31B, Gemma-3 27B) with role-preferred selection and 60 s cooldown failover.
- `configs/live.yaml:24` pins `nvidia/nemotron-3-super-120b-a12b` — a 120B
  model. "Nemotron-30B" names nothing in the pool and misstates the scale 4×.
- `artifacts/v0.5.0/lifecycle_runs.jsonl` steps carry **no model field**.
  Record keys are `backbone_used, dataset, final_msd_topk,
  final_validator_agreement, n_agents, n_rounds, seed, steps, task_id,
  wall_sec`. Which model produced which proposal is unrecoverable from the
  artifact.

This is not a naming slip. If proposals were served by whichever pool member
was off cooldown, then **model identity is an uncontrolled variable that varied
with API availability rather than with task**. The headline lifecycle result —
backbone entropy 0.36 nats, 91% `scgpt_small` — is confounded: the paper
attributes the concentration to a coherent backbone signal, but cannot
distinguish that from eight models with differing priors being sampled
non-uniformly across tasks.

It also violates the standing repo-wide constraint that every run log the exact
config it ran under.

**Smallest fix:** add `model_id` (and the resolved pool state) to every step
record; re-derive the entropy result per model or restate it as pooled across
an uncontrolled model mixture; correct the model name and scale everywhere.

---

## MAJOR

### R3 — Stated dataset composition contradicts the artifact

Abstract, `v050_experimental_setup.tex:26–30`, the conclusion, and
`CHANGELOG.md` all state Norman 2019 contributes "15 singletons + 5 doublets"
— 20 held-out tasks.

The artifact has **15 Norman tasks total: 7 singletons + 8 doublets**
(`artifacts/v0.5.0/summary.json`, `best_config_per_task` filtered to
`dataset == norman`). `n_tasks_analysed = 36 = 21 + 15`, and the results table
correctly prints n = 15 — contradicting the setup section two pages earlier.

The stratified sampler did not produce the documented design. Either the
sampler or the description is wrong; a referee checking n against the design
finds the paper disagreeing with itself.

### R4 — A single median conceals catastrophic per-task failure

Table `tab:headline-msd` reports one number per dataset with no dispersion, no
CI, and no n per cell. The committed per-task minima say:

| | min | Q1 | median | Q3 | max | tasks over gate |
|---|---|---|---|---|---|---|
| Adamson (n=21) | 0.023 | 0.111 | **0.147** | 0.371 | **7.696** | **7/21 (33%)** |
| Norman (n=15) | 0.039 | 0.053 | **0.131** | 0.248 | 0.569 | 1/15 (7%) |

Two Adamson tasks — EP300 (7.696) and CREB1 (7.689) — miss the 0.20 gate by
roughly **50×**. A third of Adamson tasks fail it. The median passes and the
gate is pre-registered on the median, so quoting it is legitimate; quoting
*only* it is not. The mean is ≈ 0.9, and the honest summary is "controlled on
two-thirds of tasks, with two order-of-magnitude failures we do not yet
explain."

This is the live half of the project's own `docs/REVIEWER_CRITIQUE.md` MC1
("zero confidence intervals on every headline number"), still unaddressed five
months later.

**Fix:** report median + IQR + max + fraction over gate, with a bootstrap CI
over tasks, and name EP300/CREB1 with a hypothesis.

### R5 — "Best of 54, then median over tasks" is a doubly-optimistic estimator

§4.1 takes the **minimum** MSD over 54 configurations per task, then the median
of those minima. Both operations select downward. If the minimum is chosen on
the same held-out split that is then reported, the statistic is
selection-on-test and is not an estimate of held-out performance at all.

`n_configs_tried: 54` is recorded per task, so the selection breadth is
auditable — but no nested split appears in the reported design.

**Fix:** either select the config on a validation split and report on a
disjoint test split, or relabel the quantity honestly as an oracle / attainable
upper bound and stop calling it held-out performance.

### R6 — A section asserts what its own data refutes

§4.2 is titled *"Agents genuinely use their configuration freedom"* over a
result in which 91% of 138 Architect picks are the same backbone and the
pre-registered entropy floor **failed** (0.36 vs ≥ 0.5 nats). §8.3 then
rationalises the miss as "substantively the right call given a coherent
backbone signal" — while R2 shows the signal's provenance is confounded.

Reporting a missed gate rather than re-prompting around it is exactly right and
should be kept. Titling the section with the refuted conclusion is not. A
referee reads the pair as interpretation selected to favour the method.

**Fix:** retitle to the finding ("Configuration freedom is exercised on the
data-curation axis, not the backbone axis"), state the null result plainly, and
move the rationalisation to Limitations as a hypothesis.

### R7 — The real/synthetic framing is defensive and should be deleted

This is the principal's standing instruction, and the manuscript is a clear
instance: **"synthetic" appears 17 times and "real" 32 times** across
`paper.tex` and the section files.

Three separate assertions in the first two pages that no synthetic data was
used: abstract ("Every reported number in this paper comes from real Perturb-seq
data"), §1 contribution 3 ("we evaluate every claim end-to-end on *real*
Perturb-seq data"), §1 Scope ("*No synthetic Perturb-seq data is generated or
consumed by any reported result.*"). Then again in §3.1, three times in §8
Reproducibility, in §9, and in the conclusion. §4 is titled *"Results on Real
Perturb-seq Data"*.

Why this hurts the paper rather than protecting it:

1. **Provenance is table stakes.** Naming Adamson 2016 and Norman 2019 with a
   Zenodo record and checksums *is* the claim. Asserting the negative eight
   times reads as a defendant's brief and invites the question it answers.
2. **It advertises the retraction.** The v0.4.1 synthetic DGP is withdrawn.
   Nothing obliges the manuscript to carry that scar; three LaTeX comments
   ("synthetic experiments removed entirely", "nothing to defend") do so even
   in the source.
3. **The section title implies a contrast that no longer exists** — "Results on
   Real …" invites "as opposed to which results?"
4. **A CI guardrail is an engineering fact, not a paper claim.**
   `tests/test_no_synthetic_generators.py` belongs in the repo README, not in
   §8 of a manuscript.

**Fix:** one factual *Data and provenance* paragraph in §3 — datasets, scPerturb
repackaging, Zenodo record, SHA-gated fetchers, stratification and seed — and
delete every other instance of both words. Retitle §4 to "Results". Drop the
LaTeX comments. Say what the data *is*; never what it is not.

Same class, same fix: **"for demonstration purposes" appears 4×** as a hedge on
the model choice. A model is either the experimental condition or it is not.
State it, and put single-backbone-LLM in Limitations.

### R8 — `scgpt_small` is a misleading identifier the paper apologises for three times

A 2.1 M-parameter from-scratch gene-token transformer is named after a
published pretrained foundation model, and the paper then disclaims the
resemblance in §3.2, again in §8.1 ("to avoid implying we tested a real
foundation model"), and again in the CHANGELOG. Three disclaimers concede the
name is wrong instead of fixing it — and the manuscript still cites
`cui2024scgpt` in §2 among backbones "the architect agent can configure."

A referee skimming Table 2 and the backbone distribution sees `scgpt_small`
beside an scGPT citation and reasonably concludes a pretrained SCFM was
evaluated. Rename in code, artifacts and prose — `gene_tx_2m` or similar — and
the three disclaimers collapse into one sentence of Limitations.

---

## MODERATE

### R9 — The provenance record omits the revision it claims to pin

§9 states "Rerunning the Modal command with the same code revision produces
byte-equivalent JSONLs." `artifacts/v0.5.0/provenance.json` records timings,
GPU-seconds, cost, and the entropies — and **no git SHA, no seed, no dataset
checksums, no library versions**. Nothing in the artifact identifies the
revision whose re-run is promised, so the claim is untestable by a third party.

Also worth correcting while there: the paper quotes the **$28 cap** as though
it were the spend. The actual run cost **$4.04 over 3.06 GPU-hours**
(`provenance.json`). The real figure is both more impressive and more useful.

### R10 — The internal reviewer critique is stale and reads as current

`docs/REVIEWER_CRITIQUE.md` is dated 2026-04-21 and reviews the **retracted**
v0.4.1 line: its MC2 and its strengths section turn on the 7.6× task-conditional
dominance and the 2.6% contextual-GP edge, both withdrawn in v0.5.0. Anyone
reading it as the current assessment is reading a review of a different paper.

Its MC1 (no confidence intervals) survives the retraction untouched and is R4
above.

**Fix:** re-scope the file to `v0.4.1` in its frontmatter and title, and run a
fresh critique against v0.5.0.

### R11 — Title drift between thesis and manuscript

`docs/THESIS.md:1` — "Agent Confidence Entropy as an **Empirical** Difficulty
Oracle for Multi-Agent Group Generation, **with a Bayesian Pre-Test for**
Agentic Hyperparameter Tuning on Perturb-Seq Experimental Design"
`paper/paper.tex:28–31` — "… as a **Pre-hoc** Difficulty Oracle …**:** Bayesian
Agentic Hyperparameter Tuning …"

Two titles for one paper, and `THESIS.md` is still marked "working draft v0.1,
2026-04-18" while the manuscript is described as release-ready with a social
kit written. Pick one title; propagate it.

---

## What the workflow currently cannot support

Stated plainly, so the rewrite does not have to rediscover it:

- **Any claim that ACE/TDI predicts task difficulty.** Not measured (R1).
- **Any attribution of the backbone-concentration result to task properties.**
  Model identity is confounded and unrecorded (R2).
- **Any claim of held-out performance from the MSD medians.** They are minima
  over 54 configs with no nested split (R5).
- **Any claim that a foundation model was evaluated.** It was a 2.1 M
  from-scratch transformer (R8).
- **Byte-equivalent reproduction by a third party.** No revision or checksums
  in the provenance record (R9).

## Recommended sequence

1. R2 — add `model_id` per step, then re-derive or restate the entropy result.
   Everything downstream depends on knowing what ran.
2. R1 — compute the TDI correlations from the committed traces, or retract the
   oracle claim. This decides what the paper *is*.
3. R3, R4, R5 — fix n, add dispersion + CIs, fix the estimator or relabel it.
4. R7, R6, R8 — language pass: delete the real/synthetic framing and the
   hedges, retitle §4.2 to its finding, rename the backbone.
5. R9, R10, R11 — provenance record, re-scope the stale critique, one title.

Steps 1–3 are substantive and may change conclusions. Step 4 is the language
pass the principal asked for and should run **last**, once the claims it has to
describe are settled.

---

# Addendum — code + workflow audit (2026-09-23, same day)

A read-only methods audit of the pipeline ran after the manuscript review above.
It found defects **more severe than anything in R1–R11**, and — importantly — it
supplies the *mechanisms* for findings the manuscript review could only observe
from the outside.

**Every finding below marked CONFIRMED-BY-CTO I re-verified myself** against the
committed code and artifacts, rather than accepting the audit's account. One of
its claims was overstated; that is recorded as such.

## The verdict changes

R1–R11 said the empirical argument was unsupported. The audit shows **two
headline results are artifacts of code defects**, and the v0.5.0 artifact set
cannot have come from the single run its provenance record describes.

### A1 — The trainer and lifecycle task sets are almost disjoint (CONFIRMED-BY-CTO)

`artifacts/v0.5.0/` — trainer file has 36 tasks, lifecycle file has 36 tasks,
and they **share exactly 2**: `SRP72` and `SAMD1_ZBTB1`. Trainer-only includes
`ATF6, BAK1, CAD, CARS, …`; lifecycle-only includes `AARS, AMIGO3, C7orf26,
CCND3, DDIT3, …`.

`scripts/modal/app_v05.py:234-240,334-338` iterate the *same* `tasks` list in one
process, so a single run cannot produce this. `provenance.json` nonetheless
reports both counts under one wall-clock window and one cost figure, and
`analyse_v05_run` **joins them** — `n_tasks_analysed: 36` comes from the trainer
file while the entropies come from the lifecycle file.

So `v050_results_filled.tex:30` ("Across 108 lifecycle runs spanning 36 held-out
tasks") describes a join across two nearly-disjoint task samples. **Every
statement linking agent behaviour to task difficulty is computed across a 2-task
intersection.** Probable proximate cause is A6.

### A2 — The 108 lifecycle runs are 36 runs counted three times (CONFIRMED-BY-CTO)

`app_v05.py:340-357` records the loop's `seed` into each record but never passes
it to `run_agentic_lifecycle`, which has no `seed` parameter; the LLM cache key
omits it too. Verified: **36 of 36 tasks have byte-identical `final_msd_topk`
across seeds 2026/2027/2028** (e.g. `AARS` → 0.2796782707371149 three times).

`n = 108`, `n_lifecycle_finite = 108`, and "138 Architect picks" are inflated 3×
by exact duplicates. Effective n = 36 tasks / 46 picks. Any standard error
computed on 108 is √3 too narrow.

### A3 — Four of the five "free-acting agents" emitted one identical proposal (CONFIRMED-BY-CTO, with a correction)

Recomputed over all 690 committed lifecycle steps (138 per role):

| role | distinct `proposal_content` |
|---|---|
| Architect | 13 |
| DataCurator | **1** |
| Literature | **1** |
| Trainer | **1** |
| Validator | **1** |

Each of those four equals its Pydantic schema default. So §4.2's claim that
"agents are not role-rigid executors" is refuted by the project's own trace
file: four of five roles produced the same default 138 times, and the widened
configuration space in §3.3 (`hvg_method`, `qc_mito_max`, `split_strategy`,
`batch_correction`, the dynamic Validator threshold, `which_genes_failed`,
`suggested_next_config_delta`) is pinned at defaults throughout. The fingerprint
is `_rule_based_fallback` in `llm_agent_pool.py:90-109`, and `LifecycleStep` has
**no field distinguishing LLM output from fallback**, so this is unrecoverable
from the artifact rather than merely unreported.

**Correction to the audit.** It reported `rationale == ""` for 138/138 steps and
`llm_confidence == 0.7` for 138/138, and inferred from the constant confidence
that "ACE_norm is identically 1.0 and CSD identically 0, therefore TDI cannot
correlate with anything." The premise is wrong. Measured across 690 steps:
**651 empty rationales, 39 non-empty** with genuine LLM text ("MSD@20 = 7.6917
exceeds threshold…", "HSPA5 encodes BiP/GR…"), and **684 × 0.7 with 6 exceptions
(3 × 0.82, 3 × 0.68)**. Confidence is 99.1% constant, not identically constant,
so ACE is near-degenerate rather than degenerate, and that inference does not
carry. The independently verified mechanism for R1's `n/a` stands on its own:
`tdi_vs_held_out_msd` is never called, and its default feature path names a field
present in no schema.

### A4 — A random gene is silently substituted for the perturbation target (CONFIRMED-BY-CTO)

`src/perturb_eval/experiments/norman.py:119-120`:
```python
# Target dropped by HVG filter — pick a deterministic fallback.
target_gene_idx[norm_label] = int(rng.integers(0, len(gene_names)))
```
A **random gene** becomes the perturbation target, with no error and no flag, in
a branch commented as deterministic.

It fires because the doublet guard is the wrong delimiter. `norman.py:110` and
`app_v05.py:211` test `"+" in label`, but the committed Norman labels use `_`:
`CBL_UBASH3A, CEBPB_PTPN12, CEBPE_RUNX1T1, KLF1_MAP2K6, SAMD1_TGFBR2,
SAMD1_ZBTB1, SNAI1_UBASH3B, UBASH3B_PTPN9` — **8 of 15**. So the doublet stratum
is empty (which is why R3's "15 singletons + 5 doublets" degenerated to 15), and
those 8 combo labels are not single gene symbols, so each received a random
target index. They were then trained and scored as ordinary tasks and
**contribute to `median_msd_norman = 0.131` and to `GATE_NORMAN = PASS`**.

The same fallback exists in `e2_adamson.py:209-212`, and `loop.py:222-226` maps a
missing target to gene index 0.

### A5 — The config embedding collapses the backbone axis (CONFIRMED-BY-CTO)

`src/perturb_eval/optimizers/base.py:34`:
```python
backbone_index = {"scGPT": 0, "scPRINT-2": 1, "scFoundation": 2}.get(phi.backbone, 0)
```
Every experiment uses `{linear, mlp, scgpt_small}`. **None is a key**, so all
three map to index 0 and `config_to_vec` emits an identical vector for all three
backbones at a given `(N, R)` — 27 configs collapse to 9 distinct embeddings.
`nearest_config` then breaks the 3-way tie by `argmin`, which always returns
`linear`.

So the CMA-ES baseline **cannot propose `mlp` or `scgpt_small`** and searches 9
of 27 configs. The audit derives the retracted 7.6× figure as
`0.075 / 0.00989 = 7.58` and shows the baseline's per-run MSDs take exactly two
values matching a linear-restricted optimum — i.e. the headline measured the bug.
That result is already retracted, but **the same collapsed embedding feeds every
published γ_T**, and `tests/test_optimizers.py:22-26` builds its space from
`("scGPT","scPRINT-2")` — the only names the dict recognises — so no test can
catch it.

### A6 — Task selection is non-deterministic across processes (CONFIRMED-BY-CTO on mechanism)

`app_v05.py:217,224` compute strata as `hash(s) % 3` on Python `str`. `str.__hash__`
is salted per process unless `PYTHONHASHSEED` is fixed, so the stratum assignment
— and therefore which tasks `stratified_subsample(seed=2026)` draws — changes on
every invocation. **The `seed=2026` is cosmetic.** This is the most plausible
proximate cause of A1.

### A7 — Nothing is checksummed, contradicting the paper (CONFIRMED-BY-CTO)

`src/perturb_eval/data/download.py:34` — `sha256: Optional[str] = field(default=None)`
for every `DatasetSpec`; `_fetch` logs "already present (no SHA pin) — trust it".
The only integrity check is a `min_bytes` floor. §3.1 and §9 both claim
"SHA256-gated" fetchers. The machinery exists; **nothing is pinned.**

## Further findings I did not independently verify

Reported by the audit, mechanism plausible, not re-checked by me — treat as
leads, not facts, and confirm before acting:

- **The contextual GP is non-contextual in every experiment.** A fresh optimizer
  per `(task, seed)` with the same `ctx` on all iterations makes the context
  kernel the all-ones matrix, so no cross-task sharing and no routing is possible
  even in principle. Offered support: three different probe provenances yield
  bit-identical trajectories, which `SUPPLEMENT.md:250` notices and attributes to
  budget saturation. If true, "probe-conditioned routing" is unsupported outright.
- **The bootstrap resamples pseudo-replicates i.i.d.**, so CI widths are ~4.5×
  too narrow; under a task-cluster bootstrap the one significant result survives
  by 0.0017 with an effective n of 2 archetypes.
- **`load_grid_jsonl` discards the trainer seeds** (last-writer-wins on
  `(phi, task)`), destroying the per-seed variance `REVIEWER_CRITIQUE.md` MC1
  specifically asked to retain.
- **HVG selection runs on the full matrix including held-out cells** before any
  split, so "held-out" is compromised upstream of the metric.
- **Temperature is hardcoded 0.3 with no seed**, the cache making runs
  reproducible is not committed, and two clients disagree (0.3 vs 0.0).
- **Documented reproduction entry points do not exist** —
  `scripts/modal/app.py`, `paper/experiments/`, and six CSVs in `DESIGN.md §6.5`
  are all referenced and all absent.
- **Orphaned `paper/tables/tab1–tab5.tex` and `figures/fig1–fig5.pdf`** still
  contain retracted synthetic results (tab2: ρ = +0.918) with no surviving
  generator. Not `\input` into `paper.tex`, but present in the downloadable
  artifact.

## What this does to the recommended sequence

The ordering in the main review is superseded. **Nothing about the paper's
claims can be settled until the artifacts are regenerated from one run**, because
A1/A2/A6 mean the current artifact set does not describe a single experiment:

1. **A6, then A1** — fix the salted-hash strata; regenerate trainer + lifecycle
   from one process and assert the task sets are identical. Until this holds,
   every joined statistic is meaningless.
2. **A2** — thread the seed, or report n = 36 and delete the seed column.
3. **A4** — raise on a missing target instead of substituting a random gene; fix
   the doublet delimiter. `GATE_NORMAN = PASS` is not currently interpretable.
4. **A3** — add `source: Literal["llm","fallback"]` to `LifecycleStep`; refuse to
   compute entropy over fallback rows. §4.2 needs retraction either way.
5. **A5, A7** — derive the backbone one-hot from the actual config space and add
   the distinct-embedding test; pin the four dataset digests and fail closed.
6. Only then R1 (compute the correlations or retract the oracle claim), R4/R5
   (dispersion, nested split), and **last** R7 (the language pass).

**Honest summary for the principal:** this is not a paper that needs a language
pass and a few CIs. Three of its four empirical claims currently rest on code
defects, and the dataset gate that passes does so partly on tasks whose
perturbation target was a randomly chosen gene.

---

# Addendum 2 — the Adamson median is contaminated too (2026-09-24)

The main review and Addendum 1 left **one** headline MSD number with a confirmed defect
(Norman's, via random target genes on `_`-delimited combos). **That is now both of them.**

## A2-1 — `_normalise_pert_label` merged four different constructs into the `ATF6` task

`src/perturb_eval/experiments/e2_adamson.py` normalises a perturbation label as
`raw.split('_')[0]`. The raw 10X005 labels encode *combination constructs*, so:

| normalised | raw labels merged into it |
|---|---|
| **`ATF6`** | `ATF6_only_pMJ145`, `ATF6_IRE1_pMJ152`, `ATF6_PERK_pMJ150`, `ATF6_PERK_IRE1_pMJ158` |
| `PERK` | `PERK_only_pMJ146`, `PERK_IRE1_pMJ154` |
| `3x` | `3x_neg_ctrl_pMJ144-1`, `3x_neg_ctrl_pMJ144-2` |

One single-gene construct, two doubles and a triple became **one task**.

**`ATF6` is in the v0.5.0 trainer task list.** So the reported **Adamson median
best-config MSD of 0.147**, and the `PASS` verdict on its pre-registered `< 0.20` gate, were
computed with a task whose cell population is a mixture of four distinct perturbations.

This is the first label defect found today with confirmed exposure **in a held-out task**.

> **CORRECTED 2026-09-24, hours after writing, and the error was mine to propagate.** This
> paragraph originally read "the other nine were unexposed by sampling luck rather than by
> design." **That is wrong for five of the nine.** The agent gave me that framing, I wrote it
> here and passed it to the principal, and neither of us had checked the right thing: the claim
> was verified only against the **held-out task lists**.
>
> Re-checked against the pre-fix code at `228d354` for **training** exposure, it splits by
> dataset:
>
> - **Adamson** (`PERK`, `IRE1`, `3x`, `Gal4-4(mod)`, plus a `nan` label on 2,919 unannotated
>   cells found in the full inventory): `load_adamson_combined` skipped labels absent from the
>   shared gene vocabulary (`e2_adamson.py:103-111`), and `LinearBackbone.fit` skips labels
>   absent from `target_gene_idx` (`linear.py:48`). Their cells trained no model. Exposure is
>   the all-cells HVG ranking only. **"Unexposed" holds.**
> - **Norman** (`C3orf72`, `C3orf72_FOXL2`, `KIAA1804`, `C19orf26`, `TGFBR2_C19orf26`): the
>   per-file loader gave each a **random target index**, which put them *into*
>   `target_gene_idx` — so they entered the **training set** of every Norman task that did not
>   hold them out, carrying a random on-target feature. **"Unexposed" is wrong.** It adds five
>   labels to A4's training-side exposure. It does not change *which* published numbers are
>   affected, since `median_msd_norman` and `GATE_NORMAN` were already uninterpretable under A4.
>
> **The lesson is a checking discipline, and it is why this correction is worth more than the
> fact it corrects:** *"not a held-out task"* and *"not an input"* are different claims. An
> impact assessment that checks only the task list answers the wrong question, and answers it
> reassuringly. Any future "did this reach the published numbers?" must check **both** the
> held-out lists **and** the training inputs.

> **CORRECTED A SECOND TIME, same day — and the `nan` half above is RETRACTED ENTIRELY. See
> §A2-5.** The `nan` account in this block traced every stage *downstream* of label decoding and
> never checked the decode itself. The pre-fix loader did not use anndata, so the `nan` label
> reasoned about never existed on the path that ran. The real mechanism is worse and it reached
> the published numbers. Two corrections to one passage: the first fixed *which* labels were
> exposed, the second finds that the exposure question had been asked of the wrong code path.

### Why nothing caught it, which is the transferable part

`ATF6` **is** a valid gene symbol. The fail-closed target resolver built to catch the nine
unresolvable labels is structurally incapable of catching this one, because the label resolves
correctly and simply *means something else*. **A validator that checks whether a name is
well-formed cannot detect a name that is well-formed and wrong.** Same family as every other
finding in this review: the check observes a property adjacent to the one that matters.

Benign by contrast, but currently implicit and now to be recorded: several plasmids for the
*same* gene already pool into one task (`XBP1` ×2, `CCND3` ×2, `ATF4` ×3, …). That is standard
gene-level pooling; it just was not stated.

## A2-2 — consequences for the reported numbers

- **Adamson `0.147` and its gate: contaminated.** Not merely uninterpretable — computed on a
  known mixture.
- **The Adamson task count will change.** `PERK`, `IRE1` and the four combination constructs
  leave the eligible pool; `3x` is reclassified as a negative control (its raw label is
  `3x_neg_ctrl`). The design is 3 quantile bins × 7 TFs = 21, and whether 21 remains fillable
  is now an open question I have asked to be escalated rather than quietly satisfied with a
  short bin.
- **Excluding `PERK`/`IRE1` loses no genes** — 10X010 carries proper `EIF2AK3` and `ERN1`
  labels, so those genes remain reachable under their current symbols.

## A2-3 — a paper-prose defect the models are immune to

**Norman 2019 is a CRISPR *activation* screen**, so an on-target effect is a **rise**, not a
knockdown. The backbones name that feature a `dip` internally. The models are unaffected
because the feature is the signed logfc — but any prose describing an on-target *knockdown*
is wrong for Norman, and the internal naming teaches the wrong direction to every future
reader. Registered as a manuscript row.

Corroborating evidence from the same pass, which also validated the Norman stable-ID join:
`CBARP` at **+0.301, rank 33,690 of 33,694** — the fourth most up-regulated gene — exactly
the direction an activation screen predicts.

## A2-4 — what this does to the review's verdict

It does not change it; it removes the last reason to soften it. Both pre-registered MSD gates
that the paper reports as `PASS` now rest on defective task definitions — Norman's on
randomised targets, Adamson's on a pooled mixture. Combined with the `n/a` correlation table
(R1) and the confounded entropy result (R2), **no headline empirical claim in v0.5.0 currently
survives**, and the regeneration is not an improvement exercise but a prerequisite.

---

## A2-5 — unannotated cells were silently relabelled as a real perturbation (`cats[-1]`)

**This supersedes every earlier statement in this review about the `nan` label.** The eighth
silent-substitution instance, and the second with confirmed exposure to published numbers.

`e2_adamson.load_adamson_matrix` (`:149-152` @ `228d354`) decoded the raw h5py categorical as:

```python
labels_raw = [cats[c] for c in codes]
```

A missing annotation is code **`-1`**. In Python, `cats[-1]` is the **last category**. So every
unannotated cell was relabelled as whatever perturbation happens to sort last — silently, with
no error, and in a way no downstream validator could detect, because the resulting label is a
real gene symbol.

| file | unannotated cells | relabelled as | real cells for that label |
|---|---|---|---|
| pilot | 10 | `ZNF326` | 557 → 567 |
| 10X005 | 296 | `YIPF5` | 1 → 297 |
| 10X010 | 2,613 | `YIPF5` | 574 → 3,187 |
| Norman | 0 missing codes | — | unaffected |

After the 200-cells-per-label cap, **v0.5.0's combined `YIPF5` task was ~91% unannotated cells**
(~363 of 400). `ZNF326` ~1.8%.

### Exposure — both halves

- **Held-out:** `YIPF5` and `ZNF326` are held-out tasks in v0.5.0's `lifecycle_runs.jsonl`.
  **`YIPF5`'s lifecycle MSD was measured on a mostly-unannotated population.**
- **Training inputs:** both are real symbols, so both sat in `target_gene_idx` and trained every
  Adamson task that did not hold them out — the 21 trainer tasks included. `YIPF5`'s
  "perturbation mean" was mostly unannotated cells.
- **Affected published numbers:** the **Adamson median 0.147 and `GATE_ADAMSON`** — via training
  inputs, a **second route entirely independent of A2-1's `ATF6` pooling** — and any lifecycle
  result including `YIPF5` or `ZNF326`.

### Why this one is the hardest to have caught

A sentinel of `-1` meeting Python's negative indexing produces a *valid* value, not an error.
Every guard in this codebase — the fail-closed resolver, the vocabulary check, `_is_control` —
operates on the label *after* decoding, and the label it receives is a real gene symbol. The
defect is upstream of every check, and it is invisible to all of them by construction.

**Norman had zero missing codes, so the same pattern (if present) would not have fired there.**
That is luck, not correctness, and it is an open question for the register: *where else does this
codebase index a raw categorical with an integer that could be `-1`?*

---

## A2-6 — half the metric family is *structurally undefined* for the system that was measured

This reframes **R1**. The empty correlation table was not only an omission — **two of TDI's four
components cannot be computed for the agentic lifecycle at all.**

The paper's Problem Setup requires both a critique matrix and a winner:

- `paper.tex:182-183` — "every other agent emits a critique with severity $S_{ij}(r)$ … A winner
  index $w(r)$ is assigned by the orchestrator"
- `:221` — $\mathrm{CSD}(r) = \mathrm{Var}(\mathbf{S}(r))$ — requires the critique matrix
- `:233` — $\mathrm{WFR} = \frac{1}{R-1}\sum \mathbb{1}[w(r) \neq w(r-1)]$ — requires the winner

Verified: `critique_matrix` and `winner_index` appear in `src/perturb_eval/metrics.py`,
`instrumentation.py` and `types.py` — the **consensus-round** framework, which
`instrumentation.py` projects from a CellForge-style `ConsensusResult`. They appear **nowhere in
`src/perturb_eval/agentic_lifecycle/`**.

The agentic lifecycle is a **role pipeline** — DataCurator → Literature → Architect → Trainer →
Validator. It has no propose-critique-vote round, so there is no $N\times(N-1)$ critique matrix
and no winner to flip. Its Validator emits a single `StructuredCritique` to the pipeline, which
is not the object CSD is the variance of.

**So the metric family is well-defined for the architecture the paper describes, and undefined
for the system the paper measured.** TDI as published — $\alpha\,\mathrm{ACE} + \beta\,\mathrm{CSD}
+ \gamma(1-\Delta C) + \delta\,\mathrm{WFR}$ — was never computable on its own testbed.

### Consequences

- **R1 is deeper than reported.** "The correlations were never computed" is true; "two of them
  could not have been" is the reason. `tdi_vs_held_out_msd` being dead code is a symptom.
- **The revision must not silently redefine TDI.** A two-component index over ACE and $1-\Delta C$
  is a *different quantity* from the published four-component TDI. It is correctly being named
  `TDI_lifecycle`, and the paper must state plainly that **the four-component TDI is not
  evaluated** — not merely that two components are unavailable. Otherwise a reader compares
  numbers across versions that are not the same metric.
- **It does not sink the paper.** The title question — does agent confidence entropy predict task
  difficulty? — turns on ACE and $\Delta C$, both of which the lifecycle does produce. The
  honest framing is a narrower instrument fully specified, rather than a wide one half-inapplicable.
- **A referee would find this in one pass**, by reading §3's definitions against the
  implementation. Declaring it up front converts the worst kind of finding into a stated scope
  limit.
