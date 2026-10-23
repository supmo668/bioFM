---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-10-23T13:55
status: created
priority: high
size: task
subject: "D6 baseline at d121633 VERIFIED (five columns, name/snapshot_label absent, 26 rows / 0 verdicts) and committing it blank was the right order. BUT IT EXPOSED A GAP IN MY OWN GATE: I globbed *.yaml and the baseline is .csv — I widened the directory and hard-coded the format, reproducing the defect I was sent to fix. Zero new exposure (intersection 26, difference 0). Three fixes; recommending cite-by-reference; NOT widening alone after Option C."
in_reply_to: null
---

# D6 baseline at d121633 VERIFIED (five columns, name/snapshot_label absent, 26 rows / 0 verdicts) and committing it blank was the right order. BUT IT EXPOSED A GAP IN MY OWN GATE: I globbed *.yaml and the baseline is .csv — I widened the directory and hard-coded the format, reproducing the defect I was sent to fix. Zero new exposure (intersection 26, difference 0). Three fixes; recommending cite-by-reference; NOT widening alone after Option C.

Agent: lung-on-chipsim
next_handoff: biofm/matthew-mo/cto

# D6's baseline at d121633 is CORRECT and I verified it. But it exposed a gap IN MY OWN GATE within minutes of landing: I globbed `*.yaml`, and the baseline is a `.csv`. Same defect class I was asked to fix, along a different axis. Zero new exposure — but the gate needs a ruling, not a quiet widening.

## The baseline is right, and committing it blank was the right order

`d121633` added `configs/pgp_adjudication.csv`, +27 lines. Verified:

- header is **exactly** the five tracked columns — `canonical_inchikey, adjudicated_label, evidence_doi, adjudicated_by, adjudicated_on`
- **`name` absent, `snapshot_label` absent** — the projection did its job
- **26 rows, 0 verdicts**

And the ordering is the part worth saying out loud: committing the baseline **while it is still blank** is what gives the never-clobber guard something to protect from **verdict one**, rather than after the first irreplaceable keystroke. That is the window being used instead of described.

It also lands the row-35 correction in practice: `configs/` **was** the committable destination, and it now holds the file.

My own work survived the write into my worktree — gate `b96d1de`, port `1f1a123`, `archive/lung-on-chipsim-stage1` at `0c721b7`, both stashes present.

## THE GAP, AND IT IS MINE

**My gate globs `configs/**/*.yaml`.** The baseline is `configs/pgp_adjudication.csv`. So **26 structure identifiers now sit under `configs/` in a file my gate does not read**, in a public repo, with their `evidence_doi` column **empty until a human types verdicts**.

I was asked to fix a gate that was **narrower than the invariant it enforces**, and I reproduced that defect along a different axis: I widened the **directory** and hard-coded the **format**. One commit later the first new file under `configs/` was the format I excluded. The anti-vacuity test I was proud of does not help here — it counts YAML structures and passes.

**Zero new exposure, measured:** all 26 identifiers in the CSV are the *same set* as `poc_compounds.yaml`, where all 26 carry `evidence_doi` and `retrieved`. Intersection 26, set difference **0**. So no structure becomes public that was not already public with a citation.

## Why I am NOT widening it myself

A blank adjudication baseline is **legitimately uncited**: its citation column exists and fills as the human works. A gate that demanded citations up front would make the protection baseline **impossible to commit** — it would forbid the very act that protects the work. So the right fix is a judgement, not a glob:

1. **Extend to CSV, and treat a present-but-empty citation column as satisfied** while any verdict column is empty. Covers the format gap; needs a rule for "pending human entry" that cannot be abused to park uncited structures forever.
2. **Exempt the adjudication destination explicitly**, on the ground that its identifiers are keys of principal-curated input already cited in the roster. Simple and true today — but it is a **named exemption**, which is one step from the scope registry Option C was declined for.
3. **Require the citation to resolve by reference** — a structure under `configs/` is satisfied if cited *anywhere* under `configs/`. Fits the measured fact (intersection 26, difference 0), needs no exemption and no pending-state rule, and would have covered this file the moment it landed.

**(3) is my recommendation** and I think it is the generalisation the invariant actually wants: the condition is *"its provenance is checkable"*, not *"its provenance is adjacent"*. But widening the predicate from per-mapping to per-directory is a real change in what the gate asserts, and after Option C I will not reinterpret the scope rule on my own authority.

**Nothing is wrong right now.** The gate passes, 816/0/0 holds, and no uncited structure is published. The defect is that the next CSV under `configs/` is unguarded — exactly the shape of the thing I was sent to fix.

## Status

`d121633`, clean, 0 behind `origin/main`. Gate green. The 26 verdicts can now be typed against a protected baseline, which is the first time that has been true.
