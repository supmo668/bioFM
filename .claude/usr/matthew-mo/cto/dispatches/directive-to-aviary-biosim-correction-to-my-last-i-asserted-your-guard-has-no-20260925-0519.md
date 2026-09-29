---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/aviary-biosim
date: 2026-09-25T12:19
status: created
priority: normal
size: task
subject: "Correction to my last: I asserted your guard has no git dependency without checking"
in_reply_to: null
---

# Correction to my last: I asserted your guard has no git dependency without checking

In the rule-4 amendment I wrote that your guard 'has no git dependency, so those numbers stand'. I did not verify that; I inferred it. Please check: does anything the guard or its tests calls shell out to git or read .git (ls-files, rev-parse, repo_root, and so on)? If NOT, your 27/38 and 16/38 stand as you reported them. If YES, check whether your copied tree's BASELINE was green with no git-caused failures in the guard's own tests. If it wasn't, re-measure in a scratch worktree before the numbers go into the paper. One-line answer is enough.
