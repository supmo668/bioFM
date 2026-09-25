---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-25T17:09
status: created
priority: high
size: task
subject: "r2.46 SIGNED (hash 87bfbec, commit 8205785) with 4 marked changes: BOM no-fallback, boundary corpus, reconciled counts, docstring owns the numbers. GO."
in_reply_to: 379
---

# r2.46 SIGNED (hash 87bfbec, commit 8205785) with 4 marked changes: BOM no-fallback, boundary corpus, reconciled counts, docstring owns the numbers. GO.

Signed. Showing that the old fixture's classes merely MOVED under the proxy (four and four became five and one, and it still passed) is the exact proof. Reporting that the docs under-specify the numbers, instead of quietly reading the code and calling it documentation-derived, was right.

FIRST: your report says plan-gate green at b77e74e. That is r2.44. r2.45 (33b74a4) and now r2.46 (87bfbec) are both signed. Pick up 87bfbec by content and re-verify before building.

FOUR CHANGES, all marked in the clause:
1. SPEC SENTENCE made exact. I read guards/decoding.py::_decode_text: a file that BEGINS with a UTF-16 BOM and fails UTF-16 returns None immediately, with NO fallback to UTF-8 or latin-1. Your 'UTF-16 if BOM; failing that as UTF-8' reads as a fallback. The signed sentence says 'there is no other route'. Your differential passed anyway because the corpus never contained a BOM followed by invalid UTF-16, which is point 2.
2. The CORPUS must include the boundary shapes: empty file; BOM plus invalid UTF-16 (odd length, lone surrogate); UTF-8-BOM; latin-1 exactly at and just below the nine-tenths ratio; a NUL in otherwise valid UTF-8; and the 256 MiB ceiling exactly at and one byte over, via sparse files (truncate), so it stays cheap. Random generation will not reach these, and they are where a wrong sentence hides.
3. COUNTS: the draft said 6,016 strings, but the clause text said '451 of 3,009'. The clause records the numbers from the IN-TREE run. Send them with the gate.
4. Update _decode_text's docstring to state the 0.9 ratio and cite _MAX_SCAN_BYTES, so the documentation owns the numbers the reference depends on.

GO: implement r2.46 in-tree, then run the gate over the WHOLE range (--base f78854d), with four reviewers in gate-created scratch worktrees, the content block, the scorer on a sanitised set, the full bracket (3b/3c/3d), the extended 0..7 token tier recorded in the receipt, and the suite run by hand in Step 8. Then E-23 on the same design, then E-24 (which must update this sentence and the reference in the same commit).
