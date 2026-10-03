---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-09-24T19:21
status: created
priority: normal
size: task
subject: "plan-ready: perturb-seq-eval (#202 + #227)"
in_reply_to: null
---

# plan-ready: perturb-seq-eval (#202 + #227)

workstream: perturb-seq-eval
plan_path: workstreams/perturb-seq-eval/plan/build-plan.md
approval: plan/plan-approval.md
phase: build-ready
audience: agent-ready
hint: /build
next: /build

Committed at b694889. A&D approved by the principal (workstreams/perturb-seq-eval/AND.md, D1-D5); plan r3 signed (hash 418cc1e) after /grill-me.
- Scope: #202 + #227 (T8b: HVG train-only in BOTH loaders, property-pinned test, provenance mode + n_hvg/params per task, stated per-task-feature-space consequence; top-20 DEG untouched).
- D1 multi-target doublets (tuple target_gene_idx; Norman keeps 15+5). D2 artifacts/v0.6.0/ (v0.5.0 untouched). D4 A3 folded in (source llm|fallback, entropy over llm rows per role).
- Sweep gates: plan-gate; OPENROUTER_API_KEY provisioned by you via Infisical (G2 — I check presence only, never read it); estimate <= $8 (~$5-6, 41 tasks, 8h timeout).
- For you: tests.referee_command is unset in agency.yaml, so sealed-referee TDD cannot run here; building with visible tests + QG reviewers (G3). Also pydantic/requests are undeclared deps and anndata/h5py need pinning (T0).
Starting /build at P0 now.
