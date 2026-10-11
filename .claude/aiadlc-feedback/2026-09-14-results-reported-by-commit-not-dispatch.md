# A worktree agent can complete a coordinator-assigned task and never report it — the framework has no gate for that

**Reporter:** biofm/matthew-mo/lung-on-chipsim · **Date:** 2026-09-14 · **Severity:** medium

## What happened

The CTO assigned the R5 pair-count power curve. I derived it, committed it, pushed
it — and sent no dispatch. The CTO found the result by reading the git log, and
said so:

> *"This landed as a commit with no dispatch. The work was fine; I found it by
> reading the log. **Send the dispatch** — a result I have to discover is one I
> might not."*

It was right, and the principal has since made it a standing instruction.

## Why this is a framework gap and not only my lapse

The framework has a **`coord-commit-check` Stop-hook** that blocks turn-end when a
dispatch *payload file* is uncommitted. So the traceability mandate is enforced in
one direction only:

- **write a dispatch but fail to commit it** → blocked at turn-end, loudly.
- **complete an assigned task and never dispatch at all** → nothing notices.

The hook guards the *record of* a report; nothing guards the *existence of* one.
And the asymmetry points the wrong way: an uncommitted payload is recoverable from
the dispatch DB, while an unsent report is invisible to everyone until a
coordinator happens to read the log.

This is the same shape as several defects this workstream has recorded in its own
design: **an absent result is not visible where the result would have been.** The
framework enforces that principle on dispatch payloads and not on dispatches.

## Repro

1. As a worktree agent, receive a `directive` dispatch assigning a task.
2. Complete it. Commit and push the work.
3. Do not create a dispatch.
4. End the turn. `coord-commit-check` passes (nothing uncommitted);
   `monitor-health` passes (monitor alive). No hook objects.
5. The assigning coordinator has no signal that the task is done.

## Suggested direction

Not a hard block — a worktree agent legitimately commits many times per dispatch,
and requiring one dispatch per commit would be noise. Two cheaper options:

- **A Stop-hook warning when the branch has advanced past the last outbound
  dispatch by more than N commits** on a work-item whose originating dispatch is
  still unresolved. Advisory, not blocking.
- **Or tie it to the dispatch that assigned the work:** if an inbound `directive`
  is marked read and its work-item has since gained commits, prompt for the
  closing dispatch. The ISCP DB already holds both halves.

The second is closer to the framework's own model — dispatch chains are supposed
to *close back to the coordinator*, and that intent is documented in the
worktree-agent class but has no mechanical support.

## Evidence

- CTO dispatch #87 (2026-09-11), quoted above.
- The commit it referred to: `60d6640` (R5 curve), pushed with no accompanying
  dispatch; the follow-up dispatch was only sent after the CTO asked.
- `hooks/coord-commit-check.sh` — enforces the committed-payload direction.
- `hooks/monitor-health.sh` — enforces listening, not reporting.
