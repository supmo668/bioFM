# Supplementary Design — Contextual Bayesian vs Non-Contextual Evolutionary Optimization of Agentic Hyperparameters on Perturb-Seq MSD

> **Role.** Companion design document to
> [`THESIS.md`](THESIS.md) and [`DESIGN.md`](DESIGN.md), scoping the next
> experimental iteration that (a) retains all historical metrics for
> continuity, (b) adds two new metrics where they measure something
> materially different, (c) compares two optimizers (contextual Bayesian and
> non-contextual evolutionary) on held-out perturbation MSD, (d) ships a
> small-but-valid scGPT-like biological backbone, and (e) is reproducible
> end-to-end from a single Modal command under a $20 budget.
>
> Status: design, 2026-04-20. No implementation work starts until this
> document has been reviewed and approved.

## 0. Why this document exists

The existing thesis argues that multi-agent group-generation dynamics carry
a difficulty signal and a Bayesian recommender can route configuration
allocation. The paper's Spearman numbers are fit on a synthetic DGP. To
convert the claim into a falsifiable empirical result we need:

1. a real perturb-seq task (Adamson 2016 pilot), with the perturb-seq
   community-standard **MSD on held-out perturbations** as the accuracy
   measure;
2. a real but small biological foundation model (scGPT-style, trained from
   scratch at ≈1–5M params) so "backbone choice" is a genuine axis;
3. a head-to-head comparison between a **contextual** optimizer (our
   probe-conditioned Bayesian recommender, upgraded to a factored GP with
   an expected-improvement acquisition) and a **non-contextual** optimizer
   (CMA-ES on the continuous relaxation of the configuration space) at
   matched budget;
4. a reproducible Modal deployment with a strict cost ceiling.

This document formalizes all four and lists the scripts + supplementary
docs that implement them. It deliberately does **not** reproduce the
thesis's theoretical framing — see [`THESIS.md`](THESIS.md).

## 1. Metric catalogue (what is kept, what is added, what is removed)

### 1.1 Historical metrics (retained unchanged for paper continuity)

| Symbol | Definition | Origin | Retained as |
|---|---|---|---|
| `ACE_H` | $H\big(\mathrm{softmax}(c/\tau)\big) / \log N$, τ=1 | `metrics.py::agent_confidence_entropy` (current) | `ace_h` |
| `CSD` | $\mathrm{Var}(S_{i\ne j})$ over off-diagonal severities | `metrics.py::critique_severity_dispersion` (current) | `csd` |
| `ΔACE`, `ΔC`, `WFR`, `CST` | first-differences + flip counts | `metrics.py` (current) | unchanged |
| `TDI` | $\alpha\,\mathrm{ACE\_H} + \beta\,\mathrm{CSD} + \gamma(1-\widetilde{\Delta C}) + \delta\,\mathrm{WFR}$ | `metrics.py::task_difficulty_index` (current) | unchanged |

All unit tests under [`tests/test_metrics.py`](../tests/test_metrics.py) continue
to pass unchanged; all numbers in the current [`paper/paper.pdf`](../paper/)
remain reproducible bit-exact.

### 1.2 New metrics (added because their claim-semantic is different)

| Symbol | Definition | Why new |
|---|---|---|
| `ACE_D` | $H(p) / \log N$ with $p_i = c_i / \sum_j c_j$ | Direct entropy of raw confidence shares; removes the softmax-temperature free parameter; matches the claim "how unequal are confidences". Disagrees with `ACE_H` on concentrated-confidence inputs (0.00 vs 0.85 at $c=(1,0,0,0,0)$). |
| `CSD★` | $(\max S_{i\ne j} - \mathrm{med}\,S_{i\ne j}) / (1 - \mathrm{med}\,S_{i\ne j} + \varepsilon)$ | Matches the thesis prose "one large critique dwarfs many small." `CSD` (variance) peaks on bimodal coalitions; `CSD★` peaks on lone outliers. They disagree sharply on the single-severe-critic pattern. |
| `TDI₂` | `TDI` plus six pairwise interaction terms (`ACE_H×(1-ΔC)`, `CSD×ACE_D`, …) with ridge fit | Nested super-model of `TDI`. Tests whether multiplicative structure (flat **and** non-converging is worse than either alone) is real. If interactions are noise, ridge shrinks them to zero and `TDI₂` collapses to `TDI`. |

