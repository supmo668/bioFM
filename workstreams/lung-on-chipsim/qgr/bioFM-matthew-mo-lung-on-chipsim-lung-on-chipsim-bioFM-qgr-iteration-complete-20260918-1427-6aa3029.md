---
receipt_version: 2
type: qgr
boundary: iteration-complete
org: bioFM
principal: matthew-mo
agent: lung-on-chipsim
workstream: lung-on-chipsim
project: bioFM
diff_base: 23a161f
hash_a: 6aa30299bd3e917139c9cab3cfe1c64eb27d9d1c4170108f5a07741f99a3480c
hash_b: ddd36cccdf66d8b82abae3c0118608264041c365e405a5e221f07951009dd67a
hash_c: ddd36cccdf66d8b82abae3c0118608264041c365e405a5e221f07951009dd67a
hash_d: ddd36cccdf66d8b82abae3c0118608264041c365e405a5e221f07951009dd67a
hash_d_source: "CTO ruling r2.34, signed 4e4aff5"
hash_e: 6aa30299bd3e917139c9cab3cfe1c64eb27d9d1c4170108f5a07741f99a3480c
date: 2026-09-18T14:27
---

# Receipt: iteration-complete — bioFM

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): 6aa3029 — artifact entering the gate
- E (final):    6aa3029 — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  ddd36cc
- C (triage):    ddd36cc
- D (principal): ddd36cc — CTO ruling r2.34, signed 4e4aff5

## Review Summary
S18: r2.34 implemented - is-an-ETL-run and may-be-invoked-unattended stop sharing a tuple, with each non-node command recording its own reason. Includes a measured correction to the ruling's severity: T13 was node-ELIGIBLE, never actually exported.
