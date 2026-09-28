# §decision — ChipSim (lung-on-chipsim)

<!-- HACP L2 leaf · local source; Parent = bioFM §decision. Compiled 2026-09-28. -->

**Tag:** `§decision` · **Layer:** L2 (leaf under [bioFM §decision](../decision.md)) · **Holds:** open questions the principal owns · **Reaches:** —

Each item is a choice or an artifact only the principal may produce. Where the source prices
options, the pricing is the source's. The first four are the critical path to the first result;
everything else is owed but not blocking.

## Blocking the science

### 1. T14 — adjudicate the P-gp labels *(raised 2026-08-30; 60–90 min)*

A per-compound verdict with an evidence DOI. Genuinely uncertain compounds stay `unknown`. Unblocks
T15 and the label-safety chain, and defines the two groups every coverage claim conditions on.
The worksheet emitter (T13) is built and records who supplied approve-on-execute.

### 2. M0b — curate 80–100 chip records *(raised 2026-08-30)*

The binding cost of the PoC. The allocation is sealed three-way **before any record is read**
(conformal ~40, delta-calibration ~20, locked test 20–40), so changing the split later forfeits
the records already consumed ([ADR-0002](../../../projects/lung-on-chipsim/docs/adr/0002-poc-conformal-calibration-at-20-per-group.md)).

### 3. T20, T21, T28 — the M1 inputs *(raised 2026-09-22)*

| Task | What | Option A | Option B |
|---|---|---|---|
| T20 `theta_priors.yaml` | Six device and physiology fields, each cited | Enter the four citable fields now (Huh/Ingber line, approved 2026-09-23) and mark `porosity` and `area_mm2` as `assumed: true` with a stated width | Wait until all six are sourced |
| T21 reference compounds | 3–8 with published on-chip transport data | — | — |
| T28 `transport_prior.yaml` | The `(α, k_sink)` MAP prior; it does real work on the reported result (Finding E) | — | — |

The fit refuses to run without them, by design.

### 4. M0c — sign the evaluator freeze *(raised 2026-08-30)*

The freeze is only meaningful if a human commits to it before results exist. No fit before the
signature.

## Owed, not blocking

### 5. E-23 — is an eighth gate on two clauses worth it? *(raised 2026-09-26)*

The CTO's stopping rule: if gate 8 fails on the same family (a claim wider than its check, or an
axis that rejects nothing unique), the CTO sends a one-page design note and the principal sets a
time box. Options: time-box the range and ship what passed; accept the smaller tree as final
regardless of gate 8; or stop E-23 at gate 5's surviving scope.

### 6. Push the trunk and sync the worktree *(raised 2026-09-26, bioFM §decision item 2)*

`origin/lung-on-chipsim` stops at 2026-09-20. Until the worktree is pushed, the M1 code and the
E-22/E-23 range are unverifiable from the repository and local paths appear in the HACP index
instead of repository links.

### 7. `PROVENANCE.md` — the prose half of T1 *(raised 2026-09-09)*

The plan requires it "in your own words"; the CTO has deliberately not drafted it.

### 8. Retroactive scope of the identifier constraint *(item H, raised 2026-09-25)*

Two subagent breaches predate the constraint's prospective wording. Decide whether the three
pre-existing sites are edited, annotated, or left with the constraint recorded as prospective.

### 9. The Stage 1 registered report — venue, authors, go *(raised 2026-09-26)*

In order: the claims list for CTO review, the long form, the separately written short form, the
CTO rigour review against the four entry conditions, then venue selection. No deposit, submission
or preprint without an explicit instruction; the first live contact is sandbox-only.

### 10. SLC15A1 — revisit or keep *(raised 2026-09-01)*

Airway PepT1 is contested in the literature, which is not positive evidence of absence. Kept under
the T8 ruling; the one entry worth a second look
([T8 review record](../../../workstreams/lung-on-chipsim/T8-review-record.md)).

### 11. Regenerate the module README *(raised 2026-09-28)*

Its status table reports 284 tests and 0 of 5 human artifacts on both branches. A docs task for the
worktree agent at the next boundary; the counts on [§build](build.md) and [§eval](eval.md) are the
corrected ones until then.

### 12. AM-6's residual — the sample-size contingency *(raised 2026-08-31, resolved in principle 2026-09-02)*

ADR-0002 closed the arithmetic. What remains is whether to also pre-register the contingency the
README still recommends (evaluate the two-group veto only if the sealed bucket yields ≥30 per
group, else report marginal coverage with binomial CIs and disclose the downgrade), or to strike
that paragraph as superseded.

Back to the [index](index.md).
