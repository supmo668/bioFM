---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-24T08:38
status: created
priority: high
size: project
subject: "AUTHORISED: regenerate v0.5.0 artifacts in one process — fixes land FIRST (A6/A2/A4), then one sweep"
in_reply_to: 201
---

# AUTHORISED: regenerate v0.5.0 artifacts in one process — fixes land FIRST (A6/A2/A4), then one sweep

AUTHORISED BY THE PRINCIPAL: regenerate the v0.5.0 artifacts in ONE process.

This is the first execution authority granted on this workstream. #200 and #201 were scoping-only; that restriction is now lifted FOR THE WORK NAMED BELOW AND NOTHING ELSE. Read #201 first — it carries the verified findings and the file:line evidence.

READ THIS BEFORE YOU RUN ANYTHING — THE ORDER IS THE WHOLE POINT.

Regenerating FIRST would reproduce the exact defect that made regeneration necessary, and would spend the principal's money to do it. Three fixes must land BEFORE the sweep, because each one is a cause of the corruption in the current artifact set:

  A6 (app_v05.py:217,224) — strata computed as `hash(s) % 3` on a Python str. str.__hash__ is salted per process, so the task draw changes on every invocation and seed=2026 is cosmetic. UNFIXED, a regeneration produces two more divergent task lists and you are exactly where you started. Fix: zlib.crc32(s.encode()) % 3.

  A2 (app_v05.py:340-357) — the loop seed is written into the record but never reaches run_agentic_lifecycle, which has no seed parameter; the LLM cache key omits it too. UNFIXED, you burn 3x the lifecycle compute to regenerate 36 runs triplicated again. Fix: add seed to run_agentic_lifecycle, thread into BackboneTrainConfig and into the cache key.

  A4 (norman.py:119-120, and the same fallback at e2_adamson.py:209-212, loop.py:222-226) — a RANDOM gene is substituted as the perturbation target when the target misses the HVG vocab. It fires on 8 of 15 Norman labels because the doublet guard tests '+' while the labels use '_'. UNFIXED, the regenerated GATE_NORMAN is as uninterpretable as the current one. Fix: RAISE, do not substitute. Make the delimiter configurable and assert the expected doublet count.

Then add the regression tests that make each one impossible to reintroduce — at minimum: the task sets of the two JSONLs are identical; lifecycle MSD differs across seeds; a missing target raises.

THEN, and only then, ONE sweep in ONE process producing both trainer_runs.jsonl and lifecycle_runs.jsonl.

HARD GATE ON THE ANALYSER: analyse_v05_run must FAIL LOUDLY when the two files' task sets differ, rather than joining them as it does today. That join is what turned two disjoint samples into '108 lifecycle runs spanning 36 held-out tasks'. Add it before the run so the run proves itself.

PROVENANCE — this is the point of the exercise, not a nicety. provenance.json currently records timings, cost and three counts, and NOTHING that identifies what ran. It must now carry: git SHA + dirty flag, the RESOLVED task list, every resolved kwarg (n_top_hvg, max_cells_per_pert, n_sweep, r_sweep, backbones, seeds), dataset SHA256 digests, model_id per lifecycle step, and library versions. Write it as record 0 of each JSONL as well, so a file is self-describing if separated from its directory. Per standing repo rule: log and save the exact config for every run, and create a NEW config copy per run rather than mutating one.

Also fold in while you are in there, since they are one-line each and the run should not have to happen twice:
  A7 — pin the three Adamson subset digests and the Norman digest in DatasetSpec; fail closed. The paper claims SHA-gated fetchers and every sha256 is currently None.
  A5 — optimizers/base.py:34 keys the backbone one-hot on {scGPT, scPRINT-2, scFoundation} while every experiment uses {linear, mlp, scgpt_small}, so all three collapse to index 0. Derive it from sorted(set(c.backbone for c in config_space)) and add `assert len({tuple(config_to_vec(c)) for c in space}) == len(space)`. Note tests/test_optimizers.py:22-26 builds its space from the only two names the dict recognises, which is why no test catches this — fix the test space too.

BUDGET AND RESOURCES. Prior sweep: $4.04 and 3.06 GPU-hours against the $28 hard-kill cap. The principal has authorised this regeneration. CHECK RESOURCE AVAILABILITY BEFORE YOU START (standing rule), keep it PoC-minimal, and report ACTUAL spend and GPU-hours rather than the cap — the paper currently quotes the cap as though it were the spend, which is its own defect.

EXPECT THE NUMBERS TO MOVE, AND DO NOT DEFEND THEM. Removing the random-gene tasks from Norman, de-triplicating the lifecycle runs, and making the task sets coherent will change median_msd_norman, the entropy figure, and quite possibly the gate outcomes. THAT IS THE CORRECT RESULT. Do not tune, reselect, or re-prompt to preserve 0.147 / 0.131 / 0.36. If a gate flips to FAIL, report it as FAIL — the project already has a good precedent for that with the entropy gate. A regenerated FAIL is worth more than a preserved PASS.

OUT OF SCOPE, EXPLICITLY. Do not touch the paper prose. Do not start the real/synthetic language pass — it is sequenced last and is now several steps further back than #200 implied. Do not attempt the TDI correlations (#200 R1) yet: whether they are even well-posed depends on what the regenerated artifacts look like, and I will rule on that after you report. Do not act on the seven UNVERIFIED leads in #201 beyond telling me verified/not.

YOUR WORKTREE IS STALE — 228d354 against main 6f4a86d. Sync before you start.

REPORT BACK: the regenerated summary.json, the new provenance record, actual spend, every gate outcome with its old value beside it, and a one-line verified/not on each of #201's seven unverified leads. Then stop — the next decision is mine and the principal's, not yours.
