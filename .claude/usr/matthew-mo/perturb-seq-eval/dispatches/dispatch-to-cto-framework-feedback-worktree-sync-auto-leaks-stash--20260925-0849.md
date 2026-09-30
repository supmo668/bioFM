---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-09-25T15:49
status: created
priority: normal
size: task
subject: "Framework feedback: worktree-sync --auto leaks stash entries on the shared stack (+ preflight compares local main)"
in_reply_to: null
---

# Framework feedback: worktree-sync --auto leaks stash entries on the shared stack (+ preflight compares local main)

Framework feedback for the plugin source (/Users/mo/github/aiadlc). Full entry: .claude/aiadlc-feedback/2026-09-25-worktree-sync-stash-leak.md in the perturb-seq-eval worktree. Not committed yet: #351 said not to commit, and the 09-24 feedback reports git-safe-commit sweeping a dirty worktree.

1 (blocking): tools/worktree-sync --auto runs a bare `git stash` and captures STASH_REF as a commit SHA. It then runs `git stash apply <SHA>` (works) and `git stash drop <SHA> || true` (fails silently: "is not a stash reference", rc=1; reproduced in a throwaway repo, while dropping by stash@{0} gives rc=0). So every dirty-tree auto-sync leaks one entry onto the SHARED stack. It made my stash@{0} and is likely behind the 12 "WIP on lung-on-chipsim" entries. Fix: `git stash push -u -m <unique-tag>`, re-find the entry's stash@{n} by tag before dropping, and remove `|| true`, or use a WIP commit instead of a stash.
2 (friction): session-preflight and session-pickup compare against LOCAL main, which produces the #309 false block. Make them honour ${AIADLC_TRUNK_REF:-origin/<trunk>}.
Please route this to whoever maintains the plugin source. Fix there, test, ship with /cto-release, then reply.
