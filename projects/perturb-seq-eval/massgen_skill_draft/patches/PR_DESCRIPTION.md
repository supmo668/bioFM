# [FEATURE] Add Difficulty-Metrics Learning System

Closes MAS-XXX (to be filed).

## TL;DR

Adds `massgen.learning.DifficultyMetricsObserver`, an opt-in observer over
existing `CoordinationTracker` events that computes four interpretable
metrics per round — Agent Confidence Entropy (ACE), Critique Severity
Dispersion (CSD), Winner Flip Rate (WFR), and a composite Task Difficulty
Index (TDI). Enabled via the new coordination flag
`learning_difficulty_metrics`. No existing behaviour is changed; no new
third-party dependency is introduced.

## How to apply this patch

```bash
cd MassGen  # your local fork
git checkout -b add-difficulty-metrics
git apply /path/to/add-difficulty-metrics.patch
pip install -e .
uv run pytest massgen/tests/unit/test_difficulty_metrics.py -q
uv run massgen --automation --config massgen/configs/learning/difficulty_metrics.yaml "design a CRISPRi screen for the IRE1 branch of the UPR"
```

## Motivation

Today MassGen propose-critique-vote runs emit rich categorical telemetry
(`AgentAnswer.content`, `AgentVote.voted_for`, `AgentVote.reason`) but no
interpretable scalar summary of "how hard was this task for this team?"
A post-run scalar enables:

1. **Run-to-run comparability.** Operators currently compare runs by
   eyeballing trajectories; TDI gives a 0-1 score.
2. **Adaptive orchestration (follow-up PR).** TDI can power a Bayesian
   recommender that picks `(n_agents, n_rounds, backbones)` before a full
   run — the multi-agent analogue of Snell et al. 2024's compute-optimal
   per-prompt TTC allocation.
3. **Evolving-skill creator input.** The existing `evolving-skill-creator`
   skill can use TDI to prioritise evolution on harder tasks.

## What the metrics are

For a run of `R` rounds with `N` agents, at round `r` we observe per-agent
vote shares `p(r) = softmax(votes_received / N)` and per-vote severities
`S_ij(r) ∈ [0,1]`:

- **ACE** — normalised Shannon entropy of `p(r)`. Low = decisive; high = contested.
- **CSD** — population variance of `S(r)` entries.
- **WFR** — fraction of consecutive rounds where the winner changed.
- **TDI** — convex combination:
  `TDI = α·ACE + β·CSD + γ·(1-ΔC) + δ·WFR` with weights that sum to 1.

Severity is obtained from an injectable rater:
- **Default rater** — `sev = 1 - vote_share(target)`; deterministic; no LLM.
- **Injected LLM rater** — follows the project's anti-pattern rule
  (`CLAUDE.md § Anti-Patterns`) by delegating free-text `AgentVote.reason`
  rating to an LLM rather than regex/keyword matching.

## Scope of changes

### Files added (6)

| File | Purpose |
|---|---|
| `massgen/learning/__init__.py` | Re-exports the public API. |
| `massgen/learning/difficulty_metrics.py` | Observer + metric math (pure stdlib). |
| `massgen/configs/learning/difficulty_metrics.yaml` | Example config. |
| `massgen/tests/unit/test_difficulty_metrics.py` | 14 unit tests across 7 classes. |
| `openspec/changes/add-difficulty-metrics/proposal.md` | OpenSpec change spec. |
| `openspec/changes/add-difficulty-metrics/tasks.md` | Task checklist + validation commands. |

### Files modified (2)

Per `CLAUDE.md § Configuration` rule for new coordination params — update
all three: dataclass field, `cli._parse_coordination_config`, and
`to_dict()`.

| File | Change |
|---|---|
| `massgen/agent_config.py` | +6 fields on `CoordinationConfig`; +6 lines in `AgentConfig.to_dict()`. |
| `massgen/cli.py` | +6 lines in `_parse_coordination_config()`. |

No changes to `orchestrator.py`, `chat_agent.py`, any backend, or
`coordination_tracker.py`.

## Test plan

- `uv run pytest massgen/tests/unit/test_difficulty_metrics.py -q` ⇒ **14 passing** locally.
- Unit tests cover: vote-share projection, ACE math, default severity rater,
  custom LLM rater injection, multi-round aggregation, winner flip rate,
  TDI bounds, TDI coefficient validation, JSON serialisation shape.
- Coefficient validation: `TDICoefficients(...)` raises `ValueError` unless
  weights sum to 1.0.
- Integration smoke test with `--automation` on the shipped example config
  is deferred to a follow-up PR — the unit tests fully cover the
  observer's math, and the orchestrator wiring (the one call site that
  needs to invoke `on_round_end`) is small and can be landed behind a
  feature flag.

## Anti-pattern compliance

Per `CLAUDE.md § Anti-Patterns`:

- ✅ **No keyword/heuristic matching for categorisation.** The default
  rater is a deterministic projection over vote-shares; the LLM rater is
  delegated to a model.
- ✅ **No explicit tool-call syntax in prompts.** This PR adds no prompts.
- ✅ **TDD.** Tests committed alongside the code and fail cleanly when
  the implementation is removed.

## Backwards compatibility

- New flag defaults to `false`. All existing configs continue to work
  unchanged.
- `AgentConfig.to_dict()` gains six fields inside the existing
  `coordination_config` block; the JSON schema is additive.
- No existing field is renamed or removed.

## What's Next

A follow-up OpenSpec proposal (`add-difficulty-recommender`) will consume
this observer's output to power a Bayesian recommender that selects
`(n_agents, n_rounds, backbones)` configurations. The orchestrator wiring
for feeding `on_round_end` during a live session is also a follow-up PR.
