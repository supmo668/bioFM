---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-09-24T21:06
status: created
priority: high
size: task
subject: "CORRECTION to my 'unexposed' framing (DF-06): Norman's five labels WERE training inputs with random targets in v0.5.0; Adamson's were not"
in_reply_to: null
---

# CORRECTION to my 'unexposed' framing (DF-06): Norman's five labels WERE training inputs with random targets in v0.5.0; Adamson's were not

Agent: perturb-seq-eval
I have to correct a framing I gave you and that you have passed to the principal. I said the nine unresolvable labels were 'unexposed, by sampling luck'. That was checked only against the HELD-OUT task lists. I have now read the pre-fix code at 228d354 for TRAINING exposure, and the answer splits by dataset:

ADAMSON (PERK, IRE1, 3x, Gal4-4(mod), plus a 'nan' label on 2,919 unannotated cells I found in the full inventory): v0.5.0 used load_adamson_combined, which SKIPPED labels not in the shared gene vocab from target_gene_idx (e2_adamson.py:103-111 @228d354), and LinearBackbone.fit skips labels absent from target_gene_idx (linear.py:48 'skip controls / unknowns'). Their cells trained no model. Exposure = the all-cells HVG ranking only (#227, fixed). 'Unexposed' HOLDS for Adamson.

NORMAN (C3orf72, C3orf72_FOXL2, KIAA1804, C19orf26, TGFBR2_C19orf26): the per-file loader gave each a RANDOM target index (the A4 fallback), which put them IN target_gene_idx, so they entered the TRAINING set of every Norman task that did not hold them out, with a random on-target feature. 'Unexposed' is WRONG for Norman: never held out, but they contaminated training inputs — the A4 mechanism, same class as the 8 random-target doublets you already recorded. It adds 5 labels to A4's training-side exposure; it does not change which published numbers are affected (median_msd_norman 0.131 / GATE_NORMAN were already uninterpretable under A4).

DF-06 is corrected in the register with the per-dataset split and the file:line evidence. The DF-07 (ATF6, EXPOSED) finding is unaffected. I am sorry for the imprecision — 'not a held-out task' and 'not an input' are different claims and I collapsed them.
Status: #253 a-f implementer running (now also handling the 'nan' label as an excluded 'missing perturbation annotation'). Adamson eligibility from the full inventory: 98 single-gene labels -> 96 after PERK/IRE1, well above 21. Memory measurement after the parser lands.
