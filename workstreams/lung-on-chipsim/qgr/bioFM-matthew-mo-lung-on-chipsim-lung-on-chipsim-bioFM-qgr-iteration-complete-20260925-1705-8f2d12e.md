---
receipt_version: 2
type: qgr
boundary: iteration-complete
org: bioFM
principal: matthew-mo
agent: lung-on-chipsim
workstream: lung-on-chipsim
project: bioFM
diff_base: 561be17
hash_a: 33a813381b5346e293631609f0cf4f151b49a12930370c20c105ea53f46aa822
hash_b: d214f6e9530a0e9d4b9545a1702025d19c4f04e9cf1c911cf4ef8ae83681f92f
hash_c: 4490ba1ae7065c9e7eadf5f53d7057155a39173da8ff9987cd888b001dd508ab
hash_d: 4490ba1ae7065c9e7eadf5f53d7057155a39173da8ff9987cd888b001dd508ab
hash_d_source: "auto-approved — no principal 1B1 (iteration boundary; directive #399)"
hash_e: 8f2d12e4034809a8ac4956f19bb3e2b2aa56acb66ba384dacfdae91dc6258b30
date: 2026-09-25T17:05
---

# Receipt: iteration-complete — bioFM

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): 33a8133 — artifact entering the gate
- E (final):    8f2d12e — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  d214f6e
- C (triage):    4490ba1
- D (principal): 4490ba1 — auto-approved — no principal 1B1 (iteration boundary; directive #399)

## Review Summary
Gate 5 over E-22 r2.47a WI-1+WI-2 (561be17..HEAD): 17 findings, 12 >=80, all fixed in-gate (atomic G5-R* commits); full suite 1171/4 exit 0; EXTENDED TIER RUN: 'cd projects/lung-on-chipsim && AIADLC_ACCESSION_ORACLE_EXTENDED=1 uv run pytest -q -p no:cacheprovider tests/test_accession_pattern_matrix.py' exit 0, 15 passed, 248 s, 2.89 GB; both record-content gates exit 0
