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
derived_from: 1f2dbd9
hash_a: 8df7dbdd804a13ddc280cb2be09e7efcb2acd9169cc1eca18d554f5b22d6e472
hash_b: 43dd918a0334b63b080e0fd10c87b41cacf80246277c5983b2a724e50b4b7377
hash_c: a62742f7e3f85102a1f63dd41c632c10ff6326b98197e6863152f9941f45c42c
hash_d: a62742f7e3f85102a1f63dd41c632c10ff6326b98197e6863152f9941f45c42c
hash_d_source: "auto-approved — derived from iteration gates c9d568c (A) and 1f2dbd9 (B)"
hash_e: 8df7dbdd804a13ddc280cb2be09e7efcb2acd9169cc1eca18d554f5b22d6e472
date: 2026-11-05T21:17
---

# Receipt: pr-prep — perturb-seq-eval

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): 8df7dbd — artifact entering the gate
- E (final):    8df7dbd — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  43dd918
- C (triage):    a62742f
- D (principal): a62742f — auto-approved — derived from iteration gates c9d568c (A) and 1f2dbd9 (B)

## Review Summary
pr-prep derived: iteration A gated bef363fe..96bd3761 (receipt c9d568c), iteration B gated 5487bac5..107bdeea (receipt 1f2dbd9); delta outside both = instinct metadata, context and QGR-log files; Iron-Law at HEAD: tests 1091 passed 0 failed
