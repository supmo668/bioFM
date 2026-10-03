---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-09-28T22:05
status: created
priority: normal
size: task
subject: "Iteration A2-fixes complete on perturb-seq-eval — gate closed 371c274, AMENDMENT 3 locked 114a01f, sweep starting per #450"
in_reply_to: null
---

# Iteration A2-fixes complete on perturb-seq-eval — gate closed 371c274, AMENDMENT 3 locked 114a01f, sweep starting per #450

event: iteration-complete
workstream: perturb-seq-eval
iteration: A2-fixes (amendment-2 measurand fixes quality gate)
branch: perturb-seq-eval
commit_hash: 371c274
base: 3bf2a9a
fix_commits: a702977 ad27533 0abf2db (per-finding, QGR-Finding trailers); prereg commit 114a01f (AMENDMENT 3)
qgr_receipt: /Users/mo/github/personal/bioFM/worktrees/perturb-seq-eval/workstreams/perturb-seq-eval/qgr/bioFM-matthew-mo-perturb-seq-eval-perturb-seq-eval-bioFM-qgr-iteration-complete-20260928-1504-1f3dc41.md
qgr_report: workstreams/perturb-seq-eval/qgr/qgr-iteration-complete-20260928-a2fixes.md
summary: 4 reviewers + own in a gate-created scratch worktree; scorer kept 11/43 (>=80). Fixed: QG-1 analyser now detects replay (step cache_hit / entries-at-start / prov flag / prereg_version mismatch) and never licenses gates on it; QG-10 eval-gene list cited + mismatch diagnostic; QG-5 non-finite hyper-parameters = schema failure; QG-2 applied-config record carries applied:false for qc_mito_max; QG-8 dry run; QG-3/4/11 test gaps. Four points the A2 text left open were ruled by the principal (AskUserQuestion, 2026-09-28) and locked as AMENDMENT 3 at 114a01f BEFORE any data: A3-1 mito threshold record-only; A3-2 precedence gains the Trainer tier; A3-3 Validator dynamic_threshold_msd REQUIRED (unstated = schema failure); A3-4 stated distinct-config count = 7 (19 fits / 27 records as detail). prereg_version -> v0.6.0-a3 (fresh cache namespace per A2-8). Iron Law on 371c274: 38 files formatted, lint clean, 1036 passed, 0 failing.
next_action: per #450 standing GO, starting the #283 sweep from 371c274 (model_id per call, config + prereg hash in manifest, $12 stop-and-report, $28 kill); will report actual spend + GPU-hours. Note: one implementer subagent died on a Claude monthly spend limit mid-gate; its work was completed by hand and verified.
next_handoff: cto ack (and /pr-cto-land after the principal pushes main)
