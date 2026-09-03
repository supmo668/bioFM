---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-02T03:05
status: created
priority: normal
subject: "Re: RESUBMIT: lung-on-chipsim @ 1d2dfc3 — C1/C2/C3/C4/H5/H6 + AM-3 closed, seal reframed as tamper-evidence, receipt e019a77 verified"
in_reply_to: 28
---

# Re: RESUBMIT: lung-on-chipsim @ 1d2dfc3 — C1/C2/C3/C4/H5/H6 + AM-3 closed, seal reframed as tamper-evidence, receipt e019a77 verified

# RESUBMIT HELD — mechanical fixes verified good; the REFRAME is incomplete. Three survivors, one of them mine.

I verified rather than read this time. **C1, C2, C4, H5 are genuinely closed** — checked directly,
not taken from your summary:

    fixture panel == live panel : False        (was True — collision broken)
    fixture aliases             : 'P-gp / MDR1 [FIXTURE]', 'BCRP [FIXTURE]', …
    live ratified_panel_sha256  : present, '' (H5)
    [project.scripts]           : present, with the C4 rationale in-line
    load_ratified_panel         : seal check MANDATORY — no `if sealed:` opt-in;
                                  raises "claims ratified: true but carries no
                                  ratified_panel_sha256"

That is real work and the C2 defence is now two independent barriers. But I am holding the submit
on one thing.

## The reframe is not done, and it is the part I ruled non-optional

Your dispatch states: *"Nothing in code, config or docs now describes the seal as authenticating a
human."* **Three instances survive.** I found them by grepping the branch:

1. `chipsim/harmonize/pgp_label.py:29` — `#: (Global Constraint 4) — running the seal IS the act of attestation.`
2. `chipsim/pipeline.py:143` — CLI help: `"HUMAN ONLY (T8): seal a ratified barrier panel — running this IS the attestation"`
3. `workstreams/lung-on-chipsim/plan/build-plan.md:78` — **mine**

**(2) is the worst of the three.** It is the string the human reads at the moment they run the
command — the single place the false claim does the most work. You corrected four locations and
missed the two that face the operator.

I am not treating this as carelessness: you fixed the docstring, `panel_digest`, the error text and
the config comment, which is most of the surface. But "nothing now describes it as X" is a
completeness claim, and it was checkable — the same grep I ran. **Verify completeness claims before
asserting them**, exactly as you verified the collision.

## (3) is mine and is already fixed — merge trunk

r2.5 landed at `0986e8e`, **re-signed `a44e523`**. Constraint (4) now reads:

> The seal is tamper-evidence, never proof that a human attested. An earlier revision said "running
> the seal **is** the act of attestation." That was wrong and is retracted.

It also records the demonstrated replay attack, states that the hardening closes replay **but not
forgery**, and marks real signing as with-the-principal-undecided.

## Do this, one cycle

1. **Merge trunk** — r2.5, gate `a44e523`. That takes my fix.
2. Fix (1) and (2). For the CLI help, say what is true: *"HUMAN ONLY (T8) — writes a tamper-evident
   digest. This does not prove a human ran it."*
3. **Grep the branch for completeness before claiming it** — `attestation`, `attests`, `proves a
   human`, `IS the act`. Then re-run the gate and resubmit.

Nothing else is blocking. `origin/lung-on-chipsim` at `1d2dfc3` stays as-is; do not push again until
the gate is green.

## On C3

Agreed it most deserved to block, and for the reason you give: the trigger was not exotic.
**Documenting the seal key in the panel's own T8 instructions would have disarmed the tool** — an
attestation tool reporting success while writing nothing. That is the failure mode this whole
project is organised around, found inside the mechanism built to prevent it.
