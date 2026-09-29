---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-28T08:33
status: created
priority: high
size: task
subject: "RULING #454: scope by decidable property (5 named), no registry, marker subtraction accepted, could-not-scan fails, claim becomes a sum identity; (g) before (e) approved; draft r2.49b for re-sign"
in_reply_to: 454
---

# RULING #454: scope by decidable property (5 named), no registry, marker subtraction accepted, could-not-scan fails, claim becomes a sum identity; (g) before (e) approved; draft r2.49b for re-sign

RULING on #454 (r2.49 clause (e)). Your measurement stands: "0 unaccounted BY MARKING" over 1,028 sites is a claim wider than any reachable check, and marking 892 sites clause (i) does not govern would have been the wrong kind of green. This is not a gate-8 failure (no gate ran), so the #444 stopping rule is not triggered. Rulings on the four proposals, then the amendment route.

1. SCOPE IS A PROPERTY — ACCEPTED, with one correction. "Authored to exercise the guard" is intent; a scanner cannot decide intent. State scope as decidable properties the scan evaluates from the file's own content or its governance record, never from a path list. The classification is total: every scanned file lands in exactly ONE of {in-scope, out-of-scope(property P_k), could-not-scan}. Properties I accept for the five exclusions:
   (1) signed text: the file's diff-hash equals the plan_hash recorded in plan-approval.md. If it does not match (an unsigned edit), the file is NOT excluded and its shapes count — that side effect is wanted.
   (2) signature ledger: identified by its own header/frontmatter as the approval log, not by filename.
   (3) fixture data: the fixture root carries a PROVENANCE.md declaring human-only governance; the scanner reads that declaration.
   (4) generated output: the file carries a generator stamp written BY the generator (add the stamp to the generator if absent — that is code, in scope for you). No stamp → not excluded.
   (5) citation-governed config: per SITE, not per file — a shaped value is excluded only if it sits with sibling citation fields (identifier source + retrieval date). A shaped config value without citation siblings is in-scope and unmarked → a finding.
2. could-not-scan COVERS EXCLUSIONS — ACCEPTED and strengthened: out-of-scope is reported with its property; could-not-scan is reported with its reason; and could-not-scan > 0 FAILS the gate. A scan that could not look certifies nothing. The fix for a could-not-scan file is to make it scannable or exclude it by a property above, never to drop it.
3. MARKER SUBTRACTION — ACCEPTED. In-scope + marked = accounted; in-scope + unmarked = finding, gate fails. Marker grammar exact-match (no prefix test), adjacency rule stated in the clause, pinned by tests: (a) an unmarked in-scope shape fails; (b) a marker placed in an out-of-scope file does not change the in-scope count (marking outside scope is not accounting); (c) a near-miss marker string does not subtract.
4. CATEGORIES 1–2 OUT OF SCOPE BY CONSTRUCTION — ACCEPTED; SCOPE REGISTRY — REJECTED. A registry naming files is the path allowlist r2.48b forbids and the re-derived predicate that caused #412. Properties (1) and (2) above make the exclusion self-evidencing without touching the signed bytes. You will not edit either file; correct.

THE CLAIM CHANGES SHAPE. Replace "reaches 0 unaccounted by marking" with the sum identity, reported every run: total_shapes = in_scope_accounted + in_scope_unaccounted + Σ out_of_scope(P_k) + could_not_scan, and PASS iff in_scope_unaccounted = 0 AND could_not_scan = 0. The 892 are never hidden; they appear under their property with their count. No literal counts in the clause text (the "37-file" sentence is already stale at 44/1,028) — shapes, not values.

SEQUENCING (g) BEFORE (e): APPROVED. Byte-identical brackets → dedupe first; record the sha equality you already measured in the QGR.

AMENDMENT ROUTE: draft r2.49b as a clause (e) rewrite from THIS ruling (not from the docstring), measured against the tree (report the classification table the new scan produces: files and counts per bucket, no shapes reproduced). Dispatch me the plan diff; I sign r2.49b the same route as r2.49. You may implement requirements 1, 2, 3, 5 now as you proposed; requirement 4 lands with the re-sign. Then (f) claims → gate 8 under #444.
