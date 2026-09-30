---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-09-25T07:18
status: created
priority: high
size: task
subject: "Pre-registration committed as 360ed49 (hypotheses + estimators locked); C-PREREG verified to pin it — 2 sentences need your confirmation"
in_reply_to: null
---

# Pre-registration committed as 360ed49 (hypotheses + estimators locked); C-PREREG verified to pin it — 2 sentences need your confirmation

Agent: perturb-seq-eval
DONE per #265/#267:
- Estimator code locked FIRST (preceding commit): experiments/preregistered.py, 672 passed / 0 failed.
- PREREGISTRATION.md + matching results.tex/experimental_setup.tex committed ALONE as 360ed49f5f51ed378c9b5a938474c9fc00f1a8d1. preregistration_record() run against the real repo returns commit=360ed49… (verified, not assumed). Merge-only branch, so the SHA survives the post-push sync; it moves only if the file is edited (which would be a visible, dated amendment).
- All four #267 additions are in the text: four-component TDI NOT evaluated and never computable on this testbed (A2-6) stated in the definition; multiplicity; seed-median presupposes A2; F12 / out-of-sample H5 / F8 named.

TWO FURTHER PRINCIPAL RULINGS (direct, 2026-09-24/25) that changed the text after #267:
 1. Single-round runs: 1-dC and TDI_lifecycle UNDEFINED (excluded, counted) — metrics.py's dC=0 convention would have scored immediate convergence (easy tasks) as maximal difficulty, a built-in bias against H4.
 2. H4 per dataset: within Adamson (n=21) and within Norman (n=20); gate passes if ANY of 6 tests passes; pooled 41-task rho descriptive only (a pooled rho can be driven by the between-dataset difference with no within-dataset signal — demonstrated by a fixture: pooled 0.543, every within-dataset rho -1, gate FAIL).

PLEASE CONFIRM two sentences the implementer wrote and I committed (conservative, but not ratified by anyone yet): (a) 'effective number of tests ~4, at most 6; false-positive rate ~1-(1-p)^4, higher than pooled because p is larger at n~20'; (b) 'a PASS driven by a single one of the six tests must be described as such'. If either is wrong, the fix is an amendment commit BEFORE the sweep, and C-PREREG will pin the amendment.
Waiting only on the trunk push.
