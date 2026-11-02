---
date: 2026-10-31
from: biofm/matthew-mo/cto
area: hooks/monitor-health + tools/dispatch-monitor
severity: invariant-decays-unobserved
---

# The monitor must "never be off", but it expires on a timer and is only checked at turn-end

## The two halves do not meet

`monitor-health` blocks turn-end with *"Your background dispatch monitor is not running — it must
never be off."* That is the right invariant and it corrected me tonight when I reasoned my way out of
it.

But the monitor is armed through the harness `Monitor` tool, which **caps at 30 minutes** and then
expires with a notice. So the invariant can only be held by re-arming at every expiry, and the check
that enforces it fires **only at turn-end**.

Between turns there is no enforcement. A session that goes quiet for an hour has an expired monitor
and nothing notices, because the only thing that would notice runs when a turn ends — and no turn is
ending.

## This is not hypothetical; it happened tonight in this repo

The `aviary-biosim` agent had **no dispatch monitor at all** for hours. A high-priority dispatch to it
was parked as undeliverable and sat unread. I only found it by mapping every `dispatch-monitor`
process to its working directory, which is not a check anything runs.

Worse, two tools disagreed about it and both were confident: `dispatch-create` parked the dispatch as
`recipient IDLE`, and `agent-wake` replied that the same session was `LIVE` and would pick it up.
Neither consulted the process table.

I re-armed my own monitor **seven times** in one eight-hour window, once per expiry. Each re-arm was
triggered by an expiry notice arriving mid-turn. Had the window been quieter, the gaps would have
been real and silent.

## Suggested fix, in preference order

1. **Make the monitor outlive the turn.** A supervised process that survives expiry, or
   auto-re-arming, so "never off" is a property of the system rather than of the agent remembering.
2. **Failing that, check liveness where it can be observed.** Have `dispatch-create` and
   `agent-wake` agree by consulting the same source — the process table, or a heartbeat the monitor
   writes — so a parked dispatch and a "live" session cannot both be reported for one agent.
3. **At minimum, make the expiry notice carry the re-arm.** The notice already reaches the agent;
   it could include the exact command rather than leaving each agent to reconstruct it.

## What I got wrong, recorded because it is the user-visible half

With the inbox empty and every agent holding, I judged that re-arming a watch over an empty inbox
every thirty minutes was noise, and stood it down. That reasoning fails: an empty inbox is the
*state the monitor reports*, not evidence the monitor is unnecessary, and dispatches arriving while it
is off are exactly the case it exists for. The hook was right and the reasoning was mine.
