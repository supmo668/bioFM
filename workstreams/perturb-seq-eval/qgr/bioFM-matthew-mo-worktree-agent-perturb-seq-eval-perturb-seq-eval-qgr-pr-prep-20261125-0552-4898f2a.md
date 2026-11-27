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
hash_a: 2fd96cd46b95dabb061d787e60c0efb0bf4bc53b5c4bf512ff5ec9ede3e1c8f9
hash_b: c8717c90b380b65430a56ad87b0a9b9cf54f9deaa7396f836a45c662e884e13b
hash_c: 9aa3dcfb279dde949556a4197bcd1ac4b3cd086ee0a9f894a1297362f57c6053
hash_d: 9aa3dcfb279dde949556a4197bcd1ac4b3cd086ee0a9f894a1297362f57c6053
hash_d_source: "auto-approved, no principal 1B1; docs-only follow-up of HACA-126 assigned by the CTO"
hash_e: 4898f2a260267c854d07845d4ea9f283d7327bf69406fb19a15eceaac8c27901
test_result: pass
date: 2026-11-25T05:52
---

# Receipt: pr-prep — perturb-seq-eval

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): 2fd96cd — artifact entering the gate
- E (final):    4898f2a — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  c8717c9
- C (triage):    9aa3dcf
- D (principal): 9aa3dcf — auto-approved, no principal 1B1; docs-only follow-up of HACA-126 assigned by the CTO

## Review Summary
HACA-140, docs only (2 files): runbook names publish.state.v063.json for the prepared 0.6.3 and the four lineage records the submitter refuses; HACP publish-complete page states 0.6.1 (Zenodo 10.5281/zenodo.24430429, Figshare v7) and 0.6.2 (Zenodo 10.5281/zenodo.24518637, Figshare v8), 0.6.3 prepared and not published, no 0.6.3 DOI; 1 reviewer (accuracy vs CITATION.cff, publish.yml, state files, LINEAGE_STATE_FILES): 3 findings, 2 fixed (8e18b44), 1 deferred: hacp_sync_check fails on publish-complete.md until the Notion mirror and synced bump (CTO brief to scribe-writer); hacp_linkcheck passes; 1292 passed 0 failed 1 skipped (test role perturb-seq-eval); reviewer-ux: skipped (not user-facing)
