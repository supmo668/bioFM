# `dispatch` DB lock contention turns the monitor's silence contract into UNKNOWN at fleet scale

**Tools:** `tools/dispatch-monitor`, `tools/dispatch` (plugin 0.52.0)
**Severity:** medium-high — degrades the trust contract the monitor exists to provide
**Found by:** `biofm/matthew-mo/cto`

## Symptom

```
[DISPATCH STATE] ⚠ could not verify inbox — dispatch catchup --json unreadable
  (exit 1: Parse error near line 2: database is locked (5))
```

Also seen as `Command '[... dispatch, list, --status, unread]' timed out after 30 seconds`.

Both are **correct behaviour by the tool** — it refuses to report "clear" when it could not read
the inbox, exactly as designed. The problem is how often it fires.

## Cause — scale, not a leak

This machine is running **~19 live Claude sessions**, each with its own `dispatch-monitor` polling
the shared ISCP SQLite DB every **10 s** (the default). That is ~114 queries/minute against one
file.

I first assumed leaked orphans and checked: tracing each monitor's parent chain, **only one of
thirteen sampled was a true orphan** (PPID 1). The rest had live `claude` parents. These are real
sessions, not leaked processes — so the contention cannot be cleaned up, only reduced.

**WAL is enabled** (`iscp.db-wal` present), so concurrent *readers* are fine. But the monitor's
reconcile path **writes** (marking dispatches seen), and WAL still serializes writers. With ~19
concurrent writers on one file, lock contention is structural rather than incidental.

Measured for contrast: a hand-run `dispatch catchup` completes in **0.58 s**. The tool is not
slow; it is queued behind other writers.

## Why this matters more than a normal flake

The monitor's value rests on a stated contract:

> silence **AND** the monitor is alive ⇒ your inbox is clear

Every lock failure converts that into **UNKNOWN**, which must then be swept by hand. The contract
degrades from "silence is evidence" to "silence is evidence, except when it isn't, and you have to
notice". An agent that trusts silence during a lock window believes a false negative.

## Suggested fixes

1. **Scale the default poll interval with fleet size**, or raise it outright. 10 s is fine for two
   or three agents and is wrong for twenty. The edge stream does not need 10 s resolution when the
   reconcile pass is the real completeness guarantee.
2. **Add jitter.** Twenty monitors started from similar scripts poll in near-lockstep; a random
   0–N s offset spreads writes without changing latency materially.
3. **Retry on `database is locked` with backoff** before declaring UNKNOWN. A 5-second lock should
   not surface as an inbox-verification failure.
4. **Separate the read path from the write path.** Reading the inbox to decide whether to announce
   should not require a write; mark-as-seen could batch or defer.

Fix 3 alone would remove most of the false UNKNOWNs; fixes 1 and 2 address the cause.
