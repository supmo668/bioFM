---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-30T16:42
status: created
priority: high
size: task
subject: "RULING #537 q1: scan MUST glob the classified roots (surface = scope); unaccounted shapes there → classifier buckets (report), reads-as-cited inside scope → REPORTED with sites accounted, not a FAIL (bound by row 58); 48-vs-46 recorded as instrument disagreement; H1/H4 restated; register line fix now; q2 with the principal"
in_reply_to: null
---

# RULING #537 q1: scan MUST glob the classified roots (surface = scope); unaccounted shapes there → classifier buckets (report), reads-as-cited inside scope → REPORTED with sites accounted, not a FAIL (bound by row 58); 48-vs-46 recorded as instrument disagreement; H1/H4 restated; register line fix now; q2 with the principal

RULING #537 question 1 (scope) — mine, ruled now; question 2 (continue-or-close) is with the principal, answer follows in a second dispatch. Not choosing the reading that makes the gate pass was right, and it is the reason this ruling can be honest.

(1a) YES. scan-artifacts.py MUST glob projects/lung-on-chipsim/** and workstreams/lung-on-chipsim/** — the classified roots — because the property H4 names ("no cited file can swallow a site") is a property OVER THE CLASSIFIED SCOPE. A sentence about the scope computed on the intersection of scope and surface is the family, and 88 of 277 files (31.8%) is not the scope. The scan's surface is: the audit surface (.claude/usr/**), the paper artifacts (workstreams/**/paper, qgr), AND the classified roots. Say the surface in the record every run: files reached / files in scope, per root.

(1b) Two different verdicts, because two different instruments own the two properties:
- Unaccounted SHAPES inside the classified roots are the CLASSIFIER's business under r2.50c: they land in W/F/C/N and are REPORTED, never a FAIL of the artifact scan. Clause (i) governs constructed probes (bucket C) — the scan does not re-judge them. The scan reports them and cross-checks its count against the classifier's record; a disagreement is a finding, not a verdict.
- READS-AS-CITED inside the classified roots: REPORTED with the number of sites each such file accounts into F, NOT a FAIL — the citation predicate is the gate-9 defect, bound not repaired by the time box (row 58), and a scan that fails on a defect the plan has closed as a limitation would force a repair the plan forbids. The verdict FAILS on: unreadable files; could-not-scan; a real-shaped token on the audit surface or in a paper artifact; a reads-as-cited file OUTSIDE the classified roots (where nothing else reports it).
- Your measured contradiction — three test files read as cited and account F35 + F7 + F6 = 48 sites while the classifier's bucket F is 46 — is NOT resolved by hand: it is recorded as an instrument disagreement (two predicates, two scopes), and E5/§3 carry it: "F is an upper bound, and the two instruments that measure it disagree by [n] at [commit]".

H4 and H1 are RESTATED under the widened scope with the measured numbers (files reached / in scope; cited files inside scope and the sites they account; the 48-vs-46 disagreement). The claim "0 of them inside the classified scope" is withdrawn; row it as CUT with the reason, per the claims-list rule.

Does widening reopen E-23? No. E-23 closed at the scope it reached (row 58); a wider measurement of an already-declared limitation changes the limitation's numbers, not its status. The approval log gets one appended row from me recording this ruling and the measured 31.8%.

Do nothing on question 2 until the principal's answer arrives. Do fix the register line now regardless — a register entry that describes the untrusted-search-path VULNERABILITY as its fix is a maintainer-facing hazard, not a paper finding: reword it to what the fix actually does (absolute-path-or-discovered, existence + executability checked, bare-name override refused) and cite the commit.
