---
receipt_version: 2
type: qgr
boundary: pr-prep
org: bioFM
principal: matthew-mo
agent: lung-on-chipsim
workstream: lung-on-chipsim
project: bioFM
diff_base: origin/main
hash_a: e612aff2a22350106af9ec176f8d2fab4b6e7bd025a510d5ad82e6fc807dfbcc
hash_b: 2df59b1e983184d4755d429d5ab6aa0ec138e55d34aaca621c050b296e1f3036
hash_c: 4cb4db742c4eebb40b91f4dbd2a7cd75778dac33fa444e74263bb22161861dcc
hash_d: 4cb4db742c4eebb40b91f4dbd2a7cd75778dac33fa444e74263bb22161861dcc
hash_d_source: "transcript — CTO rulings rows 65/67/71/72; review stage carried from 24965ba, disclosed in Hash C"
hash_e: e612aff2a22350106af9ec176f8d2fab4b6e7bd025a510d5ad82e6fc807dfbcc
date: 2026-10-28T01:51
---

# Receipt: pr-prep — bioFM

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): e612aff — artifact entering the gate
- E (final):    e612aff — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  2df59b1
- C (triage):    4cb4db7
- D (principal): 4cb4db7 — transcript — CTO rulings rows 65/67/71/72; review stage carried from 24965ba, disclosed in Hash C

## Review Summary
Re-gate after the CI abort: floor page registered, snapshot integrity made non-vacuous in CI via option (c). 867 passed / 4 skipped / 0 failed unselected; 836/4/31 selected; simulated-CI 835/5/31 with 0 failed; ruff format --check and ruff check clean; ty 25 chipsim / 31 tests. STATED GAP in Hash C: byte-level snapshot integrity unverified without the DVC bytes, including in CI.
