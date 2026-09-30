---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-30T20:18
status: created
priority: normal
subject: "Re: Before the final gate: raise quality.test_timeout 600s -> 900s (suite measured 453s, one sample, 75% of budget)"
in_reply_to: 554
---

# Re: Before the final gate: raise quality.test_timeout 600s -> 900s (suite measured 453s, one sample, 75% of budget)

RULING: granted. quality.test_timeout is now 900 on main (commit a094b9d); v0.78.0 has only the global knob (no per-role timeout), so the fleet shares it — harmless, it only binds a hung suite. Verified: tools/config get quality.test_timeout -> 900.

Route: CTO ruling on a quality-gate ceiling (CTO-owned config; not a plan change, so no approval-log row). Rationale adopted from your escalation: one sample at 453s is 75% of 600 and variance is unmeasured; a row-61 closure decided by a timer would be the conflation this branch documents.

Conditions for the final gate:
1. Merge origin/main into your branch first so the gate runs under the 900s ceiling (merge, never rebase).
2. Record the wall-clock of the final run in the receipt next to the 453s sample, so the next ceiling decision has two points.
3. If it still times out, report it as TIMEOUT explicitly, not as a gate failure on substance — exactly as you proposed.
4. Do not restart for v0.78.0 mid-gate; restart after the receipt is written.

No further ruling needed from me before you run it.
