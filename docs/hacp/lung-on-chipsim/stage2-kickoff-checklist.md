# Stage 2 kickoff checklist — ChipSim (lung-on-chipsim)

<!-- HACP Checklist · Section = build · L1 — Review · Indexed by "ChipSim (bioFM) — Index".
     SOURCE OF TRUTH: the Notion row (principal, 2026-10-03). This file mirrors it; see notion-map.json. -->

**Kind:** Checklist · **Layer:** L1 · **Holds:** the pre-conditions that flip the build phase from parked to active, in the order they can be satisfied · **Reaches:** [§decision](decision.md) (the ledger), [§build](build.md)

Tick an item only against the artifact it names. An item with no artifact stays open.

## Week 0 — governance (by 2026-10-07)

- [x] **Roster approved as final** — 26 entries; recorded 2026-10-03 as a standing assumption from the principal's session instruction; the CTO carries it into the approval log as a signed row
- [ ] **A2** archived Stage 1 tip pushed to `archive/lung-on-chipsim-stage1` on `origin` (principal, 2 min)
- [ ] **A1** successor branch `lung-on-chipsim-stage2` cut from `main`; science-bearing files taken by content from `c04e701` and the archived tip; guard machinery left where it closed (CTO)
- [ ] **Plan r3** signed by the principal; `plan-gate verify` green on the successor branch
- [ ] **Clean suite re-measurement** on the successor branch, no concurrent pytest processes, recorded with its wall time (CTO; owed since 2026-10-01)
- [ ] **C1 / C2 / C3** ruled: SLC15A1; AM-6 contingency; identifier-constraint retroactivity beyond row 59
- [ ] **Floor landed** — `docs/hacp/lung-on-chipsim/` merged to `main` so every `Local path` on the ChipSim rows resolves

## Week 1 — the worksheet and the first human entries (by 2026-10-14)

- [ ] **T13 worksheet emitted** over the approved roster, 26 rows, approve-on-execute recorded (agent; needs the DVC payload)
- [ ] **B1 · T14** 26 verdicts with DOIs entered; `load_adjudicated_labels` green (principal, 60–90 min)
- [ ] **B2 · T20** θ priors: four cited fields + two `assumed: true` with widths; `_require_sourced_theta` green (principal, 20–30 min)
- [ ] **B3 · T28** transport prior entered with its source (principal, 15–20 min)
- [ ] **B4 · T21** 3–8 reference compounds with published on-chip ordering (principal, 20–30 min)
- [ ] **B5** `PROVENANCE.md` written (principal, 5 min)
- [ ] **Audit power check** run on the realised roster: series structure, n_eff, simulated power vs the 0.80 floor; reported as a simulation with its seed (agent)
- [ ] **M0b record schema + validator + sealed-allocation tool** written and gated (agent)
- [ ] **C4** module README regenerated at the boundary (agent)

## Week 2 — the fit can run (by 2026-10-21)

- [ ] **T15** adjudicated labels loaded; label-safety tests green
- [ ] **M1 smoke run** on the sourced θ: fit executes, replay-determinism test green, run journal record written
- [ ] **Allocation sealed** — the three-way split seeded, written and digested **before any chip record is read**
- [ ] **M0b curation started**; the measured minutes-per-record after the first 10 records replace the planning assumption
- [ ] **B7** pair-stratum curation started in parallel, or explicitly deferred past the first result

## Weeks 3–5 — curation (by 2026-11-11)

- [ ] **M0b** 80–100 records curated, each passing the validator
- [ ] **M0c evaluator built**: frozen splits, the three controls, the locked test set; signature slot empty

## Week 6 — the first result (by 2026-11-18)

- [ ] **B8 · M0c signed** by the principal before any fit on real records
- [ ] **First evaluator run** on the sealed allocation: exposure ordering ρ, top-10 MoA recovery, Mondrian coverage with per-group CIs, the gate-evaluation count reported beside coverage
- [ ] **Result-review row** written under §eval as a Presentation (measured, with the run record and receipt)

## Week 7 — the publication path (by 2026-11-25)

- [ ] **A4** ruled: the Stage 1 closure as a methods note, or not
- [ ] **Stage 2 path** chosen from the result: registered-report Stage 2, or the honest "ranker, not validator" result

Every date above is a planning target set on 2026-10-03, not a measurement. The one duration with
no plan figure is M0b curation; its estimate is replaced by the measured rate in week 2.

Back to the [index](index.md).
