Analyze these files and produce GraphNode and GraphEdge objects.
Project root: `/Users/mo/github/personal/bioFM`
Project: `bioFM` — A living monorepo workspace for Biological Foundation Models (DNA, RNA, protein, single-cell, multimodal) that pairs a curated research landscape (MODELS.md, a test-time compute primer, pinned upstream submodules) with runnable Python packages: a test-time compute scaling library for BioFM-265M, a 5-agent propose-critique-vote orchestrator (cellforge-agents), and the paper-bearing perturb-seq-eval project on Bayesian agentic hyperparameter tuning.
Languages: `bib, html, json, jsonl, makefile, markdown, python, tex, toml, yaml`
Batch: `28/28`
Skill directory (for bundled scripts): `/Users/mo/.claude/plugins/cache/understand-anything/understand-anything/2.8.0/skills/understand`
Output: write to `/Users/mo/github/personal/bioFM/.understand-anything/intermediate/batch-28.json` (single-file mode) OR `batch-28-part-<k>.json` (split mode, per Step B of your output protocol).

**IMPORTANT — output file naming:** the output file MUST be named exactly `batch-28.json` (or `batch-28-part-<k>.json`). Any other name is silently dropped by the merge script.

**Additional context from main session:**

Project: `bioFM` — A living monorepo workspace for Biological Foundation Models (DNA, RNA, protein, single-cell, multimodal) that pairs a curated research landscape (MODELS.md, a test-time compute primer, pinned upstream submodules) with runnable Python packages: a test-time compute scaling library for BioFM-265M, a 5-agent propose-critique-vote orchestrator (cellforge-agents), and the paper-bearing perturb-seq-eval project on Bayesian agentic hyperparameter tuning.
Languages: `bib, html, json, jsonl, makefile, markdown, python, tex, toml, yaml`
Frameworks: PyTorch, Transformers, scikit-learn, Pydantic, Typer, pytest, Modal

> **Language directive**: Generate all textual content (summaries, descriptions, tags, titles, languageNotes, languageLesson) in **English**. Maintain technical accuracy while using natural, native-level phrasing in the target language. Keep technical terms in English when no standard translation exists (e.g., "middleware", "hook", "barrel").

Pre-resolved import data for this batch (use directly — do NOT re-resolve imports from source):
```json
{
 "projects/perturb-seq-eval/tests/test_llm_agent_pool.py": [],
 "projects/perturb-seq-eval/tests/test_metrics_extended.py": [],
 "projects/perturb-seq-eval/tests/test_metrics.py": [],
 "projects/perturb-seq-eval/tests/test_model.py": [],
 "projects/perturb-seq-eval/tests/test_no_synthetic_generators.py": [],
 "projects/perturb-seq-eval/tests/test_norman_loader.py": [],
 "projects/perturb-seq-eval/tests/test_openrouter_client.py": [],
 "projects/perturb-seq-eval/tests/test_optimizers.py": [],
 "projects/perturb-seq-eval/tests/test_probe.py": [],
 "projects/perturb-seq-eval/tests/test_proposal_schema.py": [],
 "projects/perturb-seq-eval/tests/test_v05_analysis.py": [],
 "projects/perturb-seq-eval/tests/test_validator_critique.py": [],
 "README.md": [],
 "research/pr_drafts/cellforge_preflight_hook.md": [],
 "research/pr_drafts/massgen_skill_contribution.md": [],
 "research/test-time-compute-guide/GUIDE.md": [],
 "research/test-time-compute-guide/README.md": [],
 "research/test-time-compute-guide/ref_impl/tests/__init__.py": [],
 "scripts/publish/publish.yml.template": [],
 "scripts/publish/submit.py": []
}
```

Cross-batch neighbors with their exported symbols (confidence boost for cross-batch edges):
```json
{}
```

Files to analyze in this batch (every entry MUST be passed through to `batchFiles` with all four fields — `path`, `language`, `sizeLines`, `fileCategory`):
1. `projects/perturb-seq-eval/tests/test_llm_agent_pool.py` (111 lines, language: `python`, fileCategory: `code`)
2. `projects/perturb-seq-eval/tests/test_metrics_extended.py` (156 lines, language: `python`, fileCategory: `code`)
3. `projects/perturb-seq-eval/tests/test_metrics.py` (140 lines, language: `python`, fileCategory: `code`)
4. `projects/perturb-seq-eval/tests/test_model.py` (32 lines, language: `python`, fileCategory: `code`)
5. `projects/perturb-seq-eval/tests/test_no_synthetic_generators.py` (171 lines, language: `python`, fileCategory: `code`)
6. `projects/perturb-seq-eval/tests/test_norman_loader.py` (156 lines, language: `python`, fileCategory: `code`)
7. `projects/perturb-seq-eval/tests/test_openrouter_client.py` (163 lines, language: `python`, fileCategory: `code`)
8. `projects/perturb-seq-eval/tests/test_optimizers.py` (155 lines, language: `python`, fileCategory: `code`)
9. `projects/perturb-seq-eval/tests/test_probe.py` (38 lines, language: `python`, fileCategory: `code`)
10. `projects/perturb-seq-eval/tests/test_proposal_schema.py` (156 lines, language: `python`, fileCategory: `code`)
11. `projects/perturb-seq-eval/tests/test_v05_analysis.py` (187 lines, language: `python`, fileCategory: `code`)
12. `projects/perturb-seq-eval/tests/test_validator_critique.py` (135 lines, language: `python`, fileCategory: `code`)
13. `README.md` (131 lines, language: `markdown`, fileCategory: `docs`)
14. `research/pr_drafts/cellforge_preflight_hook.md` (87 lines, language: `markdown`, fileCategory: `docs`)
15. `research/pr_drafts/massgen_skill_contribution.md` (113 lines, language: `markdown`, fileCategory: `docs`)
16. `research/test-time-compute-guide/GUIDE.md` (203 lines, language: `markdown`, fileCategory: `docs`)
17. `research/test-time-compute-guide/README.md` (49 lines, language: `markdown`, fileCategory: `docs`)
18. `research/test-time-compute-guide/ref_impl/tests/__init__.py` (0 lines, language: `python`, fileCategory: `code`)
19. `scripts/publish/publish.yml.template` (71 lines, language: `template`, fileCategory: `code`)
20. `scripts/publish/submit.py` (531 lines, language: `python`, fileCategory: `code`)
