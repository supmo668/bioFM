# Agent Confidence Entropy & Bayesian Agentic Hyperparameter Tuning

> **Standalone paper repository.**
> This directory is self-contained and can be lifted into its own git repo
> (or submitted as-is to a conference workshop) without pulling in the
> surrounding monorepo. All dependencies (the simulation scripts, figures,
> tables, bibliography) are here.

Authoritative working copy: [`../projects/perturb-seq-eval/paper/`](../projects/perturb-seq-eval/paper/).
The code/library that produced the numbers lives at
[`../projects/perturb-seq-eval/`](../projects/perturb-seq-eval/) and is
Apache-2.0 licensed.

## Paper at a glance

- **Title.** Agent Confidence Entropy as a Pre-hoc Difficulty Oracle for
  Multi-Agent Group Generation: Bayesian Agentic Hyperparameter Tuning on
  Perturb-Seq Experimental Design.
- **Length.** 12 pages incl. references.
- **Compiles with.** TeX Live minimal (no `algorithm`/`algpseudocode`).
- **Reproduce all figures.** `make figures`.
- **Reproduce paper PDF.** `make paper`.

## Layout

```text
paper_standalone/
├── README.md                    (you are here)
├── LICENSE                      Apache-2.0 (code) + CC-BY-4.0 (paper text)
├── Makefile                     build recipes
├── paper.tex                    manuscript
├── paper.pdf                    pre-built 12-page PDF (for convenience)
├── references.bib               25 verified citations
├── figures/                     fig1..fig5 PDFs + PNGs (generated)
├── tables/                      tab1..tab5 .tex snippets (generated)
├── experiments/                 simulate.py, plot.py, generate_tables.py
│                                — seeded, deterministic, ~10 s on one CPU
└── .github/workflows/latex.yml  CI builds the PDF on push
```

## Build locally

```bash
# All in one: regenerate CSVs → figures → tables → PDF
make paper

# Just the figures / tables (fast)
make figures
make tables

# Cleanup
make clean
```

Requirements:

- Python ≥ 3.10 with `numpy` and `matplotlib` (no scipy, no sklearn, no pandas).
- TeX Live with `natbib`, `booktabs`, `hyperref`, `caption`, `enumitem`,
  `xcolor`, `microtype`, `geometry`, `lmodern`.

## Reproducibility

Every number in the manuscript traces to a CSV in `experiments/out/`.
Seed: `numpy.random.default_rng(2026)`. The full dependency graph is:

```text
simulate.py ──► experiments/out/*.csv ──► plot.py ──► figures/*.{pdf,png}
                                      └► generate_tables.py ──► tables/*.tex
                                                                 │
                                           paper.tex ◄───────────┘
                                                     │
                                                     ▼
                                              paper.pdf
```

No value in the PDF is generated outside this pipeline. Changing a single
entry in the `DGP` dict at the top of `simulate.py` produces a clearly
diffable delta across all downstream artifacts.

## Initialising as a standalone repo

This directory is designed to be lifted into its own git repository:

```bash
cp -r paper_standalone/ /tmp/ace-tdi-paper
cd /tmp/ace-tdi-paper
git init -q
git add .
git commit -m "Initial paper commit"

# Optional: push to a new GitHub repo
gh repo create ace-tdi-paper --public --source=.
git push -u origin main
```

The `.github/workflows/latex.yml` workflow is ready to compile the PDF on
every push.

## Honest limitations

The paper is explicit about what it does and does not claim:

1. **All experiments are synthetic simulations.** The data-generating
   process is documented in Section 6.1 with all 17 parameters exposed
   as one Python dict.
2. **The dominant signal is convergence ($1-\Delta C$).** In the ridge
   calibration, $\gamma\approx 0.93$; the other weights are small.
3. **The single-round probe is weak** ($R^2\!=\!0.16$ against latent
   difficulty), so the adaptive policy is competitive but not strictly
   dominant over uniform in the Pareto experiment.

Section 9 of the paper lists three falsifying outcomes that would
contradict the claims, together with the one-line configuration changes
that surface each of them.

## Citation

```bibtex
@unpublished{ace_tdi_2026,
  author = {Anonymous},
  title  = {Agent Confidence Entropy as a Pre-hoc Difficulty Oracle for
            Multi-Agent Group Generation},
  year   = {2026},
  note   = {Manuscript in preparation},
}
```

## License

- **Code** (`experiments/`, `Makefile`, `.github/workflows/`): Apache-2.0.
- **Manuscript text** (`paper.tex`, `README.md`): CC-BY-4.0.

See `LICENSE` for the full text.
