---
receipt_version: 2
type: qgr
boundary: iteration-complete
org: bioFM
principal: matthew-mo
agent: lung-on-chipsim
workstream: lung-on-chipsim
project: bioFM
diff_base: 0c4e181
hash_a: 3e6ce53b30f2cc3162da2e61e01cc2c3f7476063766c3fd0034c1c3d78f57f83
hash_b: bffb7dd061267c6faca470899184f2217b8bff1247699eb8f2c9f065bd51b11a
hash_c: 1ac7096fdcdf56947bba7b408857f60b167bb10864c80812d2be40c94aa8edde
hash_d: 1ac7096fdcdf56947bba7b408857f60b167bb10864c80812d2be40c94aa8edde
hash_d_source: "auto-approved — no principal 1B1"
hash_e: 5d60397149967849e3218d8a0b95f974bcfb7b0b1986a0afecc3798ff7952d1e
date: 2026-09-16T15:32
---

# Receipt: iteration-complete — bioFM

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): 3e6ce53 — artifact entering the gate
- E (final):    5d60397 — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  bffb7dd
- C (triage):    1ac7096
- D (principal): 1ac7096 — auto-approved — no principal 1B1

## Review Summary
§3 T14/T15 r2.18 (plan 2325057): export_tracked_adjudication + T15 reads the tracked five-column file and recomputes stereo_is_relative from compounds. QG: 4 reviewers + own review; 14 findings fixed (commits add44c5 61da71b 87179a4 b4159e7), 6 escalated to CTO (SEC-1 worksheet writer can target a tracked path; plan done-when stale; unstated extra-column refusal; T14 CLI entry; read_pgp_labels drops the flag; names typed into cells). 1 finding REJECTED as not reproducible (CODE-1). Three mutations that previously left the suite green are now killed, verified. 703 passed / 5 skipped / 0 failed; ruff check clean; ruff format clean for files in scope, 5 pre-existing files still fail and are disclosed, not reformatted. Not pushed.
