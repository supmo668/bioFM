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
| **cross-family** (**20 ligands**, r1.4) | a protein unrelated to the panel | The sanity floor. A null on **this** tier too means no target sensitivity at all — a stronger and more publishable negative. **Read via the sign test over targets, NOT via an `insensitive` render — see r1.6 below.** |

> **r1.6 · the cross-family tier's designed outcome was UNREACHABLE, and r1.5's vacuity
> sweep missed it.** This row previously read *"`insensitive` on this tier too"* — the
> C12 restatement, adopted precisely because *"Δρ ≈ 0"* is not a renderable verdict. But
> P0 measured `P(insensitive) = 0.000` at every feasible n, and this tier runs on **20**
> ligands, so its CI is **wider** than the one that already cannot fit the band. The
> study's negative control was specified to confirm itself through a verdict it can never
> render — the sanity floor could not report that the sanity check passed.
>
> **Why the r1.5 sweep did not catch it.** That sweep asked which **test assertions** had
> an `insensitive` render as their subject, and correctly found two. This is not an
> assertion; it is a **design expectation** — the stated reason the tier exists. Scoping a
> vacuity sweep to the test suite misses every unreachable expectation living in the
> rationale, and the rationale is what the tests get written from. **The sweep is
> re-scoped: any claim of the form "X confirms the design" is checked against whether X is
> reachable, wherever it appears — table cell, prose, or assertion.**
>
> **The fix is the same shape as the halt rule's.** The tier's conclusion is carried by the
> **one-sided sign test over targets on point estimates**, which needs no CI to fit the
> band and is exactly why that statistic survived the width that killed `insensitive`. A
> cross-family tier failing to clear the sensitive floor across seven targets is the
> negative this arm was built to deliver; it was only ever the *equivalence framing* of it
> that was unreachable.

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

> ### Principal's ruling, 2026-09-08 (1B1): the study is TWO-REGION in practice, declared in advance
>
> P0 measured `P(insensitive) = 0.000` in all 36 cells, at every n up to 160 (median half-width
> 0.36–0.42 at n=40 against a `±0.10` band; 0.17–0.21 even at n=160). **`insensitive` is not
> renderable at any ligand count this study can reach.**
>
> **The band is NOT widened.** Widening it after seeing P0 would be setting a threshold from data —
> precisely what the sealed-formula discipline exists to prevent — and a band near the measured
> half-width would make `insensitive` mean *"Δρ is somewhere within ±0.35"*, which is not evidence of
> target-insensitivity in any useful sense. The three regions, the closed bounds and `classify`'s
> totality all stand exactly as specified: if a CI ever did fit the band, it would be rendered
> correctly. `Verdict` keeps three members and R8's `len(Verdict) == 3` is unchanged.
>
> **What changes is what the pre-registration promises.** It declares, before the run, that this
> study reports **`sensitive` or `inconclusive`**, and that `insensitive` is unreachable at its
> power. Consistent with the PVR, which already accepts *"a defensible 'inconclusive at this
> power'"* as success — the publishable negative is that, not a demonstrated insensitivity.
>
> **R5's limit goes on the card beside this one (ADR-0004).** Both arms of this study say the same
> thing about what it cannot detect, and separating them lets a reader assume one covers the other:
>
> - **R3 / the sign test** can demonstrate moiety-sensitivity but **never its absence**.
> - **R5 / the cliff test detects only a LARGE effect.** At a 15-point accuracy gain it sits at
>   **0.46 with 60 pairs**, and **no feasible pair count rescues it**.
> - **R5 additionally carries a limit that more data cannot fix:** fewer than **five discordant**
>   pairs can never reach `α = 0.05`. That is structural, not statistical — a reader told
>   "underpowered" will assume a bigger roster fixes it, and here it does not.
>
> **The card must not report a null from either arm without the matching limit beside it.**

> **The card sentence, binding and not to be softened (principal, via CTO, 2026-09-08).** The model
> card must state that the study **can demonstrate moiety-sensitivity but can never demonstrate its
> absence**, and that **`inconclusive` is not weak evidence of insensitivity.** Plainly, in those
> terms — *not* softened to "limited power to detect insensitivity", which a reader discounts as
> routine hedging.
>
> Without it, a reader converts every `inconclusive` into "probably insensitive": **absence of
> evidence read as evidence of absence.** That is this programme's standing invariant — it is why
> ABCB1 survived T8, why `unknown` is a distinct P-gp label rather than folded into `no`, and why
> this design required an equivalence test rather than a significance test in the first place. Here
> it applies to the study's **own output** rather than to its inputs.
>
> **`insensitive` is NOT deleted from D3a.** The sealed three-region definition stands exactly as
> written and the unreachability is recorded beside it as a **measured empirical fact**. Deleting
> the region would erase the finding and re-open the partition r1.2 spent fourteen corrections
> making exhaustive and disjoint; a future study at higher n, or on a lower-variance statistic,
> inherits a specification that is already precise. **The seal is unaffected because the rule did
> not change** — only what is now known about its reachability.
>
> **Why the alternatives were rejected, on their own terms:** widening collides with the `sensitive`
> floor at `+0.20` and is threshold-choosing-from-data; `n ≈ 500` is infeasible against a 20–40
> compound target with A10 naming pair assembly as the binding constraint; re-specifying the
> statistic risks selecting one for the verdict it yields.
>
> **The reading that must not be allowed, and why the card carries it.** In a three-region study
> `inconclusive` means *"the data did not separate sensitive from insensitive."* Here it means
> *"the data did not reach the sensitive floor, and insensitive was never available."* Those are
> different claims, and the second is weaker. A reader who assumes the first will read every
> `inconclusive` as evidence against target sensitivity when it is evidence of nothing at all in
> that direction. **The model card states the unreachability next to every `inconclusive` it
> renders**, not once in a limitations section — the same rule as `NOT_COMPARABLE` in R6 and
> `**Seal: MALFORMED**` in the panel block: an absent result must be visible where the result would
> have been.
>
> **Tests.** (1) a report containing any `inconclusive` verdict and no unreachability statement
> **fails**; (2) `len(Verdict) == 3` still holds and `classify` is still total — the region is
> unreachable in practice, not deleted; (3) the pre-registration's declared verdict set is
> `{sensitive, inconclusive}` and a run that renders `insensitive` without the seal having been
> re-issued **raises**, because that would mean the power assumption changed without anyone saying
> so.

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
    abundance.py    R6 · atlas-vs-HPA per-protein ratio; AbundanceOutcome (3 members,
                    distinct from verdict.py's Verdict — see R6)
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
| **substitution radicality** | **same Grantham band** — conservative `<60`, moderate `60–100`, radical `>100` | a conservative pocket swap against a radical distal one is not a control |

**G1 · the radicality metric — principal's ruling, 2026-09-06 (1B1).** r1.1 and r1.2 both said
*"comparable chemical severity"* and named no scale, so this axis could not be tested: R4's control
test asserts mutants are *"matched on count and substitution radicality"*, and "comparable" is not
measurable. **Grantham distance, banded** — conservative `<60`, moderate `60–100`, radical `>100`;
a matched pair must fall in the **same band**. Grantham composites composition, polarity and volume
into one citable number, which is what makes "comparable" checkable rather than arguable.

**Its limit, stated because the axis exists to protect against a specific failure.** Grantham is a
1974 scale derived from observed sequence conservation, **not** from structural destabilisation —
so it does not by itself answer F2a's actual worry, which is a buried distal residue whose mutation
perturbs the fold. **The `RSA ≥ 25%` axis is what carries that**, and the two axes are load-bearing
in different directions: RSA keeps the distal mutant *exposed*, Grantham keeps it *chemically
comparable*. Either alone leaves F2a's failure mode open, which is why both are declared and both
are matched. A predicted-ΔΔG metric would target destabilisation directly and was rejected here on
a separate ground — it would control this audit with a predictor as unvalidated, for these targets,
as the model under audit.

**Matching may fail, and that is a refusal, not a relaxation.** With 3 + 3 per target across seven
targets, banding on Grantham *and* RSA can leave a pocket mutant with no legal distal partner. F2a
already rules this: *"an unmatched pocket mutant raises rather than being reported against a
mismatched control."* Widening a band to find a partner is the one repair that must not happen
silently, because it converts the control into the thing it was written to exclude — so band edges
come from the **sealed** `prereg.yaml` and a run that cannot match **raises**.

**Tests.** (1) a pair spanning two Grantham bands is refused; (2) a pocket mutant with no
band-and-RSA-matched distal partner **raises** rather than pairing with the nearest available; (3)
band edges are read from the sealed pre-registration, and a `prereg.yaml` without them raises;
(4) the boundary values `60` and `100` are pinned — the bands are **closed at the lower edge**, the
same convention D3a declares, so a distance of exactly `60` is moderate and never both.

**Pocket definition:** residues with any heavy atom within **5 Å** of the co-folded ligand pose.
Distal residues are excluded from that shell and from any secondary-structure core. AFDB supplies
the wild-type geometry and mutants come from sequence, so no additional structure run is needed —
consistent with the PVR's exclusion of AlphaFold provisioning.

**Count (r1.4):** **2 pocket + 2 matched distal per target**, against a ligand set of
**|L| = 15**, = **7 × 4 × 15 = 420 complexes**.

> **r1.2's count was wrong and its budget sentence concealed it.** It read *"3 pocket + 3 matched
> distal per target = 42 mutant complexes … sits inside the ~1,200–1,500 complex budget"*. But
> `effect(M)` is a mean **over ligands**, so every mutant runs against every ligand in `L`: R4 costs
> `7 × mutants × |L|`, and **42 = 7 × 6 counts variants, not complexes**. At `|L| = 40` R4 alone is
> 1,680 complexes and the study needed ~2,520 — about **$54 against a $30 ceiling**. At `|L| = 1`,
> which "42 complexes" literally implies, the bootstrap over ligands is impossible. The arm was over
> budget and under-specified at once. See the pilot specification for the full ledger.

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

**Allowance floor — principal's ruling, 2026-09-06 (1B1): one full batch's estimate**, computed by
the G2 estimator at the slow throughput bound, for the **largest batch this run will dispatch**. It
is **derived, not picked**: the rule is *never start work you cannot finish*, which is what a
preflight is for, and there is no magic number to defend. It also moves correctly on its own when
batch size or rate changes — a fixed reserve silently becomes wrong the first time either does.

Deliberately **one** batch, not two: a two-batch floor reserves retry headroom, but on a $30 ceiling
a large batch could fence off a third of the envelope and halt a study that would have completed.
The failure this floor prevents is a run that dies mid-batch having already spent the money; a
failed batch that cannot be retried is a worse outcome than one that was never started, but it is a
*recoverable* one, and the ceiling is the harder constraint here.

**RAM and disk floors are pilot-measured** (see the sourcing ruling), not guessed — the same rule as
R4 and R5, for the same reason.
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

> **Both assertions are UNIT tests over SYNTHETIC CIs, and that is now binding (r1.5).** P0 measured
> `P(insensitive) = 0.000` at every feasible n, so written against study output — or against
> simulated study output — **these two assertions become vacuously true**. They would pass against
> any implementation, including one that never renders `insensitive` at all, because the branch they
> guard is never taken. That is the same defect as the invocation-collision test that passed on an
> untouched fixture, sitting on the exact rule the whole equivalence argument rests on.
>
> So they are specified against **hand-constructed intervals** — `classify` is a pure total function
> and must be tested over its **domain**, not over the subset this study happens to reach. A
> `[-0.02, +0.06]` renders `INSENSITIVE` whether or not any run will ever produce one.
>
> Each carries an **anti-vacuity assertion**: the test fails if the branch it names was not
> exercised. A test that cannot fail is not protecting the property it names.
>
> **Swept for siblings.** R8's assertions — the pinned boundary cases (`lo = +0.20` → `SENSITIVE`;
> `hi = +0.10, lo = −0.10` → `INSENSITIVE`), disjointness by property test over random CIs,
> `len(Verdict) == 3` — are **already** synthetic-input unit tests on `classify` and are **not**
> affected. The two above were the only **assertions** in the document whose subject was an
> `insensitive` render reachable only through study data.
>
> > **r1.6 — this sweep was INCOMPLETE, and its own wording is why.** It scoped itself to
> > *assertions*, then reported closure as though it had swept the document. It had not: the
> > **cross-family tier's designed outcome** (D3, tier table) was specified as an `insensitive`
> > render and is equally unreachable — the study's negative control could not report that it
> > passed. A design expectation is not an assertion, so a suite-scoped sweep cannot see it,
> > yet it is what the assertions get written *from*. **Re-scoped: any claim that some result
> > confirms the design is checked for reachability wherever it lives — table cell, prose, or
> > test.** The sentence *"recorded so the next reader does not re-derive the sweep"* was the
> > active harm — it invited exactly the trust that let the gap survive a full review cycle. A
> > completeness claim is only as wide as its stated scope, and this one did not state it.

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
*shape*, the closed boundaries and the totality rule are inherited; **only the numbers differ.**

