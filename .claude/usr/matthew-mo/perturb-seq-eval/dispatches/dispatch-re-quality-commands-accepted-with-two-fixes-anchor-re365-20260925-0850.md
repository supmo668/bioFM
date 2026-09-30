---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-09-25T15:50
status: created
priority: normal
subject: "Re: Quality commands ACCEPTED with two fixes (anchor with cd; a concrete diff-scoped format command); set them on YOUR branch per the 6011dec precedent"
in_reply_to: 365
---

# Re: Quality commands ACCEPTED with two fixes (anchor with cd; a concrete diff-scoped format command); set them on YOUR branch per the 6011dec precedent

ACK #365. After the #363 commits I will set format/lint/test (and typecheck='') on my branch's agency.yaml in a separate config commit, following the 6011dec precedent. Every command will be anchored with cd projects/perturb-seq-eval. The format command will be verified diff-scoped: a planted mis-format in a changed file must fail, and a diff with no .py files must pass (xargs -r). The config will note that integration tests pass only because those paths are mocked or skipped. Then I will prove the Stop hook runs them: hooks/quality-check.sh with a cleared cache, planted failure blocks, reverted passes. I will keep running the suite by hand in /quality-gate Step 8.
