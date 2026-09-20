---
type: plugin-feedback
target: aiadlc plugin (bioFM) — dispatch / agent-wake
plugin_version: 0.56.0
reporter: bioFM/matthew-mo/cto
date: 2026-09-20
scope: plugin / operating-system behavior — NOT repo/app work
---

# `agent-wake` disagrees with `lsof -d cwd` liveness, and acting on it spawns a second writer under one identity

**Self-caused, not reported by another agent.** I verified this against my own tool calls in one
continuous turn sequence.

## What happened

1. Before dispatching, I checked worktree liveness the correct way (rule 16 from earlier this
   session: `pgrep` cannot see a session's cwd, use `lsof -a -p <pid> -d cwd`). Found **3 live
   pids** with cwd in `worktrees/lung-on-chipsim`, including `pid 80498`, a `claude` process
   alive since **Wed Sep 16 13:58** — four days of continuous conversational history.
2. I used that finding correctly: I did *not* write directly into the tree, and dispatched
   instead.
3. `dispatch create` reported the recipient as **IDLE** and offered `agent-wake`. I ran it.
   `agent-wake` launched a **second, headless** process (`pid 35618`, later exited) into the
   **same worktree**, under the **same agent identity**, with **zero awareness** of pid 80498's
   four days of history.
4. Both processes had commit access to the same branch. The headless one did the actual T18
   work — wrote the file, staged it, committed. A concurrent registry-refresh commit (unrelated
   defect, filed separately) then swept the staged roster into a mislabelled commit.
5. Pid 80498 resurfaced later, found commits on its branch it had not made, and correctly
   flagged it as a coordination-integrity finding in its report back to me — without knowing the
   second writer was a process I had personally just spawned.

## Root cause

**`agent-wake`'s "IDLE" determination and `lsof -d cwd` process liveness are two different
signals, and they disagreed.** I had the stronger signal (direct OS-level cwd match, gathered
one message earlier in the same turn) and acted on the weaker one (`agent-wake`'s own liveness
check, whatever it is — task-queue state, last-activity timestamp, something else — not
inspected here) without reconciling the two.

This is the same shape as five ambient-state defects already filed this session (monitor
identity from `cwd`, receipt verification from the working copy, quality-config resolution, the
tracked monitor registry, `blocker-sweep` counting resolved escalations): **a tool derives a
correctness-relevant answer from something adjacent to the thing it describes.** Here the
adjacent thing is *whichever liveness check `agent-wake` runs*, and the two checks in this
session disagreed by a wide margin — one said "alive four days", the other said "idle."

## Why it matters beyond this one incident

The two writers **shared one registry slot** (`(monitor_type, agent_address)`), which is the
exact defect already filed under *"the monitor registry is a tracked git file"* — but that
report characterized the collision as arising from separate machines or separate `cwd`s. This is
a **third mechanism** producing the same class of harm: two live sessions, same machine, same
worktree, same identity, spawned by a coordinator action (`agent-wake`) that should have refused
or warned instead of proceeding.

**CORRECTED 2026-09-20, same day, before this file left `main`.** This section originally
repeated the agent's own claim that the collision "retroactively explains a week of monitor
churn ... attributed solely to merges." **That claim is false and I endorsed it without checking
the dates myself** — the agent caught and corrected it in a follow-up (dispatch #182) before I
did. Measured: the headless session's three commits span **13:32:31–13:41:40 on 2026-09-20**,
nine minutes. The dead-pid findings this was said to explain (pids 54304 etc.) are dated
**2026-09-16/17** — days before `agent-wake` ran here. The collision this report describes
explains only its own nine-minute window; the earlier churn is the tracked-runtime-state defect
already filed on 2026-09-16/17, unrelated to this one.

Leaving the error and this correction both visible rather than silently rewriting the section:
the failure worth naming is not the agent's over-broad first draft, it is that **I accepted it
without opening `git log` myself** — the same "check the artifact before asserting a claim about
a live state" rule (r2.35) both of us were citing at each other in the same exchange.

## Suggested fixes, in order

1. **`agent-wake` should check `lsof -d cwd` (or equivalent) before launching, and refuse (or
   warn loudly) if a process already has that worktree as its cwd.** The check I did by hand is
   exactly the one `agent-wake` should do internally before creating a second writer.
2. **`dispatch create`'s "recipient IDLE" message should say what it checked** — the same
   transparency gap already filed against `monitor-register --verify` (prints nothing on
   success). If it had printed *what* made it conclude IDLE, the disagreement with my own
   `lsof` finding would have been visible before I acted on it, not after.
3. **A headless `agent-wake` session should identify itself distinctly in commit trailers** (a
   pid or session-id, not just the shared agent address), so a receipt or `git log` can
   distinguish "the interactive session did this" from "a headless wake did this" without
   needing the interactive session to notice commits it doesn't recognize.

## What I did to contain it

- Verified content integrity end-to-end (the roster survived the mislabelled commit intact,
  byte-identical from dispatch through to `HEAD`) before treating T18 as closed.
- Did not call `agent-wake` again this session without first re-checking `lsof -d cwd` myself.
- Told the agent plainly, in reply, that I caused Finding 2 — not left as an unexplained mystery
  in its own record.
