# DRAFT — Pre-registration AMENDMENT 2 (v0.6.0 sweep) — NOT LOCKED

> **Status: DRAFT, revision 4 (CTO #395, #421, #425, #427).** Nothing here is in force. `projects/perturb-seq-eval/paper/PREREGISTRATION.md`
> is unchanged. The pre-registration is amended **once**, before any v0.6.0 data exists, and only after **all**
> the PENDING sections below are ruled. At that point this text is folded into `PREREGISTRATION.md` in a single
> `prereg(...)` commit, and the sweep's provenance pins that commit. Nothing that changes the measurand is
> implemented before the lock.
>
> **Nine sections are ruled (A2-1 to A2-9). Two are PENDING the principal: A2-10 and A2-11**, both raised by the
> CTO's mathematical re-check of the entropy formulations (2026-09-26, on the principal's instruction;
> `workstreams/perturb-seq-eval/qa/_adhoc/2026-09-26-entropy-formulation-review.md` on main).
>
> Why this lives here: `qgr/**` is excluded from the receipt diff-hash, so committing the draft does not stale
> a receipt. The P0-P5 phase boundary is closed (principal approval via CTO #421; boundary commit with the
> derived receipt cfe931f).
>
> Sources: the P0-P5 quality gate (findings: `qgr/evidence/qg-p0p5-findings-scored.md`; triage:
> `qgr/evidence/qg-p0p5-triage.md`), the principal decision brief `qgr/principal-decisions-p0p5.md`, the principal's
> rulings (2026-09-25 20:38Z in session b6e15309; 2026-09-26 via CTO #421), and the CTO's entropy-formulation review.

## Why an amendment is needed

The P0-P5 quality gate found ten items where the code as built does not measure what `PREREGISTRATION.md`
describes, or where the description is incomplete. The CTO's formulation review then found two places where a
pre-registered formula is well-defined but ill-conditioned for the hypothesis it serves. Fixing any of them
changes the measurand, so each needs a principal ruling, written here before data, rather than a silent fix.

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
  to a backbone. How H3 counts backbones is ruled under A2-6.

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

## A2-5 (C13): one gene universe for the top-20 DEGs, shared by both paths. RULED (principal, 2026-09-26, CTO #421, 2d option a)

**Found:** the 20 evaluation genes are chosen inside each model's HVG columns. The trainer path
(`experiments.heldout.select_for_task`, a fixed HVG count) and the lifecycle path (the DataCurator's applied HVG
count, A2-3) select different HVG sets, so H1/H2 and H4/H5 compute "MSD@top-20-DEG" over different genes for the
same task. The numbers are then not the same quantity.

**Amended rule:** for each held-out task, the 20 evaluation genes are selected **once**, from **one fixed gene
universe shared by the trainer and the lifecycle paths**: the dataset's full post-QC gene axis (the loader's gene
set after the label contract, identical for every task of a dataset and for every model). The ranking is
unchanged (convention 2: the 20 genes with the largest absolute mean difference between the held-out
perturbation's cells and control cells, selected using the held-out cells). The selected 20 genes are
**force-included in every model's feature set in both paths**, the way the target genes already are under
convention 1, so that each model can predict them and the MSD in H1/H2 and in H4/H5 is computed over the
identical genes. The per-task list of the 20 genes is written to provenance, and a test asserts that the trainer
and lifecycle records for a task carry the same list.

**This is not new leakage.** The 20 genes are already chosen using the held-out perturbation's own mean shift,
the CPA/GEARS convention that convention 2 declares as a stated limitation. Force-including them changes feature
**availability** (the model can predict them), not label **exposure**: no held-out expression value enters training,
and the declared DEG convention is neither widened nor worsened by it.

**Text it changes in `PREREGISTRATION.md`:**
- Convention 2: add the universe (full post-QC gene axis), the once-per-task selection, and the shared list.
- Convention 1: the force-included set becomes "the target gene(s) and the task's 20 evaluation genes";
  `hvg_n_forced` records the count.
- "Required alongside each gate": H1/H2 and H4/H5 both cite the same per-task evaluation-gene list.

## A2-6 (NEW-1 + backbone part of C1, and review F2): what H3 measures. RULED (principal, 2026-09-26, CTO #421, 2c option c)

**Found (NEW-1):** each Architect step records the backbone the Architect *stated*; the backbone that actually
*ran* can be overridden by the Validator's fixed rotation rule, which is also shown to the model in the next
prompt. **Found (C1, backbone part):** an omitted `backbone` field, or a name outside the menu, defaulted to one
backbone and was counted as an LLM choice. **Found (review F2):** `h3()` hard-codes the ceiling ln 3, which is
only the ceiling if the menu is exactly three; and the plug-in entropy is biased low by about (K−1)/(2N) nats.

**Amended rule:**
- **H3 gates on the STATED backbone**: the Architect's own `backbone` field on every Architect step with
  `source == "llm"`. An omitted field, or a stated name that is not on the menu, is a **schema failure** under
  A2-1 (the step falls back, the run is invalid) and is **never defaulted and never counted**.
- **The executed backbone is recorded and reported alongside**, descriptively: every Architect step also records
  the backbone that ran after the Validator's delta (`backbone_used`), and the H3 output reports the executed
  pick counts and the number of steps where executed ≠ stated. It does not gate.
- **The menu is pinned:** the Architect is offered exactly three backbones, `{linear, mlp, scgpt_small}`
  (`llm_agent_pool._architect_prompt` schema line; the backbone registry), on every step; the Validator's
  rotation is over the same three. **The ceiling is derived from the pinned menu, ln|menu| = ln 3 ≈ 1.099 nats**,
  and `h3()` reads it from the menu constant, not from a literal. Any change to the menu is a measurand change.
- **Bias:** H3's headline is the plug-in (maximum-likelihood) entropy, adequate at the pooled N (about 0.007 nats
  low at N = 138, K = 3). For any breakdown with **N < 50** (per `model_id`, per task) the Miller–Madow-corrected
  value, H + (K−1)/(2N), is reported beside the plug-in value.
