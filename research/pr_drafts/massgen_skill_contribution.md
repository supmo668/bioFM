# PR Draft — MassGen `perturb-seq-eval` skill contribution

> Body for a `gh pr create` against the upstream MassGen repo
> (`Leezekun/MassGen` or the forked pin at `tools/MassGen/`). Paste this
> into the PR description when the author is ready to push. Author-side
> checklist at the bottom.

## Title

> Add `perturb-seq-eval` skill: contextual BO for multi-agent HPO + live-probe collector for perturb-seq experimental design

## Summary

- Ships a MassGen-installable **evaluation skill** under
  `massgen/skills/perturb-seq-eval/` that wraps any MassGen
  `propose→critique→vote` run and emits per-round (ACE, ACE_D, CSD,
  CSD★, ΔACE, ΔC, WFR, CST) metrics plus a composite Task Difficulty
  Index (TDI).
- Ships a **preflight recommender** (`preflight_skill`) that harvests a
  round-0 probe signature via the MassGen CoordinationTracker and
  returns a hyperparameter-tuning recommendation `(n_agents, n_rounds,
  backbone)` under a FLOPs-budget constraint.
- Ships a **live-probe collector** (`scripts/modal/app_biofm.py`) that
  runs a 5-agent CellForge-style orchestrator with **BioGPT** as the
  Literature tool and **Geneformer** as the Validator tool (both pulled
  from HuggingFace Hub), then uses OpenRouter Nemotron free-tier as the
  severity + confidence rater to produce a calibrated 4-dim probe per
  perturbation.
- Reproducibility: `modal run` one-liner against cached Adamson 2016
  Perturb-seq pilot; total spend ≤ $10; full supplement in
  [`docs/SUPPLEMENT.md`](docs/SUPPLEMENT.md).

## What this upstream skill gives MassGen users

Three things any multi-agent run can now opt into:

1. **Observability** — drop the metrics module into a MassGen session to
   get per-round ACE/CSD/ΔC/WFR/TDI without touching the agent code. The
   schema is a narrow 4-field trace contract; MassGen's
   `CoordinationTracker` populates it via a ≈ 40-line projection.
2. **Adaptive compute allocation** — the preflight probe + Bayesian
   recommender route compute per task. On DGPs with task-conditional
   structure, the contextual GP dominates non-contextual CMA-ES by
   **7.6× on final MSD** (95 % CIs non-overlapping).
3. **Falsification discipline** — on DGPs without routable structure
   (synthetic shared-optimum, real Adamson pilot) the framework reports
   CI-overlap correctly and does *not* claim an advantage. Useful as a
   sanity check for users' own agent-routing pipelines.

## Files added

```
massgen/skills/perturb-seq-eval/
├── SKILL.md                    # agent-facing description
├── skill.yaml                  # MassGen skill manifest
├── prompts/severity_rater.md   # LLM prompt used by the projector
├── extractors/
│   ├── confidence.py           # vote-share projection
│   └── severity.py             # LLM-based severity extractor
└── handlers/
    ├── preflight.py            # wraps preflight_skill()
    └── evaluate.py             # wraps evaluate_skill()
```

Draft lives at
[`projects/perturb-seq-eval/massgen_skill_draft/`](projects/perturb-seq-eval/massgen_skill_draft/)
in the companion repo; this PR is the minimal upstream landing.

## Design notes

- **No changes to MassGen core.** The skill is pure-additive under
  `massgen/skills/`; no orchestrator patches.
- **Anti-pattern compliance.** The severity extractor follows MassGen's
  own rule that category/similarity projection must use an LLM, not
  keyword matching. Prompt in `prompts/severity_rater.md`.
- **Optional dependency.** Only consumers that install the skill need
  `numpy` and `typer`; the core MassGen install is untouched.

## Validation

- 92/92 pytest green in the companion repo (contextual-GP + ES + random
  optimizer kernels, bootstrap CIs, γ_T numerical estimator, probe
  extractor).
- Live-probe collection validated on 7 Adamson targeted-knockdown
  perturbations; full prompt→response audit in
  [`artifacts/real_probes/adamson_traces.jsonl`](projects/perturb-seq-eval/artifacts/real_probes/adamson_traces.jsonl).
- Regret bound `R_T = O(√(T γ_T))` (Krause & Ong 2011) estimated
  numerically per regime; γ_T = 37.36 on live Adamson probes, 53.97 on
  task-conditional synthetic DGP, 56.17 on shared-optimum synthetic.

## Test plan

- [ ] `python -m perturb_eval.experiments.e1_metric_overlap` runs (n = 5000).
- [ ] `python scripts/local/bootstrap_and_analyze.py` reproduces CIs.
- [ ] `modal deploy scripts/modal/app.py && modal run … --step all` reproduces E2 + E3 + figures.
- [ ] `python scripts/local/collect_real_probes.py` reproduces the live-probe trace on Adamson (needs `OPENROUTER_API_KEY`).
- [ ] `modal run scripts/modal/app_biofm.py::entrypoint --step all` reproduces the BioFM-grounded variant (needs `OPENROUTER_API_KEY` and HF pull rights).

## Companion documentation

- Thesis: [`docs/THESIS.md`](docs/THESIS.md)
- Engineering design: [`docs/DESIGN.md`](docs/DESIGN.md)
- Supplement: [`docs/SUPPLEMENT.md`](docs/SUPPLEMENT.md)
- Reviewer critique (what's weak, tracked): [`docs/REVIEWER_CRITIQUE.md`](docs/REVIEWER_CRITIQUE.md)

## Author-side checklist before `gh pr create`

- [ ] Fork `Leezekun/MassGen` on GitHub.
- [ ] `git checkout -b skill/perturb-seq-eval` on the fork.
- [ ] Copy `projects/perturb-seq-eval/massgen_skill_draft/*` into `massgen/skills/perturb-seq-eval/`.
- [ ] Ensure `massgen/configs/skills/perturb-seq-eval.yaml` loads the skill.
- [ ] Squash-commit, push the branch.
- [ ] `gh pr create --repo Leezekun/MassGen --title "Add perturb-seq-eval skill" --body "$(cat research/pr_drafts/massgen_skill_contribution.md)"`
