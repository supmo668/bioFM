# QGR — iteration-complete A2-fixes (amendment-2 measurand fixes) — 2026-09-28

Base 3bf2a9a (amendment-2 lock) → gated artifact df653e7 + 4840f0d (Hash A 7ccef86) → final 0abf2db (Hash E 1f3dc41).
Receipt: /Users/mo/github/personal/bioFM/worktrees/perturb-seq-eval/workstreams/perturb-seq-eval/qgr/bioFM-matthew-mo-perturb-seq-eval-perturb-seq-eval-bioFM-qgr-iteration-complete-20260928-1504-1f3dc41.md. Reviewers ran read-only in a gate-created detached scratch worktree at 4840f0d (bracket diff: the worktree entry only).

## Issues Found (post-scorer, threshold 80)
| id | sev | conf | tag | sources | summary | disposition |
|---|---|---|---|---|---|---|
| QG-1 | HIGH | 95 | DEFECT | OWN-1 CODE-1 DES-1 TEST-3 | analyser never detected a replay / prereg_version mismatch → gates licensed on cached replies (A2-8) | fixed 0abf2db |
| QG-2 | HIGH | 90 | DEFECT+RULING | DES-2 CODE-2 TEST-4 | qc_mito_max recorded as applied, never applied (A2-3) | record fixed a702977; ruled record-only → A3-1 |
| QG-3 | MED | 95 | TEST-GAP | TEST-1 | steering test's only assertion never executed; max_rounds=2 | fixed ad27533 |
| QG-4 | MED | 95 | TEST-GAP | TEST-2 | final-MSD-is-round-2 test could not tell rounds apart | fixed a702977 |
| QG-5 | MED | 88 | DEFECT | SEC-1 | Infinity / 1e308 hyper-parameters parsed and applied as stated | fixed a702977 |
| QG-6 | MED | 85 | RULING | DES-7 | fifth precedence tier (Trainer) unstated in A2-3 | ruled keep → A3-2 |
| QG-7 | MED | 85 | RULING | CODE-5 DES-5 TEST-7 | three readings of "distinct configurations" (9 / 19 / 7) | ruled 7 → A3-4; counts unified 0abf2db |
| QG-8 | LOW | 90 | DEFECT | OWN-2 CODE-8 | local dry run exercised only the fallback path | fixed ad27533 |
| QG-9 | MED | 80 | RULING | CODE-3 CODE-4 DES-8 | unstated Validator threshold defaulted to 0.1 and gated the applied config | ruled schema failure → A3-3; fixed a702977 |
| QG-10 | MED | 80 | DEFECT | DES-3 | per-task eval-gene list not cited; no trainer/lifecycle agreement check (A2-5) | fixed 0abf2db |
| QG-11 | LOW | 80 | TEST-GAP | TEST-6 | ceiling / Miller–Madow test tautological on a 3-item menu | fixed 0abf2db |
Dropped (<80, 15): see qgr evidence (scorer report). Deferred: none.

## Accountability
- reviewer-code: 9  - reviewer-security: 4  - reviewer-design: 12  - reviewer-test: 10  - own: 3
- reviewer-scorer: scored 43 (38 distinct), 11 passed threshold (>= 80)
- Implementers: three fresh subagents (estimators / lifecycle / trainer) for df653e7; fix cycle: one analyser subagent + coordinator by hand (the lifecycle fix subagent died on an API spend limit mid-QG-8; its work was inspected, completed and verified).

## Coverage Health
New tests: test_prereg_a2_analyser.py (22), test_v05_dry_run.py (9), TestDeriveStatusReplay (5), TestQG9ValidatorThresholdRequired (3), QG-7 relationship test, QG-11 menu test, QG-3/QG-4 rewrites. Every fix red→green (evidence in subagent reports; QG-11 red by temporary ln 3 hard-code).
Suite: 925 (pre-gate) → 1036 passed.

## Checks (Iron Law — run on the committed state 0abf2db)
Format: ruff format --check on all 38 .py changed since 3bf2a9a → "38 files already formatted". Lint: ruff E9,F63,F7,F82 → clean. Typecheck: none configured (#365). Tests: 1036 passed. Failing: 0. Tree: clean (config/monitor-pids.json = tool state).

## Summary
Amendment 2's measurand fixes land as specified; the gate found one blocker (replay runs would have licensed gates) and three spec gaps that only the principal could close — all closed in amendment 3 (114a01f, prereg_version v0.6.0-a3, fresh cache namespace). The paper must state: mito threshold recorded not applied; Trainer tier; required Validator threshold; 7 distinct configurations.

## Proposed Commit
Iteration A2-fixes: amendment-2 measurand fixes gated; amendment 3 locked (boundary commit carries this QGR + receipt).
