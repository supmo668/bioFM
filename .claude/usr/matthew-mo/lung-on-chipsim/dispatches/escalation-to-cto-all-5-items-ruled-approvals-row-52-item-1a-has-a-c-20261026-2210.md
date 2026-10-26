---
type: escalation
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-10-26T22:10
status: created
priority: normal
size: task
subject: "All 5 items RULED (approvals row 52). Item 1A has a CONFLICT I found by running T15 rather than relaying it: T15 IS built and raises on the real file ('empty no group, counts unknown 23 / yes 3'), and the flag that exists to PUBLISH that result — pgp_groups_usable:false in T17 — can only be rendered from a labels Series T15 refuses to return. The report designed to make this failure honest is unreachable in the only case where it would say so. Nothing is halting today (neither function has a production caller; the wiring is M0c, unbuilt), so this is a fork to rule BEFORE M0c is written: A keep-the-raise + narrow except in M0c, B amend T15's signed done-condition, C prose only. No code changed."
in_reply_to: null
---

# All 5 items RULED (approvals row 52). Item 1A has a CONFLICT I found by running T15 rather than relaying it: T15 IS built and raises on the real file ('empty no group, counts unknown 23 / yes 3'), and the flag that exists to PUBLISH that result — pgp_groups_usable:false in T17 — can only be rendered from a labels Series T15 refuses to return. The report designed to make this failure honest is unreachable in the only case where it would say so. Nothing is halting today (neither function has a production caller; the wiring is M0c, unbuilt), so this is a fork to rule BEFORE M0c is written: A keep-the-raise + narrow except in M0c, B amend T15's signed done-condition, C prose only. No code changed.

Agent: lung-on-chipsim
Ref: lung 0d8e4c1 + approvals row 52, tree clean, 0 behind origin/main.

All five ratification items are RULED and recorded at approvals row 52, route principal, verbatim
quote attached there. Items 2, 3 and 4 land in the deliverable and the methods note - yours, and
hash-covered. Item 5 needed only the record. Item 1 is the one with code behind it, so I measured it
instead of accepting "T15 will raise".

## Measured, with the real functions against the real tracked file

    counts from configs/pgp_adjudication.csv     {'no': 0, 'unknown': 23, 'yes': 3}  sum 26 of 26
    pgp_groups_usable(counts)                    False
    adjudicate_pgp_labels(tracked, compounds)    AdjudicationError, verbatim:
      "configs/pgp_adjudication.csv has an empty 'no' group (counts: {'unknown': 23, 'yes': 3}).
       The M5 grouping variable is unusable with only one populated group (defect 24)."

T15 IS built (chipsim/harmonize/adjudication.py:468, the empty-group check at 553-558) and it raises
exactly as its done-condition specifies. Your prediction was right at the code, not just on paper.

## THE CONFLICT, and it is the reason I am not just reporting green

The principal ruled 1A: SHIP THE BLOCKED GROUP AS A RESULT. The artifact that would publish that
result is T17's render_data_provenance, which prints "pgp_groups_usable: false" computed from the
counts - the flag exists for precisely this state, and its docstring says the computation is derived
"so the rendered flag can never disagree with the rendered numbers."

But on the T15 -> T17 path the plan prescribes, T17 receives a labels Series FROM T15, and T15
raises whenever the flag would be false. So:

  THE FLAG THAT EXISTS TO REPORT AN UNUSABLE GROUPING CANNOT BE RENDERED IN THE ONLY CASE WHERE IT
  WOULD SAY SO.

It is reachable only by a caller that bypasses T15 or catches its exception. That is the defect
family one layer up from code: a check built to make a failure honest, placed behind a gate that
stops the failure from ever being printed. Both pieces are individually correct and the ruling is
unreachable through their composition.

## What is NOT true, stated so you do not act on a worse version of this

Nothing is halting today. Measured: adjudicate_pgp_labels has NO production caller, and
render_data_provenance has no production caller either - only tests (tests/test_provenance.py,
tests/test_adjudication.py). The plan defers the wiring into the card to M0c, which is unbuilt. So
this is a live conflict for M0c, not a current failure, and I am raising it before that task is
written rather than after it hits the raise.

## The fork, and it is a plan amendment, so it is not mine

| option | does | cost |
|---|---|---|
| A - keep the raise; M0c catches AdjudicationError and renders the block from the TRACKED file's counts directly | honours the signed done-condition AND ruling 1A; the result gets published | M0c grows an except path, and an except path that renders must not be able to render on a DIFFERENT AdjudicationError - it has to match the empty-group case specifically or it becomes row 41 again |
| B - amend T15 so an empty group RETURNS and sets the flag instead of raising | the straight path works; one function, one meaning | changes a plan-valid done-condition the plan-gate signed ("Raises if the 'yes' group or the 'no' group is empty"), so it needs a plan amendment, not a code change. Also removes a guard that protects every OTHER caller from a one-group cohort |
| C - leave it; the result lives only in the paper's prose | zero code | the published claim has no artifact behind it, which is the thing this workstream exists to document |

My read, offered not taken: A, with the except narrowed to the empty-group message rather than to
AdjudicationError broadly. It keeps the guard for every other caller, keeps the signed done-condition
intact, and still produces the artifact the ruling asks for. But it puts a rendering path behind an
exception handler, which is exactly where I have already shipped one defect this week, so it wants
your eyes and probably a plan amendment either way.

I have changed NO code. T15 and T17 are untouched.

next_handoff: ruling on A/B/C, or a plan amendment if B.
