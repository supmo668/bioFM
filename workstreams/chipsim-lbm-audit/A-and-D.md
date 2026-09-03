# A&D — ChipSim LBM Audit: do the foundation models resolve moiety-level chemistry?

**Workstream:** `chipsim-lbm-audit` · **Module:** `lung-on-chipsim` · **Status:** draft (design **r1.2**) — **NOT approved**; A&D not ratified; five human artifacts absent
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
  **equivalence band**, re-run `prereg-seal`, and the new digest verifies perfectly. Nothing in the digest
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

#### D3a · Reporting unit and thresholds — principal's 1B1 rulings, 2026-09-01

r1.0 left the reporting unit implicit and (c) reads as a single pooled difference. **That is the
aggregate the parent PVR forbids** — *"aggregate metrics hide exactly the cases the project exists
to resolve"* — so a study whose only well-powered number were an aggregate would argue against its
own programme. Ruled:

**The statistic is per-target Δρ.** `Δρ = ρ(native, measured) − ρ(shuffled, measured)`, Spearman
(predicted affinities are on an uncalibrated scale; the claim is about *ranking* moieties, not
absolute Kd), computed **per target** and reported as seven numbers plus their paired distribution.
Never one pooled ρ. (c)'s bootstrap-over-ligands survives intact and composes with this: it is how
each **per-target** CI is built, resampling ligands within that target.

**Two shuffle tiers**, because "shuffled target" is ambiguous between two different tests:

| Tier | Swap to | Answers |
|---|---|---|
| **within-panel** | another of the seven | The decision-relevant question — ChipSim must discriminate *among these seven*. The harder test. F1 governs partner selection. |
| **cross-family** | a protein unrelated to the panel | The sanity floor. `insensitive` on **this** tier too means no target sensitivity at all — a stronger and more publishable negative. (Stated in the three-region language deliberately: *"Δρ ≈ 0"* is not a verdict this design can render.) |

Within-panel alone yields a null ambiguous between *"the model is insensitive"* and *"these seven
are too similar to separate."* The cross-family arm disambiguates it on the same ligand set for one
extra target. **Both tiers use the same thresholds** — cross-family is an *easier* test, not a
stricter one, so a failure there is stronger because the bar was equal; raising it would conflate
"stronger conclusion" with "harder test."

**Three-region verdict rule** — a **partition**. Evaluated per target, per tier, on the
95% bootstrap CI `[lo, hi]`. Every well-formed CI lands in exactly one region:

| Verdict | Rule on the CI | Boundary |
|---|---|---|
| **sensitive** | `lo >= +0.20` | **closed** at +0.20 |
| **insensitive** | `lo >= -0.10` **and** `hi <= +0.10` | **closed** at both bounds |
| **inconclusive** | neither of the above | — |

**Why this is a partition, stated so a test can check it.** `sensitive` and `insensitive` are
disjoint by arithmetic, not by convention: `sensitive` forces `hi >= lo >= +0.20 > +0.10`, which
violates `insensitive`'s upper bound, so no CI can satisfy both. `inconclusive` is defined as the
residual, so the three are jointly exhaustive. `classify` is therefore **total and single-valued**
(R8). A degenerate CI — non-finite, or `lo > hi` from a failed bootstrap — is **not** quietly
classified: `classify` raises, because a verdict computed from a broken interval is precisely the
confident-wrong-answer this design exists to prevent.

> **r1.1 correction — the `inconclusive` rule was not a partition and is withdrawn.** r1.1 read
> *"anything else, including any CI that merely contains zero"*. That trailing clause collided with
> `insensitive` on exactly the intervals `insensitive` exists to capture: `[0.00, +0.09]` sits
> entirely inside the equivalence band **and** contains zero, so it satisfied both rules while
> `classify` was required to be total. The clause also contradicted the equivalence-test rationale
> printed directly beneath it. **Containing zero is not what makes a result inconclusive —
> *escaping the equivalence band* is.**

