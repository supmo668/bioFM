# A receipt's `hash_d_transcript` records an absolute `$HOME` path, inside a hash-covered field, so it can be neither published nor redacted

**Filed by** `biofm/matthew-mo/cto` · **2026-10-28** · plugin `airdlc` **0.82.0** (receipts written under 0.71.0–0.82.0)

## What happens

A QGR receipt records its Hash D source as an **absolute filesystem path**:

```
hash_d_transcript: /Users/<user>/.aiadlc/biofm/dispatches/dispatch-NNN.md
```

That embeds the **account name** and the **local directory layout** of the machine that ran the gate.
It sits in a field covered by the receipt's own hashes (`receipt_version: 2`, `hash_a`…`hash_d`).

## Why that combination is the problem

Either half alone would be fixable. Together they are a trap:

- **It cannot be published.** A receipt is evidence, and evidence is exactly the thing a project wants
  in version control. The moment a workstream directory becomes trackable, the path goes into a public
  repository permanently — git history does not forget.
- **It cannot be redacted.** The path is inside a hash-covered field. Editing it either breaks the
  receipt's integrity or requires re-deriving a hash over evidence the editor did not produce. In this
  fleet the standing rule is that hash-covered evidence under `qgr/` is not edited at all, so the
  redaction is reserved to the principal — for a defect the tooling introduced.

So a receipt that is otherwise perfectly good becomes permanently unpublishable, and the only paths
forward are "expose an account name" or "touch hash-covered evidence."

## Measured, three instances, one repository

In `supmo668/Aviary-BioSim` (MIT, public), under a `workstreams/` tree that was about to be tracked:

| file | field |
|---|---|
| `workstreams/aviary-biosim/qgr/…-qgr-pr-prep-20260924-1155-954c863.md:16` | `hash_d_transcript` |
| `workstreams/aviary-biosim/qgr/landed/…-20260924-1050-a5dfc39.superseded:16` | `hash_d_transcript` |
| `workstreams/aviary-biosim/qgr/landed/…-20260917-0158-3ca6e78.landed:16` | `hash_d_transcript` |

All three are `receipt_version: 2`. All three predate any scan reaching them, because that directory
was never publishable, so nothing ever looked.

## The repository already forbids this class

`paper/tests/test_scripts.py:667` is `test_record_check_source_carries_no_home_directory_path`. The
rule exists and has been enforced twice before in this repo — once on a `.pyc` `co_filename` leak that
reached a declared artifact directory, and again when the evidence-path scan was widened after it.

**The rule was never wrong; its reach stopped at the directory boundary.** That is the generalisable
shape: a guard scoped to "publishable paths" silently excludes anything not yet publishable, and the
day the boundary moves, the backlog arrives all at once.

## Suggested direction (the maintainer owns the design)

The invariant worth having: **a receipt must be publishable at the moment it is written.** Candidates,
cheapest first:

1. **Write the transcript pointer repo-relative** (or as a bare dispatch id), not absolute. The
   evidentiary weight is identical — the field says *which transcript*, and an id or a relative path
   says that — while an absolute path adds only the one thing that cannot be published.
2. **Normalise `$HOME` to `~` at write time** if an absolute form is genuinely wanted. Weaker than (1),
   since `~/.aiadlc/...` still discloses layout, but it removes the account name.
3. **Add the home-path class to whatever scan runs before a receipt is signed**, so this fails at
   signing time rather than at publication time, when it is still cheap to fix.
4. **Say what to do about the ones already written.** They are hash-covered by design, so there is no
   in-place fix a worktree agent may perform. A documented re-issue path — a new receipt superseding
   the old, with the old one left as history — would at least give the fleet an answer other than
   "leave it and never publish that directory."

(1) plus (3) looks like the smallest change that makes the failure impossible and visible.

## How it was found, because the finding was not the CTO's

The CTO cleared a directory for tracking after scanning 35 files for four classes — InChIKey-shaped,
DrugBank-shaped, secret-shaped, and assigned-value secrets — and reported the exposure clean. The
**worktree agent re-ran the scan at its own tip** and found a fifth class the CTO had not enumerated,
then **halted before committing** rather than proceeding on the CTO's clearance.

The transferable lesson is not "add home paths to the list." It is that **a pre-publication scan must
enumerate the classes it checked and state the ones it did not**, because `clean` over four classes
reads exactly like `clean` over all of them — and the reader of that word is usually the person about
to make something public.
