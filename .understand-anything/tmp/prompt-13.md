Analyze these files and produce GraphNode and GraphEdge objects.
Project root: `/Users/mo/github/personal/bioFM`
Project: `bioFM` — A living monorepo workspace for Biological Foundation Models (DNA, RNA, protein, single-cell, multimodal) that pairs a curated research landscape (MODELS.md, a test-time compute primer, pinned upstream submodules) with runnable Python packages: a test-time compute scaling library for BioFM-265M, a 5-agent propose-critique-vote orchestrator (cellforge-agents), and the paper-bearing perturb-seq-eval project on Bayesian agentic hyperparameter tuning.
Languages: `bib, html, json, jsonl, makefile, markdown, python, tex, toml, yaml`
Batch: `13/28`
Skill directory (for bundled scripts): `/Users/mo/.claude/plugins/cache/understand-anything/understand-anything/2.8.0/skills/understand`
Output: write to `/Users/mo/github/personal/bioFM/.understand-anything/intermediate/batch-13.json` (single-file mode) OR `batch-13-part-<k>.json` (split mode, per Step B of your output protocol).

**IMPORTANT — output file naming:** the output file MUST be named exactly `batch-13.json` (or `batch-13-part-<k>.json`). Any other name is silently dropped by the merge script.

**Additional context from main session:**

Project: `bioFM` — A living monorepo workspace for Biological Foundation Models (DNA, RNA, protein, single-cell, multimodal) that pairs a curated research landscape (MODELS.md, a test-time compute primer, pinned upstream submodules) with runnable Python packages: a test-time compute scaling library for BioFM-265M, a 5-agent propose-critique-vote orchestrator (cellforge-agents), and the paper-bearing perturb-seq-eval project on Bayesian agentic hyperparameter tuning.
Languages: `bib, html, json, jsonl, makefile, markdown, python, tex, toml, yaml`
Frameworks: PyTorch, Transformers, scikit-learn, Pydantic, Typer, pytest, Modal

> **Language directive**: Generate all textual content (summaries, descriptions, tags, titles, languageNotes, languageLesson) in **English**. Maintain technical accuracy while using natural, native-level phrasing in the target language. Keep technical terms in English when no standard translation exists (e.g., "middleware", "hook", "barrel").

Pre-resolved import data for this batch (use directly — do NOT re-resolve imports from source):
```json
{
 "projects/perturb-seq-eval/CHANGELOG.md": [],
 "projects/perturb-seq-eval/LIVE_RUN.md": [],
 "projects/perturb-seq-eval/README.md": [],
 "projects/perturb-seq-eval/publish.state.json": [],
 "projects/perturb-seq-eval/publish.yml": [],
 "projects/perturb-seq-eval/pyproject.toml": [],
 "projects/perturb-seq-eval/requirements.txt": []
}
```

Cross-batch neighbors with their exported symbols (confidence boost for cross-batch edges):
```json
{}
```

Files to analyze in this batch (every entry MUST be passed through to `batchFiles` with all four fields — `path`, `language`, `sizeLines`, `fileCategory`):
1. `projects/perturb-seq-eval/CHANGELOG.md` (141 lines, language: `markdown`, fileCategory: `docs`)
2. `projects/perturb-seq-eval/LIVE_RUN.md` (118 lines, language: `markdown`, fileCategory: `docs`)
3. `projects/perturb-seq-eval/README.md` (103 lines, language: `markdown`, fileCategory: `docs`)
4. `projects/perturb-seq-eval/publish.state.json` (33 lines, language: `json`, fileCategory: `config`)
5. `projects/perturb-seq-eval/publish.yml` (128 lines, language: `yaml`, fileCategory: `config`)
6. `projects/perturb-seq-eval/pyproject.toml` (74 lines, language: `toml`, fileCategory: `config`)
7. `projects/perturb-seq-eval/requirements.txt` (3 lines, language: `txt`, fileCategory: `docs`)
