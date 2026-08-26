Analyze these files and produce GraphNode and GraphEdge objects.
Project root: `/Users/mo/github/personal/bioFM`
Project: `bioFM` — A living monorepo workspace for Biological Foundation Models (DNA, RNA, protein, single-cell, multimodal) that pairs a curated research landscape (MODELS.md, a test-time compute primer, pinned upstream submodules) with runnable Python packages: a test-time compute scaling library for BioFM-265M, a 5-agent propose-critique-vote orchestrator (cellforge-agents), and the paper-bearing perturb-seq-eval project on Bayesian agentic hyperparameter tuning.
Languages: `bib, html, json, jsonl, makefile, markdown, python, tex, toml, yaml`
Batch: `24/28`
Skill directory (for bundled scripts): `/Users/mo/.claude/plugins/cache/understand-anything/understand-anything/2.8.0/skills/understand`
Output: write to `/Users/mo/github/personal/bioFM/.understand-anything/intermediate/batch-24.json` (single-file mode) OR `batch-24-part-<k>.json` (split mode, per Step B of your output protocol).

**IMPORTANT — output file naming:** the output file MUST be named exactly `batch-24.json` (or `batch-24-part-<k>.json`). Any other name is silently dropped by the merge script.

**Additional context from main session:**

Project: `bioFM` — A living monorepo workspace for Biological Foundation Models (DNA, RNA, protein, single-cell, multimodal) that pairs a curated research landscape (MODELS.md, a test-time compute primer, pinned upstream submodules) with runnable Python packages: a test-time compute scaling library for BioFM-265M, a 5-agent propose-critique-vote orchestrator (cellforge-agents), and the paper-bearing perturb-seq-eval project on Bayesian agentic hyperparameter tuning.
Languages: `bib, html, json, jsonl, makefile, markdown, python, tex, toml, yaml`
Frameworks: PyTorch, Transformers, scikit-learn, Pydantic, Typer, pytest, Modal

> **Language directive**: Generate all textual content (summaries, descriptions, tags, titles, languageNotes, languageLesson) in **English**. Maintain technical accuracy while using natural, native-level phrasing in the target language. Keep technical terms in English when no standard translation exists (e.g., "middleware", "hook", "barrel").

Pre-resolved import data for this batch (use directly — do NOT re-resolve imports from source):
```json
{
 "paper_standalone/src/perturb_eval/adamson_loader.py": [
  "paper_standalone/src/perturb_eval/data.py"
 ],
 "paper_standalone/src/perturb_eval/backends/__init__.py": [
  "paper_standalone/src/perturb_eval/backends/openrouter.py"
 ],
 "paper_standalone/src/perturb_eval/backends/openrouter.py": [],
 "paper_standalone/src/perturb_eval/data.py": [],
 "paper_standalone/src/perturb_eval/model.py": [],
 "paper_standalone/tables/tab1_metric_correlations.tex": [],
 "paper_standalone/tables/tab2_calibration_improvement.tex": [],
 "paper_standalone/tables/tab3_probe_to_target.tex": [],
 "paper_standalone/tables/tab4_agent_scaling.tex": [],
 "paper_standalone/tables/tab5_pareto_samples.tex": [],
 "projects/perturb-seq-eval/artifacts/dry_run/e2_grid.jsonl": [],
 "projects/perturb-seq-eval/artifacts/lifecycle_dryrun/dryrun_runs.json": [],
 "projects/perturb-seq-eval/artifacts/lifecycle/adamson_lifecycle_runs.json": [],
 "projects/perturb-seq-eval/artifacts/lifecycle/adamson_live_optimizer.json": [],
 "projects/perturb-seq-eval/artifacts/live/last_run.json": [],
 "projects/perturb-seq-eval/artifacts/live/llm_calls.jsonl": [],
 "projects/perturb-seq-eval/artifacts/local/e1_overlap.json": [],
 "projects/perturb-seq-eval/artifacts/local/e2_grid.jsonl": [],
 "projects/perturb-seq-eval/artifacts/local/e3_trajectories.json": [],
 "projects/perturb-seq-eval/artifacts/modal_run/results/e2_grid_adamson.jsonl": [],
 "projects/perturb-seq-eval/artifacts/modal_run/results/e2_grid_synthetic.jsonl": [],
 "projects/perturb-seq-eval/artifacts/real_probes/adamson_traces_biofm.jsonl": [],
 "projects/perturb-seq-eval/artifacts/real_probes/adamson_traces.jsonl": [],
 "projects/perturb-seq-eval/artifacts/v0.5.0/lifecycle_runs.jsonl": [],
 "projects/perturb-seq-eval/artifacts/v0.5.0/trainer_runs.jsonl": []
}
```

