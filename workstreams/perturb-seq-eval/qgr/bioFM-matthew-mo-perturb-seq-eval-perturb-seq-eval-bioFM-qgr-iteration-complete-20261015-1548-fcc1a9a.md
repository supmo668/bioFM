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
hash_a: 63ea97b28b6abb58b6d70db0faa4148ab047f25f8189acb8c75a1695fc371acb
hash_b: f34b80f9ce233aa6a4406d44d526fcfa409df9a343136e1cc5972bac4ac4c058
hash_c: cb412bafbdf737585169c352ae8f3816120e1c205d6c39f83031e13320b33115
hash_d: cb412bafbdf737585169c352ae8f3816120e1c205d6c39f83031e13320b33115
hash_d_source: "auto-approved — no principal 1B1"
hash_e: fcc1a9a3d676f1b7364dc3318aad203ad845ae2095f6b2a3d9c56287100c38ff
date: 2026-10-15T15:48
---

# Receipt: iteration-complete — bioFM

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): 63ea97b — artifact entering the gate
- E (final):    fcc1a9a — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  f34b80f
- C (triage):    cb412ba
- D (principal): cb412ba — auto-approved — no principal 1B1

## Review Summary
Python 3.12 reproduction disclosure (CTO #629 item 2); requires-python narrowing blocked by the 3.11 Modal images (escalated); 2 findings passed, all fixed
