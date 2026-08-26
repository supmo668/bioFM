Analyze these files and produce GraphNode and GraphEdge objects.
Project root: `/Users/mo/github/personal/bioFM`
Project: `bioFM` — A living monorepo workspace for Biological Foundation Models (DNA, RNA, protein, single-cell, multimodal) that pairs a curated research landscape (MODELS.md, a test-time compute primer, pinned upstream submodules) with runnable Python packages: a test-time compute scaling library for BioFM-265M, a 5-agent propose-critique-vote orchestrator (cellforge-agents), and the paper-bearing perturb-seq-eval project on Bayesian agentic hyperparameter tuning.
Languages: `bib, html, json, jsonl, makefile, markdown, python, tex, toml, yaml`
Batch: `23/28`
Skill directory (for bundled scripts): `/Users/mo/.claude/plugins/cache/understand-anything/understand-anything/2.8.0/skills/understand`
Output: write to `/Users/mo/github/personal/bioFM/.understand-anything/intermediate/batch-23.json` (single-file mode) OR `batch-23-part-<k>.json` (split mode, per Step B of your output protocol).

**IMPORTANT — output file naming:** the output file MUST be named exactly `batch-23.json` (or `batch-23-part-<k>.json`). Any other name is silently dropped by the merge script.

**Additional context from main session:**

Project: `bioFM` — A living monorepo workspace for Biological Foundation Models (DNA, RNA, protein, single-cell, multimodal) that pairs a curated research landscape (MODELS.md, a test-time compute primer, pinned upstream submodules) with runnable Python packages: a test-time compute scaling library for BioFM-265M, a 5-agent propose-critique-vote orchestrator (cellforge-agents), and the paper-bearing perturb-seq-eval project on Bayesian agentic hyperparameter tuning.
Languages: `bib, html, json, jsonl, makefile, markdown, python, tex, toml, yaml`
Frameworks: PyTorch, Transformers, scikit-learn, Pydantic, Typer, pytest, Modal

> **Language directive**: Generate all textual content (summaries, descriptions, tags, titles, languageNotes, languageLesson) in **English**. Maintain technical accuracy while using natural, native-level phrasing in the target language. Keep technical terms in English when no standard translation exists (e.g., "middleware", "hook", "barrel").

Pre-resolved import data for this batch (use directly — do NOT re-resolve imports from source):
```json
{
 ".env.example": [],
 ".gitmodules": [],
 ".understand-anything/.understandignore": [],
 ".understand-anything/config.json": [],
 ".understand-anything/tmp/ua-scan-stderr.txt": [],
 "docs/superpowers/plans/2026-05-15-scilab-virtual-lab.md": [],
 "libs/cellforge-agents/examples/perturbation_run.py": [],
 "libs/cellforge-agents/tests/test_agents.py": [],
 "libs/cellforge-agents/tests/test_orchestrator.py": [],
 "libs/cellforge-agents/tests/test_tools.py": [],
 "libs/test-time-compute/examples/ttc_sweep.py": [],
 "libs/test-time-compute/src/ttc/model_loader.py": [],
 "libs/test-time-compute/tests/conftest.py": [],
 "libs/test-time-compute/tests/test_runner_smoke.py": [],
 "libs/test-time-compute/tests/test_scoring.py": [],
 "libs/test-time-compute/tests/test_strategies.py": [],
 "paper_standalone/.github/workflows/latex.yml": [],
 "paper_standalone/experiments/generate_tables.py": [],
 "paper_standalone/experiments/plot.py": [],
 "paper_standalone/experiments/simulate.py": [],
 "paper_standalone/Makefile": [],
 "paper_standalone/paper.tex": [],
 "paper_standalone/README.md": [],
 "paper_standalone/references.bib": [],
 "paper_standalone/src/perturb_eval/_env.py": []
}
```

Cross-batch neighbors with their exported symbols (confidence boost for cross-batch edges):
```json
{}
```

Files to analyze in this batch (every entry MUST be passed through to `batchFiles` with all four fields — `path`, `language`, `sizeLines`, `fileCategory`):
1. `.env.example` (43 lines, language: `config`, fileCategory: `config`)
2. `.gitmodules` (15 lines, language: `unknown`, fileCategory: `code`)
3. `.understand-anything/.understandignore` (52 lines, language: `unknown`, fileCategory: `code`)
4. `.understand-anything/config.json` (1 lines, language: `json`, fileCategory: `config`)
5. `.understand-anything/tmp/ua-scan-stderr.txt` (0 lines, language: `txt`, fileCategory: `docs`)
6. `docs/superpowers/plans/2026-05-15-scilab-virtual-lab.md` (2583 lines, language: `markdown`, fileCategory: `docs`)
7. `libs/cellforge-agents/examples/perturbation_run.py` (38 lines, language: `python`, fileCategory: `code`)
8. `libs/cellforge-agents/tests/test_agents.py` (120 lines, language: `python`, fileCategory: `code`)
9. `libs/cellforge-agents/tests/test_orchestrator.py` (64 lines, language: `python`, fileCategory: `code`)
10. `libs/cellforge-agents/tests/test_tools.py` (76 lines, language: `python`, fileCategory: `code`)
11. `libs/test-time-compute/examples/ttc_sweep.py` (57 lines, language: `python`, fileCategory: `code`)
12. `libs/test-time-compute/src/ttc/model_loader.py` (57 lines, language: `python`, fileCategory: `code`)
13. `libs/test-time-compute/tests/conftest.py` (52 lines, language: `python`, fileCategory: `code`)
14. `libs/test-time-compute/tests/test_runner_smoke.py` (31 lines, language: `python`, fileCategory: `code`)
15. `libs/test-time-compute/tests/test_scoring.py` (78 lines, language: `python`, fileCategory: `code`)
16. `libs/test-time-compute/tests/test_strategies.py` (82 lines, language: `python`, fileCategory: `code`)
17. `paper_standalone/.github/workflows/latex.yml` (54 lines, language: `yaml`, fileCategory: `config`)
18. `paper_standalone/experiments/generate_tables.py` (170 lines, language: `python`, fileCategory: `code`)
19. `paper_standalone/experiments/plot.py` (184 lines, language: `python`, fileCategory: `code`)
20. `paper_standalone/experiments/simulate.py` (619 lines, language: `python`, fileCategory: `code`)
21. `paper_standalone/Makefile` (44 lines, language: `makefile`, fileCategory: `infra`)
22. `paper_standalone/paper.tex` (757 lines, language: `tex`, fileCategory: `code`)
23. `paper_standalone/README.md` (133 lines, language: `markdown`, fileCategory: `docs`)
24. `paper_standalone/references.bib` (239 lines, language: `bib`, fileCategory: `code`)
25. `paper_standalone/src/perturb_eval/_env.py` (50 lines, language: `python`, fileCategory: `code`)
