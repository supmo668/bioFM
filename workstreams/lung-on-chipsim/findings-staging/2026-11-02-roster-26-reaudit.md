---
type: findings-staging
status: >
  THREE DISTINCT RATIFICATION STATES — do not imply one from another.
  (1) COUNT RULED at approvals row 102 ("Accept formulation-level: stays 6"). The surviving count of
  6 is RATIFIED.
  (2) DISPOSITION OF THE TWO WRONG-SOURCE ENTRIES RULED 2026-11-07, principal, verbatim
  "Confirmed — (b), keep 26", recorded at this ledger's local approvals row 103. Amlexanox and
  Procaterol STAY IN THE ROSTER and are disclosed as defects; the strike to 24 is CANCELLED, not
  deferred, and nothing in configs/ or tests/ moved. They are RETAINED BY RULING, NOT BY EVIDENCE,
  so "26 cited" is true of the count and not of the support — carry that wherever the roster size
  or a cited-row count appears, as part of the ruling and never under "limitations".
  (3) The 26 per-row VERDICTS REMAIN DRAFTED and unratified. No curation act is authorised
  — see section 8.
  CITE BY CONTENT, NOT BY NUMERAL: the ruling was dispatched by the CTO as "row 107" but
  approval-log assigned local 103, because this ledger's approvals.md ended at 102 on the branch and
  on origin/main alike and rows 104-109 exist in no file in the checkout. Two decisions now share
  the number 103 across two ledgers; recorded at local row 104 and the CTO resolves it.
authorization: principal, approvals row **100**, verbatim quote "authorize 3"; relayed via CTO #873.
  Supersedes CTO #870's "do not start it" for THIS item only.
exploratory: false
question: >
  NOT "does each DOI resolve" — the roster loader already established all 26 are present and
  well-formed. The question is whether each cited source is THE RIGHT SOURCE FOR ITS COMPOUND,
  and how many survive at the measured-target-site bar.
reading_depth: >
  ABSTRACT-LEVEL AND METADATA-LEVEL, NOT FULL TEXT. Crossref records for all 21 distinct DOIs,
  plus PubMed abstracts for the 17 rows indexed there. Stated up front because this ledger's own
  section 8.4 holds that an abstract states what a paper is ABOUT, not what it ESTABLISHES.
  Design facts (species, route, what compartment was sampled) are what abstracts do report
  reliably, and no VALUE is extracted from any abstract here.
agent: biofm/matthew-mo/lung-on-chipsim
---

# Re-audit of the 26 already-cited roster rows — DRAFTED, 2026-11-02

