# QG raw findings — c46cd22..HEAD, perturb-seq-eval (P0-P5). Deduplicated by me; IDs are consolidated.
Scope root: projects/perturb-seq-eval/. Evidence artifact: artifacts/v0.5.0/lifecycle_runs.jsonl (same code paths).

C1 [code F1, design F1] CRITICAL llm_agent_pool.py:186 — missing `confidence` silently defaulted to 0.7 on a source="llm" step; no prompt/schema asks for confidence (Architect schema text, _simple_prompt, proposal_schema.py:59-86). v0.5.0: 684/690 steps == 0.7. H4/H5 inputs (ACE_norm, dC) become constant -> degenerate. Non-numeric confidence raises ValueError outside FALLBACK_EXCEPTIONS (aborts). Also ArchitectProposal.backbone defaults "linear" -> omitted field counted as an LLM choice in H3.
C2 [code F2, design F3] HIGH data_curator_exec.py:36-37 — executor reads n_top_hvg/pct_mito_max; schema emits hvg_count/qc_mito_max -> HVG always 500 (probe: hvg_count 5000 -> 502). Stub pool uses executor keys so tests pass.
C3 [code F3, design F3] HIGH loop.py:307-311 — reads threshold_msd (default 0.5); schema emits dynamic_threshold_msd -> Validator threshold always 0.5; v0.5.0 93/108 runs single-round -> 1-dC/TDI undefined for most runs (H4 degeneracy).
C4 [code F4, design F4, test T3] HIGH trainer_exec.py:37-43 — `except Exception` around backbone.fit bypasses #245 taxonomy; programming error -> final_msd=inf with no error fields; analyser silently drops it. Probe confirmed.
C5 [code F8, design F2, test T1] HIGH e_v05_real_traces.py:87-112,149-158 — trainer grouping + task-set check key on bare `task`; SNAI1 and SPI1 are single-gene tasks in BOTH datasets (raw-label inventory) -> H1/H2 cross-contamination, task credited to one dataset.
C6 [code F9, design F2, security S-4] MEDIUM openrouter_client.py:164-180,245-260 — LLM cache key lacks dataset + run/version; persistent shared cache on biofm-cache volume; no per-step cache_hit flag -> Norman SNAI1/SPI1 replays Adamson replies; re-runs replay earlier runs; recorded as fresh source="llm". Prompt also lacks dataset/modality (CRISPRi vs CRISPRa).
C7 [code F6, test T6] HIGH heldout.py:157-181 — N sweep axis never reaches the trainer; LinearBackbone ignores seed/max_iter; only 19 of "54" configs distinct (linear 1, mlp 9, scgpt 9). Pre-registered H1/H2 "oracle best-of-54" misdescribes what runs.
C8 [code F5] MEDIUM loop.py:252-254 + architect_dispatch.py:80-107 — Architect hvg_count/learning_rate/ridge_lambda/epochs resolved but never applied; validator critique deltas on them are no-ops; architect_hvg_entropy_nats reported for an ineffective choice.
C9 [code F11] MEDIUM scgpt_small.py:160-176 — model/tensors never moved to CUDA -> sweep trains on CPU; provenance records gpu=A100 and "gpu_seconds"; cost/timeout sized for GPU.
C10 [test T5, design F6] HIGH e_v05_real_traces.py:240-247,338,415 — preregistration pin mismatch raise untested; a run with NO pin (or legacy_no_provenance) is summarised with gates LICENSED (status ok / legacy) — pre-registration not enforced at analysis time.
C11 [design F5] HIGH paper/sections/experimental_setup.tex:90-92 — claims Literature agent uses BioGPT + PubMed + STRING-DB; the sweep's LLMAgentPool Literature role is a bare prompt with no tools.
C12 [design F7] MEDIUM app_v05.py:340-344,413-415,282-285 — max_tasks_override / include_norman=False / include_adamson=False produce status ok and licensed gates on a smaller-than-pre-registered design.
C13 [design F8] MEDIUM heldout.py:104-107, validator_gate.py:86 — top-20 DEGs chosen within HVG columns (2000 trainer vs curator-count lifecycle) -> H1/H2 vs H4 MSD over different gene sets; metric duplicated with literal 20.
C14 [design F10, test T20] MEDIUM app_v05.py:477-499,522-526 — provenance.entropies computed over ALL steps incl. fallback, 0.0 when none; second producer contradicting analyser (llm-only, None).
C15 [code F7] MEDIUM loop.py:270-271 — n_params from last successful round filed under last round's backbone.
C16 [design F9] MEDIUM perturbations.py:20-37, norman.py:34-39, e2_adamson.py:137-139 — four control predicates; perturbations.is_control lacks 63(/neg_ctrl/Gal4.
C17 [test T2] HIGH tests/test_data_download.py:188-196 — fetch_adamson_all unpinned test passes for the wrong reason (SHA mismatch, no match=).
C18 [test T4] HIGH — no test that a diagnostic summary withdraws H1-H5 / tally counts None as UNEVALUATED.
C19 [test T7-T19, T21-T24] MEDIUM/LOW — untested fail-closed branches: preflight empty plan/backbones/dataset-not-in-sweep, openrouter_probe, lifecycle abort on RuntimeError, dC clip, non-finite confidence, gate thresholds at boundary + failing cases, H5 value/verdict, download truncation, loader unresolved branches, max_cells cap, source/model_id check, remap_targets refusal, label_contract validation branches, bootstrap drops, test_provenance_is_json no assert.
C20 [design F16] INFO PREREGISTRATION.md:168 — FWER "bracket" excludes negative dependence between ACE and 1-dC; could exceed 5.81%.
C21 [security S-1,S-2] LOW llm_agent_pool.py:169-172, errors.py:121,134, v05_preflight.py:125 — exception text/tracebacks logged/recorded unredacted; scrub misses repr() of a key with control chars (e.g. trailing \n -> InvalidHeader message). Currently unreachable (probe refuses first).
C22 [security S-3] LOW app_v05.py:194 — --version unvalidated -> path escape of /data.
C23 [design F12] LOW app_v05.py:17-21, README.md:101, paper/README.md:37 — docs say `source .env` / bare modal run (key on disk; missing OPENROUTER_KEY_SOURCE -> preflight refuses).
C24 [design F13] LOW e_v05_real_traces.py:461-463,490-492 — CLI defaults to v0.5.0, no positional arg; plan T24 command won't parse; [v0.5.0] log strings.
C25 [design F11] LOW v05_tasks.py:116-138 — pre-registration says "every stratum filled exactly"; code asserts pool totals only.
C26 [code F10] LOW norman.py:192, e2_adamson.py:79,344 — gene_to_idx keeps last column on duplicate symbols (duplicates unverified).
C27 [code F12,F13,F14; design F14,F15] LOW — MockAgentPool hash(role); unreachable out-of-range target drops; subsample trim alphabetical; two task-key helpers; private _rho cited.
OWN-1 HIGH app_v05.py:89,223 — CTO #283 requires stop-and-report at actual spend > $12; only the $28 kill exists.

## Scorer (reviewer-scorer, threshold 80): 24 survive; below threshold: C19 (65, split), C21 (72), C26 (55). NEW-1 added (82).
