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
