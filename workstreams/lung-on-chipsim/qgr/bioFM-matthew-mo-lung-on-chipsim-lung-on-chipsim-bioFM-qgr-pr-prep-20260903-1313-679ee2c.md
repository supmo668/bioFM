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
hash_a: cd36fc04e93c4ddc0ddfd0659557efe88fddaf1ffbb03eed095091a09fd1bf74
hash_b: 1cf06d03fb774026c3a9f85bfbd8733768a967d56368b572b88a5343912d65d9
hash_c: df565cf80be7ab1a1f623b0f0c9c4042b4f8c5a63f97f66e7b0e8ffa2ce102a9
hash_d: df565cf80be7ab1a1f623b0f0c9c4042b4f8c5a63f97f66e7b0e8ffa2ce102a9
hash_d_source: "auto-approved — no principal 1B1 for this re-gate"
hash_e: 679ee2cec0a85938d70998be69eb37e5340434bfc3bae277dfda723721598eb4
date: 2026-09-03T13:13
---

# Receipt: pr-prep — bioFM

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): cd36fc0 — artifact entering the gate
- E (final):    679ee2c — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  1cf06d0
- C (triage):    df565cf
- D (principal): df565cf — auto-approved — no principal 1B1 for this re-gate

## Review Summary
T7a re-gate over the bumped tip f0bb4c1. A=cd36fc0 is the previously gated state; A->E is one line of agency.yaml (0.2.0->0.3.0) and no Python. NO new review was run and none is claimed: Hash B is deliberately UNCHANGED because the findings document is unchanged. Hash C moves for the addendum recording that decision. Re-verified on the bumped tip: format clean, lint clean, 419 passed / 7 skipped / 0 failed.
