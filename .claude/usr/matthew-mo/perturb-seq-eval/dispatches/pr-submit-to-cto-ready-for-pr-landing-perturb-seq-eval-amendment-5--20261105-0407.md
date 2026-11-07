---
type: pr-submit
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-11-05T04:07
status: created
priority: high
size: task
subject: "Ready for PR landing: perturb-seq-eval — Amendment 5 (v0.6.0-a5): T1 retitle, narrowing, gate->criterion rename, F2 (#896, #892)"
in_reply_to: null
---

# Ready for PR landing: perturb-seq-eval — Amendment 5 (v0.6.0-a5): T1 retitle, narrowing, gate->criterion rename, F2 (#896, #892)

branch: perturb-seq-eval
sha: 4cbaca722c92a9aaead0102122b24678b502f37d (pushed; origin/perturb-seq-eval == HEAD)
diff_hash: 08729fa (vs origin/main 600e510)
receipt: workstreams/perturb-seq-eval/qgr/bioFM-matthew-mo-perturb-seq-eval-perturb-seq-eval-perturb-seq-eval-qgr-pr-prep-20261105-0405-08729fa.md
receipt_parent: iteration-complete c9d568c (4 reviewers + scorer on the A5 diff); pr-prep receipt is --derived-from it (delta = .aiadlc instinct metadata + context/QGR-log files only)
draft: false
migrations_pending: []
scope: Amendment 5 (v0.6.0-a5) - T1 retitle, contribution narrowed to the multi-agent group, 'gate' -> 'pre-registered criterion', F2 SUBMISSION.md fix (CTO #896, #892)

## Receipt trap (as you expected)
This dispatch's own context commit moves Hash E past 08729fa. After sending I will commit it and sign a
second receipt --derived-from 08729fa, then push. Verify `git diff --stat 4cbaca72..<new tip>` = dispatch
file + receipt only.

## What landed on the branch (bef363fe..4cbaca72)
- T1 title on every surface: paper.tex \title/pdftitle, PREREGISTRATION.md, CITATION.cff, publish.yml,
  README.md, paper/README.md, docs/THESIS.md, SUBMISSION.md title row + regenerated paste block.
  New test: every title surface == paper.tex \title.
- Narrowing per the ratified sweep: S3, S6 (CATTS bullet, R2 struck), S9 ((b'')+(b''-D)), S12, S13, S14
  (S14 T1 sentence now also states the H5 transfer failure - QG F8). S5 kept per sweep. Abstract untouched.
- 'gate' -> 'pre-registered criterion' (short form 'criterion') on current v0.6.0 surfaces incl. the
  fill_v060_numbers generator and two test pins. Recorded as Amendment 5 (A5-3) with the old->new map.
- F2: c0ec931 is on origin/main; run 40985145366 executed "Compile LaTeX (generates the .bbl)" and
  the .bbl assertion with success (verified via gh run view). Approval item 1 CLOSED; Path A text fixed.
- references.bib: lee2026catts, morandi2026sprt from the arXiv API (titles/authors/primary match).
- Test fix: A4 lock-commit test compared auto-abbreviated %h (now 8 chars) - full hashes now.
- No number, hypothesis identity, threshold or outcome changed. H5 still fails. A5 is NOT in
  amendments_v060.json or tab:amendments. resPreregVersion stays v0.6.0-a4.

## Principal rulings taken IN-SESSION 2026-11-04 (please record as approvals rows)
1. Substitute term: "pre-registered criterion".
2. A5 form: tagged `v0.6.0-a5` (was parked in #896).
3. Locked PREREGISTRATION.md body keeps "gate" verbatim; A5-3 maps it.
4. Historical v0.5.0 surfaces (v050_*.tex, corrections.tex, run_record_amendments.json) not renamed.

## Escalations (not edited - ratified or frozen text)
- F24: abstract sentence 1 "Multi-agent group-generation systems spend test-time compute uniformly"
  is unhedged while the paper now cites morandi2026sprt (a multi-agent compute governor) and the intro
  says "As operated here". Abstract frozen -> ride with 1.1-e.
- F21: CATTS sentence says its "uncertainty statistics" are computed "(their S3.1)"; a reviewer read
  the stats as defined in S4.1 (S3.1 builds the vote distribution). Not measured at full text by me.
- F22: (b'') "we cite their abstracts" sits beside (b''-D)'s CATTS S2/S3.1 quotes; and "we make no claim
  about how our signal relates" is followed by a contrast sentence.
- F23: "$N$ role-specialised agents" beside CATTS "$N$ candidate actions".

## Deferred / open
- F11: CITATION.cff keeps version 0.6.0 / 2026-10-16 (the minted v6 deposit, old title) but now carries
  the new title; publish.yml carries a comment that the new title takes effect at the next deposit
  (fork (b), principal's).
- arXiv override 1906 -> 1904 chars (rename only); re-ratification still parked; comment says so.
- Still parked: FINDING 1.1-e, override re-ratification, F1 venue wording, morandi sentence.
- Test follow-ups below threshold: override content guards, paste-block render test, locked-body diff
  test, no-'gate' guard.

## Checks at 4cbaca72
ruff format clean; lint (E9,F63,F7,F82) clean; tests 1089 passed, 13 skipped, 0 failed;
render_publish_description --check and fill_v060_numbers --check match; paste block == fresh
arxiv_package.py metadata. No local TeX: the .bbl/compile check is CI's (arxiv-package workflow).

## CTO action
/pr-cto-land perturb-seq-eval (principal-invoked, main checkout), after verifying the derived receipt
at the new tip. Record the four in-session rulings. Route the escalations to the principal.

next_handoff: cto /pr-cto-land
