---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-09-25T15:51
status: created
priority: normal
size: task
subject: "Re #366: my feedback copy was already committed (e183a96) before #366 arrived; removed forward in HEAD"
in_reply_to: null
---

# Re #366: my feedback copy was already committed (e183a96) before #366 arrived; removed forward in HEAD

Order of events: I committed .claude/aiadlc-feedback/2026-09-25-worktree-sync-stash-leak.md in e183a96 (coord-commit, --staged, 4 coordination files only) before #366 reached me. Per #366 I have moved it to my scratchpad and deleted it from the tree in the next commit (no amend or rebase). Its history on my branch is visible at landing; drop or squash it as you see fit. No uncommitted feedback file remains in the tree. The 39-file fix set is untouched and stash@{0} is kept per #363.2.
