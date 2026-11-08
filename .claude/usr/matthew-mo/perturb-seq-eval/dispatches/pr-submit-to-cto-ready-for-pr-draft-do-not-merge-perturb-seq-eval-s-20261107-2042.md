---
type: pr-submit
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-11-07T20:42
status: created
priority: high
size: task
subject: "Ready for PR (DRAFT, do not merge): perturb-seq-eval-staging — row 26, ledgers labelled in place; G2 needs a principal ruling (CLAUDE.md:144-147 vs row 26)"
in_reply_to: null
---

# Ready for PR (DRAFT, do not merge): perturb-seq-eval-staging — row 26, ledgers labelled in place; G2 needs a principal ruling (CLAUDE.md:144-147 vs row 26)

Row 26: the perturb-seq-eval-staging PR, raised by pr-submit. The principal said to proceed without asking for confirmation (2026-11-07).

**Open this as a DRAFT PR and DO NOT MERGE it to main.** The principal has not yet ruled on G2 (below).

branch: perturb-seq-eval-staging
sha: 63ba749c (pushed; origin == HEAD)
diff_hash: ef7196a (vs origin/main 7c293c0a; origin/main already merged in at aaac877a)
receipt: workstreams/perturb-seq-eval/qgr/bioFM-matthew-mo-perturb-seq-eval-perturb-seq-eval-perturb-seq-eval-qgr-pr-prep-20261107-2041-ef7196a.md (verifies --require-pushed)
scope: 4 ledgers under workstreams/perturb-seq-eval/findings-staging/. Docs only; 0 files outside that directory.
draft: true
migrations_pending: none

## What was done
- 61797b23: every finding is labelled in place with a `Status (2026-11-07)` line, using one vocabulary term per item or sub-item. The terms are RATIFIED + APPLIED, RATIFIED, HELD, APPLIED UNDER A DIRECTION RULING, NOT ADOPTED, SUPERSEDED, UNRATIFIED and REPORT / RECORD.
- 606c4fde: fixes for 11 gate findings. The reviewers raised 18; the scorer kept 13 at a threshold of 80.
  - G1: one Morandi affiliation was written at A:367. It is removed, with row 19 cited.
  - G3: origin/main's approvals.md ends at **row 12**. Rows 13–26 exist only on your local main, so every ledger header now glosses each of them by content.
  - G4: the §4.6 status now quotes row 24 in its own words. The aviary-biosim 2026-11-07 read and the proposed K clause ("held fixed in its real-LLM evaluation (their \S VII-C14)") are split out as sub-item **4.6-K, UNRATIFIED**, with their source stated. The principal's in-session "Wait for the CTO (Recommended)" is recorded as not yet an approvals row.
  - G5–G13: stale file-level statuses are marked historical, the vocabulary is normalised, and line ranges and per-commit attributions are corrected.
  - Also fixed: a pre-existing YAML break in the narrowed-contribution frontmatter (` #842` started a comment inside a plain scalar).
- Iron Law: the code tree is identical to origin/main outside the ledgers. The configured suite (`quality.test_command_perturb-seq-eval`) gives 1091 passed, 13 skipped, 0 failed. The staging role's own quality keys resolve NOTSCOPED.

## G2 — needs a principal ruling; the reason for the draft
CLAUDE.md:144-147: "**Unratified findings never reach the trunk** … a findings-staging ledger lives on a dedicated `<agent>-staging` branch that is never a PR head; … accepted content then moves to its real destination through a normal PR and the staging file is deleted."
Row 26 (your local main only): "THE perturb-seq-eval-staging PR IS RAISED BY pr-submit TO THE CTO … Every unratified finding is labelled in place before the gate." Row 26 does not name a merge target.
Merging would put labelled UNRATIFIED content on the public trunk: framing Item 2 / R2-a..e, the T2/T3 drafts, and 4.6-K. The principal has to rule on one of these:
  (a) row 26 overrides the rule for this branch, and CLAUDE.md records the exception; or
  (b) the PR stays a draft for review and the Notion mirror, then closes unmerged; or
  (c) only ratified content moves to its real destination, and the ledgers are deleted.
No MYB-8 guard exists. hacp-docs.yml does not trigger on findings-staging/, so this PR will show no checks.

## CTO actions
1. Open the PR as a **draft** from perturb-seq-eval-staging. Do not version-bump it or merge it until G2 is ruled.
2. Put G2 to the principal, together with pushing your local main (approvals rows 13–26 are not on origin).
3. Optional, per the HACP rule: mirror the ledgers to a Notion row under the HACP index for ratification.
4. Still open separately: the row-24 Morandi section check (§III / §VII-C14 / §VII-C17) is yours to do at the ref.
