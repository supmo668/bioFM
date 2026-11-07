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
hash_a: 1d4070fa9873818d5b00739d18bb2e9d4c34b750453235e37592fafb045c9d4f
hash_b: c2143652cd6c0b2550d307eb15e61c5bdae2a72fda4759e85aa98b2dcfc94e6f
hash_c: 332474e8b14e394e761ed87c62d61bed64d8019bb5cfa33b21de365c2a84a0d3
hash_d: 332474e8b14e394e761ed87c62d61bed64d8019bb5cfa33b21de365c2a84a0d3
hash_d_source: "auto-approved — no principal 1B1"
hash_e: ae59f9818efccbc741235ad81424efb47b6b63e18cecdd7f32a06001cf5336a5
date: 2026-11-04T01:23
---

# Receipt: pr-prep — bioFM

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): 1d4070f — artifact entering the gate
- E (final):    ae59f98 — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  c214365
- C (triage):    332474e
- D (principal): 332474e — auto-approved — no principal 1B1

## Review Summary
pr-prep vs origin/main 46c32bb: profile standard; 4 reviewers+scorer; 5 findings >=80; fixed F3 (self-test SKIP counted, exit 1), F4 (categories.primary shape check), F5 (test rename); F1 (venue contradiction) + F2 (stale c0ec931/CI text) in SUBMISSION.md ESCALATED to CTO (doc closed by #885); 1088 passed/13 skipped; self-test ALL LIVE
