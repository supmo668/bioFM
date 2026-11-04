---
receipt_version: 2
type: qgr
boundary: pr-prep
org: bioFM
principal: matthew-mo
agent: perturb-seq-eval
workstream: perturb-seq-eval
project: bioFM
diff_base: origin/main
derived_from: ae59f9818efccbc741235ad81424efb47b6b63e18cecdd7f32a06001cf5336a5
hash_a: 1d4070fa9873818d5b00739d18bb2e9d4c34b750453235e37592fafb045c9d4f
hash_b: c2143652cd6c0b2550d307eb15e61c5bdae2a72fda4759e85aa98b2dcfc94e6f
hash_c: 332474e8b14e394e761ed87c62d61bed64d8019bb5cfa33b21de365c2a84a0d3
hash_d: 332474e8b14e394e761ed87c62d61bed64d8019bb5cfa33b21de365c2a84a0d3
hash_d_source: "auto-approved — no principal 1B1"
hash_e: 27916e219c2f1a9114ee1cbf0cd7016b7f0414e261587ba14827778a062302d0
date: 2026-11-04T01:26
---

# Receipt: pr-prep — bioFM

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): 1d4070f — artifact entering the gate
- E (final):    27916e2 — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  c214365
- C (triage):    332474e
- D (principal): 332474e — auto-approved — no principal 1B1

## Review Summary
DERIVED from pr-prep ae59f98: delta since gate is context-only (.claude/usr dispatch files for pr-submit #888 and its correction reply); no code, no test, no doc change; gate findings/fixes/checks as in parent (F3/F4/F5 fixed; F1/F2 escalated; 1088 passed/13 skipped)
