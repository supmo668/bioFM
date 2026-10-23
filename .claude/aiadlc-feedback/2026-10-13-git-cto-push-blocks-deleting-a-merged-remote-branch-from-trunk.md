# `git-cto push --delete <merged-branch>` is blocked from trunk, so landed branches are never cleaned up

**Filed:** 2026-10-13 · **By:** biofm/matthew-mo/cto · **Plugin version in effect at filing:** 0.82.0
**Scope:** plugin / operating-system behavior — NOT repo/app work
**Status:** open

**Symptom.** After landing PR #27, Step 11.1 of `/pr-cto-land` says to delete the landed branch.
The local branch was already gone (the agent retired its worktree with `-D`), so only the **remote**
ref remained, merged, at `3877f78`. Both available paths refuse:

- `git-cto branch-delete perturb-seq-eval --force` → `error: branch 'perturb-seq-eval' not found`.
  It is local-only (`git branch -d/-D`) and has no remote mode.
- `git-cto push origin --delete perturb-seq-eval` → `[ERROR] Push from main is blocked. Switch to a
  feature branch first.`

**Why the second one is a false positive.** The guard's question is *"am I standing on trunk?"* when
the question it means to ask is *"am I pushing trunk?"*. Deleting an unrelated, already-merged
feature ref pushes nothing to trunk and cannot endanger it — but the CTO performs the land **from
trunk by precondition** (`/pr-cto-land` requires main checkout on `cto.branch`), so the one role
that is supposed to clean up is structurally the one role that cannot.

**Observed consequence, measured.** `tools/post-land --into main` on this repo reports **11 branches
merged and not deleted**, including seven `cto/*` coordination branches and four
`worktree-agent-*` refs. That is not neglect; it is the guard. Each land adds one. The previous CTO
session recorded the same thing in its handoff ("the CTO may not delete remote refs (classifier), so
delete on GitHub or add the allow rule") and the debt has grown since.

**Fixes, in preference order:**
(a) Narrow the trunk guard to the **refspec**, not the current branch: refuse a push whose target is
the trunk, allow `--delete <other-branch>`.
(b) Give `branch-delete` a `--remote` mode that deletes an already-merged remote ref, refusing when
the ref is not merged into the trunk.
(c) At minimum, have `post-land` print the exact command a human must run, since the CTO cannot.

**Effect.** `/pr-cto-land` Step 11.1 becomes performable by the role the skill assigns it to, and
the merged-branch list stops growing by one per land.

**Status:** resolved in airdlc v0.86.0 (maintainer, #612) — fixed, but NOT as this entry proposed. **This entry's premise was wrong:** it claimed lines 388-392 already guarded by refspec. They matched only the literal `main`/`origin/main`, so `feat:main`, `HEAD:main`, `refs/heads/main`, `--all` and `--mirror` all reached the trunk from any branch, and deleting line 393 alone would also have allowed `push origin HEAD` from the trunk. The guard now runs git's own `push --dry-run --porcelain` and refuses any destination of `refs/heads/<trunk>`; a deletion is allowed only for a branch proved merged on the remote, failing closed when that cannot be checked. `push origin --delete <merged>` now works from the trunk. Nine bypasses of the maintainer's first parser are pinned in tests.
