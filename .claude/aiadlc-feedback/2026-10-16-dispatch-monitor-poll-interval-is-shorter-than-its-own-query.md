# `dispatch-monitor` polls every 10s a query that takes 15-32s, with a hardcoded 30s timeout

**Filed:** 2026-10-16 · **By:** biofm/matthew-mo/cto · **Plugin version in effect at filing:** 0.82.0
**Scope:** plugin / operating-system behavior — NOT repo/app work
**Status:** open

**Symptom.** The edge poll began failing repeatedly:

```
dispatch-monitor: Command '[.../dispatch', 'list', '--status', 'unread']' timed out after 30 seconds
```

**Measured, not inferred.** Two consecutive runs of the monitor's own query on this machine:

| run | wall time |
|---|---|
| 1 | **15.27 s** |
| 2 | **32.20 s** |

So the query **straddles the monitor's timeout**, and whether a poll succeeds is luck. A hand sweep (`dispatch catchup`) needed a 120 s bound to complete reliably.

**The structural part.** `tools/dispatch-monitor` polls at `--interval` (default **10 s**) and bounds each
call at a **hardcoded 30 s** (`run_command(cmd, timeout: int = 30)`; also `timeout=30` at the collab
check). `--interval` and `--reconcile` are both configurable; **the timeout is not.**

A 10-second interval around a 15-32 second query means the monitor **issues queries faster than they
complete**. On this machine there are **17 inboxes** and several agent monitors running at once, so
the pattern is self-amplifying: each monitor's overlapping polls contend for the same SQLite DB,
which lengthens the query, which causes more overlap. The monitor is plausibly a *cause* of the
contention it then reports, not only a victim of it.

**Why it matters beyond noise.** The documented trust contract is: *silence AND the monitor is alive
⇒ the inbox is clear.* When the inbox check times out the monitor correctly reports
`⚠ could not verify inbox` rather than claiming clear — that part is well designed and it worked.
But the practical effect is that **the invariant degrades to "unknown" at random**, and the operator
must hand-sweep on every occurrence. An invariant that needs a manual check each time it fires is
one an operator eventually stops checking.

**Fixes, in preference order:**
(a) **Derive the timeout from the interval** rather than hardcoding it — e.g. `timeout = max(30, 3 ×
interval)` — so the two cannot be configured into contradiction.
(b) **Skip a poll while the previous one is still running** (a simple in-flight guard). This removes
the self-amplification directly and is a few lines.
(c) **Expose `--timeout`**, so an operator on a loaded machine can raise it without patching.
(d) Independently: the unread query looks like it scans every inbox on the machine. An index or an
address-scoped fast path would cut the cost at source.

**Operator mitigation applied here (not a fix):** re-armed with `--interval 60`, so this monitor's
polls no longer overlap its own query. The reconcile cadence is untouched, so the level guarantee is
unchanged.
