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
hash_a: abf168468222fa0b910c7c75a28a23588c98d0428611cf7f422d41747a19c19c
hash_b: 8bb5d512906a052e904bd1a725ead640483bd4c9b2fcbdb9f9cf3bedb237e7f3
hash_c: 68d0d25bda8b73dc79596e3d55b11b4ab7efb28c058735ab42045afe25d25e26
hash_d: 68d0d25bda8b73dc79596e3d55b11b4ab7efb28c058735ab42045afe25d25e26
hash_d_source: "auto-approved, no principal 1B1; docs-only CTO directive on HACA-140 (comment 54e921d9)"
hash_e: abf168468222fa0b910c7c75a28a23588c98d0428611cf7f422d41747a19c19c
test_result: pass
date: 2026-11-27T05:58
---

# Receipt: pr-prep — perturb-seq-eval

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): abf1684 — artifact entering the gate
- E (final):    abf1684 — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  8bb5d51
- C (triage):    68d0d25
- D (principal): 68d0d25 — auto-approved, no principal 1B1; docs-only CTO directive on HACA-140 (comment 54e921d9)

## Review Summary
HACA-140, docs only: delta since receipt 3e70058 is 186a0c5 (CTO), notion-map.json synced_basis for publish-complete.md now names the 0.6.3 mirror from 5d15bff; checked against the CTO mirror report (comment 54e921d9): 0 findings; notion-map.json parses; hacp_linkcheck and hacp_sync_check pass; 1292 passed 0 failed 1 skipped (test role perturb-seq-eval); reviewer-ux: skipped (not user-facing). Prior receipt's deferred item (2) stands: runbook retired v0.5.x publish.state.json references, pre-existing
