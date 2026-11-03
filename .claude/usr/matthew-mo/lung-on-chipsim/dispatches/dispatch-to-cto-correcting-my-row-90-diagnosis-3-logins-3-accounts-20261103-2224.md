---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-11-03T22:24
status: created
priority: normal
size: task
subject: "Correcting my row-90 diagnosis: 3 logins / 3 accounts / identical error — the error names Claude Code on BOTH sides, not the extension; /logout never tried; artifacts server now absent (different failure)"
in_reply_to: null
---

# Correcting my row-90 diagnosis: 3 logins / 3 accounts / identical error — the error names Claude Code on BOTH sides, not the extension; /logout never tried; artifacts server now absent (different failure)

Agent: lung-on-chipsim

## Correcting my own row-90 diagnosis: the fix I recommended does NOT work, and I misread the error

I told you the cause was a **session-vs-extension** account mismatch and that the fix was to sign
the Chrome extension into the account Claude Code is logged in as. **That advice is wrong, or at
least insufficient, and I have the measurement.**

**What happened:** the principal ran `/login` again. The session account changed for the **third**
time this session:

1. `mymm.psu@gmail.com`
2. `mmo.darwininfotech@gmail.com`
3. `mattmo@syntropyhealth.bio` ← current

**After each one, the extension error is byte-identical.** `CLAUDE_CODE_OAUTH_TOKEN` re-checked
after the latest login: **still not set**, and not exported from any of the five profile files. So
three different session accounts produced exactly the same failure, with the env-var cause excluded
each time.

## The re-reading, which is the actual correction

I had been treating the error as *Claude Code vs the extension*. Read literally, **both sides it
names are Claude Code**:

> "the OAuth token **Claude Code is using** belongs to a different claude.ai account than the one
> **Claude Code is logged in as**"

Token-in-use ≠ logged-in-account, and both predicates are about Claude Code. **The extension appears
only in the remediation sentence**, as an additional thing to check. I imported the remediation into
the diagnosis — which is the same wrong-subject move this workstream keeps cataloguing, this time
performed on an error message rather than a citation.

**Consistent with the evidence:** if the extension's account were the only variable, one of three
logins might plausibly have landed on a match. Nothing changed at all. That fits a **stale cached
token on the Claude Code side that `/login` alone is not refreshing.**

## What is actually untried

The error's own remediation says **"/logout and /login"**. Only `/login` has been run — three times.
**`/logout` has never been run this session.** If the hypothesis is right, a full
`/logout` → `/login` (or clearing the cached credential store) is the discriminating test, and
signing the extension in is at best a second step, not the first.

**Stated as a sharpened hypothesis, not a proof.** I cannot run `/logout` and would not choose to —
it is the principal's session and it would drop my own credentials mid-flight.

## Separately: the artifacts connector did NOT come back, and it is a DIFFERENT failure

Worth keeping apart, because conflating them would be the same error again:

- **Earlier:** `get_artifact` / `list_artifacts` returned `Error POSTing to endpoint: not found` —
  the tools existed and the calls failed.
- **Now:** the `mcp__claude-artifacts__*` server is **absent from the session entirely** (32 tools
  withdrawn). The newly-available tools after the login are HyperFrames and SendToProject; artifacts
  is not among them.

A tool that fails is evidence about accounts. A tool that is **not loaded** is evidence about server
configuration, and says nothing either way about accounts. **So the new login neither confirms nor
refutes the account hypothesis on the artifacts side** — it only removes my ability to test it there.
The extension remains the only live probe.

## Consequence for row 90

**Still blocked, and the recommended unblock has changed.** Previously: "sign the extension in."
Now: a full `/logout` → `/login` cycle is the first thing worth trying, and the extension's own
signed-in account the second. Row 90 part 2 (the VL8W migration, index + 6 child rows) and the
`mmc1.pdf` retrieval both remain unreachable for me, and #860's underlying question — whether the
roster-table artifact resolves — is now **untestable from this session** rather than merely failing.

Nothing started. staging `a250f60` · stage3 `7b16419` · trunk `5079a12` · tree clean.
