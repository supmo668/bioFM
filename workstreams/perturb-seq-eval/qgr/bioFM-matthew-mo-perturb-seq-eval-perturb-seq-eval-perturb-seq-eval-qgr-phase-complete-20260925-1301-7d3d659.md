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
derived_from: 4a2948aaef0efdd3c6c512289cc3a10a430cb35f09c2ccdb903b3611111f3d1f
hash_a: 4749f2aa11e9e06479458d45dda89a75d86254e3c79383521f545aaa1fbe803a
hash_b: 509dafeb539da6f317a9925aab8db8aa6619535fcc3071da06a3b7fe05054b95
hash_c: 9d1aabb7fc3dd2a77a160ec0e80390f3c300f1b281200f25fb087b80309130ec
hash_d: 9d1aabb7fc3dd2a77a160ec0e80390f3c300f1b281200f25fb087b80309130ec
hash_d_source: "PENDING principal approval (phase boundary) — D=C placeholder, NOT an approval; boundary commit held for the principal"
hash_e: 7d3d659e9a054e14249c1186bf9404037288ea8c7ac0cd27c8eb84d8178b5cba
date: 2026-09-25T13:01
---

# Receipt: phase-complete — perturb-seq-eval

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): 4749f2a — artifact entering the gate
- E (final):    7d3d659 — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  509dafe
- C (triage):    9d1aabb
- D (principal): 9d1aabb — PENDING principal approval (phase boundary) — D=C placeholder, NOT an approval; boundary commit held for the principal

## Review Summary
DERIVED from 4a2948a (CTO #392 option i). Entire delta since receipt 80817b1 = three non-code paths: agency.yaml (per-agent quality keys, 3420b21), workstreams/perturb-seq-eval/qgr/evidence/qg-p0p5-stophook-proof.txt (aab0b9a), .claude/usr/matthew-mo/perturb-seq-eval/dispatches/dispatch-to-cto-p0-p5-executed-...-1300.md (6e79722). NO source or test change. Only agency.yaml enters Hash E (qgr/** and dispatches are diff-hash-excluded). Gate content otherwise identical to 4a2948a: 17 ACCEPT-FIX-NOW findings, GREEN 748, RED 68/6.
