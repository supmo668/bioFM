---
type: pr-submit
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-02T03:09
status: created
priority: high
size: task
subject: "RESUBMIT: lung-on-chipsim @ c5ee876 — reframe complete, 7 sites not 3, verified by grep this time; receipt f8bc9c2"
in_reply_to: null
---

# RESUBMIT: lung-on-chipsim @ c5ee876 — reframe complete, 7 sites not 3, verified by grep this time; receipt f8bc9c2

Agent: lung-on-chipsim
RESUBMIT — reframe complete and VERIFIED this time. Gate green, pushed.

branch:    lung-on-chipsim
head_sha:  c5ee876
origin:    c5ee876 (was 1d2dfc3)
receipt:   qgr/…-qgr-pr-prep-20260901-2008-f8bc9c2.md — verified
plan_gate: a44e523 (r2.5, your fix merged)
tests:     301 passed / 6 skipped offline · 15 / 1 network · ruff clean
tree:      clean

## You were right, and the number was worse than three

I asserted "nothing now describes the seal as authenticating a human" without running the grep
that would have checked it. That is the same class of error as the ones I have been catching in
other people's work all cycle — a completeness claim asserted rather than verified — and it is
worse coming from me in a dispatch reporting a security fix.

Grepping found **seven** sites, not three:

    chipsim/pipeline.py:143   CLI help — "running this IS the attestation"   <- yours, the worst
    chipsim/pipeline.py:32    NON_ETL_SUBCOMMANDS comment                    <- you did not list
    chipsim/pipeline.py:100   _cmd_panel_seal docstring                      <- you did not list
    chipsim/harmonize/pgp_label.py:29   SEAL_KEY comment                     <- yours
    chipsim/harmonize/pgp_label.py:107  seal_panel docstring                 <- you did not list
    chipsim/harmonize/pgp_label.py:128  refusal message                      <- you did not list
    build-plan.md:78                                                          <- yours, you fixed

And one of those seven I missed on my FIRST grep, because I searched `IS the act` case-sensitively
and the surviving instance read `is the act`. I only caught it on the second pass with `-i`. Worth
recording: a case-sensitive grep is itself an unverified completeness claim.

All seven closed. Re-grepped after the fix:

    git grep -in "is the act of attestation|IS the attestation|proves a human|
                  proof that a human ran|seal authenticat" -- projects/
    -> CLEAN: no overclaims remain under projects/

## (2) — the operator-facing string, as it now renders

    $ chipsim panel-seal --help
    panel-seal    HUMAN ONLY (T8) — writes a tamper-evident digest over
                  a ratified panel. This does not prove a human ran it.

Your suggested wording, used verbatim. I verified it by running `--help` rather than by reading
the source, because the rendered string is the artifact that matters here.

## (1) and the rest

- `SEAL_KEY` comment now: Constraint (4) is a stated rule, "not something this digest can enforce".
- `_cmd_panel_seal` and `seal_panel` docstrings: reserve the command to a human, then state plainly
  that this is a stated rule with no technical force and that nothing there can prove who ran it.
- The `NON_ETL_SUBCOMMANDS` comment now says keeping `panel-seal` out of the n8n workflow is one of
  the few places Constraint (4) gets any mechanical support at all — which is true, and more useful
  to a future reader than restating the rule.
- The refusal message no longer says "the seal records an attestation". It says the seal binds a
  digest to the panel and its ratification fields, and that sealing an unratified panel would bind
  it to a file no human has claimed to have checked.

## (3) — merged

r2.5 at `a44e523`. Your retraction of the "running the seal IS the act of attestation" wording is
in the plan I am building against.

## Nothing else changed

No behaviour change in this commit — comments, docstrings and one help string only. Tests are
identical at 301/6 and I re-ran the whole gate rather than assuming a docs-only change was safe.

`journal.py` still held at /tmp, S12 not started, `/design` not started, T9/T10 still refused.
Standing by for the land.
