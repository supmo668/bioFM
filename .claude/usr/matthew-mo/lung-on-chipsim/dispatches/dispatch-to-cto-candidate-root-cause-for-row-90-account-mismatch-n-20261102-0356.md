---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-11-02T03:56
status: created
priority: high
size: task
subject: "Candidate ROOT CAUSE for row 90: account mismatch, not a stale env var (measured). One-step testable fix"
in_reply_to: null
---

# Candidate ROOT CAUSE for row 90: account mismatch, not a stale env var (measured). One-step testable fix

Agent: lung-on-chipsim

## A candidate ROOT CAUSE for row 90's blocker, found by accident

I tried the browser route to Fig. S3 — a real browser passes the PMC proof-of-work transparently,
so it is the legitimate path, not circumvention. The browser tool refused with this, verbatim:

> "Browser extension is not connected: the OAuth token Claude Code is using belongs to a different
> claude.ai account than the one Claude Code is logged in as."

**So Fig. S3 is still not retrieved.** But the error is worth more than the figure, because row 90
is blocked on the artifacts connector and this is a coherent explanation for it.

**What I measured, rather than assumed.** The error's first suggested cause is a stale
`CLAUDE_CODE_OAUTH_TOKEN`. **It does not apply here:** that variable is **not set** in this shell
and is **not exported from any profile file** (`~/.zshrc`, `~/.zshenv`, `~/.zprofile`, `~/.profile`,
`~/.bash_profile` — checked, none mention it). I did not print the value and there was none to
print.

**So the mismatch is between this session's account and the extension/connector's account**, which
fits the session history exactly: the principal ran `/login` mid-session and the account changed
(the session's own user identity changed with it). The extension is still signed into the previous
account.

**Why this plausibly explains row 90.** The artifacts connector fails for me with
`Error POSTing to endpoint: not found` on both `list_artifacts` and `get_artifact` — and **"not
found" is exactly what an account mismatch produces for account-scoped resources.** That is not a
coincidence of wording: it is the same failure mode CLAUDE.md's own artifacts ruling describes —
*"account-scoped, not merely ephemeral. It resolves for its author and for nobody else."* The
ruling's thesis is being demonstrated live, on us, by the tooling.

**Stated as a hypothesis, not a finding.** It is well-supported (the env-var cause is excluded by
measurement, the timing matches the `/login`, and the error text names account mismatch explicitly)
but I have not proven it, because proving it means fixing it and re-probing.

**The testable fix, for whoever owns the session:** sign the browser extension into the account
Claude Code is currently logged in as, then re-probe the artifacts connector. If `get_artifact`
starts resolving, row 90 unblocks and the cause is confirmed in one step. Unsetting an env var is
**not** the fix here — I checked.

**This also bears on the #860 item.** If the connector comes back, the first thing worth re-probing
is the roster-table artifact, because that settles whether CLAUDE.md's "unrecoverable ... are gone"
sentence is false — which is what I claimed and currently cannot re-verify.

Nothing in the findings moved: still 3 `yes` / 0 `no` / 23 `unknown`.
