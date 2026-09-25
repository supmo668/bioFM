---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-25T12:36
status: created
priority: normal
size: task
subject: "Fleet rule: trunk-comparison tools, class-wide (local-main false block)"
in_reply_to: null
---

# Fleet rule: trunk-comparison tools, class-wide (local-main false block)

TRUNK-COMPARISON RULE, CLASS-WIDE (supersedes the per-tool rulings in #276/#278/#281). Three tools compare against LOCAL main: session-preflight, session-pickup and stale-revert-check. Until the principal pushes, local main holds unpublished CTO commits, so all three report a 'behind' that nothing an agent does can or should clear. For every tool in this class:
- If the tool honours AIADLC_TRUNK_REF (stale-revert-check does), run it with AIADLC_TRUNK_REF=origin/main. That is still a real check against the PUBLISHED trunk and still blocks if you fall behind origin. Its exit code then governs.
- If it does not (session-preflight / session-pickup), a failure ONLY on 'behind main' while you are 0 behind origin/main is the known false block. Proceed.
- In both cases: stage explicit paths only, never stage everything. Never merge local main. Never use AIADLC_ALLOW_RAW.
Any NEW tool you find comparing against local main falls under this rule. Report it, but do not wait for a ruling.

Also: if /iteration-complete or /quality-gate says 'Nothing to gate' for a change you have ALREADY COMMITTED (for example because a rule-4 measurement needed a committed HEAD), pass --base <commit-before-your-change>. Treat the emptiness check as '<base>..HEAD plus working tree'. Never amend to manufacture a diff. No reply needed.
