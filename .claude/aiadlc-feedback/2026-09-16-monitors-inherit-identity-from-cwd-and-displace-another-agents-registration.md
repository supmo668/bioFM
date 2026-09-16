# Monitors resolve their agent identity from `cwd`, so arming one from a worktree registers it as the *worktree agent* — silently displacing that agent's slot and leaving the arming agent unmonitored

**Tools:** `tools/dispatch-monitor`, `tools/issue-monitor`, `tools/blocker-sweep --watch`,
`config/monitor-pids.json`, `hooks/monitor-health.sh` (plugin 0.56.0)
**Severity:** high — it breaks the monitor trust contract in the one direction that is invisible

## What happened

The CTO session re-armed its three monitors after they expired. The Stop hook then blocked:

```
Your background dispatch monitor is not running — it must never be off.
```

The processes *were* running. The registry showed why:

```json
{"monitor_type": "dispatch", "pid": 54304, "agent_address": "biofm/matthew-mo/lung-on-chipsim"}
{"monitor_type": "issue",    "pid": 93187, "agent_address": "biofm/matthew-mo/cto"}
{"monitor_type": "blocker",  "pid": 19569, "agent_address": "biofm/matthew-mo/cto"}
```

**No `dispatch` entry for `biofm/matthew-mo/cto`.** The CTO's own dispatch monitor had registered
itself as `biofm/matthew-mo/lung-on-chipsim`, because the shell's `cwd` at arm time was
`worktrees/lung-on-chipsim/projects/lung-on-chipsim` — the CTO had `cd`'d there minutes earlier to
verify a worktree agent's commits, which is ordinary coordinator work.

The blocker monitor confirmed it in its own output, announcing
`── self-nudge · lung-on-chipsim · every 15m ──` from a watch the **CTO** had started.

## Why this is worse than a mis-labelled process

Two failures at once, and the harmful one is silent:

1. **The arming agent is left unmonitored.** `monitor-health` looks for *its* address, finds nothing,
   and blocks turn-end. Loud, and therefore fine.
2. **The other agent's registration is overwritten.** The worktree agent's `dispatch` slot now points
   at a process belonging to a different session. If the CTO's process dies, `monitor-health` for the
   *worktree agent* reads a dead pid — or worse, a live one that is not its monitor. Its inbox can be
   unwatched while its registry says it is covered. **Nothing announces this.**

The trust contract is "silence + monitor alive ⇒ inbox clear". Failure 2 makes *alive* unverifiable
for an agent that did nothing wrong.

## Repro

1. As agent A (e.g. the CTO in the main checkout), `cd` into a worktree owned by agent B.
2. Arm any monitor without changing directory back.
3. `config/monitor-pids.json` now records that monitor under **B's** address; A has no entry.
4. A's Stop hook blocks; B's registry entry has been replaced.

## Workaround in force

Arm every monitor with an explicit directory change, never relying on the ambient shell:

```bash
cd /path/to/main/checkout && "<plugin>/tools/dispatch-monitor" --include-collab
```

## Suggested fixes, in order of preference

- **Resolve identity from the agent, not the directory.** The monitor already knows which agent
  started it in every other respect; `cwd` is a proxy that is wrong whenever a coordinator inspects a
  worktree — a normal, encouraged action.
- **Refuse to overwrite another address's slot.** A registration whose resolved address differs from
  the existing holder of that `monitor_type` should fail loudly, not replace it. Displacement is
  never the intent.
- **Record the arming agent alongside the resolved one**, so `monitor-health` can say *"a dispatch
  monitor is registered for this address, but it was started by a different session"* instead of
  reporting healthy.
- At minimum, **print the resolved address at startup** (`registering as biofm/matthew-mo/...`), so a
  mis-resolution is visible in the first line of output rather than inferred from a Stop-hook block
  twenty minutes later.
