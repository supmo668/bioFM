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
hash_a: 5294b2a327032b8c1c5643793f4b514847001da2f6bdc633770d6fd31428ec31
hash_b: 67b7b11f966f1e286ded9115528c696f52cfe702010bf9909b13dfd66e2c8580
hash_c: 7ea6ecd89dccedb58238512be8fce1123f4bd4f03ca0588cbaf6cbb4c2017f4c
hash_d: 7ea6ecd89dccedb58238512be8fce1123f4bd4f03ca0588cbaf6cbb4c2017f4c
hash_d_source: "auto-approved — no principal 1B1 for the fix cycle; CTO authorized the pr-prep re-run (dispatch #14 follow-up)"
hash_e: e019a774a19182494b7ec4b6624070dbad147fedba1d2550bd92d506fe3aa3e9
date: 2026-09-01T20:02
---

# Receipt: pr-prep — bioFM

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): 5294b2a — artifact entering the gate
- E (final):    e019a77 — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  67b7b11
- C (triage):    7ea6ecd
- D (principal): 7ea6ecd — auto-approved — no principal 1B1 for the fix cycle; CTO authorized the pr-prep re-run (dispatch #14 follow-up)

## Review Summary
P0.4 pr-prep re-gate: closed T7a findings C1 (seal verification mandatory), C2 (preimage binds attestation fields + filename; fixture/live digest collision broken — hardening, not forgery-proof), C3 (false-success write), C4 (missing entrypoint), H5, H6 (self-certifying manifest), AM-3 comment. Reframed the seal as tamper-evidence, never proof a human attested. 301 passed / 6 skipped offline, 15/1 network, ruff clean. Each reported attack reproduced as closed.
