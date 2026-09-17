---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-17T08:01
status: created
priority: normal
size: task
subject: "Iteration §9 complete on lung-on-chipsim — the declaration surface built and READ; the registry policed itself; four escalations"
in_reply_to: null
---

# Iteration §9 complete on lung-on-chipsim — the declaration surface built and READ; the registry policed itself; four escalations

event: iteration-complete
workstream: lung-on-chipsim
iteration: "§9 (r2.24 E-10 + E-08b floor + E-02 declaration surface)"
branch: lung-on-chipsim
commit_hash: 31867d2
plan_hash: db3d598
qgr_receipt: workstreams/lung-on-chipsim/qgr/bioFM-matthew-mo-lung-on-chipsim-lung-on-chipsim-bioFM-qgr-iteration-complete-20260917-0059-45c68fc.md
diff_base: 1c4f500
hash_e: 45c68fc5841959eac8d6b01130f54d60f2afe190433e0a093659ebea52368c8f
pushed: YES — origin/lung-on-chipsim = 31867d2, main = df89f50 untouched
next_handoff: cto rulings on four escalations; then E6-6/E6-7

## 1. Push report (standing clearance, three conditions)
Receipt 45c68fc verified from the worktree root, "1 of 21", covering 1c4f500..boundary. Guard run
IMMEDIATELY before the push, not from memory: 248 passed, and the live command printed 23 listed /
773 scanned / 0 not on disk / 0 failing / exit 0. Remote after: lung-on-chipsim = 31867d2, main =
df89f50 untouched. 893 passed / 5 skipped; ruff check + format clean. r2.24 merged (fb814ae),
plan-gate verified at db3d598.

You were right about my diagnosis and I want that on the record: `db3d598` is a plan-gate CONTENT
hash, so `cat-file` was never going to resolve it — it fails identically for r2.23's `78d8003`,
which I had merged an hour earlier. I read "not a valid object name" as "the commit has not reached
me" and asked you to push, which would have touched a decision reserved to the principal. The merge
was one command in my own worktree the whole time.

## 2. E-10 IMPLEMENTED AS RULED — it corrects what I shipped in §8
Counted and reported ALWAYS, failing only where we own it, exit 3 still reserved for "could not scan
at all". One interpretation I made and am flagging rather than burying: I read "fails only when this
project owns it" as failing_undeclared's predicate — owned by us OR owned by nobody — because
"unowned fails here" is load-bearing for E6-4 and a missing file is no different in that respect. If
you meant strictly THIS_PROJECT, it narrows in one line.
I also built E-08b's FLOOR, which the clause names and I had not implemented. The witness proves the
listing is of THIS tree; it cannot see a listing of the RIGHT tree that came back truncated.

## 3. E-02: "declared" was a state the code could describe and never reach
RENDERED_ARTIFACT_DECLARATIONS was an empty frozenset nothing populated. FIVE tests iterated it,
running zero times; FOUR monkeypatched it; and the oldest had been vacuous since the day it was
written, because its "binary" fixture was b"\xff\xfe not utf-8", which decodes as UTF-16 — the file
was READABLE, so the assertion held with or without a declaration. The behaviour "a declaration
clears a file" had no test at all, for four revisions.

Built, with E-11 folded in as you ruled: two data files, each owning only what it may own; entries
carrying sha256 or derived_from and never a bare path; a validator refusing a stale pin, a dead path,
a foreign path, a readable file, a container by magic, a double exemption and a dispatch payload.
Registry derived by MEASUREMENT (five owners, each with a checkable marker); live result unchanged at
23 listed / 0 failing, so E6-1b's scoping is provably untouched.

## 4. SIX WAYS TO GET A TRACEBACK OUT OF THE ONE COMMAND THAT MUST NOT FAIL SILENTLY
A non-UTF-8 byte (UnicodeDecodeError is a ValueError, NOT an OSError, so it escaped the catch); a
non-list `declarations`; mixed-type YAML keys crashing THE UNKNOWN-KEY CHECK ITSELF; mistyped fields
that are truthy and then get sliced; an unclosed handle — in TWO readers, one the reviewer had not
looked at; and `str(version)` accepting 0x1 and 01. Each was exit 1 with no report at all. The
mistyped-field one I found myself, and it is the §7 CLI-traceback defect rebuilt one clause later.

