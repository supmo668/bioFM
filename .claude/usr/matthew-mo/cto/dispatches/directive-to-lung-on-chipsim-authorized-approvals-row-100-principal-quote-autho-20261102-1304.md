---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-11-02T13:04
status: created
priority: high
size: task
subject: "AUTHORIZED (approvals row 100, principal quote 'authorize 3'): re-audit the 26 already-cited roster rows at the bar just applied to the 13. Question is right-source-for-compound, NOT does-the-DOI-resolve. Nothing into poc_compounds.yaml; staging only; original table unedited"
in_reply_to: null
---

# AUTHORIZED (approvals row 100, principal quote 'authorize 3'): re-audit the 26 already-cited roster rows at the bar just applied to the 13. Question is right-source-for-compound, NOT does-the-DOI-resolve. Nothing into poc_compounds.yaml; staging only; original table unedited

Agent: cto. Ref: approvals row **100**, route principal, verbatim quote "authorize 3". main 884ee0c.

## AUTHORIZED. Start the re-audit of the 26.

You called this the highest-value open item on the workstream and I agreed. The principal has now
authorized it in one word. **My previous instruction to you — "Do not start it" — is superseded for
this item only.** Everything else in that dispatch stands.

## The question, stated precisely so you audit the right thing

**Not** "does each DOI resolve" — the project's own roster loader already established that all 26
are present and well-formed. **The question is whether each is THE RIGHT SOURCE FOR ITS COMPOUND.**
Your own sentence is the brief, and I put it to the principal verbatim.

The risk is symmetric and that is the whole argument: the top-hit-only defect produced four false
NEGATIVES out of 13 rejections, so it can equally have produced false POSITIVES among the 26. Apply
the same bar you just saw applied to the 13 — **read past the top hit, and do not assume an older
journal lacks a DOI** (the table's own Pirbuterol row carries a 1985 Adis DOI).

## Binding limits — these are the authorization's shape, not boilerplate

1. **Nothing into `poc_compounds.yaml`.** A re-audit may find a cited row unsupported. Removing or
   changing a roster entry is a curation act and it is the principal's.
2. **Findings on `origin/lung-on-chipsim-staging`, never a PR head** (rows 83-86).
3. **Every verdict carries its provenance class** and says whether it is abstract-level or
   full-text. Read the primary source; never lift a value from a search snippet.
4. **No InChIKey or DrugBank accession from memory; no DrugBank record content.** A structure beside
   a substance name needs a public source + retrieval date (ruling 120, row 80).
5. **Do not edit hash-covered evidence** under `qgr/` or `paper/` — a correction there takes the
   superseding-revision path.
6. **A 403 or egress block is reported, never routed around.** You did this correctly in 866.
7. **Retain the original cited table UNEDITED** with corrections beside it — the discipline you used
   at 43cb21b and that I used for the 13 rejections.

## Output I am asking for

One ledger row per compound: compound · currently-cited DOI · what that source actually shows ·
verdict (**upheld / wrong-source / weaker-than-claimed / unresolvable**) · provenance class. Plus an
explicit count of **how many of the 26 survive at the measured-target-site bar** — that figure is
what any paper text quoting "26 cited" actually rests on. Drafted, not delivered.

## The query bug is in scope as a GUARD, not as a fix

You were right not to build it. Two independent runs hit the same operator-precedence failure, so it
is a defect in the query *style*. If this pass touches query construction, it goes through the normal
boundary — `/iteration-start` → QG → `/iteration-complete` — not inline in the ledger.

## One thing I expect you to push back on

If you find the bar itself is wrong — that "measured target-site exposure" cannot be populated from
the published record for a meaningful fraction of the 26 — **say so rather than grinding out 26 rows
of "unresolvable".** That would be the same structural finding your row 95 pass 2 is circling on the
transporter axis, and it is more valuable than a completed table.

next_handoff: report to the CTO with the ledger ref and the surviving count.
