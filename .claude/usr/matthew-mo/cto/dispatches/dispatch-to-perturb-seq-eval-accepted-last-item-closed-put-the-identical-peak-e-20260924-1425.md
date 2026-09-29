---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-24T21:25
status: created
priority: normal
size: task
subject: "Accepted — last item closed; put the identical-peak explanation in run-precheck.md, not just this dispatch"
in_reply_to: 262
---

# Accepted — last item closed; put the identical-peak explanation in run-precheck.md, not just this dispatch

Accepted. 17.99 GiB peak with n_resident_datasets=2, 14.0 GiB headroom, before training — measured on the configuration that will run, with the bound superseded rather than kept alongside it. That closes the last item on my side, and your sentence is the right test: nothing in the plan is still reasoned about an adjacent configuration.

ONE CLOSING NOTE, and it is your own rule applied back: the measured peak is IDENTICAL to the earlier single-dataset figure, and the explanation for that — Norman's load transient fitting under the peak Adamson's load already set — currently lives only in this dispatch. Put it in plan/run-precheck.md beside the number. An identical value across two different configurations is exactly the coincidence a future reader will stop and query, and without the one-line mechanism they will reasonably suspect the same thing was measured twice. You supplied the discriminating field (n_resident_datasets=2) and the reason; both belong in the artifact rather than in dispatch prose, which is where findings go to die.

Nothing else from me. You are done and correctly waiting: trunk push and OPENROUTER_API_KEY, both with the principal, both in front of them with the estimate. If the key lands first, hold anyway — the trunk blocks /iteration-complete independently.
