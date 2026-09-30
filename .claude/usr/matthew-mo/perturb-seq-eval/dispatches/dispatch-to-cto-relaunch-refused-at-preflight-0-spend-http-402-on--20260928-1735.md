---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-09-29T00:35
status: created
priority: normal
size: task
subject: "Relaunch REFUSED at preflight (0 spend): HTTP 402 on all 8 paid models = no OpenRouter credit balance; output dir archived; awaiting principal credits"
in_reply_to: null
---

# Relaunch REFUSED at preflight (0 spend): HTTP 402 on all 8 paid models = no OpenRouter credit balance; output dir archived; awaiting principal credits

event: relaunch REFUSED at preflight (no spend)
workstream: perturb-seq-eval
run_id: 20260929T003223Z-4f967a1 (git_dirty=False; SHA 4f967a1, receipt 9d0822d derived from 2a499b0 per your #470)
what_happened: preflight refused before any GPU or LLM spend (as designed after #467). 7 failures: (1-6) every one of the 8 paid roster models answered HTTP 402 (insufficient credits) on every role probe — the OpenRouter account has no prepaid credit balance (the key is not free-tier but had only ever been used on :free endpoints; /key reports usage 4.8, limit none); (7) output dir /data/v0.6.0 not empty — the aborted run's trainer_runs.jsonl / lifecycle_runs.jsonl / provenance.json were still there.
spend: this attempt 0 (cumulative still ~1.3 from the aborted run).
actions: (a) the principal is being asked to add OpenRouter credits (estimate for the whole sweep < $2; ~$10 suggested) — nothing I can do on that; (b) the aborted run's output files ARCHIVED (not deleted) on the data volume to v0.6.0-aborted-20260928T220916Z-291efad/ with a sha256 manifest (workstreams/perturb-seq-eval/qgr/evidence/output-archive-20260928T220916Z-291efad.manifest.json), and /v0.6.0 is now empty; (c) a cosmetic defect registered for the next code gate: Modal re-raises the remote PreflightError locally and PreflightError.__init__ iterates the message string ("1700 failure(s)") — the real 7-line report is intact in the remote log; two-line fix, no measurand effect, not worth a full gate on its own.
relaunch: after credits are confirmed, same command from 4f967a1 (--prior-spend-usd 1.3); preflight will re-probe all 8 models per role before any spend.
next_handoff: cto ack
