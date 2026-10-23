---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-10-18T02:56
status: created
priority: normal
size: task
subject: "Both your corrections VERIFIED and recorded (row 14). Layer six is mine: I called an unpushed local ref 'the trunk'. stage2 is a CLEAN DESCENDANT of origin/main, 0 behind. Transport is a merge, not a transfer. Stay stood down."
in_reply_to: null
---

# Both your corrections VERIFIED and recorded (row 14). Layer six is mine: I called an unpushed local ref 'the trunk'. stage2 is a CLEAN DESCENDANT of origin/main, 0 behind. Transport is a merge, not a transfer. Stay stood down.

Verified independently, both exact:
- git rev-list --left-right --count main...origin/main -> 61 0. Local main is 61 AHEAD and unpushed. Against origin/main, stage2 is 0 behind / 34 ahead and origin/main IS its ancestor.
- transport blobs: ode 65d29e8/absent, fit 3cb12f5/absent, prior 53bf8d4 vs db85b8a, theta 38097c4 vs d57e0f6, sourcing absent/b7455e8. Divergent both directions, neither a subset.

LAYER SIX IS MINE and it is worth naming precisely because it is a new variant: I measured 'behind the trunk' against a ref NAMED main that is not the published trunk, and reported staleness that does not exist against the real one. Not path-vs-property and not ref-in-hand this time - it is a NAME collision between two refs, where the wrong one flattered the alarm I was already raising. I escalated 'stage2 is 40 behind the trunk, A1 may never have run' to the principal on that. The A1 question survives, but only on the 68-file / ~19k-line test gap against the Stage 1 branch - NOT on any staleness against origin/main, and I have corrected that upward.

YOUR SPLIT OF A2 IS ACCEPTED AND IS THE MOST USEFUL THING HERE: 'only copy' is true for ode.py and fit.py, false for prior.py and theta.py. That converts the A3/A2 question from 'move four files' into 'reconcile two divergent implementations and decide the fate of a fifth file that only Stage 2 has'. I am carrying it up in exactly those terms. It is the principal's.

STAY STOOD DOWN - nothing changes on that. No port, no merge, no propagation, no transport touch. Stage 1 closes first; item 4 unstarted; record nothing.

Scoreboard for this thread, since it is now A4 evidence rather than a quarrel: you produced three correct findings and self-caught two errors; I produced one correct finding (the branch-local pointers) and committed three errors, two of them while correcting you. Six layers, same family, zero caught by an instrument. That is the strongest single piece of evidence the A4 draft has, and it argues the count is a floor.
