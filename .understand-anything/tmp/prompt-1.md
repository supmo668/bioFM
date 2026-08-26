Analyze these files and produce GraphNode and GraphEdge objects.
Project root: `/Users/mo/github/personal/bioFM`
Project: `bioFM` — A living monorepo workspace for Biological Foundation Models (DNA, RNA, protein, single-cell, multimodal) that pairs a curated research landscape (MODELS.md, a test-time compute primer, pinned upstream submodules) with runnable Python packages: a test-time compute scaling library for BioFM-265M, a 5-agent propose-critique-vote orchestrator (cellforge-agents), and the paper-bearing perturb-seq-eval project on Bayesian agentic hyperparameter tuning.
Languages: `bib, html, json, jsonl, makefile, markdown, python, tex, toml, yaml`
Batch: `1/28`
Skill directory (for bundled scripts): `/Users/mo/.claude/plugins/cache/understand-anything/understand-anything/2.8.0/skills/understand`
Output: write to `/Users/mo/github/personal/bioFM/.understand-anything/intermediate/batch-1.json` (single-file mode) OR `batch-1-part-<k>.json` (split mode, per Step B of your output protocol).

**IMPORTANT — output file naming:** the output file MUST be named exactly `batch-1.json` (or `batch-1-part-<k>.json`). Any other name is silently dropped by the merge script.

**Additional context from main session:**

Project: `bioFM` — A living monorepo workspace for Biological Foundation Models (DNA, RNA, protein, single-cell, multimodal) that pairs a curated research landscape (MODELS.md, a test-time compute primer, pinned upstream submodules) with runnable Python packages: a test-time compute scaling library for BioFM-265M, a 5-agent propose-critique-vote orchestrator (cellforge-agents), and the paper-bearing perturb-seq-eval project on Bayesian agentic hyperparameter tuning.
Languages: `bib, html, json, jsonl, makefile, markdown, python, tex, toml, yaml`
Frameworks: PyTorch, Transformers, scikit-learn, Pydantic, Typer, pytest, Modal

> **Language directive**: Generate all textual content (summaries, descriptions, tags, titles, languageNotes, languageLesson) in **English**. Maintain technical accuracy while using natural, native-level phrasing in the target language. Keep technical terms in English when no standard translation exists (e.g., "middleware", "hook", "barrel").

