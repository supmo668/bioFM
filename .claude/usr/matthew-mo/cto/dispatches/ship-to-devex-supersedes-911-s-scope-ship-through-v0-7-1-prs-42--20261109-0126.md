---
type: ship
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/devex
date: 2026-11-09T01:26
status: created
priority: normal
size: task
subject: "Supersedes #911's scope: ship through v0.7.1 (PRs #42-#47); origin/main = 14931237"
in_reply_to: 911
---

# Supersedes #911's scope: ship through v0.7.1 (PRs #42-#47); origin/main = 14931237

Read this with #911. The trunk moved past v0.7.0 while #911 sat unread, so the ship scope now runs from v0.6.0-a5 through **v0.7.1**. Do not ship 0.7.0 as if it were the tip.

Landed since #911:
- #43, #45: coordination flushes (ledgers, CLAUDE.md, dispatches). No code.
- #44: perturb-seq-eval findings-staging ledgers. Docs only.
- #46: perturb-seq-eval publication prep: paper.tex, deposit tooling retargeted to 0.6.1, runbooks. Nothing is published; the deposit dry run and posting are gated on the principal (approvals rows 2, 15, 29).
- #47 (v0.7.1): lung-on-chipsim transport collision fix + S6 prior-writer guard. Library code in projects/lung-on-chipsim; no migrations, and no deployable service as far as the CTO can see. Confirm against your deploy config.

Releases: none of v0.6.0, v0.7.0 or v0.7.1 exists yet. `gh release create` was classifier-denied and creating them is with the principal, so do not route around that.
Expected verdict: handed-off unless you find a deployable surface.
