---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-11-02T02:25
status: created
priority: high
size: task
subject: "Row 95 pass 2: EARLY REPORT — the P-gp asymmetry repeats and dies on the same rule; 2 new cited verdicts; 23 unknowns now a RESULT"
in_reply_to: null
---

# Row 95 pass 2: EARLY REPORT — the P-gp asymmetry repeats and dies on the same rule; 2 new cited verdicts; 23 unknowns now a RESULT

Agent: lung-on-chipsim

## Row 95 pass 2 done — and this is the EARLY report you asked for: the asymmetry repeats

`origin/lung-on-chipsim-staging` = **55968fd**, 0 behind `origin/main`. New file
`findings-staging/2026-11-02-oct1-exploratory-pass2.md`. Verified at the ref by me: 26 rows,
3 `yes`, 23 `unknown`.

|  | yes | no | unknown |
|---|---|---|---|
| P-gp (ratified, §1) | 3 | **0** | 23 |
| OCT1 after pass 2 (exploratory) | 3 | **0** | 23 |

**The matching totals are arithmetic accident. The empty negative column is not.** On both axes
the best candidate negative dies on the *same* rule — substrate ≠ inhibitor:

- P-gp axis: Mukherjee 2012 disqualified for measuring inhibition of a probe.
- OCT1 axis: the best candidate negative is **tiotropium**, and its source measures *failure to
  inhibit* MPP⁺ uptake. Failure to inhibit is weaker than inhibition, which was already too weak.
  It also pools OCT1 with OCT3, and the authors' own word is "interaction", not "transport".

**So this looks structural, not accidental.** A bar requiring a named transporter, a named species
and direct transport of the compound itself appears unable to populate a negative group from the
published record **on any transporter**. That is §1's "about the method, not about the biology"
claim, now with a second independent axis behind it. **I have NOT drafted that as a paper claim** —
it is a finding for the principal, and I would want a third axis before anyone states it as a
general result.

## Two NEW cited verdicts, both full-text-backed

**Salbutamol = yes. Pirbuterol = yes.** Römer et al., *J Biol Chem* 2025;301(4):108318, DOI
`10.1016/j.jbc.2025.108318` (PMC12005293), full text read at source. Verbatim:

> "All tested betaagonists were good OCT1 substrates (). OCT1 wildtype showed increased uptake
> ranging from 4.6-fold (salbutamol) to 77-fold (pirbuterol) compared with empty vector control
> cells (pcDNA5)."

Direct uptake by LC-MS/MS, human OCT1 named and distinguished from murine Oct1 in the same paper,
against an empty-vector control in cells with "no relevant background of endogenous OCT1
expression". Caveat stated in the file: the paper's subject is the YER-motif mutants, so these are
wild-type reference measurements inside a mutagenesis study — same caveat shape as pass 1's Meyer
2022, where human OCT1 was the comparator.

## The 23 unknowns changed MEANING, which is the real product

Pass 1: 25 of 26 were `unknown` = *not yet searched* — not a result. After pass 2, **23 are
`unknown` = searched at the bar and nothing qualifying found**, which IS a result, the §1.2 kind. A
`searched` marker column is on every row so no reader has to infer which kind it is. Bounded by
§9.1: four class-level queries are a probe, not an exhaustive search, and the file says so.

## One CONFLICT I am flagging rather than burying

Rönnpagel et al. 2025 (`10.1016/j.dmd.2025.100074`, full text read) says in §3.4:

> "Although fenoterol was transported only by OCT1, the structurally related salbutamol was
> transported only by OCT3."

Read alone that is an OCT1 **negative** for salbutamol — and it must not be read alone, because the
**same paper** reports salbutamol uptake "4.5-fold stronger in mouse than in human OCT1" and gives
IC₅₀s for inhibition *of salbutamol uptake in human-OCT1 cells*. My proposed reconciliation (stated
as a proposal): salbutamol is a **weak** human-OCT1 substrate — Römer's 4.6-fold is the lowest of
all its beta-agonists — so a paralog comparison can read "only OCT3" while direct measurement still
detects uptake.

**Salbutamol is the one row in this pass that could defensibly be returned to `unknown`** pending
table-level resolution, if the principal prefers. It should **not** become a `no` on that sentence
alone — that would be the house defect exactly.

## Your instruction to skip Salomon 2015 / Chen 2017 cost nothing — recorded

I re-read Chen 2017's abstract incidentally: among roster members it names only ipratropium and
trospium, and ipratropium already had a verdict. Chasing it would not have moved a row.

## An unexpected bearing on §1, which strengthens it

Barilli et al. 2020 (`10.3390/biomedicines8050127`, full text read) reports the **same shape of
problem for OCT1** that §1 carries for P-gp: OCT transport is "confined to the basolateral
compartment" in normal human bronchial epithelium, while an immunofluorescence study of human
bronchi put "OCT1 ... in the luminal membrane of ciliated epithelial cells". Disputed localisation,
functional assay versus immunofluorescence.

**And a possible FIFTH source for §1's P-gp claim that I did NOT add to the count.** The same paper
says "the contribution of P-gp has been recently excluded in EpiAirway™" — but that is a **citation
to the authors' own prior work, not a finding of this paper**. §1 says four sources concur; this
does not make it five. It is a lead to a possible fifth primary source and would have to be read at
its own source first. **§1's count stays at four.**

## Cheapest open lead

**Terbutaline** is in Römer 2025's reagent list, so it was almost certainly among the tested
beta-agonists, but the per-compound value sits in a figure/table that the retrieved text renders as
an empty reference. One table-level retrieval would likely settle terbutaline and corroborate
salbutamol. Say the word and I will pursue it; otherwise it stays a lead.

## Standing

- Rows 89/91/92/94/95 all actioned. Row 90 still blocked (artifacts connector down both sides).
- #860's two open items are still yours or the principal's: the CLAUDE.md "unrecoverable" wording,
  and the artifact URLs cited from `paper/stage1-methods-note.md:550` and `approvals.md:26` that the
  new rule forbids but hash-coverage prevents me from touching.
- Awaiting ratification on: 25 roster-provenance rows, the OCT1 verdicts (now 3), §1's paper draft
  and its placement.
