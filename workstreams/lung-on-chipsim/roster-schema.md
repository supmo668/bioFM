# Compound roster — attribute schema and distributional acceptance criteria

**Status:** approved for authoring by the principal, 2026-09-12 — *"define the key attributes of the
molecules including the type of interaction, to justify the choices based on data distribution as a
well-defined minimum validation set."* Authored by the CTO.

**What this document is and is not.** It defines the **attributes** every roster record must carry and
the **distributional properties** the finished roster must satisfy. It does **not** name compounds.
T18 remains a human artifact: the schema makes the curation checkable, it does not perform it.

> **The point of the schema.** A roster justified by "these are well-known lung drugs" cannot be
> defended. A roster justified by *its distribution over declared axes* can — and the same axes make
> the difference between a validation set and a convenience sample measurable rather than asserted.

---

## 1 · Record attributes

### 1.1 Identity — the join keys

| Field | Type | Notes |
|---|---|---|
| `inchikey` | string | **The canonical join key.** Computed by RDKit at the pinned version — `rdkit` is `==`-pinned precisely because it computes this and the sealed allocation keys on it |
| `smiles` | string | Canonical, as stored |
| `name` | string | Human-readable; never a join key |
| `drugbank_id` | string \| null | From the pinned 2015 snapshot. Null is legitimate and must not be inferred |

### 1.2 Interaction type — what makes this a *transport* validation set

This block is the reason the roster is not a generic chemistry set. One row **per (compound, transporter)** pair, not per compound.

| Field | Values | Why it is needed |
|---|---|---|
| `transporter` | UniProt accession from `barrier_panel.yaml` | Ties the row to a ratified panel entry |
| `interaction` | `substrate` · `inhibitor` · `non_substrate` · `unknown` | **Four values, not three.** `unknown` is a distinct state, never a silent `non_substrate` — the same rule that saved ABCB1 |
| `direction` | `efflux` · `uptake` · `passive` | Mechanism class. The barrier is saturable only through carrier terms; `passive` rows exercise the baseline |
| `evidence_class` | `measured` · `literature` · `inferred` | `inferred` rows may never enter the P-gp grouping variable |
| `source` | source id from `data/raw/sources.yaml` | Every row traces to an audited source |
| `assay` | string \| null | Assay identity, for the duplicate-aggregation rule |
| `value`, `unit` | float, string \| null | Null where the claim is qualitative |
| `censored` | `none` · `left` · `right` | A `>10 µM` is **not** a measurement of 10 µM |
| `noise_estimate` | float \| null | Per-label `s_i` — the IQR of duplicates. Intervals clamp at this floor |

> **Why `inhibitor` is separate from `substrate`.** They are different mechanisms with opposite
> consequences for delivery: a substrate is moved, an inhibitor blocks movement of others. A roster
> that conflates them cannot support the occupancy→delivery link, because the link's sign differs.

### 1.3 Physicochemical axes — the distribution the roster is justified by

| Field | Why this axis |
|---|---|
| `mw` | Size drives passive permeability and carrier recognition |
| `logp` | The single strongest passive-diffusion axis |
| `tpsa` | Polar surface area — and the axis chameleonicity moves along |
| `hbd`, `hba` | Hydrogen-bonding capacity; carrier recognition |
| `rotatable_bonds` | Conformational flexibility |
| `charge_ph74` | Charge state at physiological pH — decisive for transporter recognition |
| `aromatic_rings` | Scaffold rigidity |

These are **declared axes**, so "the roster spans chemical space" becomes a measurable claim rather than a rhetorical one.

### 1.4 Structure and stratum

| Field | Values | Notes |
|---|---|---|
| `stratum` | `diversity` · `pair` | Two strata, analysed separately. **Pair-stratum members never count toward the diversity stratum's power** |
| `murcko_scaffold` | string | Bemis–Murcko scaffold id |
| `is_acyclic` | bool | **Load-bearing.** Murcko is blind to acyclic series — six homologous fatty acids measured as fully independent. Lands directly on transporter substrates: carnitine, choline, amino acids, polyamines |
| `series_id` | string \| null | Explicit series membership where Murcko cannot see it |
| `mmp_partner` | inchikey \| null | Pair stratum only |
| `mmp_transformation` | string \| null | The single-site change |
| `fold_change` | float \| null | Must be **≥100** for a cliff pair |

