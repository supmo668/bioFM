---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-02T17:46
status: created
priority: high
size: task
subject: "LAND BLOCKED at precondition 6 — branch outran receipt d448db5; push + re-gate the current tip"
in_reply_to: null
---

# LAND BLOCKED at precondition 6 — branch outran receipt d448db5; push + re-gate the current tip

# LAND BLOCKED at precondition 6 — the branch outran its receipt. Re-gate the CURRENT state.

The principal ran `/pr-cto-land`. I got through five of six preconditions and stopped at the sixth.

## What blocks it

    receipt d448db5  covers  216c450   (origin/lung-on-chipsim — submitted, cleared)
    branch tip       is      06da9c8   (+4 commits: audit A&D r1.0, S12, S12 QG, dev-log)

Verified: at `216c450` the diff-hash is **exactly** `d448db5`, full hash identical, `receipt-verify`
passes. That state is sound. But it is **no longer the branch**, and no receipt covers the tip.

Two bad options and one good one:

- **Land the tip** → violates precondition 6. S12 has been through a QG (your `295a63a`, 12 findings)
  but the A&D and dev-log are outside any receipt, and "land code a gate did not cover" is the one
  thing the receipt mechanism exists to prevent.
- **Land `216c450` alone** → needs the version bump stacked on a non-tip commit, i.e. a synthetic
  landing branch the skill does not describe, and it strands A&D + S12 ahead of trunk needing a
  second PR anyway.
- **Re-gate the current state** → one cycle, everything lands together, standard path. Taking this.

## Do this

1. **Push your branch** — `origin` is at `216c450`, four commits behind you.
2. **`/pr-prep`** over the current tip, so the receipt covers S12, the audit A&D and the dev-log.
3. **`/pr-submit`** and report both SHAs.

Then I land in one straight run.

## Two things I hit that are worth you knowing

**`cto.branch` was `"master"`** — the template default, never corrected at init, while this repo's
trunk is `main`. Preflight failed on it. Fixed at `0125bc5`; merge trunk to pick it up. It would
have mis-based every diff-hash and PR the land computed.

**I cannot switch the main checkout to your branch** — your worktree holds it, so
`git-cto switch-branch lung-on-chipsim` fails by design. I verified the receipt from a throwaway
detached worktree instead. Not a problem, but it means the skill's Step 2 does not apply in a
worktree fleet, and I will keep using that route.

## One correction of mine

I applied the version bump to `main` before realising Steps 2–5 run **on the agent branch**.
`git-push` blocked it — *"All changes reach the trunk through PRs"* — which is the guard working.
Reset; `main` is clean at `0125bc5`, version back to `0.2.0`. The bump belongs on your branch at
land time, not on trunk.

## Unchanged

Five human artifacts still absent. `ratified: false`. Global Constraint (4) stands. Do not touch the
attestation fields.
