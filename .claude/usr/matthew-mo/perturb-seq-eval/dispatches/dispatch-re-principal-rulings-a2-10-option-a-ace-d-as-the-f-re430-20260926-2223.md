---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-09-27T05:23
status: created
priority: normal
subject: "Re: PRINCIPAL RULINGS A2-10 = option (a) ace_d as the feature; A2-11 = unclipped dC everywhere. Amendment 2 is UNBLOCKED to lock. Two consequences of (a) first: drop the now-resolved conditional, and re-point the F1-secondary N<=1 test at ace_d"
in_reply_to: 430
---

# Re: PRINCIPAL RULINGS A2-10 = option (a) ace_d as the feature; A2-11 = unclipped dC everywhere. Amendment 2 is UNBLOCKED to lock. Two consequences of (a) first: drop the now-resolved conditional, and re-point the F1-secondary N<=1 test at ace_d

Amendment 2 LOCKED: 3bf2a9a (prereg(perturb-seq-eval): AMENDMENT 2), prereg_version v0.6.0-a2. No v0.6.0 data exists.

Both #430 consequences applied:
1. A2-11: the conditional range sentence is dropped. TDI_lifecycle = 7/12 ACE + 5/12 (1-dC), unclipped, range
   [0, 17/12], stated once at the definition (nominal = attainable under ace_d).
2. A2-10: "undefined, not 0.0" re-pointed at ace_d. per_run_components must return None with a reason BEFORE
   ace_d is called when the final round has < 2 LLM-sourced steps (covers ace_d's N=0 raise and N=1 0.0) or its
   confidences sum to zero (covers ace_d's all-zero 0.0). Tests named for the fixes gate:
   test_one_llm_step_round_is_undefined_not_zero, test_zero_sum_confidence_round_is_undefined_not_zero
   (existing: test_fallback_only_final_round_is_undefined_not_imputed). Softmax ace_norm: one descriptive sentence only.

A2-9 recomputed under the lock (scripts/local/prereg_null_fwer.py --defs a2, seed 2026; evidence
qgr/evidence/h4-gate-null-fwer-a2.json.txt): identical 2.35%, reversed 4.71%, independent 5.84%; per-test
1.32% (n=20), 1.07% (n=21); pooled 0.0475%. Reversed extreme lies inside the bracket; intermediate negative
dependence not simulated, so the text says "range over the three arms", not a proven bound. DF-13's 6.15% not
reproduced. --defs a1 stays the default and reproduces amendment 1.

Fold: definitions and the FWER table edited inline; full ruled A2-1..A2-11 appended as the governing section;
results.tex H4 definitions + multiplicity aligned. The prereg_null_fwer.py change that the handoff hook flagged
as uncommitted is this --defs a2 work, now in 3bf2a9a.

Next: measurand fixes (ace_d feature, unclipped dC, no outer clip, undefined-before-ace_d + the two tests, other
ruled A2 items) through a quality gate, commit first then sign (#392); then the #283 sweep from the receipted SHA
on your GO.
next_handoff: cto ack
