---
receipt_version: 2
type: qgr
boundary: iteration-complete
org: bioFM
principal: matthew-mo
agent: lung-on-chipsim
workstream: lung-on-chipsim
project: bioFM
diff_base: 20e9edd
hash_a: b7e34299a469b6cf3da1305e1b52d11ac82880db64a41d844632cde8d40fc388
hash_b: 6a9ef450faedbf4bffb71505dcca8ea86000271df71702b38be54a18591f97e2
hash_c: 48a784c691b0b153e29d6373cbb8701904fe7e9f0aed8e2771905d03d83b5ef7
hash_d: 48a784c691b0b153e29d6373cbb8701904fe7e9f0aed8e2771905d03d83b5ef7
hash_d_source: "auto-approved — no principal 1B1"
hash_e: 54e27d508cfbb6985b58698b315dd06fbfc1f1938ec882d3e4b325f0b76717e8
date: 2026-09-17T20:22
---

# Receipt: iteration-complete — bioFM

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): b7e3429 — artifact entering the gate
- E (final):    54e27d5 — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  6a9ef45
- C (triage):    48a784c
- D (principal): 48a784c — auto-approved — no principal 1B1

## Review Summary
r2.29/r2.30/r2.31 §12: signatures-first, then errors/policy/report extracted as leaves, then r2.28's staged-blob ruling, derived_from pinning content, and four carried findings. A four-reviewer gate then found THREE FALSE CLEANS (a symlink's committed bytes are its target string and the guard read the target; a record in a numeric-dtype HDF5 dataset was invisible while the container certified as fully read; an unmerged index was scanned around, giving staged CLEAN where worktree found the accession), a RULING WITH NO READER (r2.28's commit gate existed as a capability nothing invoked - E6-7's defect one iteration after I fixed it), a ScanContext that could claim STAGED while reading the worktree, an HDF5 path whose aggregate budget could only fire after the memory was allocated, TWO REGRESSIONS OF MY OWN, and THREE VACUITIES OF MY OWN including one that passed under the exact defect it names. Mutation evidence stated with baseline AND deselection count throughout. Four cache-key components were MEASURED INERT and their non-discriminating tests deleted rather than kept. Escalated, not fixed: installing a pre-commit hook (repository configuration, the CTO's call), and checkout-index applying eol/smudge conversion so staged bytes may differ from blob bytes.