Pre-resolved import data for this batch (use directly — do NOT re-resolve imports from source):
```json
{
 "projects/perturb-seq-eval/src/perturb_eval/__init__.py": [
  "projects/perturb-seq-eval/src/perturb_eval/bayesian.py",
  "projects/perturb-seq-eval/src/perturb_eval/metrics.py",
  "projects/perturb-seq-eval/src/perturb_eval/probe.py",
  "projects/perturb-seq-eval/src/perturb_eval/types.py"
 ],
 "projects/perturb-seq-eval/src/perturb_eval/__main__.py": [
  "projects/perturb-seq-eval/src/perturb_eval/cli.py"
 ],
 "projects/perturb-seq-eval/src/perturb_eval/bayesian.py": [
  "projects/perturb-seq-eval/src/perturb_eval/probe.py",
  "projects/perturb-seq-eval/src/perturb_eval/types.py"
 ],
 "projects/perturb-seq-eval/src/perturb_eval/calibration.py": [
  "projects/perturb-seq-eval/src/perturb_eval/metrics.py",
  "projects/perturb-seq-eval/src/perturb_eval/types.py"
 ],
 "projects/perturb-seq-eval/src/perturb_eval/cli.py": [
  "projects/perturb-seq-eval/src/perturb_eval/bayesian.py",
  "projects/perturb-seq-eval/src/perturb_eval/probe.py"
 ],
 "projects/perturb-seq-eval/src/perturb_eval/experiments/__init__.py": [
  "projects/perturb-seq-eval/src/perturb_eval/experiments/common.py",
  "projects/perturb-seq-eval/src/perturb_eval/experiments/e2_grid_fill.py",
  "projects/perturb-seq-eval/src/perturb_eval/experiments/e3_optimizer_comparison.py"
 ],
 "projects/perturb-seq-eval/src/perturb_eval/experiments/common.py": [
  "projects/perturb-seq-eval/src/perturb_eval/metrics.py",
  "projects/perturb-seq-eval/src/perturb_eval/types.py"
 ],
 "projects/perturb-seq-eval/src/perturb_eval/experiments/e2_adamson.py": [
  "projects/perturb-seq-eval/src/perturb_eval/backbones/__init__.py",
  "projects/perturb-seq-eval/src/perturb_eval/experiments/common.py",
  "projects/perturb-seq-eval/src/perturb_eval/experiments/e2_grid_fill.py",
  "projects/perturb-seq-eval/src/perturb_eval/types.py"
 ],
 "projects/perturb-seq-eval/src/perturb_eval/experiments/e2_grid_fill.py": [
  "projects/perturb-seq-eval/src/perturb_eval/backbones/__init__.py",
  "projects/perturb-seq-eval/src/perturb_eval/experiments/common.py",
  "projects/perturb-seq-eval/src/perturb_eval/types.py"
 ],
 "projects/perturb-seq-eval/src/perturb_eval/experiments/e3_optimizer_comparison.py": [
  "projects/perturb-seq-eval/src/perturb_eval/experiments/common.py",
  "projects/perturb-seq-eval/src/perturb_eval/optimizers/__init__.py",
  "projects/perturb-seq-eval/src/perturb_eval/types.py"
 ],
 "projects/perturb-seq-eval/src/perturb_eval/instrumentation.py": [
  "projects/perturb-seq-eval/src/perturb_eval/types.py"
 ],
 "projects/perturb-seq-eval/src/perturb_eval/massgen_adapter.py": [
  "projects/perturb-seq-eval/src/perturb_eval/bayesian.py",
  "projects/perturb-seq-eval/src/perturb_eval/metrics.py",
  "projects/perturb-seq-eval/src/perturb_eval/probe.py",
  "projects/perturb-seq-eval/src/perturb_eval/types.py"
 ],
 "projects/perturb-seq-eval/src/perturb_eval/metrics.py": [
  "projects/perturb-seq-eval/src/perturb_eval/types.py"
 ],
 "projects/perturb-seq-eval/src/perturb_eval/optimizers/__init__.py": [
  "projects/perturb-seq-eval/src/perturb_eval/optimizers/base.py",
  "projects/perturb-seq-eval/src/perturb_eval/optimizers/cma_es.py",
  "projects/perturb-seq-eval/src/perturb_eval/optimizers/contextual_gp.py",
  "projects/perturb-seq-eval/src/perturb_eval/optimizers/random_baseline.py",
  "projects/perturb-seq-eval/src/perturb_eval/types.py"
 ],
 "projects/perturb-seq-eval/src/perturb_eval/optimizers/base.py": [
  "projects/perturb-seq-eval/src/perturb_eval/types.py"
 ],
 "projects/perturb-seq-eval/src/perturb_eval/optimizers/cma_es.py": [
  "projects/perturb-seq-eval/src/perturb_eval/optimizers/base.py",
  "projects/perturb-seq-eval/src/perturb_eval/types.py"
 ],
 "projects/perturb-seq-eval/src/perturb_eval/optimizers/contextual_gp.py": [
  "projects/perturb-seq-eval/src/perturb_eval/optimizers/base.py",
  "projects/perturb-seq-eval/src/perturb_eval/types.py"
 ],
 "projects/perturb-seq-eval/src/perturb_eval/optimizers/random_baseline.py": [
  "projects/perturb-seq-eval/src/perturb_eval/optimizers/base.py",
  "projects/perturb-seq-eval/src/perturb_eval/types.py"
 ],
 "projects/perturb-seq-eval/src/perturb_eval/probe.py": [
  "projects/perturb-seq-eval/src/perturb_eval/metrics.py",
  "projects/perturb-seq-eval/src/perturb_eval/types.py"
 ],
 "projects/perturb-seq-eval/src/perturb_eval/types.py": []
}
```

