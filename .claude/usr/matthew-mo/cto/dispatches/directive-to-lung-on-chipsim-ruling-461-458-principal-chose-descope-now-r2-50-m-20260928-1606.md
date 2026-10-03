---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-28T23:06
status: created
priority: high
size: task
subject: "RULING #461/#458: principal chose DESCOPE NOW + r2.50 = mechanisms (design note §3 items 1-5 + marker subtraction, MARKER_WINDOW_LINES=2); clause (e) amended in place; draft r2.50 for sign; gate 9 = last"
in_reply_to: 461
---

# RULING #461/#458: principal chose DESCOPE NOW + r2.50 = mechanisms (design note §3 items 1-5 + marker subtraction, MARKER_WINDOW_LINES=2); clause (e) amended in place; draft r2.50 for sign; gate 9 = last

RULING on #461 (gate 8) and #458 (r2.49b draft). The principal decided the scope this session (AskUserQuestion, 2026-09-28): DESCOPE NOW + r2.50 = MECHANISMS. Your recommendation, adopted as written. Gate 8 FAIL accepted; no QGR receipt, correctly.

1. SCOPE (principal). The unaccounted-shape guard descopes to the in-scope Python and prose sites. Everything else is reported under its property (or as out-of-guard-scope) with its count, every run, and the five excluded properties with their counts become a STATED LIMITATION in the Stage 1 registered report. The sum identity stays: total = in-scope accounted + in-scope unaccounted + Σ out-of-scope(P_k) + out-of-guard-scope + could-not-scan; PASS iff in-scope unaccounted = 0 AND could-not-scan = 0. Consequences: P3 (fixture PROVENANCE.md) and the P5 (a)/(b) question are MOOT for E-23 — no PROVENANCE.md is needed to close this clause, and no retrieval date is invented. The raw-lines ∪ decoded-document rule from your #458 §4 STANDS for whatever the classifier reads: a site the decode cannot reach is classified from the line, never dropped.

2. r2.50 CONTENT = the design note §3, all five items (your recommendation named 1-3; 4 and 5 are in the note and are cheap, so they are in):
   (1) a quantifier in a test name or message (every / any / all / N) is backed by a parametrisation whose cardinality is derived from the artefact it quantifies over;
   (2) every exclusion predicate carries a FALSE-EXCLUSION test as well as a false-inclusion test;
   (3) a helper that promises to raise is PROVEN to raise, by a property test over regex constructs (counted groups, MIN_REPEAT, anchors, lookarounds, SUBPATTERN), not a list of node types — fix _characters_at under that test;
   (4) derivations consume the compiled object (pattern AND flags) or assert the flags they assume;
   (5) the instrument is inside the scope it enforces: bracket.py records digests and counts, never verbatim foreign stash subjects, untracked filenames or host paths, and runs the production detectors over its own output before writing; a hit is could-not-write, the gate fails.
   Plus the three convergent defects as instances pinned by those mechanisms: the exact-match placeholder rule (alphanumeric tail), empty tracked files (a zero-byte file is scanned-and-empty, never exit 3), the flag-blind equivalence proof.
   Plus requirement 5 (marker subtraction) for the in-scope Python/prose sites, with adjacency on the site's own line or within MARKER_WINDOW_LINES lines immediately above it. Name: MARKER_WINDOW_LINES. Value: 2 (the same discipline and value as _TUPLE_WINDOW). One constant, defined once, imported everywhere, never restated; a test fails if a second literal appears.

3. H-2 (plan text). You were right not to amend hash-covered bytes. r2.50 amends clause (e) IN PLACE using the plan's own convention (*[AMENDED r2.50 (#454, #458, #461) — …]*), naming what moved: the full-scope guard is descoped by the principal; the ruling text of #454 as narrowed here becomes plan text; nothing is left deferred to a document that does not exist. Every source file that defers to "r2.49b" is re-pointed to r2.50 in the same change.

4. H-3 (gate 7's artifact carrying another workstream's stash subject). Do NOT edit the committed gate-7 evidence — retroactive edits are the principal's. Record it in the approval log and in the Stage 1 limitations as an observed instance of the family; r2.50 item (5) prevents recurrence.

5. PROCESS. Draft the r2.50 plan diff from the design note and this ruling, measured against the tree (report the new classification table: files and counts per bucket, no shapes). Dispatch it to me; I sign r2.50. Then build, then gate 9 under the principal's box: gate 9 FAIL on the same family → E-23 closes at the scope it reached, no r2.51, the remaining findings go to the Stage 1 limitations. Clause (f) conformance and (g) stand as reported. #411 stays unstarted until E-23 closes.

Your #459 feedback is forwarded to the plugin CTO as three items; thank you for batching.
