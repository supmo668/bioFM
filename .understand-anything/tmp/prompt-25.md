Analyze these files and produce GraphNode and GraphEdge objects.
Project root: `/Users/mo/github/personal/bioFM`
Project: `bioFM` — A living monorepo workspace for Biological Foundation Models (DNA, RNA, protein, single-cell, multimodal) that pairs a curated research landscape (MODELS.md, a test-time compute primer, pinned upstream submodules) with runnable Python packages: a test-time compute scaling library for BioFM-265M, a 5-agent propose-critique-vote orchestrator (cellforge-agents), and the paper-bearing perturb-seq-eval project on Bayesian agentic hyperparameter tuning.
Languages: `bib, html, json, jsonl, makefile, markdown, python, tex, toml, yaml`
Batch: `25/28`
Skill directory (for bundled scripts): `/Users/mo/.claude/plugins/cache/understand-anything/understand-anything/2.8.0/skills/understand`
Output: write to `/Users/mo/github/personal/bioFM/.understand-anything/intermediate/batch-25.json` (single-file mode) OR `batch-25-part-<k>.json` (split mode, per Step B of your output protocol).

**IMPORTANT — output file naming:** the output file MUST be named exactly `batch-25.json` (or `batch-25-part-<k>.json`). Any other name is silently dropped by the merge script.

**Additional context from main session:**

Project: `bioFM` — A living monorepo workspace for Biological Foundation Models (DNA, RNA, protein, single-cell, multimodal) that pairs a curated research landscape (MODELS.md, a test-time compute primer, pinned upstream submodules) with runnable Python packages: a test-time compute scaling library for BioFM-265M, a 5-agent propose-critique-vote orchestrator (cellforge-agents), and the paper-bearing perturb-seq-eval project on Bayesian agentic hyperparameter tuning.
Languages: `bib, html, json, jsonl, makefile, markdown, python, tex, toml, yaml`
Frameworks: PyTorch, Transformers, scikit-learn, Pydantic, Typer, pytest, Modal

> **Language directive**: Generate all textual content (summaries, descriptions, tags, titles, languageNotes, languageLesson) in **English**. Maintain technical accuracy while using natural, native-level phrasing in the target language. Keep technical terms in English when no standard translation exists (e.g., "middleware", "hook", "barrel").

Pre-resolved import data for this batch (use directly — do NOT re-resolve imports from source):
```json
{
 "projects/perturb-seq-eval/CITATION.cff": [],
 "projects/perturb-seq-eval/configs/live.yaml": [],
 "projects/perturb-seq-eval/docs/plans/2026-04-22-end-to-end-agentic-lifecycle.md": [],
 "projects/perturb-seq-eval/examples/end_to_end.py": [],
 "projects/perturb-seq-eval/massgen_skill_draft/patches/add-difficulty-metrics.patch": [],
 "projects/perturb-seq-eval/massgen_skill_draft/patches/PR_DESCRIPTION.md": [],
 "projects/perturb-seq-eval/massgen_skill_draft/prompts/severity_rater.md": [],
 "projects/perturb-seq-eval/paper/paper.aux": [],
 "projects/perturb-seq-eval/paper/paper.bbl": [],
 "projects/perturb-seq-eval/paper/paper.blg": [],
 "projects/perturb-seq-eval/paper/paper.out": [],
 "projects/perturb-seq-eval/paper/paper.tex": [],
 "projects/perturb-seq-eval/paper/README.md": [],
 "projects/perturb-seq-eval/paper/references.bib": [],
 "projects/perturb-seq-eval/paper/sections/v050_experimental_setup.tex": [],
 "projects/perturb-seq-eval/paper/sections/v050_results_filled.tex": [],
 "projects/perturb-seq-eval/paper/sections/v050_results.tex": [],
 "projects/perturb-seq-eval/paper/tables/tab1_metric_correlations.tex": [],
 "projects/perturb-seq-eval/paper/tables/tab2_calibration_improvement.tex": [],
 "projects/perturb-seq-eval/paper/tables/tab3_probe_to_target.tex": [],
 "projects/perturb-seq-eval/paper/tables/tab4_agent_scaling.tex": [],
 "projects/perturb-seq-eval/paper/tables/tab5_pareto_samples.tex": [],
 "projects/perturb-seq-eval/scripts/fetch_adamson.py": [],
 "projects/perturb-seq-eval/scripts/live_smoke.py": [],
 "projects/perturb-seq-eval/scripts/local/analyze_lifecycle_results.py": []
}
```

