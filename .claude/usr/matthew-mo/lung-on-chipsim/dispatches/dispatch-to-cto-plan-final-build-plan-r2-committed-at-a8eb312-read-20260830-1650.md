---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-08-30T23:50
status: created
priority: normal
size: task
subject: "PLAN FINAL — build-plan r2 committed at a8eb312, ready for plan-gate sign (scope changes inside)"
in_reply_to: null
---

# PLAN FINAL — build-plan r2 committed at a8eb312, ready for plan-gate sign (scope changes inside)

Agent: lung-on-chipsim
Commit: a8eb312 (branch lung-on-chipsim)
File: workstreams/lung-on-chipsim/plan/build-plan.md

Directive #7 executed non-interactively. No grill was run; principal approval as recorded in #6 is taken as standing. Plan is final and ready for:
  plan-gate sign --workstream lung-on-chipsim --plan workstreams/lung-on-chipsim/plan/build-plan.md --approved-by "Matthew Mo"

## What changed (r1 -> r2)

Not 16 defects — 33. I re-derived the ten that were never written down via an independent adversarial audit of r1 against the A&D, PVR and CONTEXT.md. The six you named are confirmed real and fixed. Full table in plan section 7.

The four that matter most, none of which were in the original six:

D31 NO CANONICAL InChIKey. RDKit was declared in the tech stack and used by NO task. A&D 1.2 requires canonical InChIKey after salt-strip/neutralize/tautomer and says 'never join on name or raw SMILES'. Every downstream key (T10 labels, T13 worksheet, T14's 60-90min of human adjudication, T15) was on the RAW snapshot key. The plan's own Goal — 'through the compound-identity layer' — was unmet while all 17 done-conditions passed. New T5b; all downstream re-keyed on canonical_inchikey.

D8 NO TASK EVER FETCHED THE DATA. T3 wrote a fetch script; T4-T10 all presumed fetched data existed; the only task that pulled anything was T16, dead last. T4-T10 were unexecutable in plan order. New T4a, ordered before T4.

D22 REGENERATING THE WORKSHEET DESTROYED THE ADJUDICATION. T13 wrote pgp_adjudication.csv with empty verdict columns and no overwrite guard, while T16's ETL re-runs the pipeline end to end. One re-run erases T14's 60-90 minutes of citation-backed judgement, and no done-condition anywhere detects the loss. T13 now merge-preserves and raises on a vanished key.

D24 NOTHING CHECKED THE ADJUDICATION PRODUCED TWO USABLE GROUPS. The whole point of T14 is the M5 grouping variable, yet the plan could complete green with 2 yes / 0 no / 38 unknown. T15 now raises on an empty group; T17 renders pgp_groups_usable.

## Scaffold hole — closed

S1-S11 + S11a, 12 tasks, each with a failing-test done-condition. Verified on branch: projects/lung-on-chipsim/ held ONLY CONTEXT.md, .aiadlc-agent, .claude/. Added pyproject.toml, package skeleton, pytest config, tests/ + the three day-one modules, committed fixtures, configs/, data tree, project-level .gitignore, dvc init --subdir, a DVC remote, orchestration/n8n/, and the module files every '(edit)' marker pointed at.

Note S7: a blanket 'data/raw/' ignore also swallows data/raw/drugbank.dvc — the one file that must be committed for the snapshot to be recoverable from a clone. Ignore rules now negate the .dvc pointer, and T11 asserts it is tracked.

Also: dvc is NOT installed on this machine, and system python is 3.14.5 while the plan pins 3.11. S2/S8 will need an env that satisfies both.

## THREE THINGS NEEDING YOUR RULING — I applied a default, flag if wrong

1. NEW HUMAN BLOCKER: T18. Human tasks go 4 -> 5. 'PoC compound set' had two incompatible definitions — drugbank-slim (~10^3 auto-filtered rows) vs the PVR's curated 20-40. I took the PVR reading, which makes the roster a curation CLAIM no agent may write, so T18 (H, 30-45min, configs/poc_compounds.yaml) is new. The alternative keeps it agent-only but contradicts PVR L149 and inflates T14's human cost ~50x. I did not want to absorb a 5th blocker silently.

2. T16 DESCOPED. r1 required a provisioned, running n8n instance with a Python execution path (n8n has no native Python runtime), and a 'byte-identically' done-condition that is unfalsifiable — no committed baseline, no DVC remote, and parquet bytes are not stable across pyarrow versions. T16 is now 'export a workflow JSON whose five nodes each name an existing CLI entrypoint, and whose parquet matches a recorded sha256'. Provisioning + end-to-end execution deferred as T16a. This is a real scope reduction.

3. T-IDS: I kept every original T-id stable per your instruction. New work is S1-S11, S11a, T4a, T5a, T5b, T18, T19. Nothing renumbered. T2 now runs BEFORE T1 (T1 required a hash T2 produces — an ordering error), but neither id changed. SYN-271's task list needs the 8 new ids appended, not rewritten.

## AM conformance

AM-1 ok. AM-2 ok — D4's fix removes the hard-coded P08183 from Python; composition is configuration. AM-3 ok — 'ratified' is now a real field, not a comment. AM-4 ok — every '(edit)' target now exists. AM-5 ok — T5b is 1.2 IDENTITY, inside the boundary. AM-6 left OPEN with an M5 pre-registration pointer; D24's fix means T15/T17 now MEASURE the yes/no populations, so AM-6 can be closed against real counts rather than estimates.

## Standing down as instructed

Not starting T3-T17 or writing any chipsim/ source until the signed approval lands.

next_handoff: plan-approval dispatch, then I open with P0 scaffold (S1-S11), which is unblocked by all five human tasks.
