Analyze these files and produce GraphNode and GraphEdge objects.
Project root: `/Users/mo/github/personal/bioFM`
Project: `bioFM` — A living monorepo workspace for Biological Foundation Models (DNA, RNA, protein, single-cell, multimodal) that pairs a curated research landscape (MODELS.md, a test-time compute primer, pinned upstream submodules) with runnable Python packages: a test-time compute scaling library for BioFM-265M, a 5-agent propose-critique-vote orchestrator (cellforge-agents), and the paper-bearing perturb-seq-eval project on Bayesian agentic hyperparameter tuning.
Languages: `bib, html, json, jsonl, makefile, markdown, python, tex, toml, yaml`
Batch: `26/28`
Skill directory (for bundled scripts): `/Users/mo/.claude/plugins/cache/understand-anything/understand-anything/2.8.0/skills/understand`
Output: write to `/Users/mo/github/personal/bioFM/.understand-anything/intermediate/batch-26.json` (single-file mode) OR `batch-26-part-<k>.json` (split mode, per Step B of your output protocol).

**IMPORTANT — output file naming:** the output file MUST be named exactly `batch-26.json` (or `batch-26-part-<k>.json`). Any other name is silently dropped by the merge script.

**Additional context from main session:**

Project: `bioFM` — A living monorepo workspace for Biological Foundation Models (DNA, RNA, protein, single-cell, multimodal) that pairs a curated research landscape (MODELS.md, a test-time compute primer, pinned upstream submodules) with runnable Python packages: a test-time compute scaling library for BioFM-265M, a 5-agent propose-critique-vote orchestrator (cellforge-agents), and the paper-bearing perturb-seq-eval project on Bayesian agentic hyperparameter tuning.
Languages: `bib, html, json, jsonl, makefile, markdown, python, tex, toml, yaml`
Frameworks: PyTorch, Transformers, scikit-learn, Pydantic, Typer, pytest, Modal

> **Language directive**: Generate all textual content (summaries, descriptions, tags, titles, languageNotes, languageLesson) in **English**. Maintain technical accuracy while using natural, native-level phrasing in the target language. Keep technical terms in English when no standard translation exists (e.g., "middleware", "hook", "barrel").

Pre-resolved import data for this batch (use directly — do NOT re-resolve imports from source):
```json
{
 "projects/perturb-seq-eval/scripts/local/bootstrap_and_analyze.py": [],
 "projects/perturb-seq-eval/scripts/local/collect_real_probes.py": [],
 "projects/perturb-seq-eval/scripts/local/e3b_task_conditional.py": [],
 "projects/perturb-seq-eval/scripts/local/full_local_dry_run.py": [],
 "projects/perturb-seq-eval/scripts/local/pull_v05_artifacts.py": [],
 "projects/perturb-seq-eval/scripts/local/render_fig6_lifecycle.py": [],
 "projects/perturb-seq-eval/scripts/local/render_figures_png.py": [],
 "projects/perturb-seq-eval/scripts/local/render_figures_revised.py": [],
 "projects/perturb-seq-eval/scripts/local/rerun_e3_with_real_probes.py": [],
 "projects/perturb-seq-eval/scripts/local/run_lifecycle_dryrun.py": [],
 "projects/perturb-seq-eval/scripts/local/v05_dry_run.py": [],
 "projects/perturb-seq-eval/scripts/modal/app_biofm.py": [],
 "projects/perturb-seq-eval/scripts/modal/app_lifecycle_optimizer.py": [],
 "projects/perturb-seq-eval/scripts/modal/app_lifecycle.py": [],
 "projects/perturb-seq-eval/scripts/modal/app_v05_lifecycle_only.py": [],
 "projects/perturb-seq-eval/scripts/modal/app_v05.py": [],
 "projects/perturb-seq-eval/scripts/modal/collect_traces.py": [],
 "projects/perturb-seq-eval/scripts/paper/fill_v050_numbers.py": [],
 "projects/perturb-seq-eval/scripts/publish/submit_to_venues.py": [],
 "projects/perturb-seq-eval/src/perturb_eval/_env.py": [],
 "projects/perturb-seq-eval/src/perturb_eval/adamson_loader.py": [
  "projects/perturb-seq-eval/src/perturb_eval/data.py"
 ],
 "projects/perturb-seq-eval/src/perturb_eval/agentic_lifecycle/cellforge_pool.py": [],
 "projects/perturb-seq-eval/src/perturb_eval/agentic_lifecycle/freedom_probe.py": [],
 "projects/perturb-seq-eval/src/perturb_eval/agentic_lifecycle/llm_agent_pool.py": [
  "projects/perturb-seq-eval/src/perturb_eval/agentic_lifecycle/proposal_schema.py"
 ],
 "projects/perturb-seq-eval/src/perturb_eval/agentic_lifecycle/proposal_schema.py": []
}
```