Cross-batch neighbors with their exported symbols (confidence boost for cross-batch edges):
```json
{}
```

Files to analyze in this batch (every entry MUST be passed through to `batchFiles` with all four fields — `path`, `language`, `sizeLines`, `fileCategory`):
1. `projects/perturb-seq-eval/CITATION.cff` (180 lines, language: `cff`, fileCategory: `code`)
2. `projects/perturb-seq-eval/configs/live.yaml` (76 lines, language: `yaml`, fileCategory: `config`)
3. `projects/perturb-seq-eval/docs/plans/2026-04-22-end-to-end-agentic-lifecycle.md` (1975 lines, language: `markdown`, fileCategory: `docs`)
4. `projects/perturb-seq-eval/examples/end_to_end.py` (89 lines, language: `python`, fileCategory: `code`)
5. `projects/perturb-seq-eval/massgen_skill_draft/patches/add-difficulty-metrics.patch` (854 lines, language: `patch`, fileCategory: `code`)
6. `projects/perturb-seq-eval/massgen_skill_draft/patches/PR_DESCRIPTION.md` (125 lines, language: `markdown`, fileCategory: `docs`)
7. `projects/perturb-seq-eval/massgen_skill_draft/prompts/severity_rater.md` (37 lines, language: `markdown`, fileCategory: `docs`)
8. `projects/perturb-seq-eval/paper/paper.aux` (170 lines, language: `aux`, fileCategory: `code`)
9. `projects/perturb-seq-eval/paper/paper.bbl` (209 lines, language: `bbl`, fileCategory: `code`)
10. `projects/perturb-seq-eval/paper/paper.blg` (46 lines, language: `blg`, fileCategory: `code`)
11. `projects/perturb-seq-eval/paper/paper.out` (28 lines, language: `out`, fileCategory: `code`)
12. `projects/perturb-seq-eval/paper/paper.tex` (625 lines, language: `tex`, fileCategory: `code`)
13. `projects/perturb-seq-eval/paper/README.md` (99 lines, language: `markdown`, fileCategory: `docs`)
14. `projects/perturb-seq-eval/paper/references.bib` (222 lines, language: `bib`, fileCategory: `code`)
15. `projects/perturb-seq-eval/paper/sections/v050_experimental_setup.tex` (98 lines, language: `tex`, fileCategory: `code`)
16. `projects/perturb-seq-eval/paper/sections/v050_results_filled.tex` (93 lines, language: `tex`, fileCategory: `code`)
17. `projects/perturb-seq-eval/paper/sections/v050_results.tex` (93 lines, language: `tex`, fileCategory: `code`)
18. `projects/perturb-seq-eval/paper/tables/tab1_metric_correlations.tex` (11 lines, language: `tex`, fileCategory: `code`)
19. `projects/perturb-seq-eval/paper/tables/tab2_calibration_improvement.tex` (8 lines, language: `tex`, fileCategory: `code`)
20. `projects/perturb-seq-eval/paper/tables/tab3_probe_to_target.tex` (8 lines, language: `tex`, fileCategory: `code`)
21. `projects/perturb-seq-eval/paper/tables/tab4_agent_scaling.tex` (9 lines, language: `tex`, fileCategory: `code`)
22. `projects/perturb-seq-eval/paper/tables/tab5_pareto_samples.tex` (11 lines, language: `tex`, fileCategory: `code`)
23. `projects/perturb-seq-eval/scripts/fetch_adamson.py` (49 lines, language: `python`, fileCategory: `code`)
24. `projects/perturb-seq-eval/scripts/live_smoke.py` (228 lines, language: `python`, fileCategory: `code`)
25. `projects/perturb-seq-eval/scripts/local/analyze_lifecycle_results.py` (79 lines, language: `python`, fileCategory: `code`)