**The numbers come from a formula sealed BEFORE the pilot runs** (r1.4) — `equivalence = ±1 SD of
effect(distal)`, `sensitive floor = +2 SD`, the distal arm being the empirical null. Sealing the
*rule* rather than the *number* is what makes "measure then seal" rigorous instead of "look, then
choose". Cross-checked against Boltz-2's published pairwise error (PMAE 0.85–1.20 log₁₀ units). See
the pilot specification.

Pocket = within 5 Å of the co-folded ligand pose; distal = outside that shell, RSA ≥ 25%, matched on
count and substitution radicality; 3 pocket + 3 distal per target.
**Tests.** every pocket mutant has a matched distal mutant of equal mutation count on the same
target; a raw "prediction dropped" result with no distal comparator **fails**; an unmatched mutant
raises; **a distal mutant with RSA below the declared floor raises rather than being used as a
control**; **a distal arm moving as much as the pocket arm is reported as an invalidated comparator,
never as a null**.

### R5 · ESM-2 vs descriptor baseline on cliff-stratified pairs

**Cliff, defined (r1.4) — from the literature, not the pilot.** A **matched molecular pair**
(single-site, size-restricted transformation) with a **≥100-fold (2 log) measured potency
difference**. The ≥100-fold criterion is the field's long-standing standard and MMP-restricted
similarity is its preferred modern form, superseding a raw Tanimoto cutoff, which admits pairs
differing at several sites.

**Why R5 is not on the pilot list and R4 is.** R4's threshold is in **model-internal units** with no
external convention, so it must be measured. R5's is in **experimental potency units**, where a
settled standard exists — measuring our own would spend pilot budget re-deriving an agreed number,
and a bespoke threshold is *harder* to defend than the standard one. Computed locally with
RDKit/mmpdb at no Modal cost.

**The pair stratum is CURATED toward ~50 pairs, not discovered** — principal's ruling, ADR-0004.

r1.4 described the pairs as whatever *falls out of* a ~40-compound roster. ADR-0003 had already
created a deliberately curated *pair stratum*. The two documents assumed opposite things about the
same object, and the R5 power curve made the difference decisive.

**Why discovery was rejected, and it is the reasoning worth keeping.** The diversity stratum is
selected *for structural distinctness*; an MMP is a *near-duplicate by construction*. The two
selection criteria are in direct opposition, so harvesting pairs from the diversity roster is close
to the **worst available source**. R5 would then report low power **by construction rather than by
discovery** — a different and less honest claim than the sentence below is making.

**Target: ~50 pairs**, giving **0.87** power at a 25-point LBM gain over the descriptor baseline —
the same 0.80 floor the sign test clears (`verification/r5-pair-count-curve.py`, seed 4242,
2000 trials).

**Pre-registered fallback, promoted from an expectation to a commitment:** if fewer pairs are
assembled, R5 **reports the achieved count and its power**, and **it does not loosen the criterion
to fill the stratum**. The ≥100-fold cliff is fixed.

> **A STRUCTURAL LIMIT THAT MORE DATA CANNOT FIX, and it must be stated wherever R5's power is
> reported.** McNemar consumes only **discordant** pairs, and **fewer than five discordant pairs can
> never reach `α = 0.05`** — 4–0 gives `1/2⁴ = 0.0625`. That is an impossibility, not low power.
> Median discordance runs at roughly half the pair count, so at 10 pairs the median sits *exactly*
> on the floor. A reader told "underpowered" will assume more data fixes it; this does not fix.

**R5 detects only a LARGE effect.** At a 15-point gain (0.70 vs 0.55) power is **0.46 even at 60
pairs**, and no feasible count rescues it — 0.65-vs-0.55 reaches only 0.24 at 60. This is the same
limit the sign test carries and it belongs beside it on the model card.

**Every figure is an upper bound *and* a lower bound from different directions, which do not
cancel.** The curve is computed with the arms erring **independently**, which is conservative:
shared pair difficulty *raises* power (measured 0.70 → 0.98 at 40 pairs) by stripping the symmetric
noise out of the discordant split. A2 pushes the other way — predicted affinities treated as
noise-free flatter the LBM arm. **Two errors in opposite directions widen the interval; they do not
net.**