> **The original cited table is NOT edited.** Nothing was written to
> `projects/lung-on-chipsim/configs/poc_compounds.yaml`. A re-audit may find a cited row
> unsupported; removing or changing a roster entry is a curation act and it is the principal's
> (CTO #873 limit 1). No InChIKey appears in this file — compound name and DOI only.

## 0 · THE ANSWER: 6 of 26 survive at the measured-target-site bar

| bar | count |
|---|---|
| rows whose cited source **measures human lung / target-site exposure or deposition of that compound** | **6** |
| rows whose source is real and relevant but **does not measure target-site exposure** | 18 |
| rows whose source has a **species or subject mismatch** | 2 |
| rows whose DOI is **unresolvable** | **0** |

**RULED at approvals row 102 — the count stands at 6.** Principal, verbatim: *"Accept
formulation-level: stays 6."* Deposition of a labelled product counts as target-site evidence for
its components, **with the formulation caveat carried in the text** (§2). The strict per-molecule
reading, which would give **4**, is **rejected but deliberately retained** below so a later reader
can see the fork existed and which way it went.

**The sentence any write-up quoting the figure must carry — not the bare 6:**

> **6 of 26 rest on measured target-site exposure — three of them from one 12-volunteer cohort
> (`10.1111/bph.15621`), two more from a single formulation study.**

**6, not 9 and not 13.** The claim under audit was *"of the 26, **9** rest on measured human lung
exposure or deposition"* (section 2 of the 2026-10-30 ledger); approvals row 97 revised the
measured-human-lung pool upward to **13**. **Neither figure is reproducible from the roster's own
citations.** I can find six.

**All 21 distinct DOIs resolve (HTTP 200 at Crossref).** So the "unresolvable" column is empty and
the roster loader was right about what it checked. It simply never checked what this audit checks.

## 1 · A structural finding available before any source was read

**26 compounds carry only 21 distinct DOIs.** Four DOIs are each cited for more than one compound:

| DOI | compounds | what it is |
|---|---|---|
| `10.1111/bph.15621` | Fluticasone Propionate, Salbutamol, Salmeterol | **3 rows** — primary human lung PK study |
| `10.1007/164_2016_68` | Aclidinium, Ipratropium bromide | book chapter, "Muscarinic Receptor Antagonists" |
| `10.1089/jamp.2021.0046` | Beclomethasone, Formoterol | **2 rows** — human deposition study of a combination |
| `10.1016/bs.apha.2023.05.001` | Roflumilast, Theophylline | book chapter, "Phosphodiesterase inhibitors and lung diseases" |

**Two of the four shared DOIs are class-level book chapters.** A shared citation is the signature of
a source selected for a *class* and then attached to its *members* — which is the "right source for
its compound" question in its purest form. It is also, usefully, how three of the six survivors
arise: `bph.15621` genuinely measured all three of its compounds.

## 2 · The six that survive

Measured in humans, at the lung, for that compound. According to PubMed.

| compound | DOI | what the source actually measures |
|---|---|---|
| Salbutamol | `10.1111/bph.15621` | bronchoscopic human lung sampling |
| Salmeterol | `10.1111/bph.15621` | same study, same cohort |
| Fluticasone Propionate | `10.1111/bph.15621` | same study, same cohort |
| Beclomethasone | `10.1089/jamp.2021.0046` | gamma-scintigraphic intrapulmonary deposition |
| Formoterol | `10.1089/jamp.2021.0046` | same study |
| Triamcinolone | `10.1089/08942680152484090` | gamma-scintigraphic lung deposition + PK |

**`10.1111/bph.15621` — Sadiq et al., *Br J Pharmacol* 2021 — is the strongest citation in the
roster.** It is built for exactly the question the bar asks. Verbatim:

> "Human pharmacokinetic studies of lung-targeted drugs are typically limited to measurements of
> systemic plasma concentrations, which provide no direct information on lung target-site
> concentrations."

> "Healthy volunteers received single, sequential doses of either inhaled salbutamol, salmeterol and
> fluticasone propionate (n = 12)"

> "Lung samples were taken via bronchosorption, bronchial brush, mucosal biopsy and bronchoalveolar
> lavage during each bronchoscopy."

All three compounds are named, the species is human, and the sampled compartment is lung tissue and
epithelial lining fluid. **Three rows upheld on one source, and correctly so.**

**`10.1089/jamp.2021.0046` — Usmani et al., *JAMP* 2022, the STORM study — upheld WITH a caveat I am
not burying.** It measures "intrapulmonary drug deposition … determined as the percentage of nominal
(i.e. metered) dose" in "10 healthy volunteers and 9 patients with asthma". But the radiolabel is on
the **formulation**:

> "subjects inhaled study drug (four inhalations of BDP/FF/GB 100/6/12.5 μg radiolabeled using
> technetium-99 m [Tc])"

**So the measurement is of a three-component formulation, not of beclomethasone and formoterol
individually.** It is a genuine measured human lung deposition for the product containing both; it
is **not** a per-molecule deposition figure. These are the two rows most likely to move on a
full-text pass.

**RULED, row 102 — and the caveat is part of the ruling, not a footnote.** The principal accepted
formulation-level deposition, so beclomethasone and formoterol **stay upheld** and the count is 6.
The strict per-molecule reading (**4**) is the **rejected alternative, retained not deleted.**

