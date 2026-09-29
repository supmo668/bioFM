---
type: paper-design
workstream: lung-on-chipsim
author: bioFM/matthew-mo/cto
date: 2026-09-26
status: design — NOT authorised to draft; queued behind the gate-6 iteration
genre: Stage 1 registered report (methods + pre-registered analysis plan, submitted before results exist)
principal_decision: registered report, chosen 2026-09-26
---

# lung-on-chipsim — Stage 1 registered report: design

## 1. Why this genre, and why it is not a workaround

The project has **complete machinery and zero results**, and that is by design rather than by
delay. Measured 2026-09-26:

| built | absent (human-owned) |
|---|---|
| `chipsim/transport/{ode,fit,prior,theta}.py` — 2-compartment ODE + MAP fit, ~920 lines | `configs/theta_priors.yaml` |
| M0a parsers, contracts, tests | `configs/assumptions.yaml` |
| `configs/poc_compounds.yaml` (T18 roster) | `configs/transport_prior.yaml` (T28) |
| E-21/E-22/E-23 content guards | **0** curated chip records (M0b target: 80–100) |
| 51 hash-locked plan revisions, r2 → r2.48a | no frozen evaluator signature (M0c) |

`fit.py` will refuse to run: `_require_sourced_theta` enforces Global Constraint 1 — *no coding
agent writes a biological number.* So results are gated on human judgement, permanently and
deliberately.

A **Stage 1 registered report** submits the methods and the pre-registered analysis plan for peer
review *before* results exist, for in-principle acceptance; Stage 2 adds results later. That makes
the blocker the genre rather than an obstacle to route around — and this project is unusually
well-suited, because **it already pre-registers**: the P-gp subgroups are fixed before any coverage
is computed, the evaluator is frozen and signed before fitting, and the selection budget is
declared in advance.

**The dishonest alternative to avoid:** a conventional paper whose results section is thin or
whose methods imply results exist. Stage 1 says plainly that no results have been observed, which
is the accurate claim.

## 2. Dual granularity — two artifacts, written separately

Per the principal's "dual level of granularity":

| | Long form | Short form |
|---|---|---|
| Genre | full Stage 1 registered report | conference submission |
| Reader | a referee deciding in-principle acceptance | a programme committee and a conference audience |
| Contains | every pre-registered hypothesis, the full analysis plan, the complete decision-record analysis (§4) | the design's one novel claim, one figure, the pre-registration commitment |
| Length | journal Stage 1 norms | conference norms |

**Write the short form SECOND and SEPARATELY, from the claim list — never by cutting the long
one.** Summarising a long paper produces a shortened long paper, which is the failure this
instruction exists to prevent. Both derive from one **claims list** (§6); neither is the other's
parent.

## 3. Stage 1 content, mapped claim → artifact

Every claim must point at something a referee can open. **A claim with no artifact is cut, not
softened.**

| section | claim | artifact that supports it |
|---|---|---|
| Methods — model | 2-compartment transport ODE; MAP fit of exactly two free parameters in log space | `chipsim/transport/ode.py`, `fit.py`; A&D §2 objective T3 |
| Methods — determinism | given `(θ, drug, schedule, seed)` replay is bit-comparable; without it the keep-or-revert ratchet is meaningless | A&D "Determinism requirement"; `fit.py`'s deterministic Nelder-Mead start, with its recorded reason |
| Methods — priors | every θ entry is SI, carries a citation, and an unsourced entry is flagged `assumed: true` | A&D §2; `theta.py`'s `ThetaField`; the scaffold template; `_require_sourced_theta` |
| Pre-registration — gates | the metric is a **vector**: a gate scalar **plus** vetoes, and vetoes are absolute | A&D §2A; target-shuffle, cliff-stratified accuracy, non-monotonicity, calibration each hold a veto |
| Pre-registration — selection | 20–30 gated diffs per milestone, pre-registered; locked test set opened **≤2× in the project's lifetime**; the gate-evaluation count is reported next to coverage | A&D §2A selection budget |
| Pre-registration — subgroups | the two P-gp groups are fixed **before** any coverage is computed | build-plan M5; A&D §2D |
| Integrity | agents cannot author biological values; the agent writes the schema and the validator that rejects an unsourced entry | Global Constraint 1; `_require_sourced_theta` |
| Integrity | content guards fail **closed**, and their own blind spots are measured rather than asserted | E-22/E-23 range; gate-6 survivor analysis, each survivor paired with the measurement showing why nothing saw it |
| Audit trail | §4 |

