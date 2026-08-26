---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-08-26T09:34
status: created
priority: high
size: task
subject: "BUILD: ChipSim M0 slice 1 — data spine (SYN-271, 14 CA tasks, 4 human blockers)"
in_reply_to: null
---

# BUILD: ChipSim M0 slice 1 — data spine (SYN-271, 14 CA tasks, 4 human blockers)

# BUILD DIRECTIVE — ChipSim M0 slice 1 (data spine)

You own module `lung-on-chipsim` on branch `lung-on-chipsim`, worktree `worktrees/lung-on-chipsim`.
Run `/build` against the plan below. The definition, design and plan phases are **already complete**
— they were imported from Notion, not re-derived. Do **not** re-run `/define` or `/design`.

## Read first, in this order

1. `workstreams/lung-on-chipsim/PVR.md` — requirements & vision (why, and the acceptance bars)
2. `workstreams/lung-on-chipsim/A-and-D.md` — architecture (Part I: brain/environment/uncertainty) + construction (Part II: data, 7 losses, module stack, repo layout)
3. `workstreams/lung-on-chipsim/plan/build-plan.md` — **your task list: 17 tasks, T1–T17**

Linear: **SYN-271** — https://linear.app/syntropyhealth/issue/SYN-271/m0-slice-1-chipsim-data-spine-drugbank-snapshot-identity-barrier-panel
Project: https://linear.app/syntropyhealth/project/biofm-chipsim-lung-on-a-chip-in-silico-validation-b40af105a741

Notion remains authoritative for PVR/A&D; the in-repo files are mirrors. Source index:
https://app.notion.com/p/d419cffbca33420a9a7d39abbe3eb67b

## Scope — build exactly this, nothing adjacent

**Design §1 and §1.4 only:** the ChipSim data spine through the compound-identity and
barrier-panel layer, sourcing DrugBank from a pinned public 2015 snapshot so M0's contract
tests go green with zero administrative lead time.

**Your 14 CA tasks:** T3, T4, T5, T6, T7, T9, T10, T11, T12, T13, T15, T16, T17
(T1, T2, T8, T14 are human-owned — see the blocker protocol below.)

**Tech stack:** Python 3.11 · pandas · RDKit · PyYAML · pytest · DVC · requests · n8n CE · git.
**No GPU in this slice.**

**Explicitly NOT in scope** (each has its own plan; do not fold them in):
1. M0b — curation of 60–100 chip records (human-only, needs a protocol doc)
2. M0c — the frozen evaluator (needs splits first + a human signature ceremony)
3. ChEMBL / BindingDB / TDC / LINCS ingestion (T3–T6 repeated; after this proves the pattern)

## Hard rules — violations fail the quality gate

1. **No coding agent writes a biological number.** Every value in `configs/theta_priors.yaml`
   and `configs/assumptions.yaml` is human-entered with a citation. You write the schema and the
   validator that *rejects* an unsourced entry. Drafting the `barrier_panel.yaml` accessions in T7
   is allowed **only** because they land `ratified: false` and a human flips that in T8.
2. **Never create, edit or extend a curated chip record.**
3. **Never modify the frozen evaluator, split definitions, or a sealed allocation.** (The evaluator
   does not exist yet — do not create it here.)
4. **ChipSim never redistributes DrugBank.** The snapshot lands in `data/raw/`, DVC-tracked and
   git-ignored. `test_drugbank_not_vendored` is the technical control; it must actually fail if a
   TSV is force-added.
5. **The P-gp label is three-way and must NEVER infer a negative.** `pgp_substrate_label()` may
   emit only `'yes'` or `'unknown'`. Absence of an edge is **not** "not a substrate". `'no'` is
   assignable only by `adjudicate_pgp_labels()` with a citation. This is load-bearing: the M5
   uncertainty stack conditions its Mondrian coverage veto on this exact label, so a silently
   mislabelled group would surface as a coverage failure that looks like miscalibration.
6. **No `TODO`, no `TBD`.** Every task is one action with a checkable done condition.

## Blocker protocol — T1, T2, T8, T14 are human-owned

Build the code and tests *around* them; leave the human artifacts **absent**; report the blocked
set at the boundary. **Do not fabricate a PROVENANCE.md, a commit SHA, a UniProt ratification, or
an evidence DOI** — a fabricated DOI in T14 corrupts the M5 coverage claim invisibly, which is
precisely the failure this project exists to detect.

- **T1** (licence posture → `data/raw/drugbank/PROVENANCE.md`) and **T2** (pin the 40-char
  `gh-pages` SHA; audit observed `3e87872db5fca5ac427ce27464ab945c0ceb4ec6`) gate **T11**.
  Write T11's tests so they fail cleanly and legibly with the file absent.
- **T8** (ratify 7 UniProt accessions, flip `ratified: true`) gates **T9**. T9 must
  `raise RuntimeError` against an unratified panel — test that path, it is the deliverable.
- **T14** (adjudicate P-gp labels with DOIs) gates **T15**. T15 must raise when a `yes`/`no` row
  lacks `evidence_doi` or `adjudicated_by` — test that too.

## Expected completion path

`/build` → per task: implementer subagent + `/quality-gate` + `/iteration-complete`;
`/phase-complete` at the phase boundary (principal approval required there);
then hand the branch back with `/pr-submit`. I land it via `/pr-cto-land` against the QGR receipt.
Report the blocked human tasks explicitly in the hand-off so I can route them to the principal.

Do not push to the CTO branch and do not land your own PR.
