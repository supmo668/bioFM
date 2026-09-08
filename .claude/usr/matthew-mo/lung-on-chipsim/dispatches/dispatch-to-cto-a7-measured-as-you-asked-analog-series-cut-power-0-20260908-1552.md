---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-08T22:52
status: created
priority: normal
size: task
subject: "A7 measured as you asked: analog series cut power 0.95 -> 0.46-0.75. Composition now matters as much as count, and the model was nearly wrong in the same way as the halt rule"
in_reply_to: null
---

# A7 measured as you asked: analog series cut power 0.95 -> 0.46-0.75. Composition now matters as much as count, and the model was nearly wrong in the same way as the halt rule

A7 was the assumption most likely to be quietly optimistic. It is, and by a lot.

MEASURED (n=40, 7 targets, true dRho=0.5)

  series size   icc   n_eff   power
            1   0.0    40.0    0.95
            2   0.5    26.7    0.88
            3   0.5    20.0    0.83
            5   0.3    18.2    0.86
            5   0.5    13.3    0.75
            5   0.8     9.5    0.46
            8   0.8     6.1    0.34

P0's headline 92% is the EXCHANGEABLE case. Under analog-series structure that is
entirely ordinary for a ChEMBL set — a few med-chem campaigns, series of five,
members correlated 0.5-0.8 — the study sits at 0.46-0.75. Forty compounds in
eight series of five carry about thirteen compounds' worth of independent
information; at icc 0.8, about nine.

THE DESIGN CONSEQUENCE, which did not exist before this was measured

Composition matters as much as count. Adding a compound from a series already
represented buys almost nothing; adding a structurally distinct one buys a full
unit of n. A 40-compound set assembled by taking whatever has measured values
against the panel will be WORSE than a 25-compound set chosen for distinctness.

So three requirements, now in the A&D:
- compound selection maximises structural diversity, as a pre-registered
  selection criterion rather than an afterthought;
- the pilot MEASURES realised clustering from SMILES (same RDKit/MMP machinery R5
  already needs, zero Modal cost) and P0 is re-run on the measured icc and
  series-size distribution;
- every reported power figure names the assumption it rests on. "92%" and "46%"
  are the same study under different ligand sets.

HOW THIS MODEL WAS NEARLY WRONG

The first implementation clustered only the PREDICTION NOISE and left the latent
z_y independent. That reduces no information — rho(f,y) is driven by z_y — so
measured power came out HIGHER under clustering (0.94 vs 0.92), and the model
would have argued A7 was free. The effect is not correlated errors; it is that
the (y, f) pairs within a series are near-duplicates.

Caught by the monotonicity test, which now fails with both numbers in its
message. The zero-equivalence test was also rewritten: it originally demanded
bit-identical rng streams, which was never the property worth testing and would
have coupled it to an implementation detail. It now asserts equivalence in
distribution.

Same shape as the halt rule and G5, and it is the third time: the machinery ran,
produced a well-formed number, and measured the wrong quantity.

YOUR STANDING CHECK — adopted into the A&D

"For every threshold, ask what quantity it is measured in and which statistic it
governs, before asking whether its value is right." Recorded as a table of the
three instances (R4 inherited D3a's units; the halt rule inherited the band's
authority; G5 inherited a general result's conclusion). Two of the three were
caught by measuring rather than by review, which is the argument for P0-style
cheap local measurement generally.

435 passed (+4), ruff clean. Nothing sealed, no batch authorized, A&D not
approved.
