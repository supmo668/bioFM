# Project 3 — Perturb-Seq Agentic Evaluation (Thesis Infrastructure)

Companion code for the thesis at
[`docs/THESIS.md`](docs/THESIS.md):
**"Agent Confidence Entropy as an Empirical Difficulty Oracle for Multi-Agent
Group Generation, with a Bayesian Pre-Test for Agentic Hyperparameter Tuning
on Perturb-Seq Experimental Design."**

## Thesis in one sentence

The per-round joint distribution of agent confidence + critique severity in a
[CellForge-style 5-agent team](../../libs/cellforge-agents/) is a sufficient statistic
for task difficulty. A cheap preflight probe of that distribution yields a
Bayesian recommender for the optimal team size, round count, and backbone —
turning agentic orchestration into hyperparameter tuning.

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
   Norman/Adamson loaders + synthetic CI stub; `PerturbationPredictor`
   protocol with `ScGPTPredictor` (real) and `MockPredictor` (deterministic,
   CPU-only, used by tests).
7. **MassGen adapter** — expose the whole thing as a MassGen evaluation skill.

## Layout

```text
perturb-seq-eval/
├── README.md                (you are here)
├── docs/
│   └── THESIS.md            the thesis — start here
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
│   ├── data.py              PerturbSeqDataset protocol + loaders + stub
│   ├── model.py             PerturbationPredictor + ScGPT/Mock implementations
│   ├── massgen_adapter.py   MassGen skill entrypoint
│   └── cli.py               preflight | calibrate | evaluate
├── tests/                   pytest suite (stdlib + numpy only)
├── examples/
│   └── end_to_end.py        synthetic end-to-end demo
└── scripts/
    ├── make_synthetic.py    build the tiny AnnData stub for CI
    └── fetch_norman.py      download Norman 2019 (needs network + scanpy)
```

## Quick start

```bash
cd projects/perturb-seq-eval
pip install -r requirements.txt
pip install -e .

pytest -q                                                    # framework tests

# Synthetic end-to-end demo — no downloads, no GPU
python examples/end_to_end.py

# Preflight probe on a real perturbation (needs the cellforge-agents project installed)
perturb-eval preflight --perturbation "GSK3B knockout" --modality scRNA-seq
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
