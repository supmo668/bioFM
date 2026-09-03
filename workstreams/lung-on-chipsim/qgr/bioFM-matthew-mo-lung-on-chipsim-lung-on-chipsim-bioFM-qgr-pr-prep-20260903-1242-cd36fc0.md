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
hash_a: e38ed4672be3f3b457ba2ae45a845bf1dc77ada38d8e4c93acfc2dd6d4d1cbab
hash_b: 1cf06d03fb774026c3a9f85bfbd8733768a967d56368b572b88a5343912d65d9
hash_c: 17bd53be91b5999bf44114c2660e021a3449e8a2cf024a0da44aa31b0f7cc52c
hash_d: 17bd53be91b5999bf44114c2660e021a3449e8a2cf024a0da44aa31b0f7cc52c
hash_d_source: "auto-approved — no principal 1B1 for this re-gate"
hash_e: cd36fc04e93c4ddc0ddfd0659557efe88fddaf1ffbb03eed095091a09fd1bf74
date: 2026-09-03T12:42
---

# Receipt: pr-prep — bioFM

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): e38ed46 — artifact entering the gate
- E (final):    cd36fc0 — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  1cf06d0
- C (triage):    17bd53b
- D (principal): 17bd53b — auto-approved — no principal 1B1 for this re-gate

## Review Summary
T7a re-gate: 29 findings from two reviewers (3 CRITICAL, 8 HIGH), 28 fixed, 1 INFO no-change, 0 deferred. Seal now verified before it is printed; one config boundary for every reader; panel-seal confirmation fails closed. 419 passed, 0 failed. 9-mutant sweep, 0 survivors. Hash A is caveated in the findings file: the test reviewer read a moving tree.
