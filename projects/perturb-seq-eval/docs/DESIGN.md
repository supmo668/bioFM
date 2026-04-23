# Design Document — Observability, Abstractions, Reproducibility

Companion to [`THESIS.md`](THESIS.md) and
[`paper/paper.tex`](../paper/paper.tex). Where the thesis argues the
*scientific* claim and the paper presents the *experimental* evaluation, this
document records the *engineering* design: precisely what was contributed,
what was adapted, how the abstractions compose, and how every experimental
result can be reproduced.

We aim to be unambiguous about the boundary between
**novel contribution**, **thin adapter over existing infrastructure**, and
**future work**.

## 1. Contribution audit

We distinguish three categories. Every file in this project falls into exactly
one.

### 1.1 Novel contribution (authored here, not previously available)

| File | Kind | What it contributes |
|---|---|---|
| [`src/perturb_eval/types.py`](../src/perturb_eval/types.py) | Abstraction | Trace schema: immutable `RoundTrace`, `RunTrace`, `RoundMetrics`, `RunMetrics`, `Config`. Defines the *interface* between orchestrator and evaluator. |
| [`src/perturb_eval/metrics.py`](../src/perturb_eval/metrics.py) | Metrics | `ACE`, `CSD`, `ΔACE`, `ΔC`, `WFR`, composite `TDI`. Novel as a bundle applied to multi-agent propose-critique-vote traces. |
| [`src/perturb_eval/probe.py`](../src/perturb_eval/probe.py) | Procedure | Preflight probe protocol + 4-d `ProbeSignature`. |
| [`src/perturb_eval/bayesian.py`](../src/perturb_eval/bayesian.py) | Model | Gaussian-diagonal-covariance MAP recommender over configuration space $\Phi$ with FLOPs-budget constraint. |
| [`src/perturb_eval/calibration.py`](../src/perturb_eval/calibration.py) | Procedure | Ridge-fit of TDI coefficients from logged traces; non-negativity-constrained, unit-sum normalised. |
| [`paper/experiments/simulate.py`](../paper/experiments/simulate.py) | Experiment | Deterministic synthetic DGP + seven experiments end-to-end. |
| [`paper/paper.tex`](../paper/paper.tex) + [`paper/references.bib`](../paper/references.bib) | Paper | Peer-review-ready manuscript, 10 pp, with real numbers from `simulate.py`. |

### 1.2 Thin adapter layer (translates between our schema and existing systems)

| File | Adapts | What it does |
|---|---|---|
| [`src/perturb_eval/instrumentation.py`](../src/perturb_eval/instrumentation.py) | CellForge-style `ConsensusResult` (as implemented by [`projects/cellforge-agents/`](../../cellforge-agents/)) | Duck-typed translator: takes any object with `.rounds[*].proposals` and `.rounds[*].critiques` and emits a `RunTrace`. No patching of the orchestrator. |
| [`src/perturb_eval/massgen_adapter.py`](../src/perturb_eval/massgen_adapter.py) | MassGen skill manifest shape | JSON-in / JSON-out entrypoints (`preflight_skill`, `evaluate_skill`) ready to register in a MassGen skill. |
| [`src/perturb_eval/model.py`](../src/perturb_eval/model.py) | scGPT public release | `PerturbationPredictor` protocol plus `MockPredictor` (CPU) and `ScGPTPredictor` (lazy-loaded). The latter is a thin wrapper over the existing release. |
| [`src/perturb_eval/data.py`](../src/perturb_eval/data.py) | Perturb-seq public datasets | Protocol + `SyntheticPerturbSeq` stub + placeholders for Norman/Adamson loaders. |

### 1.3 Not yet built (explicit future work)

1. **Upstream MassGen PR.** We draft a skill manifest (§4) but have not
   submitted or installed one upstream. MassGen's skill system discovers
   skills under `massgen/skills/<name>/` or via OpenSpec proposals; a real PR
   would add our skill there and update `massgen/configs/skills/` YAML.
2. **LLM-based extractor for MassGen's native trace.** MassGen's
   `CoordinationTracker` emits `AgentAnswer` (text content) and `AgentVote`
   (voter, target, reason) records — no numeric `confidence` or
   `severity`. Projecting these onto our numeric schema requires an
   LLM-based extractor (MassGen's anti-pattern docs explicitly forbid
   keyword/regex heuristics for this kind of projection).
3. **Empirical validation on a real perturb-seq dataset.** All results in the
   paper are synthetic. We outline the path on Norman/Adamson/Replogle
   perturb-seq data with scGPT in [`THESIS.md §6`](THESIS.md).

## 2. The abstraction: trace schema as contract

Our central engineering claim is a **narrow, decoupled contract** between
orchestrator and evaluator:

```
orchestrator produces a stream of:   (round_index, proposals[N], critiques[N(N-1)])
evaluator consumes:                  RunTrace    → RunMetrics | ProbeSignature | Recommendation
```

