# PoC conformal calibration uses ~20 points per group, not the PVR's >=30

**Status:** accepted (principal, 2026-09-02) — resolves AM-6

PVR §2D requires >=30 calibration points in each of two pre-registered P-gp groups. Reading
"calibration point" as a **curated chip record** (see `CONTEXT.md`), a four-way sealed
allocation of 60-100 records leaves ~8-15 per group, so 2x30 in the conformal bucket alone
would need ~200-240 records — two to four times the M0 target at its ceiling, against a
curation task that is already the project's critical path and cannot be accelerated by any
agent.

**The arithmetic closes by removing a bucket, not by weakening the claim.** The
**active-learning pool** feeds the v3 exploration loop, and v3 is deferred from the PoC.
Reserving a quarter of the scarcest artifact in the project for machinery that will not run
was the actual defect. The PoC's sealed allocation is therefore **three-way** — conformal
calibration ~40 (two groups x ~20), delta-calibration ~20, locked test 20-40 — totalling
**80-100 records, inside the existing M0 target.** No new curation task; no bar weakened.

**Why ~20 is honest rather than a quiet downgrade.** Conformal coverage is distribution-free
and **valid at any n**; the guarantee does not depend on sample size. What degrades at n=20 is
the **precision of the coverage estimate**, not the validity of the coverage claim.

## Consequences

**Binding reporting obligation:** every coverage figure is reported **with its confidence
interval, per group.** A coverage number quoted without its CI at this n commits the same
error the audit workstream's equivalence-test ruling exists to prevent — reading a wide
interval as a clean result.

The claim remains **conditional** (Mondrian), which matters because §5E states in terms that
*"marginal coverage alone does not satisfy this bar."*

This is expensive to revisit: the sealed allocation is fixed **before any record is read**, so
changing the split later means re-sealing and forfeiting the records already consumed.

## Considered options

- **Grow the corpus to ~200-240 records** — satisfies every bar literally, at a 2-4x multiple
  on the one task no agent can accelerate. Breaks the stated PoC envelope.
- **Keep >=30 and push M0 to its 100 ceiling** — protects the coverage bar by thinning the
  locked test set to ~25, weakening the ordering and MoA bars that share the corpus. Trades
  three legs of the claim for one.
- **Rescope to marginal coverage** — **not available**: §5E forbids it in terms.
- **Pre-register a sample-size contingency** — honest, but defers the decision and risks
  spending the whole PoC to conclude "underpowered".