Cross-batch neighbors with their exported symbols (confidence boost for cross-batch edges):
```json
{}
```

Files to analyze in this batch (every entry MUST be passed through to `batchFiles` with all four fields — `path`, `language`, `sizeLines`, `fileCategory`):
1. `paper_standalone/src/perturb_eval/adamson_loader.py` (104 lines, language: `python`, fileCategory: `code`)
2. `paper_standalone/src/perturb_eval/backends/__init__.py` (5 lines, language: `python`, fileCategory: `code`)
3. `paper_standalone/src/perturb_eval/backends/openrouter.py` (161 lines, language: `python`, fileCategory: `code`)
4. `paper_standalone/src/perturb_eval/data.py` (90 lines, language: `python`, fileCategory: `code`)
5. `paper_standalone/src/perturb_eval/model.py` (120 lines, language: `python`, fileCategory: `code`)
6. `paper_standalone/tables/tab1_metric_correlations.tex` (11 lines, language: `tex`, fileCategory: `code`)
7. `paper_standalone/tables/tab2_calibration_improvement.tex` (8 lines, language: `tex`, fileCategory: `code`)
8. `paper_standalone/tables/tab3_probe_to_target.tex` (8 lines, language: `tex`, fileCategory: `code`)
9. `paper_standalone/tables/tab4_agent_scaling.tex` (9 lines, language: `tex`, fileCategory: `code`)
10. `paper_standalone/tables/tab5_pareto_samples.tex` (11 lines, language: `tex`, fileCategory: `code`)
11. `projects/perturb-seq-eval/artifacts/dry_run/e2_grid.jsonl` (216 lines, language: `jsonl`, fileCategory: `code`)
12. `projects/perturb-seq-eval/artifacts/lifecycle_dryrun/dryrun_runs.json` (238 lines, language: `json`, fileCategory: `config`)
13. `projects/perturb-seq-eval/artifacts/lifecycle/adamson_lifecycle_runs.json` (16058 lines, language: `json`, fileCategory: `config`)
14. `projects/perturb-seq-eval/artifacts/lifecycle/adamson_live_optimizer.json` (177 lines, language: `json`, fileCategory: `config`)
15. `projects/perturb-seq-eval/artifacts/live/last_run.json` (14 lines, language: `json`, fileCategory: `config`)
16. `projects/perturb-seq-eval/artifacts/live/llm_calls.jsonl` (5 lines, language: `jsonl`, fileCategory: `code`)
17. `projects/perturb-seq-eval/artifacts/local/e1_overlap.json` (97 lines, language: `json`, fileCategory: `config`)
18. `projects/perturb-seq-eval/artifacts/local/e2_grid.jsonl` (72 lines, language: `jsonl`, fileCategory: `code`)
19. `projects/perturb-seq-eval/artifacts/local/e3_trajectories.json` (55 lines, language: `json`, fileCategory: `config`)
20. `projects/perturb-seq-eval/artifacts/modal_run/results/e2_grid_adamson.jsonl` (567 lines, language: `jsonl`, fileCategory: `code`)
21. `projects/perturb-seq-eval/artifacts/modal_run/results/e2_grid_synthetic.jsonl` (1080 lines, language: `jsonl`, fileCategory: `code`)
22. `projects/perturb-seq-eval/artifacts/real_probes/adamson_traces_biofm.jsonl` (175 lines, language: `jsonl`, fileCategory: `code`)
23. `projects/perturb-seq-eval/artifacts/real_probes/adamson_traces.jsonl` (175 lines, language: `jsonl`, fileCategory: `code`)
24. `projects/perturb-seq-eval/artifacts/v0.5.0/lifecycle_runs.jsonl` (108 lines, language: `jsonl`, fileCategory: `code`)
25. `projects/perturb-seq-eval/artifacts/v0.5.0/trainer_runs.jsonl` (1944 lines, language: `jsonl`, fileCategory: `code`)
