---
receipt_version: 1
type: qgr
boundary: pr-prep
org: bioFM
principal: matthew-mo
agent: lung-on-chipsim
workstream: lung-on-chipsim
project: bioFM
diff_base: origin/main
hash_a: 7c667b8ec3cf362714ddbf9ce218fdb6fd7a6cbc3b3dcdd92b911064594a683e
hash_b: 60ddecb26d5e8afc667c6f51f852add98ed5e1c2611d9d4812cb27343c6a2acf
hash_c: d2a4dceed2e38731ba34bcfabd31d3d11f35117624a27a0e28a68c39bd8b3b6d
hash_d: d2a4dceed2e38731ba34bcfabd31d3d11f35117624a27a0e28a68c39bd8b3b6d
hash_d_source: "auto-approved — no principal 1B1 in this session"
hash_e: 478df8b92492285867ed470ae9f50dbe56788ca8e575f3086983be3b30b0aa57
date: 2026-09-03T02:35
---

# Receipt: pr-prep — bioFM

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): 7c667b8 — artifact entering the gate
- E (final):    478df8b — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  60ddecb
- C (triage):    d2a4dce
- D (principal): d2a4dce — auto-approved — no principal 1B1 in this session

## Review Summary
r2.7 work order: config symlink+hardlink escape refused loudly, argv[0] basename, seed capture, TTY gate, diff/veto removed from spec. QG found 30+ findings incl. hard-link exfiltration and escapes exiting 0; all fixed. 380 tests, lint+format clean.