Empirical overlap characterization (Spearman rank correlation between each
new metric and its historical counterpart, across ≥1000 synthetic traces)
is **reported** in every experiment output: if either new metric exceeds
$\rho \ge 0.95$ in overlap we pre-commit to dropping it in the next
revision.

### 1.3 Design notes

* **Why not just replace `ACE_H` with `ACE_D`?** Because `ACE_H` is the
  metric that reports all current paper numbers and the preservation of the
  paper's reproducibility table ([`DESIGN.md §6.5`](DESIGN.md)) is a hard
  constraint. Adding `ACE_D` side-by-side is strictly more informative —
  the ridge fit chooses; the paper keeps its existing results.
* **Why keep `CSD` when `CSD★` matches the prose?** Because `CSD` actually
  carries signal about *coalition-style* disagreement (half the team
  severe, half polite) — a genuine and different failure mode. `CSD★` is
  additive, not replacement.
* **Why `TDI₂` as nested?** Nesting guarantees non-degradation: the ridge
  fit of `TDI₂` is constrained to be at least as good as `TDI` in-sample,
  and the held-out penalty reveals overfitting. This is cleaner than
  head-to-head model swap.
* **What would trigger dropping a new metric?** Pre-registered: (i)
  Spearman($m, m'$) ≥ 0.95 across seeds on E1 synthetic data, *and*
  (ii) $|\Delta$TDI₂-Spearman-on-held-out$|$ < 0.02 from removing it.

## 2. Optimizers under comparison

### 2.1 Configuration space $\Phi$

$$\Phi = \{3,4,5\}_\text{agents} \times \{1,2,3\}_\text{rounds} \times \{\text{linear},\text{mlp},\text{scgpt\_small}\}_\text{backbone}$$

$|\Phi| = 27$. Each $\phi \in \Phi$ specifies how to run the 5-agent
CellForge orchestrator and which backbone it trains when it reaches the
`Trainer` step.

### 2.2 Accuracy metric $y_T(\phi)$

For task $T$ = "hold out perturbation $p_T$ from Adamson 2016 pilot":

$$y_T(\phi) = \mathrm{MSD}_T(\phi) = \frac{1}{|K|} \sum_{g \in K} \big( \widehat{\log\mathrm{FC}}_g(p_T; \phi) - \log\mathrm{FC}_g(p_T) \big)^2$$

where $K$ is the top-$k$ (default $k=20$) differentially expressed genes
under $p_T$ (Wilcoxon rank-sum, BH-corrected q < 0.05). MSD is the
perturb-seq community-standard metric used by CPA (Lotfollahi 2023),
GEARS (Roohani 2024), and scGPT-perturb (Cui 2024) — all cited in
[§8 References](#8-references).

Lower $y$ is better.

### 2.3 Contextual GP recommender (primary innovation)

Model the surrogate

$$y_T(\phi) \sim \mathcal{GP}\big(\mu(\phi, x_T),\, k_\Phi(\phi, \phi')\, k_X(x_T, x_{T'})\big)$$

where:

- $x_T \in \mathbb{R}^4 = (\mathrm{ACE}_0, \overline{c}_0, \mathrm{CSD}_0, \max c_0)$, harvested from
  a single shallow round of orchestration on task $T$ (= the "probe");
- $k_\Phi(\phi, \phi') = \exp(-d_H(\phi,\phi')/\ell_\Phi)$ is a Hamming
  kernel over the discrete 27-point Φ;
- $k_X(x, x') = \mathrm{Mat}\acute{\text{e}}\mathrm{rn}_{5/2}(\|x - x'\|/\ell_X)$ is a standard
  length-scale Matérn on the continuous probe space;
- Acquisition: **Expected Improvement** on the Φ × X joint, argmax over
  Φ for fixed observed $x_T$.

At iteration $t$: observe $T_t$, compute $x_{T_t}$ by a one-round shallow
preflight, pick $\phi_t = \arg\max_\phi \alpha_\text{EI}(\phi, x_{T_t}; \mathcal{D}_{t-1})$, run
the full orchestration + training at $\phi_t$, observe $y_{T_t}(\phi_t)$,
update $\mathcal{D}_t$.

