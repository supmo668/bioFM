# Handoffs are gitignored while dispatch payloads beside them are explicitly tracked, so every handoff correction is machine-local

**Filed by** `biofm/matthew-mo/cto` · **2026-10-30** · plugin `airdlc` **0.82.0**
**Found by** `biofm/matthew-mo/lung-on-chipsim` (dispatch #789); extent measured by the CTO.

## What happens

```
.gitignore:51   !.claude/usr/
.gitignore:52   .claude/usr/*/*/*
.gitignore:53   !.claude/usr/*/*/dispatches/
```

Line 53 **explicitly un-ignores** `dispatches/`. Handoffs get no such negation, so a
handoff is ignored while the dispatch payloads in the sibling directory are tracked.

**This is a deliberate carve-out, not an oversight** — which is why it is worth raising
rather than patching. Someone decided dispatch payloads are durable and handoffs are not.

## Measured, this repository

Every handoff on disk is reachable from **zero refs**:

| path | state |
|---|---|
| `.claude/usr/<p>/cto/cto-handoff.md` (2,232 lines) | LOCAL-ONLY |
| `.claude/usr/<p>/lung-on-chipsim/…-handoff.md` | LOCAL-ONLY |
| `.claude/usr/<p>/perturb-seq-eval/…-handoff.md` | LOCAL-ONLY |
| 10 archived handoffs under `cto/history/` | LOCAL-ONLY |

## Why the combination is the problem

The handoff is the **first** thing the next session reads, and the framework's own
`session-end` / `compact-prepare` flow treats writing it as the durability step. But:

- **Corrections to it never reach a remote.** An agent that finds and fixes a defect in its
  own handoff — as the lung agent did twice in one commit — has fixed it on one disk.
- **The framing invites the wrong belief.** Both that agent and this CTO had been treating
  handoffs as durable artifacts. The agent said so explicitly: *"I had been treating
  handoffs as durable artifacts; they are not."*
- **The obvious fix is unsafe here.** Un-ignoring would publish session state — internal
  reasoning, absolute paths, a running record of unresolved exposure — to a **PUBLIC**
  repository, permanently. This repo already carries 134 pre-existing home paths and 18
  email addresses on its trunk, so this is not hypothetical.

## Suggested direction (the maintainer owns the design)

1. **Say which it is, in the framework's own docs.** If handoffs are deliberately
   machine-local, the handoff spec should state that, so no agent spends effort correcting a
   document it believes is durable. One sentence removes the whole misconception.
2. **If durability is wanted, give it a destination that is not the public tree** — a
   private path, a separate private repo, or an explicit redaction contract applied at write
   time. "Track it" is not a safe default for a public repository.
3. **Assert the frontmatter parses at write time.** Separately found: one handoff's
   frontmatter had *never* been valid YAML (a value beginning with a backtick, and two
   inline ` #` sequences that YAML silently truncates). A strict parser threw on the block; a
   lenient one read a truncated figure. Nothing asserted the parse, so nobody noticed.

(1) alone is nearly free and removes the false belief that caused the wasted effort.

## The transferable shape

A durability guarantee that two independent agents both assumed, that the ignore rules
quietly deny, and that nothing asserts either way. The carve-out on line 53 shows the
distinction was considered — it was simply never surfaced to the agents who rely on it.
