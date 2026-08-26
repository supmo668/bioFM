Analyze these files and produce GraphNode and GraphEdge objects.
Project root: `/Users/mo/github/personal/bioFM`
Project: `bioFM` — A living monorepo workspace for Biological Foundation Models (DNA, RNA, protein, single-cell, multimodal) that pairs a curated research landscape (MODELS.md, a test-time compute primer, pinned upstream submodules) with runnable Python packages: a test-time compute scaling library for BioFM-265M, a 5-agent propose-critique-vote orchestrator (cellforge-agents), and the paper-bearing perturb-seq-eval project on Bayesian agentic hyperparameter tuning.
Languages: `bib, html, json, jsonl, makefile, markdown, python, tex, toml, yaml`
Batch: `4/28`
Skill directory (for bundled scripts): `/Users/mo/.claude/plugins/cache/understand-anything/understand-anything/2.8.0/skills/understand`
Output: write to `/Users/mo/github/personal/bioFM/.understand-anything/intermediate/batch-4.json` (single-file mode) OR `batch-4-part-<k>.json` (split mode, per Step B of your output protocol).

**IMPORTANT — output file naming:** the output file MUST be named exactly `batch-4.json` (or `batch-4-part-<k>.json`). Any other name is silently dropped by the merge script.

**Additional context from main session:**

Project: `bioFM` — A living monorepo workspace for Biological Foundation Models (DNA, RNA, protein, single-cell, multimodal) that pairs a curated research landscape (MODELS.md, a test-time compute primer, pinned upstream submodules) with runnable Python packages: a test-time compute scaling library for BioFM-265M, a 5-agent propose-critique-vote orchestrator (cellforge-agents), and the paper-bearing perturb-seq-eval project on Bayesian agentic hyperparameter tuning.
Languages: `bib, html, json, jsonl, makefile, markdown, python, tex, toml, yaml`
Frameworks: PyTorch, Transformers, scikit-learn, Pydantic, Typer, pytest, Modal

> **Language directive**: Generate all textual content (summaries, descriptions, tags, titles, languageNotes, languageLesson) in **English**. Maintain technical accuracy while using natural, native-level phrasing in the target language. Keep technical terms in English when no standard translation exists (e.g., "middleware", "hook", "barrel").

Pre-resolved import data for this batch (use directly — do NOT re-resolve imports from source):
```json
{
 "research/test-time-compute-guide/ref_impl/__init__.py": [
  "research/test-time-compute-guide/ref_impl/adaptive_budget.py",
  "research/test-time-compute-guide/ref_impl/best_of_n.py",
  "research/test-time-compute-guide/ref_impl/iterative_revision.py",
  "research/test-time-compute-guide/ref_impl/majority_vote.py",
  "research/test-time-compute-guide/ref_impl/types.py",
  "research/test-time-compute-guide/ref_impl/weighted_majority.py"
 ],
 "research/test-time-compute-guide/ref_impl/adaptive_budget.py": [
  "research/test-time-compute-guide/ref_impl/best_of_n.py",
  "research/test-time-compute-guide/ref_impl/iterative_revision.py",
  "research/test-time-compute-guide/ref_impl/types.py",
  "research/test-time-compute-guide/ref_impl/weighted_majority.py"
 ],
 "research/test-time-compute-guide/ref_impl/best_of_n.py": [
  "research/test-time-compute-guide/ref_impl/types.py"
 ],
 "research/test-time-compute-guide/ref_impl/iterative_revision.py": [
  "research/test-time-compute-guide/ref_impl/types.py"
 ],
 "research/test-time-compute-guide/ref_impl/majority_vote.py": [
  "research/test-time-compute-guide/ref_impl/types.py"
 ],
 "research/test-time-compute-guide/ref_impl/tests/conftest.py": [
  "research/test-time-compute-guide/ref_impl/types.py"
 ],
 "research/test-time-compute-guide/ref_impl/tests/test_adaptive_budget.py": [
  "research/test-time-compute-guide/ref_impl/adaptive_budget.py",
  "research/test-time-compute-guide/ref_impl/types.py"
 ],
 "research/test-time-compute-guide/ref_impl/tests/test_best_of_n.py": [
  "research/test-time-compute-guide/ref_impl/best_of_n.py"
 ],
 "research/test-time-compute-guide/ref_impl/tests/test_iterative_revision.py": [
  "research/test-time-compute-guide/ref_impl/iterative_revision.py",
  "research/test-time-compute-guide/ref_impl/types.py"
 ],
 "research/test-time-compute-guide/ref_impl/tests/test_majority_vote.py": [
  "research/test-time-compute-guide/ref_impl/majority_vote.py"
 ],
 "research/test-time-compute-guide/ref_impl/tests/test_weighted_majority.py": [
  "research/test-time-compute-guide/ref_impl/types.py",
  "research/test-time-compute-guide/ref_impl/weighted_majority.py"
 ],
 "research/test-time-compute-guide/ref_impl/types.py": [],
 "research/test-time-compute-guide/ref_impl/weighted_majority.py": [
  "research/test-time-compute-guide/ref_impl/types.py"
 ]
}
```

Cross-batch neighbors with their exported symbols (confidence boost for cross-batch edges):
```json
{}
```

Files to analyze in this batch (every entry MUST be passed through to `batchFiles` with all four fields — `path`, `language`, `sizeLines`, `fileCategory`):
1. `research/test-time-compute-guide/ref_impl/__init__.py` (23 lines, language: `python`, fileCategory: `code`)
2. `research/test-time-compute-guide/ref_impl/adaptive_budget.py` (99 lines, language: `python`, fileCategory: `code`)
3. `research/test-time-compute-guide/ref_impl/best_of_n.py` (46 lines, language: `python`, fileCategory: `code`)
4. `research/test-time-compute-guide/ref_impl/iterative_revision.py` (64 lines, language: `python`, fileCategory: `code`)
5. `research/test-time-compute-guide/ref_impl/majority_vote.py` (54 lines, language: `python`, fileCategory: `code`)
6. `research/test-time-compute-guide/ref_impl/tests/conftest.py` (61 lines, language: `python`, fileCategory: `code`)
7. `research/test-time-compute-guide/ref_impl/tests/test_adaptive_budget.py` (55 lines, language: `python`, fileCategory: `code`)
8. `research/test-time-compute-guide/ref_impl/tests/test_best_of_n.py` (28 lines, language: `python`, fileCategory: `code`)
9. `research/test-time-compute-guide/ref_impl/tests/test_iterative_revision.py` (27 lines, language: `python`, fileCategory: `code`)
10. `research/test-time-compute-guide/ref_impl/tests/test_majority_vote.py` (35 lines, language: `python`, fileCategory: `code`)
11. `research/test-time-compute-guide/ref_impl/tests/test_weighted_majority.py` (39 lines, language: `python`, fileCategory: `code`)
12. `research/test-time-compute-guide/ref_impl/types.py` (40 lines, language: `python`, fileCategory: `code`)
13. `research/test-time-compute-guide/ref_impl/weighted_majority.py` (64 lines, language: `python`, fileCategory: `code`)
