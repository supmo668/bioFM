# perturb-seq-eval — principal decisions after the P0-P5 quality gate

_Prepared 2026-09-25 by the perturb-seq-eval agent for the CTO to relay (CTO #392). Written in shapes, not values._
_Receipt: `qgr/…-qgr-phase-complete-20260925-1301-7d3d659.md` (derived from 4a2948a). Its Hash D is recorded as PENDING your approval._

## RULED by the principal — 2026-09-25 20:38Z (AskUserQuestion in session b6e15309, verified from its transcript)

These are GIVEN. Do not re-ask them. They go into pre-registration amendment 2.

- **C1 (2a) — required verbalised confidence:** every role's schema and prompt require a `confidence` in [0,1]. A missing or non-numeric value is a schema failure: the step falls back and the run is invalid (C-KEY-2). It is never imputed.
- **C3 (2a) — FIXED 3 rounds, no early stop.** This differs from the recommendation below; the ruling governs. The Validator still critiques, and its verdict and chosen threshold are recorded but do not stop the run. Lifecycle MSD is the final round's. ΔC is defined for every run.
- **C2 + C8 (2b) — APPLY them.** Fix the key names, pass the parsed schemas to the executors, and use the precedence Validator delta > Architect > DataCurator > defaults. A test must drive real parse_proposal output through the executors.
- **C7 (2d, first half) — DROP N from the trainer sweep.** The oracle is "best over the distinct backbone × R configurations", with the distinct count and the seeds stated.

**STILL OPEN:** Decision 1 (phase boundary / Hash D); 2c NEW-1 (H3 stated vs executed); 2d C13 (DEG gene universe); 2e C25 (stratum-fill wording); 2f C6 (prompt dataset/modality + cache-start); 2g C20 (FWER wording).

## Decision 1: approve the P0-P5 phase boundary (Hash D)

What the phase delivered:

1. The v0.6.0 pre-registered pipeline (H1-H5 estimators, gates, provenance pins) was built through P0-P5 and reviewed by a four-reviewer quality gate plus a scorer. That review produced 27 findings and 24 survived the scorer's confidence threshold.
2. All 17 implementation-only findings are fixed in commits `040f022…0f85e29`. None of them changes what the experiment measures. They cover error taxonomy, dataset-qualified task keys, the LLM cache key and cache-hit flag, GPU use, fail-closed pre-registration pins, a validated output path, a $12 stop-and-report, docs and CLI.
3. The evidence was re-derived on a verified tree. GREEN: 748 tests pass, with the tree byte-identical before and after the run. RED: at the pre-fix commit, 68 of the new tests fail (24 of them on behaviour) and 6 negative controls pass.
4. Deviations the CTO accepted: one commit covers 11 findings that share files; the commit was made before signing, because the receipt hashes committed code; the format check is scoped to the working tree.
5. **The `--boundary phase` commit is held for your approval.** Approving it closes P0-P5. It does **not** authorise the sweep (see Decision 2).

**Asked of you:** approve or reject the P0-P5 phase boundary.

## Decision 2: the 10 findings that change the measurand (pre-registration amendment 2)

These were deliberately left unfixed. Each one changes what the pre-registered experiment measures, so fixing it silently would be a post-hoc change to a locked analysis. Each needs your ruling, and every ruling below goes into **pre-registration amendment 2** before any data is collected.

### 2a. H4/H5 inputs are degenerate: C1, C3 (one decision: make the trace features real)
- **C1:** no prompt or schema asks the Architect for a `confidence`. A missing value silently defaults to a constant, so in the earlier artifact almost every LLM step carries the same value, and ACE_norm (an H4/H5 input) is near-constant. **Measurand:** H4/H5 would test a constant.
- **C3:** the Validator reads a threshold key that the schema never emits, so the threshold is always the default. Most runs stop after a single round, which leaves 1-ΔC and TDI_lifecycle undefined for most tasks. **Measurand:** H4/H5 would be mostly unevaluable.
- **Options:** (a) ask for confidence explicitly in the schema. Treat a missing or non-numeric confidence as a non-LLM (fallback) step, never a default. Read the Validator threshold key the schema actually emits. (b) Keep the current behaviour and amend H4/H5 to say they are expected to be degenerate.
- **Recommendation: (a).** Without it, the H4/H5 result is an artifact of the defaults.
- **Amendment 2:** yes (how estimator inputs are defined and excluded).

### 2b. Agent choices that are never applied: C2, C8 (one decision: do the agents control these knobs?)
- **C2:** the DataCurator emits HVG-count and mito-threshold fields under names the executor does not read, so the HVG count is always the default.
- **C8:** the Architect's HVG count, learning rate, ridge λ and epochs are resolved but never applied. The Validator's critique deltas on them do nothing, and an "Architect HVG entropy" is reported for a choice that has no effect.
- **Measurand:** the lifecycle MSD (the H4 target) and the paper's description of agent freedom.
- **Options:** (a) wire the fields through, so the agents really control them. The lifecycle MSD then reflects those choices. (b) Keep them fixed, state in the pre-registration and paper that these fields are advisory or unapplied, and drop the HVG-entropy metric.
- **Recommendation: (a)** if the paper keeps its claim of agent freedom, otherwise (b). The two must not diverge. (The paper already carries a "PENDING ruling C2/C3/C8" marker.)
- **Amendment 2:** yes.

### 2c. What H3 measures: NEW-1, plus the backbone part of C1 (one decision)
- **NEW-1:** steps record the backbone the Architect *stated*. The backbone that actually *ran* can be overridden by the Validator's fixed rotation rule, which is also shown to the model in the next prompt.
- **C1 (backbone part):** an omitted backbone field defaults to one backbone and is counted as an LLM choice.
- **Measurand:** H3 entropy.
- **Options:** (a) gate on the executed backbone. (b) Gate on the stated backbone, with omitted fields excluded rather than defaulted. (c) Gate on stated, report executed as descriptive.
- **Recommendation: (c).** H3 asks whether the Architect exercises its choice, which is the stated backbone. Omitted fields are excluded, and executed backbones are reported alongside so the override is visible.
- **Amendment 2:** yes.

### 2d. The H1/H2 oracle and a shared gene universe: C7, C13 (two linked decisions)
- **C7:** the N sweep axis never reaches the trainer, and the linear backbone ignores seed and max-iterations. Only about a third of the pre-registered "54 configurations" are distinct. **Measurand:** the H1/H2 "oracle best-of-54" describes something that does not run.
  - **Options:** (a) wire N and seed through, so 54 distinct configurations exist. This costs more compute, within the $12 stop and $28 kill limits. (b) Amend the text to "best of the distinct configurations actually run", with the count stated.
  - **Recommendation: (b)** unless you want the N axis as a studied factor. It is honest and costs nothing.
- **C13:** the top-20 DEGs are chosen inside the HVG columns. The trainer and the lifecycle use different HVG sets, so H1/H2 and H4 compute MSD over different gene sets. **Measurand:** comparability of H1/H2 with H4.
  - **Options:** (a) pick the top-20 DEGs from one fixed gene universe shared by both paths. (b) Amend the text to state that the gene sets differ.
  - **Recommendation: (a).** Otherwise the "held-out error" numbers are not the same quantity.
- **Amendment 2:** yes, for both.

### 2e. The task-set draw: C25
- **C25:** the pre-registration says every stratum is filled exactly, but the code tops up bins and checks only pool totals. **Measurand:** which tasks enter the study.
- **Options:** (a) amend the text to describe the top-up that actually runs, keeping the task set. (b) Change the draw to fill strata exactly, which changes the task set.
- **Recommendation: (a).**
- **Amendment 2:** yes (text).

### 2f. LLM input and cache start: C6 (prompt and cache-start part only)
- **C6:** prompts omit the dataset and the modality (CRISPRi versus CRISPRa). There is also no rule on whether a run starts with an empty LLM cache. The cache is now dataset-keyed and every step flags cache hits (fixed under C6-key), but a warm cache still replays earlier replies. **Measurand:** the LLM input, and whether replies are fresh.
- **Options:** (a) add dataset and modality to the prompts, and start each pre-registered version with an empty, version-namespaced cache. (b) Keep the prompts as they are and allow a warm cache, reporting the cache-hit fraction.
- **Recommendation: (a).**
- **Amendment 2:** yes.

### 2g. FWER wording: C20
- **C20:** the H4 FWER is stated as a bracket that assumes the two components are not negatively dependent. Under negative dependence the rate can exceed the bracket's upper end. **Measurand:** none (text only).
- **Options:** (a) amend the wording to state that assumption, and report a permutation bound under negative dependence. (b) Amend the wording only.
- **Recommendation: (a)**, wording plus the extra permutation run (cheap, local).
- **Amendment 2:** yes (text).

## Why the #283 sweep cannot run until these are ruled

The sweep *is* the pre-registered measurement. Any of these fixes applied after it would change the measurand after the data exist, which the pre-registration forbids. Running it now would also spend the budget ($12 stop, $28 kill) on data where H4/H5 are degenerate (2a) and H3 measures an unintended quantity (2c). The order is:

1. Rulings.
2. Amendment 2, committed before any data.
3. The fixes, through a quality gate.
4. The #283 sweep from that receipted commit.

**Asked of you:** one ruling per group, 2a to 2g. Any of the recommendations can be accepted as written.
