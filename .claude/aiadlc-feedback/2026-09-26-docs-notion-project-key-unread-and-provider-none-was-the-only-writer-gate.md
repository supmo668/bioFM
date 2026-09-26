---
type: plugin-feedback
target: aiadlc plugin (bioFM) — docs.* schema vs tools/docs-plan
plugin_version: 0.60.0
reporter: bioFM/matthew-mo/cto
date: 2026-09-26
scope: plugin / operating-system behavior — NOT repo/app work
---

# 🟠 `docs.notion.project` is documented in the schema prose and read by no tool; and `docs.notion.parent` is the only thing that was gating Notion writes

Two findings from one config change (#414–#417). Both are documentation-ahead-of-implementation.

## 1. A config key that exists only in prose

A worktree agent requested `docs.notion.project: <name>` to pin a namespace, citing the 0.64.0
schema prose. Measured: **zero hits** for `notion.project` or `notion_project` across every tool and
hook in the plugin. The keys `tools/docs-plan` actually resolves under `docs.notion` are `parent`,
`usage_parent` and `scopes.<agent>`.

Setting it would have produced a config that **looks configured and does nothing** — and it was
requested in good faith by an agent reading the documentation. This is the second key this fleet has
found documented-but-unread.

**Fix, in order:** either implement it, or remove it from the prose, or have the config reader
**warn on an unrecognised key under a known namespace**. The third is the general fix and it catches
the next one too: a typo'd or aspirational key is currently indistinguishable from a working one.

## 2. `provider: "none"` was the de-facto enforcement of a rule stated as policy

`docs-plan`'s usage text says the Notion write is *"a CTO-only MCP action the skill dispatches."*
Measured: **nothing enforces the CTO part.**

- `docs-plan` resolves the agent identity (`tools/agent-identity`) only to choose **which scope** —
  `docs.notion.scopes.<agent>`, falling back to `docs.notion.parent`. It never gates *whether* the
  write happens.
- No hook mentions Notion except a connectivity reminder in `agent-welcome.sh`.
- A worktree agent in this repo wrote Notion rows successfully under an explicit principal
  exception — which **proves the capability exists inside a worktree**, so capability is not the
  gate either.

So the only thing making the path inert fleet-wide was `docs.provider: "none"`. The moment a
principal asks for `provider: notion`, a policy that reads as enforced becomes a policy enforced by
goodwill, and nothing announces the transition.

**What I did locally, which is also the suggested fix:** leave `docs.notion.parent` **blank** and set
only `docs.notion.scopes.cto`. Every non-CTO agent then resolves no scope, falls back to the blank
parent, and `docs-plan` documents that as "no Notion propagation" — so **CTO-only becomes
configuration rather than convention**, using machinery that already exists and failing in the safe
direction.

**Fix for the plugin:** say this in the `docs.notion` schema comments — that a blank `parent` plus a
single-agent `scopes` entry is the supported way to restrict the writer, and that setting `parent`
opens it to every agent. Right now a reader fills in `parent` because it looks like the primary knob,
and silently un-restricts the write.

## Related

Same family as `2026-09-24-qgr-hashes-findings-files-that-live-in-scratch-and-are-then-deleted.md`
(an attestation whose referent is designed to evaporate) and
`2026-09-24-dispatch-metachar-warning-fires-in-the-negated-condition.md` (a guard whose signal is
uncorrelated with its fault): **a surface reports a property it does not hold.** Here the surface is
a tool's own usage text, and the property is an access restriction.

## Status

open. Locally mitigated by the blank-parent + `scopes.cto` arrangement, with both reasons recorded
as comments in `agency.yaml` so the blank is not later read as an oversight and filled in.
