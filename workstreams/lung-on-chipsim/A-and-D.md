# A&D — ChipSim: Architecture & Design (lung-on-chipsim)

**Workstream:** `lung-on-chipsim`
**Status:** imported from Notion, 2026-08-26 — authoritative source is Notion; this is the in-repo mirror
**Sources**
- Index: [ChipSim — Lab-on-a-Chip In Silico Validation (Project Index)](https://app.notion.com/p/d419cffbca33420a9a7d39abbe3eb67b)
- Spec (architecture): [Spec — ChipSim Architecture: Experiment Brain, Chip Environment & Uncertainty Stack](https://app.notion.com/p/e166e53b327b43fe93301c976ab704f1)
- Design (construction): [Design — ChipSim v1: Data Sourcing → Objectives → Modeling → Application](https://app.notion.com/p/2608314aaab14913a76ba509c08a1940)
- Open Questions: [Resource-Constrained Choices for a Home Build](https://app.notion.com/p/8e0482407f574bc6ac0f508f906183ac)
- Plan (M0 slice): [Plan — ChipSim M0 Data Spine](https://app.notion.com/p/2be47ffc30a34400ab31077cc57b3ffd)

> Section numbers (§2A, §2B, §2D) are inherited from the PRD deliberately, so every
> cross-reference written into the PRD, Design and Open-Questions docs keeps resolving.
> Unqualified references (§2, §3, §5C, §5D, §5E, §6, §7) point back at the PRD/PVR.

---

## Part I — Architecture (Spec)

### §2A · The experiment brain — one orchestrator agent

ChipSim is **not a pipeline a human drives**. It is a single orchestrator agent that holds
the current hypothesis, dispatches disposable experiment runners, reads an analyser's
verdict, and ratchets. The unit of work is **one barrier consideration, kept or falsified**
— not a training run.

Three rings:
- **Inner ring** — brain → runners → frozen evaluator → analyser → brain. Fully autonomous, runs continuously.
- **Outer ring** — the wet-chip queue (≤8 conditions/cycle). Fires rarely; the only place real information enters.
- **Human ring** — `program.md` / the assumption register. The human edits intent, never the runners.

#### Borrowed from autoresearch, and adapted

| autoresearch primitive | ChipSim analogue | The adaptation that matters |
|---|---|---|
| `train.py` — the one editable file | the **mechanism hypothesis** (barrier flux law, θ target panel, link-function shape, loss weights) | the agent searches **mechanisms, not architectures**; a diff is a scientific claim |
| `prepare.py` — frozen | the **frozen evaluator** (leakage-aware splits, benchmark compounds, three §5E controls) | the evaluator *is* the deliverable, so it must be immutable, versioned, outside the agent's write scope |
| `val_bpb` — one scalar | a **gate scalar plus veto flags** | exposure ρ, cliff-stratified accuracy, calibration and shuffle-degradation cannot be averaged without hiding the failure the project exists to catch |
| fixed 5-min wall clock | a fixed **evaluation contract** (same panel, compounds, seeds, split version) | comparability, not thrift |
| ratchet — keep if better | same ratchet **plus a locked test set** opened only at v-milestones | the ratchet is the thing that overfits |
| `program.md` | the §5C **assumption register** + Open Questions | the human writes the register the agent is judged against |
| ~100 experiments overnight | thousands in-silico, then **≤8 wet conditions per cycle** | the loop does not close in the log; it closes on the chip |

#### The four domain-forced additions

1. **The search space is barrier mechanisms** — passive-only vs saturable carrier terms; panel size in θ; monotone vs valley-shaped occupancy→delivery link; quasi-equilibrium vs explicit k_on/k_off; global α vs per-barrier α.
2. **The metric is a vector, and it is gameable** — the analyser emits a gate scalar *and* vetoes. The target-shuffle control, cliff-stratified accuracy and the non-monotonicity test each hold an **absolute veto**. Any veto reverts the diff regardless of the headline.
3. **Ratchet drift must be measured** — re-score the current best against a locked, never-tuned test set at every milestone. Degradation means the agent has been optimising the evaluator: discard the leaderboard, not the test set.
4. **The loop must terminate in the wet lab** — escalation to ≤8 chip conditions per cycle is what stops the brain converging confidently on a fiction.

> **Selection budget (PoC).** Budget **20–30 gated diffs per milestone, pre-registered**;
> open the locked test set **at most twice** in the project's lifetime; record the
> **number of gate evaluations in the model card** as a first-class number, next to
> coverage. An unreported selection count silently voids every coverage claim in §2D.

> **Write scope — the brain's hard boundary.** The agent may edit mechanism hypotheses,
> priors, link functions, loss weights, panel composition and acquisition policy. It may
> **never** edit the frozen evaluator, the split definitions, the three controls, the
> locked test set, or the §5C assumption register. Proposals to change any of those are
> written to the journal as requests and require human ratification.

**Autonomy target: Level 3** — the brain owns the search; the human owns the box and the register.

#### Execution substrate — n8n drives, Modal runs

| Loop verb | Implementation |
|---|---|
| **propose** | the agent, writing one mechanism diff to a run queue — the only verb requiring judgement |
| **dispatch** | **n8n** workflow (self-hosted CE): reads the queue, stamps `(θ, drug, schedule, seed)`, calls the runner. Workflow JSON exported to git → dispatch is replayable |
| **run** | **Modal** serverless GPU functions (Boltz-2 affinity, ESM-2 embeddings, Chai-1 poses), spawned with a call id |
| **poll** | n8n **Wait + HTTP poll** on the Modal call, with a timeout that *fails* the run rather than hanging it |
| **gate** | the frozen evaluator, exposed as a **versioned HTTP service** that n8n may call and nobody may edit |
| **journal** | n8n appends the run record — diff, seeds, scores, veto state — to the journal store and the git log |
| **escalate** | the agent reads the journal; the human ratifies |

> **What n8n is not.** n8n is **not a second brain**. It computes no metric, weighs no veto
> and rewrites no proposal. If a decision ever appears inside an n8n workflow, it moves into
> the evaluator or into the agent's proposal space.

### §2B · Thin agentic layer over an LBM-configured chip environment

**Requirement — thin agent, thick environment.** The agentic layer holds **no biology**.
It owns five verbs and a journal. Every constant, prior, threshold, mechanism and
uncertainty estimate lives in the **environment**. The design target is an agent thin
enough that swapping it changes search efficiency and nothing scientific.

#### The environment contract — five calls

| Call | Responsibility | Who may change it |
|---|---|---|
| `configure(θ)` | instantiate a chip: geometry, flow, porosity, strain, **and the binding-site inventory** (P-gp, BCRP, TfR1, FcRn, PepT1 abundance) | human, via `theta_priors.yaml` |
| `reset(drug, schedule)` | load a compound and dosing profile; emit initial observation | agent, freely — this is the action space |
| `step(dt)` | advance occupancy-coupled transport to a quasi-static fixed point | agent may swap the *mechanism*; may not hand-edit a trajectory |
| `observe()` | project state onto readout channels with calibrated uncertainty | human, via the readout heads |
| `score()` | return the gate scalar plus veto flags | **nobody — frozen and versioned** |

> **Determinism requirement.** Given `(θ, drug, schedule, seed)` the environment must replay
> identically. Without bit-comparable replay the keep-or-revert ratchet is meaningless.
> Replayability is a **correctness requirement**, not an engineering nicety.

#### The state IS the occupancy model

```
s_t = ( C_a, C_b, C_free, φ_barrier, θ_target, z_ctx )
```

- `φ_barrier` — fractional occupancy of the transporters/receptors **in the boundary itself**. A **state variable, not a readout**, because it feeds back into flux and saturates.
- `θ_target` — occupancy across the lung target panel.
- `z_ctx` — cell-context embedding, fixed within a run (A7).
- **The commitment:** the environment does not *contain* an occupancy module. **Occupancy is its state.**
- **The consequence:** two chips differing only in binding-site inventory are *two different environments*, not two parameterisations of one.

> **The only dynamic loop in the system:** `C_free → occupancy engine → φ_barrier → ODE flux → C_free`.
> This feedback is what makes the barrier **saturable** rather than a passive filter. If a
> proposed diff adds a second feedback loop, it is no longer a mechanism ablation — it is a
> new environment, and belongs in `theta_priors.yaml` with human ratification.

#### Which LBM supplies which part

| Environment component | LBM providing it | Writes into state |
|---|---|---|
| Binding-site inventory in θ | context/atlas FMs (scGPT, Geneformer, HLCA priors) | transporter + receptor abundance per barrier face |
| Barrier occupancy `φ_barrier` | occupancy engine M2 — co-folding affinity + PLM-interact | saturable carrier terms in `step` |
| Target occupancy `θ_target` | same engine, shared spine | occupancy vector over the lung panel |
| Moiety resolution | surface/interface models — Chai-1, MaSIF/PINNACLE geometry | ranked surface patches (annotations, never state) |
| Readout projection | perturbation models + L1000 heads | transcriptional, viability, barrier channels |
| Long perfusion rollouts | long-context operators (StripedHyena, Mamba) | multi-hour trajectories |
| Frozen scoring | frozen evaluator | gate scalar + veto flags — reads everything, **writes nothing** |

#### The five verbs, specified exhaustively

| Verb | Does | Explicitly forbidden |
|---|---|---|
| **propose** | emit one mechanism diff from the declared hypothesis space | inventing a numeric biological constant |
| **dispatch** | instantiate the environment, run the evaluation contract | reaching into environment internals mid-run |
| **gate** | read `score()`, keep or revert | computing its own metric, or reweighting vetoes |
| **journal** | record finding, diff, seeds, veto state | summarising away a veto, or narrating a result the state does not support |
| **escalate** | nominate ≤8 wet conditions by expected information gain | choosing the acceptance criteria those runs are judged by |

#### Four tests that keep it thin

1. **Constant test** — search the agent layer for numeric biological constants. Any hit is a leak; move it to `theta_priors.yaml` or the §5C register.
2. **Swap test** — replace the orchestrator with a weaker model. Search *efficiency* may degrade; *correctness* must not move.
3. **Replay test** — re-run any kept diff from journal + seed and reproduce the trajectory exactly.
4. **Prose test** — no claim in the journal may exist without a state variable or a metric behind it.

#### Two agents, never sharing a reward

|  | Outer agent — the brain | Inner agent — M5, optional |
|---|---|---|
| Policy over | **experiments** | **molecules** |
| Action | one mechanism diff | one candidate compound/sequence |
| Reward | gated metric improvement, vetoes absolute | readout objective inside the environment |
| Lives | outside the environment | **inside** the environment |

Keeping M5 inside the environment boundary prevents the degenerate loop where the brain's
reward is raised by M5 discovering an exploit in the readout heads.

> **Design rule.** If a capability could plausibly live in either layer, it belongs in the
> environment. The agent should be the least interesting component in the repository.

### §2D · Uncertainty stack

> **Ruling.** Averaging over the chosen binding models is the right *first* move and the
> wrong *only* move. What it yields is **between-model variance over an M-open candidate
> set** — a lower bound on structural epistemic uncertainty, conditional on the model set.
> **Ship the ensemble mean; never ship the ensemble spread as *the* uncertainty.**

Three distinct reasons it is partial: (1) **M-open** — no member *is* the biology;
(2) **ensemble of opportunity** — members are what happened to be published and runnable, not a sample;
(3) **shared bias** — all train on overlapping corpora (PDB, PDBbind, BindingDB, ChEMBL), so
`N_eff` ≪ member count and spread understates error by construction.

Law of total variance: `Var(y) = E_m[Var(y|m)] + Var_m(E[y|m])`. The ensemble sees only the
**second** term. Shared bias contributes **zero** to it and a great deal to the error.

> **Terminology ruling.** Call it **within-ensemble structural variance** / **model-set-conditional
> epistemic uncertainty**. Never "the epistemic uncertainty", never without the set it is conditioned on.

#### The four layers, in order

- **L0 · Aleatoric floor.** Clamp every predictive interval at its label source's noise floor:
  **≥0.5 log** on pKd, **≥0.7 log** on mixed-source panels. (Kramer 2012 σ=0.54 log; Kalliokoski 2013 σ=0.68.)
  A model claiming more precision than its labels possess is miscalibrated by construction. **Enforced in code.**
- **L1 · Do not combine by default — measure `N_eff` first.** Compute effective independent
  model count from member residual correlation on a leakage-controlled holdout. If `N_eff` ≈ 1,
  **ship one spine plus L2** and record it as a finding. Only if `N_eff` is meaningfully >1 does
  combination earn its place, and then by **stacking** on LOO log score — never an unweighted mean.
- **L2 · Explicit discrepancy term** — `y_obs(x) = ζ·f(x,ψ) + δ(x) + ε` (Kennedy & O'Hagan 2001).
  `δ` is the *only* component that can represent bias shared by every member. Tight prior; its
  **fitted magnitude is reported as a diagnostic** — a large δ is an admission the mechanism is wrong.
- **L3 · Conformal, and conditioned.** Split conformal / CQR for distribution-free finite-sample
  coverage, with **Mondrian (group-conditional)** conditioning so the 90% interval holds *per subgroup*.
- **L4 · Spend wet runs on debiasing** — prediction-powered inference: the ≤8 conditions per cycle
  are the gold-standard sample that **debiases** the in-silico population estimate rather than merely scoring it.

#### PoC amendments (recorded, not silently dropped)

| Layer | Full design target | PoC form |
|---|---|---|
| L2 | GP functional discrepancy `δ(x)` | **scalar bias + variance-inflation** with a tight prior (GP returns above ~100 curated on-domain records) |
| L3 | Mondrian grid: target class × scaffold × θ | **two pre-registered groups on one axis — P-gp substrate status**, ≥30 calibration points each, binomial CI on every coverage figure |
| L4 | wet queue | **sealed paper-lab**: curated literature chip records, sealed before modelling, released on a fixed schedule. Retrospective validation only |
| §2A ratchet | — | **selection budget**: ~20–30 gated diffs/milestone; locked test set opened ≤2× |

#### Who owns uncertainty

| Level | Object | Owner | Machinery |
|---|---|---|---|
| Given a mechanism | `p(y ∣ x, θ, m)` | **the environment** | L0 floor, L1 stacking, L2 discrepancy, L3 conformal |
| Over mechanisms | `p(m ∣ D)` | **the brain** | the population of surviving kept diffs |

> **The uncomfortable consequence.** §2A's keep-or-revert ratchet maintains a **point mass** on
> the champion — zero mechanism uncertainty by construction, so a ratcheting agent is
> **structurally overconfident no matter how well calibrated the environment is**. Fix: retain a
> **population of surviving mechanisms** (every kept diff still within noise of the champion) and
> marginalise over it when nominating wet conditions. Keep a leaderboard *and* an ensemble of survivors.

#### Two vetoes this adds

- **Calibration veto.** Mondrian subgroup coverage must hold. A diff that improves the gate scalar while breaking coverage in any reported subgroup is **reverted**, on the same footing as target-shuffle.
- **`N_eff` disclosure.** Every occupancy claim reports **effective**, not nominal, ensemble size.

---

## Part II — Construction (Design)

### The whole design in one picture

```
  drug SMILES ----+
                  |     [E-mol]  RDKit desc + ChemBERTa emb
  dose schedule --+---> [P1] P_app head  --+
                  |     [P2] f_u head      |
  boundary theta -+     [P3] k_sink head   +--> [TRANSPORT CORE]  2-compartment ODE
                                                      |  differentiable, 6 params
                                                      v
                                              C_free(t) at tissue face   <-- the ONLY
                                                      |                      interface
                                                      v
  target panel --> [E-prot] ESM-2 650M --> [OCCUPANCY ENGINE]  public Kd + Boltz-2 fallback
                                                      |  occupancy vector o(t), dim ~300
                                                      v
  cell context --> [E-ctx] atlas priors --> [READOUT HEADS]  L1000 / Tox21 / barrier
                                                      |
                                                      v
                                          y_hat + calibrated intervals
                                                      |
                                                      v
                                       [ACQUISITION]  rank next 8 wet conditions
```

Five replaceable modules, one scalar interface, one uncertainty layer. **Nothing is jointly
trained end to end** — deliberate, justified by the timescale-separation argument in the PRD.

### §1 · Data sourcing

| # | Layer | Source & access | Volume | Lands as |
|---|---|---|---|---|
| **S1** | Chemistry | ChEMBL SQLite dump, PubChem PUG-REST, DrugBank (pinned snapshot) | ~2.4M compounds | `compounds.parquet` (InChIKey, SMILES, logP, pKa, MW, TPSA) |
| **S2** | Affinity | BindingDB TSV, ChEMBL activities, Papyrus, TDC DTI | ~2–3M measured pairs | `affinity.parquet` (InChIKey, UniProt, pAct, type, censor flag, assay id) |
| **S3** | Permeability & ADME | TDC ADME — Caco2_Wang (906), PAMPA, HIA, PPBR, VDss; CycPeptMPDB | 10³–10⁴ labels | `adme/*.csv` with official scaffold splits |
| **S4** | Structure | AlphaFold DB bulk mmCIF for the panel, PDB, PDBbind (→ CleanSplit/GEMS) | ~300 structures for v1 | `structures/` + pocket residue indices |
| **S5** | Device & physiology | OSP PK-Sim model library, PBPK-on-chip review, DigiLoCS | ~50 hand-entered rows | `theta_priors.yaml` (value, range, unit, citation) |
| **S6** | Cellular response | LINCS L1000 GSE92742 / GSE70138 level-5 via `cmapPy` | ~470k signatures, 978 landmark genes | `l1000_level5.h5` subset: lung lines + shared compounds |
| **S7** | Toxicity & barrier | Tox21, ToxCast invitrodb / tcpl | ~10k compounds × tens of assays | `tox.parquet` (compound, assay, AC50, hit call) |
| **S8** | Cell context | Human Lung Cell Atlas, Human Protein Atlas | 2 cell types for v1 | `context.yaml` (cell fractions, transporter/enzyme abundance) |

Everything except full L1000 fits in single-digit GB; subset L1000 *before* writing to disk and the project stays under ~30 GB.

#### §1.2 The harmonization contract

- **Compound identity** — canonical InChIKey from RDKit after salt stripping, neutralization, tautomer canonicalization. **Never join on name or raw SMILES.**
- **Target identity** — UniProt accession, human only, isoform collapsed to canonical; keep the original mapping in a side column for audit.
- **Affinity units** — everything to `pAct = -log10(M)`. Keep Kd, Ki and IC50 as **separate label channels** with a type token; do not average them.
- **Censoring** — preserve `>` / `<` qualifiers as a censor flag. Discarding them biases toward potent compounds.
- **Duplicates** — median-aggregate within (InChIKey, UniProt, assay type); record the IQR as a per-label noise estimate `s_i`, which becomes the observation noise in the loss.
- **Permeability** — all in `log10 (cm/s)`. Caco-2 and PAMPA stay separate tasks sharing an encoder, **never pooled**.
- **Units for θ** — SI everywhere, declared in `theta_priors.yaml` with a citation per entry. Unsourced values flagged `assumed: true`, linking back to A1–A13.

#### §1.3 Splits and leakage defences — report all four

| Split | Construction | Question it answers |
|---|---|---|
| **Scaffold** | Bemis–Murcko, disjoint train/test | does it generalize to new chemistry? |
| **Target cold-start** | held-out UniProt targets, additionally ≤30% sequence identity to any training target | new biology, or memorized targets? |
| **θ-extrapolation** | held-out flow / porosity / strain regimes | is the boundary channel actually used? |
| **Temporal** | train before a cutoff year, test after | the honest proxy for prospective use |

> **Known leakage traps.** TDC ADMET leaderboards: only 3 of 22 top methods passed all checks.
> Protein-LLM benchmarks leak through pretraining overlap. Consequences: (1) never trust a
> leaderboard number as your baseline — re-run it on your split; (2) check test targets against
> the pLM pretraining corpus; (3) keep one truly untouched holdout scored **at most twice**.

### §2 · Objectives — seven losses

| # | Task | Loss | Why this form |
|---|---|---|---|
| **T1** | Permeability & ADME regression (`log10 P_app`, `f_u`, sink) | heteroscedastic Gaussian NLL | the ODE consumes `P_app` as a rate constant; an over-confident estimate propagates into a confidently wrong exposure curve. The variance head is what makes T5 meaningful |
| **T2** | Affinity & occupancy (`pAct`) | Huber on observed + **censored likelihood** on qualified + **pairwise ranking** (λ_rank) | the application is "which condition should I run", so ordinal fidelity is the product. **Occupancy is derived, not learned:** `θ_t = C_free^n/(C_free^n + K_d,t^n)`, `K_d,t = 10^-p̂_t` |
| **T3** | Transport parameter identification | MAP fit in log space with `theta_priors.yaml` prior; only α and the sink coefficient are genuinely free | **No physics-informed loss.** Physics enters as **model structure** (the ODE), never as a penalty term |
| **T4** | Multi-readout mapping (1→many) | masked multi-task, `w_r = 1/√n_r`, CE for hit-calls / Gaussian NLL for continuous; **FiLM** context conditioning, not concatenation | `w_r` stops dense channels swamping sparse clinically-interesting ones. **Anti-shortcut term:** gradient-reversal penalty making the shared latent uninformative about cell-line identity |
| **T5** | Uncertainty & calibration | noise-floor clamp → ×5 deep ensemble + `N_eff` → scalar discrepancy → CQR + two-group Mondrian | conformal delivers coverage distribution-free at one extra data split — highest information-per-FLOP in the design |
| **T6** | Rollout consistency | discounted horizon loss `Σ γ^h ‖ŝ_{t+h} − s_{t+h}‖²`, model's own output fed back | polices the *learned readout dynamics* only — the ODE rollout is stable by construction |
| **T7** | Counterfactual monotonicity | hinge on sign knowledge (higher flow → lower cumulative flux; thicker membrane → lower flux; higher `f_u` → more delivered free drug) | the PRD's most important negative control, **promoted into a training signal**. Closes the "model ignores θ" failure mode at zero cost |

**Composite:** `L = L_trans + λ₁L_perm + λ₂L_aff + λ₃L_read + λ₄L_cf + λ₅L_roll`

Training schedule: (1) T1,T2 heads / encoders frozen → (2) T3 φ fit / T1,T2 frozen →
(3) T4 heads + T7 / transport core frozen → (4) T5,T6 / everything frozen.

> **Never tune λ on the test split.** Set weights by matching gradient norms at initialization,
> then leave them alone. Hand-tuned loss weights are the most common undetected form of
> test-set overfitting in multi-task biology projects.

### §3 · The module stack

| Module | Concrete model | Trainable | Tier |
|---|---|---|---|
| **E-mol** | RDKit descriptors + Morgan FP, optional ChemBERTa | none (frozen) | T0/T1 |
| **E-prot** | ESM-2 650M frozen, mean-pooled + LoRA (r=8–16) when fine-tuning | LoRA only | T1 |
| **E-ctx** | atlas-derived expression vector → small MLP | ~10⁵ | T0 |
| **P1–P3** | LightGBM/XGBoost on descriptors + MLP on embeddings, averaged | ~10⁶ | T0 |
| **Transport core** | 2-compartment ODE, `torchdiffeq` or SciPy `solve_ivp` | 6 params | T0 |
| **Occupancy engine** | public Kd lookup → Boltz-2 affinity for gaps → Hill transform | none at inference | T1/T2 |
| **Pose / interface** | Chai-1 with pocket + contact restraints; AF DB structures | none | T2 |
| **Readout heads** | shared trunk + per-channel heads, FiLM conditioning, ×5 ensemble | ~10⁶–10⁷ | T1 |
| **Uncertainty** | deep ensemble + split conformal | none | T0 |
| **Acquisition** | BALD over the ensemble (BatchBALD for the top-8 batch) | none | T0 |

Rationale: frozen foundations + small heads (LoRA matches/beats full FT at 0.25% of parameters;
pLM gains plateau at 1–4B and *decline* beyond ~5B); **derived, not learned, occupancy** (the Hill
transform is exact given Kd — learning it burns data to rediscover thermodynamics and invites
reward hacking); **ODE, not neural, transport**; **structure prediction outside the loop** (cache
co-folding as preprocessing).

### §3.3 Budget

| Job | Hardware | Wall-clock |
|---|---|---|
| ETL + harmonization (S1–S8) | laptop CPU | ~1 day, mostly downloads |
| P1–P3 heads (5-fold CV) | CPU | minutes |
| ESM-2 embeddings, ~300 proteins | 24 GB GPU | ~15 min (cache; never recompute) |
| LoRA fine-tune of E-prot | 24 GB GPU | 2–6 h (only if frozen embeddings underperform) |
| Boltz-2 affinity, ~2000 pairs | 24 GB or burst L40S | **~20–30 GPU-h — the single largest line item** |
| Chai-1, ~100 complexes | burst A100/L40S | ~2–5 min each |
| Readout heads ×5 | 24 GB GPU | ~1–3 h |
| Conformal calibration + eval | CPU | minutes — run on every commit |

**Bottom line:** a complete v0→v2 cycle is ~**40–80 rented GPU-hours**; Modal's free Starter
credit (~$30/mo ≈ 40–50 T4-h) covers the trimmed PoC panel (~15–30 h). **The binding constraint
is attention and data hygiene, not FLOPs.**

### §4 · Application

```python
from chipsim import ChipSim
sim = ChipSim.load("v1")           # frozen encoders + calibrated heads
result = sim.predict(
    drug="CC(=O)Oc1ccccc1C(=O)O",   # SMILES
    dose=dict(c_in_uM=10.0, schedule="bolus", duration_h=24),
    theta=dict(flow_ul_min=30.0, membrane_um=10.0, porosity=0.4,
               strain_pct=10.0, area_mm2=17.0, coating="collagen-IV"),
    context="alveolar_epithelium+microvascular_endothelium",
    readouts=["barrier_TEER", "IL6", "IL8", "viability", "L1000_sig"],
)
result.exposure     # C_free(t) with 90% conformal band
result.occupancy    # ranked target vector at C_max and at AUC-equivalent
result.readouts     # per-channel prediction + interval
result.moieties     # ranked surface patches per engaged target
result.attribution  # which occupancy terms drive which readout
```

**Three applications, in order of payoff:** (1) **dose-window finder**; (2) **one drug → many
moieties attribution** (the scientific payload — a ranked falsifiable hypothesis list, not a
single answer); (3) **condition proposer** — rank wet conditions by expected information gain
(BALD), returning the top 8 subject to a diversity constraint (BatchBALD prevents top-k collapse).

**Model card (§4.3)** — every release ships fold-error and Spearman ρ per split (**all four**),
calibration coverage at 50/80/90%, the scrambled-θ control result, the affinity-matched /
P_app-differing disambiguation test, and the active assumptions with their break tests.
*A version without this card is a demo, not a validation instrument.*

### §4.4 Repository layout

```
chipsim/
  data/            raw/ interim/ processed/     # DVC-tracked, never in git
  chipsim/
    ingest/        chembl.py bindingdb.py tdc.py lincs.py tox21.py
    harmonize/     ids.py units.py dedupe.py contracts.py   # assertions live here
    encoders/      mol.py prot.py ctx.py
    heads/         perm.py fu.py sink.py readouts.py
    transport/     ode.py fit.py theta.py
    occupancy/     lookup.py boltz.py hill.py
    surface/       chai.py moiety.py
    uncertainty/   ensemble.py conformal.py
    eval/          splits.py metrics.py controls.py card.py
    acquire/       bald.py diversity.py
  configs/         theta_priors.yaml assumptions.yaml env.yaml
  orchestration/   n8n workflow JSON exports (versioned here), modal_app.py
  journal/         append-only run records — diff, seeds, scores, veto state
  notebooks/
  tests/           test_contracts.py test_leakage.py test_monotonicity.py
```

> **Three tests that must exist from day one.** A **data-contract** test (units, identifiers,
> no duplicate keys), a **leakage** test (no test scaffold or target in train; no test target
> above the identity threshold), and a **monotonicity** test (raising flow lowers cumulative
> flux). If these three pass, most catastrophic silent failures are already excluded.

### §5 · Milestones

| Milestone | Contents | Gate to pass |
|---|---|---|
| **M0** | ETL + harmonization + splits + three tests + **literature chip-run curation** | contracts green; splits reproducible from a seed; **60–100 curated on-domain records** with a sealed, disjoint allocation (δ-calibration / conformal calibration / locked test / active-learning pool) written down **before any are read** |
| **M1** | ODE core with literature θ, reference compounds | published on-chip ordering reproduced **within 3-fold** |
| **M2** | P1–P3 heads replace all hand-set constants | **Spearman ρ ≥ 0.6** on held-out scaffolds for exposure AUC |
| **M3** | Occupancy engine with Boltz-2 gap filling | known mechanism-of-action targets in **top-10 occupancy** |
| **M4** | Readout head + context conditioning, **one channel only at PoC** (barrier_integrity) | channel calibrated within tolerance; **cell-line adversary at chance** |
| **M5** | Uncertainty stack (T5) + full evaluation card | **90% interval covers ~90% in each of the two pre-registered P-gp groups, with binomial CIs**; scrambled-θ control collapses; `N_eff` disclosed |
| **M6** | Acquisition loop — **retrospective replay only** | on the sealed paper-lab pool, error falls faster per revealed record than random selection; **no novelty claim** |

**Roadmap:** ~3.5 months calendar at nights-and-weekends pace, ~$0–150 compute, and one
unavoidable human-bound block (M0 curation) that no agent accelerates.

> **Curation is the critical path, not compute.** If M0 curation stalls below ~40 records, the
> correct response is to **drop the L2 discrepancy layer and the two-group veto and say so on the
> model card** — never to reuse the same records for calibration and testing.

### §6 · Risk register

| Risk | Early warning | Mitigation |
|---|---|---|
| L1000 heads learn cell line, not biology | adversary predicts cell line above chance | gradient reversal; hold out entire cell lines |
| Occupancy dominated by missing off-targets | top-10 panel unstable across seeds | widen the panel; report occupancy entropy |
| Public affinity heterogeneity swamps signal | censored fraction correlates with residual | keep assay-type channels separate; weight by label IQR |
| **θ channel ignored** | scrambled-θ control does not collapse | strengthen T7 monotonicity; enforce θ-extrapolation split |
| Structure jobs become the bottleneck | GPU spend dominated by co-folding | precompute and cache; AF DB structures; restrain Chai-1 to a pocket |
| Scope creep into CFD | someone proposes a mesh | **the PRD forbids it**; physics enters only as ODE structure |
| Gatekept data stalls the calendar | DrugBank / PDBbind application pending | neither is load-bearing — apply day 0, build without them |
| Free-tier compute starvation | Modal credit exhausted mid-cycle | stage heavy jobs one per monthly cycle; 24 GB local GPU is the daily driver |
| **n8n becomes a second brain** | an if-node starts weighing a veto | forbidden by construction — all gating lives in the frozen evaluator service |
| On-domain curation falls short | <40 curated chip records at M0 | drop L2 + the two-group veto; record the downgrade on the card — **never double-use records** |

---

## Licence guardrails (binding on implementation)

- **Boltz-2** — **MIT end to end** (code, weights, training code) and **affinity-capable**. The only model that may legally and technically sit inside the automated loop → **the default occupancy engine**.
- **Chai-1** — **Apache-2.0 code *and* weights** since Nov 2024. May sit inside an automated loop; used for **geometry/moiety localization only, never scoring**.
- **AlphaFold Server** — non-commercial; ToS **forbids** use "in any automated system that predicts the binding or interaction of the protein with ligands or peptides" and forbids training structure-prediction models on its outputs. **Manual, one-off hypotheses only — never an automated occupancy oracle.**
- **AlphaFold 3** — Apache-2.0 code, weights require academic-affiliation request → assume unavailable.
- **DrugBank** — pinned public **4.2 snapshot (2015-03-19)**, CC BY-NC 4.0. Identity + drug→transporter/carrier edges **only, never affinities**. 2015 vintage **forbids any coverage claim**.
- **n8n** — self-hosted CE under the Sustainable Use License (fair-code): free for personal/internal use; never redistribute or offer as a service.
- **Overall posture** — non-commercial personal research.
