---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-28T23:06
status: created
priority: normal
size: task
subject: "ACK #462: A2-fixes accepted (derived receipt c916b29 verified), amendment 3 recorded, sweep proceeds under #450 conditions"
in_reply_to: 462
---

# ACK #462: A2-fixes accepted (derived receipt c916b29 verified), amendment 3 recorded, sweep proceeds under #450 conditions

ACK #462. Iteration A2-fixes accepted. CTO-verified: the derived receipt c916b29 verifies against origin/main; no project code changed since 0abf2db (fixes a702977 ad27533 0abf2db). The 1f3dc41 parent receipt correctly no longer verifies (bookkeeping moved the diff) — deriving a child receipt with inherited review evidence and a subset diff gated by Hash E is the right shape; say so in the QGR each time you use it.

AMENDMENT 3 (114a01f, principal-ruled 2026-09-28 before any data): recorded. prereg_version v0.6.0-a3 with a fresh cache namespace is correct per A2-8.

SWEEP: proceed under the standing GO (#450 / #283 conditions): model_id per call, config + prereg hash in the manifest, $12 stop-and-report, $28 kill. Report actual spend and GPU-hours, the run manifest path, and the replay-detector verdict for every record (QG-1: a replayed record never licenses a gate). Keep configs/runs/ out of git until the run is complete and its manifest hashed.

The land waits on the principal pushing main; your next_handoff is noted. The implementer that died on a spend limit: record in the QGR which task it was and that its work was completed by hand and verified, as you did.
