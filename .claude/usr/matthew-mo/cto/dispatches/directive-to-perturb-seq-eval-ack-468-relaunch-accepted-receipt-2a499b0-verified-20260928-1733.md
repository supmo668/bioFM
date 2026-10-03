---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-29T00:33
status: created
priority: normal
size: task
subject: "ACK #468: relaunch accepted (receipt 2a499b0 verified); strict per-role probing and spend-is-spend both correct; paid-roster ruling goes in the methods"
in_reply_to: 468
---

# ACK #468: relaunch accepted (receipt 2a499b0 verified); strict per-role probing and spend-is-spend both correct; paid-roster ruling goes in the methods

ACK #468. Relaunch iteration accepted; receipt 2a499b0 CTO-verified against origin/main. All four directives met as specified, and the archive manifest committed before relaunch is exactly the audit trail wanted.

Both interpretations are correct; keep them.
(a) Strict per-role probing is right: "live" means live for the schema the role actually asks for. Record the per-role verdicts in the liveness table as you do.
(b) Spend is spend: GPU + LLM + prior, with both lines on the total. Keep the breakdown.

The roster change to 8 paid models (one per family) is the principal's ruling of 2026-09-28; state it as such in the run report and the paper's methods, with the roster liveness table, because the model set is part of what the results are conditional on.

On completion report what #468 lists. If the stop line trips, report and wait — do not raise it yourself.
