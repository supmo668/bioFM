---
receipt_version: 2
type: qgr
boundary: iteration-complete
org: bioFM
principal: matthew-mo
agent: lung-on-chipsim
workstream: lung-on-chipsim
project: bioFM
diff_base: 7098f71
hash_a: 5c9b6d34a3d6e3c756193ebaba4ec6a27d985ea9a2aa89c3b5dff152d95d218e
hash_b: 59755ce91837fc0e72b4f8f9be90411a1d3cbb01439ce02b7f6320c785f3f2c0
hash_c: 71d6fc7036bce64261f1b372ac83c5807da0621d8b8d5b4ceb69610769eefc6f
hash_d: 71d6fc7036bce64261f1b372ac83c5807da0621d8b8d5b4ceb69610769eefc6f
hash_d_source: "auto-approved — no principal 1B1 (iteration boundary)"
hash_e: f0c6bb359fac04cf0c6a82ec6d1c74ab4ce6c98e352c01786bb30bfcdb3a1911
date: 2026-09-16T22:31
---

# Receipt: iteration-complete — bioFM

## Verifiable hashes (recomputed + matched by receipt-verify)

- A (original): 5c9b6d3 — artifact entering the gate
- E (final):    f0c6bb3 — artifact after all fixes (verification anchor)

## Procedural attestation log (recorded, not independently verifiable)

These attest that each stage ran. Their inputs are ephemeral (review output,
triage notes, 1B1 transcripts) and cannot be reconstructed after the fact, so
they are a procedural log — NOT a cryptographic chain.

- B (findings):  59755ce
- C (triage):    71d6fc7
- D (principal): 71d6fc7 — auto-approved — no principal 1B1 (iteration boundary)

## Review Summary
§8: the E-08 fix still printed E-08's sentence. Four reviewers and my own pass each reproduced, through the shipped CLI, a clean report with exit 0 over a tree that was never read — seven working false-cleans in total. The root SELECTION had been made structural; the root VALIDATION and the file LISTING were left able to fail silently, and they compose. The anti-vacuity guard for exactly this already existed in the tests (check=True, len>100, every path resolves) and not in the command a human runs. Now: RecordContentScanError with exit 3, distinct from exit 2; no fallback to the narrow root; git asked to resolve the candidate so a stray .git raises; one witness check (the listing must contain this module's own tracked file, and every path must resolve) covering an unrelated enclosing repo, a foreign index, an emptied listing and a sparse checkout together. Steerable-despite-a-correct-root closed: all GIT_* dropped from the scan's environment; core.fsmonitor disabled, which was code execution from the scanned repo; owners must carry a tracked marker, since libs/ghost-lib/payload.bin reported owner=ghost-lib and exit 0; paths escaped, since one filename could draw a fake clean report over the real one. The report now states its root, its denominator, the package copy it ran from, the submodules it did not scan, and that another project's files fail no gate today. The previous E-08 test PASSED with the bug fully reintroduced and is deleted; the regression is pinned by command-equals-function instead of a >=20 floor under a number this mechanism exists to drive to zero. 12 mutants, 11 killed first pass, 1 survivor (a git failure inside a VALID checkout) closed with a new test: 12/12. Five fixture-satisfied assertions in my §7 tests repaired and re-proved against the reviewer's message-only mutants.
