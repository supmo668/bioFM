---
name: codebase-routine
description: Run the expensive periodic codebase routines, but only when source change has earned them. Gates on SOURCE lines changed since the last recorded run, refreshes the knowledge graph, verifies the refresh did not silently degrade it, and reports which routines are due but cannot be auto-invoked.
when_to_use: 'Periodic maintenance, or the rank-1 maintenance step of a cto-loop iteration. Anti-trigger: do NOT run this to "freshen things up" on a quiet day — the gate exists to say no, and overriding it defeats the point.'
argument-hint: '[--threshold N]'
---

# Codebase routine

Three routines are worth running periodically and are too expensive to run on every change.
This skill gates them on **code change**, per the principal's ruling of 2026-10-31: *"too little
codechange ... should not engage in those expensive run."*

## Step 1 — the gate. Always first, never skipped

```bash
uv run python scripts/codebase_routine_gate.py
```

Exit codes are distinct so a caller can tell a refusal from a breakage: **0 = RUN**, **10 = SKIP**,
**1 = ERROR**. An ERROR is never read as either answer — fix the measurement, do not proceed.

On **SKIP**, stop and say so, including the gate's own estimate of when the threshold will be
reached. A window that correctly declines to run these is a good window.

**The exclusion list, not the threshold, is what makes this work.** Measured on this repo
2026-10-31: over 24 hours, source change was **32** lines while unfiltered change was **59,975**,
because a day's work here is mostly generated graph JSON, dispatch payloads and prose. Gated on the
unfiltered number these routines would fire every single day. Default threshold is 10,000 source
lines, which is roughly five weeks at the current pace of ~1,840 lines/week; the gate prints the
estimate so the number can be tuned against evidence rather than feel.

## Step 2 — knowledge graph refresh

Only on RUN. Invoke the `understand-anything:understand` skill.

### Step 2a — verify it, because its incremental path has silently degraded before

Record the counts **before** refreshing, then compare after:

```bash
python3 -c "
import json,pathlib,collections
d=json.loads(pathlib.Path('.understand-anything/knowledge-graph.json').read_text())
t=collections.Counter(n.get('type') for n in d['nodes'])
print('nodes',len(d['nodes']),'edges',len(d['edges']),'layers',len(d['layers']),'file-nodes',t['file'])
"
```

**A refresh that lowers any of those counts is a regression, not an update.** On 2026-10-30 the
incremental path discarded an existing graph and left 144 files unbatched from a stale cached
inventory; the only thing that caught it was comparing counts. If a count drops, say so and do not
record the run.

## Step 3 — record the run, so the next gate measures from here

```bash
uv run python scripts/codebase_routine_gate.py --record HEAD
```

Record **only** what actually ran and verified. Recording a run that degraded the graph moves the
baseline and hides the damage from the next gate.

## Step 4 — report what is due but cannot be automated

Two of the three routines cannot be put in an automatic sequence, and the routine must say so rather
than quietly skip them. Measured 2026-10-31:

| Routine | Status |
|---|---|
| `understand-anything:understand` | model-invocable; Step 2 runs it |
| `improve-codebase-architecture` | **`disable-model-invocation: true`** — only the principal can trigger it. Report it as DUE; never claim it ran |
| `continuous-learning-v2` | hook-driven and continuous by design; its setup is one-time, not periodic. Do **not** wire it as a recurring run |

**On the ordering.** The intended sequence was graph first, then architecture. There is no data
dependency: `improve-codebase-architecture` reads `GLOSSARY.md`, `docs/adr/` and `git log` hot spots
and spawns its own sub-agent to walk the code. It never opens the knowledge graph. Refreshing first
is still worth doing, because the architecture pass's findings then land in a repo whose graph is
current, but do not present the order as a prerequisite it is not.

**On the learning pass.** This repo already runs airdlc's own instinct system under
`.aiadlc/instincts/`, which gained two instincts and reinforced three in a single window on
2026-10-30/31. `continuous-learning-v2` is a second instinct system from a different origin. Two
systems writing instincts into one repo is a collision to decide, not a routine to schedule. Use
`/instinct-capture` and `/instinct-evolve` until that decision is made.

## Guardrails

- The gate's answer is the answer. Do not raise `--threshold` to force a run, and do not pass
  `--since` to manufacture a larger window.
- Source includes **tests**. A changed test changes behaviour.
- Prove the gate still works before trusting it, especially after editing the exclusion list:
  `uv run python scripts/codebase_routine_gate.py --self-test`. It asserts the classifier rejects
  eight known non-source shapes and accepts four known source shapes. A check that cannot be made to
  fail is not evidence.
