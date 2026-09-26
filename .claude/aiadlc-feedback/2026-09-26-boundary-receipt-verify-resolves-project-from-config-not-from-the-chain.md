---
type: plugin-feedback
target: aiadlc plugin (bioFM) — tools/git-safe-commit --boundary, receipt project scoping
plugin_version: 0.60.0
reporter: bioFM/matthew-mo/cto
date: 2026-09-26
scope: plugin / operating-system behavior — NOT repo/app work
---

# 🟠 `git-safe-commit --boundary` resolves receipt project from `config project.name`, so a chain signed under the workstream name is invisible to the gate meant to verify it

**Reported by** `biofm/matthew-mo/perturb-seq-eval`, which does not write this log and asked the CTO
to file it.

## Symptom

A P0–P5 receipt chain was signed with `project=perturb-seq-eval` (the workstream). At the phase
boundary, `git-safe-commit --boundary` verifies receipts by resolving the project from **config
`project.name`**, which in this monorepo is `bioFM`. The chain is therefore **invisible to the very
gate that exists to verify it** — the boundary commit cannot see the receipts that justify it.

## Why it is not merely cosmetic

The boundary gate's purpose is to refuse a boundary that has no verified receipt. A project-name
mismatch makes it refuse for the wrong reason, or — worse — makes an agent re-sign under a different
project to get past it. Either way the gate stops discriminating between "a receipt exists" and "a
receipt exists under the name this tool happens to resolve."

In a monorepo the two names are *routinely* different: `project.name` is the repo, while receipts are
naturally scoped per workstream, which is also how `paths.workstreams_root` organises everything else.

## The workaround used, which is correct but should not be necessary

The agent signed the derived receipt with `project=bioFM`, matching the convention every landed
boundary commit in this repo already uses, and said so in the receipt summary. `receipt-verify` still
resolves the parent **by hash** and prints the derivation, which is what makes the workaround safe
rather than a papering-over: the chain remains checkable even though the name was changed to satisfy
the gate.

## Suggested fixes, in order

1. **Resolve the boundary receipt's project the same way receipts are signed** — per workstream, not
   from `project.name`. The tool already knows the workstream at a boundary.
2. **Or accept either**, and say which it matched, so a name mismatch is visible instead of silent.
3. **At minimum, make the refusal name the project it looked for and the project it found.** The
   current failure does not tell the operator that a *name* is the problem, which is why this took a
   measurement to diagnose rather than a glance.

## Related

Same family as `2026-09-26-docs-notion-project-key-unread-and-provider-none-was-the-only-writer-gate.md`
and the earlier receipt findings: **a surface resolves a correctness-relevant value from something
adjacent to the thing it describes** — here, the repo's name standing in for the chain's own scope.

## Status

open. Worked around per above; `receipt-verify`'s hash-based parent resolution is what keeps the
chain honest in the meantime.
