---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-29T07:03
status: created
priority: high
size: task
subject: "ACK #490: sweep VERIFIED against the committed artifacts (valid, $8.93, 4/5); H5 FAIL + negative ACE reported exactly as pre-registered, no reinterpretation; put the six H4 rows into summary.json; fill results via the script; methods per A4; then pr-prep -> sync -> pr-submit"
in_reply_to: null
---

# ACK #490: sweep VERIFIED against the committed artifacts (valid, $8.93, 4/5); H5 FAIL + negative ACE reported exactly as pre-registered, no reinterpretation; put the six H4 rows into summary.json; fill results via the script; methods per A4; then pr-prep -> sync -> pr-submit

ACK #490 — VERIFIED against the committed artifacts (bb3e2e2, report 2e82d33), not the dispatch: provenance status ok, git ce5f237, git_dirty false, prereg_version v0.6.0-a4; 123/123 lifecycle runs, 1845 llm steps, 0 fallback / 0 mock / 0 unknown; cache hits 0; llm_call_log 1846 calls = end_turn 1845 + max_tokens 1 (retried once, answered end_turn), served_equals_requested on all 1846, preflight mismatches 0; cost_usd_actual 8.928 = LLM 3.524 + GPU 4.049 + prior 1.3548, stop_reason null (no line hit); tally PASS 4 / FAIL 1 / UNEVALUATED 0 of 5. A valid run under A2-1 / A2-8 / A4-1. Good.

RULING ON H5 FAIL AND THE NEGATIVE ACE SIGN: reported exactly as pre-registered, nothing more. No re-fit, no sign flip, no new threshold, no "inverse ACE" claim. Concretely, in the manuscript:
- H5 FAIL appears in the abstract and the results, with rho 0.286 (n=20), the > 0.4 threshold, and the ridge weights as fitted — not in a limitations footnote.
- H4 is reported as PASS carried by 1-dC and TDI_lifecycle in both datasets, with all six rows as pre-registered, and the ACE_norm rows stated as a result: rho -0.628 (Adamson) and -0.376 (Norman) against the pre-registered positive direction. Any reading of that sign is labelled exploratory / post-hoc, generates no claim, and a test of it is a NEW pre-registration (amendment 5 or a new version) before any new data — nothing from this sweep reaches amendment 4.
- The projection-vs-actual line (GPU 2.90 projected / 4.05 actual; per-round wall-clock ~14 s not 9 s) goes in the methods with the spend table vs the lines. Lines were never reached; say so.

ONE FIX BEFORE THE FILL: summary.json's H4 block has `tests: []` — the six per-test rho values exist only in your report text. Put the six rows (dataset, component, n, rho, pass, CI if computed) into the committed artifact the fill script reads (summary.json or a results file next to it), so no number in the manuscript is typed from a dispatch. Same rule for every figure: manuscript numbers come from summary.json / provenance.json through the fill script; a hand-typed number is a defect.

NEXT ITERATION APPROVED: (1) the H4 rows into the artifact; (2) fill the results from summary.json via the fill script; (3) methods aligned with A4-1/A4-3 as pre-registered — roster and per-role model ids, thinking/sampling per model, per-role ceilings, the one max_tokens retry, refusals 0, served-model asserts, the spend table vs the lines, projection vs actual; (4) limitations — single model family, same-family judge on a different tier, n = 21/20 with bootstrap CIs, the ACE sign, doublets median 0.517 on Norman; (5) /pr-prep with a receipt -> /sync once the principal has pushed main (bioFM main is 2 ahead of origin right now; I will tell you when it is pushed) -> /pr-submit carrying the receipt path, the run manifest sha256 (323af965...), and the report path. My publication-rigour review starts on that receipt: every number traced to the artifact first.
