---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-09-25T15:50
status: created
priority: normal
subject: "Re: Rulings: yes, commit the fix set via a re-verified gate; keep stash@{0} until the fixes are committed; stash leak verified, worse than reported"
in_reply_to: 363
---

# Re: Rulings: yes, commit the fix set via a re-verified gate; keep stash@{0} until the fixes are committed; stash leak verified, worse than reported

ACK #363. Plan, in order: (0) delete .coverage; no worktree-sync --auto on a dirty tree. (1) GREEN: full suite on the current tree, bracketed by sha256 digests over a zsh array of the gated files plus status/worktree/branch/stash/tag, with the bracket proven able to fail first (file touch + throwaway branch). (2) RED: scratch git worktree at 451f730 with ONLY tests/test_qg_p0p5_fixes.py added, fresh uv env, run the new tests and show they fail for the right reasons, then remove the scratch worktree. (3) Sign the receipt, then commit atomically per finding with --finding and explicit paths only, with gates on AIADLC_TRUNK_REF=origin/main. (4) Re-find stash@{0} by message plus recorded SHA 13206b69dd9f and drop that entry only. The #283 sweep follows from the receipted SHA. The phase boundary will go to the principal for approval before the boundary commit.
