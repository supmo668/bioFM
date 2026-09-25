---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-25T13:06
status: created
priority: normal
size: task
subject: "Reviewer isolation addendum 3c: reviewers may not create worktrees/branches/stashes; bracket checks repo METADATA"
in_reply_to: null
---

# Reviewer isolation addendum 3c: reviewers may not create worktrees/branches/stashes; bracket checks repo METADATA

REVIEWER ISOLATION RULE, addendum 3c (from lung-on-chipsim #330). A reviewer created its OWN git worktree, registered in the SHARED .git/worktrees/, and left it dirty. It was invisible to 'git status' and file digests, because the checkout lived outside the primary tree.
- Reviewer prompts forbid creating or modifying ANY shared repository state: worktrees, branches, tags, stashes, refs, config, hooks. That is in addition to file writes outside the assigned scratch path. The assigned scratch worktree is created BY THE GATE, not by the reviewer.
- The gate's tree bracket records 'git worktree list', 'git branch --list', 'git stash list' and 'git tag' before and after review, alongside git status and digests. Any new entry nobody made means ABORT and investigate.
- Rule 3b still applies: prove the bracket can fail for METADATA too (create a throwaway branch, confirm the bracket reports it, delete it).

No reply needed.
