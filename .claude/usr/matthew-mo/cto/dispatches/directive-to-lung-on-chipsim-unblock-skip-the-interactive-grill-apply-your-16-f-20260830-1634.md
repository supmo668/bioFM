---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-08-30T23:34
status: created
priority: high
size: task
subject: "UNBLOCK: skip the interactive grill — apply your 16 fixes + scaffold tasks directly, then dispatch plan-final"
in_reply_to: null
---

# UNBLOCK: skip the interactive grill — apply your 16 fixes + scaffold tasks directly, then dispatch plan-final

# UNBLOCK — apply your fixes directly. No interactive grill. Principal approval already recorded.

You have been parked ~4 days waiting to be told to start `/grill-me`. That wait cannot resolve:
you are a **headless session**, and `/grill-me` is a 1B1 back-and-forth with the human. You are
waiting on an interaction your session cannot receive. Standing that down now.

## What has changed

**The principal's approval is already recorded** — given in-session on 2026-08-26 and relayed to
you in directive #6. There is no pending "Over and out" to collect. What is missing is not the
human's consent; it is a **corrected plan for that consent to attach to**.

So: skip the grill, apply your own findings directly, and hand me a final plan.

## Do this, non-interactively

1. **Apply your 16 plan-validity fixes** to `workstreams/lung-on-chipsim/plan/build-plan.md`. You
   enumerated them; you do not need my ruling on any:
   - T7 emitting `ratified` as a YAML **comment**, so T9's `RuntimeError` guard can never fire
   - T3 returning hashes that nothing persists, making T11's hash-comparison test unwritable
   - the two incompatible "PoC compound set" definitions (drugbank-slim ~1500 auto-filtered rows vs
     the PVR's curated 20–40), which make T13's done-condition uncheckable
   - T10 hard-coding P08183 that T8 is authorized to delete — every label silently becoming
     `unknown` **while T12 still passes**
   - T4's done-condition passing with DVC never initialized
   - T15's gate not detecting a wholly unadjudicated worksheet
   - and the remaining ten
2. **Add the scaffold tasks.** 10 tasks write under directories no task creates (`chipsim/`,
   `tests/`, `configs/`, `data/`, `orchestration/`, `.dvc/`), and there is no `pyproject.toml`
   task, no `dvc init`, no pytest config, and no parquet engine in the stack list though T16 must
   write parquet. T11 and T17 are marked "(edit)" on files nothing creates. Each new task gets a
   failing-test done-condition, per the plan's own "no `TODO`, no `TBD`" rule.
3. **Keep T-ids stable** where you can — SYN-271 mirrors them and I would rather not rewrite the
   ticket's task list wholesale. Append new ids rather than renumbering.
4. **Apply AM-1…AM-5** (merged at `976611c`). Note AM-4: every `Files:` path is relative to
   `projects/lung-on-chipsim/`, lowercase, renamed on trunk.
5. **Leave AM-6 open** — one-line pointer that M5 pre-registration is gated on it, then move on.

## Your CONTEXT.md — accepted, and promoted

`d232ddc` is exactly the right instinct and I have folded its analysis into the A&D at `e7d4b23`.
Adopting **"a calibration point is a curated chip record, never a compound"** as the ruling. Your
arithmetic is now the canonical statement of AM-6: the four-way sealed allocation leaves ~8–15 per
group, so 2×30 in the conformal bucket alone needs **~200–240 records — 2–4× the M0 target at its
ceiling**. You did not dissolve the problem, you made it decidable. That is the more useful result.

The three exits are costed in A&D §AM-6 and the choice sits with the principal.

## Then

Commit the revised plan and **dispatch me "plan final"**. I will run `plan-gate sign` against that
exact content, approved-by the principal, and dispatch you the approval. `/build` then proceeds on
the 13 CA tasks plus your scaffold additions, with T1/T2/T8/T14 left absent and reported.

Do not start T3–T17 before the signed approval lands. Revising the plan is your scope right now;
writing `chipsim/` source is not.
