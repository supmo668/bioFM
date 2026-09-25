---
type: plugin-feedback
target: aiadlc plugin (bioFM)
plugin_version: 0.60.0
reporter: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-25
scope: plugin / operating-system behavior — NOT repo/app work
---

## 🔴 1. worktree-sync --auto leaks one entry onto the SHARED stash stack on every dirty-tree sync
**File:** tools/worktree-sync (~L151-156 stash; ~L216-217 and ~L276-277 apply/drop)
**Symptom:** Running `/session-resume` (session-pickup --from fresh → worktree-sync --auto) in perturb-seq-eval at 08:43:04 on 2026-09-25 left stash@{0} "WIP on perturb-seq-eval: 451f730", byte-identical to the working tree (`git diff --quiet stash@{0}` → 0). Every tracked dirty file's mtime was reset to 08:43:06. There are also 12 similar "WIP on lung-on-chipsim" entries on the shared stack.
**Root cause:** STASH_REF is captured as a commit SHA (`git stash list --pretty=format:%H`). `git stash apply <SHA>` accepts it, but `git stash drop <SHA>` rejects it: "error: '<sha>' is not a stash reference", rc=1. Reproduced in a throwaway repo; `git stash drop 'stash@{0}'` → rc=0. The `|| true` hides the failure. Separately, the bare `git stash` breaks fleet rule #344 (no bare stash on the shared stack).
**Fix:** Push with a unique tag (`git stash push -u -m "worktree-sync-$$-$(date +%s)"`). Before dropping, re-find the entry's `stash@{n}` by that tag (`git stash list --format='%gd %gs' | awk '/<tag>/{print $1}'`), then drop that ref. Remove `|| true` and fail loudly. Better still, take a WIP commit instead of stashing.
**Effect:** No more leaked or duplicate entries on the stack other sessions share, so an unexplained stash stops meaning "maybe another session's work".
**Status:** open

## 🟠 2. session-preflight / session-pickup compare against LOCAL main
**File:** tools/session-preflight ("Branch is N commits behind main"), tools/session-pickup
**Symptom:** status=blocked on "78 commits behind main" while the branch is 0 behind origin/main. The local main holds the CTO's unpublished commits, so no agent action can clear it (CTO #309 classes this as a known false block).
**Root cause:** Both tools compare against the local `main` ref and ignore AIADLC_TRUNK_REF (stale-revert-check honours it).
**Fix:** Resolve the trunk as `${AIADLC_TRUNK_REF:-origin/<trunk>}` and fetch first.
**Effect:** Removes the false block; a real "behind the published trunk" still blocks.
**Status:** open
