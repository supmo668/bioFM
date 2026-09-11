# The audit's power floor is 0.80 on directly-simulated power, and the roster is stratified

**Status:** accepted (principal, 2026-09-08)

The LBM moiety-sensitivity audit's primary inference is a one-sided sign test over seven
targets. Its power depends almost entirely on how many *independent* compounds the roster
carries, and a ChEMBL set assembled against transporters naturally contains analog series
(A7). Measured at `Δρ = 0.5`, seven targets, seed 4242:

| roster | n_eff | power |
|---|---|---|
| 30 structurally diverse | 30.0 | **0.85** |
| 40 diverse | 40.0 | 0.95 |
| 40, series of 5, icc 0.5 | 13.3 | 0.71 |
| 40, series of 5, icc 0.8 | 9.5 | 0.50 |
| 60, series of 5, icc 0.5 | 20.0 | 0.92 |

**~30 diverse compounds beat 40 clustered ones, and roughly match 60 clustered ones.**
Composition buys more power than count, and the cheaper roster is the stronger one.

## Decisions

**Power floor: simulated power ≥ 0.80 at `Δρ = 0.5`**, evaluated **on the realised roster's
directly-simulated clustered power, never on `n_eff`.** Every reported figure is an upper
bound, because A2 treats measured affinities as noise-free and real assay error attenuates
`ρ_native`.

**The roster is two strata.** A *diversity stratum* of ~30 structurally distinct compounds
carries the sign test and `Δρ`. A *pair stratum* of matched molecular pairs carries R5's
cliff-stratified test and is **excluded from the power calculation** rather than discounted
into it.

## Why `n_eff` is not the gate quantity

At equal `n_eff = 20`, the diverse roster measured **0.69** and the clustered one **0.92**.
The design effect is derived for estimating a *mean*; the sign test consumes only the
*direction* of `Δρ` per target. So `n_eff` is **conservative** for this statistic, and a
halt rule keyed to it would halt studies that are in fact adequately powered — failing in
the direction that wastes the study rather than the one that wastes the money, but failing
either way.

## Consequences

Expensive to revisit: the sealed allocation is fixed before any record is read, and the
roster is a human artifact (T18) on the critical path.

**R5's required pair count does not exist.** It is the same defect class as R4's blank
threshold band and R5's undefined cliff magnitude — a requirement named but not quantified.
It must be set before the pair stratum can be curated.

## Considered options

- **One integrated ~60-compound set**, where the analog series *are* the MMP pairs: measured
  0.92 at icc 0.5, but **0.62 at icc 0.8**, and icc cannot be measured until the roster
  exists and Boltz-2 has run. Its viability rests on an unmeasurable-in-advance quantity, and
  it roughly doubles the compound count against a ceiling sized for ~40.
- **~40 diverse only, dropping R5's cliff test**: 0.95 power, no stratification, no open pair
  count — but §5E calls cliff-stratified accuracy the headline moiety bar, so this protects
  the statistic by discarding the question.
- **A 0.70 floor**: ~23–25 compounds, cheaper, but a 30% miss rate on a true effect, and a
  missed effect reads as *insensitive* — the absence-of-evidence error the equivalence-test
  ruling exists to prevent.
- **No floor, disclosure only**: honest, but G3 exists to decide *before* the spend, and a
  gate that fires afterwards is not a gate.
