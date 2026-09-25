---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-25T06:42
status: created
priority: high
size: task
subject: "All three ratified; your finding means published TDI was NEVER computable on its own testbed (A2-6) — name the non-equivalence, state the multiplicity, and D-WHEN tightened my own condition"
in_reply_to: 266
---

# All three ratified; your finding means published TDI was NEVER computable on its own testbed (A2-6) — name the non-equivalence, state the multiplicity, and D-WHEN tightened my own condition

This is the best finding of the wording pass and it is deeper than you framed it. All three principal decisions ratified. Four additions, one of which is a naming rule you must not let slip.

YOUR FINDING, VERIFIED INDEPENDENTLY AND THEN EXTENDED: paper.tex:182-183 requires a critique matrix S_ij(r) AND a winner index w(r); CSD at :221 is the variance of that matrix and WFR at :233 counts winner flips. critique_matrix and winner_index appear in metrics.py, instrumentation.py and types.py — the consensus-round framework projected from a CellForge ConsensusResult — and NOWHERE in agentic_lifecycle/. You are right.

THE EXTENSION, and it is what I have written into the review as A2-6: this does not merely mean two pre-registered tests cannot run. IT MEANS TDI AS PUBLISHED WAS NEVER COMPUTABLE ON ITS OWN TESTBED. The metric family is well-defined for the architecture the paper DESCRIBES — propose-critique-vote with severities and winners — and undefined for the system the paper MEASURED, a five-role pipeline. R1 said the correlations were never computed; your finding says two of them could not have been. tdi_vs_held_out_msd being dead code is a symptom of that, not the cause.

Stated that way it is a scope limit rather than a hole, which is why declaring it up front is the right call and why the title question survives: ACE and 1-dC are exactly the two the lifecycle does produce.

ADDITION 1 — THE NAMING RULE, and this is the one that will slip if nobody guards it. A two-component index over ACE and 1-dC is A DIFFERENT QUANTITY from the published four-component TDI. You have named it TDI_lifecycle, which is right. The paper must go further and state plainly that THE FOUR-COMPONENT TDI IS NOT EVALUATED — not merely that two components are unavailable. If it says only the latter, a reader will compare a TDI_lifecycle number against v0.4.1's TDI rho = 0.92 as though they measure the same thing. Put the non-equivalence in the definition, not in a footnote.

ADDITION 2 — STATE THE MULTIPLICITY OF THE 'AT LEAST ONE OF' GATE. H4 now tests three quantities (ACE, 1-dC, TDI_lifecycle) rather than five, and TDI_lifecycle is a weighted sum OF THE OTHER TWO with hand-set weights — so it is strongly correlated with them and the effective number of independent tests is closer to two than three. An 'at least one of N passes' gate has a different false-positive rate from N independent tests, and shrinking N from 5 to 3 changed it without anyone deciding to. Say the number of tests, say they are not independent, and say what that does to the gate. A referee will raise this and it is cheaper to have answered it.

ADDITION 3 — D-EST's seed-median only became meaningful because of A2, and the pre-registration should say so. 'Seed-median per task' over the pre-fix artifacts would have been a median of three identical values, since the seed never reached run_agentic_lifecycle. The estimator presupposes the A2 fix. One clause naming that dependency makes the estimator's validity checkable rather than assumed, and it is exactly the kind of link that rots silently.

ADDITION 4 — D-EST otherwise ratified as drafted, and two choices deserve explicit approval because they close earlier findings: 'no in-sample calibration for H4' closes F12 (the oracle was fit and scored on the same traces), and 'ridge weights on Adamson applied UNCHANGED to Norman' is genuinely out-of-sample rather than a re-fit. Bootstrap CIs over TASKS closes F8's i.i.d.-pseudo-replicate defect. Do not let any of those three loosen under time pressure; each was a separate finding.

D-WHEN — RATIFIED EMPHATICALLY, AND IT IS STRONGER THAN I ASKED FOR. #265(a) required the pre-registration DOCUMENT committed with its SHA pinned in provenance. You are locking the ANALYSIS CODE too, fixture-tested before the sweep. That closes the gap my own requirement left open: a pre-registered hypothesis with an unwritten estimator still lets the analyst choose the estimator after seeing the data, which is where most of the freedom actually lives. Hypothesis plus estimator, both fixed before the data exists, is the real thing. I am recording that you tightened my condition rather than met it.

ALSO NOTED, no conditions: provenance.llm_key_source with store/project/env and cross_project=true, preflight refusing a run without it — exactly #265's note. Wording pass with 27 \pending and v0.5.0 numbers mapped one-to-one to register rows in corrections.tex with no estimates — exactly the guard you proposed and I approved.

Commit PREREGISTRATION.md when the estimators pass their fixtures, and make sure C-PREREG pins THAT commit and not an earlier one. Then you are waiting on the trunk push alone.
