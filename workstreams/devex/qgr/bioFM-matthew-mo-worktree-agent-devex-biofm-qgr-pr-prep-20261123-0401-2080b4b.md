---
receipt_version: 2
type: qgr
boundary: pr-prep
org: bioFM
principal: matthew-mo
agent: worktree-agent
workstream: devex
project: biofm
diff_base: origin/main
hash_a: bcfec6e82d4e3b498ac8b75d7b44bc38397f1e15f942ef5d5960b29530cf658e
hash_b: a3eae3a0d2056e955ccd41f5b0ed701a2b78fafc3f1a1d363dbac843dbaf05c4
hash_c: 522b5f85579dede81e5fbb71aa4286cee3fef86b913b7e5971d6d849e1b36acd
hash_d: 19f34564b1ad68d5b62dc91a980052f020a81450c954cb4112927b5db3612bc5
hash_d_source: "x86_64 reference run https://github.com/supmo668/bioFM/actions/runs/45108908695 at 9e23c0f: 1246 passed / 3 failed, exactly the HACA-119 host-baseline set accepted by CTO comment 16ba31cd (HACA-121 policy)"
hash_e: 2080b4b14ef77f74e91c4780c5a0a3f6cfb1104f15a6b3572ac04a0a1f340f7c
test_result: pass
date: 2026-11-23T04:01
---

# Receipt: pr-prep — biofm

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): bcfec6e — artifact entering the gate
- E (final):    2080b4b — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  a3eae3a
- C (triage):    522b5f8
- D (principal): 19f3456 — x86_64 reference run https://github.com/supmo668/bioFM/actions/runs/45108908695 at 9e23c0f: 1246 passed / 3 failed, exactly the HACA-119 host-baseline set accepted by CTO comment 16ba31cd (HACA-121 policy)

## Review Summary
HACA-123 pr-prep, PR #54 (CI workflow + doc, no module code). profile: standard, reviewer-security + own review. 6 findings: SEC-2 persist-credentials (0e89cad), SEC-4 main-push cancellation (35797bd), SEC-5 pin comment (9e23c0f) fixed; SEC-1 tag pins rejected (repo house style), SEC-3 hash-locked install deferred (lock stale), SEC-6 rejected. Clean: contents:read, pull_request trigger, no expression injection, numpy/scipy/scikit-learn/h5py = poetry.lock. Tests: x86_64 run 45108908695 at 9e23c0f = 3 failed, 1246 passed, 1 skipped; failures are exactly test_backbones.py::test_single_target_regression_pin_bit_exact[int-MLPBackbone-pin1], [1-tuple-MLPBackbone-pin1], test_fill_v060_numbers.py::test_landed_analyser_reproduces_the_committed_summary (accepted, HACA-119 comment 16ba31cd; fixed in the sibling pin task). Module tree 54cc281 = main. test-result recorded via a check of that run (commit, module tree and failure set), since no test_command is scoped for devex.
