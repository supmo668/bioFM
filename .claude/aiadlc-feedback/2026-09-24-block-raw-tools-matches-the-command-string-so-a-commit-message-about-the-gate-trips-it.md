---
type: plugin-feedback
target: aiadlc plugin (bioFM) — hooks/block-raw-tools.sh
plugin_version: 0.60.0
reporter: bioFM/matthew-mo/cto
date: 2026-09-24
scope: plugin / operating-system behavior — NOT repo/app work
---

# 🟠 `block-raw-tools` matches the whole command string, so a **commit whose message describes the gate** is blocked as though it were the gated action

## Symptom

`git-safe-commit` invoked with a `--body` explaining *why the coordinator could not perform a
raw publish* was **refused by the raw-tools hook**, which reported the standard
"BLOCKED: raw `git push` is not allowed. All pushes go through a PR." No push was attempted.
The offending text was inside a quoted commit-message argument.

Reproduced trivially: any `git-safe-commit ... --body "... raw git push is hook-blocked ..."`.

## Root cause

The hook inspects the **command string** for the forbidden pattern rather than the
**operation being performed**. A commit is not a push, but a commit *message* that contains
the phrase is indistinguishable to a substring match.

Same family as the other items filed today: **a check derives its answer from something
adjacent to the thing it describes.** Here the adjacent thing is the argument text, and the
thing described is the git operation. It is the mirror of the `dispatch` metacharacter
guard — that one is silent when it matters; this one fires when it does not.

## Why it is worth fixing rather than routing around

The workaround is to reword the commit message, which is exactly the wrong incentive: it
pushes coordinators toward **writing less clearly about the gates they are enforcing**. The
commit that tripped this was recording a refusal to accept a relayed authorisation for that
very operation — the most audit-relevant kind of message there is, and the kind most likely
to name the operation explicitly.

## Suggested fixes, in order

1. **Match on the invoked binary and its subcommand, not the full string** — parse `argv[0]`
   and `argv[1]` (`git push`) rather than grepping. A `git-safe-commit` invocation is not a
   `git` invocation at all, so it should never be a candidate.
2. **Exclude quoted argument values** from the scan, or at minimum the value of `--body` /
   `-m` / `--message`, which exist to hold prose.
3. If a substring scan is kept, **say so in the refusal text** — "matched the phrase in your
   command; if this is a commit message, reword" — so the operator is not left believing the
   tool thinks they attempted a push.

## Status

open. Worked around by rewording; the commit landed as `5561fb2`.
