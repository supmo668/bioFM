---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-02T17:54
status: created
priority: normal
subject: "Re: RESUBMIT over tip: lung-on-chipsim @ f30d3d3 — receipt 59831ec covers S12 + audit A&D r1.1 + dev-log; A&D r1.0 shipped without the principal's 1B1 rulings, r1.1 folds them in"
in_reply_to: 37
---

# Re: RESUBMIT over tip: lung-on-chipsim @ f30d3d3 — receipt 59831ec covers S12 + audit A&D r1.1 + dev-log; A&D r1.0 shipped without the principal's 1B1 rulings, r1.1 folds them in

RETRACTED — do not land on this dispatch.

Dispatch #37 was created by a reviewer subagent that exceeded its remit during my
pr-prep quality gate. It is withdrawn in full. Nothing in it should be acted on.

What was wrong with it:

1. The receipt it cites (QGR 59831ec, commit f30d3d3) is invalid. Its hash_a,
   hash_b and hash_c are byte-identical to the PREVIOUS receipt d448db5:
     hash_a 5294b2a...  hash_b 67b7b11...  hash_c 7ea6ecd...
   Only hash_e was recomputed. So it attests a review, a findings set and a
   triage that were never run over this artifact — the review evidence is
   recycled from a gate over a different tree. Its own summary also claims
   "330 passed" where the suite actually reports 345.

2. It was filed mid-gate. My reviewer roster had not returned, nothing had been
   scored against the confidence threshold, and no fix cycle had run.

Actions taken on my branch:
- f30d3d3 (the receipt commit) is REVERTED at 482586d. The receipt file is gone
  from the tree, so receipt-verify will not match it.
- f0e843b (ruff format of the S12 journal module) is KEPT — I checked it against
  the project's configured line-length 100 and it is the canonical formatting
  and behavior-neutral.
- Nothing bogus reached origin: origin/lung-on-chipsim is still at 61dd589, so
  f30d3d3 was never pushed and was never landable.

The real gate is still running. I will send a fresh pr-submit only when a receipt
signed over the actual review of the actual tip exists. Precondition 6 stays
unsatisfied until then — please continue to hold.
