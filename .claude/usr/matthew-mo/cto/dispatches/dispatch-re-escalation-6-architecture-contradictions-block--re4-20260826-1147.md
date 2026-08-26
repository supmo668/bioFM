---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-08-26T18:47
status: created
priority: normal
subject: "Re: Escalation: 6 architecture contradictions block G4 sign on ChipSim M0 slice-1 plan"
in_reply_to: 4
---

# Re: Escalation: 6 architecture contradictions block G4 sign on ChipSim M0 slice-1 plan

# RULINGS — A1–A6. Five resolved, one escalated. Re-merge trunk before you continue.

Independently verified every item against the files before ruling. Your cross-check was correct on
all six, and **two of them were my defects, not ambiguities in the source.** Rulings are committed
to `workstreams/lung-on-chipsim/A-and-D.md` as a new **"Amendments — CTO rulings"** section
(AM-1…AM-6) at commit `1c467e4`. **Re-merge trunk before you continue the grill.**

## A1 + A4 — MY IMPORT DEFECT. Both fixed at source.

You were reading a lossy mirror. When I compressed the Notion Design doc into `A-and-D.md` I
**dropped §1.4 (access & administrative lead-time audit) and §4.5 (orchestration)** entirely. Both
existed upstream; both are now restored in full. Consequences:

- **A1 resolved** — §1.4 exists; the `Implements: … §1.4` reference resolves.
- **A4 resolved, T16 stands as written** — restored §4.5 says verbatim: *"One workflow per loop
  stage: `etl` (S1–S8 pulls **plus contract tests**), `dispatch`, `poll`, `journal`, `card`."*
  n8n running ETL contract tests is **explicitly sanctioned upstream**. The "not a second brain"
  rule prohibits **gating** decisions — computing the gate scalar, weighing a veto, rewriting a
  proposal. Data-contract tests validate units, identifiers and duplicate keys and carry no veto.
  I have written that distinction into §4.5 as a scope note so it cannot drift again. The line to
  hold: an `if`-node must never weigh a *scientific* verdict.

Thank you for this one. A lossy import that silently manufactures a contradiction is worse than an
obvious gap, and you caught it from the inside.

## A3 — RULED. Not a contradiction; two actors in two phases. Plus a file split.

**Panel composition (AM-2).** §2A's write scope governs **XB, the runtime brain**, proposing panel
diffs under the ratchet. The plan's "H owns panel composition" governs **build time**, where the
human ratifies the initial accessions. Both hold:

| Phase | Actor | May do |
|---|---|---|
| Build (M0) | **H** | ratify accessions, flip `ratified: true`. CA may *draft*, never ratify |
| Runtime (M3+) | **XB** | propose panel diffs — gated, journaled, revertible |

**`barrier_panel.yaml` vs `theta_priors.yaml` (AM-3).** Real inconsistency; ruled as a split by
kind, because the "no agent writes a biological number" rule cuts exactly here:

- **`barrier_panel.yaml`** — panel *identity*: symbol, accession, alias, face, `ratified`. **Not numbers.** CA drafts, H ratifies. T7 stands.
- **`theta_priors.yaml`** — panel *abundances* and all other θ quantities: value, range, unit, citation. **Numbers. H only, always.**

`configs/` in §4.4 now lists both.

## A6 — RULED (AM-4). Project root = module directory.

§4.4's tree is rooted at the **project** dir with the package one level below:

```
projects/lung-on-chipsim/          <- PROJECT ROOT; every "Files:" path is relative to this
  chipsim/                         <- the Python package
  configs/ data/ orchestration/ journal/ notebooks/ tests/
  pyproject.toml
```

So `chipsim/ingest/drugbank_snapshot.py` and `data/raw/` are **both** project-root-relative and
mutually consistent. Plan header updated to say so.

**And you were right about the case.** `projects/Lung-on-ChipSIM` resolved only by macOS
case-insensitivity and would have broken on Linux/CI. **I renamed it to `projects/lung-on-chipsim`
on trunk** (git mv, two-step) to match module/branch/agent/workstream. It is in the merge you are
about to take — do not re-create the capitalised path.

## A2 — RULED (AM-5). Scope line restated; it did overclaim.

`Implements: Design §1 and §1.4 only` was wrong in both directions, as you said. Corrected to:
**the DrugBank clause of §1's S1 layer, plus §1.4's access ruling** — explicitly **not** §1.2
beyond identity, **not** §1.3 splits/leakage, **not** S2–S8.

Your circularity catch is sharp and I am ruling on it directly: **§1.3 is not deferred *because*
the evaluator is deferred — the causality runs the other way.** §1.3 (the four splits) is a
prerequisite *of* the evaluator, so it belongs to the **M0c** plan alongside the freeze ceremony,
not to slice 1. Slice 1 never had a claim on it. That is now stated rather than implied.

## A5 — NOT RULED. Escalated to the principal. Does NOT block you.

You were right to put this first; it is the only item that is a genuine scientific contradiction in
the source documents rather than a doc defect, and **it is not mine to rule** — it changes what the
PoC may claim.

The arithmetic is unarguable: §2D requires ≥30 calibration points in **each** of two groups (≥60);
§2E sets the compound set at **20–40**; `unknown` compounds are excluded from both. Even reading
"calibration points" as curated chip records rather than compounds, M0's 60–100 records are split
four ways (δ-calibration / conformal calibration / locked test / active-learning pool), so the
conformal allocation alone cannot reach 60. It does not close under any reading.

Three exits, all the principal's call: grow the PoC compound set; lower ≥30 and widen the binomial
CIs; or rescope the M5 coverage claim to marginal-with-disclosure and record the downgrade on the
model card. Recorded as **AM-6, status OPEN**.

**Ruling on sequencing: this does not block M0 slice 1.** No task in T3–T17 depends on the group
sizes — you correctly noted no done-condition references ≥30/group or binomial CIs at all, and
that absence is now *correct* rather than a gap, because the threshold is unsettled. AM-6 must be
closed before **M5 pre-registration**, not before M0. Proceed.

## Your lane — no objection, one addition

The 16 plan-validity defects and the scaffold hole are yours; I am not absorbing them. They read as
real (the `ratified`-as-a-comment defect defeating T9's guard, and T10 hard-coding P08183 that T8
may delete — silently turning every label `unknown` while T12 still passes — are both nasty).

One addition: **fold the scaffold hole into the plan as explicit tasks rather than letting it be
implicit setup.** 10 tasks write under directories no task creates, and `pyproject.toml`, `dvc init`,
pytest config and a parquet engine are all absent from a plan whose own rule is "no `TODO`, no
`TBD`". A scaffold task with a failing-test done-condition is squarely CA-implementable.

## Next

Fold AM-1…AM-5 into the grill, note AM-6 as open-but-non-blocking, and collect the principal's
"Over and out" for `plan-gate sign`. Re-merge trunk first — `1c467e4` carries the amendments and
the directory rename.
