# A&D — ChipSim LBM Audit: do the foundation models resolve moiety-level chemistry?

**Workstream:** `chipsim-lbm-audit` · **Module:** `lung-on-chipsim` · **Status:** draft (design r1.0)
**Consumes:** [PVR](./PVR.md) (approved 2026-09-01)
**Companions:** [ChipSim PVR](../lung-on-chipsim/PVR.md) · [ChipSim A&D](../lung-on-chipsim/A-and-D.md) · [build plan](../lung-on-chipsim/plan/build-plan.md)
**Linear:** [biofm-chipsim-lbm-audit — moiety sensitivity](https://linear.app/syntropyhealth/project/biofm-chipsim-lbm-audit-moiety-sensitivity-6ee98c1f55fa)

> **Scope.** This is a **method-validation study**. It informs the ChipSim programme; it does not
> advance the M0–M6 ladder. It builds no ODE, no readout head, no acquisition loop, and it does
> not touch the frozen evaluator.

---

## Part 0 — Inherited state this design must not misread

Five human artifacts remain **absent**. `configs/barrier_panel.yaml` carries `ratified: false`.
**Global Constraint (4)** — sealing is reserved to a human — stands, with the enforcement posture
already recorded in `chipsim/pipeline.py`: it is *"a stated rule with no technical force."*

Two consequences bind this design, and both are made **mechanical** rather than left as notes,
because a note is exactly what fails at 2am:

1. **The audit may not consume the live ratified panel** (Global Constraint (4); the panel is not
   ratified anyway). It runs against a committed fixture panel, and the *claim it is allowed to
   make* narrows automatically — see §R2.4 **Claim narrowing**.
2. **No agent runs `prereg-seal` against a live pre-registration.** Same reservation, same
   non-enforcement, same fixture-only rule for agent-side work.

---

## Part I — Approaches & decision

Three choices are load-bearing. The rest follow from them.

### D1 · Where the audit code lives

| Option | Trade-off |
|---|---|
| (a) separate repo | Clean isolation; but duplicates the journal + seal primitives, and R10 replay would fork from S12's record format — two record formats is how replay dies. |
| (b) inside `chipsim/` as ETL stages | Maximum reuse; but puts a *study* into the *product* pipeline, and an audit stage in the n8n workflow is a second brain by the back door (A&D §2A). |
| **(c) `chipsim/audit/` — a sibling package, one-way dependency** | **Chosen.** Reuses `chipsim/journal.py` (S12) and the seal primitive verbatim, so R10 replay reads one record format. Imports flow **audit → chipsim core, never core → audit**, so the ladder cannot come to depend on a study. No audit entry point is registered in `SUBCOMMANDS`, so none can enter the n8n ETL workflow. |

**Test criterion for D1 itself:** a test asserts no module under `chipsim/` outside `chipsim/audit/`
imports `chipsim.audit`, and that `available_subcommands()` contains no audit stage. The one-way
rule is the kind of thing that holds for six weeks and then quietly stops; it gets a test.

### D2 · What makes the pre-registration seal actually bite — **the R2 decision**

This is the requirement most likely to be over-claimed, so it is specified before it is built.

R2 asks that a threshold edited after seeing results **fail loudly**. A digest alone does not
deliver that, and it is worth being exact about why:

- A digest detects an **unsealed** edit. Edit `prereg.yaml` without re-sealing → verification
  raises. That case is covered.
- A digest does **not** detect a **re-sealed** edit. Run the study, look at the numbers, widen the
  ambiguity band, re-run `prereg-seal`, and the new digest verifies perfectly. Nothing in the digest
  distinguishes "sealed before the first complex" from "sealed after the last one" — the digest
  carries no ordering.

So the seal is **two mechanisms, not one**:

| Mechanism | Catches | Does not catch |
|---|---|---|
| `prereg_sha256` over canonical content | unsealed post-hoc edits | re-sealing |
| Seal invocations journalled as S12 `invocation` records, against the run records in the same journal | **re-sealing after results exist** — a seal record timestamped after run records for the same pre-registration is visible on inspection | a journal discarded wholesale |

The second is the same move S12 makes for `panel-seal`: *"Recording every invocation is what makes a
Global Constraint (4) violation detectable."* Ordering evidence comes from the journal, never from
the digest. Options (a) refuse re-sealing outright and (b) silently overwrite were both rejected —
(a) because a legitimate pre-registration amendment before the first run must remain possible, and
(b) because silence is the failure mode. **Re-sealing is permitted, recorded, and never silent.**

> **§D2.1 · Honesty clause — binding on module, docstring, CLI help, report and paper.**
> The pre-registration seal uses the same digest trick as the panel seal and inherits **the same
> limit**. It detects that a threshold was **modified**; combined with the journal it makes a
> **re-seal after results visible**. It does **not prove who sealed it.** The digest is unkeyed over
> public content, so anything able to write the pre-registration can also compute its digest.
> Global Constraint (4) reserves sealing to a human; that is a **stated rule with no technical
> enforcement**.
>
> **Detection is not attestation, and visibility is not proof of authorship.** No wording anywhere
> in this workstream may describe the seal as authenticating, attesting to, or proving the identity
> of whoever sealed it. This conflation cost four gates to remove from the panel seal; it is written
> down here so it is not reintroduced under a new name.

### D3 · The form of the R3/R4 statistic

| Option | Trade-off |
|---|---|
| (a) report native-arm agreement | Rejected outright — R3's test criterion fails a run producing only the native arm. |
| (b) unpaired difference of aggregate agreements | Discards the pairing that makes this study powered at n≈40 compounds. |
| **(c) paired difference, bootstrapped over ligands** | **Chosen.** Every arm scores the **same ligand set**; the reported number is the *difference*; CI by bootstrap resampling **over ligands, not over pairs** — pairs sharing a ligand are not independent, and resampling pairs would report a confidence interval narrower than the data supports. |

---

## Part II — Components & interfaces

```
projects/lung-on-chipsim/
  chipsim/audit/
    __init__.py
    prereg.py       R2 · seal, verify, journal the seal invocation
    preflight.py    R1 · resource floors + the run token
    arms.py         R7 · arm registry; the LBM→fallback invariant
    shuffle.py      R3 · target-shuffle construction
    mutants.py      R4 · matched pocket/distal mutant construction
    cliffs.py       R5 · matched-molecular-pair cliff stratification
    abundance.py    R6 · atlas-vs-HPA per-protein ratio
    budget.py       R9 · Modal spend ledger + halt
    verdict.py      R8 · the three-valued verdict
    report.py       R7 + R8 · report generation
    replay.py       R10 · deterministic replay check
  configs/audit/
    prereg.yaml         HUMAN-sealed pre-registration
    arms.yaml           arm registry (identity only — no thresholds)
    hpa_reference.yaml  HUMAN-entered HPA values with citations
  tests/audit/
  tests/fixtures/audit/
```

### Interfaces

```python
# prereg.py — R2
def prereg_digest(prereg: dict) -> str:
    """sha256 over the canonically-serialized pre-registration."""

def seal_prereg(prereg_path: Path, journal_dir: Path) -> str:
    """HUMAN ONLY (Global Constraint (4)). Write prereg_sha256, journal an
    `invocation` record, return the digest.
    Raises if the pre-registration is incomplete (see the completeness rule).
    Re-sealing an already-sealed file is PERMITTED and JOURNALLED, never silent.
    Does NOT prove who ran it — see D2.1.
    """

def load_sealed_prereg(prereg_path: Path) -> dict:
    """Verify prereg_sha256 and return the pre-registration.
    REFUSES a file carrying no prereg_sha256 — absence is not consent.
    Raises on mismatch.
    """

def reseal_history(prereg_path: Path, journal_dir: Path) -> list[dict]:
    """Every seal invocation for this pre-registration, oldest first, each with
    the run records that already existed at that moment. A seal whose record
    postdates a run record for the same prereg is returned flagged
    `after_results=True`. Reports it; does not adjudicate it.
    """

# preflight.py — R1
def preflight(floors: dict, journal_dir: Path) -> str:
    """Check free RAM, free disk and remaining Modal credit against declared
    floors. On breach: raise PreflightError naming the floor AND its measured
    value, BEFORE any work is dispatched.
    On pass: return a run token recorded in the journal.
    """

# budget.py — R9
def authorize(batch_cost_usd: float, ledger: Ledger) -> None:
    """Raise BudgetHalt unless spent + batch_cost_usd <= ceiling.
    Charges the ESTIMATE at dispatch; reconciles against actual afterwards.
    """

# verdict.py — R8
class Verdict(str, Enum):
    SENSITIVE = "sensitive"
    INSENSITIVE = "insensitive"
    INCONCLUSIVE = "inconclusive"

def classify(statistic: float, ci: tuple[float, float], bands: Bands) -> Verdict:
    """TOTAL function: every input maps to exactly one Verdict.
    A result inside the pre-registered ambiguity band maps to INCONCLUSIVE.
    """
```

---

## Part III — Data & state

**Three arms, each with its named non-LBM fallback (G1/R7).** The fallback for the affinity arm is
the point of the study, not an afterthought: a **ligand-only baseline** that never sees the protein
*is* the null hypothesis made runnable. An affinity model that cannot beat it has no target
sensitivity to speak of.

| Arm | LBM | Named non-LBM fallback | Requirements |
|---|---|---|---|
| A · affinity / target sensitivity | Boltz-2 | ligand-only descriptor baseline (protein input withheld) | R3, R4 |
| B · cliff discrimination | ESM-2 embeddings | RDKit descriptor baseline | R5 |
| C · abundance | Atlas-derived abundances | HPA lung reference values | R6 |

**Invariants.**

- `prereg.yaml` is the **only** home for thresholds, bands, the candidate set and the inconclusive
  rule. `arms.yaml` carries identity and fallback pointers only. A threshold appearing outside the
  sealed file is a defect — tested for, because a threshold that lives in code is a threshold
  outside the seal.
- Run directories are immutable; outcome written last (S12).
- The ligand set is **identical across the arms of a comparison**. Enforced at report time.
- `hpa_reference.yaml` holds **biological numbers** → Global Constraint 1: human-entered with
  citations. The agent writes the schema and the validator that rejects an unsourced entry.
- Per defect 33, every CA done-condition is evaluable against `tests/fixtures/audit/`; the
  live-data checks are separate integration conditions, deferred and reported at the human boundary.

---

## Part IV — Failure handling

The adversarial pass. Each entry is a way this study reports a confident wrong answer.

**F1 · The shuffled target is a real target of that ligand.** Sampling a "shuffled" partner from a
seven-protein panel will sometimes draw a protein the ligand genuinely binds. Those pairs are true
positives inside the negative arm; they pull `Δ_shuffle` toward zero and bias the study toward
**"insensitive"** — the verdict that kills the moiety claim. A false negative here is expensive.
**Handling:** the shuffled partner is drawn only from panel targets with no measured and no
annotated interaction with that ligand. If the panel cannot supply one, the ligand is **dropped from
the shuffle arm and the drop is recorded in the report** — never silently retained, never silently
dropped.

**F2 · Pocket and distal mutants are not comparable.** Matching on mutation count alone is not
enough — pocket residues may be systematically more buried, so a pocket mutation is chemically more
disruptive regardless of any binding-site logic. **Handling:** matched on target, on mutation count,
and on comparable relative solvent accessibility, all drawn by one pre-registered procedure. An
unmatched pocket mutant raises rather than being reported against a mismatched control.

**F3 · R6 compares transcript to protein.** HPA lung values are commonly transcript-level (nTPM)
while an atlas abundance may be protein-level. An order-of-magnitude pass criterion across two
modalities can be satisfied by unit choice alone. **Handling:** each side of the ratio declares its
modality; a cross-modality comparison is permitted but **flagged in the report as cross-modality**,
and its limitation is carried into the verdict text. Ratios are evaluated **per protein**, never on
an average — averaging seven proteins hides exactly the case the study exists to find.

**F4 · Budget authorized from a lagging number.** Modal spend reports asynchronously; trusting a
stale remote figure authorizes a batch that overruns. **Handling:** the local ledger charges the
**estimate at dispatch** and reconciles afterwards. Authorization reads the local ledger only.

**F5 · A crashed run reads as a success.** Handled by S12: outcome written last, so absence of
`outcome.json` is unambiguous.

**F6 · Preflight skipped.** R1 requires preflight be *asserted* to have run. **Handling:** preflight
returns a run token recorded in the journal; the Modal dispatcher raises without a token for the
current `run_id`. An assertion that nobody can bypass by import order.

**F7 · An inconclusive result is rendered as a pass.** **Handling:** structural, not procedural —
the report object carries `verdict: Verdict` and **no boolean `passed` field exists anywhere on
it**. There is nothing to coerce. Tested by asserting the attribute's absence and that `Verdict` has
exactly three members.

**F8 · A weak positive reported as a pass.** The PVR calls this a failure of the study. Handled by
F7 plus the pre-registered ambiguity band and the bootstrap CI over ligands (D3).

---

## Part V — Per-requirement spec

Each carries the PVR test criterion, made precise enough for a sealed test author to write against
without seeing the implementation.

### R1 · Preflight gate
**Behavior.** `preflight()` checks free RAM, free disk and remaining Modal credit against floors
declared in `prereg.yaml`. Any breach raises `PreflightError` naming the breached floor **and its
measured value**, before dispatch. Passing returns a run token journalled against the `run_id`.
**Tests.** (1) each floor breached individually → non-zero exit, message names that floor and its
measured value; (2) no Modal call is reachable without a token for the current `run_id`.

### R2 · Pre-registration frozen before the first complex
**Behavior.** As D2. `load_sealed_prereg` refuses an unsealed file and raises on mismatch. Sealing is
human-reserved, journalled as an `invocation` record, and re-sealing is permitted but recorded.
`reseal_history` flags any seal whose record postdates a run record for the same pre-registration.
**Completeness rule.** `seal_prereg` raises unless the candidate set, every arm with its fallback,
every threshold, the ambiguity band and the inconclusive rule are all present — mirroring T7a's third
done-condition (*sealing an unratified panel raises*). A digest over an incomplete pre-registration
is a seal binding nothing.
**§R2.4 Claim narrowing.** The report reads the panel's `ratified` flag and emits the narrowed claim
string ("a generic Boltz-2 target-sensitivity audit") whenever the panel is unratified — which,
today, it is. The lung-barrier claim is unlocked by T8, mechanically, not by a human editing prose.
**Tests.** (1) edit a threshold without re-sealing → `load_sealed_prereg` raises; (2) a file with no
`prereg_sha256` raises — absence is not consent; (3) sealing an incomplete pre-registration raises;
(4) sealing is idempotent on unchanged content; (5) seal → run → re-seal produces a
`reseal_history` entry with `after_results=True`; (6) **no string in the package, its CLI help or
the report describes the seal as proving who sealed it** — a grep-level test, because this is the
failure mode with history.

### R3 · Boltz-2 target-shuffle arm
**Behavior.** Over one ligand set, compute native `f(l, t_true)`, shuffled `f(l, t_shuf)` and the
ligand-only fallback `g(l)`. Report `Δ_shuffle = A(native) − A(shuffled)` and
`Δ_fallback = A(native) − A(ligand-only)`, `A` = agreement with measured values, CI by bootstrap over
ligands. F1 governs shuffle construction.
**Tests.** a run producing only the native arm **fails**; the reported statistic is a difference; the
two arms score an identical ligand set; a ligand with no valid shuffle partner appears in the
report's drop list.

### R4 · Pocket-vs-distal mutation control
**Behavior.** Per target, matched pocket and distal mutants (F2). Report
`Δ_mut = effect(pocket) − effect(distal)`.
**Tests.** every pocket mutant has a matched distal mutant of equal mutation count on the same
target; a raw "prediction dropped" result with no distal comparator **fails**; an unmatched mutant
raises.

### R5 · ESM-2 vs descriptor baseline on cliff-stratified pairs
**Behavior.** Matched molecular pairs crossing a pre-registered potency or efflux cliff. Accuracy
reported **separately on the cliff stratum**.
**Tests.** a pooled-only report **fails**; the cliff threshold is read from the sealed
pre-registration, not from code.

### R6 · Atlas abundances vs HPA
**Behavior.** Per-protein ratio; pass evaluated per protein at one order of magnitude; modality
declared and cross-modality flagged (F3).
**Tests.** the criterion is evaluated per protein, never on an average; a cross-modality ratio is
flagged; an `hpa_reference.yaml` entry without a citation is rejected by the validator.

### R7 · Both arms always reported
**Behavior.** `arms.yaml` gives every LBM arm a `fallback:` pointer. The report generator raises if
any arm lacks its counterpart. An LBM that loses to its fallback is **recorded as a finding**, never
suppressed.
**Tests.** removing a `fallback:` makes report generation raise; a losing LBM appears in the report.

### R8 · "Inconclusive at this power" is a permitted verdict
**Behavior.** `Verdict` has exactly three members. `classify` is total. No boolean pass field (F7).
**Tests.** `len(Verdict) == 3`; a statistic inside the band maps to `INCONCLUSIVE`; the report object
has no `passed` attribute.

### R9 · Budget guard
**Behavior.** `authorize()` per F4; halts and reports remaining work.
**Tests.** ceiling below projected cost → halt, remaining work reported, ceiling never exceeded;
authorization never reads the remote figure.

### R10 · Deterministic replay
**Behavior.** Every reported number carries `(model version, seed, pair set, arm)`, sourced from the
S12 run record. Replay re-runs and compares.
**Tests.** replay from a recorded run reproduces the statistic; a missing seed **fails**; an unpinned
model version **fails**.

---

## Open questions

1. **Exact pre-registered thresholds for R3/R4** — δ bands and the cliff threshold. Carried from the
   PVR; must be fixed and sealed **before any run**. This design fixes the *mechanism* and the
   *shape*; the numbers are biological/statistical claims and are human-owned (Global Constraint 1).
2. **T8 completion** — decides lung-barrier vs generic. Not a blocker: §R2.4 makes the claim narrow
   itself, so the study runs today at the narrower claim.
3. **Chai-1 geometry arm** — in only if Modal credit remains. Would need its own named non-LBM
   fallback under R7 before admission.
4. **Rounds beyond pilot + confirmatory** — assumed two; budget caps it.
5. **AM-6** — open upstream, unrelated to this study.
