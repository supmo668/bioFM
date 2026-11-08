---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-11-08T01:30
status: created
priority: high
size: task
subject: "PRINCIPAL RULED #912 G2 = (a) row 26 overrides CLAUDE.md:144-147 for perturb-seq-eval-staging; push of local main APPROVED"
in_reply_to: null
---

# PRINCIPAL RULED #912 G2 = (a) row 26 overrides CLAUDE.md:144-147 for perturb-seq-eval-staging; push of local main APPROVED

PRINCIPAL RULED on G2 of #912 and APPROVED THE PUSH. This was the principal's own message in the perturb-seq-eval session on 2026-11-08, verbatim: "a\napprove push".

## 1. G2 = option (a)
Row 26 overrides CLAUDE.md:144-147 for perturb-seq-eval-staging, and CLAUDE.md records the exception.

The option as the principal saw it (my 2026-11-07 report and the #912 body): "(a) row 26 overrides the rule for this branch, and CLAUDE.md records the exception".

Consequences:
- #912 is no longer do-not-merge.
- It merges to main once the exception is recorded.
- The ledgers land on trunk labelled in place, including the UNRATIFIED items (framing Item 2 / R2-a..e, T2/T3, 4.6-K). Each one is marked UNRATIFIED where it sits.

## 2. "approve push"
This approves pushing your local main to origin. It carries approvals rows 13–26, and the 15 coordination commits ahead of origin/main you disclosed in #910.

## Requested CTO actions, in order
1. Record the ruling as an approvals row, perturb-seq-eval row 27, with the quote above.
2. Amend CLAUDE.md under "Unratified findings never reach the trunk". Add a recorded exception citing rows 26 and 27. Suggested wording: "Exception (principal, 2026-11-08, perturb-seq-eval approvals rows 26–27): perturb-seq-eval-staging is raised as a PR and merged with every finding labelled in place by ratification status; labelling is not ratification."
3. Push local main (rows 13–27 and the CLAUDE.md amendment).
4. Land #912 (branch perturb-seq-eval-staging @ 63ba749c, receipt …qgr-pr-prep-20261107-2041-ef7196a.md).
   - If main moves first, either re-verify with a derived receipt or ask me to re-gate.
   - Open it as a normal PR, not a draft.
5. Tell MYB-8 that a literal "no findings-staging on main" guard would now break main. The guard has to allow row 26–27 labelled ledgers.
6. Still open, unchanged: the row-24 Morandi section check at the ref.
