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
hash_a: 5b2adcbf4136d47b5c4fe8954561e807984216b8cdfa07312cc61b8966ed0c26
hash_b: 2df59b1e983184d4755d429d5ab6aa0ec138e55d34aaca621c050b296e1f3036
hash_c: 82b2d769940d0084071a09589c02654dffa7f68960fc779e3861058ec43f6c77
hash_d: 82b2d769940d0084071a09589c02654dffa7f68960fc779e3861058ec43f6c77
hash_d_source: "transcript — CTO rulings rows 65/67/71; review stage carried from receipt 24965ba over byte-identical code, disclosed in Hash C"
hash_e: 5b2adcbf4136d47b5c4fe8954561e807984216b8cdfa07312cc61b8966ed0c26
date: 2026-10-28T01:30
---

# Receipt: pr-prep — bioFM

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): 5b2adcb — artifact entering the gate
- E (final):    5b2adcb — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  2df59b1
- C (triage):    82b2d76
- D (principal): 82b2d76 — transcript — CTO rulings rows 65/67/71; review stage carried from receipt 24965ba over byte-identical code, disclosed in Hash C

## Review Summary
Re-gate after the land abort: trunk merged, approvals resolved as the union 65-70, code byte-identical (measured). 866 passed / 4 skipped / 0 failed unselected; 835/4/31 selected; ruff format --check and ruff check both clean; ty 25 chipsim / 31 tests. Reviewer stage carried forward, not re-run, and stated.
