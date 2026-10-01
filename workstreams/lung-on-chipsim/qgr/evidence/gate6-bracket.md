# Gate 6 — reviewer-isolation bracket, BEFORE half

Written **before the reviewers start**, per CTO #401. Gate 4's verdict had exactly one gap: I could
show no reviewer had mutated tracked content, because I re-checked each reviewer worktree directly,
but I could not re-derive the digest captured before the review — my context was compacted mid-gate
and the command did not survive it. This file is that command and that digest, on disk.

**CORRECTION (r2.49 (g)) — the script this record names no longer exists at that path.** The
per-gate copies `gate6-bracket.py` and `gate7-bracket.py` had drifted into being byte-identical, and
r2.49 (g) replaces both with the single shared
`workstreams/lung-on-chipsim/qgr/evidence/bracket.py`.

The command below is left **exactly as it was run** rather than rewritten: this record's job is to
state what happened, not what would happen today. The bytes that produced **this** record are the
ones **this gate's own before-capture recorded**, pinned here in one canonical line so that no reader
and no checker has to pick a hash out of prose:

```
PINNED-BYTES: sha256 887f8474865df999b8bb323629096b495f88237d4ea3393a9dbd676d1f252407 at 527234c:workstreams/lung-on-chipsim/qgr/evidence/gate6-bracket.py
```

This is deliberately NOT the bracket's final hash. Gate 6 fixed the tool twice *during* the
gate — the fail-open that reported HELD in a non-repository, then the #410 ruling-4 exit code —
and this record's before-half predates both. Pinning the final bytes here would have claimed a
provenance this gate's own capture contradicts, which is the mistake I made on the first pass.

`bracket.py` continues from the later bytes and then gains r2.49 (e)'s shape-scan call, so it is
**not** a substitute for the pinned blob when reproducing this record. `tests/test_bracket.py`
resolves this pin, re-hashes what comes back, **and** cross-checks it against
`gate6-bracket-before.json`, so a pin that is unresolvable, mismatched, or merely plausible fails
the suite.

## The command, verbatim

```
python3 workstreams/lung-on-chipsim/qgr/evidence/gate6-bracket.py \
  --root /Users/mo/github/personal/bioFM/worktrees/lung-on-chipsim \
  --base 699e495 \
  --out workstreams/lung-on-chipsim/qgr/evidence/gate6-bracket-before.json
```

The AFTER half re-runs it with `--compare` against that JSON, which exits 1 and names every
difference:

```
python3 workstreams/lung-on-chipsim/qgr/evidence/gate6-bracket.py \
  --root /Users/mo/github/personal/bioFM/worktrees/lung-on-chipsim \
  --base 699e495 \
  --compare workstreams/lung-on-chipsim/qgr/evidence/gate6-bracket-before.json
```

## The BEFORE capture

| field | value |
| --- | --- |
| base | `699e495` (the gate-5 iteration boundary) |
| head | `527234c` |
| gated files | 16 |
| **content digest** | **`3201f2cf`** (sha256, first 8) |
| worktrees | 13 |
| branches | 12 |
| stash entries | 13 |
| tags | 1 |
| status lines | 1 (`config/monitor-pids.json`, CTO #100 do-not-touch) |

The file set is **pinned** in the JSON. The after half re-measures that list rather than recomputing
the diff, so a file committed between the halves — this record, for one — cannot register as a
change no reviewer made.

## Pre-existing metadata, investigated and explained — NOT removed

The worktree and branch counts are higher than gate 4's (9 and 8). Per reviewer-isolation addendum
3d an unexplained entry is investigated and reported, never dropped, so:

- **4 worktrees** at `6b0aeb1` under this session's scratchpad (`g4-code`, `g4-sec`, `g4-design`,
  `g4-test`) — gate 4's reviewer worktrees, left after that gate failed. Detached HEAD, no branches.
- **4 worktrees** at `be6e07e` under `.claude/worktrees/` (`agent-a19bdd80…`, `agent-a3ad140f…`,
  `agent-aaabb6db…`, `agent-af202026…`) with matching `worktree-agent-*` branches — gate 5's
  reviewer worktrees, at gate 5's HEAD, left after that gate passed.

That is 8 accumulated reviewer worktrees and 4 leftover branches. **I am not removing any of them**:
removing an entry instead of reporting it is the mistake addendum 3d exists for, and I made it once
already. Whether the fleet should reap them is the CTO's call; they are recorded here so the after
half's delta can be read against a known baseline.

## What the after half should show

Exactly the gate-6 reviewer worktrees and branches as new metadata, **and no content-digest change
at all**. A content change means a reviewer mutated the tree being hashed, which voids the gate.

## Rule 3b — the bracket is proven able to fail, both ways

`gate6-bracket.py --self-test` builds a throwaway repo and measures six things; all six pass:

| check | result |
| --- | --- |
| mutate one tracked byte | content digest CHANGED, and the file is NAMED |
| restore it | returns to silence |
| add a tag | metadata CHANGED, and the tag is named |
| remove it | returns to silence |
| commit a new file after the capture | does NOT break the pinned bracket |
| then mutate a pinned file | still caught — pinning did not blind it |

---

# Gate 6 — AFTER half, run when the four reviewers returned

## The result: content HELD

```
BEFORE content digest: 3201f2cfc8b76469   over 16 files
AFTER  content digest: 3201f2cfc8b76469   over 16 files
per-file differences: []
```

