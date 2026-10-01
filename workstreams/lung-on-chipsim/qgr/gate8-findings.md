# Gate 8 — consolidated findings

Base `288821d` → HEAD `14baa46`. Hash A `fecd622b755c7f674913ce2b2d22188e325b1df98a230670456e1536f97d1c39`.
Bracket **HELD**: content `88514802` over 17 gated files, unchanged. Roster: reviewer-code,
reviewer-security, reviewer-design, reviewer-test, each on its own `git archive` snapshot, plus my
own pass. **VERDICT: FAIL** on the recurring family; #444 stopping rule engaged, design note at
`gate8-design-note.md`.

## Attribution

- reviewer-code: 7 — reviewer-security: 7 — reviewer-design: 13 — reviewer-test: 16 — own: 3
- Total 46. Severity: 3 CRITICAL, 9 HIGH, the remainder MEDIUM/LOW/INFO.
- **No fix cycle was run.** Under #444 a gate-8 failure on this family takes a design note, not a
  patch; the findings below are the design note's evidence, not a work list.

## The convergence — the actual verdict

| # | defect | found independently by | I reproduced it? |
|---|---|---|---|
| C-1 | the "exact-match" placeholder rule still ACCOUNTS an alphanumeric tail (the InChI prefix, then the placeholder word, then a formula run), so a shaped site is silently subtracted from the gate | code, security, design, test — **all four** | YES, 3/3 probes |
| C-2 | an EMPTY tracked file lands in could-not-scan and fails the gate at exit 3; six `.gitkeep` files are tracked | security, code, own | YES |
| C-3 | the equivalence proof derives from `.pattern` and is blind to `.flags` | code, own | YES |

Three defects, nine independent findings, five readers. Each was invisible to a 1,222-test suite.

## CRITICAL

- **C-1** `tests/shape_scan.py:64-67` — `[A-Za-z0-9]*` re-admits the prefix class the docstring says
  is closed. Bounded by measurement: a FULL structure cannot hide (its `/` separators break the
  `fullmatch`); what hides is a formula layer. Four probes measured accounted, four control tails
  correctly reported.
- **C-2** `tests/test_shape_scan.py:77-100` — the "cannot hand back a matched value" sweep runs over
  an ACCESSION report only. A mutation returning matched text from `scan_structure_shapes` escapes
  every test **and is copied into the committed capture JSON**. A leak path into a tracked file.
- **C-3** `tests/test_structure_pattern_differential.py` — `…_one_structure_per_line_…_BY_PROOF`
  asserts `len(row) == 3` on tuples the test's own fixture constructs; the assertion cannot fail, has
  no anti-vacuity guard, and the name promises a proof the body does not render.

## HIGH

- **H-1** `_characters_at` silently returns a WRONG set for a counted capturing group, contradicting
  its own "RAISES on anything else" contract. Measured verdict-flipper: `(Xn){1}[A-Z]{25}` at index 1
  → 26 uppercase letters, truth `n`; derived-disjoint TRUE, true-disjoint FALSE.
- **H-2** the signed plan carries **zero** `#455` and **zero** `r2.49b`; four source files defer to a
  document that does not exist, while the plan's own `*[AMENDED …]*` convention sits one paragraph
  above the clause. The stopping rule is adjudicated against that text.
- **H-3** `bracket.py` writes shared-stash commit subjects (other workstreams), untracked filenames
  and host paths verbatim into a TRACKED evidence JSON, never running the production detectors over
  its own output. Gate 7's committed artifact carries a `perturb-seq-eval` subject; gate 8's is clean
  by luck, not by a control.
- **H-4** the xfail preconditions cannot fail the suite (under strict xfail an assert IS the expected
  outcome), so a non-break character in the table would silently witness nothing.
- **H-5** the unaccounted-reporting half is exercised by no bracket test; `if False:` escapes.
- **H-6** `files_scanned` arithmetic never asserted with a non-empty absent/unreadable set.
- **H-7** a DANGLING SYMLINK branch is documented as load-bearing and has no test.
- **H-8** could-not-scan reasons other than empty-input are unswept; the comment claiming the sweep
  covers the field is false for the object under test.
- **H-9** (own) OWN-1, the flags blindness above, before the code reviewer independently found it.

## MEDIUM / LOW — themes

