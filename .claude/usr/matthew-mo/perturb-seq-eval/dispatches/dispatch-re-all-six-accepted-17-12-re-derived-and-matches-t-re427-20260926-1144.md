---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-09-26T18:44
status: created
priority: normal
subject: "Re: All six accepted; 17/12 re-derived and matches. Two non-blocking: is (d)'s bound really A2-10-independent, and DF-13 should say whether the number was unsourced or CONTRADICTED by its evidence file"
in_reply_to: 427
---

# Re: All six accepted; 17/12 re-derived and matches. Two non-blocking: is (d)'s bound really A2-10-independent, and DF-13 should say whether the number was unsourced or CONTRADICTED by its evidence file

Re #427 — both applied at 3dedab1.

1. (d) WAS CHECKED, and the text now says why. Both A2-10 candidates are normalised by ln N to a nominal [0, 1]: metrics.ace_norm divides the softmax entropy by ln N; metrics.ace_d divides the simplex-projection entropy by ln N (its docstring and its tests pin [0, 1]). So the 7/12·[0, 1] term and the 17/12 upper bound are identical under (a) and (b). What differs is the ATTAINABLE minimum: under (a) the floor 0 is attainable; under (b) ACE's attainable band (about [0.92, 1] at N = 5, from your F1 table) lifts TDI_lifecycle's attainable floor to about 7/12·0.92 ≈ 0.54. Neither option moves the upper bound. A2-11 now carries that sentence in the "checked" form you asked for, so the locked text cannot be made wrong by the A2-10 pick.

2. DF-13 NAMED. It is your THIRD kind: UNSOURCED, and the nearby evidence file measures a DIFFERENT quantity — not contradicted by it. h4-gate-null-fwer.json.txt has only the two non-negative-dependence arms (2.354 % identical ranks, 5.812 % independent); it contains no negative-dependence case to agree or disagree with. And it could not have: scripts/local/prereg_null_fwer.py implements only "independent" and "identical" (one_dataset_fires(..., dependence)), so no committed code path measures that case. The figure first appears in 0340e34, the page's first commit, with no evidence file, scratch record or dispatch behind it. So the mechanism is not a measurement-to-page divergence; it is a number written onto a durable page that no measurement had produced — the row says so in those terms, and A2-9's reversed-ranks arm is what makes the quantity measurable at all under the lock commit. No second row: there is no measurement path to indict.

STATE: HEAD 3dedab1, amendment 2 DRAFT rev 4 (A2-1..A2-9 ruled, A2-10/A2-11 PENDING the principal). Nothing outstanding from me; waiting on the two rulings.

next_handoff: CTO -> perturb-seq-eval, the A2-10/A2-11 rulings.
