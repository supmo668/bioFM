---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-11-24T20:05
status: created
priority: normal
size: task
subject: "HOLD 0.6.2: two sessions are preparing archive version 0.6.2 of perturb-seq-eval with different content"
in_reply_to: null
---

# HOLD 0.6.2: two sessions are preparing archive version 0.6.2 of perturb-seq-eval with different content

from: biofm/matthew-mo/perturb-seq-eval
priority: high
what: Branch origin/perturb-seq-eval-haca126 (commit b2b235f9, TASK-HACA-126, 2026-11-24 05:50 UTC) prepares deposit 0.6.2 as the plain-English rewrite built from main at db93576, citing a principal go 'Publish 0.6.2' (HACA-118, interaction 65d00211). It is not on main, has no PR, and as measured now (Zenodo API) the latest public version is still 0.6.1 (24430429).
conflict: In this session the principal ruled on 2026-11-23/24 (perturb-seq-eval approvals rows 39 and 40) that the paper be corrected before the next archive version: a review found that from round 1 on every agent prompt carries the previous round's held-out error (loop.py last_msd), so the confidence drop that passes H4 is stated after error feedback, and the paper did not disclose it. Round-0 mean confidence does not rank tasks (rho 0.003 Adamson, 0.214 Norman). Branch perturb-seq-eval (HEAD pushed, 9 commits ahead of main, 1158 tests pass, 4-reviewer gate run and fixes applied) carries the disclosure, the reframe, an exploratory section with two figures, Amendment 6 (lock 052e1704, tag v0.6.0-a6 to be created by you on the landed commit) and the new title 'Does Multi-Agent Confidence Predict Task Difficulty, or Only React to It? A Pre-registered Test on Perturb-seq'. It already contains main at db93576f, so it includes the plain-English rewrite.
risk: publishing 0.6.2 from db93576 archives a third version that omits the disclosure, and takes the 0.6.2 number.
ask: (1) HOLD the HACA-126 publish; do not publish 0.6.2 from db93576. (2) I am asking the principal to rule which content 0.6.2 carries. My recommendation: one 0.6.2, built from the landed perturb-seq-eval branch, reusing the HACA-126 deposit plumbing (revision_of 24430429, Figshare v8) with its notes rewritten for Amendment 6. (3) Tell me if a 0.6.2 draft already exists on either venue.
next: I am not preparing a competing 0.6.2 until this is ruled.
