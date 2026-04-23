# Draft MassGen Skill: `perturb-seq-eval`

**Status:** draft artifact. **Not** installed upstream. This directory
mirrors the layout a real MassGen PR would use
(`massgen/skills/perturb-seq-eval/`). We keep it in our project so reviewers
can inspect the shape without modifying the pinned
[`tools/MassGen/`](../../../tools/MassGen/) submodule.

When this is ready for upstream, the submission path is:

1. Fork [`Leezekun/MassGen`](https://github.com/Leezekun/MassGen).
2. Copy this directory into `massgen/skills/perturb-seq-eval/`.
3. Open an OpenSpec change proposal under `openspec/changes/` describing
   the new observability skill (see MassGen's `AGENTS.md` for the OpenSpec
   workflow).
4. Add a `massgen/configs/skills/skills_with_eval.yaml` enabling the skill.
5. Follow MassGen's TDD contract: add acceptance tests under
   `massgen/tests/` for the coordination-tracker → run-trace extractor.
6. Submit the PR.

## Files in this draft

| File | Purpose |
|---|---|
| [`SKILL.md`](SKILL.md) | Agent-facing description of what the skill does, consistent with MassGen's existing skill READMEs (e.g. `massgen/skills/file-search/`). |
| [`skill.yaml`](skill.yaml) | Skill manifest: inputs, outputs, and which handlers fire on which lifecycle event. |
| [`prompts/severity_rater.md`](prompts/severity_rater.md) | LLM-prompt for projecting a free-text `AgentVote.reason` onto a severity score. |
| [`extractors/confidence.py`](extractors/confidence.py) | Vote-share projection of per-agent confidence (no LLM). |
| [`extractors/severity.py`](extractors/severity.py) | LLM-driven severity projection using the prompt above. |
| [`handlers/preflight.py`](handlers/preflight.py) | Runs the Bayesian recommender from our perturb-eval package. |
| [`handlers/evaluate.py`](handlers/evaluate.py) | Runs ACE/CSD/TDI on a completed session. |

All Python in this directory depends on the
[`perturb_eval`](../src/perturb_eval/) package, which would enter MassGen's
dependency graph as an extra via
`pip install 'perturb-eval@git+https://github.com/…'`.

## Anti-pattern compliance

MassGen's `CLAUDE.md` explicitly forbids keyword/regex heuristics for
categorisation or similarity. Our severity extractor therefore uses a
short LLM prompt (see [`prompts/severity_rater.md`](prompts/severity_rater.md))
rather than a regex over vote reasons. This is intentional.

## Testing the extractor

The extractors are pure functions over MassGen's native dataclasses
(`CoordinationTracker`, `AgentAnswer`, `AgentVote`). They can be unit-tested
without running a real LLM by swapping in a deterministic stub backend — the
same pattern MassGen's own tests use (`massgen/tests/`). An acceptance-test
skeleton is in [`extractors/test_extractors_skeleton.py`](extractors/test_extractors_skeleton.py).
