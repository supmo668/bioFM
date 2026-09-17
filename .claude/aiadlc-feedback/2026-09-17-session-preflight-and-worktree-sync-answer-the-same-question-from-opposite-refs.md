# `session-preflight` and `worktree-sync` answer "is this branch current?" from **opposite refs**, and `worktree-sync`'s own comment explains why the other one is wrong

**Components:** `tools/session-preflight` (Check 2), `tools/worktree-sync` (plugin 0.56.0)
**Severity:** medium — a blocking preflight and the tool that is supposed to fix it disagree, so the
prescribed remedy does not clear the failure
**Observed:** 2026-09-17, bioFM, reported by the `aviary-biosim` worktree agent and verified by the
CTO against both sources

## The two tools resolve the same question differently, on purpose, in opposite directions

`session-preflight` Check 2 uses the **local** `main`:

```
88:  git rev-parse --verify main
95:  git merge-base --is-ancestor "$main_ref" HEAD     # local main
98:  behind=$(git rev-list HEAD.."$main_ref" --count)  # local main
99:  report_fail "Branch is $behind commits behind $main_ref"
```

`worktree-sync` deliberately does **not**, and says so in a comment:

```
173: # In a worktree the local `$MAIN_BRANCH` only advances when the main checkout
174: # syncs it — so without this fetch, "sync" merges however-stale-the-CTO-left-it,
175: # and an iteration starts on an out-of-date base. Prefer `origin/$MAIN_BRANCH`
178: git fetch --quiet origin "$MAIN_BRANCH"
```

So one tool treats local `main` as authoritative; the other treats it as a known-stale ref and
fetches past it. **`worktree-sync` v2.1.0 was changed specifically to stop trusting the ref that
`session-preflight` still trusts.** Whichever is right, they cannot both be.

## The failure mode, and it is not symmetrical

The interesting case is a coordinator whose local `main` is **ahead** of `origin/main` — the normal
state for a CTO holding coordination commits before a trunk flush. In this repo local `main` was
**51 commits ahead** of `origin/main`. Then, for a worktree agent:

- **`session-preflight`** compares against local `main`, sees those 51 commits absent from the
  branch, and **fails: "Branch is 51 commits behind main"**;
- **`worktree-sync --auto`** fetches and merges `origin/main`, which the branch already contains, and
  reports **"already up to date"**.

The agent is told it is behind, runs the tool prescribed to fix it, the tool says there is nothing to
do, and the preflight still fails. The only way out is to understand that two tools mean different
things by `main` — which is not discoverable from either message.

**The remedy is a decision the agent may not take.** Clearing the preflight requires the coordinator
to push `main`, and in this repo the trunk flush is explicitly reserved to the principal. So a
blocking check can be held red by a decision nobody in the loop is allowed to make, with no message
saying so. It also produced a real merge conflict on unrelated files (instinct frontmatter) when an
agent tried to satisfy it by merging local `main`.

## Why it matters beyond the inconvenience

This is the fifth defect in three days in this repo where **a tool derives a correctness-relevant
answer from ambient state rather than from the thing it is describing** — see the monitor-identity,
receipt-verification, quality-config, and monitor-registry reports filed alongside. Here the ambient
state is *which ref happens to be named `main` in this working copy*, and the two consumers of that
name resolved it differently.

## Suggested fixes, in order

1. **Make `session-preflight` use the same resolution as `worktree-sync`** — fetch and compare
   against `origin/$MAIN_BRANCH`. `worktree-sync`'s comment is already the argument for this.
2. **Say which ref was used, in both messages.** "Branch is 51 commits behind **local** main
   (origin/main is at `df89f50`)" is actionable; "behind main" is not.
3. **Distinguish "behind the trunk" from "behind an unpushed local trunk."** The second is not the
   agent's problem and should not read as its failure — name the coordinator, or downgrade it to a
   warning.
4. If the two are meant to differ, **document the difference where an operator will hit it**, because
   the current behaviour teaches that running the prescribed fix does nothing.

## Cross-reference

Reported by the `aviary-biosim` agent alongside two others worth noting: `git-safe-commit --finding`
is not repeatable (only the last trailer lands, so a commit body citing five findings shows one), and
there is **no `pr-submit` tool or skill in 0.56.0** — agents are hand-rolling the dispatch equivalent.
