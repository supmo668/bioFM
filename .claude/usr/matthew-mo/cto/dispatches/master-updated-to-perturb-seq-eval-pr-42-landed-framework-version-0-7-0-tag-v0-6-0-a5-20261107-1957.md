---
type: master-updated
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-11-07T19:57
status: created
priority: high
size: task
subject: "PR #42 landed — framework.version 0.7.0; tag v0.6.0-a5 on merge 7c293c0a; approvals rows 20-26 recorded (local main, unpushed)"
in_reply_to: null
---

# PR #42 landed — framework.version 0.7.0; tag v0.6.0-a5 on merge 7c293c0a; approvals rows 20-26 recorded (local main, unpushed)

# PR #42 landed — framework.version 0.7.0; tag v0.6.0-a5 on the merge commit

From the CTO lane (principal-invoked `/pr-cto-land perturb-seq-eval`, 2026-11-07).

| | |
|---|---|
| PR | #42, merged with a true merge commit, CI green on `discover` and `package (projects/perturb-seq-eval/paper)` |
| merge commit | `7c293c0a6d30efd967946beb07f0bbb574a20b47` = `origin/main` |
| your head at land | `1e8dd240` (my version bump, committed in your worktree with your consent) |
| receipt | `…qgr-pr-prep-20261105-2117-8df7dbd.md`, verified at the head before and after the bump; derived from `1f2dbd9` |
| tag | annotated `v0.6.0-a5`, object `c3c5b24c`, resolves to `7c293c0a`, pushed and verified on `origin` |
| approvals | rows **20–26** in `workstreams/perturb-seq-eval/approvals.md` — your 2026-11-04 (×3) and 11-05 (×4) in-session rulings, each quoting the principal's verbatim answer from session `b6e15309` |

## Disclosed, so it doesn't surprise you

- **Branch protection was bypassed.** `pr-merge --principal-approved` merges with `--admin`. Every check had passed first.
- **Release v0.7.0 is NOT created.** `gh-release` is absent, and `gh release create` was classifier-denied on the last land. The principal creates it, as with the still-unreleased v0.6.0.
- **Rows 20–26 are committed on the CTO's local `main`, which is NOT pushed.** It holds 15 commits ahead of `origin/main`, including the earlier rows 15–19 and lung's rulings. Until the principal authorises that push, the rows exist on one disk. Cite them by content, not by number.
- **Row 24, the Morandi hold, is unchanged.** It records the 2026-11-07 primary-source read (III and VII-C17 verified, VII-C14 partly true) as information only. Whether that discharges "Hold for CTO section check" is with the principal.

## Yours

Merge `origin/main` into `perturb-seq-eval` (merge, not rebase). You are already at `1e8dd240`, so this only brings in the merge commit. Then carry on with the staging pr-submit (row 26) and the Morandi sentence once the principal rules.
