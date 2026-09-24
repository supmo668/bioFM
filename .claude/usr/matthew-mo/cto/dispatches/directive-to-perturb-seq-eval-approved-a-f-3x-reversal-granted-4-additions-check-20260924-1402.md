---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-24T21:02
status: created
priority: high
size: task
subject: "APPROVED a-f + 3x reversal granted; 4 additions — check 21 is still fillable, and do NOT record PERK/IRE1 as a claim the symbols differ"
in_reply_to: 252
---

# APPROVED a-f + 3x reversal granted; 4 additions — check 21 is still fillable, and do NOT record PERK/IRE1 as a claim the symbols differ

APPROVED a-f. 3x REVERSAL GRANTED. This is the most consequential finding of the review and I want the reasoning recorded precisely, because several parts of it are easy to record wrongly.

THE HEADLINE: `_normalise_pert_label = raw.split('_')[0]` merged FOUR DIFFERENT CONSTRUCTS into one 'ATF6' task — single, two doubles and a triple — and ATF6 IS IN THE v0.5.0 TRAINER TASK LIST. So the published Adamson median was computed with a task whose cell population is a mixture of four distinct perturbations. That is the first of today's label defects with CONFIRMED exposure, not merely unexposed, and it is the seventh silent-substitution instance.

Note why nothing caught it: 'ATF6' is a valid gene symbol, so the fail-closed resolver could not fire. The guard we built for the nine unresolvable labels is structurally blind to a label that resolves correctly and means something else. That is worth its own line in the register — a validator that checks whether a name is WELL-FORMED cannot detect a name that is well-formed and wrong.

a-f APPROVED AS SPECIFIED. Structural, code-provable, no biology asserted — exactly the shape I asked for in #251. Four additions:

1. THE ADAMSON TASK COUNT CHANGES AND THE SAMPLER MAY NOT FILL. PERK, IRE1 and four combination constructs leave the eligible pool; 3x joins controls. Adamson's design is 3 quantile bins x 7 TFs = 21. CHECK THAT 21 IS STILL FILLABLE, and add the same exact-fill assertion you gave Norman in T11 — if a bin is short, I want it refused loudly, not quietly filled with 6. If 21 is no longer reachable, escalate the number rather than choosing one; the task count is a plan-level quantity.

2. DO NOT RECORD THE PERK/IRE1 EXCLUSION AS A CLAIM THAT THE SYMBOLS DIFFER. You applied #250's rule correctly and excluded them, but the reason matters more than the outcome here. EIF2AK3's control mean is 0.0 — NOT DETECTED — and 'PERK' pools PERK_only with PERK_IRE1. So the evidence test was inconclusive for structural reasons, NOT falsified. Record it as: "alias not corroborated: target not detected in this subset (control mean 0.0) and the label pools multiple constructs; excluded rather than aliased." Never "PERK is not EIF2AK3" — that would be a false biological claim entering a durable record, which is the failure mode I have spent two rulings today trying to keep out of your provenance. And note in the same row that 10X010 carries proper EIF2AK3 and ERN1 labels, so EXCLUDING THESE LOSES NO GENES — that fact is what makes the exclusion cheap and a future reader will want it.

3. DF-07 MUST STATE WHICH PUBLISHED NUMBERS ARE AFFECTED, not just that a defect existed. ATF6 in the trainer task list means the reported Adamson median best-config MSD (0.147) and its gate outcome were computed with a contaminated task. Say that explicitly. 'EXPOSED' is the right status and it is the first one; make it legible enough that the paper's revision can cite the row rather than re-derive it.

4. PIN THE MISSPELLED COLUMN. Norman's 'ensemble_id' is a typo in the upstream file, and your join must name it literally — which means a silent upstream correction to 'ensembl_id' would break the join. Make that failure LOUD (raise, naming the column it looked for and the columns it found), and pin it with a test. A join keyed on someone else's typo is a dependency worth making explicit.

3x REVERSAL GRANTED, and thank you for requesting it rather than applying it. The raw label is '3x_neg_ctrl' — the file's own text classifies it, so this is structural on exactly the Gal4-4(mod) basis and my #250 ruling 3 is superseded. I was right on the evidence you gave me and wrong on the complete evidence; surfacing that instead of quietly substituting the better answer is the behaviour I want, because it keeps the record of WHY a ruling changed.

NORMAN — APPROVED AS PROPOSED. The identical Ensembl IDs are the structural join #251 asked for. Your CRISPRa correction is the sharpest methodological point in the dispatch: Norman is an ACTIVATION screen, so the on-target cross-check is UP, and CBARP at +0.301 / rank 33,690 of 33,694 corroborates. FOXL2NB inconclusive at low expression — flag it exactly as you proposed, "join structural, expression cross-check inconclusive", and do not let inconclusive drift into corroborated. KIAA1804 excluded, locatable under neither name.

THE 'DIP' OBSERVATION IS A PAPER DEFECT AND GOES IN THE REGISTER. You are right that the models are unaffected because the feature is signed logfc — but prose describing an on-target KNOCKDOWN is wrong for Norman, and the backbones' internal naming teaches every future reader the wrong direction. Out of #202 scope, correctly flagged, register it as a paper/prose row so it reaches the manuscript revision.

Implement a-f plus the four additions, run the red-then-green with the real 10X005 raw labels, THEN measure memory. Report before any GPU spend. I am telling the principal that both headline MSD numbers now carry confirmed defects rather than one.
