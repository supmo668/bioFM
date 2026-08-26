Analyze these files and produce GraphNode and GraphEdge objects.
Project root: `/Users/mo/github/personal/bioFM`
Project: `bioFM` — A living monorepo workspace for Biological Foundation Models (DNA, RNA, protein, single-cell, multimodal) that pairs a curated research landscape (MODELS.md, a test-time compute primer, pinned upstream submodules) with runnable Python packages: a test-time compute scaling library for BioFM-265M, a 5-agent propose-critique-vote orchestrator (cellforge-agents), and the paper-bearing perturb-seq-eval project on Bayesian agentic hyperparameter tuning.
Languages: `bib, html, json, jsonl, makefile, markdown, python, tex, toml, yaml`
Batch: `27/28`
Skill directory (for bundled scripts): `/Users/mo/.claude/plugins/cache/understand-anything/understand-anything/2.8.0/skills/understand`
Output: write to `/Users/mo/github/personal/bioFM/.understand-anything/intermediate/batch-27.json` (single-file mode) OR `batch-27-part-<k>.json` (split mode, per Step B of your output protocol).

**IMPORTANT — output file naming:** the output file MUST be named exactly `batch-27.json` (or `batch-27-part-<k>.json`). Any other name is silently dropped by the merge script.

**Additional context from main session:**

Project: `bioFM` — A living monorepo workspace for Biological Foundation Models (DNA, RNA, protein, single-cell, multimodal) that pairs a curated research landscape (MODELS.md, a test-time compute primer, pinned upstream submodules) with runnable Python packages: a test-time compute scaling library for BioFM-265M, a 5-agent propose-critique-vote orchestrator (cellforge-agents), and the paper-bearing perturb-seq-eval project on Bayesian agentic hyperparameter tuning.
Languages: `bib, html, json, jsonl, makefile, markdown, python, tex, toml, yaml`
Frameworks: PyTorch, Transformers, scikit-learn, Pydantic, Typer, pytest, Modal

> **Language directive**: Generate all textual content (summaries, descriptions, tags, titles, languageNotes, languageLesson) in **English**. Maintain technical accuracy while using natural, native-level phrasing in the target language. Keep technical terms in English when no standard translation exists (e.g., "middleware", "hook", "barrel").

Pre-resolved import data for this batch (use directly — do NOT re-resolve imports from source):
```json
{
 "projects/perturb-seq-eval/src/perturb_eval/backends/__init__.py": [
  "projects/perturb-seq-eval/src/perturb_eval/backends/openrouter.py"
 ],
 "projects/perturb-seq-eval/src/perturb_eval/backends/openrouter.py": [],
 "projects/perturb-seq-eval/src/perturb_eval/biofm_tools/__init__.py": [],
 "projects/perturb-seq-eval/src/perturb_eval/biofm_tools/biogpt_literature.py": [],
 "projects/perturb-seq-eval/src/perturb_eval/biofm_tools/geneformer_validator.py": [],
 "projects/perturb-seq-eval/src/perturb_eval/data.py": [],
 "projects/perturb-seq-eval/src/perturb_eval/experiments/e_v05_real_traces.py": [
  "projects/perturb-seq-eval/src/perturb_eval/agentic_lifecycle/freedom_probe.py"
 ],
 "projects/perturb-seq-eval/src/perturb_eval/experiments/norman.py": [],
 "projects/perturb-seq-eval/src/perturb_eval/llm/__init__.py": [
  "projects/perturb-seq-eval/src/perturb_eval/llm/openrouter_client.py"
 ],
 "projects/perturb-seq-eval/src/perturb_eval/llm/openrouter_client.py": [],
 "projects/perturb-seq-eval/src/perturb_eval/model.py": [],
 "projects/perturb-seq-eval/tests/conftest.py": [],
 "projects/perturb-seq-eval/tests/test_adamson_combined.py": [],
 "projects/perturb-seq-eval/tests/test_agentic_lifecycle.py": [],
 "projects/perturb-seq-eval/tests/test_architect_dispatch_v05.py": [],
 "projects/perturb-seq-eval/tests/test_backbones.py": [],
 "projects/perturb-seq-eval/tests/test_bayesian.py": [],
 "projects/perturb-seq-eval/tests/test_calibration.py": [],
 "projects/perturb-seq-eval/tests/test_data_download.py": [],
 "projects/perturb-seq-eval/tests/test_data_subsample.py": [],
 "projects/perturb-seq-eval/tests/test_experiments.py": [],
 "projects/perturb-seq-eval/tests/test_fill_v050_numbers.py": [],
 "projects/perturb-seq-eval/tests/test_freedom_e2e.py": [],
 "projects/perturb-seq-eval/tests/test_freedom_probe.py": [],
 "projects/perturb-seq-eval/tests/test_instrumentation.py": []
}
```

