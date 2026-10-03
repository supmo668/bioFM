---
receipt_version: 2
type: qgr
boundary: iteration-complete
org: bioFM
principal: matthew-mo
agent: lung-on-chipsim
workstream: lung-on-chipsim
project: bioFM
diff_base: 1c4f500
hash_a: 75da239cdda595c8ae8ee398585a6219970789917f955f45fd16aab98b6ceee2
hash_b: 3e8d494cabcad3874ef7f632b30da18c3ff75f2a0e6a2b67d88a49e5a812965b
hash_c: 1a23a5156287bfcae4a92704fb9346a62cc2d56baf55d2de13191e2bf2efce56
hash_d: 1a23a5156287bfcae4a92704fb9346a62cc2d56baf55d2de13191e2bf2efce56
hash_d_source: "auto-approved — no principal 1B1 (iteration boundary)"
hash_e: 45c68fc5841959eac8d6b01130f54d60f2afe190433e0a093659ebea52368c8f
date: 2026-09-17T00:59
---

# Receipt: iteration-complete — bioFM

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): 75da239 — artifact entering the gate
- E (final):    45c68fc — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  3e8d494
- C (triage):    1a23a51
- D (principal): 1a23a51 — auto-approved — no principal 1B1 (iteration boundary)

## Review Summary
§9: E-10's ruled correction, E-08b's floor, and E-02 — the declaration surface built and READ. 'Declared' had been a state the code could describe and never reach: an empty frozenset nothing populated, with five tests iterating it and four monkeypatching it, and the oldest of those vacuous since it was written because its 'binary' fixture decoded as UTF-16. Now: two data files, each owning only what it is allowed to own, entries carrying sha256 or derived_from and never a bare path, and a validator that refuses a stale pin, a dead path, a foreign path, a readable file, a container by magic, a double exemption and a dispatch payload. The review found six ways to get a TRACEBACK out of the one command whose contract is that it must never fail silently, and four false-clean shapes the first real entry could reach — the sharpest being that the registry POLICED ITSELF: delisting a project made its subtree unowned and therefore repo-root-declarable, demonstrated end-to-end as exit 2 becoming exit 0 with a payload present. Placement is now judged against the marker-backed set the registry cannot shrink, and an absent declaration file is no longer an empty one. 12 mutants had survived the entire 851-test suite, including the commit's own headline claim that a broken declaration fails the gate; 18 tests added and all 16 mutants re-run in a clone — zero survivors. Ninth and tenth vacuity of the tmp_path-basename family, both in tests I wrote this session AFTER adopting the rule. Four escalations: exit-code semantics for a broken declaration, a load-once surface object, per-entry defect collection, and two notes for the E6-6 clause.