**Named and explicitly NOT claimed** (a Stage 1 that lists only what it establishes reads as a
blank cheque): no results observed; no fit performed; the 3-fold ordering gate untested; coverage
uncomputed; no wet-lab validation; the ODE is a PoC 2-compartment model, not a physiological one.

## 4. Methodology variational analysis — the novel contribution

**Interpretation, stated so it can be corrected:** I read "variational analysis" as *analysis of
methodological variants* — which choices were forced, which were free, which alternatives were
rejected and on what grounds. **If the intended reading was a sensitivity analysis of the MAP fit
to its priors, that is Stage 2 work and cannot be done before θ exists.** Both are worth doing;
only the first is possible now.

The evidence is unusual and is the reason this paper is worth writing:
**`plan-approval-log.md` is a contemporaneous, append-only, hash-locked record of 51 methodological
revisions**, each naming what changed, why, and who approved it by which route. Most papers
reconstruct their design rationale afterwards; here it was written as the decisions were made and
each revision is cryptographically bound to the plan text it approved.

Measured route distribution across the log:

| route | count | meaning |
|---|---|---|
| `standing-delegation` | 43 | CTO-invoked under a recorded delegation — *the judgement was the principal's, the invocation was not* |
| `principal-directed` | 4 | explicit real-time direction |
| `human-direct` | 2 | principal signed or instructed in so many words |
| mixed | 2 | — |

**That distribution is itself a reportable datum**, and it answers the question a referee of
AI-assisted science actually has: how much of this methodology was chosen by a human, and how much
by an agent under delegation? Reporting **43 of 51** honestly is stronger than implying human
authorship throughout.

The section should also carry the **reversals**, not only the decisions. Several revisions exist
because a ruling was measured and found wrong — and the log records the correction beside the
original rather than replacing it. A methods section that shows its own corrections is more
credible than one that reads as though nothing was ever wrong.

## 5. Stage 2 critical path — what only the principal can supply

Listed so the path to results is legible, not to schedule it here:

| item | what it is | why no agent may do it |
|---|---|---|
| **T20** `theta_priors.yaml` | 6 device/physiology fields, each cited | Global Constraint 1. Four already have citable values from the Huh/Ingber line approved 2026-09-23 (`membrane_um`, `strain_pct`, `coating`, flow); `porosity` and `area_mm2` remain, with `assumed: true` + a stated width recommended |
| **T21** reference compounds | 3–8 with published on-chip transport data | a curated scientific claim |
| **T28** `transport_prior.yaml` | the `(α, k_sink)` prior | per Finding E it does real work on the reported result |
| **M0b** | 80–100 curated chip records, sealed three-way | the binding cost of the PoC; every record human-owned |
| **M0c** | signature on the evaluator freeze | the freeze is only meaningful if a human commits to it before results |

## 6. Entry conditions for CTO rigour review

Following the BioSim white-paper precedent, review does not begin until:

1. A **claims list** exists: one row per claim, each with its artifact path and the sentence it
   supports. This is the input to both granularities (§2).
2. A **traceability check** runs: every claim in the draft resolves to an artifact that exists.
   A claim whose artifact is missing fails the check rather than being footnoted.
3. **No result numbers appear anywhere**, including as illustrations or placeholders. A worked
   example must be visibly synthetic and labelled as such.
4. The **not-claimed list** (§3) is present in both granularities.

## 7. Hard constraints on the draft

- **No agent-authored biological values**, including in worked examples. Invented values are
  marked invented.
- **The identifier constraint holds throughout**: describe the *form* of an identifier; never pair
  a value with what it denotes. This has already been breached twice in this workstream by
  subagents — see the principal's retroactivity item H.
- **No claim the artifacts do not support.** The gate-6 range exists because claims outran their
  evidence; this paper is about that discipline and must not violate it.
- **`self-improvement` is a mechanism, never a measured result** — the same rule the BioSim white
  paper carries.

## 8. Sequencing

1. Finish the **gate-6 iteration** (#410). Nothing here starts before it.
2. Author the **claims list** (§6.1) and submit it for CTO review. Cheap, and it settles scope
   before prose exists.
3. Long form Stage 1.
4. Short form, written separately from the claims list.
5. CTO rigour review against §6 conditions.
6. Venue selection and the principal's go. **No deposit, submission or preprint without an
   explicit instruction** — per the standing rule that the first live contact is sandbox-only.
