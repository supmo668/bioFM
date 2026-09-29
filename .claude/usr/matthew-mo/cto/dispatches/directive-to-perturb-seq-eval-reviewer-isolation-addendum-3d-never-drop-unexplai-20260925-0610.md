---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-25T13:10
status: created
priority: normal
size: task
subject: "Reviewer isolation addendum 3d: never drop unexplained stashes/branches; no bare stash/pop"
in_reply_to: null
---

# Reviewer isolation addendum 3d: never drop unexplained stashes/branches; no bare stash/pop

REVIEWER ISOLATION RULE, addendum 3d (from aviary-biosim #342). The stash stack is SHARED across every worktree of a repo, and other sessions push and pop it concurrently.
- An unexpected stash, branch, worktree or tag found by the bracket means ABORT and investigate. NEVER drop, delete or prune it. It may be another session's work, and 'git stash drop' on a shared stack is irreversible. Report it; the owner or the CTO decides.
- Never use bare 'git stash' or 'git stash pop'. Prefer a WIP commit. If you must stash: 'git stash push -u -m <unique-tag>', capture the SHA at once, restore with 'git stash apply <sha>', and drop only your own entry, re-found by tag.

No reply needed.
