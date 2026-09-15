---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-15T09:40
status: created
priority: normal
size: task
subject: "Address framework feedback: /iteration-complete — dispatch type rejected, ITERATION- work-item rejected, diff-hash scopes QGR docs (3 findings, eafe558)"
in_reply_to: null
---

# Address framework feedback: /iteration-complete — dispatch type rejected, ITERATION- work-item rejected, diff-hash scopes QGR docs (3 findings, eafe558)

Plugin feedback logged at .claude/aiadlc-feedback/2026-09-15-iteration-complete-dispatch-type-workitem-format-receipt-scope.md (commit eafe558). plugin.source_path is set (/Users/mo/github/aiadlc), so per /feedback this is dispatched for action rather than only logged.

Three findings, each with the failing invocation, proven root cause and a one-line fix:
1. tools/dispatch VALID_TYPES lacks 'iteration-complete'/'phase-complete' that skills/iteration-complete Step 8 prescribes → add them (or change the skill to --type dispatch + event:). I sent #109 as type 'dispatch'.
2. git-safe-commit rejects 'ITERATION-<ws>-<id>' — the skill's own Step 4 example — accepting only TASK/BUG/REQUEST → widen the validator (ITERATION-/PHASE-/PLAN-) or fix the example. Side effect worth a loud message: a rejected boundary commit leaves the index staged, and the next --staged commit sweeps it up (that is how my unshared cb85903 happened).
3. diff-hash scopes plan/quality-gate-reports.md, dev-log.md and .claude/workstreams/*/context.json (measured: E 2e1937e/10 files → 2b3623f/13 files once they are committed), so receipt-verify reports 'none match current code' for any landed boundary commit that carries its QGR report — verification only ever passes at commit time. Exclude coordination artifacts from diff-hash, or recompute E at <boundary>^ when verifying a commit; and reconcile the reference's Proposed Commit file list with the skill's commit-then-update order.

Fix there (edit tool/hook/skill → test → /cto-release), then reply. No action needed from me; the durable record is the feedback file.
next_handoff: cto — ack or route to the plugin maintainer
