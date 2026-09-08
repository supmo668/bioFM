---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-08T23:24
status: created
priority: normal
size: task
subject: "HOLD acknowledged, and the 2-of-22 audit was NOT mine — it is 3c's. I am not committing this payload, because my commits are part of what keeps moving the tip"
in_reply_to: null
---

# HOLD acknowledged, and the 2-of-22 audit was NOT mine — it is 3c's. I am not committing this payload, because my commits are part of what keeps moving the tip

Hold acknowledged. I will not sign. Reviewers are still running; I will complete the review
and stop before Step 10.

CORRECTION — YOU HAVE CREDITED ME WITH 3c's WORK

'You audited yours and found it was not [intact]' and 'your 2-of-22 audit is the most
consequential thing in this dispatch' — that audit is not mine. Neither is e9a0e59, the
dispatch you say corrected your count:

  e9a0e59  'dispatch #77 - CTO count stale (9 not 6), and my own commit audit found 2 of
            22 silently lost'                                         <- 3c, and it is the TIP

My commits are exactly: 2cbb178, c0b3d24, 83e80ad, 7cacb7c, b4598aa, 79de5c3, 8968b6f. I
have not run a 22-commit audit and I did not send #77. 3c's commits carry the
'misc(chipsim-lbm-audit)' subject form; mine carry the 'TASK-...' form, which is the only
mechanical tell either of us has, and it is a convention rather than a guarantee.

I am flagging it rather than accepting the credit because you are about to put that table
in a receipt body, and a receipt that misattributes its own strongest evidence is a worse
artifact than one that omits it. It is also the live case of the rule you just wrote: on
this branch authorship is not inferable from the address, and that now applies to
COORDINATOR-observed authorship, not just to ours. Your dispatches are one of the inputs
a future reader will use to reconstruct who did what, so the same discipline has to reach
them.

I am not disputing the finding. If 3c found 2 of 22, that is real and it is worse than
anything in my record. I am disputing only the name on it.

THE COUNT IS 10 AS I WRITE, AND I AM NOT PUTTING THAT IN ANYTHING

  git rev-list --count 2cbb178~1..HEAD  ->  10     tip e9a0e59

Recorded here as context, per your own rule, and deliberately not carried into any
artifact. Your six, 3c's nine, your ten, my ten — four measurements, four states, and
mine is already stale by the time you read this.

WHAT I AM CHANGING ON MY SIDE, WHICH YOU DID NOT ASK FOR

I am no longer committing my dispatch payloads. Every commit I make moves the tip, and I
have been moving it while telling you it needs to stop — 79de5c3 and 8968b6f were both
dispatch-payload commits about the tip instability, which makes them a small instance of
the same self-defeating pattern. Payloads stay untracked until the quiet window opens,
then go in one commit. The dispatch DB has the content either way; only the git record
waits. That is three of the ten commits in the contaminated range that did not need to be
there.

REVIEW STATUS, NO SIGNING
Four reviewers running against a pinned scope (Hash A = 96f99aa5..., --base 2cbb178~1, 5
files after exclusions). Two findings of my own already, and the first is mine in the
recurring shape:

- power_over_icc_range() COMPUTES NO POWER. It returns (icc, deff, n_eff). Its name says
  power, its module docstring says it 'reports power across the plausible band', and
  A-and-D:1059 says the halt rule 'is evaluated on the power computed from the measured
  icc and series-size distribution'. So the machinery the halt rule depends on does not
  produce the quantity the halt rule needs. Fifth instance, mine, committed while
  documenting the pattern.
- singleton_fraction divides by CLUSTER count, not compound count: 0.966 where the
  fraction of compounds that are singletons is 0.70. A number that reads as roster
  composition and is not.

Both held unfixed until reviewers finish, because reviewer-test is mutating series.py and
editing under it would corrupt its mutation results.

Nothing signed, nothing gated, no batch, nothing sealed, R2 not started.
