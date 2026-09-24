# T23 — pre-spend resource check (v0.6.0 sweep)

Measured 2026-09-24 on Modal, CPU only, through the REAL loaders with every guard active (pinned fetch
`trust_unpinned=False`, label contract, construct parser, train-only HVG). Script: `scripts/modal/measure_memory.py`.

| item | value |
|---|---|
| Adamson combined matrix | 21,841 cells x 32,738 genes, float32, **2.66 GiB** (load + one HVG pass 44 s) |
| Norman matrix | 44,423 cells x 33,694 genes, float32, **5.58 GiB** (30 s) |
| peak RSS (sequential load, each freed) | **17.99 GiB** of the 32 GiB sweep function limit — headroom 14.0 GiB |
| sweep holds BOTH resident | **MEASURED (CTO #261): peak RSS 17.99 GiB with both datasets resident, headroom 14.0 GiB** before training. The earlier ~21 GiB figure was a conservative bound and is superseded — Norman's load transient fits under the Adamson-load peak. |
| GPU | A100-40GB @ $1.32/h, Modal timeout 8 h (T22) |
| task plan | 21 Adamson (3 bins x 7, 97 eligible) + 15 + 5 Norman = **41 tasks** |
| work | 41 x 54 configs x 3 seeds ~= **2,214 trainer cells** (+14% vs 1,944) + 123 lifecycle runs |
| cost estimate | ~4 A100-h ~= **$5-6** against the **$28** soft cap (in-loop `_budget_exceeded`; no platform cap) |
| datasets | all four SHA-256 pinned; size + MD5 matched Zenodo record 13350497 |
| `OPENROUTER_API_KEY` | **ABSENT** — preflight refuses the whole run (C-KEY-1, CTO #235) |
| trunk | `main` unpushed — iteration gates blocked (stale-revert-check) |

Order note: #259 asked for the categorical sweep BEFORE this measurement; the measurement had already been
launched and completed before #259 was read. The sweep found no second reachable instance (DF-11), so the
measurement's code path is unaffected.
