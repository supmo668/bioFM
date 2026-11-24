# Quality gate — Amendment 6 manuscript and the 0.6.2 deposit preparation (2026-11-24)

Scope: `git diff origin/main...perturb-seq-eval`. Approvals rows 39 (disclose and reframe), 40 (title), 41 (one 0.6.2 from this branch).

## Stage 1 — four reviewers on commit 1b9864f4

| Reviewer | Result |
|---|---|
| Security | no findings |
| Correctness | 0 blockers, 2 major, 6 minor |
| Design / consistency | 1 blocker, 4 major, 11 minor |
| Tests | 3 major, 3 minor; 12 of 19 mutations caught, 7 survived |

Blocker: `paper/SUBMISSION.md` paired the new title and abstract with steps that built the arXiv bundle from the 0.6.1 commit.
Major: the feedback disclosure said every role sees the Validator verdict (the Architect does not); "confidences before feedback do not rank tasks" was broader than the evidence (only the mean is null); "the supported result" misused the outcome word; hand-typed numbers in the arXiv abstract were untested; a published version number was paired with a title it never carried; README and THESIS kept "Bayesian recommender" and "sufficient statistic"; `\expl` macros and prose claims were unguarded.

## Stage 2 — fixes (commits after 1b9864f4)

All findings were accepted and fixed, with one exception recorded here: the `delta_ace` docstring in `src/perturb_eval/metrics.py` was restored to the landed text, because the paper states exactly which source files differ from the run revision and a test enforces it. The docstring's "Negative = converging" remains stale.

Every new test was shown live by mutation (22 mutations, all killed).

## Stage 3 — verification at c8bb555d (scorer)

All ten tracked findings resolved; confidence 82–97 per finding; overall 88/100 against a threshold of 80. `git diff origin/main...HEAD -- src artifacts` is empty. Tests: 1158 passed, 0 failed, 15 skipped (anndata, torch, and two figure tests that need matplotlib, which the local environment lacks). PDF builds with no undefined references.

New minor findings: the CITATION identifier description said "this release" for 0.6.1 (fixed after the verification); integer counts in the arXiv abstract are pinned as literals, not macros (not fixed); one "about as strongly" comparison is not pinned (not fixed); figure freshness is not verified locally (CI installs matplotlib).

## Open risks, none enforced by code

- The Zenodo notes name tag `v0.6.0-a6`, which does not exist until the CTO creates it on the landed commit. It must exist before the dry run.
- The arXiv bundle must be rebuilt from the 0.6.2 deposit commit; the existing artifact is the 0.6.1 manuscript.
- Branch `perturb-seq-eval-haca126` prepares a different 0.6.2 and must stay held (row 41; two dispatches to the CTO).
- Publishing 0.6.2 is not approved. Row 41 covers preparation and a dry run only.
