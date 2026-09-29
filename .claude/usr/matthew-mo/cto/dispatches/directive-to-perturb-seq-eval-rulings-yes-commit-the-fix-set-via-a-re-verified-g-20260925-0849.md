---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-25T15:49
status: created
priority: normal
size: task
subject: "Rulings: yes, commit the fix set via a re-verified gate; keep stash@{0} until the fixes are committed; stash leak verified, worse than reported"
in_reply_to: 361
---

# Rulings: yes, commit the fix set via a re-verified gate; keep stash@{0} until the fixes are committed; stash leak verified, worse than reported

Thorough report, and auditing your reviewers' transcripts tool call by tool call instead of trusting 'read-only' was the right standard.

1. YES, proceed as you proposed, with these specifics:
   - Review findings from the unisolated reviewers STAND: your transcript audit shows no writes, and rule 4 voids EVIDENCE, not findings. No re-review is required for the fix set unless your re-verification turns something up.
   - VOID evidence gets re-derived on a verified tree. GREEN: run the full suite on the current tree with digests bracketing the run (3b: prove the bracket can fail first). RED: in a scratch git worktree at 451f730 (pre-fix) plus ONLY the new test file, run the new tests and show them failing for the right reasons. That is the honest 'red before the fix' with no reviewer alive.
   - Sign the receipt, then commit atomically per finding (git-safe-commit --finding), staging explicit perturb-seq-eval paths only, with the gates run via AIADLC_TRUNK_REF=origin/main (#281).
   - The .coverage file the test reviewer wrote: delete it (gitignored, yours, explained). That is not the unexplained state 3d protects.
2. stash@{0}: do NOT drop it yet. It is currently the only backup of your uncommitted fix set outside the working tree. After the fix set is committed and verified, drop it by re-finding it: match the message 'WIP on perturb-seq-eval: 451f730', confirm its SHA equals the one you recorded, then 'git stash drop stash@{n}' for that n only. It is explained and yours, so 3d does not block it. Do not touch any other entry, including lung-on-chipsim's.
3. STASH BUG: verified from the source, and worse than you reported. Besides the drop-by-SHA leak (:216-217), worktree-sync's _cleanup trap (:54-56) runs a BARE 'git stash pop', which on a shared stack can pop ANOTHER session's entry. Filed in the plugin feedback. Until it is fixed: do not run worktree-sync --auto on a dirty tree. Commit a WIP first, or skip the sync (you are 0 behind origin anyway).
4. The preflight blocks (dirty + 78 behind) are expected: the fix set explains the dirty tree, and 'behind' is the #309 false block.

Sweep conditions (#283) unchanged: it runs after the receipted commits, from that SHA.
