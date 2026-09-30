# QGR — iteration-complete A4CLIENT (AnthropicClient for the v0.6.0 lifecycle, amendment 4) — 2026-09-29

Base 535cb68 (amendment 4 lock + text fix) → gated artifact 846c770 (Hash A 91d0401) → final 00fae29 (Hash E 36b0e1d). Receipt: /Users/mo/github/personal/bioFM/worktrees/perturb-seq-eval/workstreams/perturb-seq-eval/qgr/bioFM-matthew-mo-perturb-seq-eval-perturb-seq-eval-bioFM-qgr-iteration-complete-20260928-2049-36b0e1d.md.
Reviewers ran read-only in a gate-created detached scratch worktree (bracket diff: the worktree entry only). CTO test list (#480/#482/#486) covered.

## Issues Found (post-scorer, threshold 80) — 13 kept of 43 raised; all fixed
| id | sev | conf | tag | sources | summary | disposition |
|---|---|---|---|---|---|---|
| QG-1 | HIGH | 92 | DEFECT | CODE-1 DES-1 TEST-3 | served-model mismatch / 2nd max_tokens failed over; run could end ok (and the Validator could silently move to Haiku) | fixed 2bf75f3: raised out of chat_json, no failover |
| QG-2 | HIGH | 88 | DEFECT | CODE-4 TEST-1 | our own exceptions classified as provider failures → fallback | fixed 2bf75f3: only SDK/OS errors are provider events |
| QG-3 | MED | 88 | DEFECT | DES-2 CODE-3 | abort path dropped call log, refusal category, prices, ceilings | fixed 3ade237 |
| QG-4 | MED | 85 | DEFECT | DES-6 | prior_spend_usd default 0.0; commands omitted the flag | fixed 3ade237: default 1.3548 + refusal below it for v0.6.0 |
| QG-5 | MED | 80 | DEFECT | CODE-2 | 2x-retry budget per pass, not per step | fixed 2bf75f3 |
| QG-6 | LOW-MED | 82 | DEFECT | DES-7 TEST-18 | Haiku temperature unpinned in app_v05 | fixed 3ade237: refused ≠ 0.3 for v0.6.0 |
| QG-7 | LOW | 80 | DEFECT | OWN-1 CODE-8 DES-4 TEST-9 | preflight probe spend outside the meter | fixed 3ade237 |
| QG-8 | LOW | 80 | DOCS | DES-3 CODE-3 | refusal = fatal abort vs A4-1 wording | prereg text clarified 00fae29 (CTO #480 mechanism) |
| QG-9 | MED | 82 | TEST-GAP | TEST-2 | real SDK exception classes never exercised | fixed 2bf75f3 |
| QG-10 | MED | 85 | TEST-GAP | TEST-4 | probe_model untested directly | fixed 2bf75f3 |
| QG-11 | LOW | 80 | TEST-GAP | TEST-5 TEST-6 | weak billing assertions; cache_write unpriced | fixed 2bf75f3 |
| QG-12 | LOW | 80 | TEST-GAP | TEST-8 | cooled-model re-offer untested | fixed 2bf75f3 |
| QG-13 | LOW | 82 | DOCS | DES-11 CODE-10 | OpenRouter-era wording | fixed 3ade237 |
Also folded (below threshold, cheap): SEC-1 sampling-key whitelist, SEC-2 price-table coverage, CODE-5 (≥500 cools, 404 fatal). Dropped (<80): 30 (scorer report). Deferred: none.
Design decision recorded (OWN-4/DES-14): with two preferred models per role, the ≥2-live rule requires BOTH roster models to pass every role's probe — intended strictness; a one-model "pool" is refused before spend.

## Accountability
- reviewer-code: 10  - reviewer-security: 5  - reviewer-design: 14  - reviewer-test: 21  - own: 4
- reviewer-scorer: scored 54 (43 distinct), 13 passed threshold (>= 80)
- Implementer: coordinator by hand (no implementer subagents).

## Coverage Health
tests/test_anthropic_client.py: 27 → 48 tests (real anthropic exception classes incl. connection/timeout/429/529/520/401/403/402/404; no-failover on mismatch and double truncation incl. pool propagation; own-bug propagation; per-step truncation budget across a cooldown; cooled-model re-offer; exact billing incl. cache_write; direct probe_model verdicts; pinned run params; abort-path and preflight-spend wiring by AST). DF-14 test. Every finding red→green. Suite: 1103 → 1123 passed.

## Checks (Iron Law — on the committed state 00fae29)
Format: ruff format --check on all .py changed since 535cb68 → "12 files already formatted". Lint: ruff E9,F63,F7,F82 → clean. Typecheck: none configured (#365). Tests: 1123 passed. Failing: 0. Tree: clean (configs/runs/ untracked by CTO instruction).

## Summary
The Anthropic client now cannot silently substitute a model, hide a client-side bug as a provider event, or lose a refusal's record on abort; its retry budget is per step; spend is usage x pinned prices including the preflight probes and the carried-in 1.3548, and the pinned run parameters (temperature 0.3, prior spend) are refused if wrong. Relaunch waits on the CTO's receipt verification (#486).

## Proposed Commit
Iteration A4CLIENT: AnthropicClient gated; QGR + receipt (boundary commit).
