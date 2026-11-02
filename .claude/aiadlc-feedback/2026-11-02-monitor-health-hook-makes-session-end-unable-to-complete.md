---
date: 2026-11-02
from: biofm/matthew-mo/lung-on-chipsim
area: hooks/monitor-health.sh vs skills/session-end
severity: a-sanctioned-skill-cannot-complete
---

# The `monitor-health` Stop-hook makes `/session-end` unable to complete: the skill stops monitors by design, the hook refuses to let the turn end while they are stopped

## What happened

`/session-end` ran correctly and to completion. Its own documentation states that
`--framing resumption` **stops monitors**, and `tools/session-pause` reported `status=ok`:

```
handoff_path=.../lung-on-chipsim-handoff.md
archived_previous_handoff=.../history/handoff-20261102-213752-113.md
framing=resumption
status=ok
```

The handoff was written with `mode: resumption` and a concrete `next-action`, the tree was clean,
and the skill's final instruction — *"Report ... then: **Safe to `/compact` and/or `/exit`.**"* —
was followed.

**Turn-end was then blocked by the `monitor-health` Stop-hook:**

> Your background dispatch monitor is not running — it must never be off. CTO directives and
> replies are silently queueing unseen... Restart it before ending the turn.

So the hook demands the exact state `/session-end` was designed to produce the opposite of. To end
the turn at all I had to re-arm the dispatch monitor, which **immediately undid the teardown the
skill had just performed.** The session is now logically paused (handoff written, archived, clean
tree) but mechanically still watching.

## Why this is a contract conflict rather than a nuisance

The two components encode contradictory invariants with no shared state to arbitrate them:

- `skills/session-end` → *a deliberately paused session SHOULD have monitors stopped.*
- `hooks/monitor-health.sh` → *a monitor that is off at turn-end is ALWAYS an error.*

The hook has no way to distinguish **"the monitor died"** (the failure it exists to catch) from
**"the monitor was stopped on purpose, one tool call ago, by the framework's own teardown skill"**.
Both present identically at the Stop check.

**Consequence:** `/session-end` cannot reach its documented end state through normal turn
completion. An agent can only honour the skill by violating the hook, or honour the hook by
reverting the skill. The practical escape is for the *human* to `/exit`, which stops the monitor
outside the hook's reach — meaning a skill advertised as agent-runnable actually requires a human
action to finish.

## Repro

1. In a worktree agent session with a live dispatch monitor, run `/session-end`.
2. Let `tools/session-pause --framing resumption` complete (`status=ok`).
3. Write the handoff, report, and attempt to end the turn.
4. The Stop hook blocks with the monitor-health message.
5. Re-arming the monitor is the only way to end the turn — reverting step 2's monitor-stop.

## Suggested fix, in preference order

1. **Give the hook a pause marker to read.** Have `session-pause --framing resumption` write a
   session-scoped marker (next to the handoff, or in the monitor registry) meaning *intentionally
   paused*, and have `monitor-health.sh` pass when it is present and newer than the last monitor
   stop. This preserves the invariant for its real target — a monitor that died — while letting a
   deliberate teardown stand.
2. **Have the hook exempt the turn in which `session-pause` ran**, keyed on the pause commit or the
   archived-handoff timestamp.
3. **Failing either, correct the documentation**: `/session-end`'s "Safe to `/compact` and/or
   `/exit`" should say that the monitor must be re-armed to end the turn and that only `/exit`
   actually completes the teardown — so the next agent does not spend a turn discovering the
   conflict.

## Related, and distinct from

`.claude/aiadlc-feedback/2026-10-31-the-always-on-monitor-invariant-is-enforced-only-at-turn-boundaries.md`
reports that the invariant is enforced *too weakly* — only at turn boundaries, so a monitor can be
dead for most of a turn unnoticed. **This is the opposite failure:** at the one moment the
invariant is enforced, it fires against the framework's own sanctioned way of switching it off. The
two reports are complementary and a fix should satisfy both.

## Side observation, same component

The instincts hook rewrites a **tracked** file (`last_reinforced` in
`.aiadlc/instincts/*.md`) on every `dispatch-monitor` / `blocker-sweep` invocation, and the
`context-commit-check` Stop-hook blocks turn-end on a dirty tree. Together they manufacture one
`misc:` commit per monitor cycle — this session produced several, none carrying any work. Low
severity, but it is history noise generated purely by the monitoring layer observing itself.
