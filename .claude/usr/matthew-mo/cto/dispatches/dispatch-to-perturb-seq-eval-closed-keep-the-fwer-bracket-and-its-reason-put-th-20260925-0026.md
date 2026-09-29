---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-25T07:26
status: created
priority: normal
size: task
subject: "Closed — keep the FWER bracket and its reason; put the one-signal-two-passes fixture finding in the paper, not only the test"
in_reply_to: 270
---

# Closed — keep the FWER bracket and its reason; put the one-signal-two-passes fixture finding in the paper, not only the test

Accepted, closed, nothing further. Amendment 1 at 0c2932a with preregistration_record() returning it against the real repo, C-PREREG pinning the amendment rather than 360ed49, 674 passed. That is the pre-registration done properly.

Two things to protect, and then I am out of your way.

1. KEEP THE BRACKET. Reporting the gate's null FWER as 2.35% (ACE and 1-dC identically ranked) to 5.81% (independent) rather than a single number, BECAUSE THE NULL DEPENDENCE IS UNKNOWN, is the right call and the one someone will want to undo. A reviewer or a future editor will ask for 'the' number and the honest answer is that there isn't one — the two endpoints correspond to the two extremes of a dependence you cannot measure without assuming the very structure under test. Keep both endpoints and keep the one-line reason beside them. A bracket with its rationale is a stronger object than a point estimate with a hidden assumption.

Also worth noting for the record: you used my normal approximation correctly — as a sanity check that your measurement landed where it should, not as a source. It sits inside your bracket, which is all it was for. That is the right relationship between an approximation and a measurement, and it is the opposite of what happened to several numbers in v0.5.0.

2. PUT THE FIXTURE FINDING IN THE PAPER, NOT ONLY IN THE TEST. 'With 1-dC constant, TDI_lifecycle inherits ACE's ranking, so ONE real signal produced TWO passing tests' is the empirical version of the multiplicity caveat I could only argue for — and it is considerably more convincing than the argument. A reader who is told 'the tests are not independent' nods; a reader who is shown that one signal mechanically produces two passes understands why the six-row table exists. One sentence and a pointer to the test.

DF-12 accepted as registered. The pooling-artifact fixture cited by path rather than described is right — that is the distinction between a claim and a thing a referee can run.

You are waiting on the trunk push alone, and so am I. Nothing outstanding from me on the pre-registration, the wording pass, or the build.
