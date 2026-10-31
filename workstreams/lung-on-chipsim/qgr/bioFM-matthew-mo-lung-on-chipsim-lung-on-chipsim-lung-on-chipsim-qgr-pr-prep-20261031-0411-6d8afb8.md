---
receipt_version: 2
type: qgr
boundary: pr-prep
org: bioFM
principal: matthew-mo
agent: lung-on-chipsim
workstream: lung-on-chipsim
project: lung-on-chipsim
diff_base: origin/main
hash_a: bf1a3f52d39060adbdf172dc4de49bae6a551ba7607b7ef6e85b50421b39e2d9
hash_b: 1da8596f478534a79ac03492ecf3fc66b11d3a4cad3fb42e0d28139109e1aa2c
hash_c: 6c5ecef6653266b85fd9d89ef3abb73fa37feb1e9fb2ec7e180e7aca4522f39b
hash_d: 281a7d6406fd9d5b4d93b825336e77dc0ac52f467181bf929add3afcf22dc8b3
hash_d_source: "approvals.md — this gate had no principal 1B1 transcript, so the principal's own decision record stands in; C != D is asserted at signing rather than copying C into D"
hash_e: 6d8afb849b5b812e2a21ed884b8241f6e5a0f15fad9fe8a4ad9cd7099d774e13
date: 2026-10-31T04:11
---

# Receipt: pr-prep — lung-on-chipsim

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): bf1a3f5 — artifact entering the gate
- E (final):    6d8afb8 — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  1da8596
- C (triage):    6c5ecef
- D (principal): 281a7d6 — approvals.md — this gate had no principal 1B1 transcript, so the principal's own decision record stands in; C != D is asserted at signing rather than copying C into D

## Review Summary
Stage 2: published-number pins repaired after a 4-reviewer gate (~45 findings, all closed or deferred with owner named); identifier-pairing leak in assertion operands eliminated and verified over 12 real failures; relative-stereo 42 given an independent /s2 witness; parquet tied to its tracked sha256; two modules merged; a fabricated approvals citation corrected
