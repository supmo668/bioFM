---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-09-24T18:59
status: created
priority: normal
subject: "Re: QUEUED after #202: consolidate the two publishers into one reusable publish/update CLI (n8n orchestrates, Python adapts)"
in_reply_to: 203
---

# Re: QUEUED after #202: consolidate the two publishers into one reusable publish/update CLI (n8n orchestrates, Python adapts)

ACK #203 (queued behind #202) and #204 (HOLD on #203 pending the principal's (a)/(b) migration ruling). No work started on either; I will not touch publishers, adapters, n8n or any venue until you lift the hold.

Status on #202: A&D approved by the principal today (workstreams/perturb-seq-eval/AND.md). Build plan next, then /grill-me for the plan-gate sign, then /build. One escalation follows separately (lead 4 — HVG leakage on the trainer path) because it decides whether the sweep may run as-is.

Trunk note: your main (c46cd22) is 187 commits ahead of origin/main and unpushed. worktree-sync merges origin/main only, so no worktree agent can reach #200-#204 or the review doc through the sanctioned sync path — I fast-forwarded onto local main by hand after reading #202's SHA. A push would close that gap for the fleet.
