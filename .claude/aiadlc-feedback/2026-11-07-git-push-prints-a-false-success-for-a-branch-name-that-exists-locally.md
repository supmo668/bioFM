---
type: plugin-feedback
date: 2026-11-07
from: biofm/matthew-mo/lung-on-chipsim
plugin_version: airdlc 0.87.0 (tools/git-push)
area: >
  tools/git-push — (1) its final "✓ Pushed <b> to origin" is printed UNCONDITIONALLY, after a push
  that moved nothing, and names no SHA; (2) its `branch` argument is resolved as a LOCAL ref, so
  naming the intended REMOTE target silently pushes a stale local branch of the same name.
severity: manufactures-a-false-landed-claim (the agent reports pushed; the remote never moved)
relation: >
  Same family as #895's "precondition 4 tool-blocked on the known branch-name defect" and the
  `receipt-verify --require-pushed` case that resolved by branch name to the frozen archive. Those
  surfaced as a BLOCK. This one surfaces as a SUCCESS, which is strictly worse: a block stops you,
  a false ✓ sends you on.
---

# `git-push <name>` prints "✓ Pushed" when it pushed nothing, because `<name>` resolves to a stale local branch

## What happened

Four commits ahead of the remote, I ran the sanctioned push path naming my configured push target:

```
$ tools/git-push lung-on-chipsim-stage3
To github.com:supmo668/bioFM.git
   Everything up-to-date
branch 'lung-on-chipsim-stage3' set up to track 'origin/lung-on-chipsim-stage3'.
✓ Pushed lung-on-chipsim-stage3 to origin
```

`origin/lung-on-chipsim-stage3` stayed at `a080784d`. My HEAD was `868791c6`. **Nothing was pushed
and the tool said it was.** I only caught it because "Everything up-to-date" sat one line above a ✓,
which is a contradiction — had the local branch been one commit stale instead of four, the output
would have looked entirely normal.

## Mechanism, read from the tool

```sh
[[ -z "$BRANCH" ]] && BRANCH=$(git rev-parse --abbrev-ref HEAD)
...
git push -u origin "$BRANCH:refs/heads/$REMOTE_BRANCH"
...
echo "✓ Pushed $BRANCH to origin"
```

Two independent faults compose:

1. **`$BRANCH` is a local ref on the left of the refspec.** A local branch
   `lung-on-chipsim-stage3` exists here, pinned at `a080784d`. So the command pushed *that* ref,
   not my work. Naming the remote target you want is the natural reading of
   `git-push [branch]`, and it is the wrong one.
2. **The ✓ is unconditional.** It is outside any check of the push's effect, and it names no SHA, so
   it cannot distinguish "pushed 4 commits" from "pushed nothing".

## The adjacent trap, which is worse and which I did not trigger

`git-push` with **no argument** defaults to the current branch — here `lung-on-chipsim` — and pushes
it to `refs/heads/lung-on-chipsim`. In this repo that remote branch is the **FROZEN Stage-1 archive**
(`c04e7019`), which the handoff marks do-not-push. The ergonomic path (`git-push`, no args) therefore
aims at the one ref that must never move, while the explicit path (`git-push <target>`) silently
pushes a stale local ref. Both readings are wrong and neither says so.

## What a correct push took

`git-safe` has no branch-pointer write, so the only in-lane route was: a temp worktree on
`lung-on-chipsim-stage3`, `git merge --ff-only lung-on-chipsim` there (verified `a080784d` was an
ancestor of HEAD first), then `git-push lung-on-chipsim-stage3` from inside it. That worked —
`a080784d..868791c6` — and I then verified it the only way that actually settles it:

```sh
git merge-base --is-ancestor HEAD origin/lung-on-chipsim-stage3   # the real check
```

## Proposed fixes, cheapest first

1. **Make the ✓ report the outcome.** Capture the pre- and post-push remote SHA and print
   `✓ Pushed <b>: <old>..<new>` or `• No change: origin/<b> already at <sha>`. One line, and the
   false claim becomes impossible.
2. **Refuse an argument that is not the current branch** unless something like `--as <remote-ref>` is
   passed, or at least warn loudly when the named local ref is not an ancestor of HEAD. Today the
   stale-local-ref case is indistinguishable from success.
3. **Honour a configured per-agent push target.** There is no `push_target` key (`config get
   push_target` → not found), so the branch→remote mapping lives only in the handoff as prose. That
   is why naming the target by hand is the common move, and why it misfires.
4. **Block the frozen refs by name**, the way the trunk is already blocked, so a no-arg `git-push`
   cannot aim at an archive branch.

## Limits of this report

- **I did not push to `origin/lung-on-chipsim`** and did not test whether that would have been
  rejected as non-fast-forward. `c04e7019` and my HEAD may well be unrelated enough that git would
  refuse it — so the trap in the third section is read from the code path, **not** observed. Stated
  as a hazard, not as a measured failure.
- The branch-name defect itself is **already known** (#895, `receipt-verify --require-pushed`). The
  new part here is only that this instance **reports success** rather than blocking.
