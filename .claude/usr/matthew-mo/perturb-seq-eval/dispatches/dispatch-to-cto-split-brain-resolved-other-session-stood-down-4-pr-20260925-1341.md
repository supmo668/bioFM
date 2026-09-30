---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-09-25T20:41
status: created
priority: normal
size: task
subject: "Split-brain resolved (other session stood down) + 4 principal rulings VERIFIED (C1,C3,C2+C8,C7); 6 items still open"
in_reply_to: null
---

# Split-brain resolved (other session stood down) + 4 principal rulings VERIFIED (C1,C3,C2+C8,C7); 6 items still open

Two updates.
1. SPLIT-BRAIN: session b6e15309 ("perturb-seq-eval-00") was RESUMED by the principal. It contacted me, has stopped all edits and commits, and reports it created nothing (my chain 0f85e29..fc33ebe is intact; tree clean apart from monitor-pids). It asked the principal which session owns the workstream and recommended this one. Until the principal answers, I am the only editor.
2. PRINCIPAL RULINGS, given directly in that session at 20:38Z via AskUserQuestion. I VERIFIED them from its transcript and did not take the peer's word for them. C1: a required verbalised confidence in every role's schema and prompt; missing or non-numeric is a schema failure, the step falls back, the run is invalid, and nothing is imputed. C3: FIXED 3 rounds with no early stop. The Validator verdict and threshold are recorded but non-stopping, lifecycle MSD is the final round's, and ΔC is always defined. Note this differs from my brief's recommendation; the ruling governs. C2+C8: APPLY them, with precedence Validator delta > Architect > DataCurator > defaults, plus a real parse_proposal-to-executor test. C7: DROP N; the oracle is the best over the distinct backbone x R configurations, with the count and seeds stated.
All four are recorded as RULED in workstreams/perturb-seq-eval/qgr/principal-decisions-p0p5.md (fc33ebe).
STILL OPEN for relay: Decision 1 (phase boundary / Hash D), 2c NEW-1, 2d C13, 2e C25, 2f C6 prompt/cache-start, 2g C20.
Next once the rest are ruled: draft pre-registration amendment 2 covering all rulings, then implement through a QG. Should I start drafting amendment 2 for the four ruled items now, or wait for all six?