**Regret bound.** Under assumptions standard for GP bandits, cumulative
regret after $T$ rounds is $O(\sqrt{T \gamma_T})$ where $\gamma_T$ is the
maximum information gain of the joint kernel — bounded by $O((\log T)^{d+1})$
for $d$-dimensional Matérn and $O(\log T \cdot |\Phi|)$ for the Hamming
component (Krause & Ong 2011, NeurIPS). This is the formal guarantee
the closed-form Gaussian-MAP in the current [`bayesian.py`](../src/perturb_eval/bayesian.py)
does *not* have. The closed-form Gaussian-MAP is retained as the
cheap/cold-start fallback.

Implementation: `scikit-optimize` (`skopt.Optimizer` with custom kernel)
or `botorch` if `torch` is already loaded. Either is ≈30 LOC.

### 2.4 Evolutionary baseline — CMA-ES on continuous relaxation

Non-contextual: ignores $x_T$.

Map $\Phi$ to $\mathbb{R}^3$ by dequantization: $\phi \mapsto (n_\text{agents}/5,\ n_\text{rounds}/3,\ \text{backbone\_idx}/2)$.
CMA-ES (Hansen 2016) with $\sigma_0 = 0.3$, population size $\lambda = 8$.
Each offspring is rounded to the nearest $\phi \in \Phi$; duplicates are
resampled. Objective: $\mathbb{E}_T [y_T(\phi)]$ estimated by Monte Carlo
across tasks.

Implementation: `cma` PyPI package, ≈20 LOC.

### 2.5 Random baseline

Draw $\phi_t \sim \text{Uniform}(\Phi)$ each iteration. Serves as the
floor — any real optimizer must beat it.

### 2.6 What the comparison tests

- **Contextual-BO > CMA-ES at matched budget** ⇒ the probe $x_T$ is informative and per-task routing dominates one-size-fits-all. **Validates the thesis's adaptivity claim.**
- **CMA-ES > Contextual-BO** ⇒ a dominant $\phi^*$ exists and probe noise hurts. **Falsifies the adaptivity claim cleanly.**
- **Both ≈ Random** ⇒ $|\Phi|=27$ is too small for any optimizer to matter. Design-level falsification.

This is more diagnostic than a synthetic Spearman ρ because it is grounded
in the downstream task metric perturb-seq papers actually report.

## 3. Small-but-valid scGPT-like backbone

### 3.1 Rationale

"Small but valid" = uses scGPT's architectural principles (gene-as-token,
rank-value expression encoding, transformer encoder, masked expression
objective, LoRA finetune head) at a scale that fits a single A10 and
trains in ≤ 5 minutes on Adamson pilot. Not a scaled release — a pedagogic
but honest reproduction.

### 3.2 Architecture

| Component | Value | Rationale |
|---|---|---|
| Gene vocabulary | 2 000 most variable genes (Seurat-style HVG) | scGPT uses ~36 000 at full scale; 2 000 is enough to capture UPR pathway in Adamson |
| Expression encoding | 21 rank bins per cell | scGPT uses 51; 21 keeps embedding tables small |
| Embedding dim | 128 | |
| Layers | 4 transformer encoder blocks | |
| Attention heads | 4 | |
| FFN hidden | 512 | |
| Max genes per cell | 1 024 | Ranked by expression, truncated |
| Param count | ≈ 2.1 M | |
| Pretrain objective | Masked expression modelling (15 % mask rate, cross-entropy over bins) | scGPT's MLM variant |
| Pretrain data | Adamson control cells only (≈ 3 000 cells) | Pretrain on what we have; no external pretrained weights |
| Perturbation head | 2-layer MLP 128 → 64 → |K|, LoRA on input projection (rank 8) | LoRA keeps finetune parameter count < 30 k |
| Finetune objective | MSE on log-FC for held-out genes | Matches MSD eval metric |

Total train+finetune per task: ~3 min on A10. Inference per cell: < 1 ms.

This is **not** scGPT pretrained weights — it is a from-scratch
reproduction of scGPT's *approach* at a scale appropriate to the task and
budget. The two alternative backbones in $\Phi$ are:

- **`linear`**: ridge regression from averaged-expression vector to log-FC. ≈ 1 s to train.
- **`mlp`**: 3-layer MLP 1024 → 128 → |K|, dropout 0.1. ≈ 20 s to train.

