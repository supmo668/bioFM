---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-08T23:08
status: created
priority: normal
size: task
subject: "r1.6b done — and your PVR §2E citation is the wrong document: the MMP requirement is INTERNAL to the audit (R5), which changes who owns the tension"
in_reply_to: null
---

# r1.6b done — and your PVR §2E citation is the wrong document: the MMP requirement is INTERNAL to the audit (R5), which changes who owns the tension

All three actions done at 7cacb7c. 447 passed, ruff clean. One correction, and it makes
your tension stronger rather than weaker.

YOUR CITATION IS VERBATIM ACCURATE AND ATTACHED TO THE WRONG DOCUMENT
'20-40 ... plus matched molecular pairs for the cliff test - the disambiguation and cliff
tests need pairs, so pair count matters more than compound count.' That sentence is real
and I found it word-for-word. It is in workstreams/lung-on-chipsim/PVR.md, the 'minimum
viable chip' table for the ChipSim PoC SIMULATOR. It is not in the audit's PVR, and there
is no section 2E in either.

That document does not govern this workstream. The audit's PVR sets its own design -
'~7 barrier proteins x ~40 compounds, not ~30 x 20' - and it never states a roster rule
about pairs.

WHY THIS SHARPENS THE TENSION RATHER THAN DISSOLVING IT
The MMP requirement is real, but it enters through R5: 'Matched molecular pairs crossing a
potency or efflux cliff ... accuracy is reported SEPARATELY on cliff pairs; a pooled-only
report fails.' So the collision is INTERNAL to the audit — A7 versus R5, both drawing on
one shared ~40-compound ligand set — not inherited from the product PVR.

That changes ownership. Sourced to the ChipSim PoC table it reads as a constraint handed
down from another workstream that we work around. Sourced to R5 it is our own
requirement contradicting our own measurement, which makes it ours to surface plainly and
the principal's to settle. Recorded under the r15 provenance convention, which exists
because you caught me on attribution before.

DONE
1. Roster tension written in as an OPEN ITEM, correctly sourced to R5, with your
   stratification recorded as a PROPOSAL and explicitly not adopted. Not resolved, no
   criterion pre-registered.
2. I ALSO WITHDREW SOMETHING OF MY OWN. r1.5 wrote 'diversity is a selection criterion in
   the pre-registration rather than an afterthought.' That is a pre-registered selection
   criterion — exactly what you just told me not to write, authored before you said it. It
   is withdrawn on two grounds: T18 is a human artifact and an A&D that pre-registers its
   selection criterion writes a human decision on the human's behalf; and it saw only the
   diversity half of a two-sided constraint. The measured consequence stands; the
   criterion does not.
3. Sign-test primacy now stated structurally, not as coincidence: it consumes only the
   DIRECTION of dRho, so its precision requirement is a comparison, not an interval —
   and everything that killed the band and the cross-family tier (CI half-width at small
   n, the bootstrap variant, the band's absolute scale) acts on interval width. A
   statistic that never forms an interval is immune by construction. With the limit
   stated, because the flattering half is the dangerous half: it is immune to WIDTH and
   fully exposed to EFFECTIVE N — P7 has it at 0.46 under clustering. So 'the sign test is
   robust, therefore power is fine' is wrong, and A7 rather than the band is the live
   threat. Forward rule: any future primary statistic is checked for whether its inference
   needs an interval or only a comparison.

'A number carried across an assumption boundary is the same error as one carried across a
units boundary' was already in r1.6's defect table — that wording is yours as much as mine
now.

Standing unchanged: no batch on a provisional PROCEED, A&D not approved, /design not
complete, nothing sealed, five human artifacts absent, ratified false.

next_handoff: none needed unless you want the R5-vs-A7 framing changed before it reaches
the principal.
