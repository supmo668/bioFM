---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-09-29T00:32
status: created
priority: normal
size: task
subject: "Iteration RELAUNCH complete on perturb-seq-eval (4f967a1, receipt 2a499b0) — sweep relaunched 00:31Z with prior spend 1.3 carried in; two interpretations taken"
in_reply_to: null
---

# Iteration RELAUNCH complete on perturb-seq-eval (4f967a1, receipt 2a499b0) — sweep relaunched 00:31Z with prior spend 1.3 carried in; two interpretations taken

event: iteration-complete + sweep relaunched
workstream: perturb-seq-eval
iteration: RELAUNCH (roster + preflight + client + spend fixes after the aborted run; CTO #467)
branch: perturb-seq-eval
commit_hash: 4f967a1 (boundary; fixes 0235911 49f32f4 62a12e0; base 291efad)
qgr_receipt: workstreams/perturb-seq-eval/qgr/bioFM-matthew-mo-perturb-seq-eval-perturb-seq-eval-bioFM-qgr-iteration-complete-20260928-1731-2a499b0.md (Hash E 2a499b0; verifies 4f967a1)
qgr_report: workstreams/perturb-seq-eval/qgr/qgr-iteration-complete-20260928-relaunch.md
gate: 4 reviewers + own in a gate-created scratch worktree; scorer kept 13/46 (>=80), all fixed. Iron Law on 4f967a1: 10 files formatted, lint clean, 1072 passed, 0 failing.
your_directives: (1) roster: 8 PAID models one per family (principal ruling 2026-09-28), 3 preferred per role; every model probed at preflight; id + probed_at + verdict + per-role result recorded as provenance llm_roster_liveness. (2) preflight probes EVERY roster model and refuses before spend if any role has < 2 live preferred models; a test fails if it probes fewer models than the roster lists (pinned against the real 8-model roster, not only the test pool). (3) namespace v0.6.0-a3 ARCHIVED (not deleted) to llm/_archive/20260928T220916Z-291efad/ with a sha256 manifest (workstreams/perturb-seq-eval/qgr/evidence/llm-cache-archive-20260928T220916Z-291efad.manifest.json, committed 069cca4); namespace asserted empty (0 entries) immediately before relaunch. (4) relaunched 2026-09-29T00:31:52Z from 4f967a1 with --prior-spend-usd 1.3 so the $12 line is cumulative.
two_interpretations_i_took (say if you want either changed): (a) "the same JSON probe the roles use" read STRICTLY — each role's preferred models are probed with that role's own schema (15 cheap calls), so a model that cannot meet e.g. the Architect backbone schema is not live for that role. (b) actual spend = GPU wall-clock + OpenRouter key-usage delta + prior 1.3, and BOTH the $12 stop and the $28 kill apply to that total (spend is spend); breakdown gpu_cost_usd / llm_cost_usd / prior_spend_usd is in provenance and the summary.
gate_hardening: transport errors and 408/429/5xx cool a model and the client WAITS (wall-clock deadline 300 s per call) instead of falling back; hard failures are not re-called; 401/402 abort the run (ProviderFatalError, never a fallback); the sweep latches a stop on the FIRST fallback step so no GPU-hours are spent on an invalid run.
next_action: report at completion: actual spend (aborted 1.3 + relaunch, and the sum), GPU-hours, manifest path, per-record replay verdicts, roster liveness table.
next_handoff: cto ack
