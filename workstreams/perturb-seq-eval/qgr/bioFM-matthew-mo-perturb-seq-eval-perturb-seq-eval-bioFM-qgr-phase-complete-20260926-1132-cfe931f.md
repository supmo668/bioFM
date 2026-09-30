---
receipt_version: 2
type: qgr
boundary: phase-complete
org: bioFM
principal: matthew-mo
agent: perturb-seq-eval
workstream: perturb-seq-eval
project: bioFM
diff_base: 451f730
derived_from: 7d3d659e9a054e14249c1186bf9404037288ea8c7ac0cd27c8eb84d8178b5cba
hash_a: 4749f2aa11e9e06479458d45dda89a75d86254e3c79383521f545aaa1fbe803a
hash_b: 509dafeb539da6f317a9925aab8db8aa6619535fcc3071da06a3b7fe05054b95
hash_c: 9d1aabb7fc3dd2a77a160ec0e80390f3c300f1b281200f25fb087b80309130ec
hash_d: 913c5b33a5f2d6453ecdeaee4950dbc38dc2f2e8597ba34f5536f7f55ebd1a72
hash_d_source: "PRINCIPAL APPROVED the P0-P5 phase boundary, relayed by CTO dispatch #421 (2026-09-26, 'DECISION 1: the P0-P5 phase boundary is APPROVED'). D = sha256 of the #421 payload as committed on main at 36753e3"
hash_e: cfe931f656e240646446740ed585a72e520de16e70194510f15c72ce6f350311
date: 2026-09-26T11:32
---

# Receipt: phase-complete — bioFM

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): 4749f2a — artifact entering the gate
- E (final):    cfe931f — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  509dafe
- C (triage):    9d1aabb
- D (principal): 913c5b3 — PRINCIPAL APPROVED the P0-P5 phase boundary, relayed by CTO dispatch #421 (2026-09-26, 'DECISION 1: the P0-P5 phase boundary is APPROVED'). D = sha256 of the #421 payload as committed on main at 36753e3

## Review Summary
DERIVED from 7d3d659 (CTO #392 standing order: any commit after signing needs a derived receipt). Entire in-scope delta since 7d3d659 = two documentation files: docs/hacp/index.md and docs/hacp/perturb-seq-eval-decision-p0p5.md (0340e34, HACP floor copies). NO source or test change. Gate content identical to 4a2948a/7d3d659: 17 ACCEPT-FIX-NOW findings, GREEN 748, RED 68/6. Hash D is now the principal's approval (#421), replacing the D=C placeholder; this receipt licenses the --boundary phase commit. Signed with project=bioFM (the repo's receipt convention that git-safe-commit --boundary verifies against; the parent chain 4a2948a/7d3d659 was signed project=perturb-seq-eval, which the gate cannot see).
