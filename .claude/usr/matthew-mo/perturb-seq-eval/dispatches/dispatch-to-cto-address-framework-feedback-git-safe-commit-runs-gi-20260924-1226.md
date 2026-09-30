---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-09-24T19:26
status: created
priority: normal
size: task
subject: "Address framework feedback: git-safe-commit runs git add -A, so /coord-commit sweeps implementation WIP into misc: commits"
in_reply_to: null
---

# Address framework feedback: git-safe-commit runs git add -A, so /coord-commit sweeps implementation WIP into misc: commits

Logged at .claude/aiadlc-feedback/2026-09-24-git-safe-commit-sweeps-worktree-despite-coord-commit-staging.md. Proven: tools/git-safe-commit:325-328 runs 'git add -A' unless --staged; skills/coord-commit step 8 never passes --staged. Hit today: 84a8602 (misc: coord commit) carries T0's pyproject/app_v05.py pins + untracked baseline.md from a concurrent implementer. Fix: coord-commit passes --staged; better, invert the default and refuse non-allowlisted paths in --no-work-item mode. Plugin source: /Users/mo/github/aiadlc. Mitigation: those files fall in the P1 iteration range and get QG-reviewed there; I pass --staged on every coord-commit from now.
