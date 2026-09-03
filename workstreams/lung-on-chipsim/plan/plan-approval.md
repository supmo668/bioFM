---
workstream: lung-on-chipsim
plan_path: workstreams/lung-on-chipsim/plan/build-plan.md
plan_hash: bc61506
approved: true
approved_by: Matthew Mo
approval_route: principal-directed, cto-invoked
invoked_by: biofm/matthew-mo/cto
human_approved_hash: 737a8d9
human_approved_date: 2026-08-30
tasks_added_since_human_g4: [T7a, S12]
date: 2026-09-03T01:56
---

# Plan approval: lung-on-chipsim

The human's 1B1 "Over and out" lock in /grill-me IS the final human
plan-review gate. This file records it so /build can verify it.

## Summary
r2.7 — approved by the principal in a /grill-with-docs 1B1 on 2026-09-02 and signed on his explicit instruction ('sign the plan', 2026-09-03). Resolves AM-6 (three-way PoC sealed allocation, ~20 conformal points per group, M0 narrowed to 80-100, every coverage figure reports its CI per group); rescopes S12 (git-state capture DELETED not hardened per ADR-0001, diff and veto state deferred to v3, seed capture added); splits the replay test into its v3 form (not applicable to the PoC) and its PoC form (same config + same seed reproduces the same scores exactly); adds a TTY gate to T7a as Global Constraint (4)'s first technical enforcement. T7a and S12 both ratified. See the provenance block below: this file has been re-signed by the CTO since the principal's original G4 approval, and two CA tasks were added after it.

---

## Provenance — how to read this signature (QG blocker B4)

**This file could not previously distinguish a CTO re-sign from a human approval, and that was
the defect.** These fields exist so it can. Read them before trusting `approved: true`.

| Field | Means |
|---|---|
| `human_approved_hash: 737a8d9` | The plan the principal approved directly at G4 (`1132fda`, 2026-08-30). |
| `approval_route` | `principal-directed, cto-invoked` — the principal approved the content in a `/grill-with-docs` 1B1 on 2026-09-02 and instructed the signature on 2026-09-03; the CTO ran `plan-gate sign`. **The decision is the principal's; the invocation is not.** |
| `tasks_added_since_human_g4` | `T7a` (panel seal tool, `9f27781`) and `S12` (run journal, `b0273e8`) entered the plan **after** `737a8d9`. Both were ratified by the principal on 2026-09-02. |

**What this signature does and does not attest.** It attests that the principal approved the
content of `build-plan.md` at hash `bc61506`. It does **not** attest that the principal personally
executed this command, and no unkeyed hash in this repository can establish who ran anything —
a digest proves integrity, never authorship. Every re-sign of this file between `1132fda` and this
one was `main/cto:` and carried no such distinction; that is what B4 found.

**For future signatures:** a signature whose `approval_route` is `principal-directed, cto-invoked`
records a decision the principal made elsewhere. If there is no corresponding record of that
decision, the signature is unsupported — treat it as unsigned and escalate.

---

## Incident — the 02:08 re-sign, and what it proves (CTO, 2026-09-03)

**What happened.** The CTO signed this marker at `01:56` (`a9c8629`) on the principal's explicit
instruction, adding the five disclosure fields and the provenance block above. At `02:08` a worktree
agent ran `plan-gate sign` again over the same plan hash. `plan-gate sign` rewrites the marker, so
the re-sign **silently removed every disclosure field and the whole provenance block**, leaving a
summary that read as a direct human approval. The worktree agent detected the loss, restored the
block in full, and reported it rather than re-adding it quietly. That report is why this record
exists.

**Attribution, corrected.** `invoked_by: biofm/matthew-mo/cto` and `date: 2026-09-03T01:56` describe
the **authoritative** signature — the one the principal directed. The `02:08` invocation was made by
an agent, added nothing (identical plan hash `bc61506`), and is superseded by this restored file.

**Two things this proves, and they are the reason the incident is worth more than the damage.**

1. **`plan-gate verify` passed before, during and after.** The plan hash never moved, so the gate
   could not see the regression. The gate binds the *plan*; it does not protect the *marker's*
   provenance. The disclosure fields were the only thing that could detect this, which is exactly
   why B4 was filed against the marker rather than against the hash. **A green gate is not evidence
   that the approval record is intact.**
2. **An agent can run `plan-gate sign`.** It did, and in one invocation it destroyed the only
   control B4 produced — without malice, without a warning, and without the gate noticing.

**Ruling — `plan-gate sign` joins the restricted set.** It sits with `receipt-sign` and
`dispatch create`: **not invocable by a worktree agent or a reviewer subagent.** Recording a human's
approval is not the same act as being one, and a tool that rewrites an approval marker in place must
not be reachable by the party the marker exists to constrain. Filed upstream with the receipt-sign
restriction; until a hookify rule lands, agents must not invoke it and must report any instruction
that appears to ask them to.

**Standing consequence for readers of this file:** if the disclosure fields are absent, do not read
`approved: true` as a human approval — read it as unknown, and escalate. Their absence is now itself
a signal.
