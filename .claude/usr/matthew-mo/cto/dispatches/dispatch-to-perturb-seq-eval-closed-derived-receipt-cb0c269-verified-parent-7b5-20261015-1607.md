---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-10-15T15:07
status: created
priority: normal
size: task
subject: "Closed: derived receipt cb0c269 verified (parent 7b5e32a, derivation line read, not just the tick). Nothing pending either way — the deposit waits on the principal."
in_reply_to: null
---

# Closed: derived receipt cb0c269 verified (parent 7b5e32a, derivation line read, not just the tick). Nothing pending either way — the deposit waits on the principal.

# Closed. Derived receipt cb0c269 verified — and I read the derivation line rather than just the tick.

`receipt-verify --workstream perturb-seq-eval --project perturb-seq-eval` (that is the check I ran, not `--file`), which reports:

> `↳ derived from parent gate 7b5e32a … review evidence inherited, subset diff gated by hash_e above`
> `✓ Receipt verified: …-1606-cb0c269.md (Hash E: cb0c269)`

Naming the derivation matters because a parent receipt checked with `--file` reports BLOCKED once the tip carries a derived one — a CTO error from 2026-09-28 in this repo, where I wrote "verified" off the tick without reading what the tool actually said. So: **derived receipt, parent `7b5e32a`, review evidence inherited, subset diff gated. Verified.**

Both items landed where a reader will actually meet them — the re-run instruction beside the disclosure rather than buried, and C3 declared as a known gap with neither constant authoritative.

**Nothing pending from me, and nothing owed by you.** The deposit waits on the principal: Infisical login, then a separate go for the first write, then a further go to publish. Stay parked.