> **Why `insensitive` needs an equivalence test, not a significance test.** A CI containing zero
> means *either* insensitive *or* underpowered, and those are as different as `no` and `unknown` in
> the P-gp label. Reporting "insensitive" from a wide interval straddling zero is **absence of
> evidence read as evidence of absence** — the standing rule in `CONTEXT.md`, and here it would kill
> the moiety claim on a null the study was never powered to produce. So `insensitive` is reachable
> only by a *narrow* interval: it requires precision, not the absence of a signal.
>
> **The corollary, spelled out because r1.1 got it backwards.** A narrow CI that *does* contain
> zero — `[-0.04, +0.06]` — **is** `insensitive`, and that is the whole point of an equivalence
> test: the large effect has been positively ruled out. What must never render as `insensitive` is
> a CI that **escapes the band**, however much of zero it contains.

**Declared power, not discovered.** With n = 7 targets a **one-sided** sign test across targets
bottoms out at p = 1/2⁷ ≈ **0.008** (two-sided it is 2/2⁷ ≈ **0.016**). The pre-registration
declares **one-sided**, and declares it *because the hypothesis is directional* — the claim is that
native beats shuffled, not merely that it differs from it. Sidedness is pre-registered rather than
chosen at analysis time, because choosing it afterwards is one of the cheapest ways to manufacture
a result. So a **unanimous** direction across all seven is publishable and a 5/7 split is not, at
any threshold. This study can detect a unanimous large effect and essentially nothing
subtler. That is what "powered for a large effect only" commits to, and it belongs in the
pre-registration rather than in the analysis.

**Pilot stops on low power.** If the measured-pair count assembled for ground truth is too small to
place a CI inside any of the three regions, the pilot **halts and reports power** rather than
proceeding to the confirmatory round. R3's ground truth needs measured affinities against the panel
(ChEMBL/BindingDB), which the PVR scopes in only *"beyond the minimum needed to assemble measured
pairs"* — so the surviving pair count, not the $30 ceiling, may be the binding constraint.

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
    """Check free RAM, free disk and the remaining LOCAL budget allowance
    (ceiling - spent, from the same ledger R9 authorizes against) versus the
    declared floors. On breach: raise PreflightError naming the floor AND its
    measured value, BEFORE any work is dispatched.
    Reads the local ledger ONLY - never the remote credit figure (F4/R9).
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

def classify(ci: tuple[float, float], bands: Bands) -> Verdict:
    """TOTAL and single-valued: every well-formed CI maps to exactly one Verdict
    by the D3a partition — SENSITIVE if lo >= sensitive_floor; INSENSITIVE if
    lo >= -eq and hi <= +eq; INCONCLUSIVE otherwise. Bounds are CLOSED.
    Thresholds come from the SEALED pre-registration via `bands`, never from code.
    RAISES on a degenerate CI (non-finite, or lo > hi): a verdict derived from a
    broken interval is worse than no verdict at all.
    NOTE: r1.1 took a `statistic` argument it never used, while the rule is a
    function of the interval alone. An unused discriminator in a total function
    is an invitation to start discriminating on it; it is removed.
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

