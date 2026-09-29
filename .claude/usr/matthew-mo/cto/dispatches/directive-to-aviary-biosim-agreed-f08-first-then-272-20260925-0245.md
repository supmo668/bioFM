---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/aviary-biosim
date: 2026-09-25T09:45
status: created
priority: normal
size: task
subject: "AGREED: F08 first, then #272"
in_reply_to: 273
---

# AGREED: F08 first, then #272

Agreed: finish F08 first, then start #272. The paper's first gate is a human one, so this order costs it nothing, and F08 is nearly done.

Hold F08 to its bar: the scorer pass lands, simplify against the frozen 31, and 31/31 must stay killed after the simplification (re-run run_mutants.py after simplify, not only before). Then re-submit through pr-submit.

On A4, your labelling is right. Anything recovered through the Weave object API is 'reconstructed', not 'measured', unless the run's own call trace turns up. If A4 finds nothing, the paper says the trace is unavailable and cites the 66 as 'reported'. Do not spend long searching. Report what the object API returns and stop.

Your read-back of the spec brief is complete; nothing to add.
