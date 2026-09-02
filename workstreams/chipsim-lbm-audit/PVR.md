# PVR — ChipSim LBM Audit: do the foundation models resolve moiety-level chemistry?

**Workstream:** `chipsim-lbm-audit` · **Module:** `lung-on-chipsim` · **Status:** approved 2026-09-01
**Informs:** the `lung-on-chipsim` ChipSim programme — it does **not** advance the M0–M6 ladder.
**Companions:** [ChipSim PVR](../lung-on-chipsim/PVR.md) · [ChipSim A&D](../lung-on-chipsim/A-and-D.md)

---

## Vision

ChipSim's scientific payload is a **one-drug → many-moieties** map: a single engagement fanned out
to ranked, context-specific surface moieties. That payload rests on an assumption nobody has tested
here — that the large biological models supplying occupancy are sensitive to **which protein, and
which pocket**, rather than merely to the ligand.

The parent PVR is explicit that this is the load-bearing risk:

> Independent audits find co-folding affinity heads whose predictions are largely independent of the
> final ligand pose, and whose active/inactive classification is insensitive to key binding-site
> mutations and, in some cases, **to target exchange**. A scorer that returns the same answer when
> you swap the protein cannot, unaudited, tell you *which moiety* was engaged.

And it states the consequence: **failing the target-shuffle control kills the moiety claim.**

This workstream runs that test properly, on the ratified lung barrier panel, **before** further
programme effort is spent on top of the assumption. It is a **method-validation study**, designed so
that a negative result is a publishable contribution rather than a dead end — it answers §7's
hardest open question, *"does any available affinity oracle possess moiety sensitivity, or only
ligand sensitivity?"*

**The affinity leg is single-sourced.** Chai-1 does co-folding but not affinity and is ruled
geometry-only, never scoring; Boltz-2 is the only affinity-capable model licensed to sit inside the
loop. There is no second affinity model to fall back to — only the non-LBM arm. That is precisely
why this audit runs first.

## Goals & success metrics

| # | Goal | Measured by |
|---|---|---|
| G1 | A reported **delta against its named non-LBM fallback** for every LBM arm | both arms run and reported for all three; no arm reported alone |
| G2 | A verdict on **Boltz-2's target sensitivity** | target-shuffle + pocket-vs-distal mutation, against pre-registered thresholds |
| G3 | A result that is **publishable whether positive or negative** | pre-registration frozen before the first complex; all arms reported including nulls |
| G4 | Fits the PoC envelope | ≤ $30 Modal spend; local arms on the M5 Max; no overrun |

**Success is a defensible verdict *or* a defensible "inconclusive at this power."** A weak positive
reported as a pass is a failure of this study, not a success.

## Out of scope

- The **M0–M6 ladder**. This informs it; it does not advance it. No ODE, no readout heads, no acquisition loop.
- **Slice-2 ingestion** (ChEMBL / BindingDB / TDC / LINCS parsers) beyond the minimum needed to assemble measured pairs.
- **AlphaFold provisioning on GCP.** AFDB already has the wild-type panel precomputed (CC-BY-4.0, source S4), and Boltz-2/Chai-1 co-fold from sequence, so mutants come from editing sequence, not from a separate structure run. AlphaFold Server remains barred from any automated ligand-binding path by its ToS.
- **M0b curation.** This audit does not consume the 60–100 curated chip records.
- **Four of the five human blockers.** Only T8 is relevant, and only to make the audit lung-specific rather than generic.
- **Any proteome-wide selectivity claim.** The panel is seven proteins.
- **Chai-1 geometry as a fourth arm** unless Modal credit remains after the three admission arms.
- **AM-6.** Open, gates M5 pre-registration, unrelated to this study.

## Constraints

