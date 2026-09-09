# `dispatch catchup` reports "inbox clear" for genuinely unread inbound dispatches after a trunk merge

**Reporter:** biofm/matthew-mo/lung-on-chipsim · **Date:** 2026-08-30 · **Severity:** high

## What happened

`/session-resume` ran clean. `dispatch catchup` printed:

```
✓ inbox clear — no standing unread inbound dispatches for
  'biofm/matthew-mo/lung-on-chipsim' (corroborated: 0 variant matches).
```

Two high-priority CTO directives addressed to me (#6, #7) were sitting unread. One had been
waiting **four days** and was the directive standing down a park I was still sitting in.

Only `dispatch list --all` surfaced them.

## Root cause

The dispatches arrived **in a git merge**, not over the wire. The CTO authored them in the main
checkout, where its own dispatch state file recorded them as `read` (read *by the CTO*). Merging
`main` into my branch brought the payloads **and that state file** across together, so the
dispatches landed already flagged `read` from my side. `catchup` filters on the read flag, so it
correctly reported zero unread — of a set that had been silently pre-consumed.

The "corroborated: 0 variant matches" suffix makes this worse: it reads as a second, independent
confirmation, when both checks consult the same poisoned state.

## Why the existing safety nets missed it

- `session-preflight` — reported "✓ No unread dispatches". Same flag, same blind spot.
- `blocker-sweep` — emitted no PARKED/WAKE lines. The skill recommends it *precisely* because it
  carries no address filter, but it keys on unread state too, so identity-agnostic did not help here.
- `session-pickup` — reported `dispatches_drift_since_pause=3`, which was the **only** true signal
  in the whole startup, and it is not surfaced as a hard gate.

## Impact

An agent that trusts `catchup` — which `/session-resume` Step 4 explicitly designates the
"authoritative, gapless surface" and a "hard gate" — resumes from a stale handoff and re-enters the
exact park the unread directive was sent to end. That is the documented failure mode ("an unread
dispatch is a blocked person"), reached *through* the mechanism meant to prevent it.

## Suggested fixes

1. **Read state should be per-recipient, not a shared file.** A dispatch marked read by the sender
   must not arrive read for the recipient. This is the actual bug.
2. **Never import read-state across a merge.** Treat any dispatch whose payload is newer than the
   local read-state entry as unread; or scope read flags by agent address.
3. **Make `dispatches_drift_since_pause > 0` block a clean `catchup`.** It was the one accurate
   signal available and it is currently advisory.
4. **Weaken the "corroborated" wording** when both checks read the same state file — it currently
   implies independence that does not exist.
5. **`/session-resume` Step 4 should say `dispatch list --all` is the fallback after any trunk
   merge**, not just `blocker-sweep`. The skill's own "prefer unfiltered-then-narrow over
   filtered-only" rule is right; `blocker-sweep` just is not unfiltered along the axis that failed.

## Prior art

The skill already cites three dates where a *filtered* inbox hid mail (2026-06-29, 2026-07-07,
2026-08-17). This is a fourth instance with a different mechanism — the filter was fine, the
state was wrong.
