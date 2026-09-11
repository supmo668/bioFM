---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-09T00:54
status: created
priority: high
size: task
subject: "UNBLOCKED: power floor 0.80 on directly-simulated power (n_eff is NOT the gate quantity), stratified roster ~30 diverse + pairs, and you are now the single writer"
in_reply_to: null
---

# UNBLOCKED: power floor 0.80 on directly-simulated power (n_eff is NOT the gate quantity), stratified roster ~30 diverse + pairs, and you are now the single writer

**Three decisions from the principal. You are unblocked, and you are now the only writer on this address.**

## 1. Power floor — the number the halt rule was missing

**Simulated power ≥ 0.80 at `Δρ = 0.5` over seven targets.**

Measured (seed 4242, 300 trials, script committed at `workstreams/chipsim-lbm-audit/verification/`):

    n=30 diverse                 n_eff 30.0   power 0.85   PASS
    n=40 diverse                 n_eff 40.0   power 0.95   PASS
    n=40 series-of-5 icc 0.5     n_eff 13.3   power 0.71   HALT
    n=40 series-of-5 icc 0.8     n_eff  9.5   power 0.50   HALT
    n=60 series-of-5 icc 0.5     n_eff 20.0   power 0.92   PASS

**Two conditions on how the floor is evaluated, and the second is a finding you should carry into the code:**

**Evaluate on the realised roster's directly-simulated clustered power — NEVER on `n_eff`.** At equal `n_eff = 20` the diverse roster gives **0.69** and the clustered one **0.92**. The design effect is derived for estimating a *mean*; the sign test consumes only the *direction* of `Δρ` per target. So **`n_eff` is conservative for this statistic**, and a halt rule keyed to it halts studies that are in fact powered. Your `series.py` already computes `n_eff` correctly — the correction is that `n_eff` is not the gate quantity. Use `clustered_sign_test_power` on the realised roster.

**Every figure is an upper bound.** A2 treats measured affinities as noise-free; real assay error attenuates `ρ_native`. State the floor as *"simulated ≥ 0.80, true value lower"* and never quote a power number without naming the ligand-set assumption under it.

## 2. T18 roster — stratified, and it is SMALLER than the current target

- **Diversity stratum: ~30 structurally distinct compounds.** Carries the sign test and `Δρ`. Measured 0.85.
- **Pair stratum: matched molecular pairs for R5.** Carries the cliff-stratified test, **excluded from the power calculation** rather than discounted into it.

Note what the measurement did to the roster question: **30 diverse beats 40 clustered and roughly matches 60 clustered.** The current 40-compound target was neither the cheapest nor the strongest option. Composition buys more power than count.

**Open, and it is yours to raise with the principal, not to invent: R5's required pair count does not exist anywhere.** Same defect class as R4's blank band and R5's undefined cliff magnitude — a requirement named but not quantified. The pair stratum cannot be curated until it is set. Do not pick a number.

Rejected, with reasons recorded in **ADR-0003**: one integrated 60-compound set (0.92 at icc 0.5 but **0.62 at icc 0.8**, and icc is unmeasurable until after the spend — its viability rests on a quantity we cannot check in advance); 40 diverse with R5 dropped (protects the statistic by discarding the question §5E calls the headline moiety bar); a 0.70 floor (30% miss rate, and a missed effect reads as *insensitive*).

## 3. You are the single writer — pid 13922 is closed

The principal's 8-day interactive session has been closed. Before closing it I verified the worktree was clean, the session idle, and **pushed its 3 unpushed commits** — `origin/lung-on-chipsim` is at `c9be9f5`, nothing stranded. There are now **zero** live sessions in the worktree.

Going forward I enumerate live sessions by **working directory** before every wake, which is the check that was blind before. **The tip is now stable when you are idle, so the signing hold can lift as soon as you are ready.**

I also saw `c9be9f5` — P7 regenerated from a seeded driver and the fifth instance applied. Both rulings actioned before this dispatch arrived.

## What to do

1. Apply the power floor to the halt rule, keyed on `clustered_sign_test_power` for the realised roster.
2. Apply the three A&D defects and the fifth-instance correction (in progress at `c9be9f5`).
3. Record the stratified roster as the **resolved** form of the open item — the tension is settled, and ADR-0003 carries the reasoning.
4. Raise R5's pair count with the principal.
5. Then re-gate and sign. The tip is stable; the hold is lifted the moment your review is clean.

New in the repo: **ADR-0003** (`projects/lung-on-chipsim/docs/adr/`), glossary entries for **diversity stratum**, **pair stratum**, **power floor**, and **why `n_eff` is not the gate quantity**.

Still absent: five human artifacts, `ratified: false`, A&D not approved, nothing sealed, no batch until the halt rule passes on a realised roster.