- **Compute — Modal $30 free credit, Boltz-2 only.** The sole CUDA-bound arm. At L40S rates (~$1.95/h, 80–100 complexes/GPU-h) the budget buys ~1,200–1,500 complexes.
- **Compute — local Apple M5 Max, 128 GB, 40 GPU cores**, via PyTorch/MPS for ESM-2 embeddings, RDKit descriptors, descriptor baselines, the HPA arm, and all statistics. Verified available; PyTorch not yet installed.
- **LM Studio is not in the model path.** It serves GGUF via llama.cpp — LLMs and embedding models. ESM-2 and Boltz-2 are PyTorch models and are not LM Studio artifacts. LM Studio keeps its existing bge-m3 role.
- **Design: depth over breadth.** ~7 barrier proteins × ~40 compounds, not ~30 × 20. The parent PVR forbids the alternative — *"aggregate metrics hide exactly the cases the project exists to resolve"* — so a study whose only well-powered number is an aggregate would argue against its own programme.
- **Powered for a large effect only.** Declared, not discovered.
- **Two rounds:** pilot then confirmatory, within budget.
- **Licence posture inherited:** non-commercial; Boltz-2 (MIT) may sit in the loop; AlphaFold Server never automated; DrugBank snapshot identity-only.
- **No agent writes a biological number or a citation.** Inherited Global Constraint.

## Requirements

Each carries a test criterion — how a test would prove it.

**R1 · Preflight gate.** A run refuses to start unless free RAM, free disk, and remaining Modal credit each exceed a declared floor.
*Test:* with any floor breached, the entry point exits non-zero **before** dispatching work; the failure names which floor and its measured value. Passing preflight is asserted to have run before any Modal call.

**R2 · Pre-registration frozen before the first complex.** Candidate set, arms, thresholds, and the inconclusive rule are written and hash-sealed before any model runs.
*Test:* the run refuses to start without a sealed pre-registration; the seal is verified at start and **raises on mismatch**, so a threshold edited after seeing results fails loudly. (Same mechanism as the T8 panel seal.)

**R3 · Boltz-2 target-shuffle arm.** Predicted affinity for (ligand, true target) is compared against (ligand, shuffled target) with measured values as ground truth.
*Test:* both arms produce per-pair predictions over the same ligand set; the reported statistic is the *difference* in agreement with measured values, never either arm alone. A run producing only the native arm fails.

**R4 · Pocket-vs-distal mutation control.** Pocket-residue mutants are compared against distal-surface mutants as an internal control.
*Test:* every pocket mutant has a matched distal mutant of equal mutation count on the same target; the reported statistic is the difference between them. A raw "prediction dropped" result with no distal comparator fails.

**R5 · ESM-2 vs descriptor baseline on cliff-stratified pairs.** Matched molecular pairs crossing a potency or efflux cliff, LBM arm against the descriptor baseline.
*Test:* accuracy is reported **separately on cliff pairs**, not pooled; a pooled-only report fails.

**R6 · Atlas abundances vs HPA.** Atlas-derived transporter/receptor abundances are compared against Human Protein Atlas lung values.
*Test:* per-protein ratio computed and reported; the pass criterion (within an order of magnitude) is evaluated per protein, not on an average.

**R7 · Both arms always reported.** Every LBM ships its named non-LBM fallback and both are reported.
*Test:* the report generator raises if any arm lacks its fallback counterpart. An LBM that cannot beat its fallback is recorded as a finding, not suppressed.

**R8 · "Inconclusive at this power" is a pre-defined, permitted verdict.** The study may conclude that it cannot resolve the effect.
*Test:* the verdict enum contains exactly {sensitive, insensitive, inconclusive}; a result inside the pre-registered ambiguity band maps to `inconclusive` and **cannot** be rendered as a pass.

**R9 · Budget guard.** Modal spend is tracked and the run halts before exceeding the declared credit.
*Test:* with the ceiling set below the projected cost, the run halts and reports remaining work rather than overrunning.

**R10 · Deterministic replay.** Every reported number replays from its recorded inputs.
*Test:* re-running from the recorded (model version, seed, pair set, arm) reproduces the reported statistic; a missing seed or unpinned model version fails the check.

## Open questions

- **Iteration rounds beyond pilot + confirmatory.** Assumed two; budget effectively caps it.
- **Whether T8 is completed**, which decides whether this is a *lung-barrier* audit or a generic Boltz-2 audit. Not a blocker — the study runs either way, but the claim narrows without it.
- **Exact pre-registered thresholds** for R3/R4 — to be fixed in `/design` and sealed under R2 **before** any run.
- **Chai-1 geometry arm** — in only if credit remains.
