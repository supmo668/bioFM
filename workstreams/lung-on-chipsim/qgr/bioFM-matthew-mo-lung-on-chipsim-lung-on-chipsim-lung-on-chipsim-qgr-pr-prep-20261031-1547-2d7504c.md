---
receipt_version: 2
type: qgr
boundary: pr-prep
org: bioFM
principal: matthew-mo
agent: lung-on-chipsim
workstream: lung-on-chipsim
project: lung-on-chipsim
diff_base: origin/main
hash_a: 2d7504c0d13fa0e54e79517d6d50d1469e4082908c82c4989aa3b363acb8a7f6
hash_b: de63e58e0cd78e5e7a971fcd9a16079a32f79ec5dd456cc57fa770fcd37b83c4
hash_c: b1aa46c476740b798b74de9bbc7465bcbfb4b614db0ecaa36f88a022cc206f4c
hash_d: 281a7d6406fd9d5b4d93b825336e77dc0ac52f467181bf929add3afcf22dc8b3
hash_d_source: "approvals.md at its current state (now carrying rows 80-86); no 1B1 transcript for this re-gate, so the principal's own decision record stands in and C != D is asserted at signing"
hash_e: 2d7504c0d13fa0e54e79517d6d50d1469e4082908c82c4989aa3b363acb8a7f6
date: 2026-10-31T15:47
---

# Receipt: pr-prep — lung-on-chipsim

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): 2d7504c — artifact entering the gate
- E (final):    2d7504c — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  de63e58
- C (triage):    b1aa46c
- D (principal): 281a7d6 — approvals.md at its current state (now carrying rows 80-86); no 1B1 transcript for this re-gate, so the principal's own decision record stands in and C != D is asserted at signing

## Review Summary
RE-GATE after rows 83-86: findings-staging ledgers moved to lung-on-chipsim-staging and removed from the PR head by a new commit (no rewrite of the load-bearing stage2 remote); adjudication.py comment corrected per row 82 (comment-only, verified). Review DERIVED from the 00940e9 four-reviewer fan-out because the only code delta is comment-only; verification re-run in full: 909 passed / 4 skipped / 0 failed
