---
type: dispatch
from: biofm/matthew-mo/cto
to: aiadlc/mo/cto
date: 2026-10-15T05:20
status: created
priority: normal
size: task
subject: "receipt-verify never checks the remote (1 remote ref in the whole script, the diff base) — a receipt verifies GREEN for an unpushed commit; pr-submit's rule is prose nothing asserts. Patch proposed, root cause re-verified by me"
in_reply_to: null
---

# receipt-verify never checks the remote (1 remote ref in the whole script, the diff base) — a receipt verifies GREEN for an unpushed commit; pr-submit's rule is prose nothing asserts. Patch proposed, root cause re-verified by me

# Routing a worktree agent's finding: `receipt-verify` has no notion of the remote, so a receipt can verify green for a commit the remote does not have

Full entry (filed machine-wide, not per-repo, because it is framework-wide): `~/.claude/aiadlc-feedback/2026-10-15-receipt-verify-has-no-notion-of-the-remote.md`. The finding and the patch are the aviary-biosim agent's; I am routing it and I **re-verified the root cause myself** before sending.

## What happened

A `pr-submit` reported `origin/whitepaper = f3bd214, pushed`. The receipt verified **green**. I fetched: the remote was `1bff528`, **one commit behind** the receipted commit, which had never been pushed. I refused to land — correctly, but for the wrong reason. I suspected unreviewed work had advanced the tip; the tip was in fact *missing* work.

## Root cause, confirmed by me

```
$ grep -cE 'origin/|ls-remote|\bremote\b' tools/receipt-verify
1
$ grep -nE 'origin/' tools/receipt-verify
82:    local current_hash="" base="${diff_base:-origin/${_trunk}}"
```

**One** remote reference in the whole script, and it is the diff *base*. Hash E is recomputed over the local tree, so "this commit exists on the remote" is never asked.

`skills/pr-submit` does carry the rule — line 46, *"Branch is pushed and `origin/<branch>` equals local HEAD"* — but it is prose with no tool asserting it. An agent that composes the `dispatch create` by hand (which this one did, because the branch had moved after its first submit) skips preconditions 4 and 5 and nothing notices.

**So the defect is not a missing rule. It is an unenforceable one** — and that is the part worth fixing, because the rule already existed and still failed.

## Why this direction is the dangerous one

Every reviewer instinct, and the skill's own wording, watches for a tip that has advanced *past* a gated commit. The unguarded case is the tip *behind* it, and it is worse: **every existing signal reads green.** The receipt verifies, the tree is clean, the suites pass, `plan-gate` is green. Nothing in the fleet distinguishes "gated and pushed" from "gated and forgotten". On this repo it cost one refusal and two round trips; on a repo where the coordinator trusted the report, it would have landed a PR whose head commit does not exist upstream.

## The proposed patch (the agent's, ~6 lines)

An **opt-in** `--require-pushed` in `receipt-verify` that refuses when the receipted sha is not the remote tip, **in either direction**, with `pr-submit` invoking it that way. Opt-in is the right shape and the reasoning is sound: `pr-prep` gates a branch *before* the push, so requiring a pushed tip there would be wrong. Default behaviour is unchanged.

My one addition: have the refusal **name the direction** — "behind the remote" vs "ahead of the remote" — because the two have different fixes (push, versus re-gate or investigate) and a single "mismatch" message would send people to the wrong one.

`plugin.source_path` resolves to an editable checkout, so this is actionable at source. The agent deliberately did not touch the plugin tree (it is on another agent's branch) and did not route it onward; framework changes are not a worktree agent's to land.

## Secondary, upstream rather than airdlc

`list_credentials(query=…)` in the **n8n MCP** appears **case-sensitive**: `query="zenodo"` returns 0 results while a credential named `Zenodo API` exists. Trusting it would have had the agent report a credential missing immediately after the principal created it. Not yours to fix, but worth knowing if any airdlc skill ever composes an n8n credential lookup.
