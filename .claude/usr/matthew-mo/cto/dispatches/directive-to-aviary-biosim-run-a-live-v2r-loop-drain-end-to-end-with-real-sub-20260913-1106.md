---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/aviary-biosim
date: 2026-09-13T18:06
status: created
priority: high
size: task
subject: "Run a live v2r-loop drain end-to-end with real subagents"
in_reply_to: null
---

# Run a live v2r-loop drain end-to-end with real subagents

You are the session that can do what the CTO cannot: spawn the sealed test-author and
implementer subagents a drain requires.

GOAL — one complete, genuine drain against a small register, with Weave spans, so the
loop's self-correction is demonstrable rather than merely designed.

SETUP
  export V2R_TRACE=1
  export WANDB_API_KEY=$(grep '^WANDB_API_KEY=' /Users/mo/github/personal/bioFM/.env | cut -d= -f2-)
  export WANDB_PROJECT=3m-m/Aviary-BioSim
  R="uv run --with pyyaml .claude/skills/v2r-loop/scripts/register.py"

SCOPE — keep the register SMALL (5-7 build units). This is a proving run, not the real
aviary environment. Suggested vision:
  'A SpendTracker that records per-call cost, totals it, loads a declared floor from
   config, raises BudgetExceeded above the floor, and survives a process restart.'

RUN
  Stage 1 alignment may be compressed — you may author spec.md, register.yaml and the
  interface skeleton directly rather than invoking /research. Do NOT compress stage 3.
  Stage 2: present the artifact set and get the principal's approval before draining.
  Stage 3: per unit, dispatch TWO separate subagents. The test-author receives the unit
  statement and the skeleton ONLY. The implementer receives the unit statement and the
  stub ONLY. Neither sees the other's output. Then $R seal, then $R close.
    close exit 0 = closed · 1 = retry to max_attempts then park · 3 = HALT, stop the drain.
  Never assert a close yourself. Only register.py closes a unit.

DELIBERATE FAILURE — make ONE unit genuinely hard so it parks. A parked unit with real
evidence and a park/U-nnn branch is the most convincing thing in the demo; a clean sweep
proves less.

AFTER
  $R drain-end --outcome completed, then query the Weave traces, capture what you learned
  as instincts, and report back to the CTO with: closed list, parked list, the run record
  path, and the Weave project URL.

CONSTRAINTS
  The repo is PUBLIC — never commit a secret. Never push (use /sync). Never land a PR.
  Reply to the CTO at the drain boundary.
