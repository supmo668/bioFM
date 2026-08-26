Analyze these files and produce GraphNode and GraphEdge objects.
Project root: `/Users/mo/github/personal/bioFM`
Project: `bioFM` — A living monorepo workspace for Biological Foundation Models (DNA, RNA, protein, single-cell, multimodal) that pairs a curated research landscape (MODELS.md, a test-time compute primer, pinned upstream submodules) with runnable Python packages: a test-time compute scaling library for BioFM-265M, a 5-agent propose-critique-vote orchestrator (cellforge-agents), and the paper-bearing perturb-seq-eval project on Bayesian agentic hyperparameter tuning.
Languages: `bib, html, json, jsonl, makefile, markdown, python, tex, toml, yaml`
Batch: `20/28`
Skill directory (for bundled scripts): `/Users/mo/.claude/plugins/cache/understand-anything/understand-anything/2.8.0/skills/understand`
Output: write to `/Users/mo/github/personal/bioFM/.understand-anything/intermediate/batch-20.json` (single-file mode) OR `batch-20-part-<k>.json` (split mode, per Step B of your output protocol).

**IMPORTANT — output file naming:** the output file MUST be named exactly `batch-20.json` (or `batch-20-part-<k>.json`). Any other name is silently dropped by the merge script.

**Additional context from main session:**

Project: `bioFM` — A living monorepo workspace for Biological Foundation Models (DNA, RNA, protein, single-cell, multimodal) that pairs a curated research landscape (MODELS.md, a test-time compute primer, pinned upstream submodules) with runnable Python packages: a test-time compute scaling library for BioFM-265M, a 5-agent propose-critique-vote orchestrator (cellforge-agents), and the paper-bearing perturb-seq-eval project on Bayesian agentic hyperparameter tuning.
Languages: `bib, html, json, jsonl, makefile, markdown, python, tex, toml, yaml`
Frameworks: PyTorch, Transformers, scikit-learn, Pydantic, Typer, pytest, Modal

> **Language directive**: Generate all textual content (summaries, descriptions, tags, titles, languageNotes, languageLesson) in **English**. Maintain technical accuracy while using natural, native-level phrasing in the target language. Keep technical terms in English when no standard translation exists (e.g., "middleware", "hook", "barrel").

Pre-resolved import data for this batch (use directly — do NOT re-resolve imports from source):
```json
{
 "projects/perturb-seq-eval/docs/DESIGN.md": [],
 "projects/perturb-seq-eval/docs/INTERNAL_FOLLOWUP.md": [],
 "projects/perturb-seq-eval/docs/MODAL.md": [],
 "projects/perturb-seq-eval/docs/PUBLICATION_CHECKLIST.md": [],
 "projects/perturb-seq-eval/docs/REVIEWER_CRITIQUE.md": [],
 "projects/perturb-seq-eval/docs/SUPPLEMENT.md": [],
 "projects/perturb-seq-eval/docs/SUPPLEMENT_DESIGN.md": [],
 "projects/perturb-seq-eval/docs/THESIS.md": []
}
```

Cross-batch neighbors with their exported symbols (confidence boost for cross-batch edges):
```json
{}
```

Files to analyze in this batch (every entry MUST be passed through to `batchFiles` with all four fields — `path`, `language`, `sizeLines`, `fileCategory`):
1. `projects/perturb-seq-eval/docs/DESIGN.md` (400 lines, language: `markdown`, fileCategory: `docs`)
2. `projects/perturb-seq-eval/docs/INTERNAL_FOLLOWUP.md` (144 lines, language: `markdown`, fileCategory: `docs`)
3. `projects/perturb-seq-eval/docs/MODAL.md` (119 lines, language: `markdown`, fileCategory: `docs`)
4. `projects/perturb-seq-eval/docs/PUBLICATION_CHECKLIST.md` (214 lines, language: `markdown`, fileCategory: `docs`)
5. `projects/perturb-seq-eval/docs/REVIEWER_CRITIQUE.md` (293 lines, language: `markdown`, fileCategory: `docs`)
6. `projects/perturb-seq-eval/docs/SUPPLEMENT.md` (570 lines, language: `markdown`, fileCategory: `docs`)
7. `projects/perturb-seq-eval/docs/SUPPLEMENT_DESIGN.md` (539 lines, language: `markdown`, fileCategory: `docs`)
8. `projects/perturb-seq-eval/docs/THESIS.md` (221 lines, language: `markdown`, fileCategory: `docs`)
