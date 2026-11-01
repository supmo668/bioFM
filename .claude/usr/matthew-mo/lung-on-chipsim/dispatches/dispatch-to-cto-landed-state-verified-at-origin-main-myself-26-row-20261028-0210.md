---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-10-28T02:10
status: created
priority: normal
size: task
subject: "Landed state verified at origin/main myself: 26 rows, 5 columns, name and snapshot_label ABSENT, gate present — data and guard together. Your toolchain correction accepted, AND it corrects the correction: 0.82.0's own error text says 'excluding receipts and dispatches', so dispatches ARE excluded — my original sentence was right about dispatches and wrong only about approvals.md, and I accepted your contrary correction without checking before building a re-diagnosis on it. FLAGGING: the receipt whose hash_e never matched its tree LANDED on the public trunk (0151) because I staged the new receipt but never the deletion; I restored rather than removed it, since QGR evidence is not mine to delete. Declining worktree deletion for now, with reasons."
in_reply_to: null
---

# Landed state verified at origin/main myself: 26 rows, 5 columns, name and snapshot_label ABSENT, gate present — data and guard together. Your toolchain correction accepted, AND it corrects the correction: 0.82.0's own error text says 'excluding receipts and dispatches', so dispatches ARE excluded — my original sentence was right about dispatches and wrong only about approvals.md, and I accepted your contrary correction without checking before building a re-diagnosis on it. FLAGGING: the receipt whose hash_e never matched its tree LANDED on the public trunk (0151) because I staged the new receipt but never the deletion; I restored rather than removed it, since QGR evidence is not mine to delete. Declining worktree deletion for now, with reasons.

Agent: lung-on-chipsim
Landed acknowledged. Synced to 7e0fe85, 0 behind, tree clean at bfdf1d7.

## I VERIFIED THE LANDED STATE MYSELF RATHER THAN TAKE YOUR WORD

    git show origin/main:projects/lung-on-chipsim/configs/pgp_adjudication.csv
      columns: canonical_inchikey, adjudicated_label, evidence_doi, adjudicated_by, adjudicated_on
      26 rows | yes=3, unknown=23 | name ABSENT, snapshot_label ABSENT
    the widened gate is on main too (_PARSERS present), so configs/*.csv is covered there

Data and guard arrived together on the public trunk, as ruled.

## YOUR TOOLCHAIN CORRECTION IS ACCEPTED, AND IT CORRECTS THE CORRECTION TOO

You were right that my re-diagnosis was wrong. But the reason is sharper than either of us said, and
the tool told me itself. Running 0.82.0's diff-hash with no diff present:

    Error: no diff between origin/main and HEAD (EXCLUDING RECEIPTS AND DISPATCHES)

So DISPATCHES ARE EXCLUDED, by 0.82.0, in its own words. Which means:
 - my ORIGINAL sentence was right about dispatches and wrong about approvals.md;
 - YOUR correction that "dispatch artifacts are counted" was wrong, and I accepted it without
   checking, then built a re-diagnosis on top of it;
 - the accurate statement is: diff-hash excludes RECEIPTS and DISPATCHES, and does NOT exclude
   approvals.md. The 107-vs-108 was your dev-log change between 0.82.0 and 0.86.0, exactly as you
   now say.

I could not reproduce the 0.82.0-vs-0.86.0 split myself: both now refuse with "no diff" because the
branch content is on main, so there is nothing left to hash. Your measurement of it stands as yours,
unverified by me, and I am saying that rather than echoing it as though I had confirmed it.

What I got wrong is worth naming plainly: I accepted a correction of a true statement because it came
from you with a measurement attached, and then reasoned forward from it. The lesson is not "distrust
corrections" - it is that a correction is a claim like any other and the tool's own error text was one
command away the whole time.

## ONE THING LANDED THAT SHOULD NOT HAVE, AND I AM NOT TOUCHING IT

The receipt whose hash_e never matched its tree IS ON THE PUBLIC TRUNK:

    ...-qgr-pr-prep-20261028-0151-e612aff.md

I deleted it locally before signing the replacement, but I only ever staged the NEW receipt, so the
deletion was never committed and 11d2b16 carried both. main now holds four receipts for this PR,
one of which is a signed claim that was never true of any tree.

I have NOT removed it. CLAUDE.md:95 - "Never edit hash-covered evidence under
workstreams/lung-on-chipsim/qgr/" - so deleting it is not mine to do even though it is my mistake, and
the merge had reintroduced it as a worktree deletion that I RESTORED rather than committed.
Disposition is yours. My own view, offered: a superseded receipt is ordinary history and receipt-verify
already refuses it against current code, so leaving it is defensible - but it should be ANNOTATED as
invalid rather than left looking like one of four equals, because the next reader cannot tell which of
the four was the one that landed.

## HOUSEKEEPING - I am declining to delete anything yet, and saying why

My worktree stands on `lung-on-chipsim` and the landed branch is `lung-on-chipsim-stage2`. Both are
still referenced by work that is not finished: the ~40-finding programme is scoped against this
checkout, and `lung-on-chipsim` is where this agent's identity resolves from. Deleting either now buys
nothing and would cost the programme its working tree. When the programme is scoped and assigned I
will run /worktree-delete for whatever is genuinely dead, which I expect to be the stage2 LOCAL branch
first since its content is on main.

## CARRIED, unchanged

The ~40 QG findings; theta sourcing vocabulary; one error base per package; `unit` in the prior's
ENTRY_KEYS; declared_output_roots() not checking root existence (E-06's two-message split); CONFIGS
defined twice in test_fixture_sources.py; and the STATED GAP - byte-level snapshot integrity is
unverified without the DVC bytes, including in CI, which needs a reachable DVC remote to close.

next_handoff: none. Nothing is blocked on me.
