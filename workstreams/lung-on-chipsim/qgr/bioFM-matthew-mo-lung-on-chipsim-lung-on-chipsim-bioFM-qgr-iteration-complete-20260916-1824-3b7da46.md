---
receipt_version: 2
type: qgr
boundary: iteration-complete
org: bioFM
principal: matthew-mo
agent: lung-on-chipsim
workstream: lung-on-chipsim
project: bioFM
diff_base: 83188df
hash_a: 83304787349a507025a885a788ba7950d7d3c6090a7dc1f7b9bf8a4f878be3ea
hash_b: dd348eb357a0fc066ce723be828d548c2a1226d1e9dbd6e5ef4922419a1a7e69
hash_c: 72fd70805829eb37dd5d636bc7dde7cdf2cbfa67fd412f5d2a6d4757913bb502
hash_d: 72fd70805829eb37dd5d636bc7dde7cdf2cbfa67fd412f5d2a6d4757913bb502
hash_d_source: "auto-approved — no principal 1B1"
hash_e: 3b7da46c7a9069bd4a2cf784280b144740f6ffc6ef905495b7dcda52fc2d3ac6
date: 2026-09-16T18:24
---

# Receipt: iteration-complete — bioFM

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): 8330478 — artifact entering the gate
- E (final):    3b7da46 — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  dd348eb
- C (triage):    72fd708
- D (principal): 72fd708 — auto-approved — no principal 1B1

## Review Summary
§5: r2.19 G-15 (only the export may write under configs/) + G-18 (chipsim adjudication-export). FULL roster per the CTO's standing rule. The gate found my G-15 guard was THREE EXECUTED BYPASSES — a case variant wrote a name-bearing worksheet into the real configs dir, a symlinked configs dir let the write through, and the check resolved while the write used the literal path so os.replace REPLACED a destination symlink — and simultaneously too broad, refusing every write in a checkout under any configs ancestor. Also fixed: a symlink loop raising RuntimeError past every handler, a FALSE RECOVERY INSTRUCTION with no implementing code, the CLI's traceback on a mistyped path, and my own vacuous match= assertions (a bare-path message and an unrelated error both survived; the correct message was killed). 14 fixed in 84ce8e0, all verified by 11 mutants that now fail. 6 escalated: the guard protects a directory NAME not tracked-ness; write_compounds is a second unguarded writer with the FULL record reachable via chipsim write --out; the repo guard is blind to binary files and has no name detector; fail-closed inherited by tuple membership; plan amendments for r2.20. 731 passed / 5 skipped / 0 failed; ruff check + format clean. Plan 7b29fb5. DISCLOSED: the project's real invocation journal holds 38 test-written export records (git-ignored, nothing redistributed, not purged — the CTO should decide). PROCESS: a reviewer mutated the shared tree mid-gate for the third time today; tree verified byte-identical before hashing.
