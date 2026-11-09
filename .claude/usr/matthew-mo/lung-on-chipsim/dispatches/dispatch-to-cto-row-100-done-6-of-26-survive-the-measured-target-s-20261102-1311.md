---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-11-02T13:11
status: created
priority: high
size: task
subject: "Row 100 DONE: 6 of 26 survive the measured-target-site bar, not 9 or 13 (4 if read per-molecule). 2 wrong-source, 0 unresolvable. Ledger f9a301a"
in_reply_to: 873
---

# Row 100 DONE: 6 of 26 survive the measured-target-site bar, not 9 or 13 (4 if read per-molecule). 2 wrong-source, 0 unresolvable. Ledger f9a301a

Agent: lung-on-chipsim

## Row 100 done. **6 of 26 survive the measured-target-site bar — not 9, and not 13.**

Ledger: `findings-staging/2026-11-02-roster-26-reaudit.md` at `origin/lung-on-chipsim-staging`
= **f9a301a**. 26 rows, each assigned exactly one verdict, arithmetic verified against the roster
file itself (no row assigned twice, none missed, no extras).

| verdict | count |
|---|---|
| **upheld** — source measures human lung/target-site exposure of that compound | **6** |
| **weaker-than-claimed** — real, relevant, measures no target-site exposure | 18 |
| **wrong-source** — species or subject mismatch | 2 |
| **unresolvable** | **0** |

**All 21 distinct DOIs resolve (HTTP 200, Crossref).** The roster loader was right about what it
checked; it never checked what this audit checks.

## The six, and the one source that carries half of them

`10.1111/bph.15621` (Sadiq, *Br J Pharmacol* 2021) is the strongest citation in the roster and
carries **three rows** correctly — Salbutamol, Salmeterol, Fluticasone. It was built for this exact
question: *"Human pharmacokinetic studies of lung-targeted drugs are typically limited to
measurements of systemic plasma concentrations, which provide no direct information on lung
target-site concentrations"*, then sampled lung by bronchosorption, brush, mucosal biopsy and BAL in
12 volunteers. Plus Triamcinolone (`10.1089/08942680152484090`, scintigraphic lung deposition + PK)
and Beclomethasone + Formoterol (STORM, `10.1089/jamp.2021.0046`).

**One fork I am flagging rather than deciding.** STORM radiolabels the **formulation** — "four
inhalations of BDP/FF/GB 100/6/12.5 μg radiolabeled using technetium-99 m" — so it measures
deposition of a three-component product, **not per-molecule deposition**. If the principal reads the
bar strictly per-molecule, **the surviving count is 4, not 6.** Both numbers are in the ledger.

## The two wrong-source rows

- **Amlexanox** `10.1002/bmc.5288` — "LC-MS/MS method for amlexanox in **rat plasma** … in **Wistar
  rats**". MeSH carries `Animals`, `Rats`, `Rats, Wistar` and **no `Humans`**. Wrong species, wrong
  matrix, and the paper's purpose is bioanalytical method validation.
- **Procaterol** `10.3390/ijms19071999` — procaterol genuinely *is* named, which is what makes it
  instructive, but the preparation is **guinea pig trachealis** (MeSH `Guinea Pigs`, `Trachea`). The
  same "species must be named" rule from the OCT1 passes.

## Three things in the 18 that I think matter more than the count

1. **Flunisolide is a one-source fix and the best value in the audit.** Its citation *does* report
   target-site data — "substantially increased **pulmonary deposition**", "Examination of **lung
   biopsy specimens**" — but PubMed types it `Review` and it says so itself ("through a
   comprehensive review of the published literature"). So the deposition finding is real and is
   **somebody else's measurement**. The right citation is the primary study this review drew it
   from.
2. **Epinephrine's source measures the compartment the bar excludes.** "Regional **Extrathoracic**
   Deposition … in an **Idealized Child Airway**". Extrathoracic is by definition not lung, and an
   idealized airway is a cast, not a person. A reader skimming "deposition of inhaled epinephrine"
   banks it as lung data; the word doing all the work is *extrathoracic*.
3. **Terbutaline, recorded but deliberately NOT scored wrong-source.** Its citation is SYGMA 1,
   whose subject is "Inhaled Combined **Budesonide-Formoterol** as Needed in Mild Asthma"; terbutaline
   is the **control reliever arm**. It really is in the trial in 1,277 patients, so it does evidence
   inhaled clinical use — but the paper is about something else and measures no terbutaline exposure.
   A row whose evidence is "it was the comparator" is weaker than the citation's prestige suggests.

## Your invited push-back: the bar is NOT the problem, and this is NOT the transporter finding

You asked me to say so if "measured target-site exposure" simply could not be populated. **I am not
saying that.** Six rows clear it and one source clears three on its own. **What failed is the
selection, not the bar** — a class review or an outcome trial was accepted where a deposition or
lung-PK study exists in the literature for several of these compounds.

**So this must not be merged with row 95's finding, and I want that on the record.** On the
P-gp/OCT1 axes the negative column is empty because the literature does not publish per-compound
negatives — **a limit of the record**. Here the record *does* contain qualifying sources and the
roster simply does not cite them — **a limit of our search**. The paper's defensible claim is about
the first. Conflating them would overclaim.

**And the symmetry you predicted holds exactly.** Row 97 found the top-hit-only defect producing
false *negatives* among the 13. This finds the corresponding false *positives* among the 26.

## Structural finding, available before any source was read

**26 compounds, 21 distinct DOIs.** Four DOIs serve multiple rows, and **two of those four are
class-level book chapters** (`10.1007/164_2016_68` → Aclidinium + Ipratropium;
`10.1016/bs.apha.2023.05.001` → Roflumilast + Theophylline). A shared citation is the signature of a
source chosen for a class and then attached to its members.

## Limits, stated so nobody discovers them later

**Abstract-level and metadata-level, NOT full text** — Crossref for all 21 DOIs, PubMed abstracts
for the 17 indexed rows. Adequate for design facts (species, route, sampled compartment, publication
type); **not** adequate to extract a value, so **no value is extracted**. Nine rows are not
PubMed-indexed and rest on Crossref type and title. A full-text pass could move **Flunisolide**
upward and **Beclomethasone/Formoterol** downward.

**"Weaker-than-claimed" judges the CITATION, not the compound.** Nothing here says these 20
compounds lack lung data; several almost certainly have it. And **I did not re-search for
replacements** — #873 authorised auditing the existing citations, and finding better ones is a
separate pass needing its own authorisation.

## Limits honoured

Nothing written to `poc_compounds.yaml`; original cited table unedited with corrections beside it;
findings on the staging branch only; no InChIKey or DrugBank content anywhere in the file — compound
name and DOI only; nothing under `paper/` or `qgr/` touched; no query construction changed, so no
code path and no gate needed.

**Two rows probably should not be cited as they stand (Amlexanox, Procaterol) — but that is
curation, so it is the principal's, not mine.**
