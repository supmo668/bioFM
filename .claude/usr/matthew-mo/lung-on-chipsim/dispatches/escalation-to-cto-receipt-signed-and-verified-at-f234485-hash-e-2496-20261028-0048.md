---
type: escalation
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-10-28T00:48
status: created
priority: high
size: task
subject: "RECEIPT SIGNED AND VERIFIED at f234485 (Hash E 24965ba) — but PUSH IS REFUSED and I will not force it. origin/lung-on-chipsim is 249 commits I lack: its tip IS the archived Stage 1 tip c04e701, and ls-remote shows NO archive ref on origin, so that branch is THE ONLY REMOTE COPY of Stage 1. Forcing my branch over it deletes it. Row 51's off-machine bundle does contain c04e701 (verified), so Stage 1 survives as a single org-Drive bundle — trading the last remote git copy for that is a durability decision, not a push. Recommend P1: push Stage 2 to a NEW remote branch and PR from it; P2 (push the archive ref, then force) separately as the real durability fix. /pr-submit NOT sent — its precondition is a pushed branch and I will not manufacture it."
in_reply_to: null
---

# RECEIPT SIGNED AND VERIFIED at f234485 (Hash E 24965ba) — but PUSH IS REFUSED and I will not force it. origin/lung-on-chipsim is 249 commits I lack: its tip IS the archived Stage 1 tip c04e701, and ls-remote shows NO archive ref on origin, so that branch is THE ONLY REMOTE COPY of Stage 1. Forcing my branch over it deletes it. Row 51's off-machine bundle does contain c04e701 (verified), so Stage 1 survives as a single org-Drive bundle — trading the last remote git copy for that is a durability decision, not a push. Recommend P1: push Stage 2 to a NEW remote branch and PR from it; P2 (push the archive ref, then force) separately as the real durability fix. /pr-submit NOT sent — its precondition is a pushed branch and I will not manufacture it.

Agent: lung-on-chipsim
Ref: f234485, tree clean, 0 behind origin/main. RECEIPT SIGNED AND VERIFIED. PUSH BLOCKED.

All six ruled items are built and falsified, the receipt is signed and `receipt-verify` passes at
the tip. I cannot complete /pr-submit, because the push is refused and the only way through it is an
act that is not mine to take.

## THE RECEIPT, and it does verify at the tip

    receipt   workstreams/lung-on-chipsim/qgr/...-qgr-pr-prep-20261028-0045-24965ba.md
    Hash A/E  24965ba90b7e8c5c2c932a7a151408fe7cdd36c0b5637cb55b0c1e1b6d45857d (106 files)
    verify    "Receipt verified ... (Hash E: 24965ba)"

Worth recording: committing the receipt moved the tip 557baee -> f234485 and the hash did NOT
change, because `diff-hash` excludes the QGR directory. I checked rather than assuming, since
otherwise no receipt could ever verify its own commit.

## THE PUSH IS REFUSED, AND FORCING IT WOULD DESTROY THE ONLY REMOTE COPY OF STAGE 1

`git-push` -> `! [rejected] lung-on-chipsim -> lung-on-chipsim (non-fast-forward)`.

Measured, both directions:

    ahead of origin/lung-on-chipsim   742
    BEHIND origin/lung-on-chipsim     249
    merge base                        be51b8b
    remote tip                        c04e701  <- the STAGE 1 tip, exactly as the archived handoff recorded

The 249 commits I lack are Stage 1, which the principal ARCHIVED. My branch deliberately does not
contain them. And:

    git ls-remote --heads origin | grep -iE 'archive|stage1'   -> NOTHING
    git branch -r --contains c04e701                           -> only origin/lung-on-chipsim

SO `origin/lung-on-chipsim` IS THE ONLY *REMOTE* COPY OF THE ARCHIVED STAGE 1 HISTORY. A force-push
of my branch over it deletes that copy. I am not doing that, and I am not routing around it.

WHAT DOES SURVIVE A FORCE, stated precisely so the risk is not overstated either: row 51's bundle is
off-machine on the syntropyhealth.bio org Drive, sha256-matched on both sides, and I verified its ref
0c721b7 CONTAINS the remote tip c04e701. So Stage 1 would not be lost outright - but the surviving
copy would be a single bundle in an org Drive subject to that org's retention and admin access,
which row 51 itself flagged as the reason the destination needed an explicit decision. Trading the
last remote git copy for that is a durability decision, not a push.

## OPTIONS, and I recommend the one that destroys nothing

  (P1) PUSH STAGE 2 TO A NEW REMOTE BRANCH (e.g. `lung-on-chipsim-stage2`) and open the PR from it.
       RECOMMENDED. Non-destructive, needs no force, loses nothing, and the PR works today. Costs a
       branch name that no longer matches the worktree name - which is cosmetic, and the preflight
       binds identity to the LOCAL branch, not the remote one.
  (P2) PUSH `archive/lung-on-chipsim-stage1` TO ORIGIN FIRST, then force-push `lung-on-chipsim`.
       Preserves Stage 1 as a remote git ref AND gives the PR its expected branch name. Two
       remote-mutating acts, one of them a force, so both are yours or the principal's. This is
       also the standing durability fix regardless of the PR - the archive has no remote ref at all
       today, which row 51 did not close because it chose a bundle rather than a ref.
  (P3) MERGE `origin/lung-on-chipsim` into my branch. Fast-forwardable afterwards, no force - but it
       pulls 249 archived Stage 1 commits back into Stage 2 content, contradicting the archive
       ruling and putting the withheld tip back in the PR. I recommend against it and would say so
       on the record.

My recommendation is P1 now so the PR is not held by a durability question, and P2 separately as the
archive-durability fix it is on its own merits.

I have pushed NOTHING. No force has been attempted. /pr-submit is not sent, because its precondition
is a pushed branch and I will not manufacture that.

## GATE, commands named both ways

    uv run pytest -q                                   866 passed / 4 skipped / 0 failed
    uv run pytest -q -m "not network and not integration"  835 / 4 skipped / 31 deselected
    uv run ruff format --check .                       85 files already formatted
    uv run ruff check .                                All checks passed
    uv run ty check chipsim                            25 (baseline)
    uv run ty check tests                              31 (baseline — the 2 extra were my own
                                                       tautologies, now removed not silenced)

A1 and the identifier-gate fixes are each falsified by a probe that asserts its own precondition
first. Amendment B needed NO change and I verified both halves rather than acting: the four
accessions are already in the documented synthetic DB9nnnn range (SOURCES.md:15), and every InChI
input already carries a provenance line - four PubChem CID + retrieval date, one naming the pinned
snapshot as source of record, two marked derived.

One more of mine, found by ty rather than by me: `assert RECORD_BEARING_WRITERS` is statically
always true, so my own anti-vacuity assertion was a tautology - the fourth of the day, written while
removing tautologies. Replaced with a property that can fail; the DECLARED_OUTPUT_ROOTS twin deleted.

next_handoff: ruling on P1/P2/P3.
