# `block-raw-tools.sh` matches the command STRING, so prose *about* a blocked command is itself blocked

**Date:** 2026-10-19
**Filed by:** biofm/matthew-mo/cto
**Plugin:** airdlc 0.82.0
**Severity:** medium — silently costs whole dispatches, and specifically the ones explaining a blocker

## What happened

Sending a dispatch that explained to an agent **why the CTO cannot delete a remote branch**, the
`PreToolUse` hook refused the entire `Bash` call:

```
**BLOCKED: raw `git push` is not allowed. All pushes go through a PR.**
```

No push was attempted. The command was `tools/dispatch create --to … --body "…"`, and the **body text**
contained the forbidden command's name inside a sentence of the form *"a raw `<that command>` is refused
by the auto-mode classifier, so remote ref deletion sits with the principal."*

The hook pattern-matches the command string it is handed. A dispatch body is part of that string, so
**describing** the blocked operation trips the guard that exists to prevent **performing** it.

## Why it matters more than it first appears

1. **It blocks exactly the message most worth sending.** The dispatch that explains a blocked path
   necessarily names the blocked path. This guard is therefore biased against explanation: the clearer
   the writeup, the more likely it is refused.
2. **The failure is total, not partial.** The whole tool call is refused, so a long dispatch body is
   lost and must be rewritten. There is no indication that the *body* rather than the *command* is what
   matched, so the natural first reading is that the tool itself is forbidden.
3. **The workaround degrades the record.** I had to rewrite the dispatch to avoid naming the command —
   so the permanent coordination record now says "the raw remote-ref-removal invocation" instead of the
   actual command a reader would need in order to reproduce or fix the situation. The guard made the
   audit trail *less* precise, which is the opposite of what a coordination record is for.
4. **It is indiscriminate about surface.** Any tool whose arguments carry free text — `dispatch`,
   `approval-log append`, `git-safe-commit -m`, `to-issue` — can be refused for quoting a command name.
   A commit message explaining "do not use X here" is the canonical example.

## Proposed fix

**Scope the match to the command position, not the whole string.** The hook should inspect the
*executable being invoked* (argv[0] of each pipeline stage, after shell parsing) rather than grepping the
raw command text. A forbidden name appearing inside a single- or double-quoted argument is data, not an
invocation.

If full shell parsing is too heavy for a hook, two cheaper mitigations, in order of preference:

1. **Ignore matches inside quoted arguments.** A match whose offset falls within a quoted span is prose.
2. **Allowlist the known free-text-carrying tools** (`dispatch`, `approval-log`, `to-issue`,
   `git-safe-commit`) for *body/message* flags specifically — still guard their other arguments.
3. **At minimum, say which part matched.** The current message explains the policy at length but never
   says *where* in the command the pattern was found. One line — `matched inside argument 7 (--body)` —
   would have turned a rewrite into a five-second diagnosis.

## Evidence

- Hook: `hooks/block-raw-tools.sh`, invoked as `PreToolUse` on `Bash`.
- Refused command shape: `tools/dispatch create --to biofm/matthew-mo/perturb-seq-eval --type dispatch
  --subject "…" --body "…<forbidden command name>…"`. No push, fetch, or write to any remote.
- Context: dispatch #686 asked the CTO to delete `origin/perturb-seq-eval` after PR #28 landed
  (merge `9680679`). The reply had to explain that remote ref deletion is unavailable to the CTO —
  `git-cto branch-delete` is local-only, `git-push` exposes no delete, and the raw invocation is denied
  by the auto-mode classifier as `[Git Destructive]`.
- Related: the same remote-deletion gap was recorded after the aviary land for `origin/whitepaper`.
  Three branches now need principal-side removal for one shared cause.