The backbone axis is genuinely non-trivial: the MLP will likely beat `scgpt_small`
on some easy tasks (where representation learning is wasted) and lose on hard
ones — which is exactly the conditional-routing opportunity.

### 3.3 Where it lives

- `src/perturb_eval/backbones/` — new package.
  - `base.py` — `BackbonePredictor` Protocol (refinement of the existing `PerturbationPredictor`).
  - `linear.py` — scikit-learn ridge wrapper.
  - `mlp.py` — 2-layer MLP in plain PyTorch.
  - `scgpt_small.py` — the from-scratch scGPT-like transformer.
- `src/perturb_eval/model.py` retained; `ScGPTPredictor` upgraded from
  `NotImplementedError` to "dispatches to `scgpt_small.SCGPTSmall`".
- Weights cached under the Modal volume `/data/backbones/`.

## 4. Experiments

Four experiments — each self-contained, each runnable locally (CPU, tiny
data) for debug and on Modal (GPU, real data) for the headline numbers.

### E1 — Metric overlap characterization

Purpose: establish that `ACE_D`, `CSD★`, `TDI₂` are not redundant with their historical counterparts.

Inputs: the existing synthetic DGP in `paper/experiments/simulate.py`, extended to emit `ACE_D`, `CSD★` on every round.

Outputs (CSVs in `paper/experiments/out/`):
- `e1c_metric_overlap.csv` — pairwise Spearman across 2 000 synthetic runs
- `e1d_tdi2_ablation.csv` — held-out $R^2$ for {TDI, TDI₂, TDI+`ACE_D`, TDI+`CSD★`}

Decision rule: if any new metric has Spearman ≥ 0.95 with its historical counterpart **and** brings < 0.02 held-out-Spearman improvement, drop it and commit the drop to this document.

Compute: CPU, ≈ 30 s. Modal-free.

### E2 — Offline grid fill (backbone × held-out-perturbation × recipe)

Purpose: enumerate every $(φ, T)$ pair once, cache MSD, so downstream optimizer comparisons become cheap cached-bandit evaluations. This is the pattern Archon (Saad-Falcon 2024) and the GP-BO benchmark literature use.

Inputs: Adamson 2016 pilot (`data/Adamson2016_pilot.h5ad`, already downloaded, 5 768 cells × 35 635 genes, 9 perturbations).

Grid: $|\Phi| \times |T| = 27 \times 8$ = 216 cells (one perturbation reserved as a blind held-out).

For each cell: train backbone under the φ-prescribed recipe on all perturbations except $p_T$, evaluate MSD on held-out $p_T$. Three seeds per cell → 648 training runs.

Outputs: `results/e2_grid.parquet` with columns `(phi, task, seed, msd_topk, wall_time_sec, peak_mem_mb, backbone_path)`.

Compute: 648 runs × ≈ 15 s average (linear: 1 s, mlp: 20 s, scgpt_small: 90 s) ≈ 2.7 hours on A10 (Modal `gpu="A10G"` ≈ $1.10/hour) → **≈ $3.00**. Parallelizable to ~30 min wall clock at $1 per concurrent worker × 6 workers.

### E3 — Optimizer comparison on cached grid (headline experiment)

Purpose: the iteration-vs-best-MSD plot that tests the thesis.

Inputs: `results/e2_grid.parquet` from E2; a pre-recorded agentic trace per $(\phi, T)$ for computing the probe signature $x_T$ (see §5.3 for trace protocol).

Optimizers:
1. **Contextual GP + EI** (our method, §2.3).
2. **CMA-ES** on continuous relaxation (§2.4).
3. **Random baseline** (§2.5).

Protocol: for each of 20 iterations and each of 5 seeds and each of 3 optimizers and each of 8 tasks (held-out perturbations), record (iteration, seed, task, optimizer, $\phi_t$, MSD = grid lookup).

Outputs:
- `results/e3_optimizer_trajectories.parquet`
- Figure `paper/figures/fig_optimizer_comparison.pdf` — average best-MSD-so-far vs iteration, one curve per optimizer, error bars from seeds, averaged over tasks.

Compute: after E2 is cached this is CPU-only, ≈ 2 min per full sweep. Modal-free for the optimizer; Modal-free.

### E4 — Metric ablation under real-data BO

Purpose: confirm that the metric-design choices in §1 hold up on real MSD rather than synthetic difficulty labels.

