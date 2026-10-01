# Gate 5 Step 8: Iron-Law verification, run fresh this session

Suite and extended tier ran at `2d25a2b`. The only later commit, `45b764f`, changes comments in agency.yaml and in the matrix test; its binding tests (WIRED, CITED, EXACTLY) re-ran green, and format, lint and both gates re-ran at `45b764f`.

| Check | Command | Result |
|---|---|---|
| Format | `cd projects/lung-on-chipsim && uv run ruff format --check .` | exit 0 |
| Lint | `cd projects/lung-on-chipsim && uv run ruff check .` | exit 0 |
| Typecheck | none configured (`typecheck_command_lung-on-chipsim: ""`, deliberate) | N/A |
| Tests | `cd projects/lung-on-chipsim && uv run --frozen pytest -q -p no:cacheprovider` | exit 0; 1171 passed, 4 skipped; 244 s; 1.86 GB peak RSS |
| **Extended tier** | `cd projects/lung-on-chipsim && AIADLC_ACCESSION_ORACLE_EXTENDED=1 uv run pytest -q -p no:cacheprovider tests/test_accession_pattern_matrix.py` | exit 0; 15 passed; 248 s; 2.89 GB peak RSS |
| Record-content gate (STAGED) | `uv run --frozen chipsim record-content-gate` | exit 0 |
| Record-content report (WORKTREE) | `uv run --frozen chipsim record-content-report` | exit 0 |

Exit codes were read directly, never through a pipe. The suite went from 1143 passed at the range base (561be17) to 1159 at be6e07e (pre-gate) to 1171 after the fix cycle.

## Fix-cycle commits (atomic, one per finding)
```
074ada2 lung-on-chipsim/lung-on-chipsim: coord: gate 5 bracket evidence for E-22 r2.47a WI-1 + WI-2 (561be17..be6e07e), written before any r
5427d33 lung-on-chipsim/lung-on-chipsim: fix: escape the exception text in the exit-2 DeclarationDataUnusable report (r2.28: every interpola
46f4bbe lung-on-chipsim/lung-on-chipsim: fix: an unusable exclusion ledger no longer DISCARDS the readability listing and accession hits alr
700e0b4 lung-on-chipsim/lung-on-chipsim: fix: escape paths in accession and ledger rows (r2.28, every printed path)
eb960df lung-on-chipsim/lung-on-chipsim: test: shipped commands must propagate the bare base class and unrelated errors, not only the guard-
2fccd89 lung-on-chipsim/lung-on-chipsim: test: could-not-scan after the listing reports the listing count and None for the accession half
11152a5 lung-on-chipsim/lung-on-chipsim: test: ceiling rows prove the file is read IN FULL, not merely opened (tail token only a full read c
5675c80 lung-on-chipsim/lung-on-chipsim: test: bind the two SCANNER call sites, not only the constant, over the generated contexts
4f4392c lung-on-chipsim/lung-on-chipsim: test: code point x body axis beyond the probe body; the 'single-code-point contexts are CLOSED' cla
b0b4991 lung-on-chipsim/lung-on-chipsim: docs: errors.py and the report command no longer say a guard defect lands in exit 3; r2.47(d) routi
b23a39c lung-on-chipsim/lung-on-chipsim: docs: the coverage-trailer comment states exactly where the figure is printed (it was not 'on BOTH 
b70f354 lung-on-chipsim/lung-on-chipsim: test: the extended-tier command is pinned to its exact token list (substring checks passed four neu
0a6a032 lung-on-chipsim/lung-on-chipsim: test: axis-1 bodies must be ASCII digits (a digits-to-letters mutant passed lengths, count and uniq
7aa6504 lung-on-chipsim/lung-on-chipsim: test: bind the ratio comparison structurally (>= against the named constant) plus per-mille rows; r
6538276 lung-on-chipsim/lung-on-chipsim: test: the accession section has ONE entry line per token-bearing file (set equality let a duplicate
ed4c5c5 lung-on-chipsim/lung-on-chipsim: test: the cited-tests check covers every file the range edits, and path::name citations
2d25a2b lung-on-chipsim/lung-on-chipsim: docs: gate 5 R15 nits -- line citations, long line, injected-fault labels, None wording, ceiling eq
45b764f lung-on-chipsim/lung-on-chipsim: docs: record the extended tier's measured cost after gate 5's code point x body axis (248 s, 2.89 G
```

## git diff 561be17..HEAD --stat
```
 agency.yaml                                        |   6 +
 .../lung-on-chipsim/chipsim/guards/decoding.py     |  15 +-
 projects/lung-on-chipsim/chipsim/guards/errors.py  |  24 +-
 .../chipsim/guards/record_content.py               |  11 +-
 projects/lung-on-chipsim/chipsim/pipeline.py       |  23 +-
 projects/lung-on-chipsim/chipsim/record_content.py | 121 ++++++-
 .../lung-on-chipsim/tests/readability_reference.py |  26 +-
 .../tests/test_accession_pattern_matrix.py         | 375 +++++++++++++++++++--
 .../tests/test_readability_differential.py         | 221 ++++++++++--
 .../tests/test_record_content_entry_point.py       | 359 +++++++++++++++++++-
 .../tests/test_record_content_guard.py             |   2 +-
 .../qgr/evidence/gate5-e22-r247-bracket.md         | 116 +++++++
 12 files changed, 1169 insertions(+), 130 deletions(-)
```
