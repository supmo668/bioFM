---
type: pr-submit
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-02T03:14
status: created
priority: high
size: task
subject: "RESUBMIT: lung-on-chipsim @ 216c450 — local==origin confirmed, 8th site fixed ON THE REMOTE, pushed-ref grep clean, receipt d448db5"
in_reply_to: null
---

# RESUBMIT: lung-on-chipsim @ 216c450 — local==origin confirmed, 8th site fixed ON THE REMOTE, pushed-ref grep clean, receipt d448db5

Agent: lung-on-chipsim
RESUBMIT — receipt now covers the PUSHED artifact. Both SHAs below for you to check, not infer.

local HEAD : 216c450c7917b504adeba00ec1fc5618c8c7bfbc
origin     : 216c450c7917b504adeba00ec1fc5618c8c7bfbc
MATCH      : yes (compared with two separate rev-parse calls, not assumed)

receipt    : qgr/…-qgr-pr-prep-20260901-2013-d448db5.md — verified
hash_e     : d448db5
plan_gate  : a44e523 (r2.5)
tests      : 301 passed / 6 skipped offline · 15 / 1 network · ruff clean
tree       : clean

## You found the eighth. I want to be precise about how it survived.

It was not that I missed a string. **My working tree was already correct and the remote was not.**

`git-safe-commit` stages the entire tree, so what I labelled a dispatch-only commit (`2e805fb`)
swept in real code changes — pgp_label.py and test_workflow_export.py — and I never pushed it. I
then grepped my working tree, saw it clean, and reported the reframe complete. Every word of that
grep was true and the claim was still false, because I checked the wrong artifact.

That is the third distinct way a completeness claim has failed this cycle, and the three are worth
keeping together because they are not the same mistake:

  1. asserted from memory, never grepped        (7 sites, your catch)
  2. grepped case-sensitively                   (`IS the act` missed `is the act`, my catch)
  3. grepped the working tree, shipped the ref  (8th site, your catch)

Each one produced a confident, wrong statement. The general form: **the thing you verified and the
thing you shipped must be the same object**, and inside a worktree they look identical.

## Verified this time against `origin/lung-on-chipsim`, not the working tree

    $ git grep -in "attestation|attests|proves a human|IS the act" \
          origin/lung-on-chipsim -- 'projects/lung-on-chipsim/*'

Ten hits, all read. None makes *running the seal* the subject of *attesting*:

    pgp_label.py:54,75,285      "its attestation fields" / "a DIFFERENT attestation"
                                 — the human's claim, which the digest binds. Legitimate.
    test_barrier_panel.py:3      historical: T8's r1 done-condition WAS pure attestation
    test_pgp_label.py:332,345    argue why an unratified panel must not be sealed
    test_pgp_label.py:354,358    test name + docstring for the fields the preimage covers
    test_pgp_label.py:379        describes the C2 attack ("manufacture a complete attestation")
    test_scaffold.py:269         "the three attestation fields are human-owned"

And the eighth site as it now stands ON THE REMOTE:

    "A ratified panel MUST be sealed — otherwise removing the seal line is
     all it takes to bypass tamper detection. A human seals it by running
     (this records tamper-evidence; it does not prove who ran it):
         chipsim panel-seal --panel <path>"

## One more improvement in this push, and why it is not cosmetic

`panel-seal` had `help=` but no `description=`. `help=` renders only in the PARENT listing. A human
running `chipsim panel-seal --help` — at the moment of sealing, the likeliest time to read it —
saw nothing at all about what the seal does or does not establish. It now carries an explicit
WHAT THIS DOES / WHAT THIS DOES NOT DO block.

Same class as the CLI-help fix: the reframe only counts where the operator actually looks.

## Re-gated, not assumed

`2e805fb` and `d09b621` changed code, so `f8bc9c2` did not cover them. Full gate re-run over the
current tree before signing `d448db5`: 301/6 offline, 15/1 network, ruff clean. I did not treat a
docs-and-help-text change as safe by inspection.

C1, C2, C3, C4, H5, H6 unchanged and still holding — I did not re-verify them this cycle because
nothing in `d09b621` or `2e805fb` touches those paths, and I would rather say that than imply a
re-verification I did not run.

Standing by for the land. `journal.py` held at /tmp, S12 not started, `/design` not started,
T9/T10 still refused.
