---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-24T05:57
status: created
priority: high
size: project
subject: "Publication-rigour review of paper v0.5.0 — 2 blocking, 6 major; scope the build work"
in_reply_to: null
---

# Publication-rigour review of paper v0.5.0 — 2 blocking, 6 major; scope the build work

CTO review of `paper/paper.tex` @ v0.5.0 against `artifacts/v0.5.0/`. Full findings, with file:line evidence for each, are on main at:

  workstreams/perturb-seq-eval/qa/_adhoc/2026-09-23-publication-rigor-review.md

Read that first — this dispatch is the routing note, not the review.

VERDICT: not submittable as drafted. The engineering substrate is publication-grade (frozen trace schema, SHA-gated fetchers, resume-safe JSONL, 209 tests, $4.04 for 1,944 trainer cells). The empirical argument is not: the title claim is unevaluated and the primary experimental condition is both misstated and unrecorded.

THE TWO BLOCKING ONES, in the order they must be worked:

R2 — the experimental condition is misstated and unrecorded. The paper says Nemotron-30B throughout (4 places). CHANGELOG [0.5.0] says a rotating pool of 8 heterogeneous free-tier models with cooldown failover. configs/live.yaml:24 pins a 120B model. And lifecycle_runs.jsonl steps carry NO model field at all, so which model produced which proposal is unrecoverable. Consequence: the headline entropy result (0.36 nats, 91% scgpt_small) is confounded — model identity varied with API availability, not with task. This also violates the standing repo-wide rule that every run logs the exact config it ran under.

R1 — the central claim has no reported result. Table tab:tdi-real reports n/a for the Spearman rho of EVERY TDI component vs held-out MSD; §4.4 transfer is n/a too. summary.json has no correlation key; e_v05_real_traces.py:158-159 returns NaN below 3 extractable feature values and the filler prints it as n/a. The correlations were never computed. Worse, §6 Discussion and §4.2 both cite that empty table as evidence for the thesis, and the abstract's 'two of three gates pass' drops the two unevaluated gates from the denominator (five are pre-registered in the text).

WHAT I NEED FROM YOU — scope, do not yet implement:

1. For R2: is model_id recoverable for the 108 committed lifecycle runs from any side-channel (the sha256 prompt cache keys on (task_id, round, role, prompt, model_id) — does the cache survive on the Modal volume or locally?). If recoverable, this is a re-analysis, not a re-run. If not, say so plainly and price a re-run with per-step model logging. Do NOT re-run anything before reporting back — cost and the $28 envelope are the principal's call.

2. For R1: can the 5 correlations be computed from the 108 committed traces as they stand, or does the NaN mean the feature extraction genuinely has <3 usable values per component? Read e_v05_real_traces.py's extraction path and tell me which. This decides whether the paper keeps its title or gets reframed as an infrastructure + lifecycle result.

3. For R3 (stated composition contradicts the artifact — paper says Norman = 15 singletons + 5 doublets = 20 tasks; artifact has 15 total, 7 singletons + 8 doublets): is the sampler wrong or the description? Point at the code.

4. For R5 (min over 54 configs then median over tasks, with no nested split): is there a validation split in the trainer sweep I missed, or is the reported quantity selection-on-test? If the latter, the fix is a relabel, not a re-run.

5. Price R4/R7/R8/R9/R10/R11 (bootstrap CIs + dispersion; the real/synthetic language pass; renaming scgpt_small through code+artifacts+prose; provenance.json gaining git SHA/seed/checksums/versions; re-scoping the stale REVIEWER_CRITIQUE.md to v0.4.1; one title). Most of these are mechanical.

SEQUENCING CONSTRAINT: the language pass (R7 — 'synthetic' appears 17x, 'real' 32x; the principal's standing instruction is that using published experimental data is a given and must not be asserted defensively) runs LAST. It describes the claims, so the claims settle first. Do not start there even though it is the easiest.

STANDING CONSTRAINTS that apply to anything you do run: log/save the exact config for every run and create a new config copy per run; check resource availability before running; keep it PoC-minimal.

Reply with the scope + a build plan. Nothing in category 1-5 is authorised to execute yet.
