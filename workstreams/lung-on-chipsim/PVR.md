# PVR — ChipSim: Lung-on-a-Chip as a Perturbation-Framed LBM System

**Workstream:** `lung-on-chipsim` · **Module:** `projects/lung-on-chipsim`
**Status:** imported from Notion 2026-08-26 — authoritative source is Notion; this is the in-repo mirror
**Source:** [PRD — Lung-on-a-Chip as a Perturbation-Framed LBM System (Requirements & Vision)](https://app.notion.com/p/8c73e759a0a046659e00da96898ca394)
**Companions:** [A&D](./A-and-D.md) · [build plan](./plan/build-plan.md) · [Index](https://app.notion.com/p/d419cffbca33420a9a7d39abbe3eb67b) · [Open Questions](https://app.notion.com/p/8e0482407f574bc6ac0f508f906183ac)

> **Document type — PRD (requirements & vision).** Defines *what* ChipSim must be and *why* it is
> achievable. Deliberately no implementation detail: forks and trade-offs live in Open Questions;
> construction lives in the Design doc; architecture in the A&D.

> **Premise.** Model a Lab-on-a-Chip (here, a Lung-on-a-Chip) as a **perturbation problem**, *not* a
> physics-aware / PINN-style LLM. A drug goes **in**, a drug (+ biological response) comes **out**
> through a **parameterized boundary**. Mass transport is never solved as a PDE — it is *absorbed
> into the model's conditioning* and learned empirically. The scientific payload is a
> **one-drug → many-readout** map: a single drug interaction projected onto **multiple candidate
> surface moieties** via PPI foundations.

---

## 1 · Problem — the drug-delivery validation gap

> **The rate limiter in tissue-engineered drug testing is not fabrication and not biology — it is
> the validation loop.** Every candidate condition (drug × dose × boundary θ) needs a wet chip run
> to learn how much drug actually *arrives* at the tissue and what it does once there. Chips
> iterate in **weeks**; the useful design space is **10⁶+** conditions.

**What is missing:** a cheap, fast, *falsifiable* estimate of **delivered exposure** (the free-drug
concentration–time profile that actually reaches the tissue), and a matching estimate of the
**multi-readout response** that exposure induces, *before* a wet run is committed.

**Why it bites:**
- **Throughput mismatch** — ~10–100 chip conditions/month against a space six orders of magnitude larger.
- **Nominal dose ≠ delivered dose** — PDMS absorption, tubing adsorption and protein binding silently remove lipophilic drug.
- **Confounded failure modes** — "no effect" can mean *no delivery* or *no pharmacology*. Without a delivery model the two are inseparable and **every negative result is uninterpretable**.
- **No gradient for design** — with no queryable surrogate there is nothing to optimize dose or θ against; iteration degenerates into a random walk.

**Closing the gap operationally means:** (1) predict the exposure profile at the barrier for any
(drug, dose, θ); (2) predict which targets are occupied at that exposure; (3) fan occupancy out to
multiple readouts; (4) emit **calibrated uncertainty**, so wet runs are spent only on conditions
that can falsify the model.

*(GAO-25-107335 independently confirms the field's limiting factor is the absence of benchmarks and validation studies.)*

## 2 · Vision & objective

> **Objective.** Build **ChipSim**: an in-silico Lung-on-a-Chip mimic assembled **entirely from
> publicly available data**, whose biological engine is a stack of **drug→protein interaction
> models**. It maps `(drug, dose schedule, θ)` → `(exposure(t), target-occupancy vector,
> multi-channel readouts, uncertainty)`. Computational cost is explicitly **out of scope** — assume
> unlimited FLOPs and optimize for correctness, coverage and calibration.

- **In scope.** Public data only; compartment-level transport; affinity-driven occupancy; learned multi-readout heads; uncertainty; active-learning proposals for the wet lab.
- **Out of scope (v1).** PDE/CFD physics, spatially resolved fields, compute budgets, novel chemistry, immune-cell dynamics.
- **Success criterion.** *Decision-grade* — correct rank ordering of conditions plus honest error bars — **not** absolute quantitative truth.

**Operator formulation.** Given a drug-in profile `x` and boundary parameters `θ`, learn `P(y | x, θ)`.
θ enters as extra conditioning tokens / FiLM covariates — **the boundary is parameterized, not simulated**.
One entry of θ is no longer a device parameter at all: it is a **protein panel** (binding-site inventory).

**World-model framing.** ChipSim is the **grounded transition function** `T(s′|s,a)` of a
drug-discovery world model. Nearly all public effort has gone into the *policy* (generative design)
and the *reward proxy* (docking, affinity); almost none into the transition. A lab-on-a-chip is the
cheapest physical system exposing a real transition — controllable action space (θ), measurable
state (exposure), multi-channel observations. **The failure mode this guards against:** optimize a
generative designer against an uncalibrated affinity oracle and it produces molecules that score
beautifully and deliver nothing. Reward hacking here is the default outcome, not an RL curiosity.

### The LBM stack — one spine, five functions

> **Direction change — the committee is discarded.** The earlier framing derived *multiple LLMs*
> whose disagreement would supply uncertainty. §2D showed why that fails: the candidates share PDB,
> PDBbind, BindingDB and ChEMBL lineage, so their effective independence is near one and their
> spread is not an uncertainty estimate. ChipSim is **one model spine with five functional
> components and an explicit discrepancy term** — not a vote. Redundant models are retained only as
> **named baselines** for the §5E controls, never as members of an average.

| # | Model | Input → Output |
|---|---|---|
| **M1** | Transport surrogate | (drug-in `x`, boundary θ) → drug-out time series |
| **M2** | **Occupancy engine (core)** | drug ↔ protein, protein ↔ protein → affinity, occupancy vector, interface |
| **M3** | Contextual surface-moiety mapper | one engaged target → *many* context-specific surface representations |
| **M4** | Multi-readout phenotype head | shared latent → cytokines, barrier integrity, viability, expression |
| **M5** | *(optional)* Design/optimizer | readout objective → improved drug-in candidates |

> **M2 is the shared spine, not a biology-leg module.** Because carrier- and receptor-mediated
> crossing is itself a binding event, M2 supplies *barrier* occupancy to M1 as well as *target*
> occupancy to M3/M4. **M1 and M2 are coupled and must be solved together at each timestep, not chained.**

## 3 · The occupancy core mechanism (the central claim)

**For biomolecules and transporter substrates the barrier itself is an occupancy event**: crossing
is receptor binding, internalisation and release, with its own `K_d`, `k_on`/`k_off` and finite
capacity. Transport and pharmacology share *one* mechanism rather than two, and **moiety-level
chemistry is the single variable that moves both**. This retires **A3**, softens **A4**, and weakens **FP3**.

- **Crossing is receptor engagement** — RMT flux is set by binding, sorting and release, not by a permeability coefficient (TfR1 shuttles, FcRn bidirectional IgG transport).
- **Affinity is not monotone with delivery — this is the crux.** High-affinity bivalent TfR binders are routed to degradation while **monovalent or lower-affinity** constructs increase transport; FcRn recycling shows a discrete pH-dependent affinity threshold. **Any model that assumes tighter binding → more delivered drug gets the sign wrong.**
- **The barrier is saturable and consumes the drug** — target-mediated drug disposition (TMDD, Mager & Jusko 2001).
- **Limit of the claim.** Passive transcellular diffusion of small lipophilic molecules needs no receptor. The occupancy engine is a **superset with a passive baseline**, never a replacement.

**Why moiety resolution is the right unit:** single-atom edits flip transporter status (MMP analysis
of P-gp efflux); the same molecule presents two polarities (chameleonicity — macrocycles hide polar
surface area in lipid environments); permeability data is thin (~8k cyclic-peptide values) while
affinity data is ~10⁶ — **so ChipSim borrows strength from affinity data to explain permeability, not the reverse.**

**Three reasons this is genuinely hard, each shipping a requirement:**
1. **Non-monotonicity** → *the occupancy→delivery link must represent a valley/optimum. A monotone link function is disqualifying, not merely inaccurate.*
2. **Coupling, not cascading** → *FP3 is weakened — the interface is `C_free(t)` plus a barrier-occupancy state, solved quasi-statically to a fixed point.*
3. **Non-identifiability** (permeability and affinity are confounded in every downstream readout) → *the matched-pair disambiguation test is promoted to the primary acceptance test.*

**The uncomfortable part — tool weakness in exactly the needed direction.** Boltz-2 approaches FEP
accuracy at ~1000× lower cost under MIT licence (the single reason a home build is credible), **but
independent audits find its affinity predictions largely independent of the final ligand pose, and
its active/inactive classification insensitive to binding-site mutations and sometimes to target
exchange.** Classical scoring fails the same way: strong at ranking ligands for a fixed target, weak
at ranking targets for a fixed ligand — and ChipSim's one-drug → many-moieties map runs in exactly
that weak direction.

> **So the occupancy engine ships with three controls, not one benchmark.**
> **(1) Target-shuffle and site-mutation control** — predicted affinity must degrade when the pocket is mutated or the target swapped; if it does not, the engine is reading ligand priors and its moiety attributions are decoration.
> **(2) MMP / cliff-stratified splits** — report accuracy separately on matched pairs crossing a potency or efflux cliff.
> **(3) Non-monotonicity test** — reproduce at least one published case where *reducing* affinity *increases* delivery.
> **Failing control 1 kills the moiety claim; failing control 3 kills the delivery claim.**

## 4 · The scoped PoC (§2E)

> **The addressable core.** The PoC is not ChipSim. It is the smallest artefact that tests **one
> claim**: that a large biological model, conditioned on a parameterised barrier, predicts
> **delivered exposure and target occupancy** for compounds it has never seen — well enough to
> *order* chip conditions, and honest enough to say when it cannot.

**The one claim under test:**
> For held-out drug scaffolds on a single lung barrier, an LBM-supplied occupancy vector plus a
> two-compartment transport state predicts exposure ordering at **Spearman ρ ≥ 0.6**, recovers known
> mechanism-of-action targets in the **top-10** panel, and holds **90% Mondrian subgroup coverage**
> at intervals no narrower than the assay-noise floor.

- **If it holds** — the validation gap is addressable in silico and the programme is justified.
- **If it fails on ordering** — transport conditioning is not being learned; the §5E kill criterion applies and ML retreats to the biology leg.
- **If it holds on ordering but fails coverage** — the artefact is a *ranker*, not a validator, and the wet queue cannot be safely shrunk. **That is a real result and worth publishing as one.**

### The minimum viable chip

| Element | PoC setting | Why this and not more |
|---|---|---|
| Barrier | one alveolar–endothelial bilayer: passive baseline + **two** carrier terms (P-gp efflux, one uptake carrier) | enough to exhibit saturation and non-monotonicity; few enough to stay identifiable |
| Target panel | about **30** proteins, not 300 — MoA targets of the reference set plus the barrier carriers | panel-truncation bias is measurable at 30 and merely asserted at 300 |
| Compounds | **20–40** inhaled/lung-relevant drugs with published exposure, plus matched molecular pairs for the cliff test | the disambiguation and cliff tests need *pairs*, so pair count matters more than compound count |
| θ | flow, membrane area, thickness, one strain setting, and the two carrier abundances | **5–8 identifiable parameters**, per FP1 |
| Readouts | exposure(t), occupancy vector, and **one** biological channel (barrier integrity) | the multi-channel fan-out is the programme, not the PoC |

### Which LBM earns its place — three, not nine

| LBM | Job | Admission test | Named fallback |
|---|---|---|---|
| Co-folding affinity model (Boltz-2 or Chai-1) | `K_d` wherever no measurement exists | **target-shuffle and site-mutation degradation** | curated BindingDB/ChEMBL lookup + descriptor regressor; the PoC still runs |
| Protein language model (ESM-2 / PLM-interact adapter) | barrier carrier engagement, interface residues | beats a descriptor baseline on cliff-stratified pairs | curated transporter substrate lists; the moiety claim is dropped, the PoC is not |
| Single-cell / atlas FM | transporter + receptor abundance priors for θ | abundances match HPA lung values within an order of magnitude | HPA values used directly as fixed constants |

> **The admission rule.** Every LBM in the PoC ships with a *named non-LBM fallback* that keeps the
> system running. This is the difference between **applying** LBMs and **depending** on them — and
> the only way to measure what the LBM contributed: run both arms and report the delta.
> **An LBM that cannot beat its own fallback is a finding, not a failure.**

### The deliverable is a decision object, not a number

1. `C_free(t)` at the tissue face, with an interval **clamped at the noise floor**.
2. An occupancy vector over the 30-protein panel, with per-target intervals.
3. A **subgroup label** (target class × scaffold cluster) so the coverage claim is the *conditional* one.
4. A **recommendation with a reason**: run wet, skip, or *cannot decide*. **The third option is what actually closes the validation gap; a system that never abstains has not been calibrated, only fitted.**

**Ladder mapping.** PoC = **v0 + v1**, plus the moiety-attribution and target-shuffle tests pulled
forward from v2. *Deferred:* multi-channel fan-out, contextual moiety mapper, M5 inverse design, and
the autonomous loop (a human may drive the PoC queue by hand). **Never deferred: the three controls,
the noise floor, and the discrepancy term.**

## 5 · First-principles feasibility (FP1–FP6)

| # | Argument | Verdict |
|---|---|---|
| **FP1** | `τ_diff = h²/D ≪ τ_res = L/U` → each channel is **well mixed**; transport collapses from a PDE to a few ODE states (~5–8 identifiable parameters). The high-dimensional part is drug→protein→phenotype, where BindingDB/ChEMBL/LINCS already supply millions of labels | ✅ *The project is data-rich precisely where it is hard* |
| **FP2** | Separation of timescales — transport (s–min) ≫ binding (ms–s) ≫ transcription (h) — licenses modularity; legs couple quasi-statically, no joint solver | ✅ holds |
| **FP3** | Only one scalar crosses the module boundary (`C_free(t)`) | ⚠️ **weakened** — with carrier/receptor crossing, the interface is `C_free(t)` **plus** a barrier-occupancy vector solved to a fixed point. Modularity survives; the one-scalar claim does not |
| **FP4** | Occupancy is thermodynamics and thermodynamics is public: `θ_t(C) = C^n/(C^n + K_d^n)` over hundreds of thousands of tabulated pairs → drug-in → occupancy is computable today with **zero chip data** | ✅ qualified — equilibrium occupancy is the floor; residence time/rebinding, saturation, and the oracle-audit problem are in scope |
| **FP5** | The 1→many map factorizes: `y_r = g_r(Σ w_{r,t} θ_t(C_free), z_ctx)` — a polypharmacology occupancy vector pushed through a context-conditioned readout map, **both factors publicly supervised** | ✅ a factorization problem, not a new measurement campaign |
| **FP6** | **Calibration is cheaper than accuracy** — a model 3-fold off but correctly ranked and correctly uncertain still removes most wet runs | ✅ *the single strongest reason the project is achievable* |

**Achievability ledger verdict:** two of seven links are turnkey, three are turnkey with a
calibration factor, and **only the occupancy→pathway link carries real scientific risk** — an
unusually favourable risk profile, concentrated where a wrong answer is *detectable*, not silent.

## 6 · §5C Assumption register — A1–A13

Each assumption ships with its own break test. *An assumption without a test is a hidden failure
mode, and hidden failure modes are what created the validation gap in the first place.*

| # | Assumption (v1) | Breaks when |
|---|---|---|
| **A1** | Well-mixed compartments; no spatial fields | thick gels, steep gradients, very high flow |
| **A2** | One scalar `P_app` per drug from structure, × a single lung calibration factor α | active uptake or P-gp efflux dominates; barrier damage |
| **A3 · retired** | *Was:* first-order kinetics, no saturation. **Now:** passive flux stays first-order, carrier and receptor terms are explicitly saturable (Michaelis–Menten / TMDD) | n/a — replaced by a mechanism with its own parameters and priors |
| **A4 · softened** | Quasi-equilibrium (Hill) for the readout leg; explicit `k_on`/`k_off` wherever residence time or endosomal-pH switching governs delivery | covalent binders, rebinding-dominated regimes, RMT cargo whose fate is set inside the endosome |
| **A5** | Free-drug hypothesis; `f_u` from a plasma-protein-binding model | lipid-rich media, strong nonspecific binding |
| **A6** | Device sink as one lumped loss `k_sink(logP)` | very lipophilic drugs, long runs, PDMS saturation |
| **A7** | Static tissue: expression fixed within a run | CYP/transporter induction, toxicity feedback |
| **A8** | Fixed cell composition (alveolar epithelium + microvascular endothelium) from atlas priors | immune cells, fibroblasts, disease states |
| **A9** | Readouts conditionally independent given occupancy vector and context | barrier collapse drives every channel at once |
| **A10** | Additive polypharmacology; no synergy term | combination dosing, pathway crosstalk |
| **A11** | Compute is free | only at deployment |
| **A12** | A passive permeability baseline is retained alongside the carrier terms | pure biologics/peptide cargo, where identifiability collapses onto the carrier parameters |
| **A13** | Predictive intervals clamped at the assay-noise floor — **0.5 log** for `pKd`, **0.7** for mixed-source panels | a single well-controlled assay supplies the labels → floor is intra-lab σ ≈ **0.2 log**, lowerable with evidence |

## 7 · §5D Execution ladder v0 → v3

| Version | Delivers | Go / no-go |
|---|---|---|
| **v0** Deterministic skeleton, no ML | two-compartment ODE with literature θ; reference drug set with known lung exposure | reproduce published on-chip clearance ordering **within 3-fold** |
| **v1** Public ML replaces every hand-set constant | `P_app` head (TDC Caco-2/PAMPA), `f_u` (PPB model), `k_sink` (logP); occupancy engine = BindingDB/ChEMBL lookup + DTI/affinity fallback → exposure(t) + occupancy vector | **Spearman ρ ≥ 0.6** on exposure AUC for held-out scaffolds; **MoA targets in the top-10** occupancy panel |
| **v2** Multi-readout biology | LINCS L1000 + Tox21 heads conditioned on (occupancy, cell context); contextual moiety mapper (PINNACLE + MaSIF surfaces) | Top-K moiety recall vs curated interface annotations; per-channel calibration within tolerance |
| **v3** The loop that fixes the gap | conformal intervals + discrepancy term drive active learning (**not** ensemble spread); ≤8 conditions/cycle nominated by the experiment brain | prediction error must fall **faster per wet run than random selection** — *the deliverable is iteration speed, not accuracy*. Second gate: **ratchet drift** — re-scoring the champion against the locked test set must not degrade |

## 8 · §5E Success bars — what counts as "gap closed"

- **Retrospective bar** — reference compound sets from OoC/IVIVE literature: report **fold-error and Spearman ρ, not R² alone**.
- **Prospective bar** — blind prediction on inhaled drugs with published human lung PK.
- **Negative control** — scramble θ: **performance must collapse**. If it does not, the model is memorizing chemistry and has learned nothing about delivery.
- **Disambiguation test** — two drugs matched on affinity but differing in `P_app` must be predicted to differ in readout. *This is the exact confound the validation gap creates, so it is the test that matters most.*
- **Moiety-attribution bar (headline)** — on matched pairs crossing a potency or efflux cliff, the engine must call the right direction more often than a bulk-descriptor baseline. **Report cliff-stratified accuracy separately; aggregate metrics hide exactly the cases the project exists to resolve.**
- **Target-shuffle control** — swap the protein or mutate the pocket: predicted affinity and moiety ranking **must degrade**.
- **Non-monotonicity test** — reproduce ≥1 case where reducing affinity increases delivery.
- **Calibration** — a 90% interval must cover ~90% of held-out observations, as a **Mondrian group-conditional** claim per target class × scaffold cluster × θ regime. **Marginal coverage alone does not satisfy this bar.**
- **Uncertainty-honesty bar** — report **effective** ensemble size, fitted discrepancy magnitude δ, and the assay-noise floor alongside every interval. An interval narrower than the floor, or a confident claim resting on `N_eff` ≈ 1, **fails irrespective of accuracy**.
- **Kill criterion** — if ordering accuracy on held-out θ regimes never beats a chemistry-only baseline, transport conditioning is not being learned: revert to the explicit ODE and confine ML to the biology leg.

## 9 · Requirements register

**Agent & orchestration**
| ID | Requirement |
|---|---|
| **R-AGENT-1** | Agent-driven, not human-driven. A **single agent** holds the hypothesis, dispatches runners, reads a verdict and ratchets. The unit of work is **one barrier consideration, kept or falsified** |
| **R-AGENT-2** | **The agent must be thin.** No biology, constants, priors or thresholds in the agent layer — all of it lives in the configured chip environment |
| **R-AGENT-3** | **The evaluator is frozen and out of the agent's write scope.** Splits, controls and the locked test set are the deliverable |
| **R-AGENT-4** | **Vetoes are absolute.** Target-shuffle, cliff-stratified accuracy and non-monotonicity each revert a diff regardless of the headline. **They may never be averaged into a single score** |
| **R-AGENT-5** | **Every kept result is replayable** from journal + seed |
| **R-AGENT-6** | **Autonomy target Level 3** — the agent owns the search; the human owns the box (intent, §5C register, acceptance criteria) |
| **R-AGENT-7** | **The loop terminates in the wet lab**, ≤8 conditions/cycle. A requirement, not an optimisation |
| **R-DET** | Given `(θ, drug, schedule, seed)` the environment **must replay identically**. Replayability is a **correctness** requirement |

**Mechanism**
| ID | Requirement |
|---|---|
| **R-MECH-1** | The occupancy→delivery link **must represent a valley/optimum**; a monotone link is disqualifying |
| **R-MECH-2** | Interface is `C_free(t)` **plus** barrier-occupancy state, solved quasi-statically to a fixed point; M1 and M2 solved **together at each timestep, not chained** |
| **R-MECH-3** | The matched-pair disambiguation test is the **primary acceptance test** |
| **R-MECH-4** | `φ_barrier` is a **state variable, not a readout** — occupancy *is* the environment state |
| **R-MECH-5** | Barrier flux = passive baseline **plus** saturable carrier terms (Michaelis–Menten / TMDD); passive baseline retained (A12) |
| **R-MECH-6** | **Exactly one occupancy model** in the critical path at any version; swaps are versioned mechanism diffs, never blended |

**Data & sourcing**
| ID | Requirement |
|---|---|
| **R-SRC** | **Every ChipSim parameter must trace to a public record or a fitted value with a stated prior. A number that cannot be sourced becomes an explicit assumption in §5C — never a silent constant** |
| **R-DATA** | Public data only |
| **R-PEFT** | Freeze ESM-2 / PLM-interact / PINNACLE / single-cell FM — **train only adapters + heads (PEFT)** |
| **R-NOPDE** | **No physics loss** — pure data fit; physics enters as ODE *structure*, never as a penalty term |

**PoC**
| ID | Requirement |
|---|---|
| **R-POC-1** | Every LBM ships with a **named non-LBM fallback**; run both arms and report the delta |
| **R-POC-2** | Emit a **decision object** including a "cannot decide" abstention |
| **R-POC-3** | **Never deferred:** the three controls, the noise floor, the discrepancy term |

## 10 · §7 Residual questions (open)

**Occupancy-first (the new spine)**
- Does any available affinity oracle possess *moiety* sensitivity, or only *ligand* sensitivity? *(The target-shuffle and site-mutation controls answer this, and the answer decides whether the 1→many map is science or decoration.)*
- Can barrier occupancy and target occupancy share one engine and one embedding, or do transporters/receptors need a dedicated head?
- Is the affinity→delivery non-monotonicity *learnable* from public data, or must it be imposed as structure (an explicitly valley-shaped link with a fitted optimum)?
- How far can affinity-rich supervision (~10⁶) compensate for permeability-poor supervision (~10⁴) before the transfer becomes fiction? What diagnostic detects the crossover?
- What is the minimum barrier target panel capturing most lung delivery variance, and does panel truncation bias the occupancy vector systematically?
- Where does quasi-equilibrium stop being safe?

**Orchestration (the experiment brain)**
- Is there an honest gate scalar at all, or must the brain be handed a **lexicographic order over vetoes** instead of a single number to climb?
- How many keep-or-revert cycles can run against one held-out split before **the ratchet itself becomes the overfitting mechanism**, and which drift statistic detects it soonest?
- May the brain propose amendments to the §5C register, or only operate inside it? *(Autonomy Level 3 says the latter; the ambition of the project says the former.)*
- **Can a Kennedy–O'Hagan discrepancy term be identified at all from a few dozen lung-chip measurements, or does it simply absorb α and leave θ physically meaningless?** — with the committee discarded, this is **the programme's hardest external dependency**, because nothing else now supplies structural uncertainty.
- How thick may the environment become before its own fidelity claims need a validation gap of their own?
- **PoC-specific:** what does each LBM actually contribute over its named fallback? Run both arms every time. **If the delta sits inside the noise floor, the honest conclusion is that the chip problem is currently a curation and calibration problem rather than a foundation-model problem — and that conclusion is worth more than a marginal accuracy gain.**
