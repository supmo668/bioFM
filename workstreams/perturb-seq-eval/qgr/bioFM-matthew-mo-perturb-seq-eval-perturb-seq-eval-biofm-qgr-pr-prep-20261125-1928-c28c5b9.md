---
receipt_version: 2
type: qgr
boundary: pr-prep
org: bioFM
principal: matthew-mo
agent: perturb-seq-eval
workstream: perturb-seq-eval
project: biofm
diff_base: origin/main
hash_a: d3db273a40af2082f30974b5080da5be1d110ac54ca26f3bbd16aa31ee50ae31
hash_b: c6bedbe08902439a407f15c82b950752306383aef198ba801a444097b38cef6d
hash_c: a086cc1b004c70c59f73a9f5c4f9bed2bb89942b153bf2708ae4475e8d366aee
hash_d: a086cc1b004c70c59f73a9f5c4f9bed2bb89942b153bf2708ae4475e8d366aee
hash_d_source: "auto-approved — no principal 1B1"
hash_e: c28c5b92a147f7c2a5cb3857b925c8632e479db0f730779bb5e8b5e722d8588d
test_result: pass
date: 2026-11-25T19:28
---

# Receipt: pr-prep — biofm

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): d3db273 — artifact entering the gate
- E (final):    c28c5b9 — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  c6bedbe
- C (triage):    a086cc1
- D (principal): a086cc1 — auto-approved — no principal 1B1

## Review Summary
HACA-141: Zenodo 0.6.1/0.6.2/0.6.3 isIdenticalTo Figshare v7/v8/v9 recorded as done on CITATION (root+module), CHANGELOG, README, SUBMISSION; test pins. 7 findings, 2 >=80 (F1, F5) fixed, F6 fixed below threshold; tests 1161 passed, 15 skipped; reviewer-ux: skipped (not-user-facing)
