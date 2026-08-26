Analyze these files and produce GraphNode and GraphEdge objects.
Project root: `/Users/mo/github/personal/bioFM`
Project: `bioFM` — A living monorepo workspace for Biological Foundation Models (DNA, RNA, protein, single-cell, multimodal) that pairs a curated research landscape (MODELS.md, a test-time compute primer, pinned upstream submodules) with runnable Python packages: a test-time compute scaling library for BioFM-265M, a 5-agent propose-critique-vote orchestrator (cellforge-agents), and the paper-bearing perturb-seq-eval project on Bayesian agentic hyperparameter tuning.
Languages: `bib, html, json, jsonl, makefile, markdown, python, tex, toml, yaml`
Batch: `5/28`
Skill directory (for bundled scripts): `/Users/mo/.claude/plugins/cache/understand-anything/understand-anything/2.8.0/skills/understand`
Output: write to `/Users/mo/github/personal/bioFM/.understand-anything/intermediate/batch-5.json` (single-file mode) OR `batch-5-part-<k>.json` (split mode, per Step B of your output protocol).

**IMPORTANT — output file naming:** the output file MUST be named exactly `batch-5.json` (or `batch-5-part-<k>.json`). Any other name is silently dropped by the merge script.

**Additional context from main session:**

Project: `bioFM` — A living monorepo workspace for Biological Foundation Models (DNA, RNA, protein, single-cell, multimodal) that pairs a curated research landscape (MODELS.md, a test-time compute primer, pinned upstream submodules) with runnable Python packages: a test-time compute scaling library for BioFM-265M, a 5-agent propose-critique-vote orchestrator (cellforge-agents), and the paper-bearing perturb-seq-eval project on Bayesian agentic hyperparameter tuning.
Languages: `bib, html, json, jsonl, makefile, markdown, python, tex, toml, yaml`
Frameworks: PyTorch, Transformers, scikit-learn, Pydantic, Typer, pytest, Modal

> **Language directive**: Generate all textual content (summaries, descriptions, tags, titles, languageNotes, languageLesson) in **English**. Maintain technical accuracy while using natural, native-level phrasing in the target language. Keep technical terms in English when no standard translation exists (e.g., "middleware", "hook", "barrel").

Pre-resolved import data for this batch (use directly — do NOT re-resolve imports from source):
```json
{
 "paper_standalone/src/perturb_eval/__init__.py": [
  "paper_standalone/src/perturb_eval/bayesian.py",
  "paper_standalone/src/perturb_eval/metrics.py",
  "paper_standalone/src/perturb_eval/probe.py",
  "paper_standalone/src/perturb_eval/types.py"
 ],
 "paper_standalone/src/perturb_eval/__main__.py": [
  "paper_standalone/src/perturb_eval/cli.py"
 ],
 "paper_standalone/src/perturb_eval/bayesian.py": [
  "paper_standalone/src/perturb_eval/probe.py",
  "paper_standalone/src/perturb_eval/types.py"
 ],
 "paper_standalone/src/perturb_eval/calibration.py": [
  "paper_standalone/src/perturb_eval/metrics.py",
  "paper_standalone/src/perturb_eval/types.py"
 ],
 "paper_standalone/src/perturb_eval/cli.py": [
  "paper_standalone/src/perturb_eval/bayesian.py",
  "paper_standalone/src/perturb_eval/probe.py"
 ],
 "paper_standalone/src/perturb_eval/instrumentation.py": [
  "paper_standalone/src/perturb_eval/types.py"
 ],
 "paper_standalone/src/perturb_eval/massgen_adapter.py": [
  "paper_standalone/src/perturb_eval/bayesian.py",
  "paper_standalone/src/perturb_eval/metrics.py",
  "paper_standalone/src/perturb_eval/probe.py",
  "paper_standalone/src/perturb_eval/types.py"
 ],
 "paper_standalone/src/perturb_eval/metrics.py": [
  "paper_standalone/src/perturb_eval/types.py"
 ],
 "paper_standalone/src/perturb_eval/probe.py": [
  "paper_standalone/src/perturb_eval/metrics.py",
  "paper_standalone/src/perturb_eval/types.py"
 ],
 "paper_standalone/src/perturb_eval/types.py": []
}
```

Cross-batch neighbors with their exported symbols (confidence boost for cross-batch edges):
```json
{}
```

Files to analyze in this batch (every entry MUST be passed through to `batchFiles` with all four fields — `path`, `language`, `sizeLines`, `fileCategory`):
1. `paper_standalone/src/perturb_eval/__init__.py` (34 lines, language: `python`, fileCategory: `code`)
2. `paper_standalone/src/perturb_eval/__main__.py` (4 lines, language: `python`, fileCategory: `code`)
3. `paper_standalone/src/perturb_eval/bayesian.py` (171 lines, language: `python`, fileCategory: `code`)
4. `paper_standalone/src/perturb_eval/calibration.py` (85 lines, language: `python`, fileCategory: `code`)
5. `paper_standalone/src/perturb_eval/cli.py` (54 lines, language: `python`, fileCategory: `code`)
6. `paper_standalone/src/perturb_eval/instrumentation.py` (102 lines, language: `python`, fileCategory: `code`)
7. `paper_standalone/src/perturb_eval/massgen_adapter.py` (71 lines, language: `python`, fileCategory: `code`)
8. `paper_standalone/src/perturb_eval/metrics.py` (212 lines, language: `python`, fileCategory: `code`)
9. `paper_standalone/src/perturb_eval/probe.py` (61 lines, language: `python`, fileCategory: `code`)
10. `paper_standalone/src/perturb_eval/types.py` (93 lines, language: `python`, fileCategory: `code`)
