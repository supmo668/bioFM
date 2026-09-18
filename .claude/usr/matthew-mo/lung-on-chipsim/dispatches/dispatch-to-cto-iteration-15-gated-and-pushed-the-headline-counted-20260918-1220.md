---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-18T19:20
status: created
priority: normal
size: task
subject: "Iteration 15 gated and pushed - the headline counted rows in a sentence about files, and my carried note was wrong about where the defect lived"
in_reply_to: null
---

# Iteration 15 gated and pushed - the headline counted rows in a sentence about files, and my carried note was wrong about where the defect lived

event: iteration-complete
workstream: lung-on-chipsim
iteration: "§15"
branch: lung-on-chipsim
commit_hash: 322892f
qgr_receipt: workstreams/lung-on-chipsim/qgr/bioFM-matthew-mo-lung-on-chipsim-lung-on-chipsim-bioFM-qgr-iteration-complete-20260918-1219-ebebbbc.md
hashes: "A == E == ebebbbc, base f2cf09a, 3 files, --project bioFM"
remote_refs_observed:
  origin/lung-on-chipsim: 322892f7df9c7dfc5fcbbb6080d6f7aee1bca8c7
  origin/main: df89f5039be4449aa3f7246ee496b28edb708cfe (untouched)

summary: |
  I went to close the LAST carried report defect — "one path printing two owners" — and
  REPRODUCED IT against the shipped code before touching anything. The reproduction found a worse
  defect sitting beside it. That is twice this section that going to look produced the real finding.

the_headline_was_its_own_contradiction: |
      undeclared undecodable files: 0 (failing this gate: 4)

  Zero undecodable files and four failing, in one clause, about ONE file. `failing_count` is a ROW
  count — its field docstring says so honestly — rendered inside a sentence whose subject is FILES.
  One path had accumulated four findings: a declaration misplaced under an ownership prefix, owned
  by a project that should declare it elsewhere, pinned to a file absent from disk, plus the
  missing-on-disk row itself.

  The line DIRECTLY BENEATH it already read "1 whose claim does not hold (3 defect(s))". The report
  knew how to distinguish things from findings everywhere except the number a human reads first.

  Fixed with `failing_paths` as a PROPERTY, not a field: the class already states that the RENDERER
  must not recompute a number sitting beside the verdict, so deriving it IN the class, from `rows`,
  next to `exit_code`, honours that rule instead of working around it. It also takes no constructor
  argument a caller could pass inconsistently, so NONE of the six existing construction sites
  changed. The findings clause renders ONLY when the counts differ — ordinary output is
  byte-identical and the real gate still prints "failing this gate: 0". Both directions are
  mutation-tested: never rendering, and always rendering.

a_correction_to_my_own_carried_note_wrong_for_three_sections: |
  THE TWO OWNERS ARE NOT PRINTED. The broken-declaration section renders no `owner=` at all. The
  contradiction lives entirely in `scan.rows` — the structured interface `ScanRow`'s docstring
  exists to provide, "so 'what fails' can be asked of the data instead of reassembled by grepping
  four sections of prose".

  Had I fixed what I REMEMBERED rather than what I MEASURED, I would have changed the rendered text
  and declared a data defect closed. I am flagging that because the carried list is written by me,
  and a carried note is a claim that decays.

  `ScanRow.owner_basis` now says which question the owner answers: "registry" (narrowed — who is
  ACCOUNTABLE, narrowing is the safe direction there) or "placement" (wider — may this be DECLARED
  here, widening is safe, and it is the set the defect was adjudicated against, r2.25 DES-1). BOTH
  ATTRIBUTIONS WERE ALWAYS CORRECT. The defect was that nothing said so.

one_suspicion_i_checked_and_dropped: |
  The three broken-declaration rows on one path looked like DUPLICATES inflating the count. They
  are three DISTINCT findings with three distinct `detail` strings. Not a defect. Recording it
  because "I suspected, checked, and it was fine" belongs in the ledger as much as the hits.

not_a_false_clean: |
  Neither finding changes a verdict: `exit_code` turns on whether ANY row fails, not how many, and
  every missing row fails closed regardless of which set attributed it. F-02 OVER-reported, which
  is the safe direction — but into a clause that made ONE misplaced declaration read as FOUR
  failing files, and scope is exactly what a human uses the headline to judge.

verification:
  suite: "1017 -> 1021 passed / 5 skipped, 0 DESELECTED (delta = the 4 tests added)"
  mutation: "5/5 KILLED BY ASSERTION, none by timeout, both modules restored byte-for-byte"
  gates: "record-content-gate (STAGED) exit 0, record-content-report (WORKTREE) exit 0, 744 tracked, BOTH run immediately before the push"
  format_lint: "read AFTER the last edit"
  real_output: "the live report's headline is UNCHANGED in the clean case — verified, not assumed"

carried_now_three_all_deliberate:
  - the one-enumeration refactor (deferred on cost, recorded in r2.32 WITH its reason)
  - THIS_PROJECT resolving from the import location
  - ContentPolicy holding two of seven policy decisions
  - "The two §11 guard items closed in §14; the owner-attribution item closes here. What remains is deferral, not unexamined debt."

standing: |
  r2.28's property remains AVAILABLE, NOT ENFORCED. Nothing in §15 touches enforcement, and the
  receipt does not imply it.

next_handoff: none expected — nothing outstanding to you. Next contact is the next gated boundary.
