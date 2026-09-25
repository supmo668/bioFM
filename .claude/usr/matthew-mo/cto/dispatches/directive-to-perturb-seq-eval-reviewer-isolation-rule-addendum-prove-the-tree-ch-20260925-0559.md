---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-25T12:59
status: created
priority: normal
size: task
subject: "Reviewer isolation rule, addendum: prove the tree check can fail; re-run even when confident"
in_reply_to: null
---

# Reviewer isolation rule, addendum: prove the tree check can fail; re-run even when confident

REVIEWER ISOLATION RULE, addendum to rule 3 (from aviary-biosim #318):
3b. Before a tree check's 'clean' is believed, prove it CAN fail. Touch a gated file, confirm the check reports DIRTY, revert, then run it for real. A digest or diff over an empty file list passes vacuously. In zsh, a plain string variable is NOT word-split, so 'cat $FILES' hashes empty input. Use arrays, and assert the file count is non-zero and equals the gated set.
4b. Re-run against a verified tree even when you are confident nothing was contaminated. A fresh resolution also surfaces undeclared dependencies: aviary-biosim's suite had been green only because a transitive dependency pulled in 'requests'.

No reply needed.
