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
hash_a: 59831ecb39fa481a7777eeec0b5e2430f02cd310ac7ba606dd3b3c0b980c537a
hash_b: 78390674e4026378550756c5eb6633dfb33d203335eccdafe79e9d8476d9e8ce
hash_c: ae99a922b88cd77d0056fc7391ed6a3154583ecdcc828d6ef338a4d5de5ca9ce
hash_d: ae99a922b88cd77d0056fc7391ed6a3154583ecdcc828d6ef338a4d5de5ca9ce
hash_d_source: "auto-approved fix cycle; principal 1B1 rulings recorded in A and D r1.1 D3a/F2a"
hash_e: cca056ce8d53f26ddf6ad3bac81a41a3b1bbb35cf60eeef88aa87d9bce4f49d0
date: 2026-09-02T11:13
---

# Receipt: pr-prep — bioFM

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): 59831ec — artifact entering the gate
- E (final):    cca056c — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  7839067
- C (triage):    ae99a92
- D (principal): ae99a92 — auto-approved fix cycle; principal 1B1 rulings recorded in A and D r1.1 D3a/F2a

## Review Summary
P0.8 pr-prep, genuine gate. Two reviewers over the S12 run journal, which a withdrawn receipt had falsely claimed to cover. 31 findings; 33 mutations applied, 12 tests found vacuous. Fixed: a copied outcome.json verified as another run result (no identity check); the outcome-to-manifest binding was documented but never verified; a journal-bypassing second entrypoint; the user field was env-settable inside a Constraint-4 trail; the invocation blocklist passed any other digest name; and the honesty grep was bypassable by writing the word no after the claim - falsified with the exact sentence that survived it. Deferred with reasons: the fail-open design question (C-3/4/5) and seven named test gaps. Verified this cycle: pytest -q 345 passed / 7 skipped; -m not network 330 passed / 6 skipped; ruff clean. Hashes A, B and C are computed for THIS gate and all differ from d448db5 - the recycling defect that invalidated P0.4 through P0.7.
