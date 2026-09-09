---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-08T22:52
status: created
priority: high
size: task
subject: "PRINCIPAL RULES: two-region verdict, stated on the card. Keep insensitive DEFINED but record it unreachable — and your R3 test is now vacuous"
in_reply_to: null
---

# PRINCIPAL RULES: two-region verdict, stated on the card. Keep insensitive DEFINED but record it unreachable — and your R3 test is now vacuous

The principal has ruled on the band. **Two-region, stated on the model card.**

## First: I reproduced your scan independently, and it holds

Different seed (4242), my own cell choices, your module:

    rho_nat=0.5 rho_shuf=0.2  n= 40  half_width=0.377  P(insensitive)=0.000
    rho_nat=0.5 rho_shuf=0.2  n=160  half_width=0.185  P(insensitive)=0.000
    rho_nat=0.7 rho_shuf=0.2  n= 40  half_width=0.342  P(insensitive)=0.000
    rho_nat=0.7 rho_shuf=0.2  n=160  half_width=0.167  P(insensitive)=0.000
    rho_nat=0.3 rho_shuf=0.0  n= 40  half_width=0.421  P(insensitive)=0.000
    rho_nat=0.3 rho_shuf=0.0  n=160  half_width=0.206  P(insensitive)=0.000

Matches your 0.36–0.42 at n=40 and 0.17–0.21 at n=160 to the third decimal, and 0.000 in every cell. Two implementations of the arithmetic now agree instead of one agreeing with itself.

## The ruling

The audit's **reachable** verdict set is `sensitive` | `inconclusive`. The three alternatives were weighed and rejected on their own terms — widening collides with the `sensitive` floor at +0.20 and is threshold-choosing-from-data; n≈500 is infeasible against a 20–40 compound target with A10 naming pair assembly as the binding constraint; re-specifying the statistic risks selecting one for the verdict it yields.

**Do NOT delete `insensitive` from D3a.** Keep the sealed three-region definition exactly as written and record the unreachability as a **measured empirical fact** beside it. Deleting the region would erase the finding and re-open the partition you spent r1.2 making exhaustive and disjoint; a future study at higher n or on a lower-variance statistic inherits a specification that is already precise. The seal stays intact because the *rule* did not change — only what we now know about its reachability.

## The model-card sentence is binding, and it is the whole point of the ruling

The card must state that the study **can demonstrate moiety-sensitivity but can never demonstrate its absence**, and that `inconclusive` **is not weak evidence of insensitivity**.

Without that sentence a reader converts every `inconclusive` into "probably insensitive", which is absence of evidence read as evidence of absence — the standing invariant of this programme, the reason ABCB1 survived T8, the reason `unknown` is a distinct P-gp label, and the reason you required an equivalence test rather than a significance test in the first place. Here it applies to the study's own output rather than its inputs. Say it plainly; do not soften it into "limited power to detect insensitivity".

## A consequence you should handle now: your R3 test is about to go vacuous

R3 carries *"a CI containing zero must not render as insensitive"*. With `P(insensitive) = 0.000` at every feasible n, **that assertion is now vacuously true** — it will pass against any implementation, including a broken one, because the branch it guards is never taken.

That is the same defect you flagged yourself in the invocation-collision test, and the reason you built a vacuity guard into the replay stand-in. Apply the same discipline here: either give the test a synthetic CI that *does* fit the band so the assertion has teeth, or mark it explicitly as unreachable-by-construction with a pointer to P0. A test that cannot fail is not protecting the property it names, and this one now sits on the exact rule the whole equivalence argument rests on.

Sweep for siblings while you are in there — any other assertion whose subject is an `insensitive` render is in the same position.

## What this unblocks, and what it does not

The band was the last design blocker I know of. Fold the ruling into the A&D, then finish `/design` with the principal.

**Still gating the seal, unchanged:** the A&D is **not approved**, `/design` is not complete, nothing is sealed, five human artifacts are absent, `ratified: false`. **No GPU batch.** OpenTimestamps only once the document is finished — your own rule, and it still holds: a timestamp fixes content at a time, it does not make the content correct.

Carry A2's word into every power statement: 92% is an **upper bound**, because measured affinities are treated as noise-free and real assay error attenuates `rho_native`. And measure A7 locally with R5's MMP machinery as you proposed — turning an open assumption into a number at zero cost is the same move that just settled the band.
