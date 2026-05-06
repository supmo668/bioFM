# PR Draft — `cellforge-agents` preflight hook + BioFM tool injection

> Body for a `gh pr create` against the upstream CellForge repo (or the
> companion `libs/cellforge-agents/` if it lives in the same repo).
> Author-side checklist at the bottom.

## Title

> Add `cellforge preflight` CLI hook + BioFM-backed Literature / Validator tools

## Summary

- Adds a `cellforge preflight "<perturbation>" --modality scRNA-seq`
  subcommand that runs one shallow orchestration round, serialises the
  resulting round-0 `(confidences, critique_severities, winner_index,
  consensus_score)` tuple, and prints it as JSON suitable for piping
  into a downstream recommender.
- Adds two optional tool implementations behind a lazy-import flag:
  - `cellforge.tools.biogpt_literature` → wraps `microsoft/BioGPT` for
    pathway + expected-up/down retrieval, replacing
    `cellforge.tools.literature.LiteratureTool` when `trust_biofm=True`.
  - `cellforge.tools.geneformer_validator` → wraps
    `ctheodoris/Geneformer` gene embeddings for DEG-agreement scoring,
    replacing `cellforge.tools.pathway.PathwayTool`.
- Both tools satisfy the existing tool contracts used by
  `LiteratureAgent` and `ValidatorAgent`; no orchestrator changes.

## Motivation

CellForge currently ships rule-based tool implementations that return
canned answers for a hardcoded gene list (GSK3B, TP53, …). For real
Perturb-seq targets (BHLHE40, CREB1, DDIT3, EP300, SNAI1, SPI1, ZNF326
in Adamson 2016) the rule-based `LiteratureTool` returns `"unknown"`
pathways and the agent defaults to low confidence. The BioFM-backed
variants produce real pathway text (BioGPT generation) and real DEG
similarity scores (Geneformer cosine), restoring agent confidence to
levels that reflect actual domain knowledge.

## Files added

```
cellforge/tools/biogpt_literature.py        # BioGPT mechanism + search
cellforge/tools/geneformer_validator.py     # Geneformer-backed validate()
cellforge/cli.py                            # extended with `preflight` subcommand
tests/test_preflight.py                     # unit-tests the JSON shape
```

## Design notes

- **Lazy imports.** Both tool modules gate on
  `importlib.util.find_spec("transformers") is not None and find_spec("torch")`.
  CellForge still installs without torch / transformers; users opt in
  via `pip install cellforge-agents[biofm]`.
- **Weight caching.** Tools respect `HF_CACHE_DIR` / `TRANSFORMERS_CACHE`
  so running inside a Modal volume is straightforward.
- **Preflight CLI.** `cellforge preflight "GSK3B knockdown" --modality
  scRNA-seq` prints a JSON object with
  `{confidences, critique_severities, winner_index, consensus_score,
  agent_names}` — exactly the input expected by
  `perturb_eval.experiments.common.probe_signature_from_trace`.

## Validation

- New `tests/test_preflight.py` checks the CLI output shape + that the
  preflight JSON round-trips through the downstream probe projector.
- BioFM tool tests are marked `@pytest.mark.biofm` and skip automatically
  if `transformers` is not installed.
- Live smoke: `cellforge preflight "DDIT3 knockdown" --modality scRNA-seq`
  with the BioGPT backend produces a plausible probe in < 5 s on CPU.

## Test plan

- [ ] `pytest -q` passes on core install (no torch).
- [ ] `pip install -e .[biofm] && pytest -q -m biofm` passes.
- [ ] `cellforge preflight "GSK3B knockdown" --modality scRNA-seq` prints valid JSON.
- [ ] Output plugs into
      `perturb_eval.experiments.common.probe_signature_from_trace`
      without modification.

## Author-side checklist before `gh pr create`

- [ ] Confirm whether upstream CellForge accepts BioFM tools or prefers
      them live in a separate package (`cellforge-biofm`).
- [ ] Create a branch on the CellForge repo or its fork.
- [ ] Copy the two new tool modules + CLI extension.
- [ ] Squash-commit, push.
- [ ] `gh pr create --repo <owner>/cellforge-agents --title "Preflight hook + BioFM tools" --body "$(cat research/pr_drafts/cellforge_preflight_hook.md)"`
