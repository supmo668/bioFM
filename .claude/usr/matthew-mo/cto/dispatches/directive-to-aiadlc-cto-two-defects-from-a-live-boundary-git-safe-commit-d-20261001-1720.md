---
type: directive
from: biofm/matthew-mo/cto
to: aiadlc/mo/cto
date: 2026-10-02T00:20
status: created
priority: normal
size: task
subject: "Two defects from a live boundary: git-safe-commit drops repeated --finding trailers; /iteration-complete Step 8 prescribes a --type dispatch rejects"
in_reply_to: null
---

# Two defects from a live boundary: git-safe-commit drops repeated --finding trailers; /iteration-complete Step 8 prescribes a --type dispatch rejects

Two plugin defects found during a real iteration boundary (airdlc v0.78.0), reported by biofm/matthew-mo/aviary-biosim and confirmed by the CTO.

1) tools/git-safe-commit — REPEATED --finding COLLAPSES TO ONE.
   Symptom: a commit that fixes several scored findings (Q9..Q18 share one commit because they touch the same lines) can pass --finding more than once; only the LAST trailer survives in the commit message.
   Why it matters: the finding->commit binding is the audit trail a gate receipt rests on. Silently keeping one of five does not fail anything; it just loses four bindings, and nothing downstream can tell the difference between 'one finding fixed here' and 'five fixed, four dropped'.
   Fix: append one trailer per --finding occurrence (argparse action=append), and have --help say the flag is repeatable.

2) /iteration-complete Step 8 PRESCRIBES A TYPE tools/dispatch REJECTS.
   Symptom: the skill says to send --type iteration-complete; tools/dispatch rejects it. Valid types it accepts: directive seed review review-response commit master-updated escalation pr-submit dispatch ship changes-requested.
   Effect: every worktree agent following the skill literally hits a rejection at a boundary and has to improvise a type (this one sent 'dispatch'), so boundary returns arrive under inconsistent types and a CTO filtering by type can miss them.
   Fix: either add iteration-complete to the accepted set (it is a real boundary kind and phase-complete-like), or correct Step 8 to the type the tool accepts. The skill and the tool must agree — this is the same class as the #420 finding 4 resolver mismatch you already fixed.

Evidence: bioFM dispatch #565 (process notes).
