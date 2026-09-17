---
receipt_version: 2
type: qgr
boundary: iteration-complete
org: bioFM
principal: matthew-mo
agent: lung-on-chipsim
workstream: lung-on-chipsim
project: bioFM
diff_base: b801329
hash_a: b3d8a2e4f26ef943150a4a56b3fd5fdb1838ea1e60eb2992c58578d61f5057b8
hash_b: 851aa6b19f24030e67380b267d4eb3830f8b2000bec5916a37f517ae586f0d07
hash_c: 3526c8ef17c0c3687346cd084a427200ca1032b02db88a87099c067c0532053b
hash_d: 3526c8ef17c0c3687346cd084a427200ca1032b02db88a87099c067c0532053b
hash_d_source: "auto-approved — no principal 1B1"
hash_e: 1e07e6cc8d35fd684ef0fba321c3ca670ddddccf28386f7dccb6850119949246
date: 2026-09-16T17:37
---

# Receipt: iteration-complete — bioFM

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): b3d8a2e — artifact entering the gate
- E (final):    1e07e6c — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  851aa6b
- C (triage):    3526c8e
- D (principal): 3526c8e — auto-approved — no principal 1B1

## Review Summary
§4: G-19 (label-parquet reader carries stereo_is_relative), ruff format of 5 pre-existing files (formatting-only, verified by token+AST comparison), quality command config. QG: REDUCED ROSTER (2 reviewers + own review) — disclosed. Found that my own G-19 fix re-introduced G-03 one file downstream (the reader COERCED a non-boolean flag: strings/NaN became True for every row, on the file T17 reads) and that my agency.yaml change was both inverted and unanchored, breaking 3 sibling agents. Both fixed (70a0aae, 6011dec). 9 findings fixed, 2 disclosed, 3 escalated as framework feedback. Five mutants that survived my G-19 tests are each killed now, verified. Commits d0077a2 f878a26 2e81e97 6011dec 70a0aae. 711 passed / 5 skipped / 0 failed; ruff check + ruff format --check clean via the newly configured per-agent commands. Plan 7b29fb5 merged. KNOWN DEFECT IN A PRIOR CLAIM: f878a26's message says '61 files already formatted'; true count 67. Not pushed yet.