**Between-pair clustering barely moves R5**, unlike A7's 0.95 → 0.46 for the sign test: the largest
measured delta across `icc` 0.0–0.8 is **0.033**. The mechanism is why, and it generalises —
**McNemar consumes the *split* of the discordant pairs, and clustering perturbs their *count*
without biasing the split.** Within-pair similarity is the **signal**, never a discount: the unit is
the pair, so twenty pairs are twenty units and not forty correlated compounds.
**Behavior.** Matched molecular pairs crossing a pre-registered potency or efflux cliff. Accuracy
reported **separately on the cliff stratum**.
**Tests.** a pooled-only report **fails**; the cliff threshold is read from the sealed
pre-registration, not from code.

### R6 · Atlas abundances vs HPA
**Behavior.** Per-protein ratio; pass evaluated per protein at one order of magnitude; modality
declared. **A cross-modality pair (nTPM transcript vs HPA protein) renders `NOT_COMPARABLE` and
scores nothing** — it is neither a pass nor a fail and contributes to no verdict.

**Principal's ruling, 2026-09-06 (1B1): refuse, not flag** — **on the CTO's argument.** The
*decision* is the principal's: r1.2 left this open between permitted-and-flagged and refused, and he
chose refused in the 1B1. The *argument* that persuaded him is the CTO's, raised when it routed the
question — *"an order-of-magnitude criterion can be satisfied by unit choice alone, so 'flagged' may
be too weak."* I carried it into the options without saying whose it was.

> **Why the distinction is recorded rather than smoothed over.** A ruling attributed to the
> principal cannot be argued with; a CTO argument or an agent's inference can. Collapsing the two
> makes a judgement unfalsifiable by relabelling it — the same defect as a plan-approval marker that
> cannot distinguish a re-sign from an approval. The CTO caught this and it was right to.

Refused, for the reason that decided R4's units one section earlier: **an order-of-magnitude criterion between transcript and protein can be satisfied or
broken by normalisation choice alone, so it is not a criterion.** Transcript and protein abundance
are different quantities — their correlation is weak enough in general that "agrees within 10×"
carries little evidential weight either way — and a flag on a rendered *pass* is read as a caveat on
a result rather than as the absence of one.

This costs coverage, and the cost is the point: fewer proteins receive a verdict, and the report
says so in the verdict column instead of showing a green a unit change could have manufactured.
`NOT_COMPARABLE` is a rendered outcome, not a silent omission — F7's rule (an absent result must
never read as a pass) applies here exactly as it does to `inconclusive`.

**`NOT_COMPARABLE` is NOT a fourth `Verdict` member.** R8 requires `len(Verdict) == 3` and that
stands unchanged: `Verdict` is the D3a partition over CIs in `verdict.py`, and R6 is a separate
check in `abundance.py` over abundance ratios. Written out because "renders `NOT_COMPARABLE`" reads
naturally as a new `Verdict` case, and a sealed test author who added it there would break R8's
totality test while apparently implementing this section.

R6 therefore gets its **own** three-member outcome type — `AbundanceOutcome` = `{PASS, FAIL,
NOT_COMPARABLE}` — rather than a boolean plus a flag. Same reasoning as F7: a two-valued result has
nowhere to put "no comparison was possible" except into one of the two answers, and it lands in
whichever one the caller defaults to.

**Tests.** the criterion is evaluated per protein, never on an average; **a cross-modality pair
renders `NOT_COMPARABLE` and appears in no pass/fail tally**; **a cross-modality pair that renders
as a pass fails**; an `hpa_reference.yaml` entry without a citation is rejected by the validator.

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

### Provenance convention for every ruling below

Three labels, kept distinct because collapsing them is how a judgement becomes unfalsifiable:

- **Principal's ruling** — he chose it, in a 1B1, from options put to him. Only he can revise it.
- **From the PVR / from the literature** — it was already settled upstream and merely *found*. R9's
  ceiling and R5's cliff are these; neither needed a decision, and r1.2 wrongly routed R9's as one.
- **Mine** — an engineering call I made and am accountable for. G2's cost estimator is the example.

Where an argument came from someone other than the decider, the argument is credited separately —
see R6.

### Blocking the seal — human-owned numbers

1. ~~**R1 · preflight floors.**~~ **DECIDED 2026-09-06.** The allowance floor is **one full
   batch's estimate** at the slow throughput bound — derived, not picked. RAM and disk floors are
   **pilot-measured**. See R1.
2. ~~**R3/R4 · the pre-registered thresholds.**~~ **RESOLVED 2026-09-07.** ρ-units settled a
   priori; R4's band comes from a **formula sealed before the pilot** (`±1 SD` / `+2 SD` of the
   distal null). The number is measured; the rule is pre-registered.
3. ~~**R5 · what counts as a cliff.**~~ **Principal's ruling, 2026-09-07 — MMP + ≥100-fold**,
   chosen from options I derived from the literature. The *threshold* was found upstream, not
   invented; the *choice* to adopt it over a Tanimoto form was his. Off the pilot list; sealable
   today.
4. ~~**R6 · modality handling.**~~ **DECIDED 2026-09-06 — refused.** A cross-modality pair renders
   `NOT_COMPARABLE` and scores nothing. See R6.
5. ~~**R9/R10 · the ceiling and the replay bar.**~~ **BOTH CLOSED.**
   - **R9's ceiling was never open.** The parent **PVR G4** fixes it: *"≤ $30 Modal spend; local
     arms on the M5 Max; no overrun."* r1.2 listed it as a human-owned decision, which was an
     error of the kind `/design` exists to prevent — an A&D restates the PVR's *what*, it does not
     re-decide it. Routing a settled requirement back to the principal invites re-opening a
     commitment the PVR already made, and the wrong answer would have been binding.
   - **R10 · DECIDED 2026-09-06 — a declared tolerance, sealed**, not bit-identical. Boltz-2 on GPU
     is not reliably bit-reproducible (kernel selection, atomics, TF32), so a bit-identical bar
     would fail honest replays — and the realistic consequence is not a caught defect but a bar
     quietly relaxed at analysis time, when relaxing it is indistinguishable from excusing a real
     mismatch. A sealed tolerance is falsifiable; an unmeetable one gets negotiated away.
     **The tolerance VALUE needs run-to-run variance to set honestly, so it joins the pilot list**
     rather than being invented — same ruling as R4 and R5.
6. ~~**G1 · "substitution radicality" has no metric.**~~ **DECIDED 2026-09-06 — Grantham
   distance, banded** (`<60` / `60–100` / `>100`, matched pair shares a band, edges closed at the
   lower bound and sealed). See F2a.
7. ~~**G2 · the cost estimate `batch_cost_usd` has no estimator.**~~ **CLOSED — specified below,
   from the PVR rather than invented.**

> **This list is the complete blocking set.** Items 6 and 7 come from the r1.3 sweep and are stated
> here rather than only in their own section, because a reader who trusts a list headed *"blocking
> the seal"* will not go looking for two more blockers three sections further down. A list that
> looks exhaustive and is not is the same defect as a test whose docstring overstates it.

### Threshold sourcing — principal's ruling, 2026-09-06 (1B1)

**Pilot first, then seal.** R4's affinity-unit band and R5's cliff magnitude describe a scale nobody
has measured on this system: no pilot has run, and no measured effect-size or resource figure exists
anywhere in the repository. A pre-registered threshold chosen without knowing the statistic's spread
is a guess in the costume of rigor, and it is the number a skeptic attacks first when the study
returns a null — precisely the attack the OpenTimestamps proof exists to survive. So the numbers are
measured, then sealed.

**The condition that makes this legitimate, and it is not optional.** A threshold set from data you
have *seen* is not pre-registered. The pilot therefore runs on a **held-out target set that never
enters the confirmatory analysis**, and **the split itself is sealed with the thresholds** — the
allocation is part of the pre-registration, not a decision taken afterwards. Without that, "pilot
first" is indistinguishable from tuning the band until the result clears it, and the seal would
notarise the tuning.

R1's RAM and disk floors are measured in the same pass (G3's power rule folds in here too). R1's
**allowance floor** and R9's **ceiling** are value judgments, not measurements, and remain open.

### Scope

