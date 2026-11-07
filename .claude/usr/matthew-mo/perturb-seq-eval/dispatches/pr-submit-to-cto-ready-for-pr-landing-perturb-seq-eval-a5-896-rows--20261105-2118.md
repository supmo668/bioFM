---
type: pr-submit
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-11-05T21:18
status: created
priority: high
size: task
subject: "Ready for PR landing: perturb-seq-eval — A5 (#896) + rows 15-18 (#905); SUPERSEDES the 3203c52d submit"
in_reply_to: null
---

# Ready for PR landing: perturb-seq-eval — A5 (#896) + rows 15-18 (#905); SUPERSEDES the 3203c52d submit

SUPERSEDES my Amendment 5 pr-submit (tip 3203c52d, receipt 08729fa). Land this one instead.

branch: perturb-seq-eval
sha: f51ef1a32d595b6f641f17bac977a82497bec5d5 (pushed; origin == HEAD)
diff_hash: 8df7dbd (vs origin/main 600e510)
receipt: workstreams/perturb-seq-eval/qgr/bioFM-matthew-mo-perturb-seq-eval-perturb-seq-eval-perturb-seq-eval-qgr-pr-prep-20261105-2117-8df7dbd.md
receipt_parents: iteration A c9d568c (bef363fe..96bd3761), iteration B 1f2dbd9 (5487bac5..107bdeea); 4-reviewer fan-out + scorer each.
  Delta outside both gates = .aiadlc instinct metadata + context/QGR-log files. diff-hash excludes
  dispatches, so THIS dispatch's context commit does not move Hash E.
draft: false
migrations_pending: []

## Iteration A — #896 (unchanged from the superseded submit)
T1 title on every surface (+ test); narrowing per ratified sweep; 'gate' -> 'pre-registered criterion'
on current v0.6.0 surfaces; F2 SUBMISSION.md fix; lee2026catts + morandi2026sprt bib from the arXiv API
(no affiliation fields); A4 lock-commit test now compares full hashes.

## Iteration B — #905 rows 15-18
- Row 15: SUBMISSION.md — venue TechRxiv, posting BLOCKED until the principal reads TechRxiv's terms
  first-hand (403 to agents, reported, not retried); institutional route removed; exactly one preprint
  server, archives do not count; arXiv only via Path-2 endorsement FIRST, closed once TechRxiv posts
  (the old "superseding revision" route in 7.2 removed); Parts 3-5 marked as reading venue-neutral;
  7.5 step 3 decided, step 4 (first-hand read) is the blocker.
- Row 17: abstract opening = §1.1 + 1.1-e ("already reported by \textsc{CATTS}"); CFF/publish.yml
  regenerated (2363 chars). Also closes my F24 escalation (opening now "as operated here").
- Row 18: the 1916-char override applied with the row-14 rename -> 1914 chars, 0 non-ASCII; comment
  records c1-c10 and the rename; the false "tooling asserts their presence" line corrected. A new test
  now pins the result tokens and stated length (it did not exist; mutation-checked).
- Row 16: A5 in tab:amendments (dagger, caption "A1--A4 ... before any data; A5 after the outcome") and
  amendments_v060.json ("post_outcome": true); generator + tests extended; a new test ties the row, the
  dagger and the caption to the flags (6/6 mutations caught). PREREGISTRATION.md A5 now says the tag is
  to be created by you, with a dated note that the record revision is not a sixth amendment.

## CTO actions
1. /pr-cto-land perturb-seq-eval (principal-invoked, main checkout).
2. Create the annotated tag `v0.6.0-a5` on the LANDED commit (the merge commit that carries the final
   A5 wording), NOT on f2bb193 (its text still says "not recorded"). An amendment marker, not a release.
3. Record as approvals rows the principal's in-session rulings: 2026-11-04 (term "pre-registered
   criterion"; A5 tagged; locked body keeps "gate"; v0.5.0 surfaces not renamed) and 2026-11-05
   (override applied with the rename; Morandi held for your section check; you create the tag; staging
   PR via pr-submit).
4. Row 19 still owed: verify Morandi §III / §VII-C14 / §VII-C17 at arxiv.org/html/2605.19193 (see my
   re-#905 ack). On your verification I insert the sentence after (b''-D).

## Still escalated / noted
- F21/F22/F23 (ratified CATTS/(b'') wording: §3.1 vs §4.1; "we cite their abstracts" next to §2/§3.1
  quotes; overloaded $N$) — unchanged, yours to route.
- F11: CITATION.cff version 0.6.0 carries the new title; the minted v6 deposit has the old one. Re-deposit
  is the principal's fork (b).
- B20: my own 2026-11-02 dispatch payload (re-874, tracked) says "Morandi (Cisco)". That affiliation is
  UNVERIFIED (#905 §5) and must not be copied anywhere; I do not edit dispatch payloads.
- TechRxiv field mapping deliberately not written: it would rest on secondary sources until the read.

## Checks at f51ef1a3
ruff format clean; lint clean; tests 1091 passed, 13 skipped, 0 failed; render/fill --check match;
paste block == fresh arxiv_package.py metadata. A reviewer compiled with tectonic: clean but a 0.66pt
overfull box, since fixed.

next_handoff: cto /pr-cto-land
