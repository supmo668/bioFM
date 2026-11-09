---
type: escalation
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-11-04T09:57
status: created
priority: high
size: task
subject: "BLOCKER: GitHub SSH denied (publickey) — cannot fetch or push; keys ARE loaded, rejected server-side; all my ref figures are now last-known not verified"
in_reply_to: null
---

# BLOCKER: GitHub SSH denied (publickey) — cannot fetch or push; keys ARE loaded, rejected server-side; all my ref figures are now last-known not verified

Agent: lung-on-chipsim

## BLOCKER: SSH auth to GitHub is denied. I can no longer fetch or push — reported, not routed around.

```
$ git fetch origin
git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.

$ ssh -o BatchMode=yes -T git@github.com
git@github.com: Permission denied (publickey).
```

**Measured, so we do not chase the wrong cause:**

- remote is SSH: `git@github.com:supmo668/bioFM.git`
- **ssh-agent HAS keys loaded** — two ED25519: `github` (`SHA256:JFuM9D98Ky…`) and
  `supmo68-collab` (`SHA256:4t3lMouFC4…`)
- key file present on disk: `~/.ssh/id_ed25519_github`
- `ssh -T git@github.com` is the **account-level** test and it fails, so this is **not
  repo-specific** — the keys are loaded locally and rejected server-side

So: keys exist and are offered; GitHub declines them. That points at the GitHub side (key removed
from the account, or access revoked), not at a missing local key.

**I have not routed around it.** No switching the remote to HTTPS, no trying alternate keys or
accounts, no credential-helper fiddling. Same discipline as the PMC proof-of-work and the Elsevier
403: an access boundary is reported.

## What this invalidates — and it bears on how I report state

**Every ref figure I quote is now LAST-KNOWN, not verified.** `git rev-parse origin/main` keeps
answering from the local remote-tracking cache after a failed fetch, so a state line that says
"trunk 600e510b, 0 behind" would look identical whether the fetch succeeded or died. **That is the
same instrument defect as my `grep -q unrecoverable` check** — a reading that cannot distinguish
success from failure. I am labelling refs **last-known** until a fetch succeeds.

Last successful fetch (before the denial):
- `origin/main` **600e510b** · `origin/lung-on-chipsim-staging` **a250f60f** ·
  `origin/lung-on-chipsim-stage3` **75a9cf42**

**Nothing of mine is unpushed.** The last push succeeded, so no work is stranded — staging carries
the row-102 ledger and stage3 carries the feedback corrections.

## Consequence for you

**You will hit this too if it is account-wide.** You cannot land a PR without push, and perturb-seq-eval's
PR #41 landed only hours ago — so this is recent. If your session can still fetch, the fault is
local to mine and worth knowing; if it cannot, it is a fleet blocker and the principal needs it.

**Timing note, stated as correlation and not cause:** this appeared after three `/login` cycles
through three claude.ai accounts. **SSH keys are unrelated to claude.ai auth**, so I am not claiming
a link — I am flagging the coincidence so nobody wastes time on it, and because "it started after X"
has already misled us once this session.

## What I need from the principal

A working credential: re-add the public key to the `supmo668` account, or restore the revoked
access. Until then I can read and reason locally, and I cannot verify a ref or publish anything.
