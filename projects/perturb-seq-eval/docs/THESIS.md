# Thesis — Agent Confidence Entropy as an Empirical Difficulty Oracle for Multi-Agent Group Generation, with a Bayesian Pre-Test for Agentic Hyperparameter Tuning on Perturb-Seq Experimental Design

Status: working draft (v0.1, 2026-04-18).
Target venue: workshop submission to ICML 2026 FM4LS and/or a MassGen contribution RFC.
Companion code: this directory (`projects/perturb-seq-eval/`) is the reference implementation; the orchestration layer under evaluation is `libs/cellforge-agents/`.

## 1. One-sentence claim

> **The per-round joint distribution of agent confidence and critique severity in a CellForge-style 5-agent team is a sufficient statistic for task difficulty, and a single cheap preflight round of that distribution yields a Bayesian recommender for the optimal team size, round count, and backbone choice — turning agentic orchestration into a tractable hyperparameter-tuning problem.**

Put differently: multi-agent group generation is already doing test-time compute scaling, but it spends the budget uniformly. If we read the agent dynamics themselves as a difficulty signal — the same way Snell et al. 2024 use a PRM to route single-chain TTC — we can spend compute adaptively and match full-team accuracy at a fraction of the FLOPs.

## 2. Why this matters

### 2.1 The immediate problem

CellForge (arXiv:2508.02276) and similar systems (MassGen, PlanGEN, Archon) deploy specialised agents in parallel to tackle a biology modelling problem — here, designing a perturb-seq experiment + predictor. The current default is "run every agent for every task, iterate until consensus or max-rounds." That's uniform spending. It wastes compute on easy tasks and under-spends on hard ones.

