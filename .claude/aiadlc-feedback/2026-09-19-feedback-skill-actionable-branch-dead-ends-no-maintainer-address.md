---
type: plugin-feedback
target: aiadlc plugin — skills/feedback, tools/config, /cto-init
plugin_version: 0.59.0
reporter: bioFM/matthew-mo/cto
date: 2026-09-19
scope: plugin / operating-system behavior — NOT repo/app work
status: open
---

# 🟠 `/feedback`'s "actionable" branch dead-ends: it says dispatch to a maintainer address that nothing configures

**Symptom.** `/feedback` routes on `plugin.source_path`:

- **Set** (an editable checkout) → *"the feedback is actionable, not just logged. **Dispatch** it"*,
  via `dispatch create --to <maintainer-addr> …`
- **Empty** → fall back to logging / offering an issue.

`plugin.source_path` is set here (`/Users/mo/github/aiadlc`), so the skill takes the actionable
branch — and then there is nowhere to send it. **`<maintainer-addr>` is a placeholder the skill never
resolves and nothing in the framework populates.**

**Measured this session:**

| check | result |
|---|---|
| `config get plugin.source_path` | `/Users/mo/github/aiadlc` (set) |
| maintainer address in this repo's dispatch DB | none — only `cto`, `lung-on-chipsim`, `aviary-biosim` |
| `agency.yaml` in the plugin source repo | does not exist |
| `collaboration list` | `No collaboration repos configured in agency.yaml` |

**Consequence.** Three feedback items were filed this session and **none could be dispatched**. Each
was logged with a hand-written routing note explaining why — which is the operator doing by hand,
every time, what the skill claims to automate. The failure is quiet: the skill reads as though the
loop is closed, and the durable record silently becomes the only outcome.

It also lands precisely on the defect filed alongside it — *nothing tracks a precondition one party
owes another*. Here the framework owes itself a delivery address and has no surface that notices it
is missing.

## Fix, smallest first

1. **Add a `plugin.maintainer_address` config key**, set by `/cto-init` at the same moment it sets
   `plugin.source_path`. The two are only useful together; setting one without the other is the bug.
2. **Make `/feedback` verify before it routes.** If `source_path` is set but no maintainer address
   resolves, say so and fall through to the logging path — rather than printing a dispatch command
   built around an unresolved placeholder.
3. **Offer the tracker fallback automatically.** The plugin source repo has a git remote
   (`git@github.com:supmo668/aiadlc.git`); when no agent address exists, `/feedback` can offer to open
   an issue there instead of leaving the operator to notice the gap and improvise.

**Effect.** The actionable branch either actually acts, or admits it cannot — instead of describing an
action that has no recipient.

## Related

Filed alongside, same session: the `/expert` request (domain-calibrated research pass), and the
"nothing tracks a precondition the coordinator owes the human" defect. All three are logged here for
processing via `/aiadlc:feedback` once a route exists.
