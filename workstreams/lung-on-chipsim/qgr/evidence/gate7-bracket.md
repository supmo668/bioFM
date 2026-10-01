# Gate 7 — reviewer-isolation bracket, BEFORE half

Written **before the reviewers start**, per CTO #401 and the discipline that came out of gate 4's one
gap. The tool is gate 6's, carried forward with both defects that gate found now fixed.

**CORRECTION (r2.49 (g)) — the script this record names no longer exists at that path.** The
per-gate copies `gate6-bracket.py` and `gate7-bracket.py` had drifted into being byte-identical, and
r2.49 (g) replaces both with the single shared
`workstreams/lung-on-chipsim/qgr/evidence/bracket.py`.

The command below is left **exactly as it was run** rather than rewritten: this record's job is to
state what happened, not what would happen today. The bytes that produced **this** record are the
ones **this gate's own before-capture recorded**, pinned here in one canonical line so that no reader
and no checker has to pick a hash out of prose:

```
PINNED-BYTES: sha256 9df0ccb15c83289f32a853fe1614c81a6ffe925f4172350715a7c5a0e9cfff5f at 6052e2b:workstreams/lung-on-chipsim/qgr/evidence/gate6-bracket.py
```

The pin names the `gate6` path on purpose: at gate 7's before-capture the `gate7` copy was still
UNTRACKED — its own JSON records `?? …/gate7-bracket.py` in the status block — so the tracked
bytes that capture hashed are the gate6 path's. The two were byte-identical.

`bracket.py` continues from the later bytes and then gains r2.49 (e)'s shape-scan call, so it is
**not** a substitute for the pinned blob when reproducing this record. `tests/test_bracket.py`
resolves this pin, re-hashes what comes back, **and** cross-checks it against
`gate7-bracket-before.json`, so a pin that is unresolvable, mismatched, or merely plausible fails
the suite.

## The command, verbatim

```
python3 workstreams/lung-on-chipsim/qgr/evidence/gate7-bracket.py \
  --root /Users/mo/github/personal/bioFM/worktrees/lung-on-chipsim \
  --base 699e495 \
  --out workstreams/lung-on-chipsim/qgr/evidence/gate7-bracket-before.json
```

The AFTER half re-runs it with `--compare` against that JSON. **Its exit code now carries the CONTENT
verdict only** (#410 ruling 4): a content difference voids the gate; a metadata difference is printed
under its own heading and is not a verdict.

## The BEFORE capture

| field | value |
| --- | --- |
| base | `699e495` (the gate-5 iteration boundary — gate 6 failed, so no receipt moved it) |
| head | `6052e2b` |
| gated files | 28 |
| **content digest** | **`a1bfa382`** |
| worktrees | 15 |
| branches | 14 |
| stash entries | 15 |
| tags | 1 |
| status lines | 2 |

The file set is **pinned** in the JSON; the after half re-measures that list rather than recomputing
the diff, so a file committed between the halves cannot register as a change no reviewer made.

## Metadata baseline, every line accounted for — and NOT removed

`status` is 2: `config/monitor-pids.json` (CTO #100, do-not-touch) and this gate's own bracket script,
untracked at capture time.

**TEN accumulated reviewer worktrees and SIX leftover branches**, up from eight and six at gate 6:

- 4 at `6b0aeb1` under the session scratchpad — **gate 4's** reviewers, detached, no branches.
- 4 at `be6e07e` under `.claude/worktrees/` — **gate 5's** reviewers, with `worktree-agent-*` branches.
- 2 at `14d80cf` under `.claude/worktrees/` — **gate 6's** reviewers, with `worktree-agent-*` branches.

**None removed.** Addendum 3d: an unexplained entry is investigated and reported, never dropped — and
these are explained, not unexplained. But the accumulation is monotonic: every gate adds two to four
and none is ever reaped, so each bracket's metadata baseline inflates and the signal-to-noise of the
half addendum 3d tells you to read gets worse each time. Reported to the CTO at gate 6 and again here;
reaping them is a fleet decision, not a worktree agent's.

## What the after half should show

The gate-7 reviewer worktrees and branches as new metadata, and **no content-digest change at all**.
A content change means a reviewer mutated the tree being hashed, which voids the gate.

## Rule 3b — the bracket is proven able to fail, twelve ways

`gate7-bracket.py --self-test` builds throwaway repos and measures twelve things; all twelve pass.
Six are gate 6's originals; the other six were added because gate 6 found the instrument itself
defective twice:

| check | result |
| --- | --- |
| mutate one tracked byte | content digest CHANGED, and the file is NAMED |
| restore it | returns to silence |
| add a tag | metadata CHANGED, and the tag is named |
| remove it | returns to silence |
| commit a new file after the capture | does NOT break the pinned bracket |
| then mutate a pinned file | still caught — pinning did not blind it |
| a non-repository | refused BY THE GIT GUARD, exit 2, never "held" |
| an empty gated set | refused — a digest over nothing compares equal to a digest over nothing |
| a metadata-only move | reported, and NOT a content verdict |
| a content change alongside a metadata move | still a verdict |
| the same stash entry at two indices | not a difference |
| a non-stash line | passes through the stash key unchanged |

---

# Gate 7 — AFTER half

## The result: content HELD

```
BEFORE content digest: a1bfa382   over 28 files
AFTER  content digest: a1bfa382   over 28 files
exit 0
```

**No reviewer mutated a gated file.**

## The metadata delta — nine lines, all explained, and NOT a verdict

```
branches  NEW: worktree-agent-a1ca2f63f1687edf5   (the design reviewer's own branch)
branches  NEW: worktree-agent-acdf690f8b1031d9b   (the test reviewer's own branch)
worktrees NEW: .claude/worktrees/agent-a1ca2f63f1687edf5   at 22ff0d6
worktrees NEW: .claude/worktrees/agent-acdf690f8b1031d9b   at 22ff0d6
worktrees GONE/NEW: worktrees/lung-on-chipsim   6052e2b -> 22ff0d6   (this gate's own bracket commit)
worktrees GONE/NEW: <repo>                      12a73e0 -> e6a9cc3   (another agent's work on main)
status    GONE: ?? …/gate7-bracket.py                      (untracked at capture, committed since)
```

All four reviewers disclosed that they reset their own branch to the review tip because their
worktrees were provisioned at an unrelated commit and the branch hook blocks a detached checkout.
Two of those resets are visible above; the other two reviewers' worktrees do not appear, which is the
same unexplained absence recorded at gate 6 and still not investigated to a cause.

## Both #410 ruling-4 fixes worked, measured on a live gate rather than in a self-test

| | gate 6 after-half | gate 7 after-half |
| --- | --- | --- |
| verdict for a metadata-only move | **"BRACKET BROKEN", exit 1** | reported under its own heading, exit 0 |
| stash section | **26 lines** for one entry actually added | **absent** — no spurious delta |

The stash keying and the exit-code split are the difference. This is the first after-half whose
output a reader can act on without first deciding which half of it to ignore.
