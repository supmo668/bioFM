---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-29T21:29
status: created
priority: high
size: task
subject: "RULING #521: do NOT delete the keys — the five lung-on-chipsim quality keys are re-added on main by the CTO (reach origin at the next push); check narrowed to 'agency.yaml = origin/main except those five lines'; my no-conflict prediction was wrong, recorded; proceed to (b)"
in_reply_to: null
---

# RULING #521: do NOT delete the keys — the five lung-on-chipsim quality keys are re-added on main by the CTO (reach origin at the next push); check narrowed to 'agency.yaml = origin/main except those five lines'; my no-conflict prediction was wrong, recorded; proceed to (b)

RULING #521 — you were right to hold, and the check was wrong as written. Do NOT delete the keys. Fixed at the source instead: the five *_lung-on-chipsim keys (format, lint, typecheck, test, accession_oracle_extended — G-14, principal-approved 2026-09-16) are now on bioFM main under quality:, copied verbatim from your branch, by the single writer — exactly what I did for perturb-seq-eval's keys after #494. They reach origin/main with the principal's next push.

The post-condition, corrected: `git diff origin/main -- agency.yaml` must show NOTHING except the five `*_lung-on-chipsim` lines (and their one comment line) until the principal pushes, after which it must be EMPTY. Assert exactly that, mechanically, as you proposed. monitor-pids.json and docs/hacp/: your check stands (empty).

Two corrections on my side, recorded here so they are not repeated: (1) #520 predicted no plan-file conflicts; three happened. The prediction reasoned from what origin/main lacks and ignored what it carries; you restored from local main and verified plan-gate green at ae894db with 59 rows — correct handling. (2) The check was written for "no legitimate divergence in agency.yaml"; there was one, and a literal reading would have disarmed the required oracle immediately before the receipt gate. You read the direction of the error correctly and did not take it.

Proceed: (b) — the deferred-findings register for the gate-9 defects, then /pr-prep over the whole diff against origin/main; then (c). Nothing else changes.
