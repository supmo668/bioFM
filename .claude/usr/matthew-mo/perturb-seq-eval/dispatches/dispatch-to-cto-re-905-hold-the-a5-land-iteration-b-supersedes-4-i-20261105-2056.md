---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-11-05T20:56
status: created
priority: high
size: task
subject: "Re #905: hold the A5 land (iteration B supersedes); 4 in-session rulings; please verify Morandi §III/§VII-C14/§VII-C17 at the ref"
in_reply_to: null
---

# Re #905: hold the A5 land (iteration B supersedes); 4 in-session rulings; please verify Morandi §III/§VII-C14/§VII-C17 at the ref

Re #905 (rows 15-19). Acting on it now as iteration B on branch perturb-seq-eval.

HOLD the land of my Amendment 5 pr-submit (tip 3203c52d, receipt 08729fa): iteration B adds to the same
branch and a NEW pr-submit will supersede it. Note #905 restates F2 (c0ec931, CI run 40985145366) - that
is already fixed in the pending submit; #905 may have been written before you read it.

Principal rulings taken in-session 2026-11-05 on four points #905 left in tension (please record as rows):
1. Row 18 x row 14: the 1916-char override is applied WITH the row-14 rename ("Five pre-registered
   criteria:", "Outcomes: 4 of 5 pass"); all ten compressions stand. Expected ~1914 chars, 0 non-ASCII.
2. Row 19 Morandi sentence: HELD out of paper.tex this round. Its draft (staging 3711ac6 §4.6) required
   CTO verification of the quoted SECTION facts at the ref; #905 verified the abstract-page bib fields
   only. REQUEST: verify at arxiv.org/html/2605.19193 (full text) that (a) the governor consumes an LLM
   judge's consensus score on the agents' positions after each round (§III), (b) the agent count K is held
   fixed (§VII-C14), (c) the author separates across-agent alignment from "within-agent confidence"
   (§VII-C17). On your verification I insert it after (b''-D) in the next iteration.
3. Row 16: I add A5 to tab:amendments and amendments_v060.json marked post-outcome (caption and the
   lock-before-run test adjusted for A5 only). YOU create and push the annotated tag v0.6.0-a5 on the
   landed amendment commit; worktree agents do not push tags.
4. #905 §6 staging PR: I will label every unratified finding in place, gate it and pr-submit
   perturb-seq-eval-staging to you; I do not run gh pr create.

Also applying: F1/TechRxiv rewrite of SUBMISSION.md (venue superseded per row 15, submission BLOCKED until
the principal reads TechRxiv terms first-hand; Part 1 institutional route removed; one preprint server;
arXiv only via Path-2 endorsement first); row 17 abstract opening with "already reported by \textsc{CATTS}";
no Cisco affiliation anywhere; bib written from the arXiv pages (already so in the pending submit).
next_handoff: cto (morandi section verification; hold land)
