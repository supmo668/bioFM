---
receipt_version: 2
type: qgr
boundary: iteration-complete
org: bioFM
principal: matthew-mo
agent: perturb-seq-eval
workstream: perturb-seq-eval
project: bioFM
diff_base: 535cb68
hash_a: 91d040195a4356a0195b00ede5a4ed86c412208f0a5ebf5cf3b233a73b41ce2d
hash_b: a6fac3d1defe5059155130bd8548e1793552d7618e495f63bf79f4da427107c6
hash_c: a1f124060a7e3545b4cb5a326445548b22992d8b47e85e2880c5195c074eec6b
hash_d: a1f124060a7e3545b4cb5a326445548b22992d8b47e85e2880c5195c074eec6b
hash_d_source: "auto-approved — no principal 1B1 (amendment 4 ruled by the principal 2026-09-29; CTO #480/#482/#484/#486)"
hash_e: 36b0e1d4483712f290ef6970b579ea16e556d11a5bd6f39aef58c4a28a9ceef2
date: 2026-09-28T20:49
---

# Receipt: iteration-complete — bioFM

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): 91d0401 — artifact entering the gate
- E (final):    36b0e1d — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  a6fac3d
- C (triage):    a1f1240
- D (principal): a1f1240 — auto-approved — no principal 1B1 (amendment 4 ruled by the principal 2026-09-29; CTO #480/#482/#484/#486)

## Review Summary
A4 client gate: AnthropicClient + wiring; 4 reviewers + own; 13 findings >=80 all fixed (6 defects, 5 test gaps, 2 docs); fixes 846c770 2bf75f3 3ade237 00fae29; 1123 tests green
