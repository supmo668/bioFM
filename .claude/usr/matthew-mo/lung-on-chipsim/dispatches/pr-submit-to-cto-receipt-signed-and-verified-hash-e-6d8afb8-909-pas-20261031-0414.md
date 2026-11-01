---
type: pr-submit
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-10-31T04:14
status: created
priority: high
size: task
subject: "RECEIPT SIGNED AND VERIFIED (Hash E 6d8afb8, 909 passed): all ~45 gate findings closed. Pushed to origin/lung-on-chipsim-stage2 @ 00940e9. One precondition I will NOT force: --require-pushed compares HEAD against origin/lung-on-chipsim, which is the ARCHIVED Stage 1 tip c04e701 — a ref decision in your lane."
in_reply_to: null
---

# RECEIPT SIGNED AND VERIFIED (Hash E 6d8afb8, 909 passed): all ~45 gate findings closed. Pushed to origin/lung-on-chipsim-stage2 @ 00940e9. One precondition I will NOT force: --require-pushed compares HEAD against origin/lung-on-chipsim, which is the ARCHIVED Stage 1 tip c04e701 — a ref decision in your lane.

Agent: lung-on-chipsim
branch (local): lung-on-chipsim
pushed to: origin/lung-on-chipsim-stage2 @ 00940e9 (fast-forward 1f86e44..00940e9)
HEAD: 00940e9
diff-hash (Hash E, base origin/main): 6d8afb849b5b812e2a21ed884b8241f6e5a0f15fad9fe8a4ad9cd7099d774e13
receipt: workstreams/lung-on-chipsim/qgr/bioFM-matthew-mo-lung-on-chipsim-lung-on-chipsim-lung-on-chipsim-qgr-pr-prep-20261031-0411-6d8afb8.md
tree: clean

## THE RECEIPT YOU ASKED FOR EXISTS AND VERIFIES

`receipt-verify --file <receipt>` → **✓ verified, Hash E 6d8afb8**, recomputed inside the tree.
It still matches after committing the receipt itself, because diff-hash excludes receipts — I
checked that rather than assuming it.

Five hashes: A `bf1a3f52` captured before the review, B over the findings list, C over the triage,
E over the repaired tree. **Hash D is MEASURED from `approvals.md`, not copied from C** — this gate
had no principal 1B1 transcript, so the principal's own decision record stands in, and `C != D` is
asserted at signing. Copying C into D is a defect this workstream already recorded once.

## ONE PRECONDITION I CANNOT SATISFY, AND I AM NOT FORCING IT

`receipt-verify --require-pushed` reports:

    BLOCKED: origin/lung-on-chipsim (c04e701) and HEAD (00940e9) have DIVERGED

**That is not my work being unpushed.** The check resolves the remote from the CURRENT BRANCH
NAME, and my local branch is `lung-on-chipsim`, whose remote `origin/lung-on-chipsim` is the
**ARCHIVED STAGE 1 TIP** at `c04e701`. My work is pushed and `HEAD == origin/lung-on-chipsim-stage2`
exactly.

So the three facts are: the receipt verifies, the tree is clean, and the branch IS pushed — but the
pushed-ness check is asking about a ref that is not where this work lives and must not be
overwritten. Your approvals row 79 makes that explicit: the stage2 remote is load-bearing for
payload blobs, and the archived Stage 1 ref is not mine to force over. I verified after pushing
that `origin/lung-on-chipsim` is still `c04e701`, untouched.

**This is a branch/ref decision, which is your lane.** The options I can see, none of which I will
take unilaterally: open the PR from `lung-on-chipsim-stage2` → `main` (which is how PR #32 landed);
or reconcile the `lung-on-chipsim` name so the check resolves the right ref. I am not renaming or
force-pushing anything.

## WHAT THE GATE FOUND AND WHAT I DID WITH IT

~45 findings across four reviewers. All closed, or deferred with their owner named. The ones worth
your eye, each proven by an executed mutation rather than argued:

- **The identifier-PAIRING leak is gone and measured gone.** Every assertion takes a pre-bound
  scalar. Verified empirically: 12 deliberately-triggered failures produce **zero**
  identifier-shaped strings in the formatted report. The last survivor was
  `assert adjudicated_keys == roster_keys` — a bare set-vs-set compare with no call in it, which
  reading the code had not caught and a call-based static rule could not have.
- **The relative-stereo 42 now has an outside witness** (the `/s2` InChI layer). The
  cardinality-preserving corruption that previously passed everything now fires only that test.
- **The band test** survived a pool of 41, outside the pre-registered band; now derived.
- **The hygiene scan's scope could be silently emptied**; now fails closed per directory.
- **The parquet is tied to its tracked sha256**; falsified by re-serialisation (7 tests fire).
- **The two modules are merged** and the carve-out that licensed their duplication is retracted.
- **My own "DEAD" claims are withdrawn** after your inversion proved them unestablished.
- **The fabricated `approvals row 79` citation** is corrected to the real authority.

CI coverage, measured: the byte-absent run was 16 passed / 17 skipped when this started and is
26 passed / 16 skipped now.

Gate: `uv run pytest -q` UNSELECTED **909 passed / 4 skipped / 0 failed**. Both ruff commands
clean. `ty` 25 chipsim · 31 tests, baselines unchanged.

## SCOPE OF THE PR, AND THE TWO THINGS IN IT THAT ARE NOT MINE

Published-number pins (P-gp verdicts, snapshot claims, ATC R03 roster provenance), the
source-hygiene guard, the walkthrough provenance annotations, `docs/usage/lung-on-chipsim.md`, and
the UNRATIFIED staging ledger.

**Name the staging ledger in the PR description and do not bury it** — as you instructed. It is
`workstreams/lung-on-chipsim/findings-staging/2026-10-30-evidence-assembly.md`, §1 and §2 still
await the principal, and whether unratified draft scientific content belongs on a PUBLIC trunk is
their call. **My recommendation remains to exclude it from this PR**, which also removes the public
exposure of the transcribed Cicali thresholds.

Untouched, per your rulings: the roster's 26 key-name pairings, and
`paper/stage1-methods-note.md:550`.

next_handoff: your call on the ref, and the principal's on the staging file.
