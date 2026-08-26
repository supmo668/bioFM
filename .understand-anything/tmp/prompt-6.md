Analyze these files and produce GraphNode and GraphEdge objects.
Project root: `/Users/mo/github/personal/bioFM`
Project: `bioFM` — A living monorepo workspace for Biological Foundation Models (DNA, RNA, protein, single-cell, multimodal) that pairs a curated research landscape (MODELS.md, a test-time compute primer, pinned upstream submodules) with runnable Python packages: a test-time compute scaling library for BioFM-265M, a 5-agent propose-critique-vote orchestrator (cellforge-agents), and the paper-bearing perturb-seq-eval project on Bayesian agentic hyperparameter tuning.
Languages: `bib, html, json, jsonl, makefile, markdown, python, tex, toml, yaml`
Batch: `6/28`
Skill directory (for bundled scripts): `/Users/mo/.claude/plugins/cache/understand-anything/understand-anything/2.8.0/skills/understand`
Output: write to `/Users/mo/github/personal/bioFM/.understand-anything/intermediate/batch-6.json` (single-file mode) OR `batch-6-part-<k>.json` (split mode, per Step B of your output protocol).

**IMPORTANT — output file naming:** the output file MUST be named exactly `batch-6.json` (or `batch-6-part-<k>.json`). Any other name is silently dropped by the merge script.

**Additional context from main session:**

Project: `bioFM` — A living monorepo workspace for Biological Foundation Models (DNA, RNA, protein, single-cell, multimodal) that pairs a curated research landscape (MODELS.md, a test-time compute primer, pinned upstream submodules) with runnable Python packages: a test-time compute scaling library for BioFM-265M, a 5-agent propose-critique-vote orchestrator (cellforge-agents), and the paper-bearing perturb-seq-eval project on Bayesian agentic hyperparameter tuning.
Languages: `bib, html, json, jsonl, makefile, markdown, python, tex, toml, yaml`
Frameworks: PyTorch, Transformers, scikit-learn, Pydantic, Typer, pytest, Modal

> **Language directive**: Generate all textual content (summaries, descriptions, tags, titles, languageNotes, languageLesson) in **English**. Maintain technical accuracy while using natural, native-level phrasing in the target language. Keep technical terms in English when no standard translation exists (e.g., "middleware", "hook", "barrel").

Pre-resolved import data for this batch (use directly — do NOT re-resolve imports from source):
```json
{
 "libs/test-time-compute/src/ttc/__init__.py": [
  "libs/test-time-compute/src/ttc/config.py",
  "libs/test-time-compute/src/ttc/runner.py"
 ],
 "libs/test-time-compute/src/ttc/__main__.py": [
  "libs/test-time-compute/src/ttc/cli.py"
 ],
 "libs/test-time-compute/src/ttc/cli.py": [
  "libs/test-time-compute/src/ttc/config.py",
  "libs/test-time-compute/src/ttc/runner.py"
 ],
 "libs/test-time-compute/src/ttc/config.py": [],
 "libs/test-time-compute/src/ttc/runner.py": [
  "libs/test-time-compute/src/ttc/config.py",
  "libs/test-time-compute/src/ttc/scoring.py",
  "libs/test-time-compute/src/ttc/strategies.py"
 ],
 "libs/test-time-compute/src/ttc/scoring.py": [],
 "libs/test-time-compute/src/ttc/strategies.py": [
  "libs/test-time-compute/src/ttc/config.py",
  "libs/test-time-compute/src/ttc/scoring.py"
 ]
}
```

Cross-batch neighbors with their exported symbols (confidence boost for cross-batch edges):
```json
{}
```

Files to analyze in this batch (every entry MUST be passed through to `batchFiles` with all four fields — `path`, `language`, `sizeLines`, `fileCategory`):
1. `libs/test-time-compute/src/ttc/__init__.py` (12 lines, language: `python`, fileCategory: `code`)
2. `libs/test-time-compute/src/ttc/__main__.py` (4 lines, language: `python`, fileCategory: `code`)
3. `libs/test-time-compute/src/ttc/cli.py` (145 lines, language: `python`, fileCategory: `code`)
4. `libs/test-time-compute/src/ttc/config.py` (47 lines, language: `python`, fileCategory: `code`)
5. `libs/test-time-compute/src/ttc/runner.py` (78 lines, language: `python`, fileCategory: `code`)
6. `libs/test-time-compute/src/ttc/scoring.py` (129 lines, language: `python`, fileCategory: `code`)
7. `libs/test-time-compute/src/ttc/strategies.py` (153 lines, language: `python`, fileCategory: `code`)
