---
receipt_version: 2
type: qgr
boundary: iteration-complete
org: bioFM
principal: matthew-mo
agent: lung-on-chipsim
workstream: lung-on-chipsim
project: bioFM
diff_base: 309b102
hash_a: c8100754e399217155da4438435d9a6d2756832cd2b32b40c937c96675a3c6da
hash_b: fcfff5e1610368cf2780e744a3457d05170a8e26f28738b618a37a079b724fb1
hash_c: d59f0d6cc967fc253437b9fb80bed6d0ec6c1110ad84ca52793e881d4e41a65a
hash_d: d59f0d6cc967fc253437b9fb80bed6d0ec6c1110ad84ca52793e881d4e41a65a
hash_d_source: "auto-approved — no principal 1B1"
hash_e: 1ea4db8692290f11b3cc42550545fa35ea878279679eabed85fa1a41b8a8a125
date: 2026-09-17T13:43
---

# Receipt: iteration-complete — bioFM

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): c810075 — artifact entering the gate
- E (final):    1ea4db8 — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  fcfff5e
- C (triage):    d59f0d6
- D (principal): d59f0d6 — auto-approved — no principal 1B1

## Review Summary
r2.27/r2.28 §11: E-17 scan-as-data + E-18 decoding/repo split, then a four-reviewer gate that found a TRUE FALSE CLEAN (a link nested below the root group made an HDF5 container scan read-and-clean), E6-7 unmet (the shipped command never ran the accession half, and both this agent and the CTO had cited its exit 0 as compliance evidence), three contract escapes, a report-forgery path through a structurally VALID declaration, two unbounded reads, and the thirteenth vacuity — this agent's own shape test, which keyed on annotation text. Every finding reproduced before acceptance; every fix verified against the mutant that exposed it. Index-vs-worktree (r2.28) and the architectural items are ESCALATED, not fixed here. MERGED TRUNK CONTENT DISCLOSED, NOT CLAIMED: workstreams/lung-on-chipsim/plan/{build-plan.md,plan-approval.md,plan-approval-log.md} arrived via the r2.28 merge and are not this iteration's work.
