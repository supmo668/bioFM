---
receipt_version: 2
type: qgr
boundary: iteration-complete
org: bioFM
principal: matthew-mo
agent: lung-on-chipsim
workstream: lung-on-chipsim
project: bioFM
diff_base: 31867d2
hash_a: 0c9935e2d9d3285706b8236a05f1b7fabe8dea68ee4b5ba3e639d7d13beecf3c
hash_b: c371037f1e0c1ddef823b17d67a70ae44127e8ed0c448248ea96152b34a4175d
hash_c: 699e2d4919dea03edeb028097ea2af8a75df1cbba09a987cf9befc047badd1a0
hash_d: 699e2d4919dea03edeb028097ea2af8a75df1cbba09a987cf9befc047badd1a0
hash_d_source: "auto-approved — no principal 1B1 (iteration boundary)"
hash_e: 90e392f206aeef566595abdc11224f46fc06b832178bf1994f54f7b29b3b9f66
date: 2026-09-17T03:17
---

# Receipt: iteration-complete — bioFM

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): 0c9935e — artifact entering the gate
- E (final):    90e392f — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  c371037
- C (triage):    699e2d4
- D (principal): 699e2d4 — auto-approved — no principal 1B1 (iteration boundary)

## Review Summary
§10: E6-6's extraction (1,196 lines into chipsim/guards/record_content.py), E-13/E-13b/E-14/E-15 as ruled, the bare-assert fix, and E6-7 — one entry point a non-pytest consumer can call, with the FAIL in it. The MOVE was confirmed clean by an AST census: nothing lost, duplicated or reordered, both predicates at the right call sites, the guard with zero dependency on ingest, the live report byte-identical. ALL THE RISK WAS IN THE BEHAVIOUR CHANGES, and the two worst defects each shipped beneath a sentence of mine asserting the opposite: a policy default documented as fail-closed that was fail-OPEN in one direction (exempt nothing -> the double-exemption defect never fires -> the declaration holds -> the file is CLEARED), and a broken declaration file that made the report's rows fail-open under a banner reading 'more files fail, never fewer'. Both measured by reviewers, not argued. The snapshot covered the YAML and not the verdicts, so a rebuilt artifact produced ONE REPORT THAT DISAGREED WITH ITSELF — E-14's failure inside the fix for E-14. 22 mutants were run and TEN SURVIVED, three of them inside tests I had written to prove the very property they mutate: the -O test never ran the guard under -O, the absent-file test could not tell absent from empty, and nothing bound the policy the CLI passes (two mutants dropping it entirely passed all 895 tests). Eleventh vacuity of this family. All ten now killed on a GREEN baseline — my first mutation run reported 'no survivors' from a clone whose baseline was already 8-failed, which I caught before reporting it. Four escalations: a required ScanContext with no resolving fallback plus the renderer's data/presentation split, two further pure-move extractions, the near-inert readability waiver, and a clean-looking header on a structural failure.
