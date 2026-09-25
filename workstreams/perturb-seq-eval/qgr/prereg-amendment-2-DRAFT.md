# DRAFT — Pre-registration AMENDMENT 2 (v0.6.0 sweep) — NOT LOCKED

> **Status: DRAFT (CTO #395).** Nothing here is in force. `projects/perturb-seq-eval/paper/PREREGISTRATION.md` is
> unchanged. The pre-registration is amended **once**, before any v0.6.0 data exists, and only after **all**
> the PENDING sections below are ruled. At that point this text is folded into `PREREGISTRATION.md` in a single
> `prereg(...)` commit, and the sweep's provenance pins that commit. Nothing that changes the measurand is
> implemented before the lock.
>
> Why this lives here: `qgr/**` is excluded from the receipt diff-hash, so committing the draft does not stale
> the P0-P5 receipt (7d3d659), which is waiting for principal approval.
>
> Sources: the P0-P5 quality gate (findings: `qgr/evidence/qg-p0p5-findings-scored.md`; triage:
> `qgr/evidence/qg-p0p5-triage.md`) and the principal decision brief `qgr/principal-decisions-p0p5.md`.

## Why an amendment is needed

The P0-P5 quality gate found ten items where the code as built does not measure what `PREREGISTRATION.md`
describes, or where the description is incomplete. Fixing any of them changes the measurand, so each needs a
principal ruling, written here before data, rather than a silent fix. Four items are ruled. Six are pending.

---

## A2-1 (C1): confidence is a required, verbalised field. RULED (principal, 2026-09-25 20:38Z)

**Found:** no role's prompt or schema asked for a confidence. A missing value was silently defaulted to a
constant, so on the earlier artifact almost every LLM step carried the same value, and ACE_norm (an H4/H5 input)
was near-constant.

**Amended rule:** every agent role's schema and prompt require a field `confidence`: a number in [0, 1] that the
model states verbally about its own proposal. A missing, non-numeric, non-finite or out-of-range confidence is a
**schema failure**. The step takes the fallback path, and under convention 4 the run is **invalid** (C-KEY-2).
Confidence is **never imputed or defaulted**.

**Text it changes in `PREREGISTRATION.md`:**
- Convention 4 gains the confidence rule above.
- "Per-run components": C(r) is read from this required field. The "non-finite confidence" exclusion becomes
  unreachable for a valid run, and the rule is kept as a guard.
- The same applies to the Architect's `backbone` field. An omitted field is a schema failure and never defaults
  to a backbone. (How H3 counts backbones is still PENDING, under A2-6.)

## A2-2 (C3): fixed three rounds, no early stop. RULED (principal, 2026-09-25 20:38Z)

**Found:** the Validator's own threshold was never read (a key mismatch), so it was always the default, and most
runs stopped after round 0. That left 1−ΔC and TDI_lifecycle undefined for most tasks.

**Amended rule:** every lifecycle run executes **exactly three rounds** (round_index 0, 1, 2) with **no early
stop**. The Validator still critiques every round. Its verdict and its chosen threshold are **recorded** on the
step and **do not stop the run**. The lifecycle MSD for a run is the **final round's** (round 2). For a valid run,
first = 0 and last = 2, so **ΔC is defined for every valid run**.

**Text it changes in `PREREGISTRATION.md`:**
- Design, "lifecycle" row: add "exactly 3 rounds, no early stop; Validator verdict/threshold recorded, non-stopping".
- "Per-run components": the one-round case ("the Validator accepted in round 0") can no longer occur in a valid
  run. The "Single-round runs" section is kept as history, with a note that A2-2 makes it unreachable. The
  "undefined" rules for fewer than two LLM steps in a round remain.
- H4/H5: "the lifecycle's final MSD" means the round-2 MSD.

## A2-3 (C2 + C8): agent configuration choices are applied. RULED (principal, 2026-09-25 20:38Z)

**Found:** the DataCurator emits its HVG-count and mito-threshold fields under names the executor does not read,
so the HVG count was always the default. The Architect's HVG count, learning rate, ridge λ and epochs were
resolved but never applied. The Validator's critique deltas on those fields did nothing.

**Amended rule:** the executors **apply** the parsed schema fields. The key names are fixed to match the schemas,
and the parsed proposals are passed to the executors. Precedence for each field is:
**Validator delta > Architect > DataCurator > defaults.** A test drives real `parse_proposal` output through the
executors and asserts that the applied values are the chosen ones.

**Text it changes in `PREREGISTRATION.md`:**
- Design, "lifecycle" row: the agents control the listed fields with the precedence above, and the applied value
  of each field is recorded per run in provenance.
- Convention 1: for the lifecycle, the HVG count is the applied agent choice, not a fixed number. Feature spaces
  therefore vary by run as well as by task.
- The manuscript's description of agent freedom must match (the "PENDING ruling C2/C3/C8" marker in
  `paper/sections/experimental_setup.tex` is resolved by this section).

