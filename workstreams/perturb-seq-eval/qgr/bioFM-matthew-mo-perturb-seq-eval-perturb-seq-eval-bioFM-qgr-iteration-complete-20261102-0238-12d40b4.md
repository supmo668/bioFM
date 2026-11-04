---
receipt_version: 2
type: qgr
boundary: iteration-complete
org: bioFM
principal: matthew-mo
agent: perturb-seq-eval
workstream: perturb-seq-eval
project: bioFM
diff_base: e3a3a1f
hash_a: ab4080a7d0b3b685eb01c1676764da2b5d1f2d3d729c570bbc182e2c65b801f6
hash_b: e99480b310694e702881040fa9be890c435a92579bc230ca2ced4485834a76a9
hash_c: 03b727a2aefb178eed070188da498aa24b8557383c99d9c2b9984e5520671c45
hash_d: 03b727a2aefb178eed070188da498aa24b8557383c99d9c2b9984e5520671c45
hash_d_source: "auto-approved — no principal 1B1"
hash_e: 12d40b48a5d8c345f5ecc07f8c3452bc00d13c83b20e0eab27023e44cf718d4a
date: 2026-11-02T02:38
---

# Receipt: iteration-complete — bioFM

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): ab4080a — artifact entering the gate
- E (final):    12d40b4 — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  e99480b
- C (triage):    03b727a
- D (principal): 03b727a — auto-approved — no principal 1B1

## Review Summary
FRAMING.1 cs.MA cross-list (row 12): arxiv.toml + SUBMISSION.md; QG fixes F1/F2/F3/F5 (runbook ruled/blocker/regenerated block), F6 (cross_list validation + self-test), F12 (C-TORCH-2 test); suite green in .venv
