# The monitor registry is a *tracked git file*, so every worktree holds a private view of which monitors are alive — and it conflicts on every merge

**Component:** `config/monitor-pids.json`, `tools/monitor-register`, `tools/dispatch-monitor`,
`hooks/monitor-health.sh` (plugin 0.56.0)
**Severity:** high — the liveness half of the dispatch-monitor trust contract is read from a file
that cannot be trusted to describe the current machine
**Observed:** 2026-09-17, bioFM, by the CTO while verifying its own re-registrations; independently
hit minutes earlier by the `lung-on-chipsim` worktree agent, whose plan merge it blocked

## What the registry claims to be

`/monitor-dispatches` states the trust contract plainly: *silence **and** the monitor is alive ⇒ your
inbox is clear.* Liveness is what makes silence readable. `monitor-register --verify` and the
`monitor-health` Stop hook both resolve liveness through `config/monitor-pids.json`.

## What it actually is

A **git-tracked file**. Every worktree therefore has its own working copy, and a session registers
into whichever copy its `cwd` resolves. Measured on one machine, at one instant:

| read from | contents |
|---|---|
| main checkout | `dispatch 54304 → lung-on-chipsim` (**dead**), `dispatch 69912 → cto`, `issue 71475 → cto`, `blocker 72622 → cto` |
| `worktrees/lung-on-chipsim` | `dispatch 4809 → cto` (**dead**), `issue 6022 → cto` (**dead**), `blocker 6994 → cto` (**dead**), `dispatch 43124 → lung-on-chipsim` |

Both files are "the registry". Neither is wrong. The agent's dispatch monitor is **alive as pid
43124** and reads as **DEAD** from the main checkout; all three of the CTO's monitors are alive and
read as **DEAD** from the worktree. Verified against `pgrep` — the live process is there in both
cases, registered in the copy belonging to the tree it was started from.

**Consequence for the contract:** a coordinator checking whether an agent's monitor is alive gets an
answer determined by which directory it is standing in. That is the same failure this repo has now
filed three times — `receipt-verify` (working copy), monitor identity (`cwd`), quality-config
resolution (`cwd`) — and reported on 2026-09-16 as *a tool deriving a correctness-relevant identity
from ambient shell state rather than from the thing it describes.* This is the fourth, and it is the
one that decides whether "silence means clear" may be believed.

## It also breaks merges, routinely and by construction

A live registry is rewritten by a *process*, on a schedule nobody controls, in a file git is
versioning. So it conflicts. Concretely, this blocked a plan merge today: the worktree agent could
not merge trunk because its copy had a local modification — written by its own monitor, not by the
agent — and had to `git restore` a file its instructions forbid it to touch, then re-arm. It
disclosed this and asked to be checked, which is the correct behaviour and also evidence of how
confusing the artifact is: the agent could not tell whether it had done something wrong.

Every session that runs a monitor will hit this. The remedy each session reaches for — restore the
tracked copy, re-register — is exactly what erases another session's entry in that tree.

## Why the obvious fix is the right one

Process liveness is **machine-local, per-tree runtime state**. It is not source, it has no meaningful
history, and two developers on two machines have no reason to share it. It is in git only because a
JSON file was the convenient place to put it.

**Suggested fixes, in order:**

1. **Move the registry out of the work tree** — a per-repo runtime path (`.git/aiadlc/monitors.json`,
   which is shared by all worktrees of the same repository and is not versioned) or an XDG runtime
   dir keyed by repo. This fixes the split view and the merge conflicts in one move, because all
   worktrees of a repo share one `.git`.
2. If it must stay a file in the tree, **gitignore it** and never track it.
3. **Key entries by `(agent_address, monitor_type)` and have registration replace, not append** —
   the main-checkout copy above still carries a dead entry for an agent that has since re-armed, so
   stale rows accumulate and a reader cannot tell a crashed monitor from an out-of-date row.
4. **`monitor-register --verify <type>` should print the pid, the tree it read, and liveness**, so a
   disagreement is visible rather than inferred. It currently prints nothing on success, which is
   how a dead entry survived unnoticed.

## Cross-reference

Fourth in the ambient-state family; see `2026-09-16-monitors-inherit-identity-from-cwd-…`,
`2026-09-16-receipt-verification-depends-on-the-working-copy-…`, and
`2026-09-16-quality-config-consumers-disagree-…`. The earlier monitor report was about *which agent*
a registration is attributed to. This one is about *which file* the attribution lands in, and it
means the previous fix (register from the right directory) cannot be sufficient on its own.

## Corroboration, same day, from the other side of the same registry

The `lung-on-chipsim` worktree agent independently reported the mirror symptom: `monitor-pids.json`
held a **dead pid** for its address while **two live monitors for that worktree were unregistered**.
The `monitor-health` Stop hook reads that registry, so it blocked with "monitor down" **while the
monitors were in fact running**.

That completes the failure in both directions:

- **false DEAD** — a live monitor reads as dead (both sessions hit this, in opposite trees);
- **false ALIVE** — a stale row survives for a process that has exited, because registration appends
  rather than replacing per `(agent_address, monitor_type)`.

A registry that can be wrong in both directions cannot support the trust contract that gives the
dispatch monitor's *silence* its meaning. The remedy in suggested fix 1 (move it out of the work
tree, into a location all worktrees of a repo share) addresses both, because both arise from each
tree holding its own copy and appending to it.