- **Cry-wolf availability**: empty file (C-2 family), **directory / submodule gitlink** →
  `IsADirectoryError` → exit 3 (six submodules tracked), tool-load failure rendered per-FILE instead
  of once as `tool_loaded: false`, cause discarded by a bare `except Exception`.
- **Delegation violated**: `shape_scan_gated` re-implements the read with **no size bound**, while
  production documents `_MAX_SCAN_BYTES = 256 MiB` and says *"Every other reader in this guard has a
  bound and says so."* `shape_scan.py`'s own design rule 1 forbids re-implementation.
- **Pins**: gate 7's record pins `gate6-bracket.py` while its verbatim command names
  `gate7-bracket.py`; the bridging prose *"the two were byte-identical"* is TRUE (verified: every
  committed revision hashes `9df0ccb1…`) but UNCHECKED, and `_PIN.search` takes the first match only
  so a second pin would be ignored. Gate 6's AFTER half is unpinned entirely.
- **Typed numbers**: `bracket.py` types "1,028 / 44 / 892" in the same change set as (f)'s *"counts
  regenerated, never typed"*; the band test's parametrise IDs are typed literals beside the test that
  forbids typed numbers.
- **Census narrower than its claim**: `EVIDENCE.glob("*bracket*.py")` covers one directory.
- **`re.IGNORECASE`** on `_INVENTED_BODY` is inert against production (its `_STRUCTURE_RE` is
  case-sensitive) yet widens the accounted set to any casing — an inert flag that reads as coverage.
- **Path traversal (LOW)**: `--compare` takes `gated_files` from a JSON and joins to root without
  validation; an absolute entry discards root entirely. Not reachable from the git-derived capture path.
- `ShapeReport.scanned` has no caller and no test. Two predicates for one state (`is None` vs
  truthiness) disagree on `could_not_scan=""`.

## Checked and found SOUND (recorded so the failures are read fairly)

- Clause **(f), all five items** — independently swept; no unqualified `CLOSED` remains; the column
  band was verified at **every** ceiling in [2049, 2085], not just the three parametrised.
- Clause **(g)** deletion half complete; the two-layer pin (resolve + provenance) caught my own bad
  pin; `--self-test` is suite-driven with the exit-0-without-a-pass loophole closed.
- **(e) requirement 3's deferral is an HONEST PARTIAL, not a quiet drop** — declared in the
  docstring, the capture JSON (`verdict_half_live`), every run's stdout, and two test files.
- The delimiter tail is **load-bearing, not looseness**: 0 of 5 real tokens would `fullmatch` without it.
- `_alternation_branches`' textual split is safe — five adversarial patterns all raise.
- The dangling-symlink ordering (`is_symlink()` before `exists()`) is correct.
- Bucket partition is exact for distinct names; unaccounted shapes do not affect the exit code.
- All nine strict-xfail characters genuinely diverge; none is optimistic or duplicated.

## Verification (Iron Law — run in this session, output read)

| check | invocation | result |
|---|---|---|
| extended accession oracle (REQUIRED for this role) | `AIADLC_ACCESSION_ORACLE_EXTENDED=1 uv run pytest -q -p no:cacheprovider tests/test_accession_pattern_matrix.py` | 15 passed, 139 s |
| tests | `cd projects/lung-on-chipsim && uv run pytest -q` | 1222 passed / 4 skipped / 9 xfailed, 164 s |
| lint | `cd projects/lung-on-chipsim && uv run ruff check .` | All checks passed |
| format | `cd projects/lung-on-chipsim && uv run ruff format --check .` | 100 files already formatted |
| bracket after-half | `bracket.py --compare gate8-bracket-before.json` | **HELD**, content `88514802` unchanged |
| `uv.lock` integrity | sha256 before/after `uv run` | `ce4562c1…` unchanged |

**Step 8 configuration gap, reported rather than skipped:** `quality.test_command` is empty and
`quality.tests_required` is unset, so `/quality-gate`'s own Step 8 would have skipped tests entirely.
`agency.yaml` documents this deliberately — the real commands live under role-suffixed keys that the
gate does not read (a known plugin defect filed in `.claude/aiadlc-feedback`). Every command above
was therefore run BY HAND and its invocation recorded here.

**No QGR receipt is signed.** A receipt is a completion claim; this gate did not pass.