The trace schema is fully specified in
[`src/perturb_eval/types.py`](../src/perturb_eval/types.py):

- `RoundTrace` — `(round_index, agent_names, confidences[N], critique_severities[N][N-1], winner_index, consensus_score, compute_tokens)`
- `RunTrace` — `(task_id, rounds[R], converged, backbone)`
- All fields `frozen=True` — safe to serialise, hash, and pass across
  processes without defensive copying.

**Why this matters.** If every propose-critique-vote orchestrator emits a
`RunTrace`, one evaluation stack serves them all — you do not reimplement ACE
for CellForge, MassGen, Archon, and AutoGen separately. This is the
observability abstraction we contribute. The schema deliberately omits the
LLM-facing content of proposals and critiques: metrics operate on the
numerics alone, which makes them cheap (≤ 1 ms per run) and
privacy-friendly.

### 2.1 What a CellForge orchestrator already provides

The [`cellforge-agents`](../../cellforge-agents/) project emits
`ConsensusResult` with `.rounds[i].proposals` (each with `.agent`,
`.confidence`, `.content`) and `.rounds[i].critiques` (each with
`.from_agent`, `.on_agent`, `.severity`). The translator in
[`instrumentation.py`](../src/perturb_eval/instrumentation.py) is **40
lines** of pure projection — no patching, no subclassing. It is duck-typed,
so any orchestrator whose public surface matches this minimal shape gets
full evaluator support for free.

### 2.2 What MassGen provides natively

MassGen provides a rich but structurally different observability surface:

| MassGen component | Purpose | Relation to our schema |
|---|---|---|
| `massgen/coordination_tracker.py` — `CoordinationTracker`, `CoordinationEvent`, `AgentAnswer`, `AgentVote` | Event-based coordination record (voter IDs, reasons, timestamps) | *Source* for RunTrace fields — but needs projection (§3) |
| `massgen/execution_trace.py` — `TraceEntry`, `EntryType`{ROUND_START, TOOL_CALL, VOTE, …} | Markdown-style trace for agent context recovery | Too verbose for our purposes; we only need a projection |
| `massgen/skills/*` — skill modules | User-installable capabilities | The delivery vehicle for our eval layer (§4) |

MassGen's `AgentAnswer` has no `confidence` field; `AgentVote` has no
`severity`. The voting mechanism is categorical (`voter_id` chooses
`voted_for`) rather than scored. Porting our metrics upstream therefore
requires an **extractor** that materialises `confidence` and `severity`
from the native voting and answer records.

## 3. Bridging MassGen → our schema

### 3.1 Confidence projection from votes

Let $V_{ij}$ indicate voter $i$ voted for agent $j$ in the round's voting
phase. Then a simple *vote-share* projection of per-agent confidence is
$\hat{c}_j = \frac{\sum_{i\neq j} V_{ij}}{N-1}$. This is categorical
confidence (fraction of peers who endorse agent $j$); it is noisy but
principled and requires no LLM call.

### 3.2 Severity projection from vote reasons