- **Interpretation of the gate:** the gate is a threshold on the **entropy of the stated-pick distribution**,
  not a rule about any single share. For a fixed top share the entropy is largest when the remainder splits evenly
  and smallest when the remainder sits in one option, so the gate's top-share boundary is a band: with an **even
  remainder** the gate passes below **86.08%** on the top backbone (86/7/7 = 0.502 nats); with the **remainder in one
  option** it passes only below **80.03%** (80/20/0 = 0.500 passes; 81/19/0 = 0.486 and 82/18/0 = 0.471 fail).
  For reference, 80/10/10 = 0.639 nats and 70/15/15 = 0.819 nats are both above the gate. A reader must apply the
  entropy, never a top-share rule.
- **H3 is a statement about the pool** of all LLM-sourced Architect steps across tasks, seeds and rounds, not about
  any single task, seed or round. The hypothesis sentence says so.

**Text it changes in `PREREGISTRATION.md`:**
- H3 row: "the empirical distribution of the Architect's **stated** `backbone` over all Architect steps with
  `source == "llm"`, pooled across tasks, seeds and rounds (a statement about the pool); menu {linear, mlp,
  scgpt_small}, ceiling ln 3 derived from the menu; the executed backbone is reported alongside and does not gate."
- "Required alongside each gate", H3: add executed pick counts, the stated≠executed count, and the Miller–Madow
  value for any breakdown with N < 50.
- Convention 4: a stated backbone outside the menu is a schema failure (with A2-1).

## A2-7 (C25): the task draw is described as it runs. RULED (principal, 2026-09-26, CTO #421, 2e option a)

**Found:** the Design "task draw" row says "the sampler asserts every stratum is filled exactly". The code draws up
to the per-stratum count from each stratum, tops the draw up to the exact pool total from the remaining labels,
and asserts the **total**, not the per-stratum fill.

**Amended rule (text only; the task set is unchanged):** the draw is described as implemented in
`experiments.v05_tasks.build_task_lists` and `data.subsample.stratified_subsample`:
- **Adamson:** eligible single-gene constructs are pooled across the three subsets and binned into 3 quantile bins
  of mean |Δlog1p| on the target gene. Up to 7 labels are drawn per bin with `numpy.random.default_rng(2026)`. A
  bin with fewer than 7 eligible labels contributes all of them, and the draw is **topped up to exactly 21** by a
  seeded permutation of the sorted remaining labels (or trimmed to the sorted prefix if over). The per-bin
  eligible-pool sizes are written to provenance (`adamson_bin_<b>`), so an uneven fill is visible.
- **Norman:** singletons and doublets are drawn separately. Each pool is stratified by a CRC32-derived stratum
  (never the process-salted `hash`), drawn per stratum, then topped up or trimmed to exactly 15 singletons and 5
  doublets by the same rule.
- **The total per pool is asserted** with an explicit `raise` (not `assert`, so `python -O` cannot strip it); a
  pool smaller than its requested count refuses the run in preflight. The resolved plan (tasks, strata,
  eligible-pool sizes) is written to provenance.

**Text it changes in `PREREGISTRATION.md`:** Design, "task draw" row, replacing "the sampler asserts every
stratum is filled exactly" with the description above.

