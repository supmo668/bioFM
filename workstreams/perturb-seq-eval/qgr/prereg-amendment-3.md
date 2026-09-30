# Pre-registration AMENDMENT 3 — source record (folded into projects/perturb-seq-eval/paper/PREREGISTRATION.md)

Rulings taken from the principal via AskUserQuestion in session b6e15309 on 2026-09-28 during the amendment-2 fixes quality gate (base 3bf2a9a).

## Amendment 3 (`prereg_version` = `v0.6.0-a3`): locked 2026-09-28, before any v0.6.0 data

Raised by the quality gate on the amendment-2 measurand fixes (findings QG-2, QG-6, QG-7, QG-9; five reviewers,
scored ≥ 80) and ruled by the principal on 2026-09-28. Two further gate findings (QG-1: the analyser must report a
replay run and never license gates on it; QG-10: the analyser cites the per-task evaluation-gene list beside H1/H2
and H4/H5 and refuses a trainer/lifecycle mismatch) are **enforcement of A2-8 and A2-5 as written**, implemented in
the same gate, and change no text. Where this section and any earlier text differ, **this section governs**.
Because this is a new pre-registered version, the LLM cache namespace is `<cache_dir>/v0.6.0-a3/` and starts empty
(A2-8 rule, unchanged).

### A3-1 (QG-2): the DataCurator's mito-QC threshold is recorded, not applied. RULED (principal, 2026-09-28)

**Found:** A2-3 says the executors apply the parsed schema fields and names the mito threshold among them. No
loader provides a per-cell mitochondrial fraction for either dataset, so no cell filter exists; the executor only
logs the value, while the per-round record filed it as applied.

**Amended rule:** `qc_mito_max` is resolved by the precedence rule and **recorded** per round with its value and
source, and the record carries an explicit per-field `applied` flag: `applied: false` for `qc_mito_max`, with the
reason (`architect_dispatch.NOT_APPLIED_FIELDS`), `applied: true` for every field an executor consumes. The paper
states that the mito threshold is a recorded agent choice with no effect on the data. Implementing the filter would
change the cell set per run and interact with A2-5's per-run gene ranking; it is **not** done for v0.6.0.

### A3-2 (QG-6): the Trainer role is a precedence tier. RULED (principal, 2026-09-28)

**Found:** A2-3 names four tiers. The Trainer role also states `lr`, `epochs` and `ridge_lambda`, which are parsed
schema fields A2-3 says to apply; the text gave them no tier.

**Amended rule:** precedence for each field is **Validator delta > Architect > DataCurator > Trainer > defaults**
(`architect_dispatch.APPLIED_FIELDS`). A Trainer statement applies only when no higher tier states the field.
"Validator delta" is the rule-based `score_and_gate` critique delta (A2-3 Found); the LLM Validator's own
`critique.suggested_next_config_delta` is recorded and **not applied**, and the paper says so.

### A3-3 (QG-9): the Validator's threshold is required. RULED (principal, 2026-09-28)

**Found:** when the LLM Validator did not state `dynamic_threshold_msd`, the schema default 0.1 was recorded as its
"chosen threshold" (A2-2) and decided accept/reject, which decides whether a delta enters the next round's
applied configuration — an imputed value gating the measurand (against A2-1).

**Amended rule:** `dynamic_threshold_msd` is a **required** Validator field (range [0.02, 0.3]); an unstated,
non-numeric or out-of-range value is a **schema failure** under A2-1 (the step falls back, the run is invalid).
The recorded threshold is therefore always a stated one.

### A3-4 (QG-7): what "the number of distinct configurations" counts. RULED (principal, 2026-09-28)

**Found:** A2-4 states the count but not its definition; two readings existed (distinct fits including seeds = 19;
distinct (backbone, R) = 7, since the linear backbone ignores R and seed).

**Amended rule:** the stated count is the number of **distinct (backbone, R) configurations, seeds as replicates,
an R- and seed-invariant backbone counting once**: for {linear, mlp, scgpt_small} × R ∈ {1, 2, 3} × seeds
{2026, 2027, 2028} that is **7** per task (`trainer_grid.n_distinct_configs_per_task`; the analyser's
`n_configs_tried` uses the same definition). The 19 distinct fits and 27 records per task are recorded as
supporting detail (`n_distinct_fits_per_task`, `n_records_per_task`). The oracle rule is unchanged: the minimum
over every finite record.