Cross-batch neighbors with their exported symbols (confidence boost for cross-batch edges):
```json
{
 "projects/perturb-seq-eval/src/perturb_eval/adamson_loader.py": [
  {
   "path": "projects/perturb-seq-eval/src/perturb_eval/data.py",
   "batchIndex": 27,
   "symbols": [
    "PerturbSeqSplit",
    "PerturbSeqDataset",
    "SyntheticPerturbSeq",
    "load_norman",
    "load_adamson"
   ]
  }
 ],
 "projects/perturb-seq-eval/src/perturb_eval/agentic_lifecycle/freedom_probe.py": [
  {
   "path": "projects/perturb-seq-eval/src/perturb_eval/experiments/e_v05_real_traces.py",
   "batchIndex": 27,
   "symbols": [
    "BestConfigPerTask",
    "_read_jsonl",
    "_finite",
    "best_config_per_task",
    "median_msd_per_config",
    "tdi_vs_held_out_msd",
    "_rankdata",
    "_pearson",
    "analyse_v05_run",
    "main"
   ]
  }
 ]
}
```

Files to analyze in this batch (every entry MUST be passed through to `batchFiles` with all four fields — `path`, `language`, `sizeLines`, `fileCategory`):
1. `projects/perturb-seq-eval/scripts/local/bootstrap_and_analyze.py` (351 lines, language: `python`, fileCategory: `code`)
2. `projects/perturb-seq-eval/scripts/local/collect_real_probes.py` (306 lines, language: `python`, fileCategory: `code`)
3. `projects/perturb-seq-eval/scripts/local/e3b_task_conditional.py` (126 lines, language: `python`, fileCategory: `code`)
4. `projects/perturb-seq-eval/scripts/local/full_local_dry_run.py` (256 lines, language: `python`, fileCategory: `code`)
5. `projects/perturb-seq-eval/scripts/local/pull_v05_artifacts.py` (41 lines, language: `python`, fileCategory: `code`)
6. `projects/perturb-seq-eval/scripts/local/render_fig6_lifecycle.py` (103 lines, language: `python`, fileCategory: `code`)
7. `projects/perturb-seq-eval/scripts/local/render_figures_png.py` (130 lines, language: `python`, fileCategory: `code`)
8. `projects/perturb-seq-eval/scripts/local/render_figures_revised.py` (198 lines, language: `python`, fileCategory: `code`)
9. `projects/perturb-seq-eval/scripts/local/rerun_e3_with_real_probes.py` (205 lines, language: `python`, fileCategory: `code`)
10. `projects/perturb-seq-eval/scripts/local/run_lifecycle_dryrun.py` (59 lines, language: `python`, fileCategory: `code`)
11. `projects/perturb-seq-eval/scripts/local/v05_dry_run.py` (174 lines, language: `python`, fileCategory: `code`)
12. `projects/perturb-seq-eval/scripts/modal/app_biofm.py` (363 lines, language: `python`, fileCategory: `code`)
13. `projects/perturb-seq-eval/scripts/modal/app_lifecycle_optimizer.py` (185 lines, language: `python`, fileCategory: `code`)
14. `projects/perturb-seq-eval/scripts/modal/app_lifecycle.py` (176 lines, language: `python`, fileCategory: `code`)
15. `projects/perturb-seq-eval/scripts/modal/app_v05_lifecycle_only.py` (294 lines, language: `python`, fileCategory: `code`)
16. `projects/perturb-seq-eval/scripts/modal/app_v05.py` (443 lines, language: `python`, fileCategory: `code`)
17. `projects/perturb-seq-eval/scripts/modal/collect_traces.py` (89 lines, language: `python`, fileCategory: `code`)
18. `projects/perturb-seq-eval/scripts/paper/fill_v050_numbers.py` (110 lines, language: `python`, fileCategory: `code`)
19. `projects/perturb-seq-eval/scripts/publish/submit_to_venues.py` (803 lines, language: `python`, fileCategory: `code`)
20. `projects/perturb-seq-eval/src/perturb_eval/_env.py` (50 lines, language: `python`, fileCategory: `code`)
21. `projects/perturb-seq-eval/src/perturb_eval/adamson_loader.py` (104 lines, language: `python`, fileCategory: `code`)
22. `projects/perturb-seq-eval/src/perturb_eval/agentic_lifecycle/cellforge_pool.py` (110 lines, language: `python`, fileCategory: `code`)
23. `projects/perturb-seq-eval/src/perturb_eval/agentic_lifecycle/freedom_probe.py` (84 lines, language: `python`, fileCategory: `code`)
24. `projects/perturb-seq-eval/src/perturb_eval/agentic_lifecycle/llm_agent_pool.py` (157 lines, language: `python`, fileCategory: `code`)
25. `projects/perturb-seq-eval/src/perturb_eval/agentic_lifecycle/proposal_schema.py` (119 lines, language: `python`, fileCategory: `code`)