**No reviewer mutated a gated file.** That is the claim the before-half said to look for, and it is
the one that matters: a content change would have voided the gate.

## The metadata delta, itemised — all benign, all explained

```
branches  NEW: worktree-agent-a786fd28b010e4884      (the code reviewer's own branch)
branches  NEW: worktree-agent-a7fca51b98841ff93      (the test reviewer's own branch)
worktrees NEW: .claude/worktrees/agent-a786fd28b010e4884   at 14d80cf
worktrees NEW: .claude/worktrees/agent-a7fca51b98841ff93   at 14d80cf (locked)
worktrees GONE/NEW: worktrees/lung-on-chipsim  527234c -> 14d80cf
```

The last row is this repository's own worktree, same path, HEAD advanced by the bracket-record
commit — i.e. by me, before the reviewers started.

**Unexplained, and recorded as such rather than given a cause:** the design and security reviewers'
worktrees do not appear in the delta at all. The likeliest reason is automatic cleanup of a worktree
whose content was unchanged, but I did not observe that happening, so I am not claiming it.

## What this run found out about the instrument itself

Two defects in `gate6-bracket.py`, both caught by using it rather than by reading it:

1. **It printed `BRACKET BROKEN` and exited 1 for a purely benign metadata delta.** The exit code
   cannot distinguish "a reviewer mutated the tree" from "a reviewer existed". Its own docstring
   warns that a bracket which cries wolf teaches you to ignore it; its metadata half does exactly
   that. Reported in the gate-6 verdict; not yet fixed, because the remedy (content delta fails,
   metadata delta reports) is a behaviour change worth ruling on.
2. **It reported `bracket HELD`, exit 0, in a directory that is not a git repository.** `_git`
   returned an error string instead of raising, so the gated file set became that one string and the
   two halves compared equal over zero measured bytes. The instrument built to make silence mean
   something was silent when it could not see the tree. All six original self-test directions ran
   inside a working repo, so none of them could reach it.

## The fix to (2), applied after the verdict

`_git` now raises `BracketUnusable`; an empty gated set is refused; both paths print
`BRACKET UNUSABLE (this is NOT 'held')` and exit 2. Two self-test directions were added, so the
tool now proves eight things rather than six:

| check | result |
| --- | --- |
| mutate one tracked byte | content digest CHANGED, and the file is NAMED |
| restore it | returns to silence |
| add a tag | metadata CHANGED, and the tag is named |
| remove it | returns to silence |
| commit a new file after the capture | does NOT break the pinned bracket |
| then mutate a pinned file | still caught — pinning did not blind it |
| **a non-repository** | **refused BY THE GIT GUARD, exit 2, never "held"** |
| **an empty gated set** | **refused — a digest over nothing compares equal to a digest over nothing** |

The first version of the non-repository check created its directory INSIDE the throwaway repo, so
`git -C` walked up and found the parent: it passed through the *empty-set* guard while its label
claimed it tested the *git* guard. Caught only because both messages printed identically. It now
runs outside the repo and asserts the refusal came from the right guard.

## A consequence to note before anyone re-runs the comparison

Fixing the tool changed `gate6-bracket.py`, and that file is **in this gate's pinned set**. A
re-run of `--compare` against `gate6-bracket-before.json` will therefore report

```
content digest CHANGED
  file changed: workstreams/lung-on-chipsim/qgr/evidence/gate6-bracket.py
```

That is **me, after the gate closed and after the comparison above was taken** — not reviewer
tampering. It is also an incidental end-to-end confirmation that the content-detection path works on
the live tree and names the file. The authoritative gate-6 result is the digest pair at the top of
this section.

---

## Post-verdict: the two instrument defects gate 6 found are now both fixed

Ruling 4 of #410 accepted the fail-open fix and directed the second one. Both are done, and the
self-test now proves **twelve** things rather than six.

**The exit code carries the CONTENT verdict only.** A content difference means a reviewer mutated
the tree that was hashed and the gate is void; a metadata difference usually means a reviewer
*existed*. Gate 6's own after-half printed `BRACKET BROKEN` and exited 1 for two reviewer branches
and two reviewer worktrees while the content digest was **identical**. The metadata half is not
dropped — it is the only place an unexplained worktree surfaces at all, and addendum 3d requires
such an entry to be investigated and reported — it just no longer decides the verdict.

**The stash is keyed by CONTENT, not by index.** The stack is shared with every worktree in this
repo, so one push by another agent renumbers everything below it. Measured on the live after-half:
**26 lines of delta for one entry actually added.** That is the same cry-wolf failure, in the half
whose entire job is to be read. Entries are now compared by their text with the `stash@{n}` label
stripped.

Two new self-test directions cover the first, two cover the second:

| check | result |
| --- | --- |
| a metadata-only move | reported, and **not** a content verdict |
| a content change alongside a metadata move | still a verdict |
| the same stash entry at two indices | not a difference |
| a non-stash line | passes through the key unchanged |

**Note for anyone re-running the comparison against `gate6-bracket-before.json`:** that capture
predates the stash-keying change, so its stash section still holds indexed labels and will still
report noisily against a current capture. It will also report content changes — every gate-6 fix
since. Both are expected. The authoritative gate-6 result remains the digest pair recorded above,
taken before the reviewers started and re-derived after they finished.
