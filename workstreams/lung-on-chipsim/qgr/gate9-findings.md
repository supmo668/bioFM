# Gate 9 — consolidated findings. VERDICT: FAIL, on the same family.

Base `e1a1cc4` → HEAD `6b642d8`. Plan r2.50c, hash `ae894db`.
Bracket **HELD**: content `80526253` over 14 gated files, unchanged. One metadata line, re-derived
and matched: the `gate9-bracket-before.json` this gate itself created.
Roster: reviewer-code, reviewer-security, reviewer-design, reviewer-test, each on its own
`git archive` snapshot, plus my own pass.

> **CORRECTION, self-reported after the verdict was dispatched.** This file first read "2.7 MB each,
> 11 MB total" against "gate 8's 361 MB". That was wrong, and it is this gate's own family appearing
> in the verdict about the family: **11 MB was the CREATION size**, measured before the reviewers
> ran. Each reviewer then built a virtualenv inside its own snapshot, and the size measured at
> cleanup was **269 MB**. Gate 8's 361 MB was a POST-review figure, so the original sentence
> compared a creation size against a final size and reported an improvement of roughly 33x that does
> not exist. The honest comparison is **361 MB -> 269 MB**: narrower archives, partly offset by four
> virtualenvs. Measured at `rm -rf` time, not estimated. Nothing else in this file depends on the
> number, and no verdict changes.

**This is the LAST gate on E-23.** Under the principal's time box (approval-log row 54, applied and
route-corrected 2026-09-29) and #507, a gate-9 failure on the same family closes E-23 at the scope
it reached. No r2.51 will be signed. The findings below go to the Stage 1 registered report as
stated limitations.

**No QGR receipt is signed.** A receipt is a completion claim and this gate did not pass.

## The verdict is the convergence, not the count

