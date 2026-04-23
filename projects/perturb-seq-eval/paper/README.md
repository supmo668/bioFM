# Paper — Bayesian Agentic Hyperparameter Tuning for Multi-Agent Perturb-Seq Design

Peer-review-ready manuscript for the thesis at
[`../docs/THESIS.md`](../docs/THESIS.md).

## What's here

```text
paper/
├── README.md                (you are here)
├── paper.tex                the manuscript (10 pages, compiled)
├── paper.pdf                compiled output (produced by the commands below)
├── references.bib           verified BibTeX bibliography
├── experiments/
│   ├── simulate.py          seeded synthetic DGP + all 5 (+2 followups) experiments
│   ├── plot.py              renders fig1..fig5 from CSVs → figures/
│   ├── generate_tables.py   emits LaTeX snippets → tables/
│   └── out/                 CSV artifacts produced by simulate.py (6 files)
├── figures/                 fig1..fig5 as PDF + PNG (for LaTeX includegraphics)
├── tables/                  tab1..tab5 as .tex snippets, \input'd by paper.tex
└── sections/                (reserved for future split-file LaTeX)
```

## Reproduce end-to-end

Total runtime: ~10 s on a CPU. No network, no GPU, deterministic (seed 2026).

```bash
cd projects/perturb-seq-eval

# 1. Run the simulation study — writes CSVs to paper/experiments/out/
python3 paper/experiments/simulate.py

# 2. Generate figures and LaTeX tables
python3 paper/experiments/plot.py
python3 paper/experiments/generate_tables.py

# 3. Compile the paper (2× pdflatex around 1× bibtex, then a third pass
#    for natbib cross-refs)
cd paper
pdflatex -interaction=nonstopmode paper.tex
bibtex paper
pdflatex -interaction=nonstopmode paper.tex
pdflatex -interaction=nonstopmode paper.tex
```

## What the experiments cover

| Experiment | Script entry | Figures | Tables |
|---|---|---|---|
| E1  — per-metric rank correlation with latent difficulty $d$ (n=300) | `run_experiment_1_metric_validation` | Fig.\,1 | Tab.\,1 |
| E1b — TDI coefficient calibration (80/20 split) | `run_experiment_1b_tdi_calibration` | Fig.\,2 (left) | Tab.\,2 |
| E2  — probe $\to$ TDI ridge regression | `run_experiment_2_probe_to_tdi`   | — | Tab.\,3 (top row) |
| E2b — probe $\to$ latent $d$ regression | `run_experiment_2b_probe_to_difficulty` | Fig.\,5 | Tab.\,3 (bottom row) |
| E3  — Pareto frontier: uniform / minimal / adaptive policies | `run_experiment_3_pareto` | Fig.\,3 | Tab.\,5 |
| E4  — agent-count sweep $N\!\in\!\{2,3,4,5,6,8,10\}$ | `run_experiment_4_agent_scaling` | Fig.\,4 | Tab.\,4 |
| E5  — univariate ablation of TDI features | `run_experiment_5_tdi_ablation` | Fig.\,2 (right) | Tab.\,1 |

## Reviewer-facing honest findings

The paper reports both successes and constraints explicitly. Highlights:

1. **Calibrated TDI** reaches Spearman $\rho = +0.918$ against the latent
   difficulty label on the held-out $20\%$; the default (heuristic) TDI
   reaches only $+0.524$. Calibration matters.
2. **One signal dominates**: the convergence feature $1 - \Delta C$ alone
   attains $\rho = +0.916$ — the ridge calibration concentrates nearly all
   weight on it $(\gamma \approx 0.93)$.
3. **The minimal probe is weak**: single-round probe $\to$ latent $d$
   regression achieves only $R^2 = 0.16$ / $\rho = +0.36$ on held-out tasks.
   This bounds how strongly the Bayesian recommender can outperform uniform
   allocation — the paper's most important limitation.
4. **Agent-count scaling is tier-dependent**: easy tasks gain $+0.21$ AUROC
   going from $N=2$ to $N=10$; hard tasks gain only $+0.06$ — which is
   precisely why adaptive allocation is worth the engineering effort, even
   with the currently weak probe.

## External dependencies used by the simulation

- `numpy` — core tensor math.
- `matplotlib` — figures (rendered as PDF + PNG).
- TeXLive (`pdflatex`, `bibtex`) for compilation. `algorithm`/`algpseudocode`
  are **not** required — the manuscript uses a plain boxed pseudocode block.

No `scipy`, no `scikit-learn`, no `pandas`: keeps the reproducibility surface
small.

## Referenced datasets (for the follow-up empirical validation plan)

- Norman et al., 2019 Perturb-seq K562 combinatorial screen — [GSE133344](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE133344)
- Adamson et al., 2016 UPR Perturb-seq — [GSE90546](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE90546)
- Replogle et al., 2022 genome-scale Perturb-seq — [GSE264667 (primary set)](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE264667)

See [`../docs/THESIS.md`](../docs/THESIS.md) §6 and the paper's
Section §7 + §9 for how a real-data run would be structured.

## License

Apache-2.0 (see repository root).