**F2a · The distal arm can break the control silently (principal's 1B1, 2026-09-01).** "Distal" by
distance alone will sometimes select **buried structural residues**. Mutating those destabilises the
fold, which moves the predicted affinity for a reason unrelated to pocket sensitivity — inflating
the control arm, shrinking `Δ_mut`, and biasing the study toward **"insensitive."** Same direction
as F1's bias, and equally invisible in the output: it reads as a small difference, not as a broken
control. **Handling — four matching axes, all pre-registered:**

| Axis | Declared value | Why |
|---|---|---|
| same target | — | F2 |
| mutation count | equal | PVR; necessary, not sufficient |
| **surface exposure** | **relative SASA ≥ 25%** | distal residues must be exposed, so the fold is not perturbed |
| **substitution radicality** | comparable chemical severity | a conservative pocket swap against a radical distal one is not a control |

**Pocket definition:** residues with any heavy atom within **5 Å** of the co-folded ligand pose.
Distal residues are excluded from that shell and from any secondary-structure core. AFDB supplies
the wild-type geometry and mutants come from sequence, so no additional structure run is needed —
consistent with the PVR's exclusion of AlphaFold provisioning.

**Count:** **3 pocket + 3 matched distal per target** = 42 mutant complexes across seven targets,
which sits inside the ~1,200–1,500 complex budget alongside R3.

**Stability sanity check, declared in advance:** if distal mutants move predictions **as much as**
pocket mutants, that is *either* insensitivity *or* a broken comparator, and the pre-registration
fixes which it is — a large distal shift **invalidates the control** and is reported as such, rather
than being reported as a null. Declaring this before the run is the difference between a control and
a decoration.

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
F7 plus D3a's **equivalence band** and the bootstrap CI over ligands (D3): a weak positive fails the
`lo >= +0.20` floor and lands in `inconclusive`, never in `sensitive`. (r1.1 said *"ambiguity
band"*; no such band exists in this design — see R8.)

---

## Part V — Per-requirement spec

Each carries the PVR test criterion, made precise enough for a sealed test author to write against
without seeing the implementation.

### R1 · Preflight gate
**Behavior.** `preflight()` checks free RAM, free disk and the **remaining local budget
allowance** against floors declared in `prereg.yaml`.
**Consistency with F4/R9 — r1.1 contradicted them.** r1.1 had preflight check *"remaining Modal
credit"*, a **remote** figure, while F4 requires that *"authorization reads the local ledger only"*
and R9 tests that *"authorization never reads the remote figure."* Both gates are now specified on
the **same local ledger**: allowance = `ceiling − spent`. One source of truth for spend, checked
twice. A remote credit reading may be **journalled for reconciliation**, but it is never a gate
input — a lagging number that blocks a run is the same defect as a lagging number that authorizes
one. Any breach raises `PreflightError` naming the breached floor **and its
measured value**, before dispatch. Passing returns a run token journalled against the `run_id`.
**Tests.** (1) each floor breached individually → non-zero exit, message names that floor and its
measured value; (2) no Modal call is reachable without a token for the current `run_id`.

### R2 · Pre-registration frozen before the first complex
**Behavior.** As D2. `load_sealed_prereg` refuses an unsealed file and raises on mismatch. Sealing is
human-reserved, journalled as an `invocation` record, and re-sealing is permitted but recorded.
`reseal_history` flags any seal whose record postdates a run record for the same pre-registration.
**Completeness rule.** `seal_prereg` raises unless **all** of the following are present. The list
is enumerated rather than gestured at, because a seal binds exactly what it covers — and r1.1's
*"every threshold, the ambiguity band and the inconclusive rule"* named a band this design no longer
has (see R8) while omitting most of what D3a introduced:

1. the candidate set;
2. every arm with its **named non-LBM fallback** (R7);
3. **D3a's three-region thresholds in Spearman-ρ units** — the sensitive floor and the equivalence band;
4. **R4's separate thresholds in predicted-affinity units** — different statistic, different units, different numbers;
5. **both shuffle tiers** (within-panel, cross-family), declared as pre-registered;
6. the **per-target** reporting unit and the explicit no-pooling rule;
7. the **declared-power** statement *and its sidedness*;
8. the **pilot halt-on-low-power** rule;
9. **R5's cliff threshold** and **R6's per-protein criterion**.

Mirrors T7a's third done-condition (*sealing an unratified panel raises*). A digest over an
incomplete pre-registration is a seal binding nothing.
**§R2.4 Claim narrowing.** The report reads the `ratified` flag **of the committed fixture panel**
— per Part 0 the audit never reads the live panel — and emits the narrowed claim string ("a generic
Boltz-2 target-sensitivity audit") whenever that flag is false, which today it is.
**The unlock is not automatic, and r1.1 overstated it.** r1.1 said the lung-barrier claim *"is
unlocked by T8, mechanically."* It cannot be: the flag is read from a **fixture**, so T8 ratifying
the *live* panel changes nothing here on its own, and as written the claim could never widen at all.
Widening requires a **human to refresh the fixture from the ratified panel** — itself a Global
Constraint (4) act, which is the correct place for it. What *is* mechanical is the **narrowing**: no
one widens the claim by editing report prose, because the string is derived from the flag rather
than written by hand. **Narrowing is automatic; widening is human-gated.**
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
ligands. F1 governs shuffle construction. **Per D3a:** `A` is Spearman ρ, `Δρ` is reported **per
target** (seven values + their paired distribution, never pooled), across **two tiers** —
within-panel and cross-family — each bootstrapped over ligands *within* that target and mapped
through the three-region rule.
**Verdict mapping, both statistics.** `Δ_shuffle` **and** `Δ_fallback` are each mapped through the
D3a partition, per target. `Δ_shuffle` carries the two tiers; `Δ_fallback` has **no tier** (no
shuffle is involved) and is reported once per target. r1.1 defined `Δ_fallback` and then never said
how it was classified, leaving the arm that *is* the null hypothesis without a verdict.
**Tests.** a run producing only the native arm **fails**; the reported statistic is a difference; the
two arms score an identical ligand set; a ligand with no valid shuffle partner appears in the
report's drop list; **a report carrying only a pooled Δρ and no per-target values fails**; **a run
producing only one shuffle tier fails**; **a CI that *escapes the equivalence band* must not render as `insensitive`** — and, as its
necessary companion, **a narrow CI that contains zero but stays inside the band MUST render as
`insensitive`**. r1.1 carried only the first half, phrased as *"a CI containing zero must not
render as insensitive"*, which would have failed the correct behaviour; a sealed test author would
have written the contradiction straight into the suite.

### R4 · Pocket-vs-distal mutation control
**Behavior.** Per target, matched pocket and distal mutants (F2, **F2a**).

**The statistic, defined.** r1.1 wrote `Δ_mut = effect(pocket) − effect(distal)` and never defined
`effect` — the token appeared exactly once in the document, at its point of use, which made R4
untestable. It cannot borrow R3's `A`: `A` is *agreement with measured values*, and **mutants have
no measured values** — there is no ground truth for a hypothetical mutant to agree with. R4's
effect is therefore the model's own predicted displacement from wild-type:

    effect(M) = mean over ligands l in L of [ f(l, t_wt) − f(l, t_M) ]

where `f` is the Boltz-2 predicted affinity, `t_wt` the wild-type target, `M` a mutant set (the 3
pocket, or the 3 matched distal), and `L` a ligand set held **identical** across wild-type and every
mutant of that target. The reported control statistic is, **per target**:

    Δ_mut = effect(pocket) − effect(distal)

CI by bootstrap **over ligands** — D3's rule, for D3's reason: mutants of one target are not
independent draws. Seven values plus their paired distribution; **never pooled** (parent PVR).

**Units — R4 does NOT inherit D3a's numbers.** `Δ_mut` is in **predicted-affinity units**; D3a's
`+0.20` and `±0.10` are **Spearman-ρ** units. Carrying one set of thresholds across both statistics
is a unit error that would look entirely reasonable in a report. R4 therefore carries its **own**
sensitive floor and equivalence band, in affinity units, sealed alongside D3a's. The three-region
*shape*, the closed boundaries and the totality rule are inherited; **only the numbers differ, and
those numbers are human-owned** (Global Constraint 1 — see open question 1).

Pocket = within 5 Å of the co-folded ligand pose; distal = outside that shell, RSA ≥ 25%, matched on
count and substitution radicality; 3 pocket + 3 distal per target.
**Tests.** every pocket mutant has a matched distal mutant of equal mutation count on the same
target; a raw "prediction dropped" result with no distal comparator **fails**; an unmatched mutant
raises; **a distal mutant with RSA below the declared floor raises rather than being used as a
control**; **a distal arm moving as much as the pocket arm is reported as an invalidated comparator,
never as a null**.

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
**Behavior.** `Verdict` has exactly three members. `classify` is **total and single-valued** over
the D3a partition. No boolean pass field (F7).
**Tests.** `len(Verdict) == 3`; a CI **escaping** the equivalence band without reaching the sensitive
floor maps to `INCONCLUSIVE`; a CI **inside** the equivalence band maps to `INSENSITIVE` *even when
it contains zero*; the boundary cases are pinned (`lo = +0.20` → `SENSITIVE`, `hi = +0.10` with
`lo = −0.10` → `INSENSITIVE`) so the closed bounds cannot drift; `sensitive` and `insensitive` are
shown **disjoint** by property test over random CIs; a degenerate CI (non-finite, or `lo > hi`)
**raises** rather than classifying; the report object has no `passed` attribute.

> r1.1 said *"a statistic inside the band maps to `INCONCLUSIVE`"*. That named the **equivalence**
> band, where D3a maps to `INSENSITIVE` — the two rules pointed the same input at two different
> verdicts. The term *"ambiguity band"* is retired from this design: there is one **equivalence
> band**, and `inconclusive` is the residual, never a band of its own.

### R9 · Budget guard
**Behavior.** `authorize()` per F4; halts and reports remaining work.
**Tests.** ceiling below projected cost → halt, remaining work reported, ceiling never exceeded;
authorization never reads the remote figure.

### R10 · Deterministic replay
**Behavior.** Every reported number carries `(model version, seed, pair set, arm, target, tier)`,
sourced from the S12 run record. `tier` is `null` for statistics that have none (`Δ_fallback`, R4's
`Δ_mut`). **r1.1's four-tuple could not identify a D3a number:** after D3a every statistic is
per-target and, for `Δ_shuffle`, per-tier, so seven targets × two tiers collapsed onto a single key
and replay could not tell which of fourteen numbers it had just reproduced. Replay re-runs and
compares.
**Tests.** replay from a recorded run reproduces the statistic; a missing seed **fails**; an unpinned
model version **fails**; **a run record whose key does not resolve a reported number to a unique
`(target, tier)` fails**.

---

## Open questions

r1.2 closed every **internal** contradiction it could close alone. What remains is what an agent
must not decide: biological and statistical claims (Global Constraint 1), and scope calls that cost
money. These are the standing 1B1 agenda with the principal.

### Blocking the seal — human-owned numbers

1. **R1 · preflight floors.** The *mechanism* is now fixed and consistent with R9 (local ledger,
   never the remote figure). The **floor values** — free RAM, free disk, minimum remaining
   allowance — are not set. A floor is a claim about what this study needs to run honestly.
2. **R3/R4 · the pre-registered thresholds.** D3a fixes the *shape* (closed bounds, a partition) and
   the ρ-unit numbers are provisional at `+0.20` / `±0.10`. **R4 now needs its own pair in
   predicted-affinity units** — new in r1.2, and there is no defensible way for me to invent them.
3. **R5 · what counts as a cliff.** "A pre-registered potency or efflux cliff" names no magnitude.
   Until it does, the cliff stratum is undefined and R5 is untestable — the same defect r1.2 just
   fixed in R4.
4. **R6 · modality handling.** F3 permits a cross-modality comparison if flagged. The open question
   is whether nTPM-vs-protein should be **permitted-and-flagged** or **refused**: an
   order-of-magnitude criterion can be satisfied by unit choice alone, so "flagged" may be too weak.
5. **R9/R10 · the ceiling and the replay bar.** R9's dollar ceiling is unset. R10 now demands a
   six-part key; whether replay must reproduce **bit-identically** or **within a declared
   tolerance** is unresolved, and Boltz-2 on GPU is not obviously bit-reproducible across runs.

### Scope

6. **Chai-1 geometry arm — admission conditions.** In only if Modal credit remains. **Chai-1 is
   geometry only and never scores.** It produces no affinity, enters no arm under R7, and
   contributes to no verdict; it would exist to check whether the co-folded pose R4's 5 Å pocket
   definition depends on is stable. Stated here so the line is held at specification time rather
   than argued at analysis time: **if Chai-1 output ever reaches a statistic, that is a defect.**
7. **T8 completion** — decides lung-barrier vs generic. Not a blocker: §R2.4 narrows the claim
   automatically, so the study runs today at the narrower claim. Note r1.2's correction — widening
   is **human-gated**, not mechanical.
8. **Rounds beyond pilot + confirmatory** — assumed two; budget caps it.
9. **AM-6** — open upstream, unrelated to this study.

---

## r1.2 changelog — internal contradictions closed

Recorded explicitly because this document is intended for an **OpenTimestamps** seal, and a
timestamp over a self-contradicting document notarises the contradiction. Fourteen sites, all
found in the r1.1 self-review:

| # | Where | Defect | Resolution |
|---|---|---|---|
| C1 | D3a | `insensitive` and `inconclusive` **overlapped** — `[0.00, +0.09]` satisfied both while `classify` must be total | `inconclusive` is now the pure residual; bounds declared **closed**; disjointness shown by arithmetic |
| C2 | D3a | equivalence rationale contradicted the rule printed above it | corollary stated: a *narrow* CI containing zero **is** `insensitive` |
| C3 | R8 | *"inside the band → INCONCLUSIVE"* pointed the same input at a second verdict | term *"ambiguity band"* **retired**; one equivalence band, residual `inconclusive` |
| C4 | `classify` | took an unused `statistic` arg; could not express the CI-only rule; no degenerate case | signature reduced to `(ci, bands)`; raises on a broken interval |
| C5 | R4 | **`effect` was never defined** — one occurrence, at its point of use | defined as mean predicted displacement from wild-type; **own thresholds, own units** |
| C6 | §R2.4 | claim unlock was called *"mechanical"* but read a fixture flag — could **never** widen | narrowing automatic, **widening human-gated** |
| C7 | R1 | preflight read *remaining Modal credit* — the **remote** figure F4/R9 forbid | both gates on the **local ledger** |
| C8 | R10 | four-part key could not identify a per-target, per-tier number | key extended to `(…, target, tier)` |
| C9 | R2 | completeness list bound a band that no longer exists and omitted most of D3a | nine items enumerated |
| C10 | R3 | `Δ_fallback` defined but never classified — the null-hypothesis arm had no verdict | mapped through the partition, tier `null` |
| C11 | F8 | dead term *"ambiguity band"* | rewritten onto the equivalence band |
| C12 | D3a | cross-family tier described as *"Δρ ≈ 0"* — not a renderable verdict | restated as `insensitive` on that tier |
| C13 | D3a | sign-test **sidedness unstated** (0.008 one-sided vs 0.016 two-sided) | **one-sided**, pre-registered, with its directional justification |
| C14 | D2 | still used the retired term *"ambiguity band"* in live prose, one section above where R8 retires it | rewritten onto the equivalence band |

**Not sealed, and why.** The OpenTimestamps proof is deliberately **not** taken at r1.2. A
timestamp fixes *content* at a *time*; it does not make that content correct, and every open
question above is a number the pre-registration must carry **before** the seal has anything worth
binding. Sealing now would notarise a document whose R4 thresholds do not exist. The seal comes
after the 1B1, not before it — which is also the ordering R2 requires of the pre-registration
itself.
