Analyze these files and produce GraphNode and GraphEdge objects.
Project root: `/Users/mo/github/personal/bioFM`
Project: `bioFM` — A living monorepo workspace for Biological Foundation Models (DNA, RNA, protein, single-cell, multimodal) that pairs a curated research landscape (MODELS.md, a test-time compute primer, pinned upstream submodules) with runnable Python packages: a test-time compute scaling library for BioFM-265M, a 5-agent propose-critique-vote orchestrator (cellforge-agents), and the paper-bearing perturb-seq-eval project on Bayesian agentic hyperparameter tuning.
Languages: `bib, html, json, jsonl, makefile, markdown, python, tex, toml, yaml`
Batch: `15/28`
Skill directory (for bundled scripts): `/Users/mo/.claude/plugins/cache/understand-anything/understand-anything/2.8.0/skills/understand`
Output: write to `/Users/mo/github/personal/bioFM/.understand-anything/intermediate/batch-15.json` (single-file mode) OR `batch-15-part-<k>.json` (split mode, per Step B of your output protocol).

**IMPORTANT — output file naming:** the output file MUST be named exactly `batch-15.json` (or `batch-15-part-<k>.json`). Any other name is silently dropped by the merge script.

**Additional context from main session:**

Project: `bioFM` — A living monorepo workspace for Biological Foundation Models (DNA, RNA, protein, single-cell, multimodal) that pairs a curated research landscape (MODELS.md, a test-time compute primer, pinned upstream submodules) with runnable Python packages: a test-time compute scaling library for BioFM-265M, a 5-agent propose-critique-vote orchestrator (cellforge-agents), and the paper-bearing perturb-seq-eval project on Bayesian agentic hyperparameter tuning.
Languages: `bib, html, json, jsonl, makefile, markdown, python, tex, toml, yaml`
Frameworks: PyTorch, Transformers, scikit-learn, Pydantic, Typer, pytest, Modal

> **Language directive**: Generate all textual content (summaries, descriptions, tags, titles, languageNotes, languageLesson) in **English**. Maintain technical accuracy while using natural, native-level phrasing in the target language. Keep technical terms in English when no standard translation exists (e.g., "middleware", "hook", "barrel").

Pre-resolved import data for this batch (use directly — do NOT re-resolve imports from source):
```json
{
 "projects/perturb-seq-eval/artifacts/modal_run/figures/fig1_metric_heatmap.html": [],
 "projects/perturb-seq-eval/artifacts/modal_run/figures/fig2_e3_synthetic.html": [],
 "projects/perturb-seq-eval/artifacts/modal_run/figures/fig3_e3_adamson.html": [],
 "projects/perturb-seq-eval/artifacts/modal_run/figures/fig4_e3b_task_conditional.html": [],
 "projects/perturb-seq-eval/artifacts/modal_run/figures/fig5_backbone_msd.html": [],
 "projects/perturb-seq-eval/artifacts/modal_run/figures/fig6_lifecycle_optimizer.html": []
}
```

Cross-batch neighbors with their exported symbols (confidence boost for cross-batch edges):
```json
{}
```

Files to analyze in this batch (every entry MUST be passed through to `batchFiles` with all four fields — `path`, `language`, `sizeLines`, `fileCategory`):
1. `projects/perturb-seq-eval/artifacts/modal_run/figures/fig1_metric_heatmap.html` (13 lines, language: `html`, fileCategory: `markup`)
2. `projects/perturb-seq-eval/artifacts/modal_run/figures/fig2_e3_synthetic.html` (13 lines, language: `html`, fileCategory: `markup`)
3. `projects/perturb-seq-eval/artifacts/modal_run/figures/fig3_e3_adamson.html` (13 lines, language: `html`, fileCategory: `markup`)
4. `projects/perturb-seq-eval/artifacts/modal_run/figures/fig4_e3b_task_conditional.html` (13 lines, language: `html`, fileCategory: `markup`)
5. `projects/perturb-seq-eval/artifacts/modal_run/figures/fig5_backbone_msd.html` (13 lines, language: `html`, fileCategory: `markup`)
6. `projects/perturb-seq-eval/artifacts/modal_run/figures/fig6_lifecycle_optimizer.html` (13 lines, language: `html`, fileCategory: `markup`)