Cross-batch neighbors with their exported symbols (confidence boost for cross-batch edges):
```json
{
 "projects/perturb-seq-eval/src/perturb_eval/data.py": [
  {
   "path": "projects/perturb-seq-eval/src/perturb_eval/adamson_loader.py",
   "batchIndex": 26,
   "symbols": [
    "AdamsonQC",
    "load_adamson_h5ad",
    "adamson_to_split",
    "perturbation_as_task_name"
   ]
  }
 ],
 "projects/perturb-seq-eval/src/perturb_eval/experiments/e_v05_real_traces.py": [
  {
   "path": "projects/perturb-seq-eval/src/perturb_eval/agentic_lifecycle/freedom_probe.py",
   "batchIndex": 26,
   "symbols": [
    "_coerce_step",
    "_hashable",
    "choice_entropy",
    "per_agent_field_entropy",
    "summarise_choice_distribution"
   ]
  }
 ]
}
```

Files to analyze in this batch (every entry MUST be passed through to `batchFiles` with all four fields — `path`, `language`, `sizeLines`, `fileCategory`):
1. `projects/perturb-seq-eval/src/perturb_eval/backends/__init__.py` (5 lines, language: `python`, fileCategory: `code`)
2. `projects/perturb-seq-eval/src/perturb_eval/backends/openrouter.py` (172 lines, language: `python`, fileCategory: `code`)
3. `projects/perturb-seq-eval/src/perturb_eval/biofm_tools/__init__.py` (13 lines, language: `python`, fileCategory: `code`)
4. `projects/perturb-seq-eval/src/perturb_eval/biofm_tools/biogpt_literature.py` (136 lines, language: `python`, fileCategory: `code`)
5. `projects/perturb-seq-eval/src/perturb_eval/biofm_tools/geneformer_validator.py` (225 lines, language: `python`, fileCategory: `code`)
6. `projects/perturb-seq-eval/src/perturb_eval/data.py` (90 lines, language: `python`, fileCategory: `code`)
7. `projects/perturb-seq-eval/src/perturb_eval/experiments/e_v05_real_traces.py` (268 lines, language: `python`, fileCategory: `code`)
8. `projects/perturb-seq-eval/src/perturb_eval/experiments/norman.py` (132 lines, language: `python`, fileCategory: `code`)
9. `projects/perturb-seq-eval/src/perturb_eval/llm/__init__.py` (19 lines, language: `python`, fileCategory: `code`)
10. `projects/perturb-seq-eval/src/perturb_eval/llm/openrouter_client.py` (330 lines, language: `python`, fileCategory: `code`)
11. `projects/perturb-seq-eval/src/perturb_eval/model.py` (120 lines, language: `python`, fileCategory: `code`)
12. `projects/perturb-seq-eval/tests/conftest.py` (78 lines, language: `python`, fileCategory: `code`)
13. `projects/perturb-seq-eval/tests/test_adamson_combined.py` (115 lines, language: `python`, fileCategory: `code`)
14. `projects/perturb-seq-eval/tests/test_agentic_lifecycle.py` (171 lines, language: `python`, fileCategory: `code`)
15. `projects/perturb-seq-eval/tests/test_architect_dispatch_v05.py` (65 lines, language: `python`, fileCategory: `code`)
16. `projects/perturb-seq-eval/tests/test_backbones.py` (206 lines, language: `python`, fileCategory: `code`)
17. `projects/perturb-seq-eval/tests/test_bayesian.py` (69 lines, language: `python`, fileCategory: `code`)
18. `projects/perturb-seq-eval/tests/test_calibration.py` (30 lines, language: `python`, fileCategory: `code`)
19. `projects/perturb-seq-eval/tests/test_data_download.py` (128 lines, language: `python`, fileCategory: `code`)
20. `projects/perturb-seq-eval/tests/test_data_subsample.py` (64 lines, language: `python`, fileCategory: `code`)
21. `projects/perturb-seq-eval/tests/test_experiments.py` (92 lines, language: `python`, fileCategory: `code`)
22. `projects/perturb-seq-eval/tests/test_fill_v050_numbers.py` (60 lines, language: `python`, fileCategory: `code`)
23. `projects/perturb-seq-eval/tests/test_freedom_e2e.py` (161 lines, language: `python`, fileCategory: `code`)
24. `projects/perturb-seq-eval/tests/test_freedom_probe.py` (95 lines, language: `python`, fileCategory: `code`)
25. `projects/perturb-seq-eval/tests/test_instrumentation.py` (114 lines, language: `python`, fileCategory: `code`)
