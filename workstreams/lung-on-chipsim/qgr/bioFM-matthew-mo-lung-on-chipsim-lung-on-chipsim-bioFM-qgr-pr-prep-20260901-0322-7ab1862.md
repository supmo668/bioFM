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
hash_d_source: "auto-approved — no principal 1B1 for the fix cycle; CTO authorized the pr-prep re-run (dispatch #14 follow-up)"
hash_e: 7ab1862e722bf7bf3fc828a258e878f7216e7b9291182743d9833388faf06949
date: 2026-09-01T03:22
---

# Receipt: pr-prep — bioFM

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): 5294b2a — artifact entering the gate
- E (final):    7ab1862 — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  67b7b11
- C (triage):    7ea6ecd
- D (principal): 7ea6ecd — auto-approved — no principal 1B1 for the fix cycle; CTO authorized the pr-prep re-run (dispatch #14 follow-up)

## Review Summary
P0.3 pr-prep gate: 4 reviewers + scorer, 20 findings actioned (2 rejected verified-false), DVC portability, biological numbers out of configs/, panel entry validation, first live-config face assertion, README correctness. 289 passed / 7 skipped offline, 15/1 network, ruff clean.
