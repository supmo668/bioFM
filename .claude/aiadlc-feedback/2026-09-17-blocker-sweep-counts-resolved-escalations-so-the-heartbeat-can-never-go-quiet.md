# `blocker-sweep` counts **resolved** escalations as blockers, so the coordinator's heartbeat is permanently red and can never go quiet

**Component:** `tools/blocker-sweep` (plugin 0.56.0), lines ~111–123
**Severity:** high — this is the coordinator's "not clear yet" surface. It is stuck at 30 blockers that
no action can clear, and its prescribed remedy is to interrupt the principal 30 times.
**Observed:** 2026-09-17, bioFM, by the CTO when the 15-minute `--watch` heartbeat fired a list in which
**every single item was already marked `resolved`**.

## The defect

The filter selects a row if it is an escalation **or** it is unread:

```awk
# resolved/closed items are already off the inbox, so no explicit exclusion needed.
if (type=="escalation" || status=="unread")
```

The `status=="unread"` branch is correctly status-guarded. The `type=="escalation"` branch is **not
guarded at all** — it matches an escalation in any state, including `resolved`.

The comment states the premise that makes this safe. **The premise is false.** Measured on plain
`dispatch list` (no `--all`) in this repo:

| type | status | rows |
|---|---|---|
| dispatch | resolved | 34 |
| **escalation** | **resolved** | **30** |
| pr-submit | resolved | 6 |
| dispatch | read | 5 |
| pr-submit | read | 2 |

77 rows, **70 of them resolved**. Resolved items are emphatically *not* "off the inbox" — `dispatch
list` returns the full history, and `--all` widens it further rather than being what includes resolved.

## What it produces

```
REMAINING: 30 blocker(s) across 2 agent(s) + 0 open issue(s) + 0 parked dispatch(es)
           — Do NOT rest until all clear.
ESCALATE principal #4   (agent blocked — clear it or flow up)
ESCALATE principal #10  (agent blocked — clear it or flow up)
…28 more…
```

Dispatch #4 was resolved long ago. Every one of the 30 is resolved. Verified independently against
`dispatch list --all`, which prints `resolved` for each.

Applying a status guard to the escalation branch takes the count from **30 to 0**, and there is
genuinely nothing outstanding — the only non-resolved rows are 7 with status `read`, which are neither
escalations nor unread and correctly match neither branch:

```awk
if ((type=="escalation" && status!="resolved" && status!="closed") || status=="unread")
```

## Why this matters more than a wrong number

**It cannot be cleared by doing the work.** Resolving an already-resolved dispatch is a no-op, so the
heartbeat will fire this identical list every 15 minutes forever. The tool's own instruction — *"Do NOT
rest until all clear"* — describes a state that is now unreachable.

Three consequences, in increasing order of harm:

1. **It instructs 30 spurious escalations to the principal.** A coordinator that follows the printed
   plan literally interrupts a human 30 times about work already finished. I did not follow it.
2. **It trains the coordinator to ignore the surface.** A signal that is always red carries no
   information, and the correct response to it — ignore the whole block — is indistinguishable from the
   failure mode it exists to prevent.
3. **A real blocker arrives into 30 lines of noise.** This is the actual danger. The sweep is the
   fleet-wide safety net that is *deliberately unfiltered by address* precisely so it catches what the
   per-agent inbox gate misses (session-resume, Step 3). Burying a genuine `PARKED → you` line under 30
   permanent false positives defeats the one property that made it worth running.

Note the interaction with the dispatch monitor's trust contract: that contract says silence means a
clear inbox *while the monitor is alive*. The blocker heartbeat is the level-triggered companion to it,
and a level signal that can never return to zero is not a level signal.

## Suggested fixes, in order

1. **Status-guard the escalation branch** (one line, above). This is the whole bug.
2. **Make the terminal-state set explicit and shared.** `blocker-sweep` hard-codes its notion of
   "still open" in an awk condition while `dispatch` owns the lifecycle. Have `dispatch list` take a
   `--open` flag, or emit `--json` with a boolean, so the two cannot drift.
3. **Do not infer state from a listing's default scope.** The comment's assumption — that a plain
   `list` is the open set and `--all` is history — is a reasonable reading of the CLI that happens to be
   wrong. A consumer deciding whether a human gets interrupted should read the status field, never the
   choice of subcommand flags.
4. **Print the status in the `ESCALATE` line.** `ESCALATE principal #4 (agent blocked …)` asserts a
   state it never checked; `#4 escalation/high/resolved` was right there in the `BLOCKER` line directly
   above it, and the two lines contradict each other in the same output.

## Cross-reference

Same family as the four ambient-state reports filed 2026-09-16/17 (monitor identity from `cwd`,
receipt verification from the working copy, quality-config resolution, the tracked monitor registry) and
the `session-preflight` / `worktree-sync` ref disagreement. The shared shape: **a tool derives a
correctness-relevant answer from something adjacent to the thing it is describing** — here, from which
subcommand flags were passed rather than from the status column it had already parsed into `$4`.
