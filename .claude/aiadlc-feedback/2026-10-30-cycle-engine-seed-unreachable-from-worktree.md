---
date: 2026-10-30
from: biofm/matthew-mo/cto
area: tools/cycle-engine
severity: governance
---

# The arm-time authorizations live in state a worktree agent cannot read, so the agents they govern cannot verify them

## What happened

`/cto-loop` records the principal's arm-time authorizations in the cycle-engine seed. Those
authorizations are the operative permission text for the **worktree agents**, not for the CTO — they
say what an agent may draft, land and scope. But the state is resolved per role and per checkout.

From the CTO's main checkout:

```
$ tools/cycle-engine status --label cto-loop --json
{ "label": "cto-loop", "role": "cto", "status": "running", "iteration": 7,
  "seed": "... AUTHORIZATIONS ... (1) FINDINGS - agents may DRAFT findings and numbers ..." }
```

From the perturb-seq-eval worktree, at the same moment (agent's own report, dispatch #811):

```
$ tools/cycle-engine status --label cto-loop --json
cycle-engine[cto-loop]: not armed
```

No JSON, no seed, and a status that contradicts the live window.

## Why it matters

The agent did the right thing and it still could not comply. It reported, in writing: *"the seed text
is not reachable from my worktree while the loop is down. I continue to apply your #807 paraphrase;
the gap stays open on my side."* So the agent governed itself by a **CTO paraphrase of a principal
authorization** for an entire window, and said so. On a project whose core rule is that no agent
writes an unsourced value, the permission to draft values was itself unsourced at the point of use.

The second-order effect is worse than the first: `not armed` is not merely missing information, it is
**wrong information**. An agent that trusted it would conclude the window had closed and that its
standing authorizations had lapsed.

## Repro

1. CTO arms `/cto-loop` with authorizations in `--seed`.
2. From any worktree, run `tools/cycle-engine status --label cto-loop --json`.
3. Observe `not armed` while the window is running, and no seed.

## Suggested fix

Either resolve cycle-engine state from the repo root shared by the worktrees, or have `arm` write the
authorization text to a durable, agent-readable surface (the `approvals.md` the agent itself named) so
the text the agents are governed by is readable by the agents it governs. Failing both, `status` from
a non-owning checkout should report *unreachable*, never `not armed` — a false negative here revokes
permissions that are in fact live.

## Cause

Verified in-session: the authorizations are reachable from the owning role's checkout and not from the
worktree, and the two answers disagree about whether the window is running.