8. ~~**Chai-1 geometry arm.**~~ **DECIDED 2026-09-06 — EXCLUDED from this study.** Recorded as
   future work.

   Three reasons, and the third is the one that settled it. It scores nothing, so it buys no
   verdict. **R7 requires every LBM arm to name a non-LBM fallback and Chai-1 has none** — admitting
   it would have needed R7's first exemption, and an exemption is the crack through which a later
   arm argues that it too is "not really scoring". And it spends from a $30 ceiling where the PVR
   already warns the binding constraint may be the measured-pair count rather than the money.

   Excluding it is also the cheapest way to hold the line that a geometry arm never reaches a
   statistic: by not having one. The line itself stands for any future admission — **if Chai-1
   output ever reaches a statistic, that is a defect.**

   **This adopts the PVR's default; it does not narrow it.** Checked before deciding, after R9's
   ceiling turned out to have been settled upstream all along: the parent PVR lists *"Chai-1
   geometry as a fourth arm"* under **Out of scope**, readmitted only *"unless Modal credit remains
   after the three admission arms."* Out-of-scope is therefore the PVR's baseline and admission was
   the conditional — so resolving the condition against admission is the A&D doing its job, not
   overriding a requirement. Had it read the other way round, this would have been the R9 error
   repeated one section later.

   > **What this costs, stated rather than dropped.** Chai-1 existed to check whether the co-folded
   > pose is **stable** — and R4's pocket definition (*heavy atom within 5 Å of the co-folded ligand
   > pose*) rests on that pose. Excluding the arm does not remove the concern; it converts it from a
   > mitigated risk into an **unmitigated limitation**, and one this study cannot detect from the
   > inside: an unstable pose silently mis-assigns which residues are "pocket", which corrupts the
   > pocket/distal contrast that R4 *is*. It therefore belongs in the report's limitations section
   > as a named threat to validity, not in a list of things that were considered and skipped. **F2a
   > is the partial mitigation that remains** — matching on RSA and Grantham band constrains how
   > badly a mis-assigned distal residue can differ from its pocket counterpart, but it does not
   > detect a wrong pose.
9. **T8 completion** — decides lung-barrier vs generic. Not a blocker: §R2.4 narrows the claim
   automatically, so the study runs today at the narrower claim. Note r1.2's correction — widening
   is **human-gated**, not mechanical.
10. **Rounds beyond pilot + confirmatory** — assumed two; budget caps it.
11. **AM-6** — open upstream, unrelated to this study.

### Standing check — "machinery correct, quantity wrong"

**Five** defects in this design share one shape, and each after the first was found
only because its predecessors had been named:

| # | Machinery | Quantity it was pointed at | Should have been |
|---|---|---|---|
| R4 | the three-region rule | D3a's ρ-units | predicted-affinity units |
| r1.4 halt rule | a go/no-go gate | the equivalence band (secondary) | the sign test (primary) |
| G5 | a small-n bootstrap result | this statistic, unchecked | a statistic it had been measured on |
| **r1.5 halt rule (r1.6 fix)** | **the corrected go/no-go gate** | **power under A7-exchangeable ligands (0.935)** | **power under the roster's realised clustering — UNKNOWN, T18 absent** |
| **r1.6b cross-family fix (r1.6c)** | **the sign test, as that tier's conclusion** | **power at n=40 (0.935 / 0.470)** | **power at the tier's own n=20 (0.664 / 0.232)** |

The fourth was introduced *by the correction to the second*, and the fifth *by the
correction to the fourth*. That is no longer a run of bad luck; it is a property of
corrections. Fixing a rule's **statistic** left its **assumption** unexamined (fourth);
fixing the tier's **statistic** left its **`n`** unexamined (fifth). A number carried
across an assumption boundary is the same error as a number carried across a units
boundary — and a number carried across a **sample-size** boundary is the same error
again.

> **Standing rule, adopted r1.6c: when you correct a threshold, re-derive every figure
> that governs it, not only the one you changed.** Each of these corrections was right
> about the thing it changed and silent about what that thing depended on. The review
> that writes the standing check down is not exempt — the fourth survived exactly that
> review, and the fifth survived the review that catalogued the fourth.

In each case the mechanism was correct and would pass every test written for it.
**So the check is not "is this value right" but "what quantity is this measured in,
and which statistic does it govern"** — asked before the value is discussed at all.
Two of the three were caught by measuring rather than by review.

### Named but unspecified — the R4 defect class, swept systematically (r1.3)

r1.2 fixed `effect` (R4) and the `inconclusive` overlap (D3a) **as individual defects**, both
surfaced by review rather than by search. They share one shape: *an operation the document names,
that a test must check, and that the document never defines.* A sealed test author meets these as a
blank, and the failure mode is uniform — the test gets written to whatever the author assumed, and
the assumption is never visible again.

So the class was swept for directly, rather than waiting for review to surface the rest one at a
time. Four more sites, each verified against the full document before being listed here.

| # | Site | Named | Missing | Why it bites |
|---|---|---|---|---|
| G1 | F2a axis 4, R4 tests | **"substitution radicality"** — *"comparable chemical severity"* | any **metric** — **now CLOSED: Grantham, banded (see F2a)** | R4's test asserts mutants are *"matched on count and substitution radicality."* "Comparable" is not measurable, so this test cannot be implemented as written — and F2a exists precisely because matching on count alone is insufficient. The axis that carries the control's validity is the one axis with no metric. |
| G2 | F4 / R9 `authorize(batch_cost_usd, …)` | **the cost estimate** | how `batch_cost_usd` is **computed** — **now CLOSED, see below** | The ledger "charges the estimate at dispatch", and the guard's entire correctness rests on that number. The *interface* is airtight and the *estimator* is undefined; against a $30 ceiling an estimate wrong by 3× overruns the budget while every test still passes. Same shape as R4: rigorous mechanism, undefined input. |
| G3 | D3 pilot halt rule | **"halts and reports power"** | the **power computation** and its threshold — **now CLOSED: P0's simulation IS the criterion** | Stated qualitatively and it reads as specified. But the rule must fire **pre-hoc**, and the document gave no way to evaluate it pre-hoc. A halt criterion that can only be evaluated after the thing it was meant to prevent is not a guard. |
| G5 | D3a, R3, R4 — 11 sites | **"95% bootstrap CI"** | **which bootstrap** — **now CLOSED: BCa, calibrated** | Found by literature review, not by the r1.3 sweep, because the term *looks* fully specified. Percentile/basic/BCa/studentized diverge materially at n≈20–40, and percentile intervals are **too narrow** there. Such an error *would* raise `lo` and lower `hi`, making **both** `sensitive` and `insensitive` easier to reach and suppressing **`inconclusive`**. **That harm was claimed, then measured, and the measurement does not support it for this statistic** — BCa 0.930 / 0.384 vs percentile 0.943 / 0.386 at n=40, equivalent, percentile marginally closer to nominal (see P1). BCa is sealed for skew-tracking and reproducibility, **not** because percentile was shown to fail. The r1.4 sentence *"an unnamed variant was biasing the study against its own honesty mechanism"* is **withdrawn**; it survived here for 200 lines after P1 retracted it, because the retraction was applied at the finding and not at the index. |
| G4 | Scope 8, Chai-1 | **pose "stability"** | any criterion | Lowest severity — Chai-1 scores nothing, so a vague criterion contaminates no verdict. Listed because R4's pocket definition **depends on the co-folded pose**, so "stable" is doing real work for a definition that does reach a statistic. |

