---
receipt_version: 2
type: qgr
boundary: iteration-complete
org: bioFM
principal: matthew-mo
agent: lung-on-chipsim
workstream: lung-on-chipsim
project: bioFM
diff_base: 660d600
hash_a: 4efd7737f87903e73b125a62149c26ea7732dc1dfd6ba97501da6c7786a8fe78
hash_b: 736376190251a95ab53963cbbc5454cf2167f1e6800474493c4315a55d5e3a8f
hash_c: 736376190251a95ab53963cbbc5454cf2167f1e6800474493c4315a55d5e3a8f
hash_d: 736376190251a95ab53963cbbc5454cf2167f1e6800474493c4315a55d5e3a8f
hash_d_source: "principal standing ruling: advance M0a critical path"
hash_e: 4efd7737f87903e73b125a62149c26ea7732dc1dfd6ba97501da6c7786a8fe78
date: 2026-09-18T14:21
---

# Receipt: iteration-complete — bioFM

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): 4efd773 — artifact entering the gate
- E (final):    4efd773 — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  7363761
- C (triage):    7363761
- D (principal): 7363761 — principal standing ruling: advance M0a critical path

## Review Summary
S17: T13's worksheet writer had ~30 test call sites and NO production caller, on the route to the principal's 60-90 minute T14; and T6's done-condition was verified only against the fixture. The r2.10 defect restored proves it: fixture GREEN, real-snapshot RED.
