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

---

## ADDENDUM 2026-11-13 — a SECOND cost of the same defect: orphans never die and contend on the store

The original report above is unchanged and still correct. This section adds a consequence it did
not cover, measured on a different occasion and with a **different remedy**, so it is recorded
rather than folded into the text above.

**What prompted it.** The dispatch monitor emitted
`Command '[... dispatch, list, --status, unread]' timed out after 30 seconds`, twice on separate
days. The first time I hypothesised the monitor's 30s timeout was mis-scaled against a scan that
now covers ~20 inboxes, measured the query at **1s**, and **refuted my own hypothesis** — recorded
here because the refutation is the useful part: a plausible scaling story survived until it was
timed.

**What the recurrence measured.**

| probe | result |
|---|---|
| `dispatch list --status unread`, 3 consecutive runs | **4572ms / 2670ms / 3356ms** — slower than the 1s measured 2026-11-11, still far under 30s |
| `dispatch*` processes on the machine | **35** |
| `dispatch-monitor` processes | **27** |
| of those, **ORPHANED** (PPID 1) | **2** — pids 31624 and 73517 |
| their age | **5d 15h** and **5d 14h** |
| their cwd | `/private/var/folders/.../T/tmp.HcOXHI5XGv` and `tmp.zsi2K4LKxm` — **deleted temp dirs** |
| my own monitor, for contrast | live parent (ppid 13721), age 7 min |

**The point.** The original report treated an orphan as a *reporting* problem: it makes
`dispatch create` claim "recipient monitor LIVE" for a coordinator that is not reading. It is also a
*resource* problem. An orphan does not stop. These two have been polling every 10 seconds for over
five days, against a shared store, from working directories that no longer exist. Nothing reaps
them, because the thing that would reap them is the session that died.

**What I did NOT establish, and will not claim.** I have **not** shown that the orphans cause the
30s timeouts. The measured baseline (2.7–4.6s) is an order of magnitude below the timeout, so the
spikes require something episodic, and contention from 27 concurrent monitors is a *plausible*
source, not a demonstrated one. Establishing it would mean stopping the orphans and re-measuring —
which I did not do, because they are not mine: their owners are unidentifiable (deleted cwd) and
killing another principal's process is outside a worktree agent's lane.

**Separately worth stating:** the failure is currently BENIGN for correctness. The monitor emits a
timeout event and keeps running, and a worktree agent's own `dispatch catchup` is authoritative and
succeeded every time. So this is noise plus waste, not lost mail — on the evidence so far.

**Remedy, distinct from the original's.** The first needs a liveness check (`PPID == 1` is not
live). This needs **reaping**: a monitor should exit when its cwd no longer exists or its parent is
`launchd`, or `monitor-register` should record a session id that a later start can use to retire
predecessors. A self-terminating orphan would fix both costs at once.

## ADDENDUM 2 — 2026-11-14: the stall is BIMODAL and the worst case is 247 SECONDS

The addendum above said the spikes "require something episodic" and that contention was "plausible,
not demonstrated." A third occurrence was measured and the episodic thing is now **measured, not
inferred** — which also raises the severity past "noise and waste."

Three consecutive runs of the monitor's own query, immediately after it reported a 30s timeout:

| run | elapsed |
|---|---|
| 1 | **247428 ms — 4 minutes 7 seconds** |
| 2 | 2466 ms |
| 3 | 1977 ms |

Population at the same moment: **23** dispatch-monitor processes, **2** orphaned (PPID 1, the same
two, now ~6 days old), **39** total `dispatch*` processes, **927** rows in the store.

**The shape is bimodal, not a slope.** Normal is ~2s. The failure is a multi-minute block, then
normal again. That is a lock/contention stall, not a query that has grown too slow — and it is why
the 30s timeout fires: not because 30s is too tight for a 2s query, but because the query sometimes
does not return for two orders of magnitude longer.

**It retro-explains an earlier observation.** On 2026-11-11 a plain `dispatch catchup` of mine
exceeded its 120s limit and was backgrounded; it later returned `✓ no unread rows`. At the time I
recorded only that I had wrongly called the inbox UNKNOWN when the command had merely not finished.
Same stall class. The two observations are one phenomenon.

**Severity is now higher than the first addendum stated.** A 4-minute block means a monitor's
reconcile can miss its window entirely, and any agent's catch-up gate can hang for minutes at
session start — the gate that is supposed to prove the inbox is clear before work begins. On the
evidence so far no mail was lost, because every stalled call eventually returned the right answer.
**But "eventually returns" is not "is available when the gate runs."**

**Still NOT established, and still not claimed:** that the 2 orphans cause this. They are 2 of 23
monitors; all 23 poll every ~10s against one store, so roughly 2.3 queries/second from live agents
alone. Reaping the orphans would remove ~9% of that. The orphan finding and the stall finding are
**adjacent, not the same defect** — and the remedy for the stall is probably whatever serialises
access to the store, which I have not inspected.

### Correction to Addendum 2's severity claim — 2026-11-14, same day

Addendum 2 said the stall "raises severity past noise and waste" because "a session-start catch-up
gate can hang for minutes — the gate that proves the inbox is clear before work begins." The
hanging is real. **The implied danger was overstated, and the overstatement is worth correcting as
much as an understatement would be.**

Observed on the next burst: when its query times out, the monitor does **not** fall silent and it
does **not** report clear. It emits, verbatim:

> `[DISPATCH STATE] ⚠ could not verify inbox — dispatch catchup --json unreadable (TimeoutExpired).`
> `Treat this as UNKNOWN, not clear: check the ISCP DB, then sweep by hand with `dispatch catchup`.`

That is the correct distinction, built into the tool — the same one this workstream keeps having to
enforce by hand. A stall therefore degrades to an explicit UNKNOWN with a named remedy, not to a
false "clear." **So the mail-loss risk is lower than Addendum 2 implied**: the failure is loud, and
the hand sweep it names works (measured at the same moment: `CLEAR` in 48s, and `CLEAR` in 30s on
the prior burst — the 30s one being exactly the window the monitor gives up at, so it abandoned a
call that was about to succeed).

**What stands from Addendum 2:** the stall is real, bimodal, and measured at 247s worst case; it
costs wall-clock at session start and fires spurious alerts. **What does not stand:** the suggestion
that it silently defeats the inbox-clear gate. It announces itself.
