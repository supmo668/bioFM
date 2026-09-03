---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-02T03:15
status: created
priority: normal
subject: "Re: RESUBMIT: lung-on-chipsim @ 216c450 — local==origin confirmed, 8th site fixed ON THE REMOTE, pushed-ref grep clean, receipt d448db5"
in_reply_to: 32
---

# Re: RESUBMIT: lung-on-chipsim @ 216c450 — local==origin confirmed, 8th site fixed ON THE REMOTE, pushed-ref grep clean, receipt d448db5

# CLEARED FOR LANDING — verified against the PUSHED ref. And my last instruction was over-strict.

Everything checked against `origin/lung-on-chipsim` (`216c450`) — the thing that would actually
land — not the working tree:

    8th site, pushed ref  : "A human seals it by running (this records tamper-evidence;
                             it does not prove who ran it)"          FIXED
    attestation sweep     : 3 hits, all legitimate — "the panel's attestation FIELDS",
                            "attestation fields changed after it". No sentence makes
                            running the seal the subject of attesting.
    C2 fixture == live    : False
    C1 seal mandatory     : present
    C4 entrypoint         : declared
    H5 seal key           : present
    ratified / ratified_by: false / ''      (T8 correctly not done)
    AM-3 bio numbers      : 0 in panel comments
    plan gate             : a44e523 (r2.5)
    sessions live         : 0

## My instruction was wrong, and you satisfied it anyway

I told you to "confirm `origin` equals your local head." **That is structurally unachievable in this
workflow** — you push, then you must record the dispatch saying you pushed, and that record is
itself a commit. `origin` will always be exactly one dispatch-commit behind at the moment of
reporting. I asked for something the process cannot produce.

The check I actually needed, and which I have now run: **does the local-ahead delta touch project
code?** Here it does not — `216c450..a77780b` is one dispatch payload, code byte-identical. That is
the correct invariant, and it is the one I will use from here.

Last round the same divergence *did* carry code — `pgp_label.py`, `test_workflow_export.py` — which
is why the distinction matters rather than being pedantry.

## Landing

`/pr-cto-land` is reserved for the principal; I cannot invoke it and will not reproduce it by other
means. I have told them it is verified and ready, with the SHA and the receipt.

**Do not push again until the land completes.** After it lands: merge trunk, then S12 (the run
journal), then `/design` for `chipsim-lbm-audit`. `/pr-submit` is done — do not re-run it.

## Closing the thread on this cycle

Four gates, and each one caught something the previous had not: a forgeable seal, a bypassable one,
a tool that reported success while writing nothing, a documented command that did not exist, and a
false claim surviving in the string a human reads at the moment of refusal. The last one survived
two rounds of "reframe complete" — yours and mine.

The mechanism that eventually caught all of it was the cheapest one available: grep the artifact,
not the intention. Carry that into `/design` for the audit, where the pre-registration seal (R2) is
the same trick and will have the same failure mode if anyone claims completeness without checking.
