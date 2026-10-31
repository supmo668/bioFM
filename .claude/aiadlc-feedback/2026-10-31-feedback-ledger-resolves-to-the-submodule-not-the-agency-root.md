---
type: plugin-feedback
target: airdlc plugin
plugin_version: 0.87.0
reporter: biofm/matthew-mo/cto
date: 2026-10-31
scope: plugin / operating-system behavior — NOT repo/app work
---

## 🟠 1. feedback-file resolves the ledger to a SUBMODULE's main checkout, so a worktree agent's finding lands in a foreign public repo's working tree
**File:** `tools/feedback-file` (ledger dir = "the MAIN checkout of the agency root (the parent of git's common dir)"); measured in bioFM, where `projects/aviary-biosim` is a submodule and `worktrees/aviary-biosim` is a linked worktree OF that submodule
**Symptom:** The aviary agent filed `/feedback` from `worktrees/aviary-biosim` at 01:41. The file was written to `projects/aviary-biosim/.claude/aiadlc-feedback/2026-10-31-hacp-contract-and-sync-guard.md` — the submodule's main checkout (detached HEAD at `bece4dc`), which is the public `supmo668/Aviary-BioSim` repository, not the bioFM agency root. Effects, all measured 09:30: the superproject's `git status` reported the gitlink as modified (untracked content); `session-preflight` counted it as a dirty file and BLOCKED session-resume; the agent's own Stop hook (running in the worktree) never saw the file; and it sat uncommitted for eight hours until the coordinator read it by hand.
**Root cause:** "parent of git's common dir" is the right answer for a plain repo + worktrees, and the wrong one for a submodule fleet: the submodule's common dir is the submodule's own `.git`, so the ledger resolves one level too low. The tool knows the case exists — `feedback-file where` prints "worktree" for "a linked worktree or a submodule: dispatch the coordinator" — but the relocation is then a manual copy by the coordinator, and nothing in the superproject marks the stray file as a ledger entry rather than foreign-repo dirt.
**Fix:** Resolve the ledger against the agency root that `agency.yaml` defines (walk up from the common dir's parent until a checkout containing `agency.yaml` is found), so a submodule agent's finding lands in the superproject's ledger directly. Until then, have `feedback-file new` refuse to write when `where` would answer "worktree" for a submodule and print the superproject path instead, so the file is never created in the foreign repo.
**Effect:** A finding filed from any worktree in the fleet is visible to the trunk reader on the day it is filed, and a submodule checkout stops accumulating files that belong to the superproject.
**Status:** open (filed against airdlc 0.87.0; worked around 2026-10-31 by copying the file into `.claude/aiadlc-feedback/` byte-identical and removing the stray copy)
