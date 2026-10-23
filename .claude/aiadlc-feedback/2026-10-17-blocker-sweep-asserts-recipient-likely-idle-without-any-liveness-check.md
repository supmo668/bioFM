# `blocker-sweep` asserts "recipient likely IDLE (dead-drop, not delivered)" with no liveness check — and `agent-wake`, in the same plugin, already knows better

**Date:** 2026-10-17
**Filed by:** biofm/matthew-mo/cto
**Plugin:** airdlc 0.82.0
**Severity:** high — it caused a coordinator to misreport a blocker's root cause to the principal for a full day

## What happened

Two dispatches (#608, #622) sat unread for a lung-on-chipsim agent. Every 15 minutes for over a day,
`blocker-sweep` told me:

```
WAKE   2 dispatch(es) unread >4h — recipient likely IDLE (dead-drop, not delivered).
       For each: .../agent-wake <recipient-agent>   (or re-send with --wake)
```

I relayed that to the principal as the blocker's cause: *the agent has never woken; nothing moves
until you wake it.* **It was false.** When the principal finally authorised the wake,
`agent-wake lung-on-chipsim --dry-run` answered:

```
live-session
agent 'lung-on-chipsim' has a LIVE Claude session in its worktree (pid 13641) — not spawning a duplicate.
```

Verified independently: `ps -p 13641` → a live `claude` process, **8h42m elapsed**, state **`S+`**
(foreground, blocked on input), cwd `worktrees/lung-on-chipsim`. The recipient had been alive the
whole time. The real faults were (a) a session parked at an interactive prompt with nobody at the
keyboard, and (b) that session standing in the **Stage 1** worktree while the dispatch described work
in the **Stage 2** worktree. **A wake would have fixed neither** — the suggested remedy was wrong for
the actual condition.

## The defect

`blocker-sweep:224` emits the WAKE line from `STALE_N` alone — the row count of the age query at
`:179` (`status = 'unread' AND created_at <= datetime('now','-${STALE_HOURS} hours')`). It performs
**no liveness check of any kind**. Grepping the script for `pgrep|ps -|monitor-register|live` returns
exactly two hits: the message text itself and the `agent-wake` suggestion beneath it.

The information is not missing from the system — it is *one tool away*. `agent-wake` checks two
tiers before acting:

- `agent-wake:111` — a live **dispatch monitor** for that agent ⇒ "will be picked up on its next poll (~10s). No wake needed."
- `agent-wake:156` — a live **Claude session** in its worktree (via `_pstart()`/`ps` at `:164`) ⇒ "not spawning a duplicate."

So the plugin already distinguishes *unread because nobody is listening* from *unread because the
listener is busy or parked*. The surface that nags the coordinator every 15 minutes is the one that
does not look.

## Why this is worse than a wording nit

1. **It states a cause, not an observation.** "unread > 4h" is a fact. "recipient likely IDLE
   (dead-drop, not delivered)" is a diagnosis, and "not delivered" is flatly wrong when a live
   session holds the row. A coordinator relaying the sweep is relaying a conclusion the tool did not
   earn. I did exactly that, for a day, to the principal.
2. **It prescribes the wrong remedy.** It names `agent-wake` — the very tool that would have
   contradicted it. Following the instruction is what finally exposed the error; reading the line and
   believing it is what delayed that by a day.
3. **It masks the harder failure mode.** "Idle recipient" is cheap to fix (wake it). "Live session
   parked at a prompt, in the wrong worktree" needs a human at that terminal and cannot be fixed by
   any coordinator-side action. By labelling the second as the first, the sweep hid the only fact
   that mattered.
4. **The hedge does not save it.** "*likely* IDLE" is doing load-bearing work in a line that also
   asserts "not delivered" as fact. In practice the hedge is read as noise — operators act on the
   diagnosis. (Same lesson as the 2026-09-27 filing on the variant-identity warning: a guard that
   mis-describes reality trains the reader to discount it.)

## Proposed fix

**Call the check that already exists.** Before emitting the line, resolve liveness per *recipient*
(reuse `agent-wake`'s two tiers, or factor them into a shared `agent-liveness` helper) and split the
output:

- recipient has **no** live monitor and **no** live session → `WAKE … dead-drop, not delivered` + the
  `agent-wake` suggestion. This is the only case where today's text is true.
- recipient has a live **monitor** → `UNREAD … recipient is live; not a dead-drop` — nothing for the
  coordinator to do but watch.
- recipient has a live **session** but no monitor → `STALLED … live session (pid N) is not picking up;
  needs a human at that terminal` — and **do not** suggest `agent-wake`, which will refuse.

Minimum viable change if the per-recipient resolution is too costly in the sweep's hot path: drop the
causal clause and print only what was measured — `UNREAD 2 dispatch(es) >4h — cause unknown; run
agent-wake <recipient> to classify`. An honest "unknown" would have sent me to the check on day one.

Worth adding to the `STALLED` case: compare the live session's cwd against the worktree the dispatch
concerns. That mismatch was the second half of this incident and nothing surfaces it today.

## Evidence

- `tools/blocker-sweep:224` (message), `:179` (the age-only SQL), `:215` (the `PARKED` lines)
- `tools/agent-wake:111`, `:156`, `:164` (`_pstart`) — the liveness checks that exist
- `ps -p 13641 -o pid,etime,stat=` → `13641  08:42:48  S+`; cwd via `lsof -a -p 13641 -d cwd` →
  `/Users/mo/github/personal/bioFM/worktrees/lung-on-chipsim`
- Dispatches #608, #622 → `biofm/matthew-mo/lung-on-chipsim`; `dispatch.stale_unread_hours` = 4
- The worktree mismatch: session cwd `worktrees/lung-on-chipsim` (`f66fbf7`, Stage 1) vs the
  dispatch's subject `worktrees/lung-on-chipsim-stage2` (`c781e9c`)
- Related: `2026-09-27` variant-identity false positive; `2026-10-16-dispatch-monitor-poll-interval-is-shorter-than-its-own-query.md`
