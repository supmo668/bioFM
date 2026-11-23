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
hash_a: 58aea200156dbe39ebdd6cec320a8114ad116e555ba6c654f86884bb540e3b2c
hash_b: 84d3de8bfc93ed6a721fa5d36f3b050b370847ecfe0fc3014477337ad2d545e6
hash_c: 7d067e6f07da0a7e186ad7834f1c274aebadc1fc81ccfcd3918dd925bc2389e1
hash_d: 9fd6f767c09e9c327967ac37eac1c9fb8cc7c700020649cbd091d7dd5877c257
hash_d_source: "CTO ruling HACA-119 comment 16ba31cd-b381-4d38-b038-99986aab9855 (option 2: 3 aarch64 host-baseline failures accepted, base 40c814f fails the same set)"
hash_e: c88614f01e1e148a7cb16f84f9056cf93151cb0188d3bc5452d403e86b434856
test_result: pass
date: 2026-11-23T03:17
---

# Receipt: pr-prep — biofm

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): 58aea20 — artifact entering the gate
- E (final):    c88614f — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  84d3de8
- C (triage):    7d067e6
- D (principal): 9fd6f76 — CTO ruling HACA-119 comment 16ba31cd-b381-4d38-b038-99986aab9855 (option 2: 3 aarch64 host-baseline failures accepted, base 40c814f fails the same set)

## Review Summary
HACA-119 paper wording: 11 findings (Q1-Q11) fixed, 6 rejected with reasons. Tests: quality.test_command_perturb-seq-eval full run 1117 passed / 3 failed / 13 skipped; the 3 failures are the CTO-accepted host-baseline set (test_backbones.py::test_single_target_regression_pin_bit_exact[int-MLPBackbone-pin1], [1-tuple-MLPBackbone-pin1], test_fill_v060_numbers.py::test_landed_analyser_reproduces_the_committed_summary; aarch64, same set fails at base 40c814f), recorded pass = same command with only those 3 deselected: 1117 passed, 13 skipped, 3 deselected. Waiver per CTO comment 16ba31cd.
