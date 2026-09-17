---
receipt_version: 2
type: qgr
boundary: iteration-complete
org: bioFM
principal: matthew-mo
agent: lung-on-chipsim
workstream: lung-on-chipsim
project: bioFM
diff_base: 1a5d72f
hash_a: f520f1272342d1698801f35b0d82e1ae8480604d36611c8ab93c059388e7b0b2
hash_b: cc9363ff4cbd33384197be48c888dd5424c9de0e6373ae0b990cad0dce5a9329
hash_c: 150e05e2a461d8c2517ff91538d3566032c230099b682041e874204c2ffc0c8c
hash_d: 150e05e2a461d8c2517ff91538d3566032c230099b682041e874204c2ffc0c8c
hash_d_source: "auto-approved — no principal 1B1"
hash_e: bf6ed1ac49c598a0f82f17b6d74783a7aaadd79da45155e100ede5fc31d06082
date: 2026-09-16T21:42
---

# Receipt: iteration-complete — bioFM

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): f520f12 — artifact entering the gate
- E (final):    bf6ed1a — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  cc9363f
- C (triage):    150e05e
- D (principal): 150e05e — auto-approved — no principal 1B1

## Review Summary
§7: r2.20 allow-list + r2.21 E6-2/E6-4/E6-5 + r2.22 E6-1b. FULL roster on a throwaway copy; all four reviewers confirmed the tree ended byte-identical. The gate found FOUR EXECUTED ways a record-bearing payload still reached a tracked path: the .tmp sibling symlink (bypass #3 from the r2.19 post-mortem, moved one filename over, inside the guard written to close it), a hard link, $TMPDIR redirecting the allow-list at the whole tree, and .gitignore re-including *.sha256 and *.dvc inside the 'untracked' roots. It also found that 'containers are ALWAYS READ' was false for every real container: the repo's own 34.6 MB h5ad scanned 4,270 chars — six of ~41,000 identifiers — and the 0.01s I had cited as proof the cost was acceptable was a measurement OF the elision. Now 1,212,890 chars, zero elision markers, 0.03s. Also: the registry recognised two method names, so a CLI persisting the complete record via pq.write_table survived the FULL SUITE, and it declared a PHANTOM function that does not exist; my symlink test passed on its OWN DIRECTORY NAME (the third name-collision vacuity this session); ownership invented projects from stray filenames, failing nobody's gate; a binary named .md was double-exempt; and the undeclared report reached nobody until the new record-content-report subcommand. Four phases, 24 findings fixed (7924cd0 ca273dc 4de0b33 4b28055), 7 escalated — including two more record-bearing writers (fetch_snapshot, merge_report.main) that were invisible until the registry was widened, and E6-1's per-project declaration data, which is still unbuilt. THE PATTERN: nearly every defect was the lesson of the clause above it, reappearing one level down in my implementation of that clause. 814 passed / 5 skipped; ruff check + format clean. Plan 6eba1bb. Not pushed yet.
