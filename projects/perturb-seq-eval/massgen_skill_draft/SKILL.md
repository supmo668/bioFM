---
name: perturb-seq-eval
description: >
  Observability and Bayesian agentic hyperparameter tuning for
  propose-critique-vote orchestrators. Produces per-round metrics
  (ACE, CSD, ΔACE, ΔC, WFR, TDI) from a CoordinationTracker snapshot,
  and recommends (n_agents, n_rounds, backbone) for follow-up runs.
category: evaluation
requires_api_keys: []
tasks:
  - "Score the difficulty of a completed multi-agent session via TDI."
  - "Recommend a configuration for a follow-up run under a FLOPs budget."
  - "Compute Agent Confidence Entropy and Critique Severity Dispersion
     trajectories for diagnostic inspection."
keywords:
  - evaluation
  - agentic-hyperparameter-tuning
  - test-time-compute
  - perturb-seq
  - observability
---

# perturb-seq-eval

A diagnostic + routing skill for MassGen that reads its own coordination
tracker output and emits two things:

1. **Run metrics.** `ACE` (Agent Confidence Entropy), `CSD` (Critique
   Severity Dispersion), `ΔACE`, `ΔC`, `WFR`, and a composite `TDI`
   (Task Difficulty Index). These summarise how well the propose-critique-vote
   loop converged and how hard the task was.

2. **Pre-flight recommendation.** Given a cheap round-0 probe, return the
   configuration $(n_{\mathrm{agents}}, n_{\mathrm{rounds}},
   \mathrm{backbone})$ with the highest expected utility under a compute
   budget, using a calibrated Bayesian recommender.

## Agent-facing invocation

This skill is invoked by MassGen's orchestrator at two lifecycle points:

- `on_session_start`: runs the preflight handler; recommendation is written
  to `artifacts/recommendation.json` where the orchestrator can consult it
  before launching downstream agents.
- `on_session_end`: runs the evaluate handler; metrics are written to
  `artifacts/run_metrics.json` and logged through
  `massgen.structured_logging`.

Agents do not need to call this skill directly. It is a framework-level
observer that the orchestrator injects.

## What the skill does NOT do

- It does not train or fine-tune any model.
- It does not access any perturb-seq dataset at runtime — the "perturb-seq"
  framing is historical (the metrics were developed on a perturb-seq
  testbed) but the skill is task-agnostic and applies to any
  propose-critique-vote session.
- It does not run an LLM for metric computation. Only the severity
  projection in `extractors/severity.py` uses an LLM, and only when
  the trace does not already expose numeric severity fields.

## Dependencies

- `perturb-eval` (this project) — core metrics, probe, recommender.
- `massgen.coordination_tracker` — source of the `AgentAnswer` / `AgentVote`
  records the extractor consumes.

## Reference

See the paper at `paper/paper.pdf` of the `perturb-seq-eval` project for
theoretical background and empirical validation of the metrics.
