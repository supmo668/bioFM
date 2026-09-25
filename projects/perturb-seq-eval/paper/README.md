# Paper — Does Agent Confidence Entropy Predict Task Difficulty? A Pre-registered, Provenance-Complete Test of Agentic Hyperparameter Tuning for Perturb-seq Response Prediction

Manuscript for the thesis at [`../docs/THESIS.md`](../docs/THESIS.md).

**Status:** hypotheses, gates and design are fixed; every result value is a
`\pending{...}` placeholder until the v0.6.0 sweep runs. All v0.5.0 values are
superseded — the appendix "Corrections relative to v0.5.0"
(`sections/corrections.tex`) maps each one to the register row that supersedes it.

## What's here

```text
paper/
├── README.md                    (you are here)
├── PREREGISTRATION.md           five hypotheses, gates, estimators, analysis plan
├── paper.tex                    the manuscript
├── references.bib               BibTeX bibliography
├── sections/
│   ├── experimental_setup.tex   \input by paper.tex
│   ├── results.tex              \input by paper.tex (hypotheses + \pending placeholders)
│   ├── corrections.tex          \input by paper.tex (appendix)
│   ├── v050_experimental_setup.tex   NOT input — superseded v0.5.0 text
│   ├── v050_results.tex              NOT input — v0.5.0 {{TOKEN}} template
│   └── v050_results_filled.tex       NOT input — superseded v0.5.0 values
├── figures/fig1..fig5.pdf       NOT referenced by paper.tex — retracted v0.4.1 results, no generator
└── tables/tab1..tab5.tex        NOT input by paper.tex — retracted v0.4.1 results, no generator
```

## Pipeline that will produce the results

```bash
cd projects/perturb-seq-eval

# 1. The sweep: preflight + trainer sweep + lifecycle sweep in one process.
#    OPENROUTER_API_KEY must be present in the environment; preflight refuses
#    the whole run without it.
modal run scripts/modal/app_v05.py::entrypoint

# 2. Analyse the downloaded run files -> summary.json
python -m perturb_eval.experiments.e_v05_real_traces \
    --trainer artifacts/v0.6.0/trainer_runs.jsonl \
    --lifecycle artifacts/v0.6.0/lifecycle_runs.jsonl \
    --out artifacts/v0.6.0/summary.json
```

`scripts/paper/fill_v050_numbers.py` fills `sections/v050_results.tex`, which
`paper.tex` no longer inputs. No tool currently fills the `\pending{...}`
placeholders; their values come from `summary.json` and `provenance.json`.

## Compile

Requires a TeX distribution with `latexmk` (not verified in the development
environment used for this revision).

```bash
cd paper
latexmk -pdf -interaction=nonstopmode paper.tex
```

## Referenced datasets

- Adamson et al., 2016 UPR Perturb-seq (CRISPR interference) — [GSE90546](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE90546)
- Norman et al., 2019 Perturb-seq K562 combinatorial screen (CRISPR activation) — [GSE133344](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE133344)
- Both are consumed through the scPerturb repackaging, Zenodo record 13350497, with SHA-256-pinned fetchers.

## License

Apache-2.0 (see repository root).
