---
receipt_version: 2
type: qgr
boundary: phase-complete
org: bioFM
principal: matthew-mo
agent: perturb-seq-eval
workstream: perturb-seq-eval
project: perturb-seq-eval
diff_base: 451f730
hash_a: 4749f2aa11e9e06479458d45dda89a75d86254e3c79383521f545aaa1fbe803a
hash_b: 509dafeb539da6f317a9925aab8db8aa6619535fcc3071da06a3b7fe05054b95
hash_c: 9d1aabb7fc3dd2a77a160ec0e80390f3c300f1b281200f25fb087b80309130ec
hash_d: 9d1aabb7fc3dd2a77a160ec0e80390f3c300f1b281200f25fb087b80309130ec
hash_d_source: "PENDING principal approval (phase boundary) — D=C placeholder, NOT an approval; boundary commit held for the principal"
hash_e: 4a2948aaef0efdd3c6c512289cc3a10a430cb35f09c2ccdb903b3611111f3d1f
date: 2026-09-25T12:54
---

# Receipt: phase-complete — perturb-seq-eval

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): 4749f2a — artifact entering the gate
- E (final):    4a2948a — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  509dafe
- C (triage):    9d1aabb
- D (principal): 9d1aabb — PENDING principal approval (phase boundary) — D=C placeholder, NOT an approval; boundary commit held for the principal

## Review Summary
P0-P5 QG accepted-finding fix set (17 ACCEPT-FIX-NOW findings) in commits 040f022..0f85e29. A=c46cd22...451f730 as reviewed. Evidence re-derived per CTO #363/#390: GREEN 748 passed with a bracket proven to fail and A==E; RED at 451f730 plus new tests: 68 failed (44 API-surface, 24 behavioural), 6 negative controls passed. Reviewers were unisolated (pre-#314); transcript audit found no writes; v1 evidence VOID. ACCEPT-FIX-AFTER-RULING items (C1,C2,C3,C7,C8,C13,C25,NEW-1,C6-prompt,C20) are NOT in this set and block the sweep pending a principal ruling.