**Binding consequence:** any text citing STORM for beclomethasone or formoterol target-site exposure
**must carry the formulation qualification**. A citation that silently reads as per-molecule
deposition would misstate the source — which is the exact defect class this audit exists to catch,
so it does not get to re-enter through the ruling that resolved the fork.

**`10.1089/08942680152484090` — Hirst et al., *J Aerosol Med* 2001 — upheld cleanly.** Triamcinolone
acetonide, 99mTc gamma scintigraphy, "10 patients with mild to moderate asthma", lung deposition
reported as both mass and percentage of delivered dose, with plasma PK alongside.

### 2.1 · CONCENTRATION RISK — half the surviving evidence rests on ONE paper

Recorded at the CTO's request (#877) because it is a property of the result a ratifier should meet
before deciding, not a caveat to find afterwards.

**`10.1111/bph.15621` carries 3 of the 6 survivors** — Salbutamol, Salmeterol and Fluticasone
Propionate, all from the same 12-volunteer cohort in a single study. Two more (Beclomethasone,
Formoterol) come from one other study, STORM. So:

| source | survivors it carries |
|---|---|
| `10.1111/bph.15621` (Sadiq 2021) | **3** |
| `10.1089/jamp.2021.0046` (STORM) | 2 — and both subject to the per-molecule fork at §2 |
| `10.1089/08942680152484090` (Hirst 2001) | 1 |

**Two sources carry five of the six.** Read strictly per-molecule, STORM's two fall away and
**`bph.15621` alone carries 3 of the surviving 4.**

**This is a fact about the result, not a defect in it.** `bph.15621` is the roster's strongest
citation and it legitimately measured all three compounds. But "6 of 26 rest on measured
target-site exposure" and "6 of 26 rest on measured target-site exposure, 3 of them from one
cohort" support different claims, and only the second is accurate. Any paper text quoting the
surviving count should carry the concentration with it.

**Under row 102 the fork no longer applies, so the live figure is the first row of the table above
plus the second:** **6, three of them from one 12-volunteer cohort, two more from one formulation
study.** The `3 of 4` variant below the ruling is retained only as the rejected reading.

## 3 · The two with a species or subject mismatch — WRONG-SOURCE

These are not weak sources. They are sources about something else.

**Amlexanox — `10.1002/bmc.5288`.** According to PubMed, the title is "Development and validation of
LC-MS/MS method for amlexanox in **rat plasma** and its application in **preclinical**
pharmacokinetics", and the application is "the pharmacokinetic study of amlexanox in **Wistar
rats**". **The MeSH terms include `Animals`, `Rats`, `Rats, Wistar` and do NOT include `Humans`.**
Three independent mismatches against the bar: wrong species, wrong matrix (plasma, not lung), and
the paper's purpose is **bioanalytical method validation**, not an exposure determination. This is
the clearest wrong-source row in the roster.

**Procaterol — `10.3390/ijms19071999`.** Procaterol *is* named — "β₂-adrenergic receptor agonists
(procaterol, salbutamol, formoterol)" — so the compound is genuinely present, which is what makes
this instructive. But the preparation is **guinea pig trachealis**, and the MeSH terms are
`Animals`, `Guinea Pigs`, `Trachea`, `Muscle, Smooth`. The readout is ex-vivo tracheal relaxation
and receptor crosstalk. **Right compound, wrong species, wrong preparation, no exposure measured.**
This is the same "the species must be named" rule that governed the OCT1 passes, applied here.

## 4 · The eighteen that are weaker than claimed

Each source is real, resolves, and is about its compound or its compound's class. **None measures
target-site exposure of that compound.** Grouped by *why*, because the reasons are what generalise.

**(a) Class-level book chapter standing in for a compound — 5 rows.** Not compound-specific, and not
a primary measurement.

