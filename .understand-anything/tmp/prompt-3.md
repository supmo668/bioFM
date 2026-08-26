Analyze these files and produce GraphNode and GraphEdge objects.
Project root: `/Users/mo/github/personal/bioFM`
Project: `bioFM` — A living monorepo workspace for Biological Foundation Models (DNA, RNA, protein, single-cell, multimodal) that pairs a curated research landscape (MODELS.md, a test-time compute primer, pinned upstream submodules) with runnable Python packages: a test-time compute scaling library for BioFM-265M, a 5-agent propose-critique-vote orchestrator (cellforge-agents), and the paper-bearing perturb-seq-eval project on Bayesian agentic hyperparameter tuning.
Languages: `bib, html, json, jsonl, makefile, markdown, python, tex, toml, yaml`
Batch: `3/28`
Skill directory (for bundled scripts): `/Users/mo/.claude/plugins/cache/understand-anything/understand-anything/2.8.0/skills/understand`
Output: write to `/Users/mo/github/personal/bioFM/.understand-anything/intermediate/batch-3.json` (single-file mode) OR `batch-3-part-<k>.json` (split mode, per Step B of your output protocol).

**IMPORTANT — output file naming:** the output file MUST be named exactly `batch-3.json` (or `batch-3-part-<k>.json`). Any other name is silently dropped by the merge script.

**Additional context from main session:**

Project: `bioFM` — A living monorepo workspace for Biological Foundation Models (DNA, RNA, protein, single-cell, multimodal) that pairs a curated research landscape (MODELS.md, a test-time compute primer, pinned upstream submodules) with runnable Python packages: a test-time compute scaling library for BioFM-265M, a 5-agent propose-critique-vote orchestrator (cellforge-agents), and the paper-bearing perturb-seq-eval project on Bayesian agentic hyperparameter tuning.
Languages: `bib, html, json, jsonl, makefile, markdown, python, tex, toml, yaml`
Frameworks: PyTorch, Transformers, scikit-learn, Pydantic, Typer, pytest, Modal

> **Language directive**: Generate all textual content (summaries, descriptions, tags, titles, languageNotes, languageLesson) in **English**. Maintain technical accuracy while using natural, native-level phrasing in the target language. Keep technical terms in English when no standard translation exists (e.g., "middleware", "hook", "barrel").

Pre-resolved import data for this batch (use directly — do NOT re-resolve imports from source):
```json
{
 "projects/perturb-seq-eval/src/perturb_eval/agentic_lifecycle/__init__.py": [
  "projects/perturb-seq-eval/src/perturb_eval/agentic_lifecycle/types.py"
 ],
 "projects/perturb-seq-eval/src/perturb_eval/agentic_lifecycle/architect_dispatch.py": [
  "projects/perturb-seq-eval/src/perturb_eval/backbones/__init__.py"
 ],
 "projects/perturb-seq-eval/src/perturb_eval/agentic_lifecycle/data_curator_exec.py": [],
 "projects/perturb-seq-eval/src/perturb_eval/agentic_lifecycle/literature_exec.py": [],
 "projects/perturb-seq-eval/src/perturb_eval/agentic_lifecycle/loop.py": [
  "projects/perturb-seq-eval/src/perturb_eval/agentic_lifecycle/architect_dispatch.py",
  "projects/perturb-seq-eval/src/perturb_eval/agentic_lifecycle/data_curator_exec.py",
  "projects/perturb-seq-eval/src/perturb_eval/agentic_lifecycle/literature_exec.py",
  "projects/perturb-seq-eval/src/perturb_eval/agentic_lifecycle/trainer_exec.py",
  "projects/perturb-seq-eval/src/perturb_eval/agentic_lifecycle/types.py",
  "projects/perturb-seq-eval/src/perturb_eval/agentic_lifecycle/validator_gate.py",
  "projects/perturb-seq-eval/src/perturb_eval/backbones/__init__.py"
 ],
 "projects/perturb-seq-eval/src/perturb_eval/agentic_lifecycle/trainer_exec.py": [
  "projects/perturb-seq-eval/src/perturb_eval/backbones/__init__.py"
 ],
 "projects/perturb-seq-eval/src/perturb_eval/agentic_lifecycle/types.py": [],
 "projects/perturb-seq-eval/src/perturb_eval/agentic_lifecycle/validator_gate.py": [
  "projects/perturb-seq-eval/src/perturb_eval/agentic_lifecycle/types.py",
  "projects/perturb-seq-eval/src/perturb_eval/backbones/__init__.py"
 ],
 "projects/perturb-seq-eval/src/perturb_eval/backbones/__init__.py": [
  "projects/perturb-seq-eval/src/perturb_eval/backbones/base.py",
  "projects/perturb-seq-eval/src/perturb_eval/backbones/linear.py",
  "projects/perturb-seq-eval/src/perturb_eval/backbones/mlp.py",
  "projects/perturb-seq-eval/src/perturb_eval/backbones/scgpt_small.py"
 ],
 "projects/perturb-seq-eval/src/perturb_eval/backbones/base.py": [],
 "projects/perturb-seq-eval/src/perturb_eval/backbones/linear.py": [
  "projects/perturb-seq-eval/src/perturb_eval/backbones/base.py"
 ],
 "projects/perturb-seq-eval/src/perturb_eval/backbones/mlp.py": [
  "projects/perturb-seq-eval/src/perturb_eval/backbones/base.py"
 ],
 "projects/perturb-seq-eval/src/perturb_eval/backbones/scgpt_small.py": [
  "projects/perturb-seq-eval/src/perturb_eval/backbones/base.py"
 ]
}
```

