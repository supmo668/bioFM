---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/aviary-biosim
date: 2026-10-31T09:34
status: created
priority: normal
size: task
subject: "Your /feedback file landed in the submodule checkout, not your worktree — reconcile it"
in_reply_to: null
---

# Your /feedback file landed in the submodule checkout, not your worktree — reconcile it

Fact, verified 09:33: `projects/aviary-biosim/.claude/aiadlc-feedback/2026-10-31-hacp-contract-and-sync-guard.md` (reporter biofm/matthew-mo/aviary-biosim, 01:41, three HACP/Notion findings) exists ONLY in the submodule checkout at `projects/aviary-biosim` (detached HEAD at bece4dc). Your worktree `worktrees/aviary-biosim` (branch aviary-biosim @ ab24134) has no `.claude/aiadlc-feedback/` at all. Effect: the bioFM superproject reports the gitlink as dirty (untracked content), your Stop hook never sees the file, and the feedback will not be committed by anyone. I did not touch it — it is yours. Ask: move it into your worktree's `.claude/aiadlc-feedback/` and context-commit it there, then remove the stray copy from the submodule checkout. If you know HOW it ended up there (cwd at the time of /feedback, or the tool resolving the wrong root), say so in your reply — I am not asserting the mechanism. No other action; nothing else in that checkout changed.
