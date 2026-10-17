# `/session-end` stops the monitor that the `monitor-health` Stop hook refuses to let the turn end without

**Date:** 2026-10-17
**Filed by:** biofm/matthew-mo/cto
**Plugin:** airdlc 0.82.0
**Severity:** structural — the documented teardown skill cannot complete its own turn

## What happened

Ran `/airdlc:session-end cto` at a clean boundary. It worked: `session-pause --framing resumption`
returned `status=ok`, archived the prior handoff, and — per its own documentation — **stopped the
monitors**. I wrote the resumption handoff, verified it read back, reported "Safe to `/compact`
and/or `/exit`".

The `monitor-health` Stop hook then **blocked turn-end**:

> Your background dispatch monitor is not running — it must never be off. … Restart it before
> ending the turn: run `/session-resume` … or `/monitor-dispatches`.

So the hook's remedy for having run the teardown skill is to run the **startup** skill. I re-armed
the monitor to clear the block, which means **the session ends with a live monitor and an archived
handoff that says the monitor is stopped** — the opposite of what `/session-end` is for.

## The contradiction, stated plainly

| surface | contract |
|---|---|
| `skills/session-end/SKILL.md` → `tools/session-pause --framing resumption` | "stops monitors (when the monitor layer is installed)" |
| `hooks/monitor-health.sh` (Stop hook) | a dead dispatch monitor **blocks** turn-end; "it must never be off" |

Both are working as written. `/session-end`'s entire job includes stopping the monitor, and the Stop
hook fires on the same turn and forbids exactly that state. There is no ordering that satisfies
both, because the hook runs *after* the skill's last action by construction. The skill is
advertised as idempotent and safe to re-run; re-running it reproduces the block every time.

## Why it matters beyond the annoyance

1. **The teardown surface cannot be trusted to leave the state it reports.** A session that ends via
   `/session-end` now ends with monitors *running*, not stopped. Whatever `session-pause` was
   stopping them for (clean reap, pid-registry hygiene, not leaving an orphan process polling a
   SQLite DB after the session is gone) does not actually happen on the normal path.
2. **The handoff is written before the block and is therefore wrong.** I wrote "The dispatch monitor
   is STOPPED" into the handoff, truthfully, then was forced to make it false. Every archived
   `/session-end` handoff in this repo plausibly carries the same inverted claim.
3. **It trains the operator to treat the Stop hook as noise.** This is the same failure mode already
   filed on 2026-09-27 about `dispatch-monitor`'s variant-identity warning crying wolf: a guard that
   fires on a correct, sanctioned action is a guard people learn to click through. `monitor-health`
   is the liveness half of the silence-means-clear trust contract; it should not be the thing that
   fires when you deliberately shut down.

## Proposed fixes (any one closes it)

1. **Let the teardown declare intent.** `session-pause` writes a short-lived "session is ending"
   marker (or sets `SESSION_ENDING=1` in the registry it already owns); `monitor-health.sh` fails
   open while that marker is fresh. Smallest change, keeps both contracts honest.
2. **Have `monitor-health.sh` skip when the current turn invoked `/session-end`.** The hook already
   reads `stop_hook_active` for its loop guard, so it has turn context to work with.
3. **Stop stopping the monitors in `--framing resumption`.** If the fleet rule really is "must never
   be off", then teardown should leave them armed and `session-pause` should drop that step — and
   `/session-end`'s docs should say so, instead of promising a stop it is not allowed to deliver.
4. **At minimum, make the hook's remedy correct.** Telling the operator to run `/session-resume`
   (which syncs, preflights and runs a full catch-up sweep) to undo the last step of `/session-end`
   is a much larger action than the situation needs; `/monitor-dispatches` alone is the right
   pointer, and even that should not be needed at a deliberate shutdown.

## Evidence

- `tools/session-pause --framing resumption --trigger session-end` → `status=ok`,
  `commit_sha=none`, `archived_previous_handoff=.claude/usr/matthew-mo/cto/history/handoff-20261017-085727-055.md`
- Stop hook command: `bash "${CLAUDE_PLUGIN_ROOT}/hooks/monitor-health.sh"`
- Re-armed after the block: `dispatch-monitor --include-collab --supervise --interval 60`
  (the 60s interval is the mitigation from
  `2026-10-16-dispatch-monitor-poll-interval-is-shorter-than-its-own-query.md`)
- Repo: bioFM, branch `main`, tree clean at `ddd0f04`