MassGen's `AgentVote.reason` is free text. A regex mapping from phrases like
"concerned about X" to severity scores is forbidden by MassGen's own
anti-patterns (`CLAUDE.md § Anti-Patterns`: *"no keyword/heuristic matching
for categorization or similarity"*). A principled projection uses a small
LLM-based severity rater:

```
Input:  AgentVote.reason string, scoring rubric
Output: severity ∈ [0, 1]
```

This is cheap (≤ 50 tokens per vote) and can be batched per round. The
extractor is the primary missing piece for a native MassGen integration; its
specification is section §4.3.

### 3.3 Two-mode deployment

In practice, the projected confidence and severity can come from either:
1. **Native mode** — if an orchestrator already exposes numeric fields, use
   them directly (CellForge-style).
2. **Projected mode** — if only categorical answers/votes are available
   (MassGen-style), run the extractor once per round.

Both modes yield a `RunTrace`; everything downstream is mode-agnostic.

## 4. A MassGen-installable skill (draft)

We have not submitted this to MassGen upstream. The draft below is what a
real PR would contain.

### 4.1 Skill layout

```
massgen/skills/perturb-seq-eval/
├── SKILL.md                  # agent-facing description + invocation contract
├── skill.yaml                # MassGen skill manifest
├── prompts/
│   └── severity_rater.md     # LLM prompt for §3.2
├── extractors/
│   ├── __init__.py
│   ├── confidence.py         # vote-share projection (no LLM)
│   └── severity.py           # LLM-based severity extractor
└── handlers/
    ├── preflight.py          # wraps preflight_skill()
    └── evaluate.py           # wraps evaluate_skill()
```

A draft of all of the above is committed at
[`projects/perturb-seq-eval/massgen_skill_draft/`](../massgen_skill_draft/)
so reviewers can see the shape without us touching the
[`tools/MassGen/`](../../../tools/MassGen/) submodule (which is pinned to
upstream).

### 4.2 skill.yaml contract

```yaml
name: perturb-seq-eval
description: >
  Observability + Bayesian agentic hyperparameter tuning for
  propose-critique-vote orchestrators. Consumes a coordination-tracker
  snapshot and emits (ACE, CSD, ΔACE, ΔC, WFR, TDI) + a configuration
  recommendation for follow-up runs.
inputs:
  - coordination_snapshot: path to a JSON dump of CoordinationTracker events
  - budget_flops_proxy: optional int
outputs:
  - run_metrics.json
  - recommendation.json
extensions:
  on_session_end: "handlers.evaluate:run"
  on_session_start: "handlers.preflight:run"
```

### 4.3 Severity-rater prompt

```
SYSTEM:
You are a terse rater. Read ONE AgentVote.reason string. Rate its severity
toward the voted-against alternative on a 0.0–1.0 scale, where:
  0.0  — complete agreement with the voted-for answer; no critique of others.
  0.5  — ambivalent; the reason expresses minor reservations.
  1.0  — strong rejection of at least one alternative.
Return a single floating-point number in [0,1], nothing else.

USER:
Voter: {voter_id}
Voted for: {voted_for}
Reason: {reason_text}
Available alternatives: {answer_labels}
```

Prompts like this are in scope for a MassGen PR because MassGen's
anti-patterns prohibit *keyword-based categorisation* but explicitly endorse
*LLM-based approaches*.

## 5. The MassGen CoordinationTracker → RunTrace algorithm

For completeness, here is the procedure the extractor performs, expressed in
prose so implementors can port it independently.

```
Input:   CoordinationTracker session (events, agents)
Output:  RunTrace

1. Group events by iteration_start/iteration_end. Each group becomes a
   RoundTrace with round_index = iteration number.
2. For each round:
   a. Collect all AgentAnswer events → agent_names is the ordered list of
      agent_ids that submitted an answer this round.
   b. Collect all AgentVote events in this round.
   c. For each agent j, set ĉ_j = (#votes targeting j) / (N−1).
   d. For each (voter i, target j) with i ≠ j, call the severity rater on
      the vote.reason to produce S_ij ∈ [0,1]. If agent i did not vote
      against j, set S_ij = 0.
   e. winner_index = argmax_j (ĉ_j − mean_i S_ij).
   f. consensus_score = max_j (ĉ_j − mean_i S_ij).
3. Emit RunTrace(task_id=session_id, rounds=..., converged=session_end.converged,
   backbone=session.metadata.get('backbone', 'unknown')).
```

Complexity: for $N=5, R=3$ rounds and 4 votes per round, the extractor makes
at most 12 LLM calls per session — trivially batch-able.

## 6. Reproducibility: step-by-step

Every number and figure in
[`paper/paper.tex`](../paper/paper.tex) is reproduced by the pipeline below.
Total runtime: about 10 s on a single CPU, no network.

### 6.1 Requirements

- Python ≥ 3.10 with `numpy`, `matplotlib`, `typer`.
- A TeX distribution with `pdflatex`, `bibtex`, packages
  `hyperref`, `natbib`, `booktabs`, `caption`, `subcaption`, `enumitem`,
  `xcolor`, `microtype`, `geometry`, `lmodern`.
- No `scipy`, no `scikit-learn`, no `pandas`, no network, no GPU.

### 6.2 Seeded determinism

All randomness flows through a single `numpy.random.Generator`
instantiated as `np.random.default_rng(2026)` inside
[`simulate.py`](../paper/experiments/simulate.py::main). Re-running the
script with the same seed reproduces the CSV byte-for-byte. We report this
seed in the paper's Reproducibility paragraph.

### 6.3 Full pipeline

```bash
cd projects/perturb-seq-eval

# (1) Install
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e .

# (2) Run unit tests (43 tests, ≤ 0.1 s)
pytest -q

# (3) Run the simulation — emits 6 CSV files into paper/experiments/out/
python3 paper/experiments/simulate.py

# (4) Render figures (5 figures as PDF + PNG)
python3 paper/experiments/plot.py

# (5) Generate LaTeX tables (5 tex fragments)
python3 paper/experiments/generate_tables.py

# (6) Compile the paper — three passes + bibtex
cd paper
pdflatex -interaction=nonstopmode paper.tex
bibtex paper
pdflatex -interaction=nonstopmode paper.tex
pdflatex -interaction=nonstopmode paper.tex

# Output: paper/paper.pdf (10 pages, 0 undefined references)
```

### 6.4 Artifact dependency graph

```
src/perturb_eval/
      │
      ▼
paper/experiments/simulate.py  ─►  paper/experiments/out/*.csv
                                             │
                      ┌──────────────────────┴──────────────────────┐
                      ▼                                             ▼
paper/experiments/plot.py                       paper/experiments/generate_tables.py
                      │                                             │
                      ▼                                             ▼
paper/figures/*.{pdf,png}                             paper/tables/*.tex
                      │                                             │
                      └──────────────────►  paper/paper.tex  ◄──────┘
                                             │
                                             ▼
                                        paper/paper.pdf
```

### 6.5 Which numbers come from which CSV

The paper refers to specific numbers; here is the origin of each.

| Paper claim | CSV column | Value |
|---|---|---|
| Abstract: TDI Spearman $\rho = +0.918$ | `e1b_tdi_calibration.csv::calibrated_spearman_test` | `+0.918` |
| Abstract: default TDI $\rho = +0.524$ | `e1b_tdi_calibration.csv::default_spearman_test` | `+0.524` |
| Abstract: $1-\Delta C$ univariate $\rho = +0.916$ | `e5_tdi_ablation.csv::spearman` where `feature=lack_of_convergence` | `+0.916` |
| Abstract: probe → $d$ Spearman $\rho = +0.360$ | `e2b_probe_to_difficulty.csv::probe_to_d_spearman_test` | `+0.360` |
| §7.4: AUROC $N{=}2 \to 10$ easy tier | `e4_agent_scaling.csv` filter `tier=easy` | $0.658 \to 0.866$ |

### 6.6 Immutable artefacts

Every tuple of run-time assumptions is frozen in the artefacts:

- DGP parameters — `DGP` dict at the top of `simulate.py`.
- Config space $\Phi$ — `DGP["config_space"]` in `simulate.py`.
- TDI default coefficients — `DEFAULT_TDI_COEFFS` in
  [`metrics.py`](../src/perturb_eval/metrics.py).
- Bayesian prior scale $\kappa$ — `prior_scale=3.0` in
  [`bayesian.py::BayesianRecommender`](../src/perturb_eval/bayesian.py).
- Variance floor for the likelihood — `default_likelihood_var=0.05`.

Changing any of these and re-running the pipeline yields a clearly diffable
delta in the CSVs, figures, tables, and therefore the paper. This is
deliberate.

## 7. Validation checklist (what a reviewer might want to run)

The same pipeline answers five questions a skeptical reviewer typically asks.

1. **"Does it even run?"** — `pytest -q` → 43/43 green in ≤ 0.1 s.
2. **"Is the DGP honest?"** — read `DGP` dict in `simulate.py`; every
   assumption is one line.
3. **"Can I reproduce the plot numbers?"** — `simulate.py` → CSVs; the
   tables and figures are pure functions of those CSVs.
4. **"What happens if I change $\lambda$?"** — one line in
   `calibration.py::fit_tdi_coefficients(..., ridge_lambda=...)`; re-run
   `simulate.py`; delta appears in `tab2` and the `Default` vs `Calibrated`
   Spearman numbers.
5. **"What happens on a real MassGen run?"** — see §3 and §4. We report
   this is not yet empirically validated and specify the extractor that
   would close the gap.

## 8. What would falsify the thesis

For honesty, here are three concrete outcomes that would contradict the
paper's central claims. They are all runnable within the pipeline with the
named one-line changes.

1. **Removing $\gamma$ from TDI still matches default on real data.** If on
   a real MassGen trace the convergence signal $1-\Delta C$ is less
   informative than $\mathrm{CSD}$ or $\mathrm{WFR}$, the calibrated
   coefficients would redistribute and TDI's gain over default would shrink.
   The paper honestly reports that the current $\gamma$-dominance is partly
   a feature of the DGP (§9).
2. **Probe → $d$ regression does not generalise.** On a real trace set, if
   probe regression $R^2$ drops below $0.1$, the Bayesian recommender
   provides no adaptive benefit over a fixed prior — this is the probe-weakness
   limitation called out in the paper.
3. **Uniform allocation matches adaptive at all budgets.** If Figure 3's
   adaptive curve stays strictly below uniform across a wide budget range on
   real data, the paper's practical claim is falsified. The current
   synthetic Pareto already shows adaptive is *competitive* rather than
   strictly dominant; the honest direction is enriching the probe (§4.3).

Any of these results would be valuable to report — the framework is
constructed so they are easy to observe.

## 9. Summary of the observability contribution

If someone asked us "in one sentence, what did you add?", the answer is:

> A narrow, four-field trace schema that decouples multi-agent orchestrators
> from downstream evaluation, plus a calibrated metric and recommender stack
> that consumes that schema — and an explicitly-specified extractor for the
> MassGen-native case where numeric confidence and severity must be
> projected from categorical votes and free-text reasons.

Everything else in the project is either a thin adapter over existing
infrastructure or explicitly-scoped future work.
