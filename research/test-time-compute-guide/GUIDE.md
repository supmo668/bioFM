# Test-Time Compute Scaling — A Study Guide

A self-contained primer you can read in ~20 minutes. Intended audience: someone
who already knows Transformer-based LLMs but has not internalised the modern
TTC literature. After reading, you should be able to (a) place any new TTC
paper on a four-axis taxonomy, (b) pick the right TTC strategy for a given
problem + compute budget, and (c) map each idea onto the code we wrote in
[`projects/test-time-compute/`](../../projects/test-time-compute/) and
[`projects/cellforge-agents/`](../../projects/cellforge-agents/).

## 0. Why this exists

Pre-training scaling has hit diminishing returns (data saturation, data
contamination, compute costs). **Test-time compute (TTC)** — spending extra
compute *per query* rather than on training — has re-emerged as the main lever.
The two results that kicked off the modern wave:

- **Snell, Lee, Xu, Kumar (2024), *"Scaling LLM Test-Time Compute Optimally
  can be More Effective than Scaling Model Parameters"*,
  [arXiv:2408.03314](https://arxiv.org/abs/2408.03314)** — showed that on
  MATH, a *small* base model with an **optimally allocated** TTC budget can
  beat a **14× larger** model under FLOPs-matched comparison.
- **Zhang et al. (2025), *"What, How, Where, and How Well? A Survey on
  Test-Time Scaling in Large Language Models"*,
  [arXiv:2503.24235](https://arxiv.org/abs/2503.24235)** — the four-axis
  taxonomy the testtimescaling.github.io repo is organised around. Cloned at
  [`testtimescaling.github.io/`](testtimescaling.github.io/).

The practical implication for biology: OSS BioFMs are still *small* compared
to frontier text LLMs (BioFM-265M has **265 M** parameters; ESM-3 up to 98 B;
Evo 2 up to 40 B). For the small ones, **TTC is the cheapest capability
multiplier available.**

## 1. The four-axis taxonomy (Zhang et al. 2025)

Every TTC paper can be decomposed along four orthogonal axes. This is the
single most useful lens we have.

```
                          TEST-TIME SCALING
                                 │
        ┌───────────┬────────────┼───────────┬──────────────┐
        ▼           ▼            ▼           ▼              ▼
  WHAT to scale  HOW to scale  WHERE to     HOW WELL       (one paper
                               scale        does it scale?   can touch
                                                             several
                                                             axes)
```

### 1.1 What to scale — the *shape* of the extra compute

| Shape | Idea | Example |
|---|---|---|
| **Parallel** | Generate `N` independent candidates, aggregate. | Best-of-N, self-consistency, multi-agent verification |
| **Sequential** | Revise / extend one chain step-by-step; later tokens depend on earlier critique. | Self-refine, Chain-of-Draft, Meta-Reasoner |
| **Hybrid** | Parallel branches, each sequential (or vice versa). | Tree of Thoughts, MCTS, rStar-Math |
| **Internal** | Model itself decides how much compute to allocate, through training (RL / SFT on long CoT). | DeepSeek-R1, s1, o1 replications |

### 1.2 How to scale — the *mechanism*

Divided into **training-time preparation** vs. **pure inference-time technique**:

- **Tuning** (training-time setup for later TTC)
  - *SFT*: fine-tune on long reasoning traces.
  - *RL*: reward long/correct trajectories (GRPO, DPO, PPO).
- **Inference** (pure test-time moves)
  - *Stimulation (STI)*: get the model to produce more/longer samples (CoT, Chain-of-Draft, Think prompts).
  - *Verification (VER)*: score candidates (PRM, ORM, tool-based checker, LLM-as-judge, multi-agent vote).
  - *Search (SEA)*: navigate the output space (Best-of-N ≈ width-1 tree, beam search, MCTS, DVTS, Lookahead).
  - *Aggregation (AGG)*: combine candidates (majority vote, weighted BoN, fusion, particle filtering).

### 1.3 Where to scale — the *task domain*

Two macro-families:
- **Reasoning**: math, code, science, game & strategy, medical diagnosis, theorem proving.
- **General-purpose**: open-ended Q&A, agentic workflows, knowledge retrieval, multimodal grounding.

### 1.4 How well does it scale — the *evaluation axis*

- **Performance**: Pass@1, Pass@k, win rate, AUROC, F1.
- **Efficiency**: FLOPs-matched comparison, tokens-per-correct-answer.
- **Controllability**: does it respect a stated budget or latency ceiling?
- **Scalability**: does accuracy keep rising as you add compute? (slope of the scaling curve)

## 2. Snell et al. 2024 — the canonical two mechanisms

Snell et al. were not the first to think of TTC, but they were the first to
**ask whether TTC can replace scale** under FLOPs-matched comparison. Their
two mechanisms map cleanly onto the taxonomy:

1. **Verifier-guided search over samples** (Parallel / Hybrid, Inference-SEA+VER)
   - Generate `N` candidates.
   - Score each with a **process reward model (PRM)** — a separately-trained
     model that scores *intermediate steps*, not just final answers.
     (ORMs, in contrast, only score the final answer.)
   - Pick the best, or do a beam search / look-ahead where the PRM is the
     selection criterion at each expansion.

2. **Iterative revision by a refinement model** (Sequential, Inference-STI)
   - Train (or prompt) the model to revise its own previous answer.
   - At test time, unroll `R` revisions, optionally scored by the PRM.

**The headline finding:** neither mechanism dominates. Which one wins depends
on **problem difficulty**:

```
easy  ──► sequential revision wins  (model almost had it; nudge it)
hard  ──► parallel search wins      (need to sample a different mode)
mixed ──► hybrid, adaptively routed (their "compute-optimal" strategy)
```

Under this adaptive allocation, a small model + TTC beats a 14× larger
parameter-scaled counterpart at the same total FLOPs.

## 3. A practical decision tree

Given a new problem + budget, use this ladder. The code in
[`ref_impl/`](ref_impl/) implements each rung.

```
Can you verify a candidate cheaply (rule-based, tool, test suite)?
│
├── Yes ─► Is the base model ≥ 30% accurate on the task?
│          │
│          ├── Yes ─► Best-of-N with hard verifier
│          │         (ref_impl/best_of_n.py)
│          │
│          └── No ──► Sequential revision with verifier-in-the-loop
│                    (ref_impl/iterative_revision.py)
│
└── No ──► Do you have a PRM or a domain reward model?
           │
           ├── Yes ─► Weighted Best-of-N + beam search
           │         (ref_impl/weighted_majority.py)
           │
           └── No ──► Self-consistency (majority vote)
                    (ref_impl/majority_vote.py)
```

Add a meta-layer for **adaptive allocation** (spend more budget on harder
prompts) → `ref_impl/adaptive_budget.py`.

## 4. Mapping to the code in this repo

| Concept in the taxonomy | File in our repo | Axis |
|---|---|---|
| Best-of-N with verifier | [`projects/test-time-compute/src/ttc/strategies.py::_best_of_n`](../../projects/test-time-compute/src/ttc/strategies.py) | Parallel, SEA + VER |
| Self-consistency (majority) | [`projects/test-time-compute/src/ttc/strategies.py::_self_consistency`](../../projects/test-time-compute/src/ttc/strategies.py) | Parallel, AGG |
| Temperature-sweep (width-1 search over sampling hparams) | `strategies.py::_temperature_sweep` | Hybrid, SEA |
| Swappable verifier (domain reward) | [`scoring.py`](../../projects/test-time-compute/src/ttc/scoring.py) | VER |
| Compute-budget accounting | `StrategyResult.compute_budget` | *How well: Efficiency* |
| Multi-agent verification + voting | [`projects/cellforge-agents/src/cellforge/orchestrator.py`](../../projects/cellforge-agents/src/cellforge/orchestrator.py) | Parallel + Hybrid, VER + AGG |

Everything in `ref_impl/` below is **framework-free** — no transformers, no
torch — so you can study the algorithm in isolation before looking at the
genomic wrappers.

## 5. Why TTC is specifically leveraged in biology

A few features of the biology setting amplify TTC's payoff:

1. **Strong, cheap, domain-specific verifiers exist.** GC content, k-mer
   frequency, secondary-structure free energy, docking score, pathway
   enrichment, held-out donor validation, AlphaFold pLDDT — all are much
   cheaper than a full PRM and well-calibrated. This makes Best-of-N with a
   hard verifier very attractive.
2. **OSS BioFMs are small.** At 265 M–10 B params, BioFM-265M, scGPT,
   Geneformer, etc., have room on the TTC curve *before* diminishing returns.
3. **Problem difficulty varies wildly by perturbation / gene / variant.**
   Adaptive allocation (Snell's compute-optimal strategy) is the right default.
4. **The multi-agent frontier is wide open.** Our
   [`cellforge-agents`](../../projects/cellforge-agents/) project is a direct
   instantiation of *multi-agent verification* (arXiv:2502.20379) in a
   biology setting.

## 6. Further reading (ranked by pedagogical value)

1. **Snell et al. 2024, *2408.03314*** — start here; the conceptual north star.
2. **Wang et al. 2022, *Self-Consistency*** — simplest TTC method that works.
3. **Lightman et al. 2023, *Let's Verify Step by Step*** — PRM training.
4. **Cobbe et al. 2021, *Training Verifiers to Solve Math Word Problems*** —
   the original ORM.
5. **Yao et al. 2023, *Tree of Thoughts*** — the hybrid search exemplar.
6. **Muennighoff et al. 2025, *s1: Simple test-time scaling*** —
   minimal working example (budget forcing with `"Wait"`).
7. **DeepSeek-AI 2025, *DeepSeek-R1*** — internal scaling (RL-grown CoT).
8. **Zhang et al. 2025, *2503.24235*** — the taxonomy.
9. **Multi-Agent Verification, *2502.20379*** — the direct inspiration for
   our `cellforge-agents` orchestrator.
10. **Inference Scaling Laws, *2408.00724*** — the empirical curves.

## 7. Exercises

1. Classify the three TTC strategies in
   [`projects/test-time-compute/src/ttc/strategies.py`](../../projects/test-time-compute/src/ttc/strategies.py)
   on all four axes (What / How / Where / How Well). Answer key in comments of
   each strategy function.
2. Implement **beam search with PRM-style scoring** as a new strategy in
   that file. Target ~30 LOC. Hint: keep the top-k at every step rather than
   only at the end, using the existing `Verifier`.
3. Wire your `cellforge-agents` team to use the TTC `best_of_n` strategy for
   each agent's internal proposal — you should see `consensus_score` rise for
   ambiguous perturbations.
