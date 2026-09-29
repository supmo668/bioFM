---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-25T20:00
status: created
priority: normal
size: task
subject: "Option (i): derived receipt over the 3 non-code files (verified); deviations a/b/c accepted; write ONE principal decision brief (Hash D + the 10 measurand rulings)"
in_reply_to: 391
---

# Option (i): derived receipt over the 3 non-code files (verified); deviations a/b/c accepted; write ONE principal decision brief (Hash D + the 10 measurand rulings)

Executed well. The bracket and its failure proof were written before the run, RED was measured at 451f730 with in-pytest provenance and a sensible split between API reds and behavioural reds, and the stash was dropped by message plus SHA. That is everything #363 asked for.

RULING on the stale receipt: option (i). I verified the premise myself. receipt-verify on the 4a2948a receipt reports "code changed after the gate ran", and 'git diff --stat 80817b1 HEAD' shows exactly three non-code files: agency.yaml, qgr/evidence/qg-p0p5-stophook-proof.txt, and your dispatch. So re-sign a DERIVED receipt with --derived-from 4a2948a over the new Hash E. The summary must name those three paths as the entire delta, stating that there is no source or test change. Then run receipt-verify on the new receipt and report the result. D stays recorded as PENDING principal, exactly as now. Do not fill it.

DEVIATIONS, all three accepted:
 a) The cluster commit citing all 11 IDs. Hand-splitting hunks into commits that do not match the verified tree would have been worse.
 b) Commit first, then sign. That is the correct order given what diff-hash hashes. Record it as the standing order for this workstream.
 c) Working-tree-scoped format for the Stop hook. As a turn-end check it is the right scope, and the 70-of-79 format debt is a separate PR, not now.

TWO THINGS GO TO THE PRINCIPAL. Write ONE principal-facing decision brief so I can relay it. Put it in workstreams/perturb-seq-eval/qgr/principal-decisions-p0p5.md, in shapes not values:
 1. The phase boundary (Hash D): what the P0-P5 phase delivered, in 5 lines, and that the boundary commit is held for their approval.
 2. The ACCEPT-FIX-AFTER-RULING items (C1, C2, C3, C7, C8, C13, C25, NEW-1, C6-prompt, C20). For EACH: one line on what it changes in the MEASURAND, the options, your recommendation, and whether it forces pre-registration amendment 2. Group items that share one decision. Also state plainly that the #283 sweep cannot run until these are ruled, and why.
Commit it, then send me the path.

Sessions: leave the idle session b6e15309 unresumed. If it is ever resumed, it must read the tree state before acting on its queued notifications."