Protocol: rerun E3 with the contextual GP fed four alternative probe-signature definitions: (i) current 4-d `x`, (ii) 5-d with `ACE_D` added, (iii) 5-d with `CSD★` added, (iv) 6-d with both added. Compare cumulative-regret-to-iteration-20.

Output: `results/e4_probe_ablation.parquet` + a 4-column table in the supplement.

Compute: ≈ 8 min CPU total.

### E5 — Data and compute dignity check (sanity)

Purpose: confirm that what we learned on Adamson pilot is not an artifact of the pilot's 9-perturbation size.

Protocol: bootstrap the pilot to 3× size by drawing cells with replacement within each perturbation; rerun E3 on bootstrap samples; report regret-CI overlap with the original.

Output: `results/e5_bootstrap.parquet`.

Compute: ≈ 5 min.

## 5. Scripts and Modal organization

### 5.1 Project layout additions

```
projects/perturb-seq-eval/
├── docs/
│   ├── SUPPLEMENT_DESIGN.md          ← this document
│   ├── SUPPLEMENT.md                 ← generated after all experiments; reproducibility instructions
│   └── MODAL.md                      ← Modal-specific deployment & troubleshooting
├── src/perturb_eval/
│   ├── backbones/                    ← NEW (§3.3)
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── linear.py
│   │   ├── mlp.py
│   │   └── scgpt_small.py
│   ├── metrics.py                    ← EXTENDED: add ace_d, csd_star, tdi2
│   ├── optimizers/                   ← NEW
│   │   ├── __init__.py
│   │   ├── contextual_gp.py          ← §2.3
│   │   ├── cma_es.py                 ← §2.4
│   │   └── random_baseline.py        ← §2.5
│   └── experiments/
│       ├── __init__.py
│       ├── e1_metric_overlap.py
│       ├── e2_grid_fill.py           ← Modal entrypoint
│       ├── e3_optimizer_comparison.py
│       ├── e4_probe_ablation.py
│       └── e5_bootstrap.py
├── scripts/
│   ├── modal/
│   │   ├── app.py                    ← Modal app + image + volume definitions
│   │   ├── train_grid_cell.py        ← the unit of work for E2
│   │   ├── orchestrate_e2.py         ← spawns 648 train_grid_cell calls
│   │   ├── collect_traces.py         ← records agent traces over OpenRouter free tier
│   │   └── run_all.py                ← one-button reproducibility driver
│   ├── local/
│   │   ├── debug_backbone.py         ← 200-cell toy backbone train
│   │   ├── debug_e3.py               ← run E3 on a 2×3 mini-grid
│   │   └── sanity_probe.py           ← extract probe signature from a dummy trace
│   ├── fetch_adamson.py              ← EXISTING
│   └── live_smoke.py                 ← EXISTING
├── pyproject.toml                    ← MIGRATED to Poetry (§5.4)
├── poetry.lock                       ← NEW
└── Modalfile                         ← optional, for docs
```

### 5.2 Modal app structure (`scripts/modal/app.py`)

```python
import modal

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("git", "build-essential")
    .pip_install("poetry==1.8.3")
    .add_local_dir(
        "/home/mo/projects/Hackathon/ContextualGenticmen/bioFM/projects/perturb-seq-eval",
        remote_path="/app",
    )
    .workdir("/app")
    .run_commands(
        "poetry config virtualenvs.create false",
        "poetry install --with scgpt,modal,research,paper --no-interaction",
    )
)

app = modal.App("perturb-eval")
VOL = modal.Volume.from_name("perturb-eval-data", create_if_missing=True)

@app.function(image=image, gpu="A10G", timeout=600, volumes={"/data": VOL})
def train_grid_cell(phi: dict, task: str, seed: int) -> dict:
    """One (phi, task, seed) training run. Returns MSD + wall time."""
    from perturb_eval.experiments.e2_grid_fill import train_one
    return train_one(phi, task, seed, data_dir="/data/adamson")

@app.function(image=image, cpu=2.0, timeout=7200, volumes={"/data": VOL})
def orchestrate_e2() -> str:
    """Fan out 648 train_grid_cell calls; write parquet to /data/results/."""
    import pandas as pd
    phis = enumerate_phi()        # 27
    tasks = adamson_tasks()       # 8
    seeds = [2026, 2027, 2028]
    futures = [
        train_grid_cell.spawn(phi=phi, task=t, seed=s)
        for phi in phis for t in tasks for s in seeds
    ]
    rows = [f.get() for f in futures]
    pd.DataFrame(rows).to_parquet("/data/results/e2_grid.parquet")
    return "/data/results/e2_grid.parquet"
```

