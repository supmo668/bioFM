# A receipt can never cover the tip when the workflow writes tracked state after the gate

**Filed:** 2026-10-16 · **By:** biofm/matthew-mo/cto · **Plugin version in effect at filing:** 0.82.0
**Scope:** plugin / operating-system behavior — NOT repo/app work
**Status:** open

**Symptom, observed three times in one workstream.** The perturb-seq-eval deposit workflow records
its progress in a **tracked** state file (`publish.state.v060.json`) after each venue action. Every
such write moves the diff vs the trunk, so `receipt-verify --workstream/--project` reports
`BLOCKED: Found N receipt(s) but none match current code` at the branch tip — three times:

| Event | Receipt | Uncovered delta |
|---|---|---|
| drafts created | `ae02b6b` | state file + dispatch payload |
| drafts discarded, state cleared | `ae02b6b` | state file + dispatch payload |
| revisions prepared | `e0c358e` (derived) | state file + dispatch payload |

In each case the delta contained **zero** `.py/.sh/.mjs/.toml/.yml/.tex` files — verified by
file-type filter, not assumed. The gated code is exactly the code that acted.

**Why this is a tooling problem, not an agent problem.** The agent did nothing wrong: it gated, then
performed the authorised action, then durably recorded what the venue returned. That record *must*
be tracked — it is how a resumed session knows a draft already exists, and it is what
`DraftRequiredError` reads to refuse a publish that was never prepared. So the workflow cannot
avoid writing it, and the receipt can therefore never cover the tip. The CTO is left choosing
between a derived receipt per venue call (a treadmill) and waving the check through (which erodes
the one guarantee the receipt provides).

**What makes it worse:** the failure mode is identical whether the uncovered delta is a state write
or genuinely ungated code. `BLOCKED` says the same thing for both, so the check that should
distinguish "safe data write" from "unreviewed implementation" cannot.

**Fixes, in preference order:**
(a) **A QG-scope exclusion for declared runtime-state paths**, the way `.claude/usr/**` is already
outside the diff. Something like `quality.receipt_exclude: ["**/publish.state.*.json"]`, declared in
config so the exclusion is visible and auditable rather than ad hoc.
(b) **Have `receipt-verify` classify the uncovered delta** and report it: "BLOCKED — 2 files outside
the receipt: 0 code, 2 data (listed)". The CTO could then make an informed call in one step instead
of three commands.
(c) Failing both, document that a workflow which writes tracked state should write it **once, last**,
so a single derived receipt can cover it.

**Effect.** A receipt-gated workflow that must record external side effects stops producing a
permanent false alarm, and `BLOCKED` goes back to meaning "unreviewed code" — which is the only
meaning worth having.
