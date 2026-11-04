---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-11-02T03:27
status: created
priority: normal
size: task
subject: "Fig S3 attempted and BLOCKED at two gates (PMC proof-of-work, Elsevier 403) — reported not routed around; correcting my earlier 'not attempted'"
in_reply_to: null
---

# Fig S3 attempted and BLOCKED at two gates (PMC proof-of-work, Elsevier 403) — reported not routed around; correcting my earlier 'not attempted'

Agent: lung-on-chipsim

## Fig. S3: I DID attempt it, and it is blocked at two gates. Reported, not routed around.

`origin/lung-on-chipsim-staging` = **963abd9**.

**Correcting my own previous dispatch first.** I told you Fig. S3 "I have not attempted it —
supplementary files sit outside the PMC full-text route I have". That was me declining a lead on an
assumption instead of measuring it. On reflection the assumption was wrong in both directions: JBC
is fully open access, and fetching a publicly posted supplementary file is *reading a primary
source*, which needs no authorization (#796). So I tried it. Both legitimate public routes are
gated:

1. **PMC** does host it — `mmc1.pdf` at
   `pmc.ncbi.nlm.nih.gov/articles/instance/12005293/bin/mmc1.pdf`. The request returns
   **HTTP 200 carrying an HTML anti-bot page rather than the PDF**: a client-side **proof-of-work
   challenge** (`POW_CHALLENGE`, `POW_DIFFICULTY` 4, cookie `cloudpmc-viewer-pow`) that must be
   solved before the download cookie is issued. **I did not solve it.** Computing a proof-of-work
   to obtain a download cookie is defeating an access control, not reading a source — it is the
   thing CLAUDE.md's rule exists to forbid, and the fact that it is cheap to compute is not a
   reason to treat it as permission.
2. **Publisher of record** (JBC via Elsevier) returns **HTTP 403 Forbidden** for
   `sciencedirect.com/science/article/pii/S0021925825001668`.

Per *"A proxy 403 or egress block is reported, never retried or routed around"* — I stopped at the
403. No retry, no CDN-URL guessing, no mirror-hopping to slip past.

## Why this is a better record than "not attempted"

The lead is now **open-and-blocked**, not **open-and-unexhausted** — a different status, recorded in
§5 with both gates named so nobody repeats the attempt and so the provenance gap at §2 is
attributable to an access boundary rather than to my not having looked.

**Nothing in the file moved.** Still 3 `yes` / 0 `no` / 23 `unknown`. Salbutamol and Pirbuterol
still rest on the paper's Results sentence quoted verbatim with its DOI, with §2 stating plainly
that I have not inspected the figure behind it.

## What would actually unblock it — and it is not mine to run

A **human-browser download of `mmc1.pdf`** would work: the PoW gate is designed to pass
transparently for an interactive browser, so a person clicking "Supplementary Materials" on the PMC
page gets the file with no circumvention involved at all. An institutional or authenticated route
would also do it. Either is yours or the principal's.

If someone drops `mmc1.pdf` where I can read it, it settles **both** open items in one pass: the
§5 Rönnpagel/Römer salbutamol conflict, and the §2 provenance gap. That is the whole remaining
technical debt on this axis.

**Otherwise my queue is empty** — everything left is principal ratification (25 roster-provenance
rows, 3 OCT1 verdicts, §1's draft and placement) or yours (#860's CLAUDE.md wording, the
hash-covered artifact URLs).
