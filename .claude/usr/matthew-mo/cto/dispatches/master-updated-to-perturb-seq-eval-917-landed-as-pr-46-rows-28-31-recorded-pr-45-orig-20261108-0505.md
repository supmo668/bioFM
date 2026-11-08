---
type: master-updated
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-11-08T05:05
status: created
priority: high
size: task
subject: "#917 landed as PR #46; rows 28-31 recorded (PR #45); origin/main = 6e048b3b"
in_reply_to: 917
---

# #917 landed as PR #46; rows 28-31 recorded (PR #45); origin/main = 6e048b3b

Rows 28–31 are recorded. I verified each one against your session's harness-recorded AskUserQuestion answers (04:34:32Z and 04:46:37Z), and the (b″) text matches the ruled option word for word. They landed in coordination PR #45.

#917 is PR #46 from origin/perturb-seq-eval @ aeaae2fa, no bump. CI passed (discover, package). It merged under normal protection, with no --admin. The principal approved both merges in the CTO session.

Your local 1aea6eab (the pr-submit dispatch, unpushed) was NOT in the PR. pr-create read it as HEAD and the receipt check failed (the known pr-submit-invalidates-receipt defect), so I opened the PR with gh pr create --head at the pushed, gated SHA. Merge origin/main and push.

Nothing is published. The principal's steps remain: the TechRxiv terms read, the infisical dry run for 0.6.1 followed by a separate go, the TechRxiv post, and Scholar/ORCID/OpenAlex.
