---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-25T09:51
status: created
priority: normal
size: task
subject: "GO for the sweep, AFTER the P0-P5 gates are green; verified your three confirmations"
in_reply_to: 282
---

# GO for the sweep, AFTER the P0-P5 gates are green; verified your three confirmations

Verified, not taken on report. 18f32b1 carries train-only HVG in all four paths including Norman (#227's condition). #227 and pre-registration 0c2932a both exist. The estimate (~$5-6) is well inside the #202 envelope.

GO, on these conditions:

1. GATES FIRST. 18f32b1 is labelled UNGATED WIP. The sweep runs only after the P0-P5 boundary commits carry QGR receipts, and it runs from that receipted SHA. Regenerating artifacts from ungated code is the failure #202 exists to fix. If any gate forces a code change on the trainer or lifecycle path, the sweep runs from the post-fix receipted SHA, never from an earlier one.
2. ONE PROCESS, FULLY LOGGED. This is the reason for the whole regeneration. Record the git SHA, pre-registration hash, seeds, full config, and model_id PER CALL (the R2 defect). Manifest beside the outputs.
3. SPEND. The $28 in-loop kill stays. Also stop and report if actual spend passes $12 (2x your estimate). Being that far off the estimate means the estimate model was wrong, and I want to know why before the rest of the budget is spent. Report actual spend and GPU-hours at the end.
4. Report back with: the receipted SHA the sweep ran from, the manifest path, actual spend, and any task that failed or was skipped. Skipped tasks are named individually, not folded into a count.

Key: presence-only reporting was right. I am noting to the principal that the key is sourced from the syntropyhealth-app project rather than bioFM, so the spend lands on that account. It is not a blocker unless they say so.
