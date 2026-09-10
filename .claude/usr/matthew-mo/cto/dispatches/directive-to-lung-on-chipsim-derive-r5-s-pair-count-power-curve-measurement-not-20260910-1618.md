---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-10T23:18
status: created
priority: high
size: task
subject: "Derive R5's pair-count power curve — measurement, not a decision. And do NOT apply A7's discount within pairs: the unit is the pair, not the compound"
in_reply_to: null
---

# Derive R5's pair-count power curve — measurement, not a decision. And do NOT apply A7's discount within pairs: the unit is the pair, not the compound

Plan re-signed at **373931c** — r2.8 landed, so T8's text no longer contradicts the Global Constraints block. You are unblocked on plan-gated work.

New task, and it is a **measurement, not a decision**.

## R5's pair count does not exist. Derive the curve; do not pick the number.

R5 requires *"matched molecular pairs crossing a potency or efflux cliff … accuracy reported separately on cliff pairs; a pooled-only report fails."* The **cliff is now defined** (principal's 1B1: MMP + ≥100-fold). What has never existed is **how many pairs the test needs** — the same defect class as R4's blank band, which you correctly refused to invent.

**Do exactly what P0 did for the sign test:** compute power as a function of pair count, locally, at zero spend, and report the curve. The principal picks the operating point, as he did for the 0.80 floor.

The statistic is a **paired** comparison — LBM arm vs descriptor baseline on the same pairs — so the unit of analysis is the pair, and the natural test is McNemar-style on discordant pairs rather than two independent proportions. Report what you actually implement.

## One thing to get right, because A7 will mislead you here

Pairs are analog series **by construction** — a matched pair differs by one moiety, which is the whole point of the cliff test. It is tempting to apply A7's clustering discount and conclude the pair stratum is crippled.

**Do not.** In the sign test the unit is the *compound* and near-duplicate compounds carry redundant information, so clustering destroys effective `n`. In the cliff test the unit is the **pair**, and the within-pair similarity is the *signal being measured*, not correlated noise between units. Twenty pairs are twenty units, not forty correlated compounds. The A7 discount applies **between** pairs — if several pairs come from one med-chem series they are not independent of each other — and that is the question worth measuring, not within-pair similarity.

Getting this backwards would be the fifth instance of the standing pattern in a new costume: **the right machinery applied to the wrong unit.**

## Deliverables

1. Power vs pair count for the R5 comparison, over a plausible range of true accuracy gaps (LBM over descriptor). Say which effect sizes are worth naming.
2. State whether between-pair clustering materially moves it, measured rather than assumed.
3. Every figure an **upper bound**, and say why — the A2 analogue applies: predicted affinities treated as noise-free flatter the LBM arm.
4. A committed, **seeded** driver, per the P7 ruling. A number that sizes the roster must be regenerable.
5. Report the curve to me and to the principal together. **Do not pre-register a pair count.**

## Standing

The signing hold **remains**. A second interactive session is live in this worktree (pid 56186, writing today), so the tip still moves during computation and no receipt signed against it would survive its own verification. The four ambiguous-authorship commits stay ungated until that resolves — this is not a judgement about your work.

Also still true: five human artifacts absent, `ratified: false` (T8's last ratification attempt did not save; the panel is unchanged in both checkouts), A&D not approved, nothing sealed, no GPU batch.

T2 and T1's structured half are done and contract-validated on trunk — merge trunk before you start.
