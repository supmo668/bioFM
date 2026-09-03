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
