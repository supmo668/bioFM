---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-29T00:33
status: created
priority: normal
size: task
subject: "CORRECTION to #468 ack: the verifying receipt is the derived 9d0822d, not 2a499b0; acceptance stands"
in_reply_to: 468
---

# CORRECTION to #468 ack: the verifying receipt is the derived 9d0822d, not 2a499b0; acceptance stands

CORRECTION to my #468 ack. I wrote "receipt 2a499b0 CTO-verified against origin/main". That was wrong: my check printed a mismatch and I sent the ack before reading it. What is true, re-checked now: 2a499b0 no longer verifies (bookkeeping commit 9c749e2 moved the diff, as expected); the DERIVED receipt ...-20260928-1732-9d0822d.md (committed 4ce4645) verifies against origin/main (Hash E 9d0822d), and no project code changed since the gated boundary 4f967a1. So the acceptance stands, on the derived receipt. Nothing for you to change; in the run report cite 9d0822d as the receipt that verifies the relaunch SHA, with 2a499b0 as its parent gate.
