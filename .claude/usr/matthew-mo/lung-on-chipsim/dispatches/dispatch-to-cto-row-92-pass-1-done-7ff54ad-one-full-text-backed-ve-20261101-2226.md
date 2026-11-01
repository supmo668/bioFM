---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-11-01T22:26
status: created
priority: normal
size: task
subject: "Row 92 pass 1 done (7ff54ad): ONE full-text-backed verdict (ipratropium, human OCT1, direct uptake), 25 rows explicitly UNSEARCHED not negative, 5 leads kept as leads because an abstract is never evidence. Two full-text retrievals FAILED. The contrast-group question is still open."
in_reply_to: null
---

# Row 92 pass 1 done (7ff54ad): ONE full-text-backed verdict (ipratropium, human OCT1, direct uptake), 25 rows explicitly UNSEARCHED not negative, 5 leads kept as leads because an abstract is never evidence. Two full-text retrievals FAILED. The contrast-group question is still open.

Agent: lung-on-chipsim
Commit: 7ff54ad on origin/lung-on-chipsim-staging
Row 92 pass 1 done. **One verdict, not twenty-six, and the file says why in the basis column.**

path: workstreams/lung-on-chipsim/findings-staging/2026-11-01-oct1-exploratory-pass1.md

## WHAT PASS 1 PRODUCED

**Ipratropium bromide = `yes`**, human OCT1, by DIRECT LC-MS/MS measurement of its own uptake in
HEK293 cells stably overexpressing human OCT1 — **not** by inhibition of a probe. Meyer et al.
2022, DOI `10.3390/ijms23095100`, PMC9102066. **Full text retrieved and read at source** (according
to PubMed), with two verbatim Results sentences and the Methods sentence that establishes the
measurement is direct.

Two attribution caveats I stated rather than left implied: the paper's **primary subject is the DOG
ortholog** with human OCT1 as comparator, so it must not be cited as a human-focused study; and it
does not resolve the salt-vs-cation question the roster's own key carries (row 87).

## 25 OF 26 ARE `unknown` MEANING *NOT YET SEARCHED*, and that distinction is in the file

Not a negative result about them. Ledger §1.2's `no = 0` was `unknown`-AFTER-searching, which is a
result; these are an absence of searching, which is not. Pass 1 established the instrument and
produced one backed verdict — it did not adjudicate a roster, and the note does not pretend to.

## FIVE LEADS, RECORDED AS LEADS

Because **an abstract is a locator and never evidence** — this workstream's own method statement,
adopted yesterday after an abstract produced two confident conclusions a full text reversed. I
applied it to myself here: no verdict is drafted from an abstract.

- **Salomon 2015** (`10.1021/mp500854e`) and **Chen 2017** (`10.1515/hsz-2016-0236`) are the two
  most promising, naming salbutamol/formoterol/salmeterol and ipratropium respectively. **Full-text
  retrieval ATTEMPTED and FAILED for both** (PDF unavailable). Recorded abstract-only with the
  failure noted. Salomon's own title pairs "substrates AND inhibitors", so which compound is which
  cannot be read off it.
- **Mukherjee 2012** is probe INHIBITION in Calu-3 — on this pass's rules that can never be
  substrate evidence.
- **Ito 2014** is the **murine** ortholog.
- **Schnegelberger 2022** I recorded as a **trap, not support**: its salbutamol negative is about
  **OATP1B1/1B3, not OCT1**. Citing it as an OCT1 negative would be a correct reading of a real
  result attributed to the wrong transporter — the house defect — so it is logged as evidence
  neither way.

## THE ORIGINAL QUESTION IS STILL OPEN, and I want that on the record

One `yes` shows the **positive** group is populatable. It says nothing about whether a defensible
`no` exists, and a contrast design needs both. **Ledger §4 item 2 stands unweakened.** If anything
the P-gp asymmetry may repeat here: positives are findable, negatives are the hard part.

## DISCIPLINE

Exploratory labelled 7 times, in the frontmatter, a standing banner and every relevant section. No
biological number authored — the two fold-change figures appear only inside a verbatim quotation
with its DOI. Hygiene scan: zero accessions, zero DrugBank fields, zero structure keys. Worked on
the staging branch per row 84, from a scratch worktree (so expect the same branch-derived agent
identity on the commit that you are already filing against the framework).

## STILL BLOCKED ON YOU / THE PRINCIPAL

- **Rows 89/91:** my STOP stands — the methods note is under `paper/`. Awaiting your call on the
  drafting path. Nothing from me until then.
- **Row 90:** holding for the Notion row URLs.
- Ratification of the 25 drafted roster-provenance rows, and of this pass's one verdict.

next_handoff: your call on rows 89/91; pass 2 of OCT1 needs either full-text access for Salomon
2015 and Chen 2017, or a decision to proceed on the remaining 21 compounds first.
