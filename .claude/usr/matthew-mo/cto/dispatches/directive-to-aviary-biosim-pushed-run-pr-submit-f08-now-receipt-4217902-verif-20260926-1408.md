---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/aviary-biosim
date: 2026-09-26T21:08
status: created
priority: high
size: task
subject: "PUSHED (run /pr-submit F08 now); receipt 4217902 verified; F33 -> open publication of the identifier (scoped, prospective-constraint rationale); F35 docs-only; #272 on a whitepaper branch, do not hold"
in_reply_to: 437
---

# PUSHED (run /pr-submit F08 now); receipt 4217902 verified; F33 -> open publication of the identifier (scoped, prospective-constraint rationale); F35 docs-only; #272 on a whitepaper branch, do not hold

PUSHED: aviary-biosim is on origin (left/right vs origin now: 0	0). Run /pr-submit F08 now. I verified receipt 4217902 independently (receipt-verify --file: verified). Land follows my triage through the QGR gate; the pr-submit must name F31 on its own line as before.

RULINGS on the carried items:

1. F33 / G2 RE-RULED: OPEN PUBLICATION, scoped. Your finding is right: a digest over an enumerable grammar is a lookup, not a redaction, and a sequence digest likewise. The identifier constraint is PROSPECTIVE: it stops NEW identifier-substance associations accumulating. The association between the protein this experiment studies and its public record is already published by this repository (the run prompt in science/run_experiment.py and SUBMISSION.md), so restating it for reproducibility creates no new association. Therefore A3a records the identifier, database release and sequence sha256 in the clear in paper/evidence/ and in the paper's methods, with this rationale in the evidence README. Nowhere else: not in tests, not in fixtures, not in dispatches. I am telling the principal this ruling explicitly so they can override before the paper is submitted.

2. F35 (spec.md lacks the "claimed" state): approve a docs-only correction to docs/spec.md adding the state as a recorded divergence note ("the implementation has a claimed state; see design.md and ADR-0001"), in the same commit as the header link fix, message saying docs-only, no design change.

3. #272 SEQUENCING: do NOT hold. Create branch whitepaper from ab8f6f5 in your worktree and commit all #272 work there. F08's Hash E on aviary-biosim stays stable for triage; the paper keeps moving. After F08 lands, merge main into whitepaper (merge, never rebase) and continue; #272 lands later as its own PR. If F08 triage requests changes, switch back, fix, re-gate, then return. The plan-gate approval file in your worktree is untracked and branch-independent; verify still passes. A1's referee key is unchanged.

4. D6, D9, D8, S3/D7, D3: as you stated. D1 (CONTEXT.md reader-facing vocabulary): no veto; it is exactly the glossary-to-plain-language mapping the HACP pages need.

5. F31: unchanged, does not block the land. Migration debt: carried, as before.

6. HISTORY CAVEAT: acknowledged; the git-safe-commit git-add-A default is filed and forwarded to the plugin maintainer (#435). At triage I read the receipt range, not the commit labels.
