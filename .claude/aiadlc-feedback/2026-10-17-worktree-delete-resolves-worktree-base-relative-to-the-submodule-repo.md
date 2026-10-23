# `tools/worktree-delete` resolves `paths.worktree_base` relative to the submodule repo, so it cannot find sibling worktrees

**Date:** 2026-10-17
**Found by:** biofm/matthew-mo/aviary-biosim (dispatch #661); relayed + filed by biofm/matthew-mo/cto
**Plugin:** airdlc 0.82.0
**Severity:** medium — the sanctioned retirement path is unusable in a submodule repo; the agent had to fall back to raw git

## What happened

Retiring the merged `whitepaper` worktree after Aviary-BioSim PR #2 landed, the owning agent ran
`tools/worktree-delete` from inside the submodule checkout. It resolved `paths.worktree_base`
**relative to the submodule repo** and looked for the worktree at:

```
.../worktrees/aviary-biosim/worktrees/<name>
```

i.e. it joined the configured base onto the submodule's own root. The real sibling worktree is at
`.../bioFM/worktrees/aviary-biosim-272-scratch`, one level up, so the tool could not find it and the
delete could not proceed.

**The agent fell back to `git worktree remove` directly** and completed the retirement correctly
(worktree removed first, then the local branch deleted with `-d` as a fully-merged check). So the
outcome was right — but it was reached by bypassing the tool that exists to get the ordering right.

## Why it matters

1. **The guarded path is the one that encodes the ordering rules.** `/pr-cto-land` Step 11 leans on
   `worktree-delete` precisely because it is submodule-aware and honours remove-worktree-before-
   delete-branch and `worktree prune` afterwards. When it fails to resolve, every agent hand-rolls
   raw git at the exact moment the ordering matters most.
2. **It fails by "not found", which reads like "already gone".** A path-resolution bug that
   presents as an absent worktree is the kind of false-clean this fleet keeps cataloguing: the
   operator cannot tell "nothing to do" from "looked in the wrong place".
3. **Config inheritance is the root.** In this monorepo the submodule has **no** `agency.yaml` of its
   own (deliberately — a local one would shadow the whole parent config, per the 2026-09-25 ruling),
   so `paths.worktree_base` comes from bioFM's config and is meaningful only relative to the
   **parent** repo root. Anything resolving a parent-scoped path against a submodule root will be
   wrong for the same reason.

## Proposed fix

Resolve `paths.worktree_base` against the repo that **owns the config** (the parent / superproject
root), not against `git rev-parse --show-toplevel` of wherever the tool happens to run. Where the
tool genuinely needs the submodule root, derive it explicitly (`--module-dir`) rather than inferring
it from cwd. Secondarily: when the computed path does not exist, say *which path was tried* instead
of reporting the worktree as absent — that single line would have made this self-diagnosing.

## Evidence

- Dispatch #661 (aviary-biosim → cto), 2026-10-17T17:14, verbatim: *"tools/worktree-delete resolves
  paths.worktree_base relative to the submodule repo (looked in .../worktrees/aviary-biosim/worktrees/<name>),
  so it cannot find sibling worktrees. I used git worktree remove directly."*
- Context: Aviary-BioSim PR #2 landed as merge `bece4dc`; parent gitlink bumped on bioFM `main` at `54e581d`.
- Submodule has no `agency.yaml` (verified during the land), so all config resolves up to bioFM's.
- Related: `2026-09-25-preflight-local-main-false-block.md` (the trunk-comparison class — same
  shape: a tool resolving a path/ref against the wrong repo root).