| compound | DOI | source |
|---|---|---|
| Aclidinium | `10.1007/164_2016_68` | book chapter, "Muscarinic Receptor Antagonists" |
| Ipratropium bromide | `10.1007/164_2016_68` | same chapter |
| Roflumilast | `10.1016/bs.apha.2023.05.001` | book chapter, "Phosphodiesterase inhibitors and lung diseases" |
| Theophylline | `10.1016/bs.apha.2023.05.001` | same chapter |
| Clenbuterol | `10.1016/bs.podrm.2017.02.002` | monograph, "Clenbuterol Hydrochloride" |

Clenbuterol's monograph is compound-specific, which is better — but *Profiles of Drug Substances*
documents identity, physicochemistry and analytical methods, not lung exposure.

**(b) Compound-specific REVIEW cited for a measurement it only reports — 6 rows.** PubMed types each
of these as `Review`. Citing a review for a measurement is citation-by-proxy: the measurement, if
any, belongs to a source this one cites.

| compound | DOI | note |
|---|---|---|
| Tiotropium | `10.2165/00003495-200262080-00008` | Adis review; receptor pharmacology + trial efficacy, no deposition |
| Pirbuterol | `10.2165/00003495-198530010-00002` | Adis "A Preliminary Review" |
| Nedocromil | `10.1177/106002809302700515` | Ann Pharmacother review of clinical trials |
| Ibudilast | `10.1517/14656560903426189` | review, and its emphasis is neurological, not respiratory |
| Bitolterol | `10.1002/j.1875-9114.1985.tb03410.x` | review of chemistry/PK/PD/efficacy |
| **Flunisolide** | `10.2500/aap.2015.36.3835` | **the closest near-miss in the roster — see below** |

**Flunisolide is the row I came nearest to upholding, and the reason I did not is worth stating.**
Its abstract does discuss target-site data: the HFA formulation "substantially increased **pulmonary
deposition** and decreased oropharyngeal deposition", and "Examination of **lung biopsy specimens**
indicated a favorable anti-inflammatory response … in peripheral airways". **But PubMed types it
`Review`, and it says so itself** — the assessment was made "through a comprehensive review of the
published literature and data from the past 10 years". So the deposition finding is real and is
*somebody else's measurement*. **The right citation for flunisolide is whichever primary study this
review drew that deposition figure from.** That is a one-source fix, not a dead end, and it is the
single highest-value follow-up in this audit.

**(c) Human measurement, but the wrong route or compartment — 4 rows.**

| compound | DOI | what was actually measured |
|---|---|---|
| Dyphylline | `10.1016/0091-6749(75)90128-1` | 7 human subjects — but **intramuscular and oral**, plasma PK. Not inhaled, not lung. Compound identity confirmed: the paper's "dihydroxypropyltheophylline" is dyphylline |
| Montelukast | `10.1002/(sici)1099-081x(199712)18:9<769::aid-bdd60>3.0.co;2-k` | human PK and bioavailability, **oral**, plasma |
| Budesonide | `10.1186/s12931-015-0318-z` | human cells **in vitro** — 16HBE line and primary bronchial epithelial cells, barrier electrical resistance. Budesonide is a genuine subject; the preparation is not a lung |
| Epinephrine | `10.1007/s11095-026-04048-w` | "Regional **Extrathoracic** Deposition … in an **Idealized Child Airway**". Extrathoracic is by definition **not** lung, and an idealized airway is a physical model, not a person |

**Epinephrine deserves the sharpest note in group (c).** Its source measures inhaled epinephrine
deposition — and measures it in the compartment the lung bar excludes, in a cast rather than a
subject. A reader skimming "deposition of inhaled epinephrine" would bank it as lung data. The word
doing all the work is *extrathoracic*.

**(d) Clinical outcome trial cited for exposure — 3 rows.** Large, real, human, inhaled — and
containing no exposure measurement at all.