## A2-8 (C6, prompt and cache-start part): dataset and modality in every prompt; empty, version-namespaced cache. RULED (principal, 2026-09-26, CTO #421, 2f option a)

**Found:** prompts name the task but not the dataset or the modality (CRISPRi versus CRISPRa), so the model
cannot condition on either. There was no rule on the LLM cache's initial state: a warm cache replays earlier
replies (now flagged per step by `cache_hit` and keyed by dataset, under C6-key, which is not part of this
amendment).

**Amended rule:**
- **Every prompt for every role states the dataset and its modality** (Adamson 2016: K562, CRISPR interference;
  Norman 2019: K562, CRISPR activation) in the system preamble. The prompt text is part of the cache key, so this
  change alone invalidates every earlier cache entry.
- **Each pre-registered version starts with an empty, version-namespaced LLM cache.** The cache root is
  `<cache_dir>/<prereg_version>/`, where `prereg_version` is a string constant pinned in this amendment at the
  lock (`v0.6.0-a2`) and recorded in provenance. The preflight records the number of entries in that namespace at
  sweep start; for the pre-registered run it **must be 0**, and every step's `cache_hit` must be `false`. A run
  that starts on a non-empty namespace, or records any cache hit, is a **replay**, which the analyser reports as
  such and does not treat as the pre-registered run.

**Text it changes in `PREREGISTRATION.md`:** Convention 5 (LLM condition): add the prompt content rule and the
empty-cache rule; "Run record": add `prereg_version`, the cache-entry count at start (must be 0) and the cache-hit
count (must be 0).

## A2-9 (C20): the FWER bracket states its assumption and adds a permutation bound. RULED (principal, 2026-09-26, CTO #421, 2g option a)

**Found:** the H4 multiplicity paragraph brackets the six-test gate's null false-positive rate as 2.35% – 5.81%
(components with identical ranks; components independent). That bracket assumes the ranks of ACE_norm and 1−ΔC
are **not negatively dependent** under the null. Under negative dependence the rate can exceed the upper end.

**Amended rule (text plus one cheap local run):** the paragraph states the assumption, and the table gains a third
row, **components with reversed ranks** (the negative-dependence extreme), computed by the same script
(`scripts/local/prereg_null_fwer.py`, seed 2026, the pre-registered estimator `_rho`), so that the reported range
is a bound over the whole dependence family rather than over its non-negative half. The value is **not written as
a number here**: it is produced by the script and written into the table under the lock commit. If A2-10 or
A2-11 changes a component, the whole table is recomputed once, under the lock commit.

**Text it changes in `PREREGISTRATION.md`:** the "H4 gate and its multiplicity" paragraph and its table.

---

## A2-10 (review F1): the ACE_norm feature for H4/H5. PENDING principal ruling

**Found (CTO review, 2026-09-26):** `metrics.ace_norm` takes the softmax of confidences in [0, 1] at τ = 1 and
divides the entropy by ln N. Because the logits live in a unit interval, no two softmax probabilities can differ
by more than a factor of e, so the most concentrated vector possible, (1, 0, …, 0), is still near-uniform.
Attainable minimum over [0, 1]^N: about 0.84 (N = 2), 0.89 (N = 3), 0.93 (N = 5). For a five-role round the
pre-registered feature occupies at most about **[0.92, 1.00]**, eight percent of its nominal range. The
pre-registration notes the narrow band and says rank statistics are unaffected; that holds only for noiseless
confidences. LLMs report rounded confidences (0.7, 0.8, 0.9), so the band produces ties and near-ties, and
Spearman ρ over about 20 tasks is then decided by tie-breaking of a quantisation artefact. H4's ACE_norm test is
under-powered by construction, and H5 fits ridge weights to a feature with no spread. `metrics.ace_d` (direct
simplex projection, no temperature) already exists, has full range [0, 1] on the same inputs, and its docstring
says why.

