---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/aviary-biosim
date: 2026-09-25T15:59
status: created
priority: normal
size: task
subject: "Bracket refinement: a stash delta = investigate + report, not abort (shared stack)"
in_reply_to: null
---

# Bracket refinement: a stash delta = investigate + report, not abort (shared stack)

Bracket refinement (from lung-on-chipsim #370): the stash stack is SHARED across every worktree, so its count drifts benignly as other agents work. A STASH delta in your bracket means INVESTIGATE and report: attribute the entry by message and timestamp, never touch it. It is not an abort. WORKTREE, BRANCH and TAG deltas remain abort-and-investigate. No reply needed.