Concurrency cap: Modal's default concurrency limit is 100; we set
`@app.function(..., allow_concurrent_inputs=4)` and rely on 4-way
parallelism to hold cost at ≤ $4/hour on A10. Grid fill completes in ≈ 45
minutes wall clock.

### 5.3 Agentic trace recording (`scripts/modal/collect_traces.py`)

Agent traces are expensive to collect repeatedly (LLM calls). We record
**once per (φ, T) pair** — 216 traces — using OpenRouter's
`nvidia/nemotron-3-super-120b-a12b:free` (already configured in
[`configs/live.yaml`](../configs/live.yaml)). This runs locally against the
free tier, wall-clock ≈ 3–4 hours, **out-of-pocket cost $0** (free-tier
quota permitting) — not part of the Modal budget.

Each trace serializes to `artifacts/traces/<task>_<phi>.json` and is
replayed deterministically during E3 to compute probe signatures.

### 5.4 Poetry migration

Current `pyproject.toml` uses setuptools + PEP 621. Migrating to Poetry
with dependency **groups** gives us the "separate Modal dependency group"
the user requested.

```toml
[tool.poetry]
name = "perturb-eval"
version = "0.2.0"
description = "..."
authors = ["..."]

[tool.poetry.dependencies]
python = ">=3.10,<3.13"
numpy = ">=1.26"
typer = ">=0.12"

[tool.poetry.group.dev.dependencies]
pytest = ">=8"
pytest-cov = ">=4"
ruff = ">=0.5"

[tool.poetry.group.scgpt.dependencies]
torch = ">=2.2"
transformers = ">=4.42"
scanpy = ">=1.10"
anndata = ">=0.10"

[tool.poetry.group.research.dependencies]
scikit-optimize = ">=0.10"
cma = ">=3.3"
botorch = { version = ">=0.11", optional = true }

[tool.poetry.group.modal.dependencies]
modal = ">=0.68"

[tool.poetry.group.paper.dependencies]
matplotlib = ">=3.8"
pandas = ">=2.2"
pyarrow = ">=16"

[tool.poetry.scripts]
perturb-eval = "perturb_eval.cli:app"

[build-system]
requires = ["poetry-core>=1.8"]
build-backend = "poetry.core.masonry.api"
```

Local debug install: `poetry install --with dev,research,paper`.
Modal install: `poetry install --with scgpt,modal,research,paper`.
CI install (current behavior preserved): `poetry install` → only core deps; tests pass with stdlib + numpy only.

Tests continue to use only `numpy` + `typer`; no test touches `torch`,
`scanpy`, `cma`, `scikit-optimize`, or `modal`.

## 6. Supplementary document `docs/SUPPLEMENT.md` — outline

Generated **after** experiments run; it is the artifact we hand to a
reviewer for full reproduction. Sections:

1. **Environment** — Python, Poetry, Modal, CUDA, git commit hash.
2. **Data provenance** — Adamson 2016 pilot SHA-256; `fetch_adamson.py` invocation; QC numbers (n_cells, n_genes, perturbations, control fraction).
3. **Model cards** — the three backbones' exact hyperparameters, param counts, train times, peak memory.
4. **Full Modal reproduction path** — from `git clone` to `paper/figures/fig_optimizer_comparison.pdf`, every command with expected runtime and cost.
5. **Results tables** — headline MSD numbers; cumulative-regret curves; ablations.
6. **Raw artifacts** — links to the parquet + JSON files on the Modal volume (or a Zenodo mirror).
7. **Known failure modes** — list of experiments where the pipeline exited non-zero, with minimal-repro commands.
8. **Pre-registered decision rules** — the §1 decision rules applied *after* the fact, with the empirical numbers that triggered each decision.

## 7. Budget, timing, reproducibility

