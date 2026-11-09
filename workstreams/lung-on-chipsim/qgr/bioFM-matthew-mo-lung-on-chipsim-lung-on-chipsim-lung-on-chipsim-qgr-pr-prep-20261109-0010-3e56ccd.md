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
hash_a: 6559d66af043d70cf3c8dfb6b08a225019e7e7ed71e8e9f3209f1fe06e51ba07
hash_b: 2d7d12153820a017b22b2379dbd7424454ff9e5fd0744844c6bc4553108eec8a
hash_c: 31b33e82e29b6d37a2e40789282f16d1bbc676a813bdee6e312c17c89b46fc46
hash_d: 31b33e82e29b6d37a2e40789282f16d1bbc676a813bdee6e312c17c89b46fc46
hash_d_source: "principal approved the SCOPE in-session via AskUserQuestion (2026-11-08: 'Fix it now, in this gate' + 'Rename both colliding functions'), not via a 1B1 transcript, so D=C"
hash_e: 3e56ccda5cea457248a00ed9bd30e9dc72972a87ee5c2edd5be59157abdb0cfa
date: 2026-11-09T00:10
---

# Receipt: pr-prep — lung-on-chipsim

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): 6559d66 — artifact entering the gate
- E (final):    3e56ccd — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  2d7d121
- C (triage):    31b33e8
- D (principal): 31b33e8 — principal approved the SCOPE in-session via AskUserQuestion (2026-11-08: 'Fix it now, in this gate' + 'Rename both colliding functions'), not via a 1B1 transcript, so D=C

## Review Summary
Cross-module constant+callable collision closed in chipsim.transport, plus the S6 writer-guard asymmetry it exposed. 17 findings from 4 reviewers + own review, ALL fixed, 0 deferred. 12 of the 17 were defects in my OWN new guard. NOTE: Hash A was taken against c2094fd4 BEFORE the origin/main merge; Hash E is against origin/main, so the two bases differ by that merge - stated rather than silently reconciled. Suite 929 passed / 4 skipped / 0 failed (911 before, +18 tests). ruff format+check clean; ty 25 on chipsim, baseline unchanged. Tree-bracket reported TREE_CHANGED: the only moved paths were two hook-written .aiadlc/instincts counters, outside the gated artifact (Hash A/E are committed diffs). Disclosed, not passed off as clean.
