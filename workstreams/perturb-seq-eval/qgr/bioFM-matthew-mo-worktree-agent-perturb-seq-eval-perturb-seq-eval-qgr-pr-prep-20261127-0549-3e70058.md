---
receipt_version: 2
type: qgr
boundary: pr-prep
org: bioFM
principal: matthew-mo
agent: worktree-agent
workstream: perturb-seq-eval
project: perturb-seq-eval
diff_base: origin/main
hash_a: 3e70058e1f3c139fc52133027450b483f70155cda039c6008be553e4f7c98071
hash_b: 9b620459622104cd410ff88c396a671374dcf9aee3c3954b194738c5c620e068
hash_c: 2594e68587669c32c413318094c0184b0e60778b3207a3fe98ade087879b7160
hash_d: 2594e68587669c32c413318094c0184b0e60778b3207a3fe98ade087879b7160
hash_d_source: "auto-approved, no principal 1B1; docs-only CTO directive on HACA-140 (comment 1c2ef6fd)"
hash_e: 3e70058e1f3c139fc52133027450b483f70155cda039c6008be553e4f7c98071
test_result: pass
date: 2026-11-27T05:49
---

# Receipt: pr-prep — perturb-seq-eval

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): 3e70058 — artifact entering the gate
- E (final):    3e70058 — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  9b62045
- C (triage):    2594e68
- D (principal): 2594e68 — auto-approved, no principal 1B1; docs-only CTO directive on HACA-140 (comment 1c2ef6fd)

## Review Summary
HACA-140, docs only: publish-complete.md and PUBLISHING_RUNBOOK.md record 0.6.3 as published 2026-11-25 (Zenodo 10.5281/zenodo.24519260, Figshare 32086920 v9) and isIdenticalTo closed for v7-v9 (HACA-141), per CITATION.cff and publish.state.v063.json on main; CTO notion-map synced bump df3acf7 and origin/main merge kept; 1 reviewer (accuracy vs CITATION.cff, publish.yml, state files, LINEAGE_STATE_FILES): 2 findings, 0 fixed, 2 deferred: (1) notion-map synced 2026-11-27 covers the 0.6.2 mirror, so the row must be re-mirrored from this head and synced re-bumped (CTO); (2) runbook retired v0.5.x publish.state.json references, pre-existing; hacp_linkcheck and hacp_sync_check pass; 1292 passed 0 failed 1 skipped (test role perturb-seq-eval); reviewer-ux: skipped (not user-facing)
