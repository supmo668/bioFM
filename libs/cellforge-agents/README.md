# Project 2 — CellForge-Inspired 5-Agent Group Generation PoC

A proof-of-concept multi-agent system that tackles **perturbation-response modelling from multi-omics data** (the core problem in [CellForge](https://arxiv.org/abs/2508.02276)) by orchestrating five specialised agents the way [MassGen](https://github.com/Leezekun/MassGen) coordinates general-purpose reasoners: **propose → critique → vote**.

Each agent owns a distinct slice of the problem and has access to a narrow, biology-specific tool belt. The orchestrator is backend-agnostic — swap the `MockBackend` for an LLM (OpenAI, Anthropic, local model via `vllm`, etc.) without touching agent logic.

## The five agents

| # | Agent | Responsibility | Tools / data access |
|---|---|---|---|
| 1 | **DataCuratorAgent** | Fetch, QC and pre-process scRNA-seq / scATAC-seq / CITE-seq. Produce an AnnData-like bundle with batch flags, mito %, HVGs selected. | `tools.omics`: local scanpy-style loader, GEO / CellxGene / 10x HDF5 fetch, standard QC metrics |
| 2 | **LiteratureAgent** | Mine published priors for the perturbation of interest (target gene / drug / cytokine); return candidate mechanistic hypotheses. | `tools.literature`: PubMed / bioRxiv search, gene-name NER, pathway lookup |
| 3 | **ArchitectAgent** | Propose a neural architecture on top of a BioFM backbone (scGPT / Geneformer / scPRINT / scFoundation) with an appropriate perturbation head. | `tools.biofm_catalog`: reads `research/MODELS.md`, matches modality → candidate backbones |
| 4 | **TrainerAgent** | Convert the architecture into a training recipe: optimiser, schedule, batch composition, cross-validation split (by donor/cell type), early-stopping rule. | `tools.trainer`: recipe templates, compute budget estimator |
| 5 | **ValidatorAgent** | Biological & statistical validation: pathway enrichment of predicted DEGs, held-out cell-type transfer, calibration, negative controls. | `tools.pathway`: GSEApy-style enrichment stub, DEG overlap, Spearman vs. wet-lab ground truth |

Each agent produces a `Proposal` with a confidence score and a rationale. All five proposals plus every agent's `Critique` of the others then feed into a **consensus vote** (MassGen-style). If consensus is reached above a threshold, the winning proposal is emitted; otherwise a second round begins with the critiques fed back as additional context.

## Why this mirrors CellForge

CellForge uses "collaborative reasoning among specialised agents" to go from raw multi-omics data to an executable neural architecture that predicts perturbation responses across gene knockouts, drug treatments, and cytokine stimulations. Our five roles cover the same pipeline (data → prior → architecture → training → validation) and commit to the same evaluation modalities (scRNA-seq / scATAC-seq / CITE-seq). The difference is that this is a thin PoC: tools return stubbed biological payloads so the pattern is testable without GPUs or real-time PubMed calls.

## Why it mirrors MassGen

MassGen's thesis is **redundancy + iterative refinement + consensus**: every agent tackles the full problem, observes and critiques the others, and when confidence is high enough they vote. We implement exactly that loop in [`orchestrator.py`](src/cellforge/orchestrator.py), but with five **role-specialised** agents instead of five copies of a generalist.

## Layout

```text
cellforge-agents/
├── README.md                (you are here)
├── pyproject.toml
├── requirements.txt
├── src/cellforge/
│   ├── __init__.py
│   ├── problem.py           # immutable Problem / Context / Proposal / Critique
│   ├── backends/            # pluggable LLM backend (mock, openai, anthropic, vllm)
│   ├── tools/               # biology-specific tool belts
│   ├── agents/              # five specialised agents
│   ├── orchestrator.py      # propose → critique → vote loop
│   └── cli.py
├── tests/                   # unit tests — no network, no GPU
└── examples/
    └── perturbation_run.py  # end-to-end demo on a fake GSK3B-KO problem
```

## Quick start

```bash
cd libs/cellforge-agents
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e .

pytest -q
python -m cellforge.cli run --perturbation "GSK3B knockout" --modality scRNA-seq
python examples/perturbation_run.py
```

## Contributing back upstream

Two clear paths into the open-source ecosystem:

1. **MassGen plugin** — package `cellforge.orchestrator` as a MassGen `skill` (they explicitly support `npx skills add`). Our 5-agent team becomes a MassGen-installable role preset for biological problems. See `tools/MassGen/AGENTS.md` and `openspec/` for the extension points.
2. **CellForge companion** — open a PR on the CellForge repo (once released) adding our `ValidatorAgent.biological_validate` as a pluggable post-training hook; or contribute our `BioFMCatalog` as a shared component so other teams can reuse the `MODELS.md` inventory.

## Evaluation layer

The **per-round trace** emitted by this orchestrator (proposals × confidences × critique matrix × winner × consensus score) is the raw material for the thesis evaluation work at [`projects/perturb-seq-eval/`](../perturb-seq-eval/) — which defines `ACE`, `CSD`, `ΔACE`, `ΔC`, `WFR`, `TDI` and a Bayesian preflight recommender that adaptively picks `(n_agents, n_rounds, backbone)` for a given perturb-seq task. Read [`perturb-seq-eval/docs/THESIS.md`](../perturb-seq-eval/docs/THESIS.md).

## References

- CellForge, Chen et al., arXiv 2508.02276 — <https://arxiv.org/abs/2508.02276>
- MassGen — <https://github.com/Leezekun/MassGen>
- scGPT, Geneformer, scFoundation, scPRINT — see `research/MODELS.md`
