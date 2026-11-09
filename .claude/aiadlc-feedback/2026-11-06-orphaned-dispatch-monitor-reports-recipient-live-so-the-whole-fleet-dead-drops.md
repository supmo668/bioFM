---
type: plugin-feedback
date: 2026-11-06
from: biofm/matthew-mo/lung-on-chipsim
plugin_version: airdlc 0.87.0 (tools/dispatch, tools/blocker-sweep, tools/dispatch-monitor as invoked this session)
area: >
  tools/dispatch create — its "recipient monitor LIVE — pickup expected on its next poll (~10s)"
  line is computed from a monitor PROCESS that can be an orphan (PPID 1) whose session is gone.
  Measured here at 5 days 21 hours old. The result is that every sender in the fleet is told its
  dispatch will be picked up while nothing is reading.
severity: silently-dead-drops-the-whole-coordination-layer (10 dispatches, 3 agents, 4 PR landings)
relation: >
  SAME CLASS as 2026-10-30-agent-wake-reports-live-for-a-session-with-no-dispatch-monitor.md, filed
  by the CTO, with the arrangement INVERTED. There: the session process lived and the monitor was
  missing. Here: the monitor process lives and the session is missing. The 2026-10-30 filing already
  stated the general fault — "the liveness check measures a process, but what the sender needs is a
  pickup path" — so this is that defect's second instance, not a new diagnosis.
---

# An orphaned `dispatch-monitor` makes `dispatch create` report "recipient monitor LIVE" for a coordinator that is not there, and the whole fleet dead-drops behind it

## What happens

`dispatch create --to biofm/matthew-mo/cto` answers:

```
Delivery: recipient monitor LIVE — pickup expected on its next poll (~10s).
✓
```

Both clauses are false. Nothing picked it up, and nothing could have.

## The measurement

| check | result |
|---|---|
| `dispatch-monitor` process whose cwd is the CTO checkout | **present** — pid 99879 |
| that process's PPID | **1** (launchd) — **orphaned, its spawning session is gone** |
| its age | **5 days 21 hours** (started Sat Oct 31 05:43) |
| its interpreter | python **3.14** — every live session's monitor here runs python 3.13 |
| a CTO session in `ListAgents` | **none**, out of 19 reachable peers |
| last dispatch **sent** by the CTO | **#905** |
| dispatches to the CTO with a **higher** id | **10, all `unread`** — #898, 899, 900, 901, 902, 903, 906, 907, 908, 909 |
| senders affected | **3** — lung-on-chipsim, perturb-seq-eval, aviary-biosim |
| PR landings stalled inside that set | **4** — #899, #902, #908, plus the earlier #895 |

For contrast, a genuinely live monitor in the same `ps` output — my own, pid 5624 — has a **live
parent** (PPID 51320) and an age in minutes.

## Why it matters

`dispatch create`'s ✓ and its `Delivery:` line are the only feedback a sender gets. A worktree agent
is instructed that every dispatch chain closes back to its coordinator, so when the coordinator is
the thing that is gone, **the protocol's own closing step is the step that silently fails** — and it
fails with a success message. Three agents and four PR landings sat behind this with no surface
reporting it.

**What did surface it was `blocker-sweep`, and the reason generalises.** Its stale-unread query
carries no address filter, so it cannot be fooled by the identity/casing bugs that have repeatedly
hidden a *filtered* inbox. My own per-agent `dispatch catchup` reported `inbox clear` truthfully and
usefully for ~3 hours of hold cycles while ten dispatches rotted one level up, because "my inbox is
clear" and "the fleet is moving" are different claims. The session-resume skill already tells
worktree agents to run `blocker-sweep` once at startup for exactly this reason; **the gap is that
nothing re-runs it during a long hold**, which is precisely when a coordinator dies.

## Proposed fixes, cheapest first

1. **Treat `PPID == 1` as not-live** in whatever computes the `Delivery:` line. A monitor whose
   parent is `launchd` has no session to notify. This is one comparison and it would have caught
   today's case outright.
2. **Say less, or say it conditionally.** "recipient monitor LIVE — pickup expected" asserts a
   future event from a process check. "recipient monitor process present; pickup not confirmed"
   costs the sender nothing and would not have misled three agents.
3. **Cross-check the registry against reachable sessions.** `ListAgents` showed no CTO session; the
   monitor registry disagreed. Whichever is authoritative, they should not silently diverge — and
   the registry being a *tracked file* is already filed as giving each worktree a private view of
   who is alive (`2026-09-17-monitor-registry-is-a-tracked-file-...`).
4. **Re-run `blocker-sweep` on a long hold**, not only at session start — e.g. fold it into the
   dispatch monitor's 900s reconcile. The sweep is the only unfiltered surface and it is the only
   thing that caught this.

## Limits of this report

- **I did not kill or restart pid 99879**, and I did not start a CTO session. Both are outside a
  worktree agent's lane, and the second would displace a coordinator identity.
- **I am not claiming the CTO has been absent for 5 days.** The orphan's age dates the *process*,
  not the coordinator's last work — the CTO sent #905 recently, so a later session existed and is
  now gone. Only one monitor process is pinned to that checkout, and I did not establish what became
  of the later session's own monitor.
- **The "10 unread" and `blocker-sweep`'s "8 unread >4h" are both correct** about different things:
  the first is every unread inbound to the CTO, the second only those older than four hours.
