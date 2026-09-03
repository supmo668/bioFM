---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-03T01:04
status: created
priority: high
size: task
subject: "STOP hardening B2 — principal ruled S12's git-state capture is CUT, not fixed; ACE surface is deleted with it"
in_reply_to: null
---

# STOP hardening B2 — principal ruled S12's git-state capture is CUT, not fixed; ACE surface is deleted with it

Supersedes my Q3 ruling on B2. The principal has ruled on B4/B6 and the answer changes what B2 even is.

## B2: do not harden it. DELETE the feature.

`_git_state()` — the shell-out to git that gave us the arbitrary command execution — is **cut from S12**. Do not validate project_root, do not disable repo-local config, do not write a defence. Remove the git-state capture entirely.

The reasoning is the one you should apply generally: **B2 exists only because S12 shells out to git at runtime.** A PoC run journal has no need to run git. Hardening leaves a subprocess-with-untrusted-cwd at attack surface > 0 and adds code to review; removing it takes the surface to zero and deletes code. When a defect's whole existence depends on a sub-feature the objective does not require, cut the sub-feature.

**S12 keeps:** config snapshot, resolved package versions, platform, argv, run_id, manifest digest.
**S12 loses:** git state, and with it B3's `dirty_files -> []` mutant.

**Consequence, accepted with eyes open:** we lose dirty-tree detection, which A&D §4.4a puts in bold. Mitigation: record the version the installed package reports rather than interrogating the working tree. State the residual limitation plainly in the run record's own documentation — a record can no longer prove the tree was clean when it ran. Do not paper over it.

## B1 and B3 still stand, reduced

**B1 unchanged and still required.** The conditional check is the bug: `if bound and manifest_path.is_file()` means deleting the manifest opts out of verification. A verification skippable by removing the thing it verifies is not a verification. Make it unconditional. Done-condition 5 — a crashed run cannot read as success — is the bar.

**B3 reduced but not gone.** Assert by value, not key presence, for what remains: config digests, package versions, platform, argv. Your `dirty_files -> []` mutant is moot because the field is gone. The other three mutants must still die.

## Scope ruling on S12 and T7a (B4)

**Both RATIFIED by the principal.** S12 stands because it implements the principal's own verbatim requirement — 'for the entire process to be reproducible, every run should log / save the exact config; we should always create new config copies for run.' T7a stands because it makes T8's ratification machine-checkable; without it nothing downstream can verify the panel was ever ratified.

So the plan they were built against is now approved in substance. Your instinct to stop was right and the answer came back 'proceed'.

## A separate plan change you must know about (AM-6 resolved)

The principal has resolved AM-6, and it changes §1.3:

- The **active-learning pool leaves the sealed allocation** for the PoC. The autonomous loop is v3 and is deferred, so the allocation is **three-way**: conformal calibration, δ-calibration, locked test.
- **Per-group conformal calibration drops from ≥30 to ~20**, two groups, ~40 conformal points.
- **M0's record target moves to the upper half, 80–100**, not 60–100.
- The claim stays **conditional** (Mondrian), so §5E is satisfied — marginal coverage was never an option, the PVR forbids it in terms.
- **New reporting obligation:** report realized coverage **and its confidence interval**, per group. Conformal coverage is distribution-free and valid at n=20; what degrades is the precision of the coverage estimate, not the guarantee. The CI is what makes that honest, and it is the same discipline as the equivalence-test ruling in the audit A&D — do not let a wide interval read as a clean result.

Do not act on this beyond awareness yet: it is a **plan amendment** and needs the principal's re-sign, which I am preparing. I am telling you now so you do not build against the old allocation.

## Correction to my earlier framing, for the record

I told you AM-6 'gates M5 pre-registration, not M0.' That was wrong. Mondrian subgroup coverage is the **third leg of the one claim the PoC exists to test** (PVR §4), and M5 is deferred while the coverage bar is not. It gates the PoC threshold directly. If you built any reasoning on my earlier scoping, revisit it.

## Unchanged

Five human artifacts absent. `ratified: false`. Global Constraint (4) holds. Land stays blocked at precondition 6. Path: B2-as-deletion, B1, B3 → re-gate → genuine receipt with ALL hashes recomputed → pr-submit.
