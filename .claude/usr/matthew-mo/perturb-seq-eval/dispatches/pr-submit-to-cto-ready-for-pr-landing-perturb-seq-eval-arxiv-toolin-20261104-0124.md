---
type: pr-submit
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-11-04T01:24
status: created
priority: normal
size: task
subject: "Ready for PR landing: perturb-seq-eval — arXiv tooling + SUBMISSION.md Part 7 (receipt ae59f98; F1/F2 escalated)"
in_reply_to: null
---

# Ready for PR landing: perturb-seq-eval — arXiv tooling + SUBMISSION.md Part 7 (receipt ae59f98; F1/F2 escalated)

Closes #885 and #887 on my side. Land request follows.

branch: perturb-seq-eval
sha: 9fef94d (pushed; origin/perturb-seq-eval == HEAD, receipt-verify --require-pushed ✓)
base: origin/main 46c32bb (merged at 459adf0; 0 behind at submit)
diff-hash: ae59f98
receipt: workstreams/perturb-seq-eval/qgr/bioFM-matthew-mo-perturb-seq-eval-perturb-seq-eval-bioFM-qgr-pr-prep-20261104-0123-ae59f98.md
draft: false
migrations_pending: none
supersedes: pr-submit #863 (receipt 03e8998 is stale; do not use it)

## Scope
arXiv package tooling + runbook: scripts/arxiv_package.py (cross_list + primary shape validation; self-test reports SKIPs as NOT RUN and exits 1), scripts/README-arxiv.md, paper/arxiv.toml (cs.MA cross-list, rows 11/12), paper/SUBMISSION.md (Part 7 verbatim per #885, plus the two exact pointer sentences in Part 1 and Part 5; nothing else in that file touched by me this session), tests/test_agentic_lifecycle.py (C-TORCH-2 assertion; renamed _or_raises).

## #885 — done as specified
Part 7 inserted after Part 6, before "Approval required before Part 1". A programmatic check confirmed the payload matches byte for byte. The Part 1 and Part 5 sentences are exact. arxiv.toml, the paste block, the abstract and every other file are untouched by the #885 edit. Paste block re-checked: byte-identical to `arxiv_package.py metadata` output, before and after the QG fixes. Committed a69a1ec, pushed.

## QG (pr-prep, profile standard): 4 reviewers + scorer, threshold 80, 5 survivors
- F3 FIXED (7bf5ffc): self-test without pyyaml printed ALL CHECKS PROVEN LIVE and exited 0 with 11 cases unrun. It now prints "N CHECK(S) NOT RUN" and exits 1. README no longer calls self-test stdlib-only. CI is unaffected (it installs pyyaml).
- F4 FIXED (794f36d, 2ea8087): categories.primary is now shape-checked like cross_list. Planted red → green.
- F5 FIXED (b6f0d0e): test renamed; the body asserts raise, not fallback.
- F1 ESCALATED, not fixed (score 90, HIGH). SUBMISSION.md contradicts itself on the venue. The header row (:28) and Approval item 2 (:470-473) say RULED arXiv cs.LG (row 12), "bioRxiv no longer under consideration". Part 7.1/7.2/7.5 say arXiv is unavailable without a named endorser, recommend TechRxiv, and list "Principal decides the venue". Part 1 :115-119 still offers the institutional-address route and the bioRxiv fallback. #885 closed the file to further edits, and which ruling governs is the principal's call, so I made no change. Needed: a principal ruling (does row 12 stand with Path 2 only, or is the venue re-opened?) and then a doc edit you authorize.
- F2 ESCALATED, not fixed (score 85, MED; pre-existing text). Part 0 (:50,:52) and approval item 1 (:466-468) call c0ec931 "held unflushed" / "Flush c0ec931?". Measured: `git merge-base --is-ancestor c0ec931 origin/main` is true. :59-63 cites a measured CI run 40985145366 that produced paper.bbl, while :66-68 and :469 say "The workflow's LaTeX step has never executed". Same restriction applies.
Filtered (<80): CFF "single source of truth" header shown above an arxiv.toml-overridden abstract (65; pre-existing, outside the paste markers); README check table; label truncation; others listed in the receipt's QGR.

Checks, run fresh this session: ruff format (configured cmd) ✓; root script under default ruff ✓; lint ✓; typecheck NOTSCOPED; pytest 1088 passed / 13 skipped (torch absent) / 0 failed; arxiv self-test ALL CHECKS PROVEN LIVE.

## CTO actions
1. /pr-cto-land perturb-seq-eval with this receipt.
2. Your switch-branch blocker: I have no pending work on this branch after this submit, except what the five rulings (#876) and F1/F2 may produce, and those come back to this branch. Landing from inside this worktree (receipt-verify here) is fine with me. I will not retire the worktree.
3. Route F1 to the principal. F2 needs only your go-ahead for a factual doc correction.

next_handoff: CTO → master-updated / changes-requested to perturb-seq-eval.
