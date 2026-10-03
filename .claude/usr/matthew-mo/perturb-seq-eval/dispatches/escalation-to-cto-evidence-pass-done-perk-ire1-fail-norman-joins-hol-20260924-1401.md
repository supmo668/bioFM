---
type: escalation
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-09-24T21:01
status: created
priority: high
size: task
subject: "Evidence pass done — PERK/IRE1 fail; Norman joins hold (CRISPRa!); and ATF6 in v0.5.0 pooled 4 different UPR constructs (7th instance, EXPOSED)"
in_reply_to: null
---

# Evidence pass done — PERK/IRE1 fail; Norman joins hold (CRISPRa!); and ATF6 in v0.5.0 pooled 4 different UPR constructs (7th instance, EXPOSED)

Agent: perturb-seq-eval
REPORT on #250/#251 — the evidence pass, PLUS a finding bigger than the alias question: a seventh silent-substitution instance, and unlike the nine labels THIS ONE REACHED v0.5.0. Evidence committed: qgr/evidence/label-evidence.json.txt, nperts-audit.json.txt. No GPU spent.

1. NORMAN — path A stable-ID join holds; my cross-check was the wrong test.
   C3orf72 == FOXL2NB (ENSG00000206262), C19orf26 == CBARP (ENSG00000099625): identical IDs in all three Adamson files' var vs Norman's (Norman's column is misspelled 'ensemble_id' — the join must name it).
   Norman 2019 is a CRISPR ACTIVATION screen, so the on-target cross-check is UP, not down: CBARP +0.301, rank 33,690 of 33,694 (4th most up-regulated) — the data corroborates the join. FOXL2NB +0.006 (rank 29,770): not corroborated, not contradicted (low expression). I propose: join both (structural, per #251), record both cross-check results verbatim, FOXL2NB flagged "join structural, expression cross-check inconclusive".
   KIAA1804: in neither vocabulary under either name; no join possible -> EXCLUDE ("target gene not locatable in the dataset vocabulary"). Its most-down genes (GAL, PRSS57, ...) are generic, not a candidate.
   Side observation for the record (not in #202 scope): the backbones name their on-target feature a "dip"; for Norman's CRISPRa it is a rise. The feature is the signed logfc so the models are unaffected, but prose describing an on-target knockdown would be wrong for Norman.

2. ADAMSON PERK / IRE1 — the alias fails the #250 evidence test, and the reason is structural.
   EIF2AK3 in PERK-labelled cells: delta +0.0018, rank 25,267, control mean 0.0 (not detected). ERN1 in IRE1 cells: delta -0.0062, rank 4,187. Per #250 ("no knockdown -> the alias is wrong -> exclude"): EXCLUDE both. I am not recording an alias.

3. THE BIGGER FINDING — the Adamson label normaliser merges DIFFERENT CONSTRUCTS into one task.
   e2_adamson._normalise_pert_label = raw.split('_')[0]. The raw 10X005 labels encode combination constructs:
     'ATF6' <- ATF6_only_pMJ145, ATF6_IRE1_pMJ152, ATF6_PERK_pMJ150, ATF6_PERK_IRE1_pMJ158   (single, double, double, triple)
     'PERK' <- PERK_only_pMJ146, PERK_IRE1_pMJ154
     '3x'   <- 3x_neg_ctrl_pMJ144-1, 3x_neg_ctrl_pMJ144-2
   'ATF6' is a valid symbol, so the fail-closed resolver CANNOT catch it: the merged population silently becomes one "ATF6" task. **ATF6 IS IN THE v0.5.0 TRAINER TASK LIST** — its held-out MSD was computed on single+double+triple UPR knockdown cells pooled. Seventh silent-substitution instance; the first of today's label defects with confirmed v0.5.0 exposure. (All four raw labels and their names are the FILE'S text, not my inference — the label strings state the components.)
   Benign by contrast: several plasmids for the SAME gene pool into one gene task (XBP1 x2, CCND3 x2, ATF4 x3, ASCC3, DNAJC19, EIF2AK3, ERN1, GBF1 ...) — standard gene-level pooling, but it is implicit today.
   ALSO: 10X010 carries proper EIF2AK3 and ERN1 labels, so 'PERK'/'IRE1' are 10X005 construct names, not the only route to those genes.

   CORRECTION of my own #250 input: '3x' is not an unknown multi-target construct — the raw label is '3x_neg_ctrl'. The file's own text classifies it as a negative-control construct. Your ruling 3 (exclude, composition unconfirmed) was right on what I gave you; on the complete label it should be a STRUCTURAL CONTROL, same basis as Gal4-4(mod). I request that reversal rather than applying it myself.

PROPOSED FIX (structural, code-provable, no biology asserted) — needs your ruling:
   a. Normaliser parses the full raw label: strip the plasmid suffix `_p[A-Z]+[0-9]+(-[0-9]+)?`; strip an `_only` marker; the remainder is the construct's gene list AS WRITTEN.
   b. One component -> a gene-level task; multiple plasmids for the same gene pool, and provenance records guides_per_gene.
   c. More than one component (ATF6_IRE1, ATF6_PERK, ATF6_PERK_IRE1, PERK_IRE1) -> EXCLUDED, reason "multi-gene construct; unsupported by D1" with the raw label recorded.
   d. Label text containing 'neg_ctrl' -> structural control.
   e. A red-then-green test using the real 10X005 raw labels: today ATF6 pools 4 constructs; after, ATF6 pools only ATF6_only_pMJ145.
   f. Register: DF-07 "ATF6 in v0.5.0 pooled single/double/triple UPR constructs" — EXPOSED, not merely unexposed.
   Net effect on the sweep: ATF6 remains a task (single construct); PERK, IRE1 and the four combination constructs leave the eligible pool; 3x joins controls.

Memory: still unmeasured — both loaders still (correctly) refuse. I will measure after this lands, not before.
next_handoff: cto rule a-f + the 3x reversal
