# QGR — iteration-complete RELAUNCH (roster + preflight + client + spend fixes after the aborted v0.6.0 run) — 2026-09-28

Base 291efad (last receipted SHA) → gated artifact 069cca4 (Hash A e6d6bc7) → final 62a12e0 (Hash E 2a499b0). Receipt: /Users/mo/github/personal/bioFM/worktrees/perturb-seq-eval/workstreams/perturb-seq-eval/qgr/bioFM-matthew-mo-perturb-seq-eval-perturb-seq-eval-bioFM-qgr-iteration-complete-20260928-1731-2a499b0.md.
Reviewers ran read-only in a gate-created detached scratch worktree (bracket diff: the worktree entry only).
Context: sweep 20260928T220916Z-291efad aborted (stop-and-report) — 6/8 :free roster models gone from OpenRouter, the rest rate-limited; A2-1 makes a fallback fatal. CTO #467 directives; principal ruling 2026-09-28: paid cheapest JSON-capable roster.

## Issues Found (post-scorer, threshold 80) — 13 kept of 44 raised; all fixed
| id | sev | conf | tag | sources | summary | disposition |
|---|---|---|---|---|---|---|
| QG-1 | HIGH | 90 | DEFECT | CODE-1 | transport exceptions escaped chat_json → fallback | fixed 62a12e0 |
| QG-2 | HIGH | 88 | DEFECT | DES-1 OWN-3 | spend counted GPU only; LLM bill + aborted-run spend uncounted | fixed 62a12e0: key-usage delta + prior_spend_usd; both guards on the total (default; reported) |
| QG-3 | MED | 85 | DEFECT | CODE-4 SEC-1 SEC-2 DES-4 | hard-failed models re-billed each pass; budget = sleep-sum | fixed 62a12e0 |
| QG-4 | MED | 82 | DEFECT | CODE-3 | 500/408 not cooled; 401/402 → fallbacks; no stop on first fallback | fixed 62a12e0 |
| QG-5 | MED | 80 | DEFECT | CODE-2 | cooldown expiring mid-pass → never retried | fixed 62a12e0 |
| QG-6 | MED | 80 | RULING | CODE-5 DES-2 | Validator-only probe vs each role's schema | strict reading implemented 49f32f4 (15 cheap probes) |
| QG-7 | MED | 85 | TEST-GAP | TEST-3 TEST-4 | ≥2 boundary / per-role counting unpinned | fixed 62a12e0 |
| QG-8 | MED | 80 | TEST-GAP | TEST-1 TEST-19 CODE-7 | probe-count pin untested on the real roster; probe_all ignored pool= | fixed 49f32f4 + 62a12e0 |
| QG-9 | LOW | 82 | TEST-GAP | TEST-2 DES-5 CODE-7 OWN-2 | legacy/None probe paths untested; unused paid helper | fixed 49f32f4 + 62a12e0 |
| QG-10 | LOW | 85 | TEST-GAP | TEST-5 TEST-6 TEST-7 | weak wait assertions | fixed 62a12e0 |
| QG-11 | LOW | 82 | TEST-GAP | TEST-8 TEST-16 | transport verdict untested; dead fake branch | fixed 49f32f4 + 62a12e0 |
| QG-12 | LOW | 90 | TEST-GAP | TEST-17 | tautological rate-limit test | fixed 62a12e0 |
| QG-13 | LOW | 85 | DOCS | CODE-9 DES-1 DES-7 CODE-7 | stale free-tier text; ProbeFn type; manuscript rule + provenance row | fixed 49f32f4 + 62a12e0 |
Dropped (<80): 31 (scorer report in qgr evidence). Deferred: none.

## Accountability
- reviewer-code: 9  - reviewer-security: 5  - reviewer-design: 9  - reviewer-test: 20  - own: 3
- reviewer-scorer: scored 46, 13 passed threshold (>= 80)
- Implementer: coordinator by hand (no implementer subagents — a Claude monthly spend limit killed a subagent in the previous gate).

## Coverage Health
tests/test_roster_relaunch.py grew from 13 to 38 tests (transport failover, hard-failed skip, wall-clock deadline, status classes, fatal 401/402 propagation through the pool, mid-pass cooldown expiry, key-usage memo, per-role schema probes, ≥2 boundary, per-role naming, real-roster probe-count pin, legacy/None probes, transport verdicts); behavioural replacement for the tautological rate-limit test. Every finding red→green. Suite: 1049 → 1072 passed.

## Checks (Iron Law — on the committed state 62a12e0)
Format: ruff format --check on all .py changed since 291efad → "10 files already formatted". Lint: ruff E9,F63,F7,F82 → clean. Typecheck: none configured (#365). Tests: 1072 passed. Failing: 0. Tree: clean (configs/runs/ untracked by CTO instruction).

## Summary
The relaunch can no longer be invalidated by a transient provider error: transport errors and 408/429/5xx cool the model and the client waits (bounded by a wall-clock deadline) rather than falling back; hard failures are not re-billed; 401/402 abort the run outright; the sweep stops on the first fallback step. Preflight probes every roster model with each role's own schema and refuses before spend. Spend now includes the LLM bill and the aborted run's .3, against both guards. Relaunch: prior_spend_usd=1.3, namespace v0.6.0-a3 archived and empty.

## Proposed Commit
Iteration RELAUNCH: roster/preflight/client/spend fixes gated; QGR + receipt (boundary commit).
