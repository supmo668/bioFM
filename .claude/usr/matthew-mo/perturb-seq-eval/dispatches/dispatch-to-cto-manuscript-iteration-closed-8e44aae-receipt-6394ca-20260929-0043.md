---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-09-29T07:43
status: created
priority: high
size: task
subject: "MANUSCRIPT iteration CLOSED (8e44aae; receipt 6394ca9): manuscript filled via generated macros per #491; H4 rows key path; LaTeX compile requested; next /pr-prep"
in_reply_to: null
---

# MANUSCRIPT iteration CLOSED (8e44aae; receipt 6394ca9): manuscript filled via generated macros per #491; H4 rows key path; LaTeX compile requested; next /pr-prep

Agent: perturb-seq-eval (worktree perturb-seq-eval, branch perturb-seq-eval). Re: #491 approved iteration.

MANUSCRIPT iteration CLOSED — boundary commit 8e44aae; bookkeeping eeae7f5 (HEAD).
Receipts: workstreams/perturb-seq-eval/qgr/bioFM-matthew-mo-perturb-seq-eval-perturb-seq-eval-bioFM-qgr-iteration-complete-20260929-0041-6394ca9.md (boundary), ...-20260929-0043-c194cd4.md (derived, post-bookkeeping).
QGR: workstreams/perturb-seq-eval/qgr/qgr-manuscript-v060-20260929T074135Z.md

(1) H4 six rows: they were already in the committed artifact — artifacts/v0.6.0/summary.json -> preregistered.H4.all_six (list of six {dataset, component, rho, n, ci_low, ci_high, passes}); the two descriptive forms are at preregistered.H4.descriptive.{adamson_full,norman}.{ace_norm_softmax,one_minus_delta_c_clipped}; pooled at preregistered.H4.pooled_descriptive. No artifact change was needed.
(2) Fill by script: scripts/paper/fill_v060_numbers.py -> paper/sections/generated_numbers.tex (187 \res macros from summary.json + provenance.json + lifecycle_runs.jsonl + paper/data/projection_v060.json [A4-2 figures]); --check is a test. Tests pin every result macro to an independent artifact key path, check invariants (CI/IQR order, pick/call/spend sums), pin the prose claims (which tests pass, ACE CIs, doublet stratum, three rounds, one model per role, retry, lines not reached) to the artifact, pin the methods wording to A2-7/A3-2/A3-3/A4-1/A4-3, and scan results/setup/paper.tex for hand-typed decimals against a pre-registration-checked allowlist. No number is typed by hand.
(3) Methods per A4-1/A4-3: roster + per-role served model asserted (all calls per role on the pinned model; failovers 0), structured outputs + key/value maps, thinking off, Haiku T=0.3 / Sonnet defaults (non-default rejected), ceilings 256/1316/256/256/1192, one max_tokens retry (1 occurrence, answered), refusals 0, served-model mismatches 0, spend vs lines (LLM 3.52 + GPU 4.05 + prior 1.3548 = 8.93 vs 12/28/30), projection vs actual (7.19 projected; both components above projection, within the stop line — no causal clause).
(4) Limitations: single family, same-family judge on a different tier, n=21/20 via macros with bootstrap CIs, ACE sign (point estimates negative; Adamson CI excludes zero, Norman CI includes it; exploratory, no claim), Norman doublet median above the H2 gate.
H5 FAIL is in the abstract, results and conclusion, stated as pre-registered (no re-fit, no sign flip).

Gate (23 findings fixed, 0 deferred), the substantive ones: the sampler paragraph had kept the pre-A2-7 "every stratum filled exactly" sentence; the Validator was described as "recorded, not acted on" although its threshold gates the applied rule-based delta (135/369 rounds carry a Validator-sourced value; the LLM Validator's own delta is recorded, not applied — now stated per A3-2); the descriptive softmax/clipped H4 rows and the H5 Adamson standardisation (ACE mean 0.9962, sd 0.0046) were required and missing; the abstract/Discussion read meaning into the ACE sign — now estimators only; the generator's fallback count read a nonexistent key (always 0) and the test asserted the literal — now keyed to n_steps_fallback with a patched-artifact test. Section Metrics now points at A2-10/A2-11.

Two items for you:
(a) pdflatex/latexmk are not installed on this machine, so the manuscript is checked structurally (macros defined, braces, refs, input order) but NOT compiled. The stale v0.5 paper.pdf and .aux/.log/.out/.bbl/.blg were untracked (they contradicted the source) and gitignored. Please compile on the CTO side (or tell me to install TeX) before landing.
(b) Config quality.*_command keys are empty; the gate ran the #365 commands (lint E9,F63,F7,F82; full pytest = 1145 passed; typecheck ''), reported, not skipped.

Next on my side: /pr-prep (receipt) now; /sync ONLY when you say the principal has pushed main; then /pr-submit carrying the receipt path, run manifest sha256 323af965b631ce83, and the run report path. Nothing from the sweep touched the amendments.
next_handoff: CTO -> perturb-seq-eval (ack + "main pushed" signal, or changes-requested).
