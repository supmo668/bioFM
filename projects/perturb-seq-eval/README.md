# Project 3 — Perturb-Seq Agentic Evaluation (Thesis Infrastructure)

Companion code for the paper [`paper/paper.tex`](paper/paper.tex) and the
thesis [`docs/THESIS.md`](docs/THESIS.md):
**"Does Agent Confidence Entropy Predict Task Difficulty? A Pre-registered,
Provenance-Complete Test of Agentic Hyperparameter Tuning for Perturb-seq
Response Prediction."**

Hypotheses, gates and analysis plan: [`paper/PREREGISTRATION.md`](paper/PREREGISTRATION.md).
Results are pending the v0.6.0 sweep; all v0.5.0 values are superseded (see
the paper's appendix "Corrections relative to v0.5.0").

## Question in one sentence

Is the per-round joint distribution of agent confidence + critique severity in a
[CellForge-style 5-agent team](../../libs/cellforge-agents/) a sufficient statistic
for task difficulty? If so, a cheap preflight probe of that distribution
would yield a Bayesian recommender for team size, round count, and backbone —
turning agentic orchestration into hyperparameter tuning. The paper tests
this under five pre-registered gates.

Read [`docs/THESIS.md`](docs/THESIS.md) for the full argument.

## What this project delivers

1. **Metrics** — `ACE` (Agent Confidence Entropy), `CSD` (Critique Severity
   Dispersion), `ΔACE`, `ΔC`, `WFR` (Winner Flip Rate), `CST` (Consensus-Score
   Trajectory), and a composite `TDI` (Task Difficulty Index). All immutable,
   all unit-tested.
2. **Instrumentation** — non-invasive hook into the CellForge orchestrator
   that emits a `RoundTrace` per round without changing agent code.
3. **Preflight probe** — runs one shallow round, extracts a 4-d signature.
4. **Bayesian recommender** — maps probe signature → recommended
   `(n_agents, n_rounds, backbone)` configuration under a compute budget.
5. **Calibration harness** — fits TDI coefficients + Bayesian likelihood from
   logged runs on a labelled calibration set.
6. **Perturb-seq data + model adapters** — `PerturbSeqDataset` protocol,
   Norman/Adamson loaders with a recorded label contract; `PerturbationPredictor`
   protocol with `ScGPTPredictor` (adapter over the public scGPT release; not
   used by the paper's sweep) and `MockPredictor` (deterministic, CPU-only,
   used by tests).
7. **MassGen adapter** — expose the whole thing as a MassGen evaluation skill.

## Layout

```text
perturb-seq-eval/
├── README.md                (you are here)
├── docs/
│   └── THESIS.md            the thesis — start here
├── paper/
│   ├── paper.tex            the manuscript
│   └── PREREGISTRATION.md   hypotheses, gates, analysis plan
├── pyproject.toml
├── requirements.txt
├── src/perturb_eval/
│   ├── __init__.py
│   ├── types.py             RoundTrace, RunTrace, ProbeSignature, Config
│   ├── metrics.py           ACE, CSD, ΔACE, ΔC, WFR, CST, TDI
│   ├── instrumentation.py   orchestrator hook → RoundTrace emitter
│   ├── probe.py             preflight probe → ProbeSignature
│   ├── bayesian.py          Gaussian-likelihood recommender + MAP policy
│   ├── calibration.py       fit TDI + likelihood from logged runs
│   ├── data/protocol.py     PerturbSeqDataset protocol + loaders + stub
│   ├── model.py             PerturbationPredictor + ScGPT/Mock implementations
│   ├── massgen_adapter.py   MassGen skill entrypoint
│   ├── experiments/         sweep task plan, provenance, analyser (e_v05_real_traces.py)
│   └── cli.py               preflight | evaluate
├── tests/                   pytest suite (stdlib + numpy only)
├── examples/
│   └── end_to_end.py        toy-trace demo (hand-written RoundTraces)
└── scripts/
    ├── modal/app_v05.py     the sweep: preflight + trainer + lifecycle, one process
    └── paper/fill_v050_numbers.py  v0.5.0 number filler (targets a file the paper no longer inputs)
```

## Quick start

```bash
cd projects/perturb-seq-eval
pip install -r requirements.txt
pip install -e .

pytest -q                                                    # framework tests

# Toy-trace demo — hand-written RoundTraces, no downloads, no GPU
python examples/end_to_end.py

# Bayesian recommendation from a probe signature
perturb-eval preflight --ace-norm 0.6 --mean-conf 0.5 --max-conf 0.7 --csd 0.05
```

`tests/test_no_synthetic_generators.py` is a repository guardrail: it fails if a
synthetic-cell generator is reintroduced under `src/`, `scripts/` or `paper/`.

## Reproducing the sweep

```bash
# From projects/perturb-seq-eval. ANTHROPIC_API_KEY is injected by Infisical at
# run time (never written to disk); LLM_KEY_SOURCE records where it came
# from. Preflight refuses the whole run without either, and also requires the
# pinned pre-registration: paper/PREREGISTRATION.md tracked and committed with
# no local edits. Spend: stop-and-report above $12, hard kill at $28.
LLM_KEY_SOURCE=infisical:syntropyhealth-app:dev infisical run \
    --projectId 589d1e3b-5798-48ea-97c0-2d58086a375b --env dev -- \
    modal run scripts/modal/app_v05.py::entrypoint --version v0.6.0 \
    --norman-n-singletons 15 --norman-n-doublets 5 --seeds 3

# Analyse the downloaded run files (refuses mismatched (dataset, task) sets,
# fallback steps, unfinished or unpinned runs); defaults to artifacts/v0.6.0
python -m perturb_eval.experiments.e_v05_real_traces artifacts/v0.6.0
```

## Relationship to the other projects

```text
research/test-time-compute-guide/       theory of TTC + taxonomy
libs/test-time-compute/             TTC applied to a single BioFM (BioFM-265M)
libs/cellforge-agents/              5-agent orchestration — the thing under study here
projects/perturb-seq-eval/  ──────────► evaluation + Bayesian HP tuning for the above
```

This project is the **evaluation and adaptive-allocation layer** on top of
`cellforge-agents`. `cellforge-agents` produces the dynamics; `perturb-seq-eval`
measures them, reasons about them, and recommends how to spend compute.

## Sources

- CellForge, [arXiv:2508.02276](https://arxiv.org/abs/2508.02276)
- Snell et al. 2024, [arXiv:2408.03314](https://arxiv.org/abs/2408.03314)
- Norman et al. 2019 Perturb-seq, [Cell](https://doi.org/10.1016/j.cell.2019.05.031), [GSE133344](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE133344)
- Adamson et al. 2016 UPR Perturb-seq, [Cell](https://doi.org/10.1016/j.cell.2016.11.048), [GSE90546](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE90546)
- scGPT, [Cui et al. 2024, Nature Methods](https://www.nature.com/articles/s41592-024-02201-0) · [bowang-lab/scGPT](https://github.com/bowang-lab/scGPT)
- MassGen, [Leezekun/MassGen](https://github.com/Leezekun/MassGen)
