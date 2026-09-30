---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-09-29T07:01
status: created
priority: normal
size: task
subject: "SWEEP COMPLETE 20260929T035447Z-ce5f237: valid (0 fallbacks, 0 cache hits, 0 mismatches, 0 refusals); $8.93 total; gates H1-H4 PASS, H5 FAIL; artifacts + manifest committed"
in_reply_to: null
---

# SWEEP COMPLETE 20260929T035447Z-ce5f237: valid (0 fallbacks, 0 cache hits, 0 mismatches, 0 refusals); $8.93 total; gates H1-H4 PASS, H5 FAIL; artifacts + manifest committed

event: SWEEP COMPLETE — valid run; 4/5 pre-registered gates pass (H5 fails); total spend $8.93 < $12
workstream: perturb-seq-eval
report_doc: workstreams/perturb-seq-eval/qgr/v060-run-report-20260929T035447Z-ce5f237.md

# v0.6.0 sweep — run report (run_id 20260929T035447Z-ce5f237, git ce5f237, prereg_version v0.6.0-a4)

Launched 2026-09-29T03:51:54Z under CTO GO #488 from the receipted tip ce5f237 (receipt 47e2523 derived from 36b0e1d); finished with provenance status `ok`; `git_dirty` False. Analyser (`analyse_v05_run`): status `ok`, diagnostic None, replay False.

## Validity (A2-1 / A2-8 / A4-1)
- Lifecycle runs 123/123, all 3 rounds; steps 1845: source counts {'llm': 1845} — **0 fallback steps**.
- Replay: cache entries at start 0, cache hits 0, replay False (namespace v0.6.0-a4; 255 entries written by this run). Per-record replay verdict: 0 of 123 records carry a cache hit.
- Calls 1846 (1,845 steps + 1 retry): stop_reason counts {'end_turn': 1845, 'max_tokens': 1}; the single `max_tokens` (ceiling) was retried once at 2x and answered `end_turn` — no fallback-class event. Refusals 0. Served-model mismatches 0/1846 (served == requested on every call).
- Roster liveness at preflight: {claude-haiku-4-5-20251001: live=True, claude-sonnet-5-5: live=True}. Steps by model: {'claude-haiku-4-5-20251001': 1476, 'claude-sonnet-5-5': 369} (Haiku 4 roles x 369, Sonnet 5.5 Validator 369 — no failover occurred).
- Ceilings {'DataCurator': 256, 'Literature': 1316, 'Architect': 256, 'Trainer': 256, 'Validator': 1192}; price table recorded (Anthropic first-party list prices; claude-api skill model table cached 2026-09-25; re-cited 2026-09-29); sampling {'claude-haiku-4-5-20251001': {'temperature': 0.3}, 'claude-sonnet-5-5': {}}.
- Eval-gene lists: trainer and lifecycle agree on all 41 tasks (mismatch tasks: []).
- Run manifest `configs/runs/20260929T035447Z-ce5f237.json` sha256 323af965b631ce83d237644b0e97336c4b46ed48bb848ba81b4af2e90fa3e4cb. Aborted-run archives: cache `llm/_archive/20260928T220916Z-291efad/` (manifest sha256 703916525d4591ac9f8d304020e8cc81f6114cc9d00db93c1cefad29a17c697a), outputs `v0.6.0-aborted-20260928T220916Z-291efad/` (manifest sha256 419daa10f1492436e0cb4fdee464e86eb6f72519b6e92d7c57a68de380d23e5d).

## Spend vs the lines (A4-2)
| component | USD |
|---|---|
| LLM (usage x pinned prices; 1,242,639 in / 277,906 out tokens; Haiku 1.751, Sonnet 1.762) | 3.524 (incl. preflight probes 0.0105) |
| GPU (A100 wall-clock 3.07 h x $1.32) | 4.049 |
| prior (aborted run 1.3 + dry runs 0.0548) | 1.3548 |
| **total** | **8.928** vs $12 stop / $28 kill / $30 ceiling — stop_reason None |
Projection was $7.19; actual $8.93 (GPU 4.05 vs 2.90 projected: the lifecycle's per-round wall-clock ran ~14 s, not 9 s).

## Pre-registered gates (PREREGISTRATION.md; nothing here changes any amendment)
| gate | value | threshold | verdict |
|---|---|---|---|
| H1 Adamson trainer oracle median MSD | 0.1315 (CI 0.111-0.149, n=21) | < 0.20 | **PASS** |
| H2 Norman trainer oracle median MSD | 0.1842 (CI 0.092-0.395, n=20; doublets median 0.517) | < 0.30 | **PASS** |
| H3 Architect stated-backbone entropy | 0.859 nats (linear 19 / mlp 167 / scgpt_small 183; ceiling ln 3 = 1.099; executed != stated: 0) | >= 0.5 | **PASS** |
| H4 any of six within-dataset rho > 0.5 | 4 of 6 pass (table below) | > 0.5 | **PASS** |
| H5 Adamson-fitted TDI transferred to Norman | rho 0.286 (n=20; ridge weights ace_norm -1.53, 1-dC -0.29) | > 0.4 | **FAIL** |
Tally: {'PASS': 4, 'FAIL': 1, 'UNEVALUATED': 0, 'out_of': 5}.

### H4 — all six tests (reported regardless of outcome, as pre-registered)
| dataset | component | n | rho | > 0.5 |
|---|---|---|---|---|
| adamson_full | ace_norm | 21 | -0.628 | fail |
| adamson_full | one_minus_delta_c | 21 | +0.663 | PASS |
| adamson_full | tdi_lifecycle | 21 | +0.661 | PASS |
| norman | ace_norm | 20 | -0.376 | fail |
| norman | one_minus_delta_c | 20 | +0.703 | PASS |
| norman | tdi_lifecycle | 20 | +0.702 | PASS |
Note (result, not interpretation): ACE (`ace_d`) correlates NEGATIVELY with held-out error in both datasets; the H4 pass is carried by 1-dC and TDI_lifecycle in both datasets.

Artifacts: `projects/perturb-seq-eval/artifacts/v0.6.0/` (trainer_runs.jsonl, lifecycle_runs.jsonl, provenance.json incl. the full call log, summary.json).

next_action proposed: (1) commit the artifacts + hashed run manifest (this dispatch's commit); (2) next iteration: fill the manuscript results from summary.json via the fill script and align the methods (Anthropic roster + caveats per A4-3), then /pr-prep -> /sync -> /pr-submit once the principal has pushed main. Say if you want the H5 FAIL or the negative ACE sign handled any differently than 'reported as pre-registered'.
next_handoff: cto ack
