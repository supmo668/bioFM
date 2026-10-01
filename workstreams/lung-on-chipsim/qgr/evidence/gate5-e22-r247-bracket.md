# Gate 5 bracket evidence: E-22 r2.47a WI-1 + WI-2

Written 2026-09-25T23:12Z BEFORE any reviewer starts (r2.47 evidence discipline).
Plan hash 5c7523f (r2.47a). Directive #399.

## Range

- base (bracket start, merge of main r2.47a): `561be17c3256aa3a2b5b63b288423c0043871953` tree `c6dd4bba19ba8241f322bebcdca1faa2a973f070`
- head (bracket end): `be6e07e95628142174291ad50494bf043360dd68` tree `0a36c49a34cf4054de31788f43c431d0c6767464`
- diff digest: `git diff 561be17..HEAD | shasum -a 256` = `33a813381b5346e293631609f0cf4f151b49a12930370c20c105ea53f46aa822`

## Commits (one per item)

```
a26ef46 lung-on-chipsim/lung-on-chipsim: E-22 r2.47(a): pin the detector over its TEXT and its FLAGS, plus a lowercase-prefix row
148cb7d lung-on-chipsim/lung-on-chipsim: E-22 r2.47(b): the context axis walks EVERY single code point on both sides; three guard mutants that beat ga
26f3533 lung-on-chipsim/lung-on-chipsim: E-22 r2.47(c): pin the size ceiling from BELOW as well as above; a 48 MiB ceiling now fails two rows plus the
1babc02 lung-on-chipsim/lung-on-chipsim: E-22 r2.47(d): restore the E-13 taxonomy at the composition root; unusable declaration data is exit 2 with th
9d80674 lung-on-chipsim/lung-on-chipsim: E-22 r2.47(e): fix the axis-1 off-by-one (bare prefix now generated) and WIRE the extended tier as a document
82d25b5 lung-on-chipsim/lung-on-chipsim: E-22 r2.47(g): ratio rows that REACH the rule (invalid UTF-8, NUL-free latin-1) at, below and above nine tent
be6e07e lung-on-chipsim/lung-on-chipsim: E-22 r2.47 WI-2: hygiene -- owned-path reference import, false docstrings and messages corrected, documented 
```

## Bracket command

```
git worktree list; git rev-parse HEAD^{tree}; git diff 561be17..HEAD --stat;
for f in $(git diff --name-only 561be17..HEAD); do shasum -a 256 "$f"; done
```

## git worktree list

```
/Users/mo/github/personal/bioFM                                                                                                             3495bc4 [main]
/private/tmp/claude-501/-Users-mo-github-personal-bioFM-worktrees-lung-on-chipsim/abe82a15-02b1-4427-8fec-ef8b93ce281b/scratchpad/g4-code   6b0aeb1 (detached HEAD)
/private/tmp/claude-501/-Users-mo-github-personal-bioFM-worktrees-lung-on-chipsim/abe82a15-02b1-4427-8fec-ef8b93ce281b/scratchpad/g4-design 6b0aeb1 (detached HEAD)
/private/tmp/claude-501/-Users-mo-github-personal-bioFM-worktrees-lung-on-chipsim/abe82a15-02b1-4427-8fec-ef8b93ce281b/scratchpad/g4-sec    6b0aeb1 (detached HEAD)
/private/tmp/claude-501/-Users-mo-github-personal-bioFM-worktrees-lung-on-chipsim/abe82a15-02b1-4427-8fec-ef8b93ce281b/scratchpad/g4-test   6b0aeb1 (detached HEAD)
/Users/mo/github/personal/bioFM/worktrees/cellforge-agents                                                                                  228d354 [cellforge-agents]
/Users/mo/github/personal/bioFM/worktrees/lung-on-chipsim                                                                                   be6e07e [lung-on-chipsim]
/Users/mo/github/personal/bioFM/worktrees/perturb-seq-eval                                                                                  a1fdf4a [perturb-seq-eval]
/Users/mo/github/personal/bioFM/worktrees/v2r-loop                                                                                          7f5ff4d [v2r-loop]
```

## Changed files, sha256 at head

