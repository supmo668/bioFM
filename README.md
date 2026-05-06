# bioFM — a living workspace for Biological Foundation Models

A monorepo that keeps me up-to-date on the BioFM space (DNA, RNA, protein, single-cell, multimodal) **and** turns that reading list into running code.

```text
bioFM/
├── research/     ← surveys + reference implementations; source of truth for the landscape
│   ├── Awesome-Bio-Foundation-Models/            (submodule: apeterswu/Awesome-Bio-Foundation-Models)
│   ├── awesome-foundation-model-single-cell-papers/ (submodule: OmicsML)
│   ├── biofm-eval/                               (submodule: m42-health/biofm-eval — BioFM-265M source)
│   ├── test-time-compute-guide/                  ← 📘 educational primer on test-time compute
│   │   ├── GUIDE.md                              start here (~20 min read)
│   │   ├── testtimescaling.github.io/            (submodule: TTC taxonomy & paper table)
│   │   └── ref_impl/                             framework-free reference implementations
│   └── MODELS.md                                 my classification & pipeline-fit cheat-sheet
├── tools/
│   └── MassGen/                                  (submodule: Leezekun/MassGen multi-agent scaling)
├── libs/                                         ← reusable libraries consumed by projects/
│   ├── test-time-compute/                        TTC scaling library for BioFM-265M
│   └── cellforge-agents/                         5-agent propose-critique-vote orchestrator
├── projects/
│   └── perturb-seq-eval/                         the paper-bearing research project
│                                                  (Bayesian agentic HP tuning — thesis,
│                                                   v0.5.0 real-data headline)
└── docs/
```

After cloning this repo, run:

```bash
git submodule update --init --recursive
```

to hydrate all upstream reference repositories.

## How to read this repo

1. **Start with [`research/MODELS.md`](research/MODELS.md)** — the classification of 60+ BioFMs across six domains with architecture, tokenization, objective, pipeline fit, and strengths. Groupings: DNA & Gene · RNA · Protein · Single-cell · Multimodal / science LLMs · Pathology.
2. **Read [`research/test-time-compute-guide/GUIDE.md`](research/test-time-compute-guide/GUIDE.md)** — a ~20-minute primer on test-time compute scaling (Snell 2024 + the 4-axis Zhang 2025 taxonomy) with a framework-free reference implementation (`ref_impl/`) you can run with stdlib only.
3. **Then look at the two projects** — both are standalone Python packages with working CLIs and green test suites.
4. **The `research/` submodules are pinned references** — `git submodule update --remote` to refresh; nothing in this repo writes back into them.

## Project 1 — Test-Time Compute Scaling for BioFM-265M

See [`libs/test-time-compute/README.md`](libs/test-time-compute/README.md).

Wraps `m42-health/BioFM-265M` (a 265 M Mistral-style causal genomic decoder with biologically-informed tokenization) and adds three orthogonal TTC levers:

1. **Best-of-N sampling** with a swappable biological verifier (GC content, k-mer consensus, log-likelihood, linear probe).
2. **Self-consistency** via k-mer majority voting — the DNA analogue of text self-consistency.
3. **Temperature / top-k search** to trace the compute ↔ quality Pareto frontier.

```bash
cd libs/test-time-compute
pip install -r requirements.txt && pip install -e .
pytest -q                                          # 21/21 unit tests
ttc best-of-n --prompt ATGCGTACGT --n 8
ttc self-consistency --prompt ATGCGTACGT --n 16
ttc sweep --prompt ATGCGTACGT --budget 32
```

## Project 2 — CellForge-inspired 5-Agent Group Generation PoC

See [`libs/cellforge-agents/README.md`](libs/cellforge-agents/README.md).

Five specialised agents coordinated **MassGen-style** (propose → critique → vote → refine) on perturbation-response modelling from multi-omics data:

