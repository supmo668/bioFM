---
receipt_version: 2
type: qgr
boundary: pr-prep
org: bioFM
principal: matthew-mo
agent: worktree-agent
workstream: perturb-seq-eval
project: biofm
diff_base: origin/main
hash_a: ae60245e1dbdd7fc632f06f841792a4d5af53c5dd1ccdaf9e63179c25098bbb2
hash_b: 368087bb20fd8505d367051ea3b6ff267c78a3185f66c865ff36f66f60fbb994
hash_c: 0f402e263b8ac4fb3bac143ef901d948141fc3b718e0cb140775e656d5dbab74
hash_d: 012ed3693b078808e217d146d8000c38f00a97bd557eb1321286bff0186034d4
hash_d_source: "no waiver: host test-result run at 9cf6238 = 1254 passed (aarch64); x86_64 reference run https://github.com/supmo668/bioFM/actions/runs/45112417868 green at 9cf6238 = 1253 passed, 1 skipped (ruff absent in CI), module_tree 23679d2 (HACA-121 policy)"
hash_e: 469e67817d4a6173f50ea7b38a3fced1cf3c85fd2fcfe36ec2f27c1b20fdbbe5
test_result: pass
date: 2026-11-23T04:35
---

# Receipt: pr-prep — biofm

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): ae60245 — artifact entering the gate
- E (final):    469e678 — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  368087b
- C (triage):    0f402e2
- D (principal): 012ed36 — no waiver: host test-result run at 9cf6238 = 1254 passed (aarch64); x86_64 reference run https://github.com/supmo668/bioFM/actions/runs/45112417868 green at 9cf6238 = 1253 passed, 1 skipped (ruff absent in CI), module_tree 23679d2 (HACA-121 policy)

## Review Summary
HACA-124 pr-prep, perturb-seq-eval. Three bit-exact pins replaced per CTO ruling on HACA-121, pins kept not re-recorded. Linear pin stays bit-exact; MLP pin bounded at 4 ulp of max|pin| (deviation from literal per-element assert_array_max_ulp: element 0 is a cancellation result moving 12/28 of its own ulp on aarch64/x86, ~5e-17 abs; every element within 1 ulp of scale on both); MLP int and 1-tuple asserted byte-identical. Summary test: exact for every key except H5/weights/one_minus_delta_c and H5/norman_tdi (<=4 ulp), every reported rounded value asserted identical. Numeric environment in tests/fixtures/numeric_environment.json and printed each run; README, paper.tex Reproducibility, CHANGELOG and docs/ci updated. QG (reviewer-code, reviewer-test, own): 13 findings, 3 above threshold (F1 README, F2 int/1-tuple bytes, F4 optional scipy/sklearn) fixed in fda1f81/805b631/5c9046a; F3,F5-F9 fixed in 7e2af00; F10-F13 rejected. Post-gate: merge of origin/main (PR #54, no module change) and two docs/ci commits, self-reviewed. Tests: host 1254 passed, x86 1253 passed + 1 skipped, both at 9cf6238.
