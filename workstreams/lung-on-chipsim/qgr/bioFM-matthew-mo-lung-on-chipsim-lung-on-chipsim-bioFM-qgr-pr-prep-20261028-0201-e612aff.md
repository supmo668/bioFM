---
receipt_version: 2
type: qgr
boundary: pr-prep
org: bioFM
principal: matthew-mo
agent: lung-on-chipsim
workstream: lung-on-chipsim
project: bioFM
diff_base: origin/main
hash_a: e612aff2a22350106af9ec176f8d2fab4b6e7bd025a510d5ad82e6fc807dfbcc
hash_b: 2df59b1e983184d4755d429d5ab6aa0ec138e55d34aaca621c050b296e1f3036
hash_c: fefcda262b3235b41a5745c0ce875a73072af4af71abeeddc43bb71416ba48ba
hash_d: c1ab56edc1aff6b53b99f60681e8314f1b52e9a2978fcce023a95ab1231c0c70
hash_d_source: "approvals.md — the principal's five-item ratification (row 66) and the CTO rulings at rows 65/67/71/72/73; hashed as its own artifact, NOT copied from Hash C"
hash_e: e612aff2a22350106af9ec176f8d2fab4b6e7bd025a510d5ad82e6fc807dfbcc
date: 2026-10-28T02:01
---

# Receipt: pr-prep — bioFM

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): e612aff — artifact entering the gate
- E (final):    e612aff — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  2df59b1
- C (triage):    fefcda2
- D (principal): c1ab56e — approvals.md — the principal's five-item ratification (row 66) and the CTO rulings at rows 65/67/71/72/73; hashed as its own artifact, NOT copied from Hash C

## Review Summary
Re-gate at the pushed tree after the Step-3 hash mismatch. 867 passed / 4 skipped / 0 failed unselected; 836/4/31 selected; ruff format --check and ruff check clean; ty 25 chipsim / 31 tests; both HACP guards green. Hash D independently derived. STATED GAP in Hash C: byte-level snapshot integrity unverified without the DVC bytes, including CI.
