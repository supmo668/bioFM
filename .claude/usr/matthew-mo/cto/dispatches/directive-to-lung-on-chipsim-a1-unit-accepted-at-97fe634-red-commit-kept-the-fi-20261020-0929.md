---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-10-20T08:29
status: created
priority: normal
size: task
subject: "A1 unit ACCEPTED at 97fe634, red commit KEPT. The five divergent modules go to per-file reconciliation folded in with transport/, adjudication.py FIRST because D6 depends on it. A1's text needs amending like A2's. Your sha256 reasoning was right."
in_reply_to: null
---

# A1 unit ACCEPTED at 97fe634, red commit KEPT. The five divergent modules go to per-file reconciliation folded in with transport/, adjudication.py FIRST because D6 depends on it. A1's text needs amending like A2's. Your sha256 reasoning was right.

Both ruled (approvals row 25). I verified every load-bearing claim rather than relaying it.

THE UNIT STANDS. Verified: 41 additions / 0 modifications - nothing overwritten - and the arithmetic closes exactly, 41 + 24 + 6 = 71 = your measured gap.

YOUR sha256 CALL WAS RIGHT AND THE REASONING IS THE PART THAT MATTERS. No parquet is tracked, so drugbank_compounds.sha256 is a standalone ORACLE, and regenerating it from the pipeline that writes the artifact would make the check SELF-FULFILLING - a verification derived from the thing it verifies. That is the project's own vector and you named it. I asked you to flag rather than guess and you did better: you dispositioned it with an argument that settles it.

RED COMMIT KEPT AS-IS. The red is caused entirely by the unreconciled divergent modules and you named the cause in the commit message. Keeping it makes the cause auditable; reverting would hide a true state and re-do verified work. Do not revert.

THE FIVE DIVERGENT MODULES: per-file reconciliation, FOLDED IN WITH transport/, so theta.py is decided once rather than twice. I verified all five divergent by blob - ids.py 7aa90a6/d6f6850, adjudication.py 976795c/83a473c, drugbank_snapshot.py c028fa7/1f398eb, theta.py 38097c4/d57e0f6, roster.py 47eb346/cb06ddb.

TAKE adjudication.py FIRST. D6 depends on it and nothing can be typed until it resolves.

YOUR DIAGNOSIS IS ACCEPTED AND RECORDED: A1 ASSUMES THE GAP IS PRESENCE-VS-ABSENCE AND IT IS NOT. That is A2's defect one level deeper, and A1's text needs amending the way A2's does - both are now flagged for the principal together. roster.py is the sharpest case and you are right about why: A1 NAMES IT FOR TRANSFER while it is divergent, so a manifest-built unit would have copied Stage 1's roster.py over live Stage 2 work. Your own framing - that you escaped it because you built from 'absent on HEAD' so divergent files were excluded as a PROPERTY OF THE METHOD, not by foresight - is the honest account and it is in the record as luck with good manners, again.

ON D6, AND THIS IS THE ONE WITH CONSEQUENCES OUTSIDE THE REPO. I verified your finding: export_tracked_adjudication 6 occurrences on the Stage 1 lineage and ZERO on HEAD, TRACKED_COLUMNS 11/0, EXPORT_DROPPED_COLUMNS 2/0, and zero definitions of the export function on HEAD. So the protection the principal APPROVED is not present where the verdicts will be typed. I have told them in those terms. D6's substance still holds for Stage 1's code; what failed is the applicability you asserted - and the window is open only because nothing can be typed yet, which is luck rather than design. You called it your third ref-in-hand error and that is the correct count; what matters more is that you measured it and reported it before any verdict existed to lose.

NEXT, IN ORDER:
1. Reconcile adjudication.py per-file. Report the diff shape - what each side has that the other does not - and STOP for the principal's call. Do not merge either direction on your own authority; both sides are live work.
2. Then ids.py, drugbank_snapshot.py, roster.py.
3. Then transport/ - ode.py and fit.py are Stage-1-only ADDITIONS, prior.py and theta.py are divergent, sourcing.py is Stage-2-only. theta.py is decided in this same pass.
4. When you report, state A2 AND A1 together for the principal: A2's 'only copy' clause is half false, and A1's presence-vs-absence assumption is wrong. Both need restating or retiring before the per-file calls are settled.
5. Suite stays red until the reconciliations land. Do not paper over it; do not push.

One housekeeping note so you do not chase it: #687 is parked to perturb-seq-eval, which concluded and self-retired. That recipient deliberately no longer exists, so the dispatch is undeliverable and harmless - nothing is waiting on it.
