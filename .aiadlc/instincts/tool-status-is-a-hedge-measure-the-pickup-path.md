---
name: tool-status-is-a-hedge-measure-the-pickup-path
confidence: 1.000
created: 2026-10-30T18:41:53Z
last_reinforced: 2026-11-02T03:07:09Z
ttl_days: 30
triggers: [agent-wake, dispatch, blocker-sweep, dispatch-monitor, @{u}, rev-list]
tags: []
---

A tool's status line is a claim about its own subject, which is rarely the thing you need. agent-wake's LIVE meant 'a Claude process has that cwd', not 'something is reading its inbox': the aviary session had no dispatch monitor after a restart, so routed dispatch #799 sat unread while agent-wake both refused to spawn a reader and promised pickup. Same class this window: dispatch's 'idle' hint for an agent with a live session, and git rev-list @{u}.. reporting 0 unpushed when the real predicate is reachability from any remote ref. **Why:** two independent false assurances (dispatch ✓ plus LIVE) are worse than none, because they stop you looking. **How to apply:** measure the thing you need. For delivery, check for a dispatch-monitor process pinned to the recipient's worktree and for files changing there. For pushed-ness, test merge-base --is-ancestor against every refs/remotes ref.
