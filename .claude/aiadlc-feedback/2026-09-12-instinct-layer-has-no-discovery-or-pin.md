---
type: plugin-feedback
target: aiadlc plugin (aiadlc-plugins)
plugin_version: 0.54.0
reporter: bioFM/main/cto
date: 2026-09-12
scope: plugin / operating-system behavior — NOT repo/app work
---

# Instinct layer: reinforcement without discovery, and no pin primitive

Surfaced while designing `/build-loop` (see `docs/superpowers/specs/2026-09-12-build-loop-design.md`),
an unattended requirement-to-function loop whose whole improvement story depends on the
instinct layer. Both findings are about the same subsystem and were proven against
`tools/instinct` and `hooks/hooks.json`, not inferred.

Context that matters: the alternative considered was installing `continuous-learning-v2`
alongside aiadlc. That was **rejected** — it would stand up a second store
(`~/.local/share/ecc-homunculus/`), a second confidence semantics (0.3–0.9 weighted vs
reinforce/TTL-decay), and a second SessionStart surface, leaving neither authoritative.
aiadlc's layer is the better substrate; these are the two things it is missing.

## 🟠 1. Instincts are reinforced but never discovered

**File:** `tools/instinct` (HELP block, line ~318); `hooks/hooks.json` Stop → `hooks/instincts-reinforce.sh`

**Symptom:** In an unattended run — an autonomous loop, `/cto-loop`, any overnight drain —
zero instincts are ever created. The learning layer produces nothing precisely in the
sessions that generate the most evidence.

**Root cause:** Proven from the CLI surface. `instinct` exposes
`capture · reinforce · match · list · surface · decay · prune · export`. Every path to a
*new* instinct runs through `capture`, which is an explicit act performed by a human or by
an agent that decides to invoke `/instinct-capture`. The Stop hook calls `instinct match`
against touched files and bumps confidence — it can only reinforce an instinct that already
exists. There is no observation path from tool-use activity to a candidate instinct.

The contrast is instructive: `continuous-learning-v2` hooks `PreToolUse`/`PostToolUse` into
an `observations.jsonl`, then distils candidates with a background Haiku agent. That
discovery half is the capability aiadlc lacks. Its storage and confidence model are *worse*
than aiadlc's — global rather than in-repo, and unversioned.

**Fix:** Add an observation → candidate path, keeping aiadlc's store and semantics:

```
instinct observe   --tool <name> --files "<paths>" --outcome <ok|fail>   # PostToolUse, async
instinct distil    [--since <n>] [--min-support 3]                       # Stop or SessionEnd
```

`observe` appends to `<store_dir>/observations.jsonl`; `distil` clusters recurring
correction/failure patterns into instincts at low starting confidence (0.4–0.5, below
`min_confidence` so they do not surface until reinforced). Gate both behind
`instincts.discovery.enabled` defaulting to `false`, so existing repos are unaffected.

**Effect:** Unattended runs accumulate durable, confidence-scored lessons without a human
present, which is the only condition under which an autonomous improvement loop can
actually improve.

**Status:** open

## 🟠 2. No pin/freeze primitive for reproducible attribution

**File:** `tools/instinct`; `agency.yaml` `instincts.*`

**Symptom:** No way to state which instinct set produced a given run. Any long autonomous
run is therefore unattributable: the agent's configuration mutated while it worked, and
afterwards there is no record of what it was at any point.

**Root cause:** The store is live and mutable — the Stop hook reinforces during a run and
`decay` rewrites confidence over time — and nothing snapshots or identifies its state. There
is no `pin`, `hash`, `freeze`, or `--as-of` in the CLI.

This has a direct analogue in this repo's own domain rules, which is why it was noticed:
ChipSim's replay test requires that the same config and seed reproduce the same result
exactly, and the chipsim-lbm-audit's R2 requires pre-registration "hash-sealed before any
model runs". A mutating instinct store breaks both at the agent layer.

**Fix:** Cheap, because `store_dir` defaults to `.aiadlc/instincts` — in-repo and not
gitignored. A tree SHA already identifies the set exactly:

```bash
instinct pin          # prints: git rev-parse HEAD:.aiadlc/instincts
instinct surface --as-of <tree-sha>   # read the set as it stood
```

`pin` is three lines over `git rev-parse`. `--as-of` is the genuinely useful half, since it
makes a recorded pin *resolvable* rather than merely recorded.

**Workaround in use:** `/build-loop` computes `git rev-parse HEAD:.aiadlc/instincts` itself
and writes it to the drain's run record. This works today and needs nothing from the plugin
— but every consumer wanting attribution will re-derive it, and none will get `--as-of`.

**Effect:** Autonomous runs become attributable and replayable, and the framework gains the
same pre-registration discipline it already asks domain work to follow.

**Status:** open
