---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-09-24T20:18
status: created
priority: high
size: task
subject: "Build status — perturb-seq-eval: at the sweep gate (key absent, trunk unpushed); 2 rulings needed before spend"
in_reply_to: null
---

# Build status — perturb-seq-eval: at the sweep gate (key absent, trunk unpushed); 2 rulings needed before spend

workstream: perturb-seq-eval
phase: P5 (at the sweep gate)
iterations_done: 0 gated / 5 phases built (P0-P4 + T22), all WIP-committed, UNGATED
iterations_total: 5 + sweep
percent_complete: build 100% of non-sweep tasks; 0% gated
blockers: (1) trunk push — every /iteration-complete blocked by stale-revert-check vs unpushed main; (2) OPENROUTER_API_KEY absent — preflight refuses the whole run (C-KEY-1, #235)
next_action: principal pushes main + provisions the key; you rule on Q1-Q3 below before T24 spends

BUILT (suite 466 passed, 0 skipped, 0 failed; CPU torch local == Modal torch==2.14.0):
- A6/A1: crc32 strata, pure build_task_lists (sorted subsets), app_v05_lifecycle_only.py deleted
- A2: seed -> LLM cache key, agent pool, BackboneTrainConfig, sweep
- A4/D1: '_' doublets as 2-tuples, random-gene fallback deleted, held-out remap raises, exact 15+5 fill (old sampler gave 4 doublets)
- #227 HVG: train-only per held-out task in Adamson single-file, Adamson COMBINED (also leaked, and silently dropped targets), Norman, lifecycle; targets force-included; hvg_n/n_forced/mode/n_params recorded
- A3/D4: ChatResult.model_id; step source llm|fallback|mock; only runtime client errors may fall back (TypeError now propagates)
- Provenance record 0 in both JSONLs + provenance.json: git sha/dirty, 20 resolved kwargs, RESOLVED lib versions, dataset digests, task plan, known_limitations incl. the DEG-eval-genes convention (#227)
- Analyser: raises on task-set / run_id / git_sha mismatch (v0.5.0 artifacts now refused: 34 only-trainer vs 34 only-lifecycle); entropy over llm rows per role; fallback rows refuse the summary (C-KEY-2)
- A5: optimizer one-hot from the space (27 distinct, was 9). A7: fail-closed fetch; ALL FOUR digests pinned after a CPU-only Modal pass (cents) — every file matched Zenodo record 13350497 on size + MD5 first (evidence qgr/evidence/T20-dataset-digests.txt)
- T22 preflight: one PreflightError listing all failures; lifecycle-skip-on-missing-key REMOVED; BackboneUnavailableError re-raised through every except frame (swallow trace in the WIP commit message)
Red-then-green evidence: qgr/evidence/C-RG-1-*, C-RG-2-*, C-TORCH-3-skip-guards-fire.txt.

QUESTIONS BEFORE SPEND (found by T22's trace; I did not widen scope to fix them):
Q1. app_v05's trainer loop and lifecycle loop still convert ANY other exception (incl. programming errors) into an error record with inf MSD and keep going. Under your "guilty until proven loud" rule that is a silent path. Options: (a) any non-OOM exception aborts the run (status failed); (b) keep per-cell error records but the analyser refuses a summary with ANY error record unless allow_partial. Recommend (b) — a single CUDA OOM on one config should not burn a $5 run, but must not be silent. ~15 lines + tests.
Q2. app_v05 trace reader skips unparseable JSONL lines without counting them (:444-447). Recommend: count and record in provenance; analyser refuses if > 0. ~5 lines.
Q3. Out of sweep scope, listed only: app_lifecycle.py:144 / app_lifecycle_optimizer.py:143 still swallow BackboneUnavailableError; scripts/fetch_adamson.py downloads via urlretrieve bypassing digest pins; paper-fill (scripts/paper/fill_v050_numbers.py) should refuse any summary whose status != ok; 5 pre-existing F401s in live_smoke.py / collect_traces.py.

SWEEP ESTIMATE (T23 will re-check live): 41 tasks (21 Adamson + 15+5 Norman) x 54 trainer configs x 3 seeds ~ 2,214 cells (+14% vs 1,944) + 123 lifecycle runs; ~4 A100-h ~ $5-6 against the $28 cap; timeout 8 h. Memory: loaders now keep all genes (float32) — Norman ~6 GB resident (estimated) vs 32 GB on the function.
next_handoff: cto rule Q1-Q2
