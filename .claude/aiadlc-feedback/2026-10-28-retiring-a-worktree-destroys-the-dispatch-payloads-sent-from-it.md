# Retiring a worktree destroys the dispatch payloads sent from it, and the dispatch record survives as a read receipt for substance that no longer exists

**Filed by** `biofm/matthew-mo/cto` · **2026-10-28** · plugin `airdlc` **0.82.0**

> ## AMENDED 2026-10-29 — THE DIAGNOSIS BELOW IS MISSING ITS CONTROLLING VARIABLE
>
> **The title's claim is too broad and the mechanism it names is not the determinant.** Found by the
> `lung-on-chipsim` worktree agent, which measured this filing against its *own* worktree because it
> had a deferred retirement decision riding on it. CTO-verified independently before amending:
>
> ```
> lung-on-chipsim payloads   57 on disk · 57 TRACKED at HEAD · 0 untracked · 54 on origin/main
> aviary-biosim   payloads   0 on origin/main
> ```
>
> **The four aviary payloads did not die because the worktree was retired. They died because they
> were NEVER COMMITTED**, and retirement is merely when that became visible. The lung worktree could
> be retired today and lose nothing but its three most recent, which are committed and awaiting a
> flush.
>
> **Restated, with the variable in it:** *retiring a worktree destroys dispatch payloads **that were
> never committed** — and the dispatch row survives either way, so a surviving row is
> indistinguishable from one whose payload is intact.*
>
> **That relocates the fix, which is why this amendment matters more than a wording correction.** As
> originally written, this filing pointed at `post-land` Step 11 and `worktree-delete`, both of which
> are doing their job. With the variable in it, **the mitigation already exists and is already
> enforced**: the coord-commit traceability mandate, whose Stop-hook nagging is exactly what made the
> lung payloads survivable. **The gap is that nothing CHECKS the mandate was honoured before
> retirement.**
>
> **The agent's proposed fix supersedes the four candidates below, and is narrower than any of them:**
> `tools/worktree-delete` should REFUSE while the worktree holds dispatch payloads that are untracked
> **or committed-but-unpushed**, and name them. Fail-closed, no new bookkeeping — the information is
> already in `git ls-files --others` and `git rev-list @{u}..`.
>
> Note that candidate (3) below guessed at this and keyed on the **wrong predicate** — "an unresolved
> dispatch's payload", i.e. mail state — and was dismissed in this filing's own words as "probably too
> strict on its own". The right predicate is **durability**, not resolution. A payload that is
> committed and pushed can be retired over freely however unresolved its row is; one that is untracked
> cannot be, however resolved.
>
> It is the same shape as the output-root registry defect this fleet fixed a day earlier: **the claim
> existed and nothing checked it.**
>
>
> ### AMENDED AGAIN 2026-10-29 — the proposed command is wrong, and the predicate is NON-STATIONARY
>
> Two corrections to the fix recommended above, both measured on the live worktree:
>
> **1. `git rev-list @{u}..` is the wrong test.** On the `lung-on-chipsim` worktree, `@{u}` resolves
> to `origin/lung-on-chipsim`, which is the **archived Stage 1 tip** — the branch the agent is 770
> commits ahead of and deliberately never pushes to. So the rule as written returns 770 and would
> **refuse retirement permanently**, while all its payloads are demonstrably safe on
> `origin/lung-on-chipsim-stage2`. "Unpushed relative to the tracking branch" is not the same question
> as "do the bytes exist on a remote", and in a fleet that pushes work to a differently-named branch
> they diverge completely.
>
> **The predicate should be: every payload blob at HEAD is reachable from SOME remote ref.** Measured
> that way on the same worktree: 58 payloads at HEAD, 57 byte-identical on a remote, 1 not.
>
> **2. The property is non-stationary, and that is the sharper point.** The one payload not on a
> remote is *the dispatch reporting that all payloads are on a remote*. The agent measured zero
> unpushed, sent the report, and the act of reporting made it one. This is not a careless measurement
> — it is unavoidable: any agent-asserted "all payloads are safe" is falsified by the dispatch that
> asserts it.
>
> **So the check cannot be a thing an agent reports and a human trusts. It must be evaluated inside
> `tools/worktree-delete` at the moment of deletion.** That is a stronger argument for making it a
> precondition than the durability argument that motivated it: a convention an agent self-certifies is
> not merely unchecked, it is *uncheckable from the agent's side*.
> Everything below is preserved as filed. The four-instance evidence and the symlink mechanism are
> still accurate as far as they go — a payload *is* reachable only by symlink from the recipient's
> inbox — but that mechanism is what makes an uncommitted payload *fragile*, not what destroys it.


## What happens

A dispatch's body is stored as a file in the **sender's** `.claude/usr/<principal>/<agent>/dispatches/`
directory. When the sender is a worktree agent, that directory lives **inside the worktree**. The
recipient's inbox holds a **symlink** to it.

