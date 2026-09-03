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
date: 2026-09-03T02:08
---

# Plan approval: lung-on-chipsim

The human's 1B1 "Over and out" lock in /grill-me IS the final human
plan-review gate. This file records it so /build can verify it.

## Summary
r2.7 — approved by the principal in a `/grill-with-docs` 1B1 on 2026-09-02 and signed on his
explicit instruction ('sign the plan', 2026-09-03). Covers: AM-6 resolution (three-way PoC sealed
allocation, ~20 conformal points per group, M0 record target narrowed to 80-100, the claim stays
conditional, every coverage figure reports its CI per group); S12 records no git state (ADR-0001)
with the cost stated plainly; seed capture; T7a TTY gate as Global Constraint (4)'s first technical
enforcement; diff and veto state removed from the record spec; the replay test defined as a
two-meaning term. T7a and S12 both ratified. See the provenance block below: this file has been
re-signed by the CTO since the principal's original G4 approval, and two CA tasks were added
after it.

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

## Restoration note (worktree agent, 2026-09-03)

At `02:08` this file was rewritten by a re-sign that **dropped all five disclosure fields and the
provenance block above**, leaving a summary reading "approved by the principal, in-session" with no
route distinction — i.e. reading as a direct human approval. That is precisely the conflation B4
identified and the disclosure exists to prevent.

Two things worth recording, because both are the point:

1. **`plan-gate verify` still passed, before and after.** The hash was unchanged, so the gate could
   not see the regression. The disclosure was the only thing that could — which is exactly why B4
   was filed against the marker and not against the hash.
2. **The removal was captured by this agent's commit `26b6780`** via `git add -A`, under its
   authorship, in a commit whose message did not mention it. Restored here in full and reported to
   the CTO rather than quietly re-added.

The `02:08` timestamp and the re-sign's summary content are preserved; only the disclosure is
restored.
