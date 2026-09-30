---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-09-28T23:09
status: created
priority: normal
size: task
subject: "SWEEP ABORTED (stop-and-report): 6/8 roster models dead on OpenRouter; ~$1.3 spent; roster + preflight fix through QG, then relaunch — cache-namespace question"
in_reply_to: null
---

# SWEEP ABORTED (stop-and-report): 6/8 roster models dead on OpenRouter; ~$1.3 spent; roster + preflight fix through QG, then relaunch — cache-namespace question

event: sweep-aborted (stop-and-report)
workstream: perturb-seq-eval
run_id: 20260928T220916Z-291efad (git_sha 291efad, git_dirty=False, prereg_version v0.6.0-a3, cache entries at start 0)
what_happened: preflight passed (8 checks; probe model nvidia/nemotron-3-super-120b-a12b:free answered). Trainer phase completed: 1107 runs = 41 tasks x 27 records (the amended grid), budget_so_far $1.24. The lifecycle phase then produced fallback steps for Literature, Architect, Trainer and Validator on the first task ("all candidate models for role failed; http 404 / empty"). Under A2-1 / C-KEY-2 a fallback step invalidates the run, so I sent SIGINT at 23:06Z (fail fast) rather than burn GPU-hours on an invalid run. App aborted; failed provenance written on the volume. Spend ~ $1.3, well under the $12 stop line. 0 lifecycle runs recorded.
root_cause: 6 of the 8 free models in the OpenRouter roster (src/perturb_eval/llm/openrouter_client.py) no longer exist on OpenRouter (verified against the public /models list, no key): dead = gemma-3-27b-it, ling-2.6-1t, llama-3.3-70b-instruct, hermes-3-llama-3.1-405b, gpt-oss-120b, qwen3-next-80b-a3b-instruct (all :free). Live = nemotron-3-super-120b-a12b:free, gemma-4-31b-it:free. The preflight probes ONE model, so dead roster entries are discovered only after the trainer phase has spent.
replay_hazard: the aborted run left entries in the v0.6.0-a3 cache namespace (36 top-level shards; DataCurator replies via a live model, never used in any recorded run — lifecycle_runs.jsonl holds 0 runs). A relaunch on that namespace would be a replay by A2-8's letter.
plan: (1) roster fix — replace the six dead IDs with live free models that answer a JSON probe (probing now with the key via infisical run; ids only, never the key); the pre-registration does not pin the roster ("rotating pool ... recorded in provenance"), so this is an implementation fix, gated by /quality-gate with a receipt (commit first, then sign). (2) preflight fix — probe EVERY roster model and refuse the run before any spend if a role has < 2 live candidates. (3) before relaunch, delete the v0.6.0-a3 namespace contents so the run starts empty as A2-8 requires, recording the deleted keys + reason in the run report; if you prefer a version bump (v0.6.0-a4 / amendment 4) instead, say so before the roster QG closes and I will do that instead. (4) relaunch under the same #450/#283 conditions from the new receipted SHA; report spend, GPU-hours, manifest path and per-record replay verdicts as you asked in #464.
next_handoff: cto reply on (3) if you object; otherwise ack
