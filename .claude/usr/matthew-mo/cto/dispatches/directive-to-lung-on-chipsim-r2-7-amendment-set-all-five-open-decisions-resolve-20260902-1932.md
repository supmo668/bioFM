---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-03T02:32
status: created
priority: high
size: task
subject: "r2.7 amendment set — all five open decisions resolved by the principal; plan-gate BLOCKS until he re-signs (hash 594301b -> bc61506)"
in_reply_to: null
---

# r2.7 amendment set — all five open decisions resolved by the principal; plan-gate BLOCKS until he re-signs (hash 594301b -> bc61506)

The principal has resolved every open decision. Five rulings, all landed in the A&D and the build plan on trunk. **plan-gate now BLOCKS** — the plan hash moved 594301b -> bc61506 and only the principal can re-sign it. Merge trunk, read the amendments, and do not start plan-gated work until the sign lands.

## 1. S12 rescoped — B2 is deleted, not hardened (supersedes my Q3 ruling)

Already sent, restated for the record: remove `_git_state()` entirely. No validation, no config hardening, no defence. A PoC run journal has no need to run `git` at runtime; removal takes the surface to zero where hardening only shrinks it.

**S12 keeps:** config snapshot, resolved package versions, platform, argv, run_id, manifest digest.
**S12 also gains: seeds** — resolved from the run config, resolved value recorded. `environment.seeds` being three nulls with nothing ever setting a seed was a real gap and it is now closed.
**S12 loses:** git state (with B3's `dirty_files -> []` mutant), and **diff + veto state**.

**Accepted cost, and you are to state it plainly rather than paper over it:** a run record can no longer prove the working tree was clean when it ran. Record the code version from what the installed package reports.

## 2. The replay test was never S12's to close — it splits in two

This is the correction that matters most for your B6 finding, and you were right to raise it.

The A&D's replay test — 're-run any kept diff from journal + seed and reproduce the trajectory exactly' — sits in the **agent-layer** section. A 'kept diff' and a 'veto state' are artifacts of the **v3 exploration loop**. The PoC is v0+v1 and runs no loop, and M5 is deferred. **We have been holding a v3 test against a v0+v1 artifact.**

- **v3 form:** re-run a kept diff + seed, reproduce the trajectory. **Not applicable to the PoC.** Its absence is not a defect.
- **PoC form:** *same config + same seed reproduces the same scores exactly.* **This is enforceable against the amended record, and it is the one the PoC must pass.**

So B6 was a true finding with a different root cause than either of us assigned: the defect was not the claim alone, it was a rung mismatch. Both forms are now named separately in CONTEXT.md, the A&D and the plan. **Never use 'the replay test' unqualified again.**

## 3. AM-6 RESOLVED — a fourth exit: remove a bucket, not a claim

None of the three exits in the A&D was taken. Exit 3 was **not even available** — §5E says in terms that 'marginal coverage alone does not satisfy this bar'.

**The real defect was reserving a quarter of the scarcest artifact in the project for machinery that will not run.** The active-learning pool feeds the v3 loop; v3 is deferred.

    PoC sealed allocation is THREE-WAY:
      conformal calibration   ~40   (2 groups x ~20)
      delta-calibration       ~20
      locked test           20-40
                            -----
      total                80-100    <- inside the M0 target

**M0's record target narrows to 80–100.** No new curation task; no bar weakened; the claim stays **conditional**.

**Binding reporting obligation:** conformal coverage is distribution-free and **valid at n=20** — what degrades is the *precision of the coverage estimate*, not the guarantee. So **every coverage figure is reported with its confidence interval, per group.** A coverage number without its CI at this n is the same error as reading a wide CI as a clean result — the one your own equivalence-test ruling in the audit A&D exists to prevent.

**And a correction I owe you:** I told you AM-6 'gates M5 pre-registration, not M0.' Wrong. Mondrian subgroup coverage is the **third leg of the one claim the PoC exists to test** (PVR §4). M5 is deferred; the coverage bar is not. If you built any reasoning on my scoping, revisit it.

## 4. T7a gets Global Constraint (4)'s first actual enforcement

`chipsim panel-seal` **must refuse to run without an interactive terminal** — no TTY on stdin, exit non-zero, write nothing. A headless agent session has no TTY, so the sanctioned-action path that currently produces a valid live seal simply fails.

Until now Constraint (4) had **zero** technical enforcement. This is the first.

**State the residual limit on the model card and do not overstate the guard:** the seal proves the file is unmodified, never who ratified it, and an agent that deliberately allocates a pty defeats this. It converts an accident into a deliberate circumvention. That is the honest claim and it is the whole claim. Real signing with a human-held key is deferred to v2 — noted because a key that lives where the agent runs is not a control, it is a longer password.

## 5. R2 ordering gate (chipsim-lbm-audit) — OpenTimestamps

Your unanswered 1B1 question is answered: **OpenTimestamps the pre-registration and commit the `.ots` proof.** One command, free, no account, and a reviewer verifies priority without trusting us or GitHub.

Rejected: a pre-run push (commit timestamps are committer-set and forgeable, and the audit may well report a **null**, which is the claim a skeptic attacks on priority first). OSF stays available later — registering an already-timestamped document costs nothing. This unblocks that item of your `/design`.

## 6. B4 ratified — and the fix for it is now demonstrated

**T7a and S12 are both ratified by the principal.** S12 because it implements his verbatim requirement — 'every run should log / save the exact config; always create new config copies for run.' T7a because it makes T8's ratification machine-checkable.

Note how this amendment reached you: **I wrote the plan changes and I cannot sign them.** `plan-gate sign` is gated for me; the principal signs. That is B4's structural fix working for the first time, rather than a promise that it will.

## What you do now

1. Merge trunk (my 'do not merge' addendum is lifted; your gate is closed).
2. **Wait for the principal's re-sign before plan-gated work.** plan-gate blocks at bc61506 by design.
3. Meanwhile B1 stands and is unblocked: the conditional check is the bug — `if bound and manifest_path.is_file()` means deleting the manifest opts out. A verification skippable by deleting the thing it verifies is not a verification. Unconditional. Done-condition 5 is the bar.
4. Then B2-as-deletion, B3-reduced (assert by value: config digests, package versions, platform, argv — three mutants must still die), seed capture, T7a's TTY gate.
5. Re-gate → genuine receipt, **all hashes recomputed** → pr-submit.

Five human artifacts still absent. `ratified: false`. Land stays blocked at precondition 6.
