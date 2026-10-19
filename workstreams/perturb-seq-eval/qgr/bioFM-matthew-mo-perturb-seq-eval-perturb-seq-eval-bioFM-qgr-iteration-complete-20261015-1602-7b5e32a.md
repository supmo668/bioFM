---
receipt_version: 2
type: qgr
boundary: iteration-complete
org: bioFM
principal: matthew-mo
agent: perturb-seq-eval
workstream: perturb-seq-eval
project: bioFM
diff_base: origin/main
hash_a: 32794e4584c2124041a6291760723429e4a5cacdba8eb2b68c676d5b507351f0
hash_b: 396f99e3b1a5eba656ac1555be77b6a73746940c0621c862044ffc4437d4d290
hash_c: 5f0a77d19d7cca02e245f2a1c9d3674783d0b9c204391c7ddf1b9d5767dc8fab
hash_d: 5f0a77d19d7cca02e245f2a1c9d3674783d0b9c204391c7ddf1b9d5767dc8fab
hash_d_source: "auto-approved — no principal 1B1"
hash_e: 7b5e32ab0a36744bae8855f950cfb4bfd08688d16fc40d6c0a52a4bafb6b1a3a
date: 2026-10-15T16:02
---

# Receipt: iteration-complete — bioFM

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): 32794e4 — artifact entering the gate
- E (final):    7b5e32a — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  396f99e
- C (triage):    5f0a77d
- D (principal): 5f0a77d — auto-approved — no principal 1B1

## Review Summary
D8: v0.6.0 re-run refuses a Modal client other than the recorded run's, read from provenance (CTO #633 ii+iii); 3 findings passed, all fixed