| Phase | Where | Wall time | Cost |
|---|---|---|---|
| Poetry migration + metric extensions + backbone package | Local | 2 h dev | $0 |
| E1 synthetic overlap | Local CPU | 30 s | $0 |
| Agentic trace collection | Local, OpenRouter free tier | 3–4 h wall clock | $0 |
| E2 grid fill | Modal A10, 4-way concurrent | 45 min | ≈ $3 |
| E3 optimizer comparison | Local CPU | 2 min | $0 |
| E4 probe ablation | Local CPU | 8 min | $0 |
| E5 bootstrap | Local CPU | 5 min | $0 |
| Modal debug, retries, cold starts | Modal | 20–40 min | ≤ $2 |
| Figures, tables, paper rebuild | Local | 2 min | $0 |
| **Total Modal** | | **≤ 90 min** | **≤ $5** |

The $20 ceiling leaves a ~4× headroom for debugging, GPU queuing, failed
runs, and rerun-on-corrupted-data. If the optimizer comparison surprises
(regret curves need a longer horizon), we can afford 60 additional
iterations on Modal (~$2) without breaching.

## 8. Risks and falsification

### 8.1 What makes this result wrong

- **Confound in the probe.** If `x_T` is dominated by the literature
  agent's recall on well-studied genes, the probe encodes "how studied is
  this gene" not "how hard is this task." The regret improvement then
  comes from memoization, not from real difficulty signal. *Check:* rerun
  E3 with the literature agent disabled; if regret improvement survives,
  the probe is real.
- **Task-count underpower.** With only 8 held-out tasks the Pareto
  comparison is noisy. *Check:* bootstrap CIs in E5; if CMA-ES and
  contextual-BO CIs overlap at all iterations, report "inconclusive" and
  scope a larger calibration set.
- **Backbone dominance.** If `scgpt_small` wins on 7/8 tasks, $\Phi$
  collapses to a trivial "always scgpt" recommendation. *Check:* report
  per-task MSD tables; note any dominance explicitly and adjust $\Phi$ in
  revision 2 (add ridge-finetune as a 4th backbone).

### 8.2 What would make the new metrics wrong

Pre-registered drop rules from §1.3: Spearman(new, old) ≥ 0.95 AND
held-out-Spearman delta < 0.02. Either rule firing triggers removal of the
new metric from the paper.

### 8.3 Deviation discipline

Any deviation from this design made during implementation is logged in
[`docs/SUPPLEMENT.md §8`](SUPPLEMENT.md) with the rationale and a diff
link.

## References

- Krause, Ong. *Contextual Gaussian Process Bandit Optimization.* NeurIPS 2011.
- Snell, Loh, Chi, Le, Liang, Kumar. *Scaling LLM Test-Time Compute Optimally Can Be More Effective than Scaling Model Parameters.* arXiv:2408.03314, 2024.
- Saad-Falcon et al. *Archon: An Architecture Search Framework for Inference-Time Techniques.* arXiv:2409.15254, 2024.
- Hansen. *The CMA Evolution Strategy: A Tutorial.* arXiv:1604.00772, 2016.
- Frazier. *A Tutorial on Bayesian Optimization.* arXiv:1807.02811, 2018.
- Lotfollahi et al. *Predicting cellular responses to complex perturbations in high-throughput screens.* Molecular Systems Biology, 2023.
- Roohani, Huang, Leskovec. *Predicting transcriptional outcomes of novel multigene perturbations with GEARS.* Nature Biotechnology, 2024.
- Cui et al. *scGPT: toward building a foundation model for single-cell multi-omics using generative AI.* Nature Methods, 2024.
- Lakshminarayanan, Pritzel, Blundell. *Simple and Scalable Predictive Uncertainty Estimation using Deep Ensembles.* NeurIPS 2017.
- Du, Li, Torralba, Tenenbaum, Mordatch. *Improving Factuality and Reasoning in Language Models through Multiagent Debate.* arXiv:2305.14325, 2023.
- Wang, Wei, Schuurmans, Le, Chi, Narang, Chowdhery, Zhou. *Self-Consistency Improves Chain of Thought Reasoning in Language Models.* ICLR 2023.
- Adamson et al. *A Multiplexed Single-Cell CRISPR Screening Platform Enables Systematic Dissection of the Unfolded Protein Response.* Cell 167, 2016.
- Norman et al. *Exploring genetic interaction manifolds constructed from rich single-cell phenotypes.* Science 365, 2019.
