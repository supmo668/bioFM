---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-03T20:10
status: created
priority: high
size: task
subject: "Land is one re-gate away — version bump landed FIRST this time (framework deadlock, explained); then A&D phase follow-up on chipsim-lbm-audit"
in_reply_to: null
---

# Land is one re-gate away — version bump landed FIRST this time (framework deadlock, explained); then A&D phase follow-up on chipsim-lbm-audit

Two threads: finish the land, then back to the A&D.

# 1 — Land: re-gate over the bumped tip

**Receipt cd36fc0 verified independently.** A/B/C (`e38ed46` / `1cf06d0` / `17bd53b`) distinct from BOTH prior receipts; `receipt-verify` passed; `diff-hash --base origin/main` returned cd36fc0 exactly. Your work is good and I pushed the branch.

Then `pr-create` blocked, and the reason is a framework defect rather than anything you did:

    BLOCKED: Receipt Hash E does not match current code.
      Receipt: cd36fc0   Current: 679ee2c

**The documented land flow is internally unsatisfiable.** `pr-create` requires *both* (a) `framework.version` bumped against the default branch *and* (b) the receipt matching current code — while the skill's own Step 4 → Step 5 order bumps the version *after* the gate, which invalidates the receipt it then demands. Each requirement is right; the order makes them exclusive.

It is a **missed exclusion**, and the precedent is already in the tool. `diff-hash` deliberately excludes exactly this class:

    :(exclude,glob) …/qgr/**                  <- receipts
    :(exclude,glob) …/plan/plan-approval.md   <- the approval marker
    :(exclude,glob) …/dispatches/**           <- dispatch records

`agency.yaml` is a fourth instance of the same pattern and is not in the list. Filed upstream.

**Today's route out — and note the ordering, because it is the whole fix.** I have already bumped 0.2.0 → 0.3.0 and **pushed it (`f0bb4c1`)**. So re-gate over the tip **as it now stands**. The bump is *behind* the gate rather than ahead of it, which breaks the loop: gate → PR, with nothing mutating in between. I will not touch the branch again after your receipt.

Send the new receipt with A/B/C/E explicit as usual and I land in one straight run — CI, merge, v0.3.0 release, DevEx hand-off.

# 2 — A&D phase: chipsim-lbm-audit

Once the receipt is away, go back to `/design`. It is not complete and the A&D is **not approved** — that stands.

**R2 is answered, so the blocked item is unblocked:** seal the pre-registration with **OpenTimestamps**, committing the `.ots` proof. One command, free, no account, and a reviewer verifies priority without trusting us or GitHub. A pre-run push was rejected because commit timestamps are committer-set and forgeable — and the audit may well report a null, which is the claim a skeptic attacks on priority first. OSF stays available later at no cost to the timestamp.

**Fix before anything gets sealed — your own r1.1 findings.** You cannot timestamp a document that contradicts itself:

- **D3a is not a partition.** A CI of [0.00, 0.09] satisfies both *insensitive* and *inconclusive* while `classify` is required to be **total**. Make the three regions exhaustive and mutually exclusive, and say which boundary is closed.
- **R4 has no defined statistic.** `effect` appears exactly once in the document, at its point of use. Define it or R4 is untestable.
- The remaining internal contradictions you counted in r1.1.

**Then the outstanding 1B1 items with the principal:** R1's preflight floors, R5's cliff definition, R6's modality handling, R9/R10, and the Chai-1 arm. Chai-1 is geometry only and never scores — hold that line when you specify it.

**Carry forward into the audit design**, because they are the same discipline in a different domain:

- `insensitive` requires an **equivalence** test, not a significance test. A CI containing zero means *either* insensitive *or* underpowered, and those are as different as `no` and `unknown` in the P-gp label.
- The **distal control can break silently** — distance alone selects buried structural residues, so mutating them destabilises the fold and inflates the control arm while reading as a small difference rather than a broken comparator.
- **Per-target Δρ, never pooled.** The parent PVR forbids aggregate-only reporting.
- **Every coverage figure carries its CI, per group** — the ~20/group allocation makes this binding, not optional.

Five human artifacts absent. `ratified: false`. The land does not move any of that.
