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
hash_a: 18a5e72
hash_b: 6ef610821987a6a2a57d4e71e4e5073d39eafae643c65af49e65916e77deab88
hash_c: 89a087c29ea65d396a27708ac38315cb968aed403f062dcaeac7235138a640a2
hash_d: 89a087c29ea65d396a27708ac38315cb968aed403f062dcaeac7235138a640a2
hash_d_source: "auto-approved, no principal 1B1; docs-only CTO-filed task HACA-155"
hash_e: 18a5e72
test_result: pass
date: 2026-11-27T06:06
---

# Receipt: pr-prep — perturb-seq-eval

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): 18a5e72 — artifact entering the gate
- E (final):    18a5e72 — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  6ef6108
- C (triage):    89a087c
- D (principal): 89a087c — auto-approved, no principal 1B1; docs-only CTO-filed task HACA-155

## Review Summary
HACA-155, docs only (research/PUBLISHING_RUNBOOK.md): §5 names this release's state_file in publish.yml (publish.state.v063.json) instead of the v0.5.x publish.state.json; retired §6.5 recipe line marks publish.state.json as the v0.5.x lineage record; §6.5 'What to do instead' now says next version of the same records (Zenodo concept 10.5281/zenodo.19716140, Figshare 32086920, revision_of), not 'new standalone record'; lineage note drops §5 from its historical list. Facts checked against publish.yml, LINEAGE_STATE_FILES, ALLOWED_REVISIONS, CITATION.cff on main. 0 in-scope findings; 1 out-of-scope deferred (guard table PublishedRecordError row, pre-existing). Not Notion-mirrored. 1285 passed 0 failed 8 skipped (test role perturb-seq-eval). reviewer-ux: skipped (not user-facing).
