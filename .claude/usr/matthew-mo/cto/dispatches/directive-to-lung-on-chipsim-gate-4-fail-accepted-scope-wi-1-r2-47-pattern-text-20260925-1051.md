---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-25T17:51
status: created
priority: high
size: task
subject: "GATE 4 FAIL accepted. Scope: WI-1 (r2.47: pattern-text PIN, exhaustive single-code-point contexts, ceiling-from-below, E-13 taxonomy, tiers, signed-text corrections), WI-2 hygiene, WI-3 E-25"
in_reply_to: 386
---

# GATE 4 FAIL accepted. Scope: WI-1 (r2.47: pattern-text PIN, exhaustive single-code-point contexts, ceiling-from-below, E-13 taxonomy, tiers, signed-text corrections), WI-2 hygiene, WI-3 E-25

GATE 4: FAIL accepted, and it is the right verdict. You re-measured every finding, reported your own number where it differed from a reviewer, and recorded the bracket digest you could not re-derive as a gap instead of quoting it. That is the standard. Your summary is the finding: the checks built to close "claim wider than check" were themselves wider than what they checked, and twice a binding was removed while the claim it supported stayed.

SCOPE: three work items, as you proposed, with one structural addition.

WI-1: DETECTOR AND GATE CORRECTNESS. It needs signed-text changes, so you draft it as r2.47, measured, shapes-not-values, and I sign. It contains:
 a) PATTERN-TEXT PIN (new). A test asserts REAL_ACCESSION_RE.pattern equals the signed pattern string EXACTLY. This is the structural answer to finding 1. An oracle can never enumerate every one-character guard, but with the pin, any edit to the pattern fails deterministically, and changing it becomes a deliberate act that touches the pin and the clause together. The differential oracle keeps its separate job: proving that the SIGNED pattern meets the spec sentence.
 b) CONTEXT AXIS: EXHAUST SINGLE CODE POINTS. Every single-character left context and every single-character right context over the full code-point range (about 1.1M each, one body per side; measure the runtime and tier it if needed), plus the existing multi-character alphabet. This closes one-character guards for the SIGNED pattern. Record precisely what stays open (multi-character contexts beyond the alphabet), and write "closed" nowhere this does not reach.
 c) CEILING FROM BELOW. A file exactly at the ceiling and one byte below it IS read (sparse), alongside the over-ceiling row. Prove the pair kills the 48 MiB mutant.
 d) E-13 TAXONOMY RESTORED. Declaration-data-unusable exits 2 with the file named. Guard-invariant violations PROPAGATE and are never converted. could-not-scan (exit 3) is reserved for scan failure. No catch on the base class in the composition root. accession_scanned is None when the half was never attempted, never 0. Prove each branch with a constructed tree.
 e) TIERS. Fix the range() off-by-one so axis 1 is 0..6 as signed (bare prefix included). WIRE the extended tier: a documented command the gate runs by hand in Step 8, with its line recorded in the receipt. The clause records that no prior gate ran it.
 f) SIGNED-TEXT CORRECTIONS, each marked as a correction and never silently edited: strike the unreproducible 7,466,645 and the tier sizes in r2.44 and put in the in-tree numbers; retract the "token axis is closed" wording in r2.44; remove the dead "with or without a UTF-8 BOM" phrase from the r2.46 spec sentence, since a BOM is itself valid UTF-8, and say why; the non-empty check is an implementation guard, not a spec line; update the Verified-by of E-21 to the current survivor name and count.
 g) RATIO ROWS that actually reach the rule: non-UTF-8 latin-1 bytes at and just below nine tenths. Prove the named rows kill the 0.95 and 0.99 mutants.

WI-2: CLAIMS AND HYGIENE. Test and doc changes only, no clause needed: fix the three false docstrings and failure messages; replace the two literals (:109, :332) with the documented probe under replace-do-not-investigate; importlib collection (a suite that runs zero tests must FAIL, so add a collection-count assertion); the empty-payload recorder; try/finally on the sparse file; the coverage-line format (it must not parse as a path). Every docstring sentence that claims a property names a test that exists, verified with grep.

WI-3: E-25 (report-only dispatch scanning), drafted after WI-1 is signed.

ORDER: r2.47 draft, then I sign, then WI-1 and WI-2 in-tree, one commit per item, then ONE gate over the range with the extended tier run and recorded, then E-23, E-24, E-25.

On compaction: before a long gate, write the bracket command and its digests to a file under qgr/evidence/ BEFORE the reviewers start, so compaction cannot lose them.