Cross-batch neighbors with their exported symbols (confidence boost for cross-batch edges):
```json
{
 "projects/perturb-seq-eval/src/perturb_eval/experiments/e2_adamson.py": [
  {
   "path": "projects/perturb-seq-eval/src/perturb_eval/backbones/__init__.py",
   "batchIndex": 3,
   "symbols": [
    "available_backbones",
    "build_backbone"
   ]
  }
 ],
 "projects/perturb-seq-eval/src/perturb_eval/experiments/e2_grid_fill.py": [
  {
   "path": "projects/perturb-seq-eval/src/perturb_eval/backbones/__init__.py",
   "batchIndex": 3,
   "symbols": [
    "available_backbones",
    "build_backbone"
   ]
  }
 ]
}
```

Files to analyze in this batch (every entry MUST be passed through to `batchFiles` with all four fields — `path`, `language`, `sizeLines`, `fileCategory`):
1. `projects/perturb-seq-eval/src/perturb_eval/__init__.py` (34 lines, language: `python`, fileCategory: `code`)
2. `projects/perturb-seq-eval/src/perturb_eval/__main__.py` (4 lines, language: `python`, fileCategory: `code`)
3. `projects/perturb-seq-eval/src/perturb_eval/bayesian.py` (171 lines, language: `python`, fileCategory: `code`)
4. `projects/perturb-seq-eval/src/perturb_eval/calibration.py` (85 lines, language: `python`, fileCategory: `code`)
5. `projects/perturb-seq-eval/src/perturb_eval/cli.py` (54 lines, language: `python`, fileCategory: `code`)
6. `projects/perturb-seq-eval/src/perturb_eval/experiments/__init__.py` (27 lines, language: `python`, fileCategory: `code`)
7. `projects/perturb-seq-eval/src/perturb_eval/experiments/common.py` (68 lines, language: `python`, fileCategory: `code`)
8. `projects/perturb-seq-eval/src/perturb_eval/experiments/e2_adamson.py` (294 lines, language: `python`, fileCategory: `code`)
9. `projects/perturb-seq-eval/src/perturb_eval/experiments/e2_grid_fill.py` (57 lines, language: `python`, fileCategory: `code`)
10. `projects/perturb-seq-eval/src/perturb_eval/experiments/e3_optimizer_comparison.py` (192 lines, language: `python`, fileCategory: `code`)
11. `projects/perturb-seq-eval/src/perturb_eval/instrumentation.py` (102 lines, language: `python`, fileCategory: `code`)
12. `projects/perturb-seq-eval/src/perturb_eval/massgen_adapter.py` (71 lines, language: `python`, fileCategory: `code`)
13. `projects/perturb-seq-eval/src/perturb_eval/metrics.py` (340 lines, language: `python`, fileCategory: `code`)
14. `projects/perturb-seq-eval/src/perturb_eval/optimizers/__init__.py` (48 lines, language: `python`, fileCategory: `code`)
15. `projects/perturb-seq-eval/src/perturb_eval/optimizers/base.py` (55 lines, language: `python`, fileCategory: `code`)
16. `projects/perturb-seq-eval/src/perturb_eval/optimizers/cma_es.py` (78 lines, language: `python`, fileCategory: `code`)
17. `projects/perturb-seq-eval/src/perturb_eval/optimizers/contextual_gp.py` (118 lines, language: `python`, fileCategory: `code`)
18. `projects/perturb-seq-eval/src/perturb_eval/optimizers/random_baseline.py` (20 lines, language: `python`, fileCategory: `code`)
19. `projects/perturb-seq-eval/src/perturb_eval/probe.py` (61 lines, language: `python`, fileCategory: `code`)
20. `projects/perturb-seq-eval/src/perturb_eval/types.py` (93 lines, language: `python`, fileCategory: `code`)
