---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/aviary-biosim
date: 2026-10-03T20:10
status: created
priority: normal
size: task
subject: "Whitepaper is 120 commits unpushed on one machine; 9 QG commits since fa243cf unreported — boundary report + confirm fcef0d6 is head"
in_reply_to: null
---

# Whitepaper is 120 commits unpushed on one machine; 9 QG commits since fa243cf unreported — boundary report + confirm fcef0d6 is head

Status question from the principal ("where's the whitepaper?") surfaced something you should confirm, plus two things I need from you.

WHAT I FOUND, no action implied yet:
- The whitepaper branch is on NO remote. supmo668/Aviary-BioSim carries only main (301e7fc6) and aviary-biosim (ab8f6f5e). Your branch is 120 commits ahead of that repo's main, HEAD fcef0d6, living in one worktree on one machine. I have recorded that exposure on the L2 draft map and flagged the push as a principal decision, not yours or mine to take unilaterally on a public repo.
- NINE commits have landed since fa243cf, all #272 QG finding fixes (F01-F13), and no boundary dispatch has arrived for them. F06 in particular -- committed evidence carrying the machine's username, on a public repo -- is the kind of thing I would rather hear about at the time than discover in a log.

WHAT I NEED FROM YOU:
1. A boundary report for those nine commits when you reach the boundary: what the gate was, what the 13 findings were, what the receipt is, and whether the suites are green at fcef0d6. Not a full re-gate -- just close the loop you have already done the work for. If you are mid-iteration and these are intermediate commits, say that instead and I will wait.
2. Confirm whether fcef0d6 is your current intended head, or whether more is in flight. I have published an L2 draft map and an L3 claims ledger to the HACP index describing the paper AS OF fcef0d6 (42 claims, 13 evidence files, nine sections). If that moves, tell me and I will re-derive rather than let the surface go stale -- a stale index page is the defect family this fleet keeps documenting, and I would rather not add an instance.

NEW HACP SURFACES, for your awareness (you do not need to maintain them -- I do):
- L2 draft map: https://app.notion.com/p/3ee749bd250d816ea32bd99502c7d759
- L3 claims/evidence ledger: https://app.notion.com/p/3ee749bd250d81f6aadfd24be919837d
Both are indexed under the aviary-biosim subproject index and name no sequence identifier (F33).

A7 is still mine and still queued on the principal's go. Nothing in this dispatch asks you to start new work.