The single most impactful result from the TTC literature in 2024-25 — Snell et al. ("Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters", [2408.03314](https://arxiv.org/abs/2408.03314)) — showed that for single-chain LLM inference, a compute-optimal per-prompt allocation makes a small model match a 14× larger one at equal FLOPs. **The multi-agent analogue has not been worked out.** That's the gap.

### 2.2 The broader frame

This is the group-generation version of the question Snell asked. His levers were (a) parallel best-of-N with a PRM and (b) sequential revision with a revision model, and his trick was to *condition the lever choice on prompt difficulty*. In a 5-agent group, the levers are (a) number of agents, (b) number of refinement rounds, (c) which backbone each agent uses, (d) whether to admit outside tool-call budget. The analogue of his PRM is the group's own confidence-and-critique signal. The analogue of prompt difficulty is task difficulty.

## 3. The setup: perturb-seq experimental design as the reasoning task

### 3.1 Why perturb-seq

Perturb-seq (single-cell CRISPR screens with transcriptomic readout) is the cleanest test-bed we have for agentic scientific reasoning:

1. It spans **data curation** (which donor, which filters), **prior** (which pathway, which expected DEGs), **architecture** (which BioFM backbone, which perturbation head), **training** (CV split by donor, batch-correction strategy), and **validation** (pathway enrichment, held-out perturbation transfer). That is, it exercises all five CellForge agents at once.
2. **Ground-truth hardness is measurable.** A perturbation's intrinsic difficulty can be proxied by: literature density (how many PubMed hits for this target gene × cell line), DEG overlap between independent wet-lab replicates, signal-to-noise in baseline scRNA-seq, and whether it's a single vs. combinatorial perturbation. This gives us a reliable difficulty label for calibration.
3. **Pre-trained backbones exist and are small enough to GPU-load.** scGPT (33M-cell pretrain, ≈50M params) and its LoRA adapters fit comfortably on a single consumer GPU; scFoundation/scPRINT/UCE offer lightweight alternatives. See §6 for the specific configuration.

### 3.2 The 5 CellForge agents (our standing setup)

Identical to `libs/cellforge-agents/`: **DataCurator · Literature · Architect · Trainer · Validator**, coordinated via a MassGen-style propose→critique→vote loop. The orchestrator emits a per-round trace (proposals[5], confidences[5], critiques[5×4]) that is the raw material for every metric below.

## 4. The metrics (the core contribution)

At round `r`, the orchestrator produces:
- `c(r) ∈ [0,1]^5` — confidences, one per agent.
- `S(r) ∈ [0,1]^{5×4}` — critique severities (row `i` = severities of critiques from agent `i` on the other four; diagonal is excluded).
- `w(r) ∈ {1..5}` — identity of the current winner (argmax consensus-score).

From these five quantities per round we derive:

### M1 — Agent Confidence Entropy (ACE)

For the softmax-normalized confidence distribution `p(r)_i = softmax(c(r)/τ)_i` with temperature τ (default 1):

```
ACE(r) = -Σᵢ p(r)ᵢ · log p(r)ᵢ
ACE_norm(r) = ACE(r) / log(N)           # N = number of agents; bounds [0,1]
```

Interpretation:
- `ACE_norm → 0`  ⇒ one agent dominates → crisp hierarchy → *easy* task (trust winner).
- `ACE_norm → 1`  ⇒ flat distribution → paired with `mean(c)`:
  - high mean ⇒ "confident consensus" (still easy — team collectively knows it).
  - low mean  ⇒ "uniform uncertainty" (hard — likely out-of-distribution).

### M2 — Critique Severity Dispersion (CSD)

```
CSD(r) = Var(S(r))                       # variance over all valid off-diagonal entries
CSD_row(r, i) = Var(S(r)[i, :])          # how inconsistent is critic i?
CSD_col(r, j) = Var(S(r)[:, j])          # how contested is proposal j?
```

Interpretation: CSD concentrates disagreement — a large single critic-proposal disagreement dwarfs many small ones, which matches the intuition that "one agent flagging a real bug" is worth more signal than "everyone mildly disagreeing".

### M3 — Round-over-round Convergence (ΔACE, ΔC, WFR, CST)

```
ΔACE(r) = ACE(r) - ACE(r-1)              # negative = converging
ΔC(r)   = mean(c(r)) - mean(c(r-1))      # positive = team growing confident
WFR(R)  = (1/(R-1)) Σ_{r=2..R} 𝟙[w(r) ≠ w(r-1)]     # winner-flip rate
CST(r)  = consensus_score(r)             # the existing orchestrator output
```

A well-posed run has `ΔACE < 0`, `ΔC > 0`, `WFR ≈ 0`, `CST` monotonically rising. Deviations from this pattern are the difficulty signal.

### M4 — Task Difficulty Index (TDI)

A single scalar summary, linearly combining the above (coefficients calibrated in §5):

```
TDI = α·ACE_norm(R)                      # residual entropy at end-of-run
    + β·CSD(R)                           # residual disagreement
    + γ·(1 − normalize(ΔC(R)))           # lack of convergence
    + δ·WFR(R)                           # instability
```

TDI is our **empirical difficulty oracle**. Thesis Claim 1: TDI computed post-hoc on a run strongly rank-correlates with a held-out, biology-based difficulty label (perturbation literature density; wet-lab DEG reproducibility; donor-split AUROC drop).

## 5. The preflight probe + Bayesian recommender (the practical contribution)

TDI is useful diagnostically, but by the time you've computed it the compute has been spent. The interesting question is: **can we estimate TDI — or, equivalently, the optimal `(n_agents, n_rounds, backbone)` configuration — from a much cheaper preflight?**

### 5.1 The preflight probe

Run exactly **one round** of the team with agents in a shallow configuration (smaller context window, no tool calls beyond the cheapest one per agent, cap at k=3 literature hits rather than k=20). Extract:

```
probe signature x = (ACE_norm(0), mean(c(0)), CSD(0), max(c(0)))  ∈ ℝ⁴
```

The probe is ≤ ~10% of the cost of a full run. It captures the first-look shape of group disagreement on the task.

### 5.2 The Bayesian recommender

Model task configuration as a random variable φ = (n_agents, n_rounds, backbone) ∈ Φ, and ground-truth-required configuration as φ* (the smallest configuration that reaches the accuracy plateau on that task).

We want the posterior:

```
P(φ* = φ | x) ∝ P(x | φ*) · P(φ*)
```

Calibrated on a labelled set of (task, probe_x, observed_φ*) tuples. Under a Gaussian likelihood for `x | φ*` and a structured prior on `φ*` (small configurations more likely), the posterior is closed-form and cheap to query.

For each new task we compute `x`, then pick:

```
φ̂(x) = argmax_φ  E_{φ* | x} [ accuracy(φ) ]  s.t.  FLOPs(φ) ≤ B
```

This is the **agentic hyperparameter tuning** move: the analogue of Snell's prompt-conditional compute-optimal allocation, applied to orchestration hyperparameters.

### 5.3 Why this is tractable

The configuration space Φ is small (say 3 choices of n_agents × 3 of n_rounds × 3 backbones = 27 configurations). The probe signature is 4-dim. A hundred calibration tasks is enough to fit the likelihood. This is a classic small-n Bayesian regression setting, and the uncertainty on φ̂ is meaningful and reportable.

## 6. Experimental design

### 6.1 Dataset

Default: **Norman 2019 (GSE133344)** — genome-scale perturb-seq on K562, ~100k cells, ~200 dual- and single-gene perturbations. Accessible via `scanpy.datasets` indirectly, or via the scGPT preprocessed fork.

Lightweight variant (for laptop-scale iteration): **Adamson 2016 (GSE90546)** — UPR perturb-seq, ~25k cells, 87 perturbations. Small enough to run end-to-end in an hour on a single GPU.

Stub variant (framework tests only): a synthetic AnnData with 500 cells × 50 genes and 5 perturbations generated by `scripts/make_synthetic.py` — this is what CI uses.

### 6.2 Backbone: scGPT

We use **scGPT_whole_human** (≈50M params) as the default backbone, frozen, with a thin LoRA adapter (~100k params) on the perturbation head. Fits on a single 16 GB GPU; batches of 64 cells fit on 8 GB. The `ScGPTPredictor` in `src/perturb_eval/model.py` wraps the HuggingFace release and exposes a `predict_response(perturbation, context) -> anndata` method that agents' `Validator` can call.

Alternative small backbones: **scFoundation-small** (30M params, denoising) or **scPRINT-50M** (contrastive); the `PerturbationPredictor` protocol in `model.py` lets you swap without touching the orchestrator.

### 6.3 Task classes in the calibration set

We run the 5-agent team on ~100 perturbations labelled by three difficulty tiers:

| Tier | Example | Expected configuration |
|---|---|---|
| Easy | Well-studied single gene KO (TP53, CTNNB1) in a cell line with abundant literature. | 3 agents × 1 round; any backbone |
| Medium | Cytokine stim (LPS, IL-6) with medium literature coverage. | 5 agents × 2 rounds; scGPT |
| Hard | Combinatorial dual-KO with sparse literature. | 5 agents × 3 rounds; scGPT with extra tool budget, or escalate to scFoundation |

The "expected configuration" is determined empirically by finding the smallest (n_agents, n_rounds) that reaches ≥ 95% of the full-team downstream validation AUROC on held-out donors.

### 6.4 Evaluation

Two headline numbers:

1. **Intrinsic** — Spearman rank correlation between post-hoc TDI and the biology-based difficulty label across the 100-task calibration set. Target: ρ ≥ 0.6.
2. **Extrinsic** — accuracy-per-FLOPs of the **preflight-routed** configuration vs. the **uniform-full-team** baseline, at matched compute budgets. Target: the preflight-routed policy should reach ≥ 95% of the full-team downstream AUROC at ≤ 50% of the compute.

Secondary diagnostics:
- ACE, CSD, ΔC, WFR trajectories per task, clustered by tier.
- Probe-to-TDI correlation — how much of post-hoc TDI is already captured by the round-0 probe signature.
- Failure mode analysis — when does the probe underestimate difficulty? (Hypothesis: on tasks where the literature agent is spuriously confident because a near-synonym search term matches.)

## 7. Protocol

1. Instrument the CellForge orchestrator to emit `RoundTrace` records (see `instrumentation.py`).
2. Build the 100-task calibration set (gene list + difficulty-tier labels).
3. For each calibration task, run the orchestrator at each point in Φ (27 configs), log all metrics + final downstream AUROC.
4. Fit the Bayesian likelihood P(probe_x | φ*).
5. Fit the TDI coefficients (α, β, γ, δ) via ridge regression against the difficulty-tier labels.
6. On a held-out set of 20 tasks, apply the preflight-routed policy and compare accuracy-per-FLOPs vs. uniform.
7. Report both headline numbers + 95% CIs.

## 8. Risks and limitations

1. **Confound: overconfident agents.** An agent with a high prior (e.g., LiteratureAgent for a well-studied gene) can push the probe to look "easy" when the task is actually hard in the *modelling* sense. Mitigation: weigh probe signals by each agent's historical calibration (Brier score on prior tasks).
2. **Identifiability of φ\*.** The "true" configuration required for a task is an empirical artefact of our particular pipeline; another team could need a different φ\*. Mitigation: report φ\* as a *relative* configuration (rank within Φ) rather than absolute.
3. **Non-stationarity.** If backbones are updated (new scGPT release), the calibration drifts. Mitigation: schedule re-calibration whenever any component's version changes, and expose this via a calibration timestamp in the recommender output.
4. **Small agent count.** With N=5 agents, ACE is quantised to 5 levels; the probe signal may be too coarse for some tasks. Mitigation: also feed per-agent confidence rank into the likelihood, not just the aggregated ACE.
5. **Probe cost vs. savings.** If the probe is too expensive, the adaptive savings shrink. We target probe ≤ 10% of a full run; the one-round shallow config makes this achievable.

## 9. Contributions back upstream

### 9.1 To MassGen

A MassGen-installable evaluation skill `cellforge-eval` that wraps any MassGen multi-agent run and reports (ACE, CSD, ΔC, WFR, CST, TDI) + a preflight recommendation. See `src/perturb_eval/massgen_adapter.py`. Becomes a generic "how hard is this problem for my agent team?" diagnostic.

### 9.2 To CellForge

An instrumentation hook + a preflight CLI (`cellforge preflight "GSK3B knockout" --modality scRNA-seq`) that returns a configuration recommendation before running. Essentially a routing layer that turns CellForge into a compute-optimal system rather than a fixed-budget one.

### 9.3 To the TTC literature

A clean extension of Snell 2024 to group generation: the same "difficulty-conditional allocation" principle holds, with the group's own internal dynamics serving as the difficulty proxy — no separate PRM needed.

## 10. What's in this repo, right now

| File | Role |
|---|---|
| `src/perturb_eval/metrics.py` | ACE, CSD, ΔACE, ΔC, WFR, CST, TDI (immutable dataclasses, verified by tests) |
| `src/perturb_eval/instrumentation.py` | `RoundTrace` recorder + orchestrator hook |
| `src/perturb_eval/probe.py` | preflight probe — runs one shallow round, returns signature |
| `src/perturb_eval/bayesian.py` | closed-form Gaussian-likelihood recommender + MAP policy |
| `src/perturb_eval/calibration.py` | fits TDI coefficients + Bayesian likelihood from logged runs |
| `src/perturb_eval/data.py` | `PerturbSeqDataset` protocol + Norman/Adamson loaders + synthetic stub |
| `src/perturb_eval/model.py` | `PerturbationPredictor` protocol + `ScGPTPredictor` + `MockPredictor` |
| `src/perturb_eval/massgen_adapter.py` | expose as a MassGen skill |
| `src/perturb_eval/cli.py` | `perturb-eval preflight`, `calibrate`, `evaluate` |
| `examples/end_to_end.py` | demo run on synthetic data showing all pieces wired |
| `tests/` | unit tests for every metric and every Bayesian move |