**Checked and NOT a gap** — recorded so the next reviewer does not re-derive it: *"a ligand with no
valid shuffle partner appears in the report's drop list"* looks like the same defect, and is not. F1
defines partner validity exactly (*"drawn only from panel targets with no measured and no annotated
interaction with that ligand"*) and mandates the drop record (*"never silently retained, never
silently dropped"*). A negative result is worth writing down: an unrecorded check gets repeated, and
the second reviewer has no way to tell "verified fine" from "nobody looked."

**G2 · closed, from the PVR — the estimator.** The figures already exist upstream and did not
need a ruling. PVR *Constraints* declares the L40S rate at **~$1.95/GPU-hour** and Boltz-2
throughput at **80–100 complexes/GPU-hour**; PVR **G4** caps spend at **$30**. So:

    batch_cost_usd = n_complexes / THROUGHPUT_COMPLEXES_PER_GPU_HOUR * RATE_USD_PER_GPU_HOUR

**The throughput constant takes the SLOW end of the published range — 80, never 100.** This is the
whole design decision, and it is a fail-closed choice rather than a conservative habit: throughput
appears in the *denominator*, so an optimistic value **understates** cost. Estimating at 100 when
the true rate is 80 understates every batch by 25%, and the ledger charges the estimate at dispatch
— so the guard authorizes its way past a $30 ceiling while `ceiling − spent` reads healthy the
entire time and every existing R9 test passes. The direction of the error is what matters, not its
size: overestimating halts a run that could have continued, which is recoverable; underestimating
overruns the budget the guard exists to protect, which is not.

Both constants live in the **sealed `prereg.yaml`**, never in code — the same rule D3a's bands
follow, for the same reason. The pilot **measures actual throughput** and the measured value is
sealed with the other pilot-derived numbers; until then the published slow bound stands.

**Tests.** (1) the estimator uses the slow throughput bound — a test pins the constant and **fails
if it rises**, because that single edit is what silently converts the guard into a rubber stamp;
(2) a batch whose estimate would breach `ceiling − spent` is refused **before** dispatch, not
reconciled after; (3) estimator constants are read from the sealed pre-registration, and a run
whose `prereg.yaml` lacks them **raises** rather than defaulting.

**Consequence for the seal.** G1 and G2 are **blockers**, and neither was on the blocking list
before this sweep. G1 makes R4's control untestable — the same defect r1.2 closed in R4's statistic,
still open one line below it in R4's matching. G2 makes R9's guard unfalsifiable. Sealing over
either notarises a pre-registration whose tests cannot be written, which is the failure the seal
exists to prevent rather than a cost of delaying it.

**All four are now closed.** G1 by the principal's Grantham ruling (see F2a), G2 from the PVR's own
rate figures (above), G3 into the pilot ruling, and **G4 is moot — Chai-1 is excluded**, so there is
no pose-stability criterion left to specify (the limitation that creates is recorded under Scope 8,
not dropped). What blocks the seal is now only the **pilot-measured numbers**.

---


---

## The pilot — specification (r1.4, principal's 1B1 of 2026-09-07)

Literature-driven throughout. Every number below is either measured, taken from a cited source, or
derived from one — none is chosen.

### P0 · The power simulation gates everything, and costs nothing

**The first deliverable is a local simulation, before any GPU batch is authorized.** It runs on the
M5 Max at **zero Modal spend**, and it exists because a pre-hoc calculation says the study may not be
able to render the verdict it was built around.

**The finding that forces it.** `insensitive` requires the whole 95% CI inside `±0.10`. Using
Fisher-z (`SE ≈ 1.06/√(n−3)`), at n≈40 ligands a single Spearman ρ has a 95% half-width of about
**0.33**. For the *difference* `Δρ`, the half-width depends on how correlated the native and shuffled
ρ estimates are across ligand resamples:

| corr(ρ_native, ρ_shuf) | Δρ 95% half-width | inside ±0.10? |
|---|---|---|
| 0.0 | ~0.48 | no |
| 0.5 | ~0.34 | no |
| 0.8 | ~0.22 | no |
| 0.95 | ~0.11 | marginal |

Fitting the band needs `r ≳ 0.96` — and **shuffling is designed to destroy the signal**, so that
correlation should be *low*. The realistic half-width is 3–5× the band. If that holds, D3a's
three-region partition collapses to two in practice and the PVR's *"publishable whether positive or
negative"* is unachievable on the negative side.

These were analytic approximations. **P0 has now run** (`chipsim/audit/power.py`, zero Modal spend)
and the measured answer is worse than the estimate on one axis and much better on another.

**Result 1 — `insensitive` is unreachable, confirmed.** `P(insensitive) = 0.000` in **all 36 cells**:
ρ_native ∈ {0.3, 0.5, 0.7} × ρ_shuffled ∈ {0.0, 0.2} × n ∈ {20, 30, 40, 60, 100, 160}. Median
half-width at n=40 is **0.36–0.42** against a band of `±0.10`; even at **n=160** it is 0.17–0.21.
No feasible ligand count brings a CI inside the equivalence band. **D3a's three-region partition is
two-region in practice**, and the pre-registration must say so rather than let a reader infer a
three-way outcome.

**Independently reproduced.** The CTO re-ran the scan on a different seed (4242) with its own cell
choices: half-widths 0.342–0.421 at n=40 and 0.167–0.206 at n=160, `P(insensitive) = 0.000`
throughout — matching to the third decimal. Two implementations of the arithmetic agree, rather than
one agreeing with itself. That mattered here because the number changed what the study claims it can
conclude.

**Result 2 — the primary inference is well powered.** The study's actual inference is the one-sided
**sign test** (`p = 1/2⁷ ≈ 0.008`), which uses point estimates and never touches the band:

| true Δρ | n=20 | n=40 | n=60 | n=100 |
|---|---|---|---|---|
| 0.1 | 0.03 | 0.05 | 0.09 | 0.13 |
| 0.2 | 0.09 | 0.17 | 0.35 | 0.56 |
| 0.3 | 0.22 | 0.50 | 0.71 | 0.91 |
| **0.5** | 0.67 | **0.92** | 0.99 | 1.00 |
| 0.7 | 0.97 | 1.00 | 1.00 | 1.00 |

At the planned n≈40 the study has **92% power for a large effect** and 50% at Δρ=0.3. The A&D's
existing claim — *"can detect a unanimous large effect and essentially nothing subtler"* — is
**confirmed and now quantified**: *large* means `Δρ ≳ 0.5`.

**Both results are upper bounds.** A2 (measured affinities treated as noise-free) and A4 (equal n and
equal effect across targets) both err optimistic; see `ASSUMPTIONS.md`. Real assay noise attenuates
`ρ_native`, and per-target heterogeneity weakens a unanimity criterion that is only as strong as its
weakest target.

The halt criterion this feeds — the thing r1.2 named and could not evaluate:

> **G3 · halt rule — CORRECTED after P0 ran (r1.5).** The r1.4 wording was:
> *"if no achievable CI fits the equivalence band, halt and authorize no batch."*
> **That rule was wrong and would have killed the study.** P0 measured
> `P(insensitive) = 0.000` in all 36 cells, so it fires unconditionally — while the
> PVR explicitly accepts *"a defensible 'inconclusive at this power'"* as success.
> It keyed a go/no-go on a **secondary** statistic: the study's primary inference is
> the one-sided **sign test** over seven targets (`p = 1/2⁷ ≈ 0.008`), which uses
> point estimates only and never touches the equivalence band. Same defect class as
> R4 inheriting D3a's units — the machinery was right and was pointed at the wrong
> quantity.
>
> ### THE FLOOR HAS A SCOPE — CTO ruling 2026-09-11, correcting its own omission
>
> The 0.80 floor governs the **PRIMARY INFERENCE ONLY**: the sign test over seven
> targets on the **within-panel** tier.
>
> **Control tiers report their power beside their verdict and never gate on it.**
> Cross-family is a **negative control** — its designed outcome is that the effect
> *vanishes* when the target is swapped. **Requiring a detection-power floor of an
> arm built not to detect anything is a category error**, and it is what made the
> gate fire unconditionally: cross-family at n=20 tops out at **0.664** and no
> feasible thinning reaches 0.80, so applied per tier the floor HALTS the study
> whatever the data say.
>
> That is the r1.4 halt-rule defect one rung up — there, a go/no-go keyed on a
> *secondary statistic*; here, a floor applied to a *secondary arm*. Same shape:
> **a gate pointed at something it was not built to measure.** Ninth instance of
> the standing check.
>
> **So cross-family reports 0.664 next to its verdict, disclosed and not gating.**
> A floor without a stated scope is what produced this, so the scope is now part of
> the floor wherever it appears.

> **The rule, restated:** the pilot halts if the **sign test** is underpowered at the
> effect size the study declares it targets. The A&D declares *"powered for a large
> effect only"*; P0 quantifies *large* as `Δρ ≳ 0.5`, where power at n=40 is **0.92 —
> an UPPER BOUND (A2), and the exchangeable case (A7)**.
> **Verdict: PROCEED — PROVISIONALLY.** The qualifier is part of the rule, not a caveat
> appended to it.
>
> **r1.6 · the halt rule inherited a number computed under an assumption it does not
> state — the FOURTH instance of this document's own standing defect.** P7 measured that
> under analog-series structure entirely ordinary for a ChEMBL set the same study sits at
> **0.46–0.75**; at `icc = 0.8`, series of five, power is **0.46**. A rule that halts on
> *"underpowered at the declared effect size"* evaluates to **PROCEED at 0.92** and to
> **HALT at 0.46**. The gate exists to fire **pre-hoc**, and it was being evaluated on the
> single ligand-set assumption guaranteed not to hold: no real compound set is
> exchangeable. Same shape as R4 inheriting D3a's units, the r1.4 halt rule inheriting the
> equivalence band's authority, and G5 inheriting a general result's conclusion — the
> machinery was right and was pointed at the wrong quantity.
>
> **PROCEED is therefore conditional, and its condition is now named.** The halt rule is
> evaluated on the power computed **across the `icc` sensitivity band** at the roster's
> **measured series-size distribution** (P7), never on the exchangeable idealisation, and
> PROCEED requires it to hold **across the whole band**.
>
> > **r1.6c — this sentence previously read *"the power computed from the measured `icc`"*,
> > which is the identical construction r1.6 excised 250 lines below, reproduced inside the
> > halt rule itself.** `icc` is not measurable pre-spend; only the size distribution is.
> > The r1.6 sweep corrected the P7 clause and did not sweep the G3 block above it — the
> > same partial-sweep-declared-complete this document has now committed **three** times
> > (r1.5's vacuity sweep, r1.6b's A&D-but-not-ledger sweep, and this one). **A sweep is
> > not complete until it has been run against the load-bearing site, and the load-bearing
> > site is the one defining the precondition of spend.** Until that
> roster exists (**T18 — absent**), realised power is **UNKNOWN, not 0.92**, and PROCEED
> stays provisional. **No batch is authorized on a provisional PROCEED.**
>
> **Ordering consequence, which is the operative part.** The realised-clustering
> measurement is a **precondition of the halt decision**, not a refinement reported
> beside it. It is free — RDKit/MMP, local, zero Modal cost — and it gates spend, so it
> runs **before** the halt rule is evaluated, not after.

#### Why the sign test is the PRIMARY inference — stated, not coincidental (r1.6)

The sign test has now been the statistic that still works **twice**, in two unrelated
rescues, and the CTO is right that leaving that as coincidence wastes the finding:

1. **`insensitive` became unreachable** — no feasible `n` brings a CI inside `±0.10`
   (half-widths 0.34–0.42 at `n=40`, 0.17–0.21 at `n=160`). The equivalence band died.
   The sign test did not.
2. **The cross-family negative control became unreachable** for the same reason, on a
   *wider* CI still (20 ligands). Its conclusion was re-based on the sign test.

**The reason is structural, and it is one sentence:** the sign test consumes only the
**direction** of `Δρ` per target, so its precision requirement is a *comparison*, not an
*interval*. Everything that killed the other two — CI half-width at small `n`, the
bootstrap variant (G5), the equivalence band's absolute scale — acts on **interval width**.
A statistic that never forms an interval is immune to all of it by construction.

**What that buys, and what it does not.** It buys robustness: seven independent directional
calls at `p = 1/2⁷ ≈ 0.008` one-sided need no CI to be narrow. It does **not** buy immunity
to `n` — P7 showed the sign test degrading 0.935 → 0.470 under clustering, because effective
`n` still governs whether each *direction* is called correctly. So the correct reading is
**not** "the sign test is robust, therefore power is fine": it is immune to *width* and
fully exposed to *effective n*. That is exactly why A7, not the band, is the live threat to
this study, and why the halt rule keys on the sign test while the realised-clustering
measurement gates the halt rule.

**Design consequence:** any future statistic proposed as primary must be checked against the
same question — does its inference require an interval, or only a comparison? Interval-based
primaries are not viable at this `n`, and that is now a known property of the design rather
than a lesson re-learned per statistic.

P0 also calibrates the CI method (below) by measuring realised coverage at the realised n.

### P1 · Statistic method — BCa, calibrated

**G5 (new gap, found by literature review).** r1.2 said *"95% bootstrap CI"* **eleven times and never
named the variant.** Percentile, basic, BCa and studentized bootstraps diverge materially at n≈20–40,
and the simulation literature is unambiguous that percentile intervals are **too narrow** at small n
— 81–83% actual coverage for a nominal 95% at n=5, and still optimistic at n=20; for Spearman at
n=10 with ρ≤0.5, intervals can exceed unity in length.

**The direction of such an error would make it a defect and not a detail.** A too-narrow CI raises
`lo` and lowers `hi`, so it makes **both** `sensitive` and `insensitive` easier to reach — it would
systematically suppress **`inconclusive`**, the verdict R8 and F7 exist to make renderable.

> **Correction (r1.5) — this harm was claimed and then measured, and the measurement does not
> support it.** r1.4 asserted that "an unnamed bootstrap variant was quietly biasing the study
> against its own honesty mechanism." For **this** statistic at **this** n, that is false. Measured
> over 300 trials at n=40:
>
> | method | coverage (nominal 0.95) | median half-width |
> |---|---|---|
> | BCa | 0.930 | 0.384 |
> | percentile | 0.943 | 0.386 |
>
> They are equivalent, and percentile is marginally closer to nominal. The r1.4 claim was imported
> from the general small-n literature and asserted about a specific statistic it had not been checked
> against — the same defect class as R4 inheriting D3a's units, committed while documenting that
> defect class.
>
> **BCa is still what gets sealed**, for the reasons that survive: its acceleration term tracks skew,
> and `Δρ` is a bounded difference that is skewed near the ends of the ρ range; and a named variant
> is reproducible where an unnamed one is not. It is **not** sealed because percentile was shown to
> fail. No test in this suite discriminates the two, and that is now stated where a reader will find
> it rather than left to be re-derived.

**Sealed: BCa**, plus P0's coverage calibration. If measured coverage falls below nominal, the
interval is widened by a calibrated (double) bootstrap and *that* is sealed. Coverage becomes a
measured property rather than an assumed one.

### P2 · What is held out, and what is not

**Ligands, not targets.** The panel is seven proteins across three families (ABCB1/ABCG2/ABCC1;
TFRC/FCGRT; SLC15A1/SLCO2B1). Holding out *targets* — the reading *"held-out target set"* invites —
breaks two things: the confirmatory study drops to 5–6 targets, so *"unanimous across all seven is
publishable"* no longer applies as written; and F1 draws shuffle partners from panel targets, so
removing targets shrinks the within-panel pool and changes the harder tier's difficulty. **Ligands
are also the correct unit on the design's own terms** — the CI is bootstrapped *over ligands*, so
ligands are the resampling unit and a ligand split is the statistically coherent independent draw.

**The holdout is scoped to R4 alone.** Pre-registration integrity is a property of *each threshold's
provenance*, not a blanket rule:

- **R3 needs no holdout.** Its `+0.20`/`±0.10` band was fixed *a priori* by principal ruling,
  independent of any data from this system. Nothing about R3 is circular, so it keeps the full
  ligand set and its CIs stay as tight as the data allows.
- **R5 needs no holdout either** — see P4; its threshold is a literature convention, not a
  measurement.
- **R4 does**, because its band is derived from observed spread.

### P3 · R4 — the band formula, sealed BEFORE the pilot runs

**This is what makes "pilot first" rigorous rather than theatre.** The rule mapping observations to
thresholds is sealed *before* the pilot executes, so no judgement is applied after seeing data:

    equivalence band = ± 1 SD of effect(distal) across ligands
    sensitive floor  = + 2 SD of effect(distal) across ligands

**The distal arm IS the empirical null** — matched mutations that should not move binding — so it
measures how much this model moves for reasons unrelated to pocket engagement. The band therefore
describes *this system* instead of importing a convention.

**Mandatory cross-check against the literature.** Boltz-2's published **pairwise** error (PMAE) is
**0.85–1.20 log₁₀ units** on FEP+ and hit-to-lead benchmarks. PMAE is error on *differences between
compounds*, which is exactly `Δ_mut`'s shape, so it is the correct reference — not MAE. **If 2 SD
lands below that range, R4 is claiming resolution finer than Boltz-2 has ever demonstrated on
differences, and the report must say so.** (The comparison is not decisive on its own: PMAE is error
against *experiment* on other targets, while R4 compares model to model on ours, where systematic
error partly cancels. It is a sanity bound, and it is recorded as one.)

### P4 · R5 — off the pilot list, sealed from the literature today

**Cliff = a matched molecular pair (single-site, size-restricted transformation) with a ≥100-fold
(2 log) measured potency difference.** This is the field's preferred definition; the ≥100-fold
criterion is the long-standing standard, and MMP-restricted similarity supersedes a raw Tanimoto
cutoff because a Tanimoto threshold admits pairs differing at several sites.

**Why R5 differs from R4, stated because the two look alike and are not.** R4's threshold is in
**model-internal units** with no external convention, so it must be measured. R5's is in
**experimental potency units**, where the field has a settled standard — measuring our own would
spend pilot budget to re-derive a number already agreed on, and a bespoke threshold is *harder* to
defend than the standard one. Computable locally with RDKit/mmpdb at no Modal cost.

**The cost, recorded:** MMP restricts the pair pool, so at ~40 compounds the cliff stratum may be
small **if discovered** — but ADR-0004 rules the stratum is **curated toward ~50 pairs**, precisely
because discovery from a diversity-selected roster is the worst available source. R5 reports the
achieved count and its power, and **it does not quietly loosen the criterion to fill the stratum**.
See R5 for the curve and the five-discordant structural floor.

### P5 · Budget — the design did not fit, and now does

**r1.2's complex count was wrong.** It read *"3 pocket + 3 matched distal per target = 42 mutant
complexes … sits inside the ~1,200–1,500 complex budget."* But `effect(M) = mean over ligands l in L
of [f(l,t_wt) − f(l,t_M)]` requires **every mutant against every ligand in L**, so R4 costs
`7 × mutants × |L|` complexes. **42 = 7 × 6 counts variants, not complexes.** At `|L| = 40` that is
1,680 complexes for R4 alone; with R3 the study needed ~2,520 — roughly **$54 against a $30
ceiling**. At `|L| = 1`, which "42 complexes" literally implies, bootstrap-over-ligands is impossible.
The arm was simultaneously over budget and under-specified, and the budget sentence concealed it.

**Resolved** — `2 pocket + 2 distal` per target, `|L| = 15`:

| Item | Complexes |
|---|---|
| R3 native (40 ligands × 7) | 280 |
| R3 within-panel shuffle (40 × 7) | 280 |
| R3 cross-family shuffle (**20** × 7) | 140 |
| R4 confirmatory (7 × 4 × 15) | 420 |
| R4 pilot (3 targets × 4 × **10 held-out** ligands) | 120 |
| **Total** | **1,240** |

At **90 complexes/GPU-h** on L40S ($1.95/GPU-h) → **13.8 GPU-h ≈ $26.87**.

> **The principal ruled to keep 90, with the risk in front of him. Recorded plainly.**
> 90 sits inside the PVR's stated 80–100, so it is a legitimate reading and not a
> fabricated number. But the design's own estimator constant is the **slow** bound,
> and at 80 the same 1,240 complexes cost **$30.22 — a breach of the $30 ceiling**.
> **The apparent $3.13 of headroom is an artefact of the assumption, not margin.**
>
> **So the assumption is MEASURED, not merely disclosed.** `chipsim/audit/budget.py`
> re-projects the total from **realised** throughput after batch 1 and **halts
> pre-emptively if the projection breaches $30** — before the remaining work is
> dispatched, not after. A ledger that compares only *spent-so-far* against the
> ceiling discovers a breach at the moment it is too late to avoid: every batch is
> individually affordable while the total is not.
>
> This matches the rest of the design rather than being a special case — P0 measures
> before any spend, G3 halts before the batch, R9 now projects before the remainder.
> Realised throughput is reported beside the cost in the run record, so **90 is
> auditable against what actually happened** (the A9 shape: a planning number a
> single early measurement can replace). **Treat 90 as provisional until batch 1
> measures it.** Wild-type predictions are shared with R3's
native arm, so R4 adds no separate WT cost.

**Two costs, both deliberate and both stated.** `2+2` shrinks the Grantham/RSA matching pool, so
F2a's *"an unmatched pocket mutant raises rather than being reported against a mismatched control"*
will fire more often — which is the correct failure, loudly. And thinning the cross-family tier to 20
ligands widens its CI further on the tier that would give the **stronger** negative; it is the
sanity floor rather than the decision-relevant question, which is why it was the one thinned.
**Per r1.6 this cost is smaller than r1.4 believed, and for an uncomfortable reason:** the CI on
this tier was never going to fit the equivalence band at *any* feasible width, so thinning it to 20
costs nothing that was reachable at 40 **for the CI**.

> **r1.6c — the second half of that sentence was FALSE, and it was mine.** r1.6b continued
> *"the tier's conclusion rests on the sign test over point estimates, which loses precision
> from the cut but does not lose a verdict it could otherwise have rendered."* Measured at
> the tier's own `n = 20`: the sign test reaches **0.664** under full exchangeability and
> **0.232** at `icc = 0.8`, against 0.935 / 0.470 at n=40. A tier at 0.23 power **does** lose
> verdicts it would otherwise have rendered — that is what low power means.
>
> The error is exact and it is instructive: r1.6b re-based this tier's conclusion onto the
> sign test **because** the sign test is immune to interval width, and then reasoned about
> the ligand cut as though the tier were still CI-limited. But this document's own
> §*"Why the sign test is PRIMARY"* states the sign test is **immune to width and fully
> exposed to effective `n`** — and the cut is a cut in `n`. The rhetorical split between
> "width" and "effective n" is precisely what concealed it: a reader who accepts "immune to
> width" stops asking about the tier whose `n` was halved to save budget.
>
> **Consequence, unresolved here:** the cross-family tier is underpowered *before* clustering
> is considered. Either it returns to 40 ligands, or its power is stated beside its verdict
> every time that verdict is reported. **The halt rule is evaluated per tier, at each tier's
> own `n`, across the `icc` band** — not once at n=40 for a design that runs two tiers at two
> different ligand counts.

### P7 · A7 measured — analog series are the largest single threat to power

**A7 was the assumption most likely to be quietly optimistic, and it is.**

> **r1.6c · regenerated from a committed, seeded driver.** The r1.6 table carried no
> seed, no trial count and no driver anywhere in the repo, and its power column did not
> reproduce — `(5, 0.8)` returned 0.497 / 0.467 / 0.477 / 0.520 across seeds against a
> recorded `0.46`. That spread is Monte-Carlo noise at 300 trials (SE ≈ 0.029), so the
> recorded values were noise-consistent and **not fabricated** — but `0.46` is the single
> number that flips the halt rule from PROCEED to HALT, in a repository whose S12
> machinery exists so that a run can be regenerated from its recorded config and seed. A
> go/no-go figure that cannot be regenerated fails this project's own standard.
>
> **Driver:** `workstreams/chipsim-lbm-audit/verification/p7-power-table.py`,
> `seed = 0`, `trials = 20000`, run from `projects/lung-on-chipsim`. Trials raised from
> 300 so the Monte-Carlo SE (~0.0035) sits in the **third** decimal rather than the
> second — at 300 trials the SE was the entire discrepancy. **The seed was fixed before
> running and the output is reported as it came**; no seed was selected to reproduce the
> previously recorded values.

`clustered_sign_test_power`, 7 targets, true `Δρ = 0.5`, seed 0, 20000 trials:

**n = 40 ligands — within-panel arm, and the headline.**

| series size | icc | n_eff | sign-test power | MC SE |
|---|---|---|---|---|
| 1 (none) | 0.0 | 40.0 | **0.935** | 0.0017 |
| 2 | 0.5 | 26.7 | 0.886 | 0.0022 |
| 3 | 0.5 | 20.3 | 0.845 | 0.0026 |
| 5 | 0.3 | 18.2 | 0.873 | 0.0024 |
| 5 | 0.5 | 13.3 | **0.746** | 0.0031 |
| 5 | 0.8 | 9.5 | **0.470** | 0.0035 |
| 8 | 0.8 | 6.1 | 0.318 | 0.0033 |

**n = 20 ligands — the CROSS-FAMILY tier. Never previously computed.**

| series size | icc | n_eff | sign-test power | MC SE |
|---|---|---|---|---|
| 1 (none) | 0.0 | 20.0 | **0.664** | 0.0033 |
| 2 | 0.5 | 13.3 | 0.579 | 0.0035 |
| 3 | 0.5 | 10.3 | 0.532 | 0.0035 |
| 5 | 0.3 | 9.1 | 0.583 | 0.0035 |
| 5 | 0.5 | 6.7 | **0.447** | 0.0035 |
| 5 | 0.8 | 4.8 | **0.232** | 0.0030 |
| 8 | 0.8 | 3.4 | 0.208 | 0.0029 |

> **What regeneration changed.** Every previously recorded value sits within ~2 MC SE of
> the regenerated one, so nothing here overturns r1.6's conclusion. Three things do move:
> the exchangeable baseline is **0.935**, which retires the 0.92 / 0.94 / 0.95
> multiplicity (all three were the same quantity under different estimator runs); the
> clustered range is **0.47–0.75**, not 0.46–0.75; and the `(3, 0.5)` `n_eff` is **20.3**,
> not 20.0, because 40 does not divide by 3 — the old column assumed exact divisibility
> and the remainder cluster was dropped.
>
> **The cross-family tier is underpowered before clustering is considered at all.** At
> `n = 20` the sign test reaches only **0.664** even under full exchangeability, against
> 0.935 at n=40, and falls to **0.232** at `icc = 0.8`. See the fifth instance below.

**P0's headline 92% assumes exchangeable ligands.** Under analog-series structure
that is entirely ordinary for a ChEMBL set — a handful of med-chem campaigns,
series of five, members correlated at 0.5–0.8 — the study sits at **0.46–0.75**.
Forty compounds in eight series of five carry about **thirteen** compounds' worth
of independent information, and at `icc = 0.8` about **nine**.

**The design consequence, which did not exist before this was measured:
composition matters as much as count.** Adding compounds from a series already
represented buys almost nothing; adding a structurally distinct compound buys a
full unit of n. So:

- **Structural diversity buys power.** A 40-compound set assembled by taking whatever
  has measured values against the panel will be *worse* than a 25-compound set chosen
  for distinctness. **This is a measured consequence, NOT a pre-registered selection
  criterion — see the open item below.**

> **r1.6 · OPEN ITEM — diversity and matched pairs pull the roster in opposite
> directions. NOT RESOLVED HERE, and deliberately so.**
>
> r1.5 wrote the line above as *"diversity is a selection criterion in the
> pre-registration rather than an afterthought."* **That pre-registration is
> withdrawn.** Two reasons, and the second is the substantive one.
>
> **First, it is not this document's to set.** The roster is `configs/poc_compounds.yaml`
> (**T18**), a human artifact. An A&D that pre-registers its selection criterion has
> written a human decision on the human's behalf — the same class of over-reach the
> five absent artifacts exist to prevent.
>
> **Second, and worse: it collides with R5.** **`R5` requires matched molecular pairs
> crossing a potency or efflux cliff, reported cliff-stratified** (audit PVR, R5). **An
> MMP is an analog series by construction** — a pair differing by one moiety *is* the
> cliff test's unit and *is* the clustering that destroys effective `n`. So on a single
> shared ligand set:
>
> | Pulls toward | Requirement | Source |
> |---|---|---|
> | **diversity** | structurally distinct compounds, so the sign test and `Δρ` keep their `n` | A7 / P7, measured |
> | **analog pairs** | MMPs across a cliff, or R5 has no test | **audit PVR · R5** |
>
> Following either alone damages the other test. r1.5 saw only the first and pre-registered it.
>
> **Provenance note, because it changes who owns this.** The CTO put the tension against
> *"PVR §2E — 20–40 … plus matched molecular pairs … pair count matters more than compound
> count."* That sentence is **verbatim accurate but belongs to a different document**:
> `workstreams/lung-on-chipsim/PVR.md`, the *"minimum viable chip"* table for the **ChipSim
> PoC simulator**, and there is no §2E. It does not govern this workstream. The audit's own
> PVR sets its own design — *"~7 barrier proteins × ~40 compounds"* — and its MMP
> requirement enters through **R5**, not through a roster rule. The tension is therefore
> **internal to the audit**, not inherited from the product PVR, which makes it ours to
> surface and the principal's to settle. Recorded under the r15 provenance convention.
>
> **The CTO's proposed resolution, recorded as a PROPOSAL and not adopted:** stratify the
> roster — a **diversity stratum** carrying the sign test and `Δρ`, and a **pair stratum**
> of MMPs carrying the cliff and disambiguation tests, **excluded from the power
> calculation rather than discounted into it**. It has the merit of extending to
> *construction* the stratification the design already requires for *analysis* (R5 reports
> cliff pairs separately because *"aggregate metrics hide exactly the cases the project
> exists to resolve"*). **Whoever curates T18 must be shown both numbers before choosing;
> no criterion is pre-registered until they do.**
- **The pilot measures the realised clustering** — series membership is computable
  locally from SMILES with the same RDKit/MMP machinery R5 already needs, at zero
  Modal cost — and **P0 is re-run on the measured series-size distribution**. The
  power statement that reaches the model card is the one computed from the actual
  compound set, not the exchangeable idealisation.

> **r1.6 · `icc` is NOT measurable from SMILES, and r1.5 said it was.** The clause
> above previously read *"P0 is re-run on the measured `icc` and series-size
> distribution"*, having opened by correctly noting that **series membership** is what
> SMILES gives you for free. It slid from a quantity that IS free to one that is NOT,
> inside one sentence, and the word *"measured"* carried across the join.
>
> Structure says **which** compounds are analogs. `icc` says how correlated their
> `(y, f)` contributions are — and `f` is a Boltz-2 prediction that **does not exist
> until the batch has been spent**. So a pre-spend `icc` cannot be measured; it can only
> be assumed. A halt rule fed an assumed `icc` labelled *"measured"* is the failure this
> gate exists to prevent, reproduced one level up.
>
> **So `icc` is a sensitivity RANGE, not an input.** `series.power_over_icc_range`
> reports `(icc, deff, n_eff)` across the plausible band and refuses to return a point
> estimate. **The halt rule holds across the band or it does not hold** — PROCEED at
> `icc = 0.3` and HALT at `icc = 0.8` is not a PROCEED. What the roster genuinely
> supplies pre-spend is the **series-size distribution**, and that alone is a real
> tightening: it converts A7 from unbounded to bounded.

> **r1.6 · `power.effective_n` assumes EQUAL cluster sizes, and real rosters are not.**
> The design effect is `1 + (m_A − 1)·icc` where `m_A = Σmᵢ²/Σmᵢ` — the **size-weighted**
> mean. `effective_n(n, cluster_size, icc)` takes one scalar size, so applied to a real
> roster it is reached through the **arithmetic** mean. By Cauchy–Schwarz `m_A ≥ mean(m)`
> for every size vector, equality only when all clusters are identical — so the
> arithmetic form **always** understates the discount, and never in the safe direction.
>
> **Measured:** one series of 12 among 28 singletons at `icc = 0.5` — arithmetic mean
> reads `n_eff = 33.6`, size-weighted reads **15.1**. A **2.2× overstatement** of the
> independent information in the roster, on a shape that is entirely ordinary. P7's
> table is unaffected (it used equal sizes of 5, and `effective_n_unequal([5]*8, 0.5)`
> reproduces its `13.3` exactly — the new path is cross-checked against the old on the
> case where both are valid), but any application to an actual roster would have
> inherited the optimistic form. `design_effect`/`effective_n_unequal` in
> `chipsim/audit/series.py` are now the path for unequal sizes.
- **Every reported power figure carries which assumption it rests on.** "92%" and
  "46%" are the same study under different ligand sets, and a number quoted
  without that qualifier is not interpretable.

> **How this model was nearly wrong, recorded because the number is load-bearing.**
> The first implementation clustered only the *prediction noise* and left the
> latent independent. It reduced no information — measured power came out
> *higher* under clustering (0.94 vs 0.92) — and would have argued A7 was free.
> The effect is not correlated errors; it is that the **(y, f) pairs within a
> series are near-duplicates**. Caught by the monotonicity test, which is now
> written to fail loudly with both numbers in its message.

### P6 · What the pilot returns

1. **P0's power simulation** — the halt decision, before any spend.
2. **Realised BCa coverage** at the achieved n, and the calibration if needed.
3. **`effect(distal)` SD per target** → R4's band by the P3 formula.
4. **Run-to-run σ on identical input** → R10's replay tolerance. Boltz-2's affinity head is a
   **two-model ensemble** and the paper states no determinism guarantee — *"deterministic"* does not
   appear in it — so this cannot be taken from the literature and must be measured.
5. **Measured throughput on L40S** → replaces the published bound in G2's estimator. The paper's
   **20 GPU-sec/complex** on H100 (~180/GPU-h) independently corroborates the PVR's 80–100/GPU-h for
   the slower L40S, which is why the estimator's slow bound is defensible until measured.
6. **RAM and disk high-water marks** → R1's floors.

### Sources

- Boltz-2 (Passaro, Corso, Wohlwend et al.) — affinity units *"standardized to log 10 scale derived
  from values measured in µM"*; PMAE/MAE tables on FEP+ and hit-to-lead; *"20 GPU sec"* per complex;
  two-model affinity ensemble. <https://jeremywohlwend.com/assets/boltz2.pdf>
- Bishara & Hittner, *Confidence intervals for correlations when data are not normal*, Behavior
  Research Methods. <https://link.springer.com/article/10.3758/s13428-016-0702-8>
- Activity-cliff definition (≥100-fold potency difference; MMP-restricted similarity) — Stumpfe &
  Bajorath, *Evolving Concept of Activity Cliffs*, ACS Omega.
  <https://pubs.acs.org/doi/10.1021/acsomega.9b02221>

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
