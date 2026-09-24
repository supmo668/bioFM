---
type: escalation
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-09-24T20:55
status: created
priority: high
size: task
subject: "Addendum to the Adamson-labels escalation: Norman has 5 more (outdated HGNC symbols) — same ruling covers both"
in_reply_to: null
---

# Addendum to the Adamson-labels escalation: Norman has 5 more (outdated HGNC symbols) — same ruling covers both

Agent: perturb-seq-eval
Addendum — the Norman memory pass hit the same resolver refusal:
  ValueError: 5 perturbation target gene(s) absent from the gene vocabulary (len=33694). Missing (label, gene): ('C3orf72_FOXL2','C3orf72'), ('C3orf72','C3orf72'), ('KIAA1804','KIAA1804'), ('C19orf26','C19orf26'), ('TGFBR2_C19orf26','C19orf26')
These are OUTDATED HGNC symbols for genes the vocabulary holds under current names (C3orf72 -> FOXL2NB, KIAA1804 -> MAP3K21, C19orf26 -> CBARP) — label/vocab naming skew, not missing genes. Two are doublets. Checked: none in the v0.5.0 artifacts (sampling luck again; the old '+' guard would also have randomised them).

So both datasets need the same ruling: how perturbation labels map to vocabulary genes. Revised recommendation, in order of preference:
 A. Resolve via the h5ad's own gene metadata if it carries Ensembl IDs / symbol synonyms (checkable in one CPU pass: list adata.var columns for both files). Data-derived, not hand-curated.
 B. Otherwise an explicit, reviewed LABEL_ALIASES table per dataset (PERK->EIF2AK3, IRE1->ERN1, C3orf72->FOXL2NB, KIAA1804->MAP3K21, C19orf26->CBARP), each mapping asserted to hit exactly one vocab gene, recorded in provenance.label_aliases. Never fuzzy.
 Plus Gal4-4(mod) -> control, 3x -> excluded with reason (as in the first message).
Memory still unmeasured — both loaders refuse before allocation. I will not bypass the resolver to get the number.
next_handoff: cto rule label mapping (A or B)
