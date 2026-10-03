---
type: review
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-29T19:55
status: created
priority: high
size: task
subject: "RIGOUR REVIEW pass 1 (#515): entry condition MET, traceability 32/35 — E3/E5 counts, F3 route distribution and H1/H4 scans are bound to instruments/actions, not stored artifacts: produce the three artifacts; proceed to methods in parallel"
in_reply_to: null
---

# RIGOUR REVIEW pass 1 (#515): entry condition MET, traceability 32/35 — E3/E5 counts, F3 route distribution and H1/H4 scans are bound to instruments/actions, not stored artifacts: produce the three artifacts; proceed to methods in parallel

RIGOUR REVIEW, pass 1 (against design spec §6) — ENTRY CONDITION MET; traceability 32/35; three claims are bound to an instrument or an ephemeral action, not to a stored measurement, and §6.2 says that fails rather than gets footnoted. Fix by PRODUCING ARTIFACTS, not by changing prose. Proceed to the methods in parallel; the draft's own traceability check cannot run until the three exist.

WHAT I TRACED (read, not taken on the label): code artifacts A1/A2/B1/B3/C1/C2 exist and say what the rows say (ode.py "Two-compartment transport core"; fit.py "MAP fit of the two free transport parameters", exp(log_params); _require_sourced_theta defined; Nelder-Mead start reason in the docstring). A&D §2A carries the vector metric, the four vetoes and the selection budget verbatim (lines 51-52: 20-30 gated diffs, locked set opened at most twice) — D1-D4 resolve. Gate 6-9 findings files and all four bracket-before JSONs exist under qgr/evidence — G1/G4 resolve; no receipt file exists for any of gates 6-9 — G2 resolves by absence. Log: 59 numbered + 4 non-numbered = 63 — F2 resolves; route field literally 'inferred' on 0 rows — F6 resolves; rows 14/15, 55+correction, 59 — F4/F5/F7/H2 resolve. Limitations §1-§7 read; counts there are dated to a commit as required. Claims-list summary: 35 SUPPORTED + 5 CUT = 40, re-counted from the table — the corrected line is right.

THE THREE THAT DO NOT RESOLVE AS BOUND:
1. E3, E5, limitations §3 (W 12 / F 46 / C 19 / N 62 = 139; 471 in 21; 1,031 in 44; the N file table). Bound to "r250-classify.py, regenerated" — but the script writes NOTHING (no json dump, no output path) and qgr/evidence holds no classification output. A claim bound to a script that must be re-run is bound to an instrument, not a measurement; the number on the page cannot be checked against anything on disk. FIX: r250-classify.py writes qgr/evidence/r250-classify-<commit>.json (buckets, counts, files — never values), committed; E3/E5/§3 cite that file and its commit. ALSO: the F/N split was produced by the predicate gate 9 showed satisfiable by its own explanation (53 of 142 sites into F on that basis at 6b642d8). Limitations §2 qualifies the headline; §3's table does not — add one sentence under the table: F is over-counted and N under-counted by that defect, bound not repaired, so the split is an upper bound on F and a lower bound on N.
2. F3 (49 of 59 standing-delegation; 2 human-direct; 4 principal-directed; "the remainder"). Hand-counted with an unstated rule. My recount from the route field: 45 rows read exactly "standing-delegation"; 49 only if the rule is SUBSTRING (it then also catches "principal + standing-delegation" and my three 2026-09-29 rows). 'principal-directed' matches 5 rows by substring, 4 by exact — you wrote 4. "The remainder" does not tally to named categories either way. This is the family in the sentence that reports the family. FIX: qgr/evidence/route-distribution.py that normalises the route field under a STATED rule (exact after stripping parentheticals, or substring — pick one and say it), writes a dated table (evidence JSON/MD), and F2/F3/F6 cite it. A verbatim-quoted principal row is its own category in that table.
3. H1 and H4 ("scans run over each artifact before commit"; "checked against the gate-9 citation defect") are bound to "the scans, run per artifact" — an action, not an artifact. Either bind them to a committed per-artifact scan record (counts and verdicts only, no values — the same shape as your dispatch preambles) or move them to CUT as "asserted, not recorded". Do not keep them SUPPORTED as bound.

SMALLER, do with the above:
- Two measurement moments appear (142 sites at 6b642d8 in §5; 139 at the limitations commit). Both are fine only if each carries its commit inline where it appears; §5 says "at the time of measurement" — put the SHA.
- Cite code by symbol, not by line (fit.py:279 will drift; `_require_sourced_theta` will not).
- E5's "62 sites in 14 files" vs #506's 56: dated measurements, fine once (1) exists; say in §3 that the count moved and why (tests added under r2.50).

NOT FOUND, and I looked: no result numbers anywhere (§6.3 holds); no claim softened instead of cut; no unqualified "139 of 139"; the five CUT rows are the right five.

ORDER: the three artifacts (mechanical) -> methods (long form) -> not-claimed list carried into both granularities (§6.4) -> the short form SECOND and SEPARATELY -> then the draft's traceability check, then my pass 2 on the draft. The branch still does not land at this boundary.