Cross-batch neighbors with their exported symbols (confidence boost for cross-batch edges):
```json
{
 "projects/perturb-seq-eval/src/perturb_eval/backbones/__init__.py": [
  {
   "path": "projects/perturb-seq-eval/src/perturb_eval/experiments/e2_adamson.py",
   "batchIndex": 1,
   "symbols": [
    "load_adamson_combined",
    "_normalise_pert_label",
    "_is_control",
    "load_adamson_matrix",
    "train_grid_cell_adamson"
   ]
  },
  {
   "path": "projects/perturb-seq-eval/src/perturb_eval/experiments/e2_grid_fill.py",
   "batchIndex": 1,
   "symbols": [
    "enumerate_grid",
    "phi_identifier",
    "_train_cfg_from_phi",
    "write_results_jsonl"
   ]
  }
 ]
}
```

Files to analyze in this batch (every entry MUST be passed through to `batchFiles` with all four fields — `path`, `language`, `sizeLines`, `fileCategory`):
1. `projects/perturb-seq-eval/src/perturb_eval/agentic_lifecycle/__init__.py` (15 lines, language: `python`, fileCategory: `code`)
2. `projects/perturb-seq-eval/src/perturb_eval/agentic_lifecycle/architect_dispatch.py` (91 lines, language: `python`, fileCategory: `code`)
3. `projects/perturb-seq-eval/src/perturb_eval/agentic_lifecycle/data_curator_exec.py` (40 lines, language: `python`, fileCategory: `code`)
4. `projects/perturb-seq-eval/src/perturb_eval/agentic_lifecycle/literature_exec.py` (16 lines, language: `python`, fileCategory: `code`)
5. `projects/perturb-seq-eval/src/perturb_eval/agentic_lifecycle/loop.py` (283 lines, language: `python`, fileCategory: `code`)
6. `projects/perturb-seq-eval/src/perturb_eval/agentic_lifecycle/trainer_exec.py` (48 lines, language: `python`, fileCategory: `code`)
7. `projects/perturb-seq-eval/src/perturb_eval/agentic_lifecycle/types.py` (75 lines, language: `python`, fileCategory: `code`)
8. `projects/perturb-seq-eval/src/perturb_eval/agentic_lifecycle/validator_gate.py` (129 lines, language: `python`, fileCategory: `code`)
9. `projects/perturb-seq-eval/src/perturb_eval/backbones/__init__.py` (58 lines, language: `python`, fileCategory: `code`)
10. `projects/perturb-seq-eval/src/perturb_eval/backbones/base.py` (121 lines, language: `python`, fileCategory: `code`)
11. `projects/perturb-seq-eval/src/perturb_eval/backbones/linear.py` (86 lines, language: `python`, fileCategory: `code`)
12. `projects/perturb-seq-eval/src/perturb_eval/backbones/mlp.py` (129 lines, language: `python`, fileCategory: `code`)
13. `projects/perturb-seq-eval/src/perturb_eval/backbones/scgpt_small.py` (190 lines, language: `python`, fileCategory: `code`)
