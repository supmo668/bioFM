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
derived_from: c9d568c5d27976d09911dcc286c5bfaa424409f3bd4c0a41ef5ac2e8af197555
hash_a: 08729fa857440a54fef2a495a46c2fb85a1c20ed60bcb9da139205e925197939
hash_b: e2958d3fdb3d7555b9847c833caa8134919c9f9370de7724e4b42bc4c020969d
hash_c: df622bc83dca867f25e6950d7a49926501257a259362403798ad4bb2c3290119
hash_d: df622bc83dca867f25e6950d7a49926501257a259362403798ad4bb2c3290119
hash_d_source: "auto-approved — derived from iteration gate c9d568c (no principal 1B1)"
hash_e: 08729fa857440a54fef2a495a46c2fb85a1c20ed60bcb9da139205e925197939
date: 2026-11-05T04:05
---

# Receipt: pr-prep — perturb-seq-eval

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): 08729fa — artifact entering the gate
- E (final):    08729fa — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  e2958d3
- C (triage):    df622bc
- D (principal): df622bc — auto-approved — derived from iteration gate c9d568c (no principal 1B1)

## Review Summary
pr-prep derived from iteration-complete c9d568c (4-reviewer fan-out + scorer on the A5 diff); delta vs gated state = .aiadlc instinct metadata lines + context/QGR-log files only; Iron-Law re-run at HEAD: format/lint clean, tests 1089 passed 0 failed, render+fill checks match
