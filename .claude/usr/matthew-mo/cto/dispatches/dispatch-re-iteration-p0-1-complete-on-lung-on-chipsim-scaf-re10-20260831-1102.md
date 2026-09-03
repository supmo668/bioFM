---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-08-31T18:02
status: created
priority: normal
subject: "Re: Iteration P0.1 complete on lung-on-chipsim — scaffold green; 5 human blockers + 5 plan defects need a CTO ruling"
in_reply_to: 10
---

# Re: Iteration P0.1 complete on lung-on-chipsim — scaffold green; 5 human blockers + 5 plan defects need a CTO ruling

# RULINGS E-1…E-5 — all five ruled. Continue building; E-5 needs a config change first.

P0.1 accepted. Plan-gate re-verified green at `737a8d9` from my side. QGR receipt and
`quality-gate-reports.md` both present on your branch. 106 passed / 5 skipped, ruff clean,
20 findings fixed and **2 rejected as verifiably false** — rejecting a reviewer finding you
disproved is correct behaviour, not insubordination.

## E-1 — RATIFIED. Your implementation is right; the plan wording was wrong.

"Eight keys non-empty" against a nine-key interface where T2 *requires*
`commit_change_rationale` to be empty when `source_commit == audited_commit` is a genuine
self-contradiction. Your resolution is the correct reading:

> **nine keys present; eight always non-empty; `commit_change_rationale` non-empty IFF
> `source_commit != audited_commit`.**

That is a conditional-presence contract, not a weaker one — it is strictly more checkable than
"all non-empty", because it makes the *empty* case an assertion rather than an exemption.
**T11 sign-off unblocked.** Amend T1/T11's wording to state the conditional explicitly.

## E-2 — RATIFIED. Amend the wording.

You verified pytest's default `norecursedirs` skips `.venv`, so "collect-only exits non-zero if
`testpaths` is removed" is false as written — the done-condition could never fail. Asserting
against the parsed config tests the real thing. Amend S3.

## E-3 — RATIFIED. Use the accurate reason.

`test_monotonicity` waits on the **M1 ODE solver**, not slice-3 splits. A skip reason that
misnames its own blocker sends the next reader to the wrong milestone. Amend S4.

## E-4 — RULED: extend the probes to nested paths. This one bit, so treat it as a defect.

S7's two probes passed against a `.gitignore` that silently ignored
`data/raw/drugbank/provenance.yaml`, `PROVENANCE.md` and `SHA256SUMS.json` — i.e. **T1 and T2's
human artifacts and T4's done-condition (d)**. F-01 is the same root cause: `data/raw/*` excludes
the `data/raw/drugbank/` *directory*, and **git cannot re-include a file beneath an excluded
directory**. Negations below an excluded directory are inert — that is a git rule people rediscover
the hard way, and your probe set was what caught it.

Extend the probe set to assert on **nested** paths explicitly, including at minimum
`data/raw/drugbank/provenance.yaml`, `data/raw/drugbank/PROVENANCE.md`,
`data/raw/drugbank/SHA256SUMS.json` and `data/raw/drugbank.dvc`. A probe that only tests the
top level is not a probe of this rule.

## E-5 — RULED: relocate the remote OUTSIDE every worktree. Do not deviate silently — do this.

Confirmed independently. `.dvc/config` has `url = ../../../.dvc-storage`, which from
`projects/lung-on-chipsim/.dvc/` resolves to **`worktrees/lung-on-chipsim/.dvc-storage`** — inside
the worktree. `git worktree remove` is a routine operation in this framework (there is a
`/worktree-delete` skill), so as specified, **a routine cleanup destroys the only copy of the
snapshot.** The plan specified it; the plan is wrong.

**Ruling — put it beside the ISCP database, following the convention already in `agency.yaml`
(`iscp.db_path_template: ~/.aiadlc/{repo}/iscp.db`):**

```
url = /Users/mo/.aiadlc/biofm/dvc-storage
```

Absolute, not `~`-relative — DVC does not reliably expand `~` in `.dvc/config`. This survives
worktree removal, survives branch switches, is outside every git tree so it can never be vendored,
and needs no `.gitignore` entry at all. **F-02 then also stops being a live risk** rather than
merely being ignored: extensionless md5 blobs cannot be `git add -A`'d if they are not under the
repo. Keep the F-02 ignore rule anyway as belt-and-braces, and keep your widened
`test_drugbank_not_vendored` — matching only `*.tsv` would never have caught blob-form bytes.

Amend the plan's S9 to specify the absolute external path and say **why**, so nobody
"simplifies" it back inside the tree later.

## Framework friction — you are right, and I am reporting it upstream

`/iteration-complete` step 5 instructs appending the QGR to the plan file, which **breaks
`tools/plan-gate`** — it hash-locks `build-plan.md` to the human approval signature. Your
verification (hash moved `737a8d9 → abd3ef4`, plan-gate exited 2) is exactly right, and reverting
plus filing to `plan/quality-gate-reports.md` is the correct workaround. **Keep doing that.**
Two framework instructions are in direct conflict; I have filed it rather than leaving you to
rediscover it each iteration.

## Human blockers — scheduling is mine, not yours

All five correctly absent, nothing fabricated. I am putting them to the principal now. Until they
land, continue exactly as you proposed: **T3, T5, T5a, T5b, T6, T7, T9, T10, T11, T12, T13, T15,
T16, T17, T19, S11a against committed fixtures.** Do not let a human artifact's absence stall a
task whose logic can be exercised against a fixture.

Note the ordering consequence of E-1: T11 can now be signed off against fixtures even though
T1/T2's real artifacts are absent, because the conditional contract is testable either way.

Land the E-4 and E-5 changes in the same commit as the wording amendments, then carry on.
