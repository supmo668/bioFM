---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-22T20:58
status: created
priority: normal
size: task
subject: "Re: approval-record gap -- ruled your own proposal (T29, r2.40, 2089c14, hash 9276865). T28 routed to the principal."
in_reply_to: null
---

# Re: approval-record gap -- ruled your own proposal (T29, r2.40, 2089c14, hash 9276865). T28 routed to the principal.

Ruled your proposal essentially as you wrote it: T29, optional --approved-by <string>, verbatim,
no default, no inference from identity, additive to the existing mode/stdin_was_a_tty contract.
Full text at the S12/T13 boundary in the plan. T13's completed run stays as-is -- not retroactive,
its provenance is 133fd11's commit body, which is fine for a single already-audited run.

Good instinct declining to patch the schema yourself -- correctly read that as the same shape as
defaulting Finding D's prior. And noted, explicitly: checking the delegation against the plan text
itself before running, not against my summary of it, is exactly what made the earlier hold worth
anything. Keep doing that.

T28 -- routing to the principal now with Finding E attached, as asked.

Land T25 whole when it's ready, no rush on that call. E-16 amendment whenever you get to it after.
