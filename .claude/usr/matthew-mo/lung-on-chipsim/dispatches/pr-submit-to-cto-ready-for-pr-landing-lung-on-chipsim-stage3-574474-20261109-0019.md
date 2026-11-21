---
type: pr-submit
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-11-09T00:19
status: created
priority: normal
size: task
subject: "Ready for PR landing: lung-on-chipsim-stage3 @ 5744743d — transport collision closed + the S6 writer-guard hole it exposed (17/17 findings fixed; precondition 4 tool-blocked on the branch-name defect)"
in_reply_to: null
---

# Ready for PR landing: lung-on-chipsim-stage3 @ 5744743d — transport collision closed + the S6 writer-guard hole it exposed (17/17 findings fixed; precondition 4 tool-blocked on the branch-name defect)

Agent: biofm/matthew-mo/lung-on-chipsim
Branch: lung-on-chipsim
SHA: 5744743d
PUSH TARGET: origin/lung-on-chipsim-stage3 = 5744743d (NOT origin/lung-on-chipsim — see PRECONDITION 4)
diff-hash: 3e56ccd (base origin/main, is_submodule=false, file_count 14)
Receipt: workstreams/lung-on-chipsim/qgr/bioFM-matthew-mo-lung-on-chipsim-lung-on-chipsim-lung-on-chipsim-qgr-pr-prep-20261109-0010-3e56ccd.md
draft: false
migrations_pending: none (migration-delta empty)

PRECONDITION 4 — READ THIS BEFORE YOU LAND. `receipt-verify --require-pushed` EXITS 1:
  "BLOCKED: origin/lung-on-chipsim (c04e701) and HEAD (5744743) have DIVERGED"
That is the known branch-name defect, not a real divergence. The tool resolves the push target by
BRANCH NAME, so it compared against origin/lung-on-chipsim — the FROZEN Stage-1 archive at
c04e7019, which the handoff marks do-not-push. My actual push target is stage3.
I am NOT claiming precondition 4 passed. I am claiming the underlying property holds, verified
independently and by the only check that settles it:
  git merge-base --is-ancestor HEAD origin/lung-on-chipsim-stage3  -> TRUE
  origin/lung-on-chipsim-stage3 = 5744743d = local HEAD
  origin/lung-on-chipsim        = c04e7019, untouched
PRECONDITION 5 passes on its own: `receipt-verify` without --require-pushed exits 0, Hash E
3e56ccd, and `diff-hash --base origin/main` independently returns 3e56ccd. Receipt matches HEAD.

RELATED TOOL DEFECT, filed at 5640d7b1 and relevant to YOUR landing step: tools/git-push printed
"Everything up-to-date" and then "✓ Pushed" while four commits stayed local. The branch argument
resolves to a LOCAL ref and the ✓ is unconditional and names no SHA. Verify any push with
`git merge-base --is-ancestor`, never the ✓. Also: `git-push` with NO argument defaults to the
current branch and would aim at origin/lung-on-chipsim, the frozen archive.

SCOPE — two things, one of which you should look at first.

1. THE AUTHORIZED FIX (dispatch 909, principal authorized all three steps in-session 2026-11-08).
   A cross-module collision in chipsim.transport: ENTRY_KEYS and SCAFFOLD_RELPATH were public in
   both theta.py and prior.py with different values, and pipeline.py imported SCAFFOLD_RELPATH and
   write_scaffold from BOTH under one name in two function bodies. Correct only because of that
   placement. Now: _ENTRY_KEYS private; THETA_/PRIOR_SCAFFOLD_RELPATH distinct;
   write_theta_scaffold / write_prior_scaffold and theta_/prior_scaffold_text distinct; and two new
   guards — a cross-file public-constant rule and a one-name-from-two-modules import rule.

2. A LIVE INTEGRITY HOLE THE GATE EXPOSED, pre-existing, NOT caused by this change, and the reason
   the scope grew. prior.write_scaffold had NO S6 forbidden-path refusal while theta's had one, so
   `chipsim transport-prior-scaffold --out configs/theta_priors.yaml` CREATED the human-owned file
   whose ABSENCE is the mechanical enforcement of "no coding agent writes a biological number".
   I reproduced it myself: returned normally, 766 bytes, exit 0; prior.py never referenced
   S6_FORBIDDEN_RELPATHS. Both writers now share one guard (chipsim/transport/_s6.py), the compare
   is case-folded (configs/Theta_Priors.yaml evaded it on APFS), and theta's path.resolve() symlink
   handling is preserved verbatim. A parallel find: each writer judged the OTHER's filled file blank
   and overwrote it — fixed both directions.

GATE: 17 findings from 4 reviewers plus my own review. ALL 17 FIXED, 0 deferred, 0 rejected.
12 of the 17 were defects in my OWN new guard — a shallow AST walk where the sibling walks deep,
textual comparison standing in for value comparison, and the decision logic inline where it could
never be probed. Fix commits 8b25b7e5 (code) and d0eabeb0 (tests); boundary 5744743d.
PROVED NON-VACUOUS rather than asserted, because I shipped two unsound instruments earlier in this
session: four plants, each red then restored byte-identically — the original collision, one nested
in try:, one hidden behind identical source text over different private helpers, and the
one-name-from-two-modules shape. The middle two previously PASSED. The CLI tests were planted both
ways, confirming the content and path assertions are each necessary.
Suite 929 passed / 4 skipped / 0 failed (911 before, +18 tests). ruff format + check clean.
ty 25 diagnostics on chipsim, baseline unchanged.

TWO DISCLOSURES IN THE RECEIPT, stated rather than reconciled away:
- Hash A was taken against c2094fd4 BEFORE the origin/main merge; Hash E is against origin/main.
  The bases differ by that merge.
- tree-bracket reported TREE_CHANGED. The only moved paths were two hook-written
  .aiadlc/instincts counters, outside the gated artifact (A and E are committed diffs).

CARRIED FORWARD, disclosed not hidden: LIVE_PROVENANCE drift in tests/ (one file spells it
RAW_DIR / 'provenance.yaml', another PROJECT_ROOT / 'data' / 'raw' / 'drugbank' /
'provenance.yaml'). Pre-existing test drift outside this change's subject; recorded in the guard's
limits section instead of being hidden behind the old "noisy" claim.
NOT PRE-DECIDED: nothing else about those two modules' public surface was touched.

ALSO ON THIS BRANCH (context + ledger, no code): approvals rows 111-115 and the reconciliation of
your trunk rows 103-110, the row 115 supersession of row 107's "26 -> 24" clause, the row 108
disclosure applied to the T18 candidate list, and two plugin-feedback entries.

CTO ACTIONS:
1. Land stage3 @ 5744743d. Do NOT land origin/lung-on-chipsim (c04e7019, frozen archive).
2. Treat precondition 4 as satisfied on the ancestry evidence above, or re-check it yourself with
   `git merge-base --is-ancestor HEAD origin/lung-on-chipsim-stage3`. Do not take git-push's ✓.
3. Note row 115: the roster stays at 26 and the strike is OFF. If any landing step was going to
   act on row 107's "26 -> 24", it should not.
