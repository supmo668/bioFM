---
receipt_version: 2
type: qgr
boundary: pr-prep
org: bioFM
principal: matthew-mo
agent: perturb-seq-eval
workstream: perturb-seq-eval
project: perturb-seq-eval
diff_base: origin/main
hash_a: 41bbffc9e3a2b02aa5f426e6c8656f89b1403c3578b183c984314b24a9ddba34
hash_b: 65a4ccfdbe434ae9e4fa3843608f769915e1fe76c1273deb2961ed0c8851bb6d
hash_c: 65a4ccfdbe434ae9e4fa3843608f769915e1fe76c1273deb2961ed0c8851bb6d
hash_d: 65a4ccfdbe434ae9e4fa3843608f769915e1fe76c1273deb2961ed0c8851bb6d
hash_d_source: "principal instruction in session, row 42 (2026-11-25); no 1B1"
hash_e: 41bbffc9e3a2b02aa5f426e6c8656f89b1403c3578b183c984314b24a9ddba34
test_result: pass
date: 2026-11-25T01:43
---

# Receipt: pr-prep — perturb-seq-eval

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): 41bbffc — artifact entering the gate
- E (final):    41bbffc — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  65a4ccf
- C (triage):    65a4ccf
- D (principal): 65a4ccf — principal instruction in session, row 42 (2026-11-25); no 1B1

## Review Summary
self-contained reader-facing surfaces (row 42): clarity pass, meaning-drift review scored 70/100 with 8 findings, all fixed and pinned by test; CellForge reference corrected from arXiv; 1159 passed 0 failed 15 skipped; stage-3 fixes not independently re-reviewed; publication of 0.6.2 NOT approved
