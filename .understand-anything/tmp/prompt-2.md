Analyze these files and produce GraphNode and GraphEdge objects.
Project root: `/Users/mo/github/personal/bioFM`
Project: `bioFM` — A living monorepo workspace for Biological Foundation Models (DNA, RNA, protein, single-cell, multimodal) that pairs a curated research landscape (MODELS.md, a test-time compute primer, pinned upstream submodules) with runnable Python packages: a test-time compute scaling library for BioFM-265M, a 5-agent propose-critique-vote orchestrator (cellforge-agents), and the paper-bearing perturb-seq-eval project on Bayesian agentic hyperparameter tuning.
Languages: `bib, html, json, jsonl, makefile, markdown, python, tex, toml, yaml`
Batch: `2/28`
Skill directory (for bundled scripts): `/Users/mo/.claude/plugins/cache/understand-anything/understand-anything/2.8.0/skills/understand`
Output: write to `/Users/mo/github/personal/bioFM/.understand-anything/intermediate/batch-2.json` (single-file mode) OR `batch-2-part-<k>.json` (split mode, per Step B of your output protocol).

**IMPORTANT — output file naming:** the output file MUST be named exactly `batch-2.json` (or `batch-2-part-<k>.json`). Any other name is silently dropped by the merge script.

**Additional context from main session:**

Project: `bioFM` — A living monorepo workspace for Biological Foundation Models (DNA, RNA, protein, single-cell, multimodal) that pairs a curated research landscape (MODELS.md, a test-time compute primer, pinned upstream submodules) with runnable Python packages: a test-time compute scaling library for BioFM-265M, a 5-agent propose-critique-vote orchestrator (cellforge-agents), and the paper-bearing perturb-seq-eval project on Bayesian agentic hyperparameter tuning.
Languages: `bib, html, json, jsonl, makefile, markdown, python, tex, toml, yaml`
Frameworks: PyTorch, Transformers, scikit-learn, Pydantic, Typer, pytest, Modal

> **Language directive**: Generate all textual content (summaries, descriptions, tags, titles, languageNotes, languageLesson) in **English**. Maintain technical accuracy while using natural, native-level phrasing in the target language. Keep technical terms in English when no standard translation exists (e.g., "middleware", "hook", "barrel").

Pre-resolved import data for this batch (use directly — do NOT re-resolve imports from source):
```json
{
 "libs/cellforge-agents/src/cellforge/__init__.py": [
  "libs/cellforge-agents/src/cellforge/orchestrator.py",
  "libs/cellforge-agents/src/cellforge/problem.py"
 ],
 "libs/cellforge-agents/src/cellforge/__main__.py": [
  "libs/cellforge-agents/src/cellforge/cli.py"
 ],
 "libs/cellforge-agents/src/cellforge/agents/__init__.py": [
  "libs/cellforge-agents/src/cellforge/agents/architect.py",
  "libs/cellforge-agents/src/cellforge/agents/base.py",
  "libs/cellforge-agents/src/cellforge/agents/data_curator.py",
  "libs/cellforge-agents/src/cellforge/agents/literature.py",
  "libs/cellforge-agents/src/cellforge/agents/trainer.py",
  "libs/cellforge-agents/src/cellforge/agents/validator.py"
 ],
 "libs/cellforge-agents/src/cellforge/agents/architect.py": [
  "libs/cellforge-agents/src/cellforge/agents/base.py",
  "libs/cellforge-agents/src/cellforge/problem.py",
  "libs/cellforge-agents/src/cellforge/tools/biofm_catalog.py"
 ],
 "libs/cellforge-agents/src/cellforge/agents/base.py": [
  "libs/cellforge-agents/src/cellforge/problem.py"
 ],
 "libs/cellforge-agents/src/cellforge/agents/data_curator.py": [
  "libs/cellforge-agents/src/cellforge/agents/base.py",
  "libs/cellforge-agents/src/cellforge/problem.py",
  "libs/cellforge-agents/src/cellforge/tools/omics.py"
 ],
 "libs/cellforge-agents/src/cellforge/agents/literature.py": [
  "libs/cellforge-agents/src/cellforge/agents/base.py",
  "libs/cellforge-agents/src/cellforge/problem.py",
  "libs/cellforge-agents/src/cellforge/tools/literature.py"
 ],
 "libs/cellforge-agents/src/cellforge/agents/trainer.py": [
  "libs/cellforge-agents/src/cellforge/agents/base.py",
  "libs/cellforge-agents/src/cellforge/problem.py",
  "libs/cellforge-agents/src/cellforge/tools/trainer.py"
 ],
 "libs/cellforge-agents/src/cellforge/agents/validator.py": [
  "libs/cellforge-agents/src/cellforge/agents/base.py",
  "libs/cellforge-agents/src/cellforge/problem.py",
  "libs/cellforge-agents/src/cellforge/tools/pathway.py"
 ],
 "libs/cellforge-agents/src/cellforge/cli.py": [
  "libs/cellforge-agents/src/cellforge/agents/__init__.py",
  "libs/cellforge-agents/src/cellforge/orchestrator.py",
  "libs/cellforge-agents/src/cellforge/problem.py"
 ],
 "libs/cellforge-agents/src/cellforge/orchestrator.py": [
  "libs/cellforge-agents/src/cellforge/agents/base.py",
  "libs/cellforge-agents/src/cellforge/problem.py"
 ],
 "libs/cellforge-agents/src/cellforge/problem.py": [],
 "libs/cellforge-agents/src/cellforge/tools/__init__.py": [
  "libs/cellforge-agents/src/cellforge/tools/biofm_catalog.py",
  "libs/cellforge-agents/src/cellforge/tools/literature.py",
  "libs/cellforge-agents/src/cellforge/tools/omics.py",
  "libs/cellforge-agents/src/cellforge/tools/pathway.py",
  "libs/cellforge-agents/src/cellforge/tools/trainer.py"
 ],
 "libs/cellforge-agents/src/cellforge/tools/biofm_catalog.py": [],
 "libs/cellforge-agents/src/cellforge/tools/literature.py": [],
 "libs/cellforge-agents/src/cellforge/tools/omics.py": [],
 "libs/cellforge-agents/src/cellforge/tools/pathway.py": [],
 "libs/cellforge-agents/src/cellforge/tools/trainer.py": []
}
```

