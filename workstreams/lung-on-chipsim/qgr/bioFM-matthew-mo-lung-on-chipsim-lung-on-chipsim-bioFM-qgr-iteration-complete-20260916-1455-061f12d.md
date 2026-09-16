---
receipt_version: 2
type: qgr
boundary: iteration-complete
org: bioFM
principal: matthew-mo
agent: lung-on-chipsim
workstream: lung-on-chipsim
project: bioFM
diff_base: ecda7b0
hash_a: 14a6dba6c1dddf77c96db91e2be2fc17984a8d364e0a2c5d7618635698fb9a44
hash_b: a6b7f508d444e4c2948404cf436f8089410c7b61d65feecc7e355205b9d3d1eb
hash_c: b8b7d894075dcfd18a53e8603a6dc775ad9c2eac476b30d3b72749e2c15f9ec1
hash_d: b8b7d894075dcfd18a53e8603a6dc775ad9c2eac476b30d3b72749e2c15f9ec1
hash_d_source: "auto-approved — no principal 1B1"
hash_e: 061f12d72315c4642fed6d94fdf98acd90e24a5306853dd29236562a88a98a00
date: 2026-09-16T14:55
---

# Receipt: iteration-complete — bioFM

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): 14a6dba — artifact entering the gate
- E (final):    061f12d — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  a6b7f50
- C (triage):    b8b7d89
- D (principal): b8b7d89 — auto-approved — no principal 1B1

## Review Summary
§2 relative-stereo re-key + generated worksheet columns + record-content guard. QG: 9 findings kept (F-01..F-09), 8 fixed in atomic commits 262a4f0 90b6cde 8b2544c 7182b85 22150f5 98455c4 6118c50 392b955; F-05 (T14 worksheet destination) plan-level, escalated to CTO, not fixed. 22 dropped (<80) recorded in findings-20260916-s2.md. 663 passed / 4 skipped / 0 failed; ruff clean. Diff ecda7b0...HEAD also carries merged trunk content (plan, CTO dispatches, aiadlc-feedback) — disclosed, not claimed. Plan hash 33b43a9. Not pushed.