**Option (a), recommended by the CTO:** pre-register `metrics.ace_d(C(last))` as the **ACE_norm feature** used
by H4 (component test), H5 (ridge input) and TDI_lifecycle. The softmax version `metrics.ace_norm` is reported
**descriptively only**, beside it. The TDI_lifecycle weights (7/12, 5/12) are **carried over unchanged**, not
re-fitted (review F4). H5's standardisation is unchanged. Two guards are stated with it: confidences are in
[0, 1] by A2-1, so `ace_d`'s negative-input error is unreachable for a valid run; a round whose confidences sum to
zero is **undefined** (the metric's all-zero → 0.0 convention is not used), consistent with "undefined, not
imputed".

**Option (b):** keep the softmax τ = 1 `ace_norm` as pre-registered, stating the attainable band [0.92, 1.00] for
N = 5 and accepting that ties from rounded confidences may decide the ACE_norm rows of H4 and the H5 fit.

**Not pending (enforcement of an existing rule, either option):** `metrics.ace_norm` and `metrics.ace_d` both
return 0.0 for N ≤ 1, while the pre-registration says a round with fewer than two LLM-sourced steps is
**undefined**. `preregistered.per_run_components` is the one that enforces "undefined" (via `_round_vector`, which
returns `None` with the reason `"< 2 required"` before any metric is called); the metric's 0.0 must never reach a
component. The test that pins this is named here: `tests/test_preregistered.py::test_fallback_only_final_round_is_undefined_not_imputed`
(zero LLM steps, existing) and `tests/test_preregistered.py::test_one_llm_step_round_is_undefined_not_zero`
(exactly one LLM-sourced step in the final round → `ace_norm is None` with the reason, never 0.0; added in the
fix quality gate).

**Text it changes in `PREREGISTRATION.md` (if a):** "Per-run components", ACE_norm definition; the "narrow band"
paragraph is replaced by the reason for the change; H5 ridge note ("ACE_norm's range is narrow") is removed;
"Required alongside each gate" adds the descriptive softmax value.

## A2-11 (review F3): the sign of ΔC. PENDING principal ruling

**Found (CTO review, 2026-09-26):** 1−ΔC = 1 − min(max(ΔC, 0), 1). Every run whose confidence **fell** across
rounds (ΔC < 0) maps to exactly 1.0, tied with every run whose confidence stayed flat (ΔC = 0). A falling
confidence is arguably the strongest difficulty signal the trace carries; the clip erases it and creates a tie
block at the top of the ranking. With A2-2 (three fixed rounds) the single-round tie source is already gone.

**Option (a), recommended by the CTO:** pre-register the **unclipped** quantity, 1−ΔC without the lower clip
(range [0, 2]; equivalently −ΔC for ranking), as the second H4 component and the H5 ridge input, and use it in
the Spearman tests. The clipped value is reported descriptively beside it. For TDI_lifecycle, the unclipped value
enters the weighted sum and the outer clip₀₁ is **removed** (Spearman is rank-based and the ridge standardises, so
neither needs the [0, 1] range; keeping the outer clip would re-create the tie block inside TDI). Weights carried
over unchanged (review F4). **Consequence, stated so it is chosen with eyes open:** TDI_lifecycle's range becomes
**[0, 17/12 ≈ 1.417]** (= 7/12 · [0, 1] + 5/12 · [0, 2]) instead of [0, 1]; it is no longer an index on [0, 1],
and the paper must describe it as a score with that range. **The bound holds under both A2-10 options, checked:**
`metrics.ace_norm` (softmax) and `metrics.ace_d` are both normalised by ln N to a nominal [0, 1], so the
7/12 · [0, 1] term and the 17/12 upper bound are the same under (a) and (b). Only the *attainable* minimum differs:
under (a) the floor 0 is attainable; under (b) ACE's attainable band (about [0.92, 1] at N = 5) lifts TDI_lifecycle's
attainable floor to about 7/12 · 0.92 ≈ 0.54. Neither option changes the upper bound. Dropping the outer clip is
not a separate decision: option (a) is incoherent without it (CTO #425 d).

**Option (b):** keep the clipped 1−ΔC as pre-registered and state that falling-confidence runs tie with flat runs
at the top of the ranking.

**Text it changes in `PREREGISTRATION.md` (if a):** "Per-run components", the 1−ΔC and TDI_lifecycle
definitions; "Required alongside each gate" adds the descriptive clipped value.

---

## Not part of this amendment

- Decision 1 in the brief (the P0-P5 phase boundary / Hash D) was a process approval, not a pre-registration
  change. It is closed (principal via CTO #421; boundary commit with derived receipt cfe931f).
- The 17 ACCEPT-FIX-NOW findings (committed 040f022…0f85e29) do not change the measurand and are not amended here.
- The dataset-keyed LLM cache and the per-step `cache_hit` flag (C6-key) are implementation, already committed.

## Lock checklist (used once, when A2-10 and A2-11 are ruled)

1. Every PENDING section is replaced by ruled text, and no PENDING marker remains.
2. The FWER table (A2-9) is recomputed once against the final component definitions, and `prereg_version` (A2-8)
   is pinned.
3. The text is folded into `PREREGISTRATION.md` in one `prereg(perturb-seq-eval): AMENDMENT 2` commit, before any
   data exists.
4. Then the measurand fixes go through a quality gate (commit first, then sign: CTO #392), and then the #283 sweep
   runs from that receipted SHA, which pins that prereg revision (conditions unchanged: `model_id` per call,
   $12 stop-and-report, $28 kill).
