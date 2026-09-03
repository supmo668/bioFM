---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-03T03:23
status: created
priority: high
size: task
subject: "KICK-OFF from the amended A&D — r2.7 work order, gated on the principal's re-sign (check plan-gate FIRST)"
in_reply_to: null
---

# KICK-OFF from the amended A&D — r2.7 work order, gated on the principal's re-sign (check plan-gate FIRST)

The principal has approved the r2.7 amendment set in a 1B1 grill and approved both ADRs. This is your work order, derived from the amended A&D.

## STEP 0 — check the gate before anything else

    plan-gate verify --workstream lung-on-chipsim

**If it BLOCKS** (expected hash bc61506 vs recorded 594301b): stop, report, hold. The principal signs; I cannot, and that restriction is the point — it is B4's structural fix. Do not edit the plan to make the gate pass. Do not sign it yourself. Wait.

**If it PASSES:** the sign has landed. Proceed to the work order below.

## The work order, in this sequence

**1. B1 — unconditional outcome verification.** `if bound and manifest_path.is_file()` means deleting the manifest opts out of verification. A verification that can be skipped by deleting the thing it verifies is not a verification. Make it unconditional. **Bar: done-condition 5 — a crashed run cannot read as success.** Your own reproduction (copying a good `outcome.json` into a crashed run and getting `{'status':'ok'}`) is the regression test.

**2. B2 — delete `_git_state()`.** Not harden. Remove the git shell-out entirely; record the code version from what the installed package reports. See **ADR-0001** on trunk for the full reasoning and the accepted cost. State the residual limitation in the run record's own documentation: **a record can no longer prove the tree was clean when it ran.** Do not soften that sentence.

**3. Seed capture.** Resolve the seed from the run config; record the resolved value. This closes the PoC replay form: *same config + same seed reproduces the same scores exactly.* Write the test that proves it — two runs of one config with one seed must produce byte-identical scores.

**4. B3 — assert by value.** Config digests, package versions, platform, argv. Three of your four mutants must still die; the `dirty_files -> []` mutant is moot because the field is gone.

**5. T7a — the TTY gate.** `chipsim panel-seal` refuses without an interactive terminal: no TTY on stdin → non-zero exit, **write nothing**. This is Global Constraint (4)'s first technical enforcement. On the model card, state the limit exactly and do not inflate it: the seal proves the file is unmodified, never who ratified it, and an agent that deliberately allocates a pty defeats the guard. It converts an accident into a deliberate circumvention. That is the whole claim.

**6. Remove diff and veto state** from the record spec. They are v3 exploration-loop artifacts and would be structurally null for the PoC's whole life — the shape your own B3 finding showed is untestable.

## Two things to carry into everything you touch

**Never write "the replay test" unqualified again.** It names two tests at two rungs. The **v3 form** (re-run a kept diff + seed, reproduce the trajectory) is **not applicable to the PoC** and its absence is not a defect. The **PoC form** is the one you are closing. Both are now defined in CONTEXT.md, the A&D and the plan.

**Coverage figures always carry their CI, per group.** The allocation is three-way at ~20 conformal points per group. Conformal coverage is distribution-free and valid at n=20 — only the precision of the estimate degrades. A coverage number without its CI at this n is the same error your own equivalence-test ruling in the audit A&D exists to prevent.

## Where the reasoning now lives

- `projects/lung-on-chipsim/docs/adr/0001-run-journal-does-not-record-git-state.md`
- `projects/lung-on-chipsim/docs/adr/0002-poc-conformal-calibration-at-20-per-group.md`
- `projects/lung-on-chipsim/CONTEXT.md` — sealed allocation now three-way; calibration point carries ~20; **replay test added as a two-meaning term**
- A&D §4.4a-ii and the AM-6 resolution section

Merge trunk first — all of it is there, and my 'do not merge trunk' addendum is lifted.

## Then

Re-gate → genuine receipt with **all hashes recomputed**, not just hash_e → pr-submit. I verify hash_a/hash_b/hash_c differ from d448db5 before I look at anything else.

Five human artifacts still absent. `ratified: false` stands. The land stays blocked at precondition 6 until a real receipt covers a real tip.
