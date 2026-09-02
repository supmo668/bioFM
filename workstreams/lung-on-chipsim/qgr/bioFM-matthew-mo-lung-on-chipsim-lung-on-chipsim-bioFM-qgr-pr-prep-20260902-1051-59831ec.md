---
receipt_version: 1
type: qgr
boundary: pr-prep
org: bioFM
principal: matthew-mo
agent: lung-on-chipsim
workstream: lung-on-chipsim
project: bioFM
diff_base: origin/main
hash_a: 5294b2a327032b8c1c5643793f4b514847001da2f6bdc633770d6fd31428ec31
hash_b: 67b7b11f966f1e286ded9115528c696f52cfe702010bf9909b13dfd66e2c8580
hash_c: 7ea6ecd89dccedb58238512be8fce1123f4bd4f03ca0588cbaf6cbb4c2017f4c
hash_d: 7ea6ecd89dccedb58238512be8fce1123f4bd4f03ca0588cbaf6cbb4c2017f4c
hash_d_source: "auto-approved for the fix cycle; principal 1B1 rulings recorded in A and D r1.1 D3a/F2a"
hash_e: 59831ecb39fa481a7777eeec0b5e2430f02cd310ac7ba606dd3b3c0b980c537a
date: 2026-09-02T10:51
---

# Receipt: pr-prep — bioFM

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): 5294b2a — artifact entering the gate
- E (final):    59831ec — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  67b7b11
- C (triage):    7ea6ecd
- D (principal): 7ea6ecd — auto-approved for the fix cycle; principal 1B1 rulings recorded in A and D r1.1 D3a/F2a

## Review Summary
P0.7 pr-prep over the branch tip: covers slice-1, the S12 run journal plus its tests, the chipsim-lbm-audit A and D r1.1, and the dev-log. r1.0 was written by a concurrent session without the principal 1B1 rulings; r1.1 folds them in - D3a per-target Spearman delta-rho with two shuffle tiers and a three-region verdict, F2a four-axis distal matching with a stability sanity check. 330 passed / 6 skipped offline, 15 / 1 network, ruff clean.
