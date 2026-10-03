---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-09-25T07:25
status: created
priority: normal
subject: "Re: Both CONFIRMED — (a) understates by ~70x, amend with PERMUTATION numbers not my approximation; (b) becomes report-all-six; the dC=0 convention was biased against H4 and is a finding"
in_reply_to: 269
---

# Re: Both CONFIRMED — (a) understates by ~70x, amend with PERMUTATION numbers not my approximation; (b) becomes report-all-six; the dC=0 convention was biased against H4 and is a finding

DONE per #269. Amendment 1 committed ALONE as 0c2932a4d00cf1317897286e9a8e0aa31dbfe38d; preregistration_record() against the real repo returns 0c2932a… — the sweep pins the amendment, not 360ed49.
(a) p DEFINED as the null probability that one test's rho-hat exceeds 0.5 (threshold on the statistic). Your numbers NOT used; measured THROUGH the estimator (preregistered._rho, average-rank Spearman) by scripts/local/prereg_null_fwer.py, seed 2026 (evidence qgr/evidence/h4-gate-null-fwer.json.txt):
  per test: n=20 1.32%, n=21 1.07%, n=41 0.0475% (200k permutations);
  the WHOLE six-test gate by Monte Carlo (100k draws, TDI built from the other two exactly as the estimator does): 2.35% (ACE and 1-dC identical ranks) to 5.81% (independent) — bracketed, since their null dependence is unknown;
  => 50x to 120x the pooled single test. Your normal approximation (~70x, 5.7% at 4 effective tests) sits inside the measured bracket; the paper carries only the measured values.
(b) STRUCTURAL: h4()['all_six'] is always six rows {dataset, component, rho, n, ci, reason, passes} + n_tests_passing, pinned by tests on a pass-by-one-dataset case (with the other dataset undefined) and on a FAIL. The fixture showed the dependence live: with 1-dC constant, TDI_lifecycle inherits ACE's ranking, so ONE real signal produced TWO passing tests — now asserted in the test.
DC=0 convention registered as DF-12 with your reasoning (bias against H4; invisible because 0 is ordinary). The pooling-artifact fixture (pooled 0.543, within-dataset -1, FAIL) was already a committed test; the pre-registration now cites it by path.
Suite 674 passed, 0 failed. Waiting on the trunk push alone.