| compound | DOI | note |
|---|---|---|
| Indacaterol | `10.1056/NEJMoa1516385` | FLAME. Indacaterol is a genuine subject; the endpoint is **COPD exacerbation rate** |
| Isoetarine | `10.1007/BF02991319` | 1983 "Adrenergic drugs", a class review |
| **Terbutaline** | `10.1056/NEJMoa1715274` | **the compound is not the paper's subject — see below** |

**Terbutaline is the subject-mismatch I want on the record even though I did not score it
wrong-source.** Its citation is SYGMA 1, whose title and purpose are "**Inhaled Combined
Budesonide-Formoterol** as Needed in Mild Asthma". Terbutaline appears as the **control reliever
arm** — "twice-daily placebo plus terbutaline (0.5 mg) used as needed (terbutaline group)". So:
terbutaline really is in the trial, in 1,277 patients, which is why this is not scored
wrong-source — it does evidence inhaled clinical use. **But the paper is about something else, and
it measures no terbutaline exposure of any kind.** A row whose evidence is "it was the comparator"
is a weaker claim than the citation's prestige suggests.

## 5 · What I am NOT concluding — the push-back CTO #873 invited

#873 asked me to say so if the bar itself were wrong — if measured target-site exposure simply could
not be populated from the published record. **I am not saying that, because it can be: six rows
clear it, and one source clears three of them on its own.** The bar is usable. What failed is not
the bar but the **selection**: a class review or an outcome trial was accepted where a deposition or
lung-PK study exists in the literature for several of these compounds.

**That is a different finding from the transporter axis and should not be merged with it.** On the
OCT1/P-gp axes the negative column is empty because the literature does not publish per-compound
negatives — a property of the record. Here the record *does* contain qualifying sources; the roster
just does not cite them. **The first is a limit of the literature; the second is a limit of our
search.** Keeping them apart matters, because the paper's defensible claim is about the first.

## 6 · Limits of this audit, stated so they are not discovered later

1. **Abstract-level and metadata-level, not full text.** Crossref for 21 DOIs, PubMed abstracts for
   the 17 indexed rows. Adequate for design facts — species, route, sampled compartment,
   publication type — and **not** adequate to extract a value, which is why no value is extracted.
   A full-text pass could move individual rows, most plausibly **Flunisolide** (upward, if the
   review's deposition data is its own) and **Beclomethasone/Formoterol** (downward, on the
   per-molecule question at section 2).
2. **Nine rows are not PubMed-indexed** (the book chapters and older titles) and rest on Crossref
   type and title alone. For those, "is it a primary measurement?" is answered from publication
   type, which is strong for a book chapter and weaker for a journal article.
3. **"Weaker-than-claimed" is a verdict about the CITATION, not about the compound.** Nothing here
   says any of these 20 compounds lacks lung data in the literature. Several almost certainly have
   it. The finding is that the roster does not cite it.
4. **I did not re-search for better sources.** #873 authorised an audit of the existing citations.
   Finding replacements is a separate pass and would need its own authorisation.
5. **No biological number originates with me.** Every figure in this file is inside a verbatim
   quotation carrying its DOI, or is a count I derived from the roster file itself.

## 7 · What follows, for the principal

1. **Any paper text resting on "9 rest on measured human lung exposure" is wrong, and so is 13.**
   The ruled figure (row 102) is **6**, quoted with its concentration: *three of the six from one
   12-volunteer cohort, two more from one formulation study.* The per-molecule reading (**4**) is
   recorded as rejected, not deleted.
2. **Two rows should probably not be cited as they stand** — Amlexanox (rat) and Procaterol (guinea
   pig). Changing them is curation and therefore yours.
3. **Flunisolide is a one-source fix** and the best value in the audit.
4. **The 26-row selection method has the same defect row 97 found in the 13**: a source accepted
   without checking it was the right source. Row 97 found false negatives; this finds the
   corresponding false positives. **Symmetric, as predicted.**
