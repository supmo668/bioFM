---
receipt_version: 2
type: qgr
boundary: iteration-complete
org: bioFM
principal: matthew-mo
agent: lung-on-chipsim
workstream: lung-on-chipsim
project: bioFM
diff_base: 514ff17
hash_a: 74cbc26e6914a9e748bf2660961c0f2552d36533b944c64538b0a6cf62875eb9
hash_b: a4682351fb4920f7d0b8d099b9997374735326b9d5ee26baf65b6103e59b938e
hash_c: f0452395a90957130d28f0f2b2fadc22027bcc51b1537b7b9d8481ae74cb660e
hash_d: f0452395a90957130d28f0f2b2fadc22027bcc51b1537b7b9d8481ae74cb660e
hash_d_source: "auto-approved — no principal 1B1"
hash_e: b0a20cbbdfc136a88cd6d242c60cf22509de8609aa1351c90a3fd49573e17a79
date: 2026-09-18T10:55
---

# Receipt: iteration-complete — bioFM

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): 74cbc26 — artifact entering the gate
- E (final):    b0a20cb — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  a468235
- C (triage):    f045239
- D (principal): f045239 — auto-approved — no principal 1B1

## Review Summary
§13.2: the blob reader trusted the filesystem, the bytes and the memory it was handed — a reproduced case-collision false clean, replace-ref substitution, an unbounded tree in RAM, and a writer that left the record-bearing registry by changing how it writes
