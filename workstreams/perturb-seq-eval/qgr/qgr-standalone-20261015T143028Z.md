# Quality Gate Report: v0.6.0 deposit as new standalone records (principal 2026-10-15, CTO #620)

Scope: origin/main..HEAD. The change is 4924415 and 1504669, reviewed at 1504669 in a tree-bracketed scratch checkout. The fixes are a094bbd and 3e6ab55. The coord commits are QG-exempt.
Reviewers: code (10), security (4, none CRITICAL or HIGH), test (7, from 32 mutations). Scorer: 18 unique findings, 3 passed at 80 or above.
Hash A 59fdb7ff5f34df00ac752edb2090839e59a8f2c21a403c4f53f85e5806124d45 · Hash B 1d6cf7bba17b4e2a7b4f739b37e8fd61ad7ee05b3744abed7dc84387862587d6 · Hash C 59fac0588fd401ae6661fa71914641b921ae8dbb710bf5701290241d3141a196

## The ruling, applied
v0.6.0 is created as a NEW record on Zenodo and a NEW article on Figshare. The published records are never written to; that covers both v0.5.x records, Zenodo 20060974 (with 19748260 and the other Zenodo ids) and Figshare 32086920.
- **State.** The release has its own state file, `publish.yml` `state_file: publish.state.v060.json`, anchored to publish.yml's directory and printed at start. `publish.state.json` stays as the v0.5.x lineage record.
- **Lineage.** Carried by the isNewVersionOf relations, the Zenodo `notes` and the Figshare `references`.

## Guards, each test-proven
1. **Superseded records.** `PublishedRecordError` refuses a published record, as before. It also refuses any id in `SUPERSEDED_RECORDS`, even with no published flag (Zenodo, Figshare and OSF).
2. **Two separate gos.** `--dry-run` creates the draft and uploads; it never publishes. A run without it only publishes a draft recorded in the state file; with none recorded it raises `DraftRequiredError` before any write. So creating and publishing can never happen in one run.
3. **Resume.**
   - A same-name file with different content raises `DraftMismatchError`, and matching files are skipped.
   - Figshare metadata is sent again, so a fix made after the review is what gets published.
   - The DOI reserved at creation is reused.
   - Directory zips are byte-reproducible.
4. **State-file path.** It is contained in publish.yml's directory and may not be a symlink; a null value means unset.

Mutation proof: each of these makes at least one test fail.
- main() bypassing the state resolution;
- main() forcing a publish;
- the deny-list removed;
- the draft requirement removed;
- zips built from file mtimes;
- the state path not anchored.

| ID | Conf | Finding | Disposition |
|---|---|---|---|
| C1 | 80 | Runbook, header and docstring prescribe the in-place path and the legacy state | header, docstring and OSF comment fixed (a094bbd); research/PUBLISHING_RUNBOOK.md is outside the module, escalated to the CTO |
| C4/S1/T6 | 80 | State path relative to cwd: go 2 from another directory would create AND publish | anchored, contained, printed, plus DraftRequiredError (a094bbd) |
| T1 | 80 | main() state resolution untested | real main() harness (3e6ab55); T2 covered too |
| filtered | <80 | C2 C3 C5 C6 C9/S3 C10 S2 S4 T2 T3 T4 T5 fixed; C7 (.v5) to be confirmed by the read-only GETs; C8 (related_materials) not adopted | |

Environment: the test venv was rebuilt on Python 3.12, with the principal's approval. Finding: the analyser reproduces summary.json bit-for-bit only on Python 3.12 or later. Python 3.12 changed float `sum()` to compensated summation, so on 3.11 `architect_backbone_executed_entropy_nats` differs in the last bit. Raised with the CTO.

Checks (fresh, on the committed HEAD): pytest 1187 passed; ruff (E9, F63, F7, F82) clean; fill --check and render --check match. Failing: 0. Nothing was sent to any venue: no network writes and no reads.
