---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-10-30T20:11
status: created
priority: normal
size: task
subject: "New window armed (19:05-04:10, same authorizations). While your claim-bearing track waits on the principal, one rank-1 task that touches no paper or claim: draft docs/usage/lung-on-chipsim.md — what a user can now DO with chipsim. docs-ticket-align scores the workstream ALIGNED 0 because docs/usage has never existed here."
in_reply_to: null
---

# New window armed (19:05-04:10, same authorizations). While your claim-bearing track waits on the principal, one rank-1 task that touches no paper or claim: draft docs/usage/lung-on-chipsim.md — what a user can now DO with chipsim. docs-ticket-align scores the workstream ALIGNED 0 because docs/usage has never existed here.

Window 2 armed 19:05, ends 04:10, with authorizations unchanged: you draft with provenance, the principal ratifies, and code lands via gated PRs. Your claim-bearing work still waits on the principal (sections 1 and 2, the number collisions, OCT1).

One unblocked rank-1 task: write docs/usage/lung-on-chipsim.md, describing what a user can now DO with chipsim. Cover the commands they can run, the inputs each needs, and what each produces; leave out how it works internally. Describe the CLI as it exists at your current HEAD, and verify every command you list by running its --help, rather than recalling it.

Constraints: no biological number and no identifier paired with a substance (it is a public surface). Do not describe results or findings; this is a how-to-use doc, not the paper. Say what is NOT yet usable (for example, steps blocked behind the M1 inputs) rather than leaving it implied.

docs-ticket-align scores the workstream ALIGNED 0 for two reasons, the missing usage doc and no recorded ticket pointer. The ticket-pointer half is filed as a Linear issue for a convention decision; it is not yours. Land the doc through your normal gate. It is docs, not code, but goes on your branch.
