# ChipSim

A lung-on-chip simulator that predicts drug exposure and barrier response, and reports
honest uncertainty about those predictions. This glossary fixes the language of the
evaluation and data layers, where several terms have historically been used for more
than one thing.

## Language

### Data subjects

**Compound**:
One chemical entity in the proof-of-concept set — an inhaled or lung-relevant drug with
published exposure data. The PoC set is 20–40 compounds, hand-curated, plus matched
molecular pairs for the cliff test.
_Avoid_: drug, molecule, ligand

**Curated chip record**:
One published lung-on-chip run — a single **compound** observed under one device and
condition. Several records can share a compound, which is why 20–40 compounds yield a
target of 60–100 records. The unit of the sealed allocation.
_Avoid_: chip run, data point, sample, observation

**Calibration point**:
One **curated chip record** that has been allocated to the conformal-calibration bucket.
Never a **compound**. Coverage requirements expressed in calibration points are
requirements on records, not on chemistry. The PoC requires **~20 per pre-registered
group**, two groups (see AM-6, resolved).
_Avoid_: calibration sample, calibration compound

### Evaluation

**Sealed allocation**:
The disjoint, written-down assignment of every **curated chip record** to exactly one
bucket, fixed before any record is read. Records are never double-used across buckets.
**In the PoC the allocation is three-way** — δ-calibration, conformal calibration, locked
test. The **active-learning pool** is a fourth bucket that belongs to v3; the PoC runs no
exploration loop, so it allocates no records to it.
_Avoid_: split (reserve "split" for the four §1.3 generalization splits)

**Split**:
One of the four §1.3 generalization partitions — scaffold, target cold-start,
θ-extrapolation, temporal — each answering a different question about generalization.
Distinct from the **sealed allocation**, which is about record reuse, not chemistry.

**Replay test**:
Names **two different tests** at two different rungs, and they must not be conflated.
The **PoC form** (v0+v1): *same config + same seed reproduces the same scores exactly.*
The **v3 form** (A&D "four tests that keep it thin"): *re-run any kept diff from journal +
seed and reproduce the trajectory exactly* — a test of the agent exploration loop, which
requires a kept **diff** and a **veto state** that only v3 produces. The PoC cannot run the
v3 form because it has no exploration loop, and its absence is not a defect in the PoC.
_Avoid_: using "the replay test" unqualified

**Frozen evaluator**:
The immutable, versioned scorer that is itself the project deliverable. Outside the
agent's write scope; served as a versioned interface that nobody may edit in place.
_Avoid_: scorer, eval harness, metrics module

**P-gp substrate status**:
A three-valued attribute — `yes` / `no` / `unknown` — of a **compound**, not of a record.
Absence of evidence yields `unknown` and never `no`; `no` is assignable only by human
adjudication carrying a citation.
_Avoid_: P-gp label, efflux flag

### Panels

**Barrier panel**:
The *identity* of the transporters and receptors at the barrier — symbol, UniProt
accession, alias, membrane face, and a ratification flag. Identity only; carries no
numbers. Drafted by the coding agent, ratified by a human.
_Avoid_: binding-site inventory (that name covers the abundances, not the identities)

**θ priors**:
The *quantities* — abundances, flow, area, thickness, strain — each with value, range,
unit and citation. Always human-entered. Disjoint from the **barrier panel**, which
holds no quantities.
_Avoid_: parameters, constants

**Target panel**:
The ~30 proteins scored for occupancy — MoA targets of the reference set plus the
barrier carriers. Distinct from the **barrier panel**, which is the transporter/receptor
set at the barrier itself.

## Flagged ambiguities

**"Calibration point" was undefined and load-bearing.** §2D requires ≥30 calibration
points in each of two pre-registered P-gp groups. Read as **compounds**, that demands ≥60
against a set of 20–40 and fails outright. Read as **curated chip records** — the reading
adopted here — a four-way sealed allocation of 60–100 records leaves roughly 8–15 per
group, so reaching 2×30 in the conformal bucket alone needs ~200–240 records, two to four
times the M0 target at its ceiling. **Resolved: a calibration point is a curated chip
record.**

**AM-6 RESOLVED (principal, 2026-09-02).** The arithmetic closes by removing a bucket, not
by weakening the claim. The **active-learning pool** is v3 machinery and leaves the PoC's
sealed allocation, making it three-way; the per-group requirement drops to **~20**, giving
~40 conformal points against ~20 δ-calibration and 20–40 locked test — **80–100 records**,
inside the M0 target. The claim stays **conditional** (Mondrian), because §5E forbids
marginal coverage in terms. Conformal coverage is distribution-free and **valid at n=20**;
what degrades is the precision of the coverage estimate, not the guarantee — so every
coverage figure is reported **with its confidence interval, per group**. A coverage number
without its CI at this n is the same error as reading a wide interval as a clean result.

**"Panel" named four different objects** across the plan, A&D and PVR — the barrier
transporter set, the binding-site inventory in θ, the ~30-protein target panel, and the
PoC's two-carrier barrier. Resolved above by splitting **barrier panel** (identity),
**θ priors** (quantities) and **target panel** (occupancy scoring).

**"Contract test" named two different things** — the A&D's data-contract test (units,
identifiers, no duplicate keys) and the build plan's provenance and non-vendoring checks.
Both are legitimate; they are not the same test and should not share an unqualified name.

## Example dialogue

> **Dev:** The coverage requirement is thirty per group. We only have twenty-eight
> compounds with a firm P-gp call — do we fail?
>
> **Domain expert:** Those are different units. Thirty is thirty *calibration points*,
> and a calibration point is a curated chip record in the conformal bucket. Your
> twenty-eight compounds might be seventy records.
>
> **Dev:** So more records fixes it?
>
> **Domain expert:** Only records that land in the conformal bucket. The sealed
> allocation splits everything four ways before anyone reads a record, so seventy total
> is maybe eighteen calibration points. You'd need a couple of hundred records before two
> groups of thirty exist.
>
> **Dev:** And the ones we can't call — do they go in the `no` group?
>
> **Domain expert:** Never. Unknown is its own value. If we don't have a citation saying
> it isn't a substrate, it stays unknown and sits out of both groups. Absence of an edge
> in a 2015 snapshot is not evidence of absence.
