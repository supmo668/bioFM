---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-29T17:45
status: created
priority: high
size: task
subject: "RULING #506 (principal, verbatim): requirement 5 DESCOPED TO REPORTING — signed r2.50c (ae894db): buckets W/F/C/N, file-level citation counts, needs-curation reported never marked (stated limitation + principal curation item); pass = all classified AND could-not-scan 0; gate 9 = last"
in_reply_to: null
---

# RULING #506 (principal, verbatim): requirement 5 DESCOPED TO REPORTING — signed r2.50c (ae894db): buckets W/F/C/N, file-level citation counts, needs-curation reported never marked (stated limitation + principal curation item); pass = all classified AND could-not-scan 0; gate 9 = last

RULING #506 — the principal chose your recommendation, (b) with (a) folded in. Put to the principal directly (AskUserQuestion, this session, 2026-09-29); option chosen verbatim: "Descope req 5 to reporting; file-level counts; 56 → limitation". Signed as r2.50c, plan_hash ae894db (was 6795e2d), approval-log row 57 (route: principal via AskUserQuestion, quoted), plan-gate verify green. Restore the three signed plan files from main (your path).

What changed in the signed text — three sentences, read against each other before the sign:
1. (e) amendment pass condition: PASSES iff every in-scope site is CLASSIFIED into exactly one bucket AND could-not-scan = 0. "in-scope unaccounted = 0" is withdrawn as the pass condition — measured, it cannot be reached truthfully.
2. Requirement 5 → REPORTING, four buckets, reported by count and file every run:
   (W) marker on the site's line or within MARKER_WINDOW_LINES (=2) above — your 20;
   (F) FILE-LEVEL citation header (CID + retrieval date in the module docstring/file header), judged on the enclosing file the way P5 is judged on the enclosing mapping — your 45; NO inline restatement;
   (C) constructed shape-only probe governed by clause (i), which you can classify WITHOUT comparing any constant to an adjacent literal or looking anything up — the differential's 12 and whatever else meets that test;
   (N) NEEDS-CURATION — no citation in the file and the status needs the forbidden comparison (e.g. test_unparseable_exclusions.py's 18). NEVER marked. Counted and listed by file in the harness output, a STATED LIMITATION in Stage 1 next to the out-of-guard-scope count, and the PRINCIPAL'S Stage 2 curation item.
   Sum identity: in-scope = W + F + C + N; no marker on a guess.
3. The CTO addition's done-condition now reads: every in-scope site in exactly one of W/F/C/N (in_scope_unclassified == 0) AND could_not_scan == 0; N reported, never marked. Stopping rule: gate 9 runs on the five mechanisms + the four-bucket reporting; E-23 closes after it either way.

Implement requirement 5 as reporting: the classifier for W/F/C/N with a false-exclusion test per bucket (a file-level header must account its sites; a site with no header must NOT be accounted by F; a probe that fails the clause-(i) test must NOT be C), the N list by file (counts and files only — no values, no identifiers), and the sum-identity test extended. Then gate 9, the last gate. Your "not marking 84 sites on a best guess" is the right instinct and it is now the rule.

Recorded with appreciation: the measurement that requirement 5 had twice produced machinery whose claims outrun the tree is exactly the finding the design note predicted; the mechanisms are the transferable part and they are in.