## A2-4 (C7): N is dropped from the trainer sweep, and the true grid is reported. RULED (principal, 2026-09-25 20:38Z)

**Found:** the N axis never reached the trainer, and the linear backbone ignores seed and max-iterations. Only
about a third of the advertised "54 configurations" were distinct fits.

**Amended rule:** **N is removed** from the trainer sweep. The H1/H2 oracle is the **best over the distinct
backbone × R configurations actually run**. The number of distinct configurations and the seeds used are
**stated** in provenance and in the paper.

**Text it changes in `PREREGISTRATION.md`:**
- Design, "trainer sweep" row: {linear, mlp, scgpt_small} × R ∈ {1,2,3} × seeds. N is removed. The distinct count
  is recorded, not assumed. It is **not written as a number here**: it is fixed by the implemented grid and
  recorded in provenance at implementation time, under the lock commit.
- Convention 3: "Best-of-54" becomes "best over the distinct configurations (oracle)".
- H1/H2 estimator: "min over the 54 configurations" becomes "min over the distinct configurations".

---

## A2-5 (C13): the gene universe for the top-20 DEGs. PENDING principal ruling

_No text until ruled._ The issue is in the decision brief, §2d (C13). The options there are a shared fixed gene
universe for the trainer and lifecycle paths, or a stated difference.

## A2-6 (NEW-1): H3, stated versus executed backbone. PENDING principal ruling

_No text until ruled._ The issue is in the brief, §2c. Note that A2-1 already makes an omitted backbone a schema
failure. What remains open is whether H3 gates on the stated or the executed backbone.

## A2-7 (C25): stratum fill. PENDING principal ruling

_No text until ruled._ The issue is in the brief, §2e. It affects the Design "task draw" row ("the sampler asserts
every stratum is filled exactly").

## A2-8 (C6, prompt and cache-start part): dataset/modality in prompts, and the initial cache state. PENDING principal ruling

_No text until ruled._ The issue is in the brief, §2f. The dataset-keyed cache and the per-step `cache_hit` flag
were already fixed as implementation under C6-key and are not part of this amendment.

## A2-9 (C20): FWER bracket wording. PENDING principal ruling

_No text until ruled._ The issue is in the brief, §2g. It affects the H4 multiplicity paragraph in
`PREREGISTRATION.md` (the stated bracket assumes the components are not negatively dependent).

---

## Not part of this amendment

- Decision 1 in the brief (the P0-P5 phase boundary / Hash D) is a process approval, not a pre-registration
  change.
- The 17 ACCEPT-FIX-NOW findings (committed 040f022…0f85e29) do not change the measurand and are not amended here.

## Lock checklist (used once, when A2-5 to A2-9 are ruled)

1. Every PENDING section is replaced by ruled text, and no PENDING marker remains.
2. The text is folded into `PREREGISTRATION.md` in one `prereg(perturb-seq-eval): AMENDMENT 2` commit, before any
   data exists.
3. Then the measurand fixes go through a quality gate, and then the #283 sweep runs from the receipted SHA, which
   pins that prereg revision.