```
2130363b8b1dbc60164d0cdc818e33960fff78c071656d5308e20c7e55fbbc9b  agency.yaml
eaa9a7e0dcd4868d1462b3ee91a88c4acf51b21f4ea0fa7e198ad3bfe239908d  projects/lung-on-chipsim/chipsim/guards/decoding.py
146e18842e1ee1147abee6149bc1cc975486ffb4f891aa2052fedcba022ca7cc  projects/lung-on-chipsim/chipsim/guards/record_content.py
e777ca7ebab06289f3a28d22d8b111331c8ba263506b1112f122b9227383b323  projects/lung-on-chipsim/chipsim/pipeline.py
33b6bb6e48af2216075ca0978a3bdab04cbc18fa7a15c9eab480c318e44148b1  projects/lung-on-chipsim/chipsim/record_content.py
610a08b5e412c63e3b79e6213f8322d65996fd20fcf28f3a9052a7b4245ed0cf  projects/lung-on-chipsim/tests/readability_reference.py
4fd6332f829c277df77df67fb648782407bd51359e37628d0fd3a6a40bd32b8c  projects/lung-on-chipsim/tests/test_accession_pattern_matrix.py
3601dbdc6b4003fa08787706110fc76885d57407ffbbd9733a5f49c92c9ae4e1  projects/lung-on-chipsim/tests/test_readability_differential.py
9be7e75a912f48b782db87c9b6f5fb7f51cab82aff10a5ba32be67acec78adec  projects/lung-on-chipsim/tests/test_record_content_entry_point.py
510ce2e9210ce590039e1d6ea4f3beb9b49af52aaa10c3533f9ce5ce170c2e35  projects/lung-on-chipsim/tests/test_record_content_guard.py
```

## Stat

```
 agency.yaml                                        |   5 +
 .../lung-on-chipsim/chipsim/guards/decoding.py     |  15 +-
 .../chipsim/guards/record_content.py               |  11 +-
 projects/lung-on-chipsim/chipsim/pipeline.py       |  19 +-
 projects/lung-on-chipsim/chipsim/record_content.py |  75 ++++++-
 .../lung-on-chipsim/tests/readability_reference.py |  25 ++-
 .../tests/test_accession_pattern_matrix.py         | 218 ++++++++++++++++++--
 .../tests/test_readability_differential.py         | 167 ++++++++++++----
 .../tests/test_record_content_entry_point.py       | 222 +++++++++++++++++++--
 .../tests/test_record_content_guard.py             |   2 +-
 10 files changed, 646 insertions(+), 113 deletions(-)
```

## Baseline at base (measured before any change)

Full suite at 561be17: 1143 passed / 4 skipped, exit 0 (150 s).

## Scratch mutation harness (not tracked)

/tmp/locmut/locmut_plugin.py swaps REAL_ACCESSION_RE before collection (LOCMUT_PATTERN,
LOCMUT_FLAGS). It patches decoding._MAX_SCAN_BYTES and _MIN_PRINTABLE_RATIO at session start
(LOCMUT_CEILING, LOCMUT_RATIO). Per-item mutant results are in each commit body.
Its sha256: `7025bbaa339fff86fabc0d141d1a05e48850678a045e487343285b4929b018be`

### Harness source, verbatim, so the mutant results are reproducible after /tmp is gone

```python
"""Scratch mutation harness: LOCMUT_PATTERN / LOCMUT_FLAGS replace REAL_ACCESSION_RE before collection."""
import os, re
def pytest_configure(config):
    pat = os.environ.get("LOCMUT_PATTERN")
    if pat is None:
        return
    flags = int(os.environ.get("LOCMUT_FLAGS", str(int(re.UNICODE))))
    import chipsim.ingest.drugbank_snapshot as d
    d.REAL_ACCESSION_RE = re.compile(pat, flags)

def pytest_sessionstart(session):
    import os
    c = os.environ.get("LOCMUT_CEILING")
    if c is not None:
        import chipsim.guards.decoding as dec
        dec._MAX_SCAN_BYTES = int(c)

def pytest_sessionstart(session):  # noqa: F811 - chained: ceiling + ratio
    import os
    import chipsim.guards.decoding as dec
    c = os.environ.get("LOCMUT_CEILING")
    if c is not None:
        dec._MAX_SCAN_BYTES = int(c)
    r = os.environ.get("LOCMUT_RATIO")
    if r is not None:
        dec._MIN_PRINTABLE_RATIO = float(r)
```