| # | Agent | Tool belt |
|---|---|---|
| 1 | DataCurator | scanpy-style QC, GEO/CellxGene fetch |
| 2 | Literature | PubMed search, mechanism hypothesis, gene-name NER |
| 3 | Architect | BioFM catalog (reads `research/MODELS.md`) |
| 4 | Trainer | optimiser / schedule / CV-split recipe builder |
| 5 | Validator | pathway enrichment, DEG overlap, held-out AUROC, negative controls |

```bash
cd libs/cellforge-agents
pip install -r requirements.txt && pip install -e .
pytest -q                                          # 28/28 unit tests
cellforge run --perturbation "GSK3B knockout" --modality scRNA-seq
python examples/perturbation_run.py
```

Demo output (GSK3B-KO, scRNA-seq):

```text
converged            = True
consensus_score      = 0.750
winner_agent         = Validator
winner_confidence    = 0.95
n_rounds             = 2
n_proposals          = 10
n_critiques          = 40
```

## Project 3 — Perturb-Seq Agentic Evaluation + Bayesian HP Tuning (thesis)

See [`projects/perturb-seq-eval/`](projects/perturb-seq-eval/) and the full thesis at
[`projects/perturb-seq-eval/docs/THESIS.md`](projects/perturb-seq-eval/docs/THESIS.md).

Claim: the per-round joint distribution of agent confidence + critique severity in the Project 2 5-agent team is a sufficient statistic for task difficulty, and a cheap preflight probe yields a Bayesian recommender for the optimal `(n_agents, n_rounds, backbone)` configuration — the group-generation analogue of Snell 2024's compute-optimal per-prompt TTC allocation.

Ships:

- Metrics: `ACE` (Agent Confidence Entropy), `CSD` (Critique Severity Dispersion), `ΔACE`, `ΔC`, `WFR`, `CST`, composite `TDI`.
- Instrumentation hook that turns any CellForge `ConsensusResult` into a `RunTrace` without patching the orchestrator.
- Preflight probe + Bayesian Gaussian-likelihood recommender with configurable prior.
- Calibration harness (ridge regression for TDI coefficients).
- Perturb-seq dataset protocol + synthetic stub; `PerturbationPredictor` protocol with `MockPredictor` (CPU) and `ScGPTPredictor` (GPU, lazy).
- MassGen-skill adapter entrypoints.

```bash
cd projects/perturb-seq-eval
pip install -r requirements.txt && pip install -e .
pytest -q                      # 43/43 unit tests
python examples/end_to_end.py  # shows metrics + coefficient fit + Bayesian routing
```

## Contributing back upstream

- `libs/cellforge-agents/src/cellforge/orchestrator.py` is intentionally shaped like a [MassGen](https://github.com/Leezekun/MassGen) skill so it can be packaged via `npx skills add` (MassGen already supports multi-framework skill install).
- `research/MODELS.md` is a PR-ready addition to either [Awesome-Bio-Foundation-Models](https://github.com/apeterswu/Awesome-Bio-Foundation-Models) or [awesome-foundation-model-single-cell-papers](https://github.com/OmicsML/awesome-foundation-model-single-cell-papers) (pipeline-fit columns are not in either today).
- `libs/test-time-compute` layers cleanly on top of [m42-health/biofm-eval](https://github.com/m42-health/biofm-eval); a natural PR target is adding a `Generator.best_of_n(...)` convenience method alongside their existing `Generator.generate`.

## Re-running the surveys

The `research/` sub-repos are regular git clones. `cd research/<name> && git pull --ff-only` refreshes them; delete and re-clone if upstream force-pushes. Nothing in this workspace writes back into them, so updates are non-destructive.

## License

Everything I authored in `libs/`, `projects/`, and `research/MODELS.md` is Apache-2.0. The cloned sub-repos keep their upstream licenses (CC-BY-NC-4.0 for `biofm-eval`, MIT for `Awesome-Bio-Foundation-Models`, Apache-2.0 for `MassGen`, etc. — see each directory).
