---
name: never-tell-an-agent-to-delete-the-worktree-it-is-running-in
confidence: 0.720
created: 2026-11-03T19:15:10Z
last_reinforced: 2026-11-03T19:15:10Z
ttl_days: 30
triggers: [worktree-delete, worktree-remove, worktree retire, post-land, blocker-sweep, PARKED]
tags: []
---

A self-retire instruction is unsafe when the agent's only session is INSIDE the worktree being removed: '/worktree-delete <branch>' then deletes the floor under the live session, which is the exact ordering the framework forbids (remove the worktree before deleting the branch, never from inside it). Caught by the recipient refusing, not by me. **Why:** 'prefer self-retire over direct removal' is correct about WHO should act and silent about WHERE they are standing; waking an idle agent to retire its own worktree guarantees it is inside it. **How to apply:** before asking for a retire, ask where the agent's session will be. Safe order: the agent ends its session, THEN removal happens from the main checkout (a destructive act needing principal confirmation). Also check the reason still holds before spending a session on housekeeping — reading a parked dispatch already clears it from blocker-sweep, so the noise being fixed may be gone before the fix is asked for. And do not warn about 'uncommitted files' in an airdlc worktree without looking: '.aiadlc-agent' and '.aiadlc-coordinator' are identity scaffolding present in every one of them, never work.
