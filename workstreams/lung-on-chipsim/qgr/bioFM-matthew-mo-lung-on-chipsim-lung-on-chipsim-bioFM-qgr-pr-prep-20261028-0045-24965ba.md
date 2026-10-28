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
hash_a: 24965ba90b7e8c5c2c932a7a151408fe7cdd36c0b5637cb55b0c1e1b6d45857d
hash_b: 2df59b1e983184d4755d429d5ab6aa0ec138e55d34aaca621c050b296e1f3036
hash_c: 7ca84e41978e8a8fd3bf5bc53bd012ac99c9a0e7bfcdbeba31964b361f2f70b7
hash_d: 7ca84e41978e8a8fd3bf5bc53bd012ac99c9a0e7bfcdbeba31964b361f2f70b7
hash_d_source: "transcript — CTO rulings at approvals rows 65 and 67 after the agent refused to sign the failed gate; principal's five-item ratification at row 66"
hash_e: 24965ba90b7e8c5c2c932a7a151408fe7cdd36c0b5637cb55b0c1e1b6d45857d
date: 2026-10-28T00:45
---

# Receipt: pr-prep — bioFM

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): 24965ba — artifact entering the gate
- E (final):    24965ba — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  2df59b1
- C (triage):    7ca84e4
- D (principal): 7ca84e4 — transcript — CTO rulings at approvals rows 65 and 67 after the agent refused to sign the failed gate; principal's five-item ratification at row 66

## Review Summary
PR gate re-run after the HOLD ruling: output-root guard wired + 14-test registry (AST-discovered), work-tree anchoring with NoWorkTreeError, four identifier-gate vacuity holes closed, ruff format step restored. 866 passed / 4 skipped / 0 failed unselected; 835/4/31 selected; ruff format --check and ruff check both clean; ty 25 chipsim / 31 tests.
