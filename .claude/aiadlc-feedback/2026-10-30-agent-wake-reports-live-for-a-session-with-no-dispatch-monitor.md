# agent-wake reports a session LIVE when it has no dispatch monitor, so dispatches to it dead-drop silently

**Filed by** `biofm/matthew-mo/cto` · **2026-10-30** · plugin `airdlc` **0.87.0**

## What happens

`agent-wake <agent> --dry-run` answers:

```
agent 'aviary-biosim' has a LIVE Claude session in its worktree (pid 41060) — not spawning a
duplicate. The dispatch is in its inbox; that session picks it up
```

That last clause is **not true** when the session is running no dispatch monitor, and here it
was not:

| check | result |
|---|---|
| pid 41060 alive, cwd = the aviary worktree | yes, up 1h30m |
| `dispatch-monitor` process pinned to the aviary worktree | **none** |
| `dispatch-monitor` pinned to lung-on-chipsim / the CTO checkout | present (pids 2553, 61420) |
| files modified in the aviary worktree since the session started | **none** |
| pid 41060's children | three MCP servers only |

So a `changes-requested` dispatch routing a red CI on the **primary** track sat unread, and
`agent-wake` both refused to start a session that would read it and told the sender it would be
picked up.

## Likely mechanism

A harness restart killed every background monitor in every session. The CTO re-armed its own;
the aviary session came back without re-arming its monitor. The process survived; the pickup path
did not. Nothing distinguishes the two states from outside except the absence of a process.

## Why it matters

The liveness check measures **a process**, but what the sender needs is **a pickup path**. The
gap between those is exactly where a dispatch dead-drops — and `dispatch create` returning ✓ plus
`agent-wake` saying LIVE gives the sender two independent false assurances.

## Suggested direction (maintainer owns the design)

1. **Define LIVE as "a dispatch monitor is pinned to that worktree", not "a Claude process has
   that cwd".** A process with no monitor is `PRESENT-NOT-LISTENING` and should be reported as
   such.
2. **For that state, offer the fix rather than refusing.** Either nudge the session (if there is a
   channel) or say plainly that a human at that session must re-arm the monitor or close it so a
   headless session can be woken.
3. **After a restart**, sessions that resume could re-arm their monitor as part of
   `/session-resume` — the CTO only re-armed because its own standing rule said to.

Found during a cto-loop sweep (iteration 6), by checking for a monitor process after
`agent-wake` had already said LIVE — the same rule that has caught this class before: a hedge
from a tool is not a measurement.
