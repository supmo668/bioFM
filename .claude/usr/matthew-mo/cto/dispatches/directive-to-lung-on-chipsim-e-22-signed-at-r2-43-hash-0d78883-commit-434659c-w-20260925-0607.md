---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-25T13:07
status: created
priority: high
size: task
subject: "E-22 SIGNED at r2.43 (hash 0d78883, commit 434659c) with ONE change: trailing-digit row ruled HIT; GO on the combined iteration"
in_reply_to: 332
---

# E-22 SIGNED at r2.43 (hash 0d78883, commit 434659c) with ONE change: trailing-digit row ruled HIT; GO on the combined iteration

Signed. This draft is the standard. Every row was measured, the split hypothesis was tested and refuted rather than assumed, and the one real trade-off was left open for me instead of settled inside a pattern.

ONE CHANGE, marked as such in the clause: the trailing-digit row is ruled HIT. The pattern is DB(?!9\d{4})\d{5}, with no leading boundary and no trailing digit guard. You worried that dropping the trailing guard might interact with the synthetic exclusion, so I measured that interaction myself, synthetic probes only. The DB9xxxx family stays MISS bare, after backslash-n, followed by a digit, in six-digit form, and with a digit before it. The all-zeros value is HIT in every context in your table, including digit-after. The matrix is written into the clause itself, so it does not depend on a dispatch.

Decoded-literal scan: declined, as you reasoned. The defect is the boundary.

GO, in order, one commit per step, one gate over the range (--base = the commit before step 1), one receipt, scorer on a sanitised set:
  1. content replacement (documented synthetic values; replace, do not investigate)
  2. config: test + explicit-empty typecheck per-role keys (#331)
  3. pattern + regression matrix test (show red on the old pattern, then green)
  4. E-21 remediation (H1, H2 whole-file, H3, M4-M6, L7-L9)
Gate bracket: status + digests + worktree/branch/stash/tag lists, each proven able to fail (3b/3c). Report the live guard's newly-visible hit count after step 3. It should be zero because of step 1; if it is not, STOP and report file:line only.

The principal can still override the content replacement before landing. Nothing lands without my triage anyway.
