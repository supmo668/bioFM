# Stage 2 kickoff checklist — ChipSim (lung-on-chipsim)

<!-- HACP Checklist · Section = build · L1 — Review · Indexed by "ChipSim (bioFM) — Index".
     SOURCE OF TRUTH: the Notion row (principal, 2026-10-03). This file mirrors it; see notion-map.json.
     Week 0's governance items were ruled 2026-10-04 in the principal's grill. -->

**Kind:** Checklist · **Layer:** L1 · **Holds:** the pre-conditions that flip the build phase from parked to active, in the order they can be satisfied · **Reaches:** [§decision](decision.md) (the ledger), [§build](build.md)

Tick an item only against the artifact it names. An item with no artifact stays open.

## Week 0 — governance (by 2026-10-07)

- [x] **Roster approved as final** — 26 entries; recorded 2026-10-03 as a standing assumption from the principal's session instruction; the CTO carries it into the approval log as a signed row
- [ ] **A2** archived Stage 1 tip pushed to `archive/lung-on-chipsim-stage1` on `origin` (principal, 2 min)
- [ ] **A1 executed** — successor branch `lung-on-chipsim-stage2` cut from `main` as ruled; science-bearing files taken by content from `c04e701` and the archived tip; guard machinery left where it closed (CTO, on the r3 signature)
- [x] **Plan r3 approved** by the principal 2026-10-04 ("approve all"); the CTO folds and signs it, then `plan-gate verify` must come back green on the successor branch
- [ ] **`plan-gate verify`** green on the successor branch after the fold (CTO)
- [ ] **Clean suite re-measurement** on the successor branch, no concurrent pytest processes, recorded with its wall time (CTO; owed since 2026-10-01)
- [x] **C1 / C2 / C3 ruled** 2026-10-04 — SLC15A1 kept under the T8 ruling (re-checked at M1); the AM-6 residual struck as superseded by ADR-0002; row 59 closes identifier-constraint retroactivity
- [x] **A1 / A3 / A4 ruled** 2026-10-04 — successor branch by content; the five withheld files stay on the archived branch with the gap recorded; the closure is published as a standalone methods note
- [ ] **Floor landed** — `docs/hacp/lung-on-chipsim/` merged to `main` by the CTO (ruled 2026-10-04: no agent pull request) so every `Local path` on the ChipSim rows resolves

## Week 1 — the worksheet and the first human entries (by 2026-10-14)

- [ ] **T13 worksheet emitted** over the approved roster, 26 rows, approve-on-execute recorded (agent; needs the DVC payload)
- [ ] **B1 · T14** 26 verdicts with DOIs entered; `load_adjudicated_labels` green (principal, 60–90 min)
- [x] **S13 / S14 scaffolds + T24 / T28 / T21 validators** built 2026-10-04: no value slots filled, every refusal a test that can fail (agent — [§experiment](experiment.md))
- [ ] **B2 · T20** θ priors: four cited fields + two `assumed: true`; `chipsim theta-check` exits 0 (principal, 20–30 min)
- [ ] **B3 · T28** transport prior entered with its source (principal, 15–20 min)
- [ ] **B4 · T21** 3–8 reference compounds with published on-chip ordering (principal, 20–30 min)
- [ ] **B5** `PROVENANCE.md` written (principal, 5 min)
- [ ] **Audit power check** run on the realised roster: series structure, n_eff, simulated power vs the 0.80 floor; reported as a simulation with its seed (agent)
- [ ] **M0b/M0c plan draft** signed, amended or refused by the principal, including the identities-or-slots question (principal; the build plan defers both milestones and gives no done-conditions)
- [ ] **M0b record schema + validator + sealed-allocation tool** written and gated **before any curation starts** (agent; blocked on the plan above, not on effort)
- [ ] **C4** module README regenerated at the boundary (agent)

## Week 2 — the fit can run (by 2026-10-21)

- [ ] **T15** adjudicated labels loaded; label-safety tests green
- [ ] **M1 smoke run** on the sourced θ: fit executes, replay-determinism test green, run journal record written
- [ ] **Allocation sealed** — the three-way split seeded, written and digested **before any chip record is read**
- [ ] **M0b curation started** by the principal as **sole curator** (ruled 2026-10-04); the measured minutes-per-record after the first 10 records replace the planning assumption
- [ ] **B7** pair-stratum curation started in parallel, or explicitly deferred past the first result

## Weeks 3–5 — curation (by 2026-11-11)

- [ ] **M0b** 80–100 records curated, each passing the validator
- [ ] **M0c evaluator built**: frozen splits, the three controls, the locked test set; signature slot empty

## Week 6 — the first result (by 2026-11-18)

- [ ] **B8 · M0c signed** by the principal before any fit on real records
- [ ] **First evaluator run** on the sealed allocation: exposure ordering ρ, top-10 MoA recovery, Mondrian coverage with per-group CIs, the gate-evaluation count reported beside coverage
- [ ] **Result-review row** written under §eval as a Presentation (measured, with the run record and receipt)

## Week 7 — the publication path (by 2026-11-25)

- [ ] **A4a** the Stage 1 closure methods note drafted by the CTO (by 2026-10-17) and ratified by the principal; venue chosen on the draft
- [ ] **Stage 2 path** chosen from the result: registered-report Stage 2, or the honest "ranker, not validator" result

Every date above is a planning target set on 2026-10-03 and confirmed in the principal's grill of
2026-10-04, not a measurement. The one duration with no plan figure is M0b curation; its estimate
is replaced by the measured rate in week 2.

Back to the [index](index.md).
