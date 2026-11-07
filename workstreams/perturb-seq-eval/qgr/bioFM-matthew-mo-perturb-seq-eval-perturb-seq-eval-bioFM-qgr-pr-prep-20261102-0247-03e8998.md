---
receipt_version: 2
type: qgr
boundary: pr-prep
org: bioFM
principal: matthew-mo
agent: perturb-seq-eval
workstream: perturb-seq-eval
project: bioFM
diff_base: origin/main
hash_a: 03e8998303f74af6b9a3987db087aabd7eb65efdd25a296d341e83d70e4063f7
hash_b: e99480b310694e702881040fa9be890c435a92579bc230ca2ced4485834a76a9
hash_c: 03b727a2aefb178eed070188da498aa24b8557383c99d9c2b9984e5520671c45
hash_d: 03b727a2aefb178eed070188da498aa24b8557383c99d9c2b9984e5520671c45
hash_d_source: "auto-approved — no principal 1B1; review record = FRAMING.1 iteration gate (receipt 12d40b4); delta from 12d40b4 is only .claude/workstreams/perturb-seq-eval/context.json (phase-state, ISCP state, not code)"
hash_e: 03e8998303f74af6b9a3987db087aabd7eb65efdd25a296d341e83d70e4063f7
date: 2026-11-02T02:47
---

# Receipt: pr-prep — bioFM

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): 03e8998 — artifact entering the gate
- E (final):    03e8998 — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  e99480b
- C (triage):    03b727a
- D (principal): 03b727a — auto-approved — no principal 1B1; review record = FRAMING.1 iteration gate (receipt 12d40b4); delta from 12d40b4 is only .claude/workstreams/perturb-seq-eval/context.json (phase-state, ISCP state, not code)

## Review Summary
pr-prep (re-sign): cs.MA cross-list (row 12) + QG fixes F1/F2/F3/F5/F6/F12 + context.json state; code diff identical to 12d40b4; lint/format/self-test/tests fresh: 1088 passed / 13 skipped / 0 failed