Cross-batch neighbors with their exported symbols (confidence boost for cross-batch edges):
```json
{}
```

Files to analyze in this batch (every entry MUST be passed through to `batchFiles` with all four fields — `path`, `language`, `sizeLines`, `fileCategory`):
1. `libs/cellforge-agents/src/cellforge/__init__.py` (12 lines, language: `python`, fileCategory: `code`)
2. `libs/cellforge-agents/src/cellforge/__main__.py` (4 lines, language: `python`, fileCategory: `code`)
3. `libs/cellforge-agents/src/cellforge/agents/__init__.py` (26 lines, language: `python`, fileCategory: `code`)
4. `libs/cellforge-agents/src/cellforge/agents/architect.py` (41 lines, language: `python`, fileCategory: `code`)
5. `libs/cellforge-agents/src/cellforge/agents/base.py` (29 lines, language: `python`, fileCategory: `code`)
6. `libs/cellforge-agents/src/cellforge/agents/data_curator.py` (52 lines, language: `python`, fileCategory: `code`)
7. `libs/cellforge-agents/src/cellforge/agents/literature.py` (53 lines, language: `python`, fileCategory: `code`)
8. `libs/cellforge-agents/src/cellforge/agents/trainer.py` (57 lines, language: `python`, fileCategory: `code`)
9. `libs/cellforge-agents/src/cellforge/agents/validator.py` (49 lines, language: `python`, fileCategory: `code`)
10. `libs/cellforge-agents/src/cellforge/cli.py` (47 lines, language: `python`, fileCategory: `code`)
11. `libs/cellforge-agents/src/cellforge/orchestrator.py` (121 lines, language: `python`, fileCategory: `code`)
12. `libs/cellforge-agents/src/cellforge/problem.py` (56 lines, language: `python`, fileCategory: `code`)
13. `libs/cellforge-agents/src/cellforge/tools/__init__.py` (13 lines, language: `python`, fileCategory: `code`)
14. `libs/cellforge-agents/src/cellforge/tools/biofm_catalog.py` (57 lines, language: `python`, fileCategory: `code`)
15. `libs/cellforge-agents/src/cellforge/tools/literature.py` (61 lines, language: `python`, fileCategory: `code`)
16. `libs/cellforge-agents/src/cellforge/tools/omics.py` (43 lines, language: `python`, fileCategory: `code`)
17. `libs/cellforge-agents/src/cellforge/tools/pathway.py` (48 lines, language: `python`, fileCategory: `code`)
18. `libs/cellforge-agents/src/cellforge/tools/trainer.py` (33 lines, language: `python`, fileCategory: `code`)
