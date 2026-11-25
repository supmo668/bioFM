# Quality gate — self-contained reader-facing surfaces (2026-11-25)

Scope: `git diff origin/main...perturb-seq-eval` after PR #56. Approvals row 42 (remove undefined labels and shorthand; content self-contained and referenced).

## Stage 1 — clarity pass (commit 220d18f2)

About 180 defects fixed across six surfaces: both abstracts, the manuscript body with tables and captions, deposit notes and descriptions, the citation file, READMEs and changelog, figure captions. Hypothesis labels H1–H5 and amendment labels A1–A6 are gone from the manuscript and forbidden by test.

## Stage 2 — meaning-drift review of 220d18f2 (scorer, threshold 80)

Confidence that the pass changed wording only: 70/100 — below threshold. Eight findings kept (scores 80–92):

- "held-out" added to the two attainable-error hypotheses, which are oracle quantities (major);
- "the one feature that meets its criterion" — two features meet it (major);
- the trainer sweep's R glossed as a round count; it is an iteration budget (major);
- "records neither critiques" — it records no critique-severity matrix (minor);
- amendment version labels called git tags (minor);
- "(versions 0.6.0 and 0.6.1)" read as a complete list of earlier archives (minor);
- arXiv abstract dropped "role-specialised" and "asserted per call" (minor);
- the transfer row called the ridge-fitted index by the fixed-weight composite's name (minor).

No number, threshold, inequality or estimator had moved; no test guard was loosened.

## Stage 3 — fixes

All eight fixed, plus the below-threshold items and the undefined terms listed for the abstracts. A new test pins each corrected statement to its source (for example the sweep's iteration formula against `trainer_config`). The CellForge reference was corrected from arXiv's record for 2508.02276 (first author Xiangru Tang; version-1 and current titles) and the correction is disclosed in the changelog and the deposit notes. Four works were added to the citation file's reference list from `references.bib` fields only.

One abstract sentence added by the fix pass ("the testbed's agents do not critique one another") was narrowed by the session to what the body supports ("records no agent-by-agent critiques and no per-round winner").

Tests: 1159 passed, 0 failed, 15 skipped (torch, anndata, and two figure tests needing matplotlib locally). PDF builds with no undefined references.

## Not re-reviewed

The stage-3 fixes were verified by tests and by the session's reading of the report, not by a second independent review.

## Known and left

- `paper/PREREGISTRATION.md` still says the `v0.6.0-a6` tag "is to be created"; the file is locked and the tag now exists (created 2026-11-25 on 07a5e57b).
- The manuscript abstract is 4,332 characters; the arXiv form uses the separate 1,919-character override.
- References other than CellForge and the two checked earlier in this workstream were not re-verified against their sources.
