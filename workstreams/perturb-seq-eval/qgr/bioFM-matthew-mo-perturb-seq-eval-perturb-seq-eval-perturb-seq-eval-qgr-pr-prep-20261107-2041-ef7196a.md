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
hash_a: c4ef7037f927514018d2c298811f6840dcdf0fb7251cc615ae2de731291a196b
hash_b: d8787638559c1c79d465541988d7e12280e93d936d38fd4e84a0f98ce00f151f
hash_c: 62f50903d4c6c5cc9ef406d03e39076be51e89196b31dbe185495734cf75ea8d
hash_d: 62f50903d4c6c5cc9ef406d03e39076be51e89196b31dbe185495734cf75ea8d
hash_d_source: "auto-approved — principal 2026-11-07 'proceed without confirmation'; no 1B1"
hash_e: ef7196a8c71276737ef9d3561f3bbda438689d3b75a3e3e57c2b2869a3120b45
date: 2026-11-07T20:41
---

# Receipt: pr-prep — perturb-seq-eval

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): c4ef703 — artifact entering the gate
- E (final):    ef7196a — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  d878763
- C (triage):    62f5090
- D (principal): 62f5090 — auto-approved — principal 2026-11-07 'proceed without confirmation'; no 1B1

## Review Summary
row-26 staging PR: 4 findings-staging ledgers labelled in place; 18 findings, 13 >=80 (11 fixed, G2 escalated: CLAUDE.md:144-147 vs row 26; G1 Morandi affiliation removed); module suite 1091 passed 0 failed (code == origin/main)
