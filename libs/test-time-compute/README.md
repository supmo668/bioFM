# Project 1 — Test-Time Compute Scaling for BioFM-265M

This project demonstrates **test-time compute (TTC) scaling** on a biological foundation model by wrapping [`m42-health/BioFM-265M`](https://huggingface.co/m42-health/BioFM-265M) — a 265 M-parameter Mistral-style genomic decoder — and adding three orthogonal TTC levers on top of vanilla generation:

1. **Best-of-N sampling with a biological verifier** — sample `N` completions, score each with a domain-aware reward, return the argmax.
2. **Self-consistency** — sample `N` completions, aggregate to a consensus via k-mer majority voting (the DNA analogue of text self-consistency).
3. **Temperature / top-k search ladder** — sweep sampling hyper-parameters to trace the compute-vs-quality Pareto frontier.

The BioFM source (cloned at `research/biofm-eval/`) already exposes a causal `generate()` in
[`biofm_eval/generator.py`](../../research/biofm-eval/biofm_eval/generator.py) — we build TTC on top of it rather than reimplement inference.

> **New here?** Read the ~20-minute primer first:
> [`research/test-time-compute-guide/GUIDE.md`](../../research/test-time-compute-guide/GUIDE.md)
> — it covers the 4-axis taxonomy (What / How / Where / How Well) and ships a
> framework-free reference implementation of Best-of-N, majority vote, weighted
> majority, iterative revision, and adaptive budget allocation in
> [`research/test-time-compute-guide/ref_impl/`](../../research/test-time-compute-guide/ref_impl/).
> This project is the *applied-to-genomics* version of those ideas.

## What "test-time compute scaling" means here

For an LLM the canonical TTC moves are **majority vote** (Wang et al., 2022) and **best-of-N with a reward/verifier** (Cobbe et al., 2021; Lightman et al., 2023). Recent Anthropic / DeepMind / OpenAI results (2024-25) show you can often **match a 10× larger model by spending ~10× more inference compute on the small one**, provided the verifier is well-calibrated.

In genomics the same idea transfers but the verifier is *domain-specific*:
- for **variant embeddings** → a linear probe on a labelled benchmark becomes the scoring function;
- for **sequence generation** → biological plausibility (GC content window, stop-codon density, k-mer likelihood vs. a reference corpus, or the model's own log-likelihood) becomes the reward;
- for **variant effect prediction** → agreement across paraphrased prompts (context shuffled, stranded flipped) acts as self-consistency.

## Layout

```
test-time-compute/
├── README.md                (you are here)
├── pyproject.toml
├── requirements.txt
├── src/ttc/
│   ├── __init__.py
│   ├── config.py            dataclass-based, frozen run config
│   ├── model_loader.py      thin wrapper that handles CPU/GPU/bfloat16
│   ├── scoring.py           verifiers: log-likelihood, GC, k-mer match, linear-probe
│   ├── strategies.py        greedy / best-of-N / self-consistency / temperature-sweep
│   ├── runner.py            orchestrates a TTC run, returns RunResult dataclass
│   └── cli.py               `python -m ttc ...`
├── tests/
│   ├── test_scoring.py
│   ├── test_strategies.py
│   └── test_runner_smoke.py
└── examples/
    └── ttc_sweep.py         end-to-end demo: seed seq → compare all strategies
```

## Quick start

```bash
cd libs/test-time-compute
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e .

# Smoke test (no model weights, mocks transformer)
pytest -q

# Real demo (downloads BioFM-265M ≈ 1 GB on first run, CPU-ok)
python -m ttc.cli best-of-n --prompt "ATGCGTACGT" --n 8 --max-new-tokens 64
python -m ttc.cli self-consistency --prompt "ATGCGTACGT" --n 16 --max-new-tokens 64
python -m ttc.cli sweep --prompt "ATGCGTACGT" --budget 64
```

## Design notes

- **Immutable configs**: `RunConfig` and `StrategyResult` are `@dataclass(frozen=True)` so every experiment record is reproducible and safe to log.
- **Verifier pluggability**: `scoring.Verifier` is a `Protocol` — swap in a linear probe from `biofm-eval` without touching strategy code.
- **Budget accounting**: every strategy returns `compute_budget` (total generated tokens) so Pareto plots just work.
- **No hidden state**: all sampling is functional — `generate_many(model, tokenizer, cfg) -> list[Candidate]` — which makes self-consistency and best-of-N share infrastructure.

## Expected outcome

Running `examples/ttc_sweep.py` produces `results.jsonl` + a matplotlib PNG showing log-likelihood vs. generated tokens for each strategy. Best-of-N with the linear-probe verifier should dominate greedy at ≥4 samples; self-consistency should catch up for longer generations.

## References (theory)

- Wang et al., *Self-Consistency Improves Chain of Thought Reasoning in Language Models*, 2022.
- Lightman et al., *Let's Verify Step by Step*, 2023.
- Snell et al., *Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters*, 2024.
- Medvedev et al., *BioToken and BioFM — Biologically-Informed Tokenization*, bioRxiv 2025.03.27.
