# Test-Time Compute — educational sub-folder

A self-contained study zone for understanding **test-time compute (TTC)
scaling** before looking at how it applies to biology.

```
test-time-compute-guide/
├── README.md                       (you are here)
├── GUIDE.md                        the primer — read this first
├── testtimescaling.github.io/      cloned taxonomy website + paper tables
│                                   (Zhang et al. 2025, arXiv 2503.24235)
└── ref_impl/                       framework-free reference implementations
    ├── __init__.py
    ├── types.py                    Candidate, Verifier protocol, Generator protocol
    ├── best_of_n.py                parallel + verifier (Snell mechanism #1)
    ├── majority_vote.py            self-consistency (Wang et al. 2022)
    ├── weighted_majority.py        verifier-weighted majority (PRM-style aggregation)
    ├── iterative_revision.py       sequential revision (Snell mechanism #2)
    ├── adaptive_budget.py          compute-optimal routing (Snell's headline result)
    └── tests/
        ├── test_best_of_n.py
        ├── test_majority_vote.py
        ├── test_weighted_majority.py
        ├── test_iterative_revision.py
        └── test_adaptive_budget.py
```

## Why "framework-free"?

`ref_impl/` uses only the Python standard library. No torch, no transformers,
no HF weights. The point is to show *the algorithms*, not *one
implementation*. Once you see the shape of Best-of-N in ten lines, you can
recognise it in any codebase — including the ~300-line BioFM-aware version at
[`libs/test-time-compute/`](../../libs/test-time-compute/).

## How to study this

1. **Read [GUIDE.md](GUIDE.md)** (~20 minutes) — primer + the Zhang 2025 4-axis taxonomy.
2. **Skim [testtimescaling.github.io/README.md](testtimescaling.github.io/README.md)** — scan the big paper table to see how the taxonomy classifies real papers.
3. **Open `ref_impl/` in order**: `best_of_n` → `majority_vote` → `weighted_majority` → `iterative_revision` → `adaptive_budget`. Each file is ≤ 80 lines with a docstring explaining the axis and the canonical paper.
4. **Run the tests**: `PYTHONPATH=ref_impl python3 -m pytest ref_impl/tests/ -q`. All pass without any downloads.
5. **Jump to the applied version**: [`libs/test-time-compute/`](../../libs/test-time-compute/) shows the same strategies wrapped around BioFM-265M.

## Sources

- [Snell et al., arXiv 2408.03314](https://arxiv.org/abs/2408.03314) — the canonical TTC paper.
- [Zhang et al., arXiv 2503.24235](https://arxiv.org/abs/2503.24235) — the 4-axis taxonomy this guide adopts.
- [testtimescaling/testtimescaling.github.io](https://github.com/testtimescaling/testtimescaling.github.io) — cloned here for the per-paper classification table.
- [Wang et al., 2022 — Self-Consistency](https://arxiv.org/abs/2203.11171), [Lightman et al., 2023 — Let's Verify Step by Step](https://arxiv.org/abs/2305.20050), [Yao et al., 2023 — Tree of Thoughts](https://arxiv.org/abs/2305.10601), [Muennighoff et al., 2025 — s1](https://arxiv.org/abs/2501.19393), [DeepSeek-R1](https://arxiv.org/abs/2501.12948).
