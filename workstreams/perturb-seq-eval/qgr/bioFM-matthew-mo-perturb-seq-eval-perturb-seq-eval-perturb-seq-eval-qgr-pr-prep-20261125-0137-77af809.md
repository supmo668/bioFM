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
hash_a: a03a7396548cdd7add7f301ff421d29dad32001b6e8bfba39e671cc62d8c3d56
hash_b: d74d1d10f58eeaabdb7927b05b5f4741985bcbfd017a892448ce4894ad8652c4
hash_c: 3fb1965c52efed02b1a20e0ce403e92f09fbe8e562fb777e53eaaf76bcb64083
hash_d: 3fb1965c52efed02b1a20e0ce403e92f09fbe8e562fb777e53eaaf76bcb64083
hash_d_source: "auto-approved, no principal 1B1; the publish itself is the principal's go of approvals row 42 (card 0c57e559)"
hash_e: 77af809b1de418d80de06a901a6a0dbf261c21933666955cde2a2501afded307
test_result: pass
date: 2026-11-25T01:37
---

# Receipt: pr-prep — perturb-seq-eval

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): a03a739 — artifact entering the gate
- E (final):    77af809 — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  d74d1d1
- C (triage):    3fb1965
- D (principal): 3fb1965 — auto-approved, no principal 1B1; the publish itself is the principal's go of approvals row 42 (card 0c57e559)

## Review Summary
0.6.2 published on Zenodo (10.5281/zenodo.24518637) and Figshare (v8): state file, approvals rows 42-43, CITATION (module and root), CHANGELOG, README, SUBMISSION, publish.yml and submitter comments, one strengthened test; 4 reviewers (security 0) + scorer: 3 at or above 80, all fixed, 10 below threshold fixed, 2 rejected (ledger rows are not edited); 1289 passed 0 failed 1 skipped; test role set to perturb-seq-eval for this branch; reviewer-ux: skipped (not user-facing: docs, metadata, one test)
