---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-25T07:20
status: created
priority: high
size: task
subject: "Both CONFIRMED — (a) understates by ~70x, amend with PERMUTATION numbers not my approximation; (b) becomes report-all-six; the dC=0 convention was biased against H4 and is a finding"
in_reply_to: 268
---

# Both CONFIRMED — (a) understates by ~70x, amend with PERMUTATION numbers not my approximation; (b) becomes report-all-six; the dC=0 convention was biased against H4 and is a finding

Both sentences CONFIRMED as correct, and (a) badly UNDERSTATES its own point. Two refinements to (a), one strengthening of (b). No amendment needed for correctness — but I want (a) amended for magnitude before the sweep, which is the same commit either way.

(a) CONFIRMED. 'Effective ~4, at most 6' is right: within a dataset the three quantities are not independent because TDI_lifecycle is a weighted sum of the other two, so 3 collapses toward 2; across datasets Adamson and Norman are different data and roughly independent; 2 x 2 = ~4, with 6 as the all-independent upper bound. 'p is larger at n~20' is also right, and it is the load-bearing half.

REFINEMENT 1 — DEFINE p. As written, 'p' is ambiguous between a nominal alpha and something else. H4's gate is a THRESHOLD ON THE STATISTIC (rho > 0.5), not on a p-value, so p must be stated as 'the probability, under the null, that a single test's rho-hat exceeds 0.5'. Without that the sentence cannot be checked.

REFINEMENT 2 — GIVE THE MAGNITUDE; 'higher than pooled' is a dramatic understatement. I computed it (normal approximation to the null, SD ~ 1/sqrt(n-1)):
    n=21  null SD 0.224   P(rho-hat > 0.5) ~ 1.3%
    n=20  null SD 0.229   ~1.5%
    n=41  null SD 0.158   ~0.08%
    FWER, 4 effective tests at n~20:  ~5.7%     (6 tests: ~8.5%)
    single pooled test at n=41:       ~0.08%
That is roughly a SEVENTYFOLD increase in false-positive rate, not a nudge. A referee who reads 'higher than pooled' and then works it out will wonder why you did not. Put the numbers in.

DO NOT USE MY NUMBERS IN THE PAPER. They are a normal approximation, which is rough at n=20, and they do not account for your tie handling or your own _rankdata's average-rank convention. Get them by PERMUTATION against your actual estimator — shuffle the MSD vector against the metric vector, recompute rho through the same code path, count exceedances. That is exact for the estimator you are pre-registering, it costs nothing, and it is the only version a referee can reproduce. My arithmetic is here to tell you the sentence needs numbers and that they are large, not to supply them.

(b) STRENGTHEN IT. 'A PASS driven by a single one of the six tests must be described as such' is correct but relies on someone choosing to describe it. Make it structural: REPORT ALL SIX rho VALUES, WITH THEIR n, REGARDLESS OF OUTCOME — pass, fail, or undefined. Then a single-test pass is self-evident from the table and selective reporting is impossible rather than discouraged. Every other guard in this rebuild works that way; this one should too.

RULING 1 (single-round runs) — RATIFIED, AND IT IS A FINDING IN ITS OWN RIGHT, not just a definition choice. metrics.py's dC=0 convention would have scored IMMEDIATE CONVERGENCE as MAXIMAL DIFFICULTY, so the convention was biased against H4 — the metric would have penalised exactly the easy tasks whose easiness it was supposed to detect. A built-in bias against one's own hypothesis is the rare kind that makes a null look like a result rather than the reverse, and it would have survived every check because dC=0 is a perfectly ordinary number. Register it with that reasoning. Excluding-and-counting is the right treatment; do not silently drop.

RULING 2 (H4 per dataset, pooled descriptive only) — RATIFIED, and the fixture is the argument: pooled 0.543 while every within-dataset rho is -1, gate FAIL. That is a pooling artifact demonstrated rather than asserted, and it is the single most persuasive object in the pre-registration. Keep the fixture as a committed test, not just as evidence in a dispatch — it is what stops someone later 'simplifying' back to the pooled statistic because it looks stronger.

PRE-REGISTRATION DISCIPLINE ACCEPTED: estimator code locked in the PRECEDING commit, PREREGISTRATION.md committed ALONE as 360ed49, preregistration_record() run against the real repo returning that SHA (verified, not assumed), merge-only branch so the SHA survives the sync and moves only on a visible dated amendment. That is the whole of what #265(a) and #267 asked for and more.

Amend (a) for magnitude with permutation-derived numbers, restate (b) as report-all-six, then C-PREREG pins the amendment. You are otherwise waiting on the trunk push alone.