| defect | found independently by | reproduced? |
|---|---|---|
| **The citation predicate is satisfied by the PROSE THAT EXPLAINS IT.** `shape_scan.py:122-123` (the worked example inside `_carries_a_citation`'s own docstring) and `test_shape_scan.py:385` (the positive-control fixture of the test that proves this cannot happen) each put a source identifier, a retrieval word and an ISO date on one line — so each file reads as cited and every shaped site in it is subtracted into bucket F. | **ALL FOUR** + me | YES — live, measured: 53 of 142 sites land in F; 4 of them are `test_shape_scan.py`'s own |
| **The scanner and the classifier disagree about what a line is.** `_positions` numbers lines with `count("\n")`; `classify_sites` indexes `str.splitlines()`, which breaks on nine further code points. One such character above a site drops it from ALL FOUR buckets while the pass condition still reads 0. | code, security, design | YES (all nine breakers); latent — 0 live instances in tree |
| **The sum-identity test asserts a different identity from the one the clause states**, and is vacuous over half its own formula: both `accounted` terms are 0 in all three of its samples. | code, design, test | YES |
| **The union rule is prose over dead code.** `r250-classify.py:150-153` — the loop body is `pass`; the rule the docstring calls load-bearing is not implemented. | security, design, test | YES (by reading) |
| **The reporting artefact is unwired and hardcodes host paths.** `r250-classify.py` is imported by nothing, and pins an absolute `/Users/...` path and a plugin version into a TRACKED file — added by the same revision that taught `bracket.py` to strip exactly that. | security, design, test | YES |
| **The self-check covers a prefix of what is written**, not the written bytes: `shape_scan` is added to the payload after the check, and the check reads a compact dump while `indent=2` reaches disk. | code, security, design | YES |

Six defects, nineteen independent findings, five readers. Every one invisible to a 1,257-test suite.

## The sharpest one, stated plainly

`test_PROSE_ABOUT_citations_does_not_make_a_file_count_as_cited` is the test I added *in this
revision* to close this exact defect. Its own positive-control fixture re-creates the defect, in the
same file, 115 lines below a comment block that records the mitigation and applies it correctly to
the module-level constant. The header says *"FIXTURES ASSEMBLED FROM PARTS … written as plain
literals, the citation text made THIS WHOLE FILE read as cited, so bucket F swallowed its own
genuine needs-curation sites."* It then does precisely that.

One assertion would have caught both instances — `assert not _carries_a_citation(<own source>)` —
and both files fail it today.

## What the mutation pass proved (reviewer-test, ~20 mutations)

Tests that DID NOT die when the thing they name was broken:

- **Bucket W has no test in either direction.** `cited_in_window = False` (W made permanently dead)
  → 23 passed. `MARKER_WINDOW_LINES = 2` → `0` → 23 passed. The constant's VALUE is unverified;
  `shape_scan.py:96` calls it "value confirmed r2.50a", which is prose with no code behind it.
- **Proximity is never exercised.** `_CITATION_SPAN_LINES = 3` → `10000` → 23 passed. The only
  thing the prose test actually discriminates on is the presence of a date.
- **The anti-vacuity corpus guard pins syntax, not the load-bearing property.** It matches "a
  counted capturing group"; the H-1 defect needs a group WIDER THAN ONE CHARACTER. Drop the single
  width-2 pattern AND restore the gate-8 H-1 bug → **9 passed**: the defect is back and everything
  is green.
- **Both preconditions inside the strict-xfail splitlines test are structurally inert** — under
  strict xfail an assertion failure IS the expected outcome. Break the probe so no parameter
  witnesses anything → 2 passed, 9 xfailed, a report byte-identical to the real thing.
- `files_scanned` hardcoded to the constant `1` → 13 passed.
- A sibling key carrying `git branch --list` VERBATIM added to the record → 13 passed. The
  branch-leak assertion checks one key; the host-path assertion checks the whole blob.
- Bucket C's branch disabled → 23 passed; no test ever puts a site into C.

## What reviewer-security added that no one else framed

**The citation predicate is positively correlated with the violation it exists to leave visible.**
A block naming a compound beside its source accession, its key-shaped token and a retrieval date is
simultaneously the strongest match for `_carries_a_citation` AND a textbook name-to-identifier
association — one of the three standing prohibitions. A site is subtracted from the gate *because*
it sits next to the thing the rule forbids. One comment block excuses all 35 shaped sites in a file,
spanning 240 lines, including sites ABOVE it.

The honest form of the headline claim is therefore much narrower than "139 of 139 sites classified":
**W and F test provenance adjacency only. The name-association and coined-title prohibitions are
measured by nothing in this change set**, and the production accession detector is shaped for one
database, so another database's accession form is structurally invisible to it.

**Escalated separately, not investigated here:** reviewer-security reports association-shaped lines
in two TRACKED, HASH-COVERED plan files. Determining whether those are real identifiers requires the
comparison this agent is forbidden to make, so it is recorded and referred to the principal rather
than resolved.

Also from security, all reproduced: a path-traversal primitive in `--compare` (a crafted
`gated_files` entry escapes the root and yields a hash/existence oracle written into the tracked
record); the refusal path echoing the absolute host root and git's raw stderr to stdout while the
RECORD redacts it; YAML aliases making a bucket count go negative and silently clamping the union
gap to zero.

## Checked and found SOUND — recorded so the failures are read fairly

- **Mechanism (1) DERIVED QUANTIFIERS** — the breaker set is measured across the whole Unicode range,
  the count is interpolated, and the derivation is re-measured independently by a second route.
  Design and code both called this the mechanism done properly.
- **Mechanism (3) RAISE-PROMISES PROVEN** — reviewer-code ran a differential against `re` over two
  alphabets and found **0 disagreements**; the hoisted body-type check raises at EVERY index on the
  gate-8 shape, not only the one that lands on the group. Reverting it kills a test. Subject to the
  anti-vacuity gap above.
- **Mechanism (4) DERIVATIONS CONSUME THE WHOLE ARTEFACT** — design called it "the strongest work
  here": the guard fires on the flag with the pattern text held identical, and a third test proves
  the refused flag would really break the disjointness.
- **C-1 is the strongest result in the change set**: reverting `[A-Z]*` → `[A-Za-z0-9]*` kills all
  four parametrised false-exclusion tests.
- **C-2's asymmetric pair is well designed** — both cases in one gated set, so only a rule that
  distinguishes them is green.
- **N is genuinely never marked** — verified by grep across the whole change set; there is no marker
  write path anywhere.
- **The content constraint holds in the new code** — `classify_sites` cannot return a token, and the
  refusal reports a count and never the value.
- **The bracket held**, and its one metadata line was re-derived and named.

## Verification (Iron Law — run in this session, output read)

| check | result |
|---|---|
| suite | 1257 passed / 4 skipped / 9 xfailed |
| ruff check / format | clean, 100 files |
| extended accession oracle (REQUIRED for this role) | 15 passed, 143 s |
| bracket after-half | **HELD**, content `80526253` unchanged |
| metadata delta | 1 line, re-derived and matched to this gate's own evidence file |

**No QGR receipt is signed.** A receipt is a completion claim; this gate did not pass.
