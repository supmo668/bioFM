Analyze these files and produce GraphNode and GraphEdge objects.
Project root: `/Users/mo/github/personal/bioFM`
Project: `bioFM` — A living monorepo workspace for Biological Foundation Models (DNA, RNA, protein, single-cell, multimodal) that pairs a curated research landscape (MODELS.md, a test-time compute primer, pinned upstream submodules) with runnable Python packages: a test-time compute scaling library for BioFM-265M, a 5-agent propose-critique-vote orchestrator (cellforge-agents), and the paper-bearing perturb-seq-eval project on Bayesian agentic hyperparameter tuning.
Languages: `bib, html, json, jsonl, makefile, markdown, python, tex, toml, yaml`
Batch: `14/28`
Skill directory (for bundled scripts): `/Users/mo/.claude/plugins/cache/understand-anything/understand-anything/2.8.0/skills/understand`
Output: write to `/Users/mo/github/personal/bioFM/.understand-anything/intermediate/batch-14.json` (single-file mode) OR `batch-14-part-<k>.json` (split mode, per Step B of your output protocol).

**IMPORTANT — output file naming:** the output file MUST be named exactly `batch-14.json` (or `batch-14-part-<k>.json`). Any other name is silently dropped by the merge script.

**Additional context from main session:**

Project: `bioFM` — A living monorepo workspace for Biological Foundation Models (DNA, RNA, protein, single-cell, multimodal) that pairs a curated research landscape (MODELS.md, a test-time compute primer, pinned upstream submodules) with runnable Python packages: a test-time compute scaling library for BioFM-265M, a 5-agent propose-critique-vote orchestrator (cellforge-agents), and the paper-bearing perturb-seq-eval project on Bayesian agentic hyperparameter tuning.
Languages: `bib, html, json, jsonl, makefile, markdown, python, tex, toml, yaml`
Frameworks: PyTorch, Transformers, scikit-learn, Pydantic, Typer, pytest, Modal

> **Language directive**: Generate all textual content (summaries, descriptions, tags, titles, languageNotes, languageLesson) in **English**. Maintain technical accuracy while using natural, native-level phrasing in the target language. Keep technical terms in English when no standard translation exists (e.g., "middleware", "hook", "barrel").

Pre-resolved import data for this batch (use directly — do NOT re-resolve imports from source):
```json
{
 "projects/perturb-seq-eval/artifacts/dry_run/e1_overlap.json": [],
 "projects/perturb-seq-eval/artifacts/dry_run/e3_trajectories.json": [],
 "projects/perturb-seq-eval/artifacts/dry_run/e3b_task_conditional.json": [],
 "projects/perturb-seq-eval/artifacts/dry_run/summary.json": []
}
```

Cross-batch neighbors with their exported symbols (confidence boost for cross-batch edges):
```json
{}
```

Files to analyze in this batch (every entry MUST be passed through to `batchFiles` with all four fields — `path`, `language`, `sizeLines`, `fileCategory`):
1. `projects/perturb-seq-eval/artifacts/dry_run/e1_overlap.json` (98 lines, language: `json`, fileCategory: `config`)
2. `projects/perturb-seq-eval/artifacts/dry_run/e3_trajectories.json` (85 lines, language: `json`, fileCategory: `config`)
3. `projects/perturb-seq-eval/artifacts/dry_run/e3b_task_conditional.json` (101 lines, language: `json`, fileCategory: `config`)
4. `projects/perturb-seq-eval/artifacts/dry_run/summary.json` (50 lines, language: `json`, fileCategory: `config`)
