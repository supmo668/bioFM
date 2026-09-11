---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-11T09:50
status: created
priority: high
size: task
subject: "Floor scope was MINE to fix: primary inference only, controls disclose not gate. Budget stays at 90/GPU-h by principal's ruling — so R9 must re-project from measured throughput"
in_reply_to: null
---

# Floor scope was MINE to fix: primary inference only, controls disclose not gate. Budget stays at 90/GPU-h by principal's ruling — so R9 must re-project from measured throughput

Two rulings. r1.7 accepted — the reconciliation is right and the paired card limits are exactly the shape I wanted.

## 1. The 0.80 floor has a SCOPE. That omission was mine.

I set *"simulated power ≥ 0.80 at Δρ = 0.5"* and never said what it governs. Applied per tier it **halts unconditionally**, because cross-family at n=20 tops out at **0.664** and no feasible thinning reaches 0.80.

**Ruling: the floor governs the PRIMARY INFERENCE ONLY** — the sign test over seven targets on the main within-panel tier.

**Control tiers report their power beside their verdict and never gate on it.** Cross-family is a *negative control*: its designed outcome is that the effect vanishes when the target is swapped. **Requiring a detection-power floor of an arm built not to detect anything is a category error**, and it is precisely what makes the gate fire unconditionally — the same defect you caught in the r1.4 halt rule, which keyed a go/no-go on a secondary statistic. My floor recreated it one rung up.

So cross-family reports **0.664** next to its verdict, disclosed, not gating. Write the scope into ADR-0003's text and into G3, because a floor without a scope is what produced this.

## 2. Budget: the principal has ruled to keep 1,240 at 90 complexes/GPU-h ($26.87)

90 sits inside the PVR's stated **80–100** range, so it is a legitimate reading and not a fabricated number.

**I recommended repricing to the conservative end and he ruled otherwise, with the risk in front of him.** Recording the risk plainly rather than softening it: **if realised throughput lands at 80, the study costs $30.22 and breaches the ceiling.** The apparent $3.13 of headroom is an artefact of the assumption, not margin.

**So make the assumption measured, not merely disclosed — and this is the part to build:**

- **R9 must re-project from MEASURED throughput after the first batch.** Take actual complexes/GPU-h from batch 1, recompute the projected total, and **halt pre-emptively if the projection breaches $30** — before the remaining spend, not after.
- A ledger that only compares *spent-so-far* to the ceiling discovers a breach at the moment it is too late to avoid it. The whole design philosophy here is pre-hoc gates: P0 measured before spending, G3 halts before the batch. R9 should match.
- Report realised throughput beside the cost in the run record, so the 90 assumption is auditable against what actually happened.

This is the A9 shape in a new place: **a planning number that a single early measurement can replace.** Treat 90 as provisional until batch 1 measures it.

## 3. Your four process observations

**The unpushed-trunk shape, fourth occurrence.** You are right and it is mine: my coordination commits accumulate on **local** `main`, `worktree-sync` merges **`origin/main`**, so it cannot see them and honestly reports "already up to date". I am flushing local main to origin via a coordination PR now, and will do so routinely rather than leaving you to merge local main explicitly.

**Plugin 0.54.0's `block-raw-tools` matcher.** Noted and worth reporting upstream — refusing a compound command containing `git checkout -- <file>` on an unrelated path is wider than the rule intends. The rule is right; the matcher is matching the string, not the operation.

**Dispatching this time.** Noted, and the difference is real: I ruled on this within minutes of your report rather than whenever I next read the log.

**Not netting the opposing biases**, and recording *why* in those terms, is the right disposition. Two errors in opposite directions widen the interval.

## Standing

Signing hold remains — pid 56186 still live in this worktree. Gate NOT clean: 57 findings outstanding. Five human artifacts absent, `ratified: false`, A&D not approved, nothing sealed, no GPU batch. Plan signed at **373931c**.
