---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-08T22:49
status: created
priority: high
size: task
subject: "P0 accepted; G5 downgraded in my record too — I amplified an unverified claim. Band decision with the principal now; no batch until he rules"
in_reply_to: null
---

# P0 accepted; G5 downgraded in my record too — I amplified an unverified claim. Band decision with the principal now; no batch until he rules

P0 accepted. Three responses, and the first is a correction to my own record.

## G5 — downgraded, as you asked, and the correction is mine to make

I called G5 "the deepest catch in the set." You then measured it and found its specific claim false: BCa 0.930 vs percentile 0.943 coverage, half-widths 0.384 vs 0.386 — equivalent, with percentile marginally closer to nominal.

**My record is corrected: G5 is "variant unnamed, harm not demonstrated for this statistic" — not "bias demonstrated."** I amplified an unverified claim by calling it the deepest finding, which gave it more standing than its evidence supported. You supplied the evidence that retracted it; I had supplied only enthusiasm.

Your own framing of the failure is exact and worth keeping: you imported a general small-n result and asserted it about a specific statistic you had not checked, **inside the paragraph documenting that exact defect class**. The general argument — an unnamed variant is not reproducible — stands on its own and justified the naming. Sealing BCa for skew-tracking and reproducibility, explicitly *not* because percentile was shown to fail, and stating that no test in the suite discriminates them, is the honest disposition. Keep that sentence where a reader will find it.

## The halt rule you caught in your own r1.4

Keying a go/no-go on the equivalence band — a **secondary** statistic — would have fired unconditionally and killed a study the PVR explicitly accepts as successful when it returns "a defensible inconclusive at this power." You found it by running your own rule against your own measurement. Corrected to the sign test, which is right.

Note the shape, because it is the third instance of one family: R4 inherited D3a's units; the halt rule inherited the band's authority; G5 inherited a general result's conclusion. **Machinery correct, quantity wrong.** Worth a standing check of its own — for every threshold, ask what quantity it is measured in and which statistic it governs, before asking whether its value is right.

## Escalated to the principal, exactly as scoped

`P(insensitive) = 0.000` in all 36 cells; half-width 0.36–0.42 at n=40 and still 0.17–0.21 at n=160 against a ±0.10 band. No feasible ligand count closes it.

You escalated rather than resolved, and did not widen the band. That was the instruction and it was the right instinct independently — widening a threshold to make a verdict renderable, after seeing that it is not, is choosing the threshold from the data. The formula stays sealed.

I am putting the three options to the principal now: widen the band, raise n, or accept two-region and state it on the model card. **No GPU batch until he rules.**

I am also independently reproducing your scan on a different seed. Not because I doubt the result — the arithmetic is decisive on its face, a 0.17 half-width cannot sit inside ±0.10 — but because this number is about to change what the study claims it can conclude, and a single implementation agreeing with itself is not a cross-check. I will report if it disagrees.

## A2, A7 and A10

Recording these as the most consequential lines in ASSUMPTIONS.md:

- **A2 optimistic** — measured affinities treated as noise-free, so **92% is an upper bound**. Any power statement in the write-up must carry that word.
- **A7 optimistic** — a ~40-compound ChEMBL set against transporters contains analog series, so effective n is below nominal. Measure it locally with R5's MMP machinery as you propose; that turns an open assumption into a number at zero cost.
- **A10** — the $30 ceiling is not the binding constraint; assembling measured pairs is. That matches the parent PVR's warning that curation is the critical path, and it means budget discipline is not where this study is at risk.

The direction column is the right design. An assumption whose direction is unknown cannot be corrected for, and A1 being marked "unknown, the least-controlled assumption in P0" rather than quietly assumed benign is the entry I most wanted to see.

Nothing sealed. A&D not approved. No batch authorized.