`tools/post-land` Step 11 then correctly instructs the CTO to retire the merged worktree, and
`tools/worktree-delete` removes it. **The payloads go with it.** The dispatch rows survive in the
out-of-tree ISCP database, so `dispatch list` still shows them — with their subject lines, their
priority, their `read` status and a dangling symlink.

The result is a **read receipt for substance that no longer exists**, and it is indistinguishable
from a read receipt for substance that was read and handled.

## Measured, four instances, one cause

All four are from `biofm/matthew-mo/aviary-biosim`, and all four symlink into the **same** retired
worktree:

| dispatch | type | subject survives | payload |
|---|---|---|---|
| `#587` | pr-submit | "Ready for PR landing: whitepaper — A7 fixes re-gated (receipt f8569cb verified)" | **gone** |
| `#590` | pr-submit | "Ready for PR landing: whitepaper — plugin-tests re-pinned per #588, re-gated" | **gone** |
| `#603` | pr-submit | "A7-8 ruled by the principal and applied; deposit pipeline built; receipt 2713c48 verified" | **gone** |
| `#626` | review-response | "No-credit clause DROPPED (not softened) … I added one sentence beyond your instruction and flag it for pushback" | **gone** |

```
$ dispatch read 626
(note: stale payload symlink → .../worktrees/aviary-biosim-272-scratch/.claude/usr/.../dispatches/...
 — falling back to repo-tracked copies)
(payload file not found at .claude/usr/matthew-mo/aviary-biosim/dispatches/... — searched symlink,
 local, main checkout, all branches, all worktrees, and the sender repo's recorded root)
```

`worktrees/aviary-biosim-272-scratch` was retired during the PR #2 post-land on 2026-10-17, exactly as
`post-land` Step 11 prescribes. **The tool did its job and the payloads were collateral.**

The fallback search is thorough — symlink, local, main checkout, all branches, all worktrees, sender
root — which is what makes the conclusion safe: these are not misplaced, they are **destroyed**.

## Why this one matters more than a lost file

`#626` is the sharpest case. Its subject says the agent *"added one sentence beyond your instruction
and flag[s] it for pushback"* — so the record states that **something was flagged for the CTO to push
back on, and what it was is unrecoverable.** The surrounding question (a venue service credit, which
is load-bearing on a retained sentence in a landed paper) is still open on our side. The evidence that
would settle what changed is gone.

Three of the four are `pr-submit` dispatches naming **verified receipts**. A receipt's whole purpose is
to bind a gate to an exact diff and be auditable later. The binding survives; the submission that
explained it does not.

## This is not an aviary problem

Nothing about it is specific to that agent or that workstream. **Any** worktree agent that dispatches
and is later retired loses its payloads the same way. In this repository that is three live worktrees
(`lung-on-chipsim`, `cellforge-agents`, `v2r-loop`) plus nine `.claude/worktrees/agent-*` checkouts.
The lung agent is mid-PR as this is filed and will be retired on landing.

It also interacts badly with a rule the framework already enforces elsewhere: `post-land` **prefers
self-retire**, dispatching the owning agent to run `/worktree-delete` once it has no pending work.
"No pending work" is evaluated on the agent's own queue — it says nothing about whether *other*
agents' records depend on files inside that worktree.

## Suggested direction (not a patch — the maintainer owns the design)

The invariant worth having: **a dispatch's payload must outlive its sender's worktree.** Candidates,
cheapest first:

1. **Copy, don't symlink, at dispatch time.** The recipient's inbox gets the bytes. A symlink is an
   optimisation that trades durability for deduplication, and the dedup saves kilobytes.
2. **Copy on retire.** `worktree-delete` materialises any payload that something still symlinks to,
   before removing the tree. Keeps the symlink optimisation and closes the hole at the one moment it
   opens.
3. **Refuse to retire** while an unresolved dispatch's payload lives inside the worktree, naming them.
   Fails closed, but blocks legitimate cleanup behind unrelated mail — probably too strict on its own,
   and strictly worse than (2).
4. Whatever is chosen, **`dispatch read` on a destroyed payload should be a distinguishable state**,
   not prose in a note. A caller cannot currently tell "payload gone" from "payload empty" without
   reading the human-readable text — which is how four instances went unnoticed here for eleven days.

(2) plus (4) looks like the smallest change that makes the failure both impossible and visible.

## How it was found, because the finding was accidental

Not by a sweep. The CTO was reviewing 52 read-but-unresolved dispatches — a backlog whose own cause is
that `dispatch read` is not `dispatch resolve` (bioFM lung approvals rows 59, 62, 64) — and three
`pr-submit` rows reported a missing payload while being triaged. A fourth turned up when `#626` was
read for an unrelated question, and its note was the only one that printed the **stale symlink path**,
which is what identified the retired worktree as the common cause.

**Had those dispatches been resolved and forgotten rather than reviewed, the cause would still be
unknown** — and the next worktree retirement would have taken more payloads with it.
