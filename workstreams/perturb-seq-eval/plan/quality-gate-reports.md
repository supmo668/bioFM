# Quality-gate reports — perturb-seq-eval

| iteration | date | commit | receipt | findings (>=80 / scored) | checks | status |
|---|---|---|---|---|---|---|
| FRAMING.1 — cs.MA cross-list (row 12) | 2026-11-02 | 3055506 | `workstreams/perturb-seq-eval/qgr/bioFM-matthew-mo-perturb-seq-eval-perturb-seq-eval-bioFM-qgr-iteration-complete-20261102-0238-12d40b4.md` | 6 / 13 — F2 F12 F1 F5 F3 F6 fixed; F7 F11 deferred (<80, repo-level); F4 F8 F9 F10 F13 rejected | lint ok · format ok · typecheck NOTSCOPED · tests 1088 passed / 13 skipped / 0 failed | done |

## QGR — Iteration A5 (2026-11-04) — commit 96bd3761, receipt c9d568c

Scope: `bef363fe..96bd3761`. Amendment 5 (`v0.6.0-a5`): T1 retitle, contribution narrowed, "gate" → "pre-registered criterion", F2 SUBMISSION.md fix (CTO #896, #892).
Reviewers: code 10, security 0 (1 low note), design 18, test 7, own review 0; the scorer scored 26, and 7 passed the threshold (≥ 80).
Fixed: Q1 title/rename on publish.yml, THESIS.md, README.md; Q2 tally attribution in A5; Q3 preamble pointers; Q4 A5-2 wording; Q5 full-hash test; Q6 title-surface test (red → green). Below threshold, also fixed: F6, F8, F9, F10, F12, F13.
Escalated (not edited): Q7/F24 abstract sentence 1 vs morandi2026sprt (abstract frozen); F21/F22/F23 ratified CATTS/(b″) wording.
Deferred: F11 CITATION.cff version vs minted deposit (the principal decides the re-deposit); F16–F20 test follow-ups.
Incident: the tree moved during review, from my own Q5 test fix and two Stop-hook instinct files. The reviewers reviewed the fixed SHA f2bb1933, so their findings are unaffected.
Checks: ruff format clean (3 files); lint clean; typecheck not configured; tests 1089 passed, 13 skipped, 0 failed.

| iteration | status | commit | receipt |
|---|---|---|---|
| A5 | done | 96bd3761 | c9d568c |
