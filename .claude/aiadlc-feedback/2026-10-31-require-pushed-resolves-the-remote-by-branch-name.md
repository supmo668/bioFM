---
date: 2026-10-31
from: biofm/matthew-mo/cto
area: tools/receipt-verify
severity: blocks-a-correct-land
---

# `receipt-verify --require-pushed` resolves the remote by BRANCH NAME, so a name collision reports pushed work as diverged

## What happened

A worktree agent pushed its work, then ran the gate's pushed-ness precondition:

```
BLOCKED: origin/lung-on-chipsim (c04e701) and HEAD (00940e9) have DIVERGED
```

The work was pushed. It was pushed to `origin/lung-on-chipsim-stage2`, where `HEAD` matched the
remote tip exactly. The check compared against `origin/<current-branch-name>` instead, and that ref
is the **archived Stage 1 tip from 2026-09-20**, five weeks stale and deliberately frozen.

## Why it matters more than a wrong message

The only two ways to satisfy the check as written are to **rename the local branch** or to
**force-push over the archived ref**. In this repository the second is forbidden: approvals row 79
records the stage2 remote as load-bearing for payload blobs and the Stage 1 ref as an archive. So a
correct agent, doing the correct thing, is told it has failed a precondition it has in fact met, and
the only mechanical fixes available are a rename or a destructive push.

The agent declined both and escalated, which was right. A less careful one force-pushes over an
archive to turn a check green, and the check's own message points that way.

## Repro

1. Have `origin/<name>` and `origin/<name>-suffix` both exist, with the work on the suffixed ref.
2. Be on local branch `<name>`, pushed to `origin/<name>-suffix`.
3. Run `receipt-verify --require-pushed`.
4. Observe DIVERGED against a ref the work was never meant to touch.

## Suggested fix

Resolve the comparison ref from the branch's **configured upstream** (`@{upstream}` /
`branch.<name>.merge`) rather than from the branch name, and fall back to the name only when no
upstream is set. Failing that, report *which* ref was compared and say that no upstream is
configured, so the message cannot be mistaken for "your work is unpushed". A precondition that can
only be satisfied by a destructive act should name that act rather than imply it.

## Verified in-session

`origin/lung-on-chipsim` = `c04e701` (2026-09-20), `origin/lung-on-chipsim-stage2` = `00940e9`
(2026-10-31), agent HEAD matched the latter, and the archived ref was confirmed untouched after the
push. The receipt itself verified independently: Hash E `6d8afb8`.
