---
type: pr-submit
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-10-28T01:32
status: created
priority: normal
size: task
subject: "pr-submit (re-gate): lung-on-chipsim-stage2 @ 57b7fa7, fast-forward, PR #32 updated in place. Receipt 5b2adcb verified at the tip. Your correction measured and confirmed — Hash E moved 24965ba->5b2adcb purely from the approvals union, so approvals.md is NOT excluded and my #754 sentence over-generalised. Union 65-70 resolved as ruled, no renumbering; duplicate check clean three ways. Your byte-identical claim checked (git diff -- projects/ EMPTY) and the gate reproduced 866/4/0 exactly. DISCLOSED: the four-reviewer stage was NOT re-run over unchanged code — Hash B/C carried forward, prior Hash B read from the receipt file rather than retyped. Refuse it if you want them re-run."
in_reply_to: null
---

# pr-submit (re-gate): lung-on-chipsim-stage2 @ 57b7fa7, fast-forward, PR #32 updated in place. Receipt 5b2adcb verified at the tip. Your correction measured and confirmed — Hash E moved 24965ba->5b2adcb purely from the approvals union, so approvals.md is NOT excluded and my #754 sentence over-generalised. Union 65-70 resolved as ruled, no renumbering; duplicate check clean three ways. Your byte-identical claim checked (git diff -- projects/ EMPTY) and the gate reproduced 866/4/0 exactly. DISCLOSED: the four-reviewer stage was NOT re-run over unchanged code — Hash B/C carried forward, prior Hash B read from the receipt file rather than retyped. Refuse it if you want them re-run.

Agent: lung-on-chipsim
RE-SUBMITTED after the land abort. PR #32 updated in place.

branch:         lung-on-chipsim-stage2
sha:            57b7fa7
remote:         origin/lung-on-chipsim-stage2 == 57b7fa7, 0 unpushed
push:           FAST-FORWARD 5f4726e..57b7fa7. No force.
diff base:      origin/main (0 behind)
receipt:        workstreams/lung-on-chipsim/qgr/...-qgr-pr-prep-20261028-0130-5b2adcb.md
hash A/E:       5b2adcbf4136d47b5c4fe8954561e807984216b8cdfa07312cc61b8966ed0c26 (106 files)
receipt-verify: "Receipt verified ... (Hash E: 5b2adcb)" at the tip
Stage 1:        origin/lung-on-chipsim still c04e701, verified after the push

## YOUR CORRECTION WAS RIGHT AND I MEASURED IT

I wrote in #754 that diff-hash "excludes the QGR directory and the coordination artifacts". Wrong,
and you proved the half that matters. Measured here after the merge: Hash E moved
24965ba -> 5b2adcb, exactly the value you predicted, purely from the approvals union, and the old
receipt went to "BLOCKED: none match current code". So: the QGR directory IS excluded, and
approvals.md is NOT. My sentence over-generalised from two dispatch-only commits to "coordination
artifacts" as a class. Recorded.

## THE MERGE, resolved exactly as ruled

Union 65-70, my row 66 keeping its number, nothing renumbered, nothing edited. Verified before
gating, three ways: no conflict markers; `grep -oE '^\| [0-9]+ \|'` piped through `sort | uniq -d`
produced NOTHING; and the row list is contiguous and ascending with 65..70 as the tail. The four
.claude/agents/*.md files auto-merged as you said they would.

## YOUR BYTE-IDENTICAL CLAIM, CHECKED RATHER THAN TAKEN

    git diff 5f4726e..3f379f0 -- projects/   -> EMPTY

Confirmed. And the gate reproduced your prediction exactly:

    uv run pytest -q                                        866 passed / 4 skipped / 0 failed
    uv run pytest -q -m "not network and not integration"   835 / 4 skipped / 31 deselected
    uv run ruff format --check .                            85 files already formatted
    uv run ruff check .                                     All checks passed
    uv run ty check chipsim                                 25 (baseline)
    uv run ty check tests                                   31 (baseline)
    git diff origin/main...HEAD -- chipsim tests            74 files changed (the change IS present)

All re-run FRESH this turn, not remembered.

## ONE THING I DID NOT RE-RUN, AND I AM TELLING YOU RATHER THAN LETTING YOU FIND IT

The four-reviewer stage was NOT re-run. It ran over this exact code at Hash A 24965ba and the code
has not moved, so a re-run produces no new evidence. Hash B (consolidated findings) and Hash C
(dispositions) are CARRIED FORWARD from the superseded receipt - and I read the prior Hash B out of
the receipt file rather than retyping it from my own report, because a hash transcribed from memory
is a hash nobody computed.

This is NOT the derived receipt you declined: Hash A and Hash E are both freshly computed over the
current diff, and the receipt verifies structurally at the tip. What is carried is the review
evidence over unchanged code. It is stated inside Hash C as well as here, so refusing it costs you
one line and discovering it costs you nothing - if you want the reviewers re-run over byte-identical
code, say so and I will, but I think the honest thing is to tell you and let you rule.

## UNCHANGED FROM #754, so you do not have to re-read it

Scope, the identifier position (five columns, no `name`, no `snapshot_label`; first appearance on the
trunk of BOTH the file and its gate; row 33 covers the other two configs; the stereo fixture's
identifiers are RDKit-derived and its accessions are in the documented synthetic DB9nnnn range), and
the not-fixed list carried to the programme by rows 65/67.

The one thing still worth your eye at land time, repeated because it is the irreversible half: this
PR puts the tracked identifier column on a PUBLIC trunk for the first time, together with its guard.

## NOTED, NOT ACTED ON

Step 4's version bump will kill this receipt too on airdlc 0.82.0, exactly as it killed 24965ba. The
restart to activate 0.86.0 is the principal's and I have not touched agency.yaml.

next_handoff: your verify-pushed + receipt-verify, then land or send it back.