### 1.5 Lung relevance — the PoC's domain

| Field | Notes |
|---|---|
| `route` | `inhaled` · `systemic_lung_exposure` |
| `published_exposure` | The reference value the v0 ordering test scores against |
| `exposure_source` | DOI or PMID. **No value without a citation** |

---

## 2 · Distributional acceptance criteria

A roster satisfying §1 may still be a bad validation set. These are the properties that make it a **minimum** one — each is checkable by script, and each exists because a specific failure is otherwise invisible.

| # | Criterion | Why — the failure it prevents |
|---|---|---|
| **D1** | **Both P-gp groups ≥ 20** curated records; `unknown` in neither | The Mondrian coverage claim conditions on this grouping variable. Folding `unknown` into `no` fabricates a group and voids the conditional claim |
| **D2** | **Interaction types all populated**: ≥1 `inhibitor`, and both `substrate` and `non_substrate` well represented | A roster of only substrates cannot show the model *discriminates* — it can only show it agrees. The negative class is what makes the claim falsifiable |
| **D3** | **≥1 non-monotonicity case** — a pair where *reducing* affinity *increases* delivery | §5E never defers this. Without it the occupancy→delivery link's valley is untested, and a monotone link is disqualifying rather than merely inaccurate |
| **D4** | **Diversity stratum: singleton fraction high, no scaffold with >2 members** | Analog series cut power 0.95 → 0.46. This is the criterion that makes ~30 diverse compounds beat 40 clustered ones |
| **D5** | **Acyclic check passes** — homologous series flagged via `series_id`, not trusted to Murcko | Murcko reported six homologous fatty acids as fully independent. **Blindness is not evidence of independence**, and it lands precisely on this domain's substrates |
| **D6** | **Pair stratum: ~50 MMP pairs**, single-site, `fold_change ≥ 100` | R5's power. **Never loosen the cliff to fill the stratum** — report the achieved count instead (ADR-0004) |
| **D7** | **Every `measured` row carries `noise_estimate`**, and intervals clamp at it | An interval narrower than the assay noise floor fails §5E irrespective of accuracy |
| **D8** | **Every `published_exposure` carries a citation** | A reference value without a source is an assertion the v0 test then scores against |
| **D9** | **Realised power reported, not assumed** | Power is computed from the *realised* roster via `clustered_sign_test_power`, never from effective *n* — at equal effective *n* = 20 a diverse roster measured 0.69 and a clustered one 0.92 |

### What a failing roster does

**It reports, it does not get repaired by loosening a criterion.** If D6 cannot be met, R5 reports the achieved pair count and its power. If D1 cannot be met, the Mondrian claim is reported as unevaluable. The criteria are acceptance tests, not targets to be reached by redefinition — that is the discipline the sealed-formula rule exists to protect.

---

## 3 · Why this constitutes a minimum validation set

Each criterion maps to a claim the PoC makes. Drop the criterion and the claim becomes unfalsifiable rather than merely weaker:

| Claim under test | Criterion that makes it falsifiable |
|---|---|
| Exposure ordering, ρ ≥ 0.6 | D4, D5 (real independent *n*), D8 (a reference to score against) |
| MoA targets in top-10 occupancy | D2 (a negative class to discriminate against) |
| 90% Mondrian subgroup coverage | D1 (both groups populated), D7 (a noise floor to clamp at) |
| Moiety sensitivity (R5) | D6 (cliff pairs at a pre-registered magnitude) |
| The delivery claim | D3 (the valley case) |
| Any power statement | D9 (realised, not assumed) |

**The set is "minimum" in a precise sense:** removing any one criterion leaves a roster that can still produce a number, but produces one that cannot be wrong. That is the property being bought — not size, and not coverage for its own sake.
