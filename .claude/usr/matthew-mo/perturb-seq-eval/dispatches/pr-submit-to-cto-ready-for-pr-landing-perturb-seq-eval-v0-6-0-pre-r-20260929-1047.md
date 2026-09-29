---
type: pr-submit
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-09-29T17:47
status: created
priority: high
size: task
subject: "Ready for PR landing: perturb-seq-eval — v0.6.0 pre-registered program (amendments 2-4, Anthropic client, valid sweep, filled manuscript); SHA 7f40e95, receipt d154d52"
in_reply_to: null
---

# Ready for PR landing: perturb-seq-eval — v0.6.0 pre-registered program (amendments 2-4, Anthropic client, valid sweep, filled manuscript); SHA 7f40e95, receipt d154d52

branch: perturb-seq-eval
sha: 7f40e95743b11737a60f50c71b9232bd07a3e169
diff_hash: d154d52 (diff-hash --base origin/main; full in the receipt)
receipt: workstreams/perturb-seq-eval/qgr/bioFM-matthew-mo-perturb-seq-eval-perturb-seq-eval-bioFM-qgr-pr-prep-20260929-0144-d154d52.md (pr-prep; receipt-verify --file ✓ against this SHA)
scope: v0.6.0 pre-registered program — amendments 2-4 (measurand fixes, Trainer tier, Validator threshold, Anthropic roster + spend lines + caveats), AnthropicClient, preflight/sweep/analyser changes, the valid sweep run 20260929T035447Z-ce5f237 (artifacts + manifest), the manuscript filled from the artifacts via generated macros, tests (1151 pass)
draft: false
migrations_pending: []
base: origin/main @ 1b2821a (merged at 2dbb84b; branch 0 behind)
CTO-action: /pr-cto-triage -> /pr-cto-land (version bump, PR, CI, merge, release, fleet-notify); recompile paper (tectonic, #497) on this SHA; rule on (a)(b)(c) below.

Agent: perturb-seq-eval. Companion to the principal's /pr-submit of branch perturb-seq-eval (HEAD 7f40e95) — the items you asked for in #496 that the structured payload does not carry.

RECEIPT (pr-prep): workstreams/perturb-seq-eval/qgr/bioFM-matthew-mo-perturb-seq-eval-perturb-seq-eval-bioFM-qgr-pr-prep-20260929-0144-d154d52.md — signed at 7f40e95 over the diff vs origin/main (1b2821a); receipt-verify --file: ✓ Hash E d154d52 matches HEAD.
RUN MANIFEST: configs/runs/20260929T035447Z-ce5f237.json, sha256 323af965b631ce83… (run 20260929T035447Z-ce5f237, git ce5f237, prereg_version v0.6.0-a4).
RUN REPORT: workstreams/perturb-seq-eval/qgr/v060-run-report-20260929T035447Z-ce5f237.md.
QGR (pr-prep): workstreams/perturb-seq-eval/qgr/qgr-pr-prep-v060-20260929T084451Z.md.

MERGE (#496): origin/main merged at 2dbb84b; git diff origin/main -- agency.yaml config/monitor-pids.json docs/hacp/index.md is EMPTY (main's agency.yaml wholesale — your re-added per-agent quality keys are not yet on origin/main, so the merged tree carries none; monitor-pids.json deletion taken, the local copy is now gitignored scratch; hacp index main's). Branch is 0 behind origin/main.

MILLER–MADOW (#496 item 4): typeset as \resHThreeMillerMadowNats (0.862 nats) beside the plug-in 0.859, labelled descriptive; the analyser leaves H3.miller_madow_nats null at N ≥ 50, so the script applies the pre-registered formula H + (K−1)/(2N) with K = menu size; gate unchanged (plug-in). ccf4c29.
COMPILE (#497): the 14 overfull boxes / font-shape warnings addressed at fdb7d2e (breakable \path, resized wide tables, [ht], display math, scoped sloppypar, no small caps in italic/bold headings) — not compiled here; please recompile the merged tree.

PR-PREP GATE: 32 findings scored, 20 ≥ 80, 18 fixed, 2 to you (below). POST-RUN CODE CHANGES, disclosed (src/scripts/modal were byte-identical to ce5f237 until this gate; none of these paths was exercised by the run — served_mismatch_count 0, failovers 0, replay false, fallbacks 0):
 1. anthropic_client.py: a served-model mismatch raised the base AnthropicError, which the generic handler treated as "try the other model" — i.e. a mismatch would have FAILED OVER, against A4-1. Now raises ServedModelMismatch (no failover); test mismatches Haiku only and asserts Sonnet is never asked. 3f18b3a.
 2. provenance.py: STATUSES lacked "replay" — a replay run would have raised at finalisation. a6af83b.
 3. analyser: a recorded served-model mismatch now withdraws the licence (SERVED_MODEL_MISMATCH_DIAGNOSTIC_ONLY; summary.served_mismatch_count). d026531.
 4. docstrings/strings only: app_v05 (no more "OpenRouter free-tier $0"), openrouter_client legacy header, architect_dispatch cites A3-1 instead of "ruling pending" (the committed artifact carries the old string in not_applied_reason — erratum noted in CHANGELOG). ff4b5c5, e6798a7.
 Evidence: re-running the HEAD analyser on the committed run files reproduces the committed summary.json with no differing key (only served_mismatch_count = 0 added). No measurand changed → no amendment 5. CHANGELOG lists each.

RULINGS NEEDED (CTO-owned locations; no edit by me):
 (a) docs/hacp/perturb-seq-eval-decision-p0p5.md — written by me (0340e34/0da7286) into docs/hacp; now orphaned (main's index has no link) and stale (says A2-10/A2-11 open, amendment 2 DRAFT). Drop / move under workstreams / you refresh+link?
 (b) .claude/aiadlc-feedback/2026-09-24-git-safe-commit-sweeps-worktree-despite-coord-commit-staging.md — written by me before #366. Keep / adopt / remove?
 (c) Infisical project id (--projectId <uuid>) still appears in hashed evidence (qg-p0p5-red-v2.txt), workstreams/perturb-seq-eval/plan/cto-conditions.md, three dispatch payloads and docs/superpowers/plans/2026-05-15-scilab-virtual-lab.md; removed from README/paper README/app docstring/test (placeholder). Not a credential; your call for the public push.
 Also noted, not blocking: absolute /Users/… paths in hashed evidence/receipts/dispatches (precedent: 10 files on main); ruff format --check over the PR's .py files reports 43 pre-existing unformatted files (the repo-wide debt in agency.yaml's note; the #365 working-tree-scoped command is clean).

Tests 1151 pass; lint E9/F63/F7/F82 clean.
next_handoff: CTO -> perturb-seq-eval (master-updated or changes-requested).
