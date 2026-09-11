# The R5 pair stratum is curated toward ~50 pairs, not discovered from the roster

**Status:** accepted (principal, 2026-09-11) — resolves a contradiction between ADR-0003 and the
audit A&D

ADR-0003 created a **pair stratum** carrying R5's cliff test. The audit A&D described the same
pairs as something that *falls out of* a ~40-compound roster: *"MMP restricts the pair pool, so at
~40 compounds the cliff stratum may be small. R5 then reports low power; it does not loosen the
criterion to fill the stratum."* One document assumed deliberate curation, the other discovery.
Nothing reconciled them, and the measured power curve shows the difference is decisive.

## The measurement

One-sided exact McNemar on discordant pairs, descriptor baseline p = 0.55, seed 4242, 2000 trials
(`workstreams/chipsim-lbm-audit/verification/r5-pair-count-curve.py`):

| LBM accuracy | 20 pairs | 40 | 60 |
|---|---|---|---|
| 0.80 (+25 pts) | 0.37 | 0.71 | **0.87** |
| 0.90 (+35 pts) | 0.69 | 0.97 | 1.00 |
| 0.70 (+15 pts) | 0.16 | 0.31 | 0.46 |

Two structural facts:

- **Fewer than five discordant pairs can never reach α = 0.05** (1/2⁴ = 0.0625) — a floor
  independent of effect size. At 10 pairs the median discordant count is exactly 5.
- **Between-pair clustering costs at most a few points**, against A7's 0.95 → 0.46 for the sign
  test. McNemar consumes the *split* of discordant pairs; clustering perturbs their *count*
  without biasing the split.

## Decision

**Curate the pair stratum deliberately, targeting ~50 pairs** — which meets the same 0.80 power
floor set for the sign test (ADR-0003), at a 25-point LBM gain over the descriptor baseline.

**Pre-registered fallback:** if the data yields fewer, R5 **reports the achieved pair count and
its power**, and **never loosens the ≥100-fold cliff to fill the stratum**. This is not new
policy — it is the A&D's existing commitment, promoted from an expectation to a pre-registration.

## Why discovery was rejected

The diversity stratum is selected **for structural distinctness**. Matched molecular pairs are
near-duplicates. **The two criteria are in direct opposition**, so discovering pairs from the
diversity roster is close to the worst available source — the likely yield is a handful, and
below five discordant the test cannot reach significance at any effect size. R5 would then report
low power *by construction* rather than by discovery, which is a different and less honest claim.

## Consequences

Cost is **human curation only**: R5 runs locally on RDKit/mmpdb at **zero Modal spend**, so the
$30 ceiling is not the constraint here — consistent with A10, which already found pair assembly
rather than budget to be the binding risk.

**R5 detects only a large effect.** At a 15-point gain it sits at 0.46 with 60 pairs and cannot be
rescued by any feasible count. This mirrors the sign test's own limit and must appear on the model
card: R5 can demonstrate a large moiety-sensitivity advantage and cannot rule out a modest one.

Expensive to revisit — the roster is a human artifact (T18) on the critical path, and the sealed
allocation is fixed before any record is read.

## Considered options

- **Discovered only** — keeps the A&D as written, adds no curation burden, but sources pairs from
  the roster least able to supply them.
- **~25 curated pairs** — half the burden, 0.81 power at a 35-point gain, but 0.49 at 25 points;
  likely returns inconclusive on the exact question R5 exists to answer.
