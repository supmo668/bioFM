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
derived_from: ae02b6b4fa6eaefb1126348cd4f2dcac197e59e45bd2bdd7e396861e6cad4e71
hash_a: 5b7a8b07144c6d0ebec6bbc6a52c3207fd17f0b6e626d8c57c015f84d04f1ee3
hash_b: 8e6a8859a9ef279bb43c2d5828f82b7250b05d58c120e3302d69a95e79641dc2
hash_c: 4cb925834faa4c0bc750379eac0ca661f474c7a4711339dfc8e899b881f7817f
hash_d: 4cb925834faa4c0bc750379eac0ca661f474c7a4711339dfc8e899b881f7817f
hash_d_source: "auto-approved — no principal 1B1"
hash_e: e0c358e949b5534e6e6c35da75a59fa26b9e2af5040f43d5fad7b1789007eed0
date: 2026-10-16T17:43
---

# Receipt: iteration-complete — bioFM

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): 5b7a8b0 — artifact entering the gate
- E (final):    e0c358e — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  8e6a885
- C (triage):    4cb9258
- D (principal): 4cb9258 — auto-approved — no principal 1B1

## Review Summary
Derived from REV-1 (ae02b6b): publish.state.v060.json emptied after the standalone drafts were discarded (data, not code; the empty state is what DraftRequiredError reads); 1214 tests pass on the committed HEAD