## 5. FOUR FALSE-CLEAN SHAPES THE FIRST REAL ENTRY COULD HAVE REACHED
- THE REGISTRY POLICED ITSELF. Placement was judged against the owner set defined in the very file
  whose declarations it constrains, so DELISTING a project made its subtree "unowned" and therefore
  repo-root-declarable: one edit, one file, another team's artifacts cleared, zero defects. The
  security reviewer demonstrated it end-to-end against the shipped command — exit 2 became exit 0
  with a payload present. Two questions now use two sets, and a path under an ownership prefix
  belongs to a project whether or not that project is registered. Re-run after the fix: refused both
  ways round, payload still reported.
- AN ABSENT DECLARATION FILE READ AS AN EMPTY ONE and silently reverted the registry to the
  pre-r2.24 marker-only mitigation, with a healthy exit code. This module already says "an
  unreadable declaration file is not an empty one"; an absent one is not either. E-02 reproduced
  inside the fix for E-02.
- DISPATCH PAYLOADS were declarable — the one class this module calls never-exemptible. The trap
  worth recording: reusing the waiver's own regex would have exempted precisely `leak.pdf`, because
  that pattern is `.md`-only by design.
- A DECLARED PATH COULD ALSO BE CONTENT-EXCLUDED. A missing RULE, not a missing test — and the test
  that claimed it was vacuous on both sides, since both collections are empty.

## 6. 12 MUTANTS SURVIVED THE ENTIRE 851-TEST SUITE
Including THIS WORK'S OWN HEADLINE CLAIM — that a declaration whose claim does not hold fails the
gate. Every defect test asserted on the validator's return value; none on the exit code. 18 tests
added, all 16 mutants re-run in a throwaway clone: ZERO survivors.

## 7. THE NINTH AND TENTH VACUITY ARE MINE, WRITTEN THIS SESSION, AFTER ADOPTING THE RULE
"stale" and "container" are substrings of the tmp_path directories pytest names after those very
tests. Proven by replacing each message with an absolute path and watching both still pass. Also
repaired: an assertion true by construction, a report test asserting a label and no number (it passed
with the count hardcoded to 999), an oracle that passed when EMPTY, and two tests proving a path was
refused without proving why.
One more on myself: a probe of mine "proved" a declaration does not exempt content using a synthetic
DB9xxxx accession, which the scan excludes by design — it could never have produced a hit. I caught
it before reporting it, but it is the same shape.

## 8. FOUR ESCALATIONS — yours, not mine
E-13 [MED] EXIT-CODE SEMANTICS. A malformed declaration file turns the WHOLE gate to exit 3 and hides
  which file actually failed; and the header's `failing` count now mixes undecodable files with
  declaration defects, so the first line does not add up on its own. But exit 3 is a contract YOU
  set, and a broken declaration is arguably not "could not scan at all" — the scan works, only the
  exemption data is unreadable. Recommendation: treat nothing as declared, still render the listing,
  exit 2 with the structural error alongside. I did not take it because it changes your contract.
E-14 [MED] A LOAD-ONCE DeclarationSurface. 19 YAML parses per report and a pinned artifact hashed 3x.
  The half that is correctness rather than speed: no snapshot, so a concurrent edit yields a
  SELF-CONTRADICTORY single report — rows marked FAILS HERE under an owner the footer says fails
  nobody. It is also the natural home for the two owner sets.
E-15 [LOW] One defect per entry: the chain `continue`s, so a reader repairing an entry learns its
  next problem one gate run at a time.
E-16 [LOW] For the E6-6 clause: `undecodable_unallowed` reaching into the DrugBank exclusions is the
  one non-mechanical part of that extraction, and the shared .venv's editable install points at the
  worktree, so a reviewer running a script from the wrong cwd exercises the tree being hashed. A
  reviewer hit exactly that and disclosed it.

## 9. One documentation defect worth naming as such
My own data files said derived_from is "a claim a reader can check". The gate checks the source is
tracked, readable, same-owner and not itself declared — it does NOT check that the file derives from
it. Prose implying verification the tool does not perform invites exactly the over-trust this
mechanism exists to remove, so both files now state what is actually verified. That is the kind of
defect that survives review precisely because it reads as reassurance.
