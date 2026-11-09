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
hash_a: f525be92f495366f1d87e35fdf1119544c1be76752632f51cba9d92c1849f65c
hash_b: 1312eef3e216f97749a540b7a4e87aab308c986c6cdf58abc11b964656d1b313
hash_c: 2bd81e07b1f94863faccc7b952d10da269ed9c5be78037259934ec2a56b8b251
hash_d: 2bd81e07b1f94863faccc7b952d10da269ed9c5be78037259934ec2a56b8b251
hash_d_source: "auto-approved — no principal 1B1 occurred for this boundary; HASH_D = HASH_C"
hash_e: da83b3092cc336768397e02c14465099bddb3ca59ae69884f6fa4d82bc945bcb
date: 2026-11-04T16:11
---

# Receipt: pr-prep — lung-on-chipsim

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): f525be9 — artifact entering the gate
- E (final):    da83b30 — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  1312eef
- C (triage):    2bd81e0
- D (principal): 2bd81e0 — auto-approved — no principal 1B1 occurred for this boundary; HASH_D = HASH_C

## Review Summary
Coordination flush, 19 md files, zero code. 15 raw findings -> 9 survivors >=80 (4 merges, 3 false positives dropped). 1 receipt blocker: three personal emails on a public repo, redacted. 8 prose corrections incl. my own unsound grep prescription and a file-count-as-commit-count. Suite 909/4/0 fresh, ruff format+check clean, typecheck NOTSCOPED.
