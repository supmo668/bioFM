---
type: findings-staging
status: EXPLORATORY — UNRATIFIED. Every verdict is DRAFTED. The principal ratifies or rejects each.
authorization: principal ruling 2026-11-01, lung approvals row 92, relayed via CTO #847 — OCT1
  adjudication pass AUTHORIZED, EXPLORATORY ONLY
exploratory: true
primary_finding_unchanged: the pre-registered P-gp axis (ledger section 1, ratified at approvals row 89)
  remains the PRIMARY finding. This pass NEVER replaces it.
agent: biofm/matthew-mo/lung-on-chipsim
---

# OCT1 (SLC22A1) substrate adjudication — **EXPLORATORY**, pass 1, 2026-11-01

> **EXPLORATORY.** Row 92 authorises this pass as exploratory only. It does **not** replace the
> pre-registered P-glycoprotein axis, and ledger §1 — ratified at row 89 — stays the primary
> finding. Every sentence in this file is to be read as exploratory, and every verdict below is
> **drafted** for the principal to ratify or reject. **No biological number is authored here.**

## The evidence rules this pass applies, the same as the P-gp axis

| rule | how it binds here |
|---|---|
| tri-state | `yes` / `no` / `unknown`, and `unknown` is a RESULT when it follows a search, not a blank |
| `cited` needs a verbatim quote AND a confirmed DOI | a quote is taken from the FULL TEXT, never an abstract |
| substrate ≠ inhibitor | a compound that merely INHIBITS uptake of a probe is **not** thereby a substrate |
| the transporter must be named | an OCT2 / OCT3 / MATE result is **not** an OCT1 result |
| species must be named | a murine or canine ortholog result is **not** a human result |

**An abstract is a locator, never evidence.** That is this workstream's own method statement
(2026-10-31, adopted as house wording after an abstract produced two confident conclusions that
the full text reversed). It binds this pass: **no verdict below is drafted from an abstract.**
Abstract-level findings are recorded in §3 as LEADS and are explicitly not verdicts.

## 1 · Verdicts — DRAFTED

| compound | OCT1 verdict | basis | provenance class |
|---|---|---|---|
| Aclidinium | unknown | **not yet searched in this pass** | — |
| Amlexanox | unknown | **not yet searched in this pass** | — |
| Beclomethasone | unknown | **not yet searched in this pass** | — |
| Bitolterol | unknown | **not yet searched in this pass** | — |
| Budesonide | unknown | **not yet searched in this pass** | — |
| Clenbuterol | unknown | **not yet searched in this pass** | — |
| Dyphylline | unknown | **not yet searched in this pass** | — |
| Epinephrine | unknown | **not yet searched in this pass** | — |
| Flunisolide | unknown | **not yet searched in this pass** | — |
| Fluticasone Propionate | unknown | **not yet searched in this pass** | — |
| Formoterol | unknown | **not yet searched in this pass** | — |
| Ibudilast | unknown | **not yet searched in this pass** | — |
| Indacaterol | unknown | **not yet searched in this pass** | — |
| Ipratropium bromide | **yes** | human OCT1, DIRECT uptake measured by LC-MS/MS in HEK293 cells stably overexpressing human OCT1 | **cited** — full text read at source |
| Isoetarine | unknown | **not yet searched in this pass** | — |
| Montelukast | unknown | **not yet searched in this pass** | — |
| Nedocromil | unknown | **not yet searched in this pass** | — |
| Pirbuterol | unknown | **not yet searched in this pass** | — |
| Procaterol | unknown | **not yet searched in this pass** | — |
| Roflumilast | unknown | **not yet searched in this pass** | — |
| Salbutamol | unknown | **not yet searched in this pass** | — |
| Salmeterol | unknown | **not yet searched in this pass** | — |
| Terbutaline | unknown | **not yet searched in this pass** | — |
| Theophylline | unknown | **not yet searched in this pass** | — |
| Tiotropium | unknown | **not yet searched in this pass** | — |
| Triamcinolone | unknown | **not yet searched in this pass** | — |

**`unknown` here means two different things and the column says which.** For 25 of 26 rows it
means *not yet searched* — an absence of searching, which is **not** a result. Only a row searched
and found wanting at the stated bar would be an `unknown` that IS a result, as in ledger §1.2.
Conflating those two is the error this project exists to document, so pass 1 does not pretend to
have adjudicated 26 compounds.

## 2 · The one verdict's evidence, quoted from the FULL TEXT

**Ipratropium bromide — `yes`.** Meyer, Falk, Römer, Prinzinger, Tacke, Geyer, Simm & Tzvetkov,
*International Journal of Molecular Sciences* 2022;23(9):5100. DOI `10.3390/ijms23095100`
(PMC9102066). **Full text retrieved and read at source** via PubMed Central; according to PubMed.

Verbatim, from the Results:

> "We compared the uptake of five clinically relevant OCT1 substrates (fenoterol, ipratropium,
> trospium, metformin, and butylscopolamine) between dog, mouse, and human OCT1 orthologs."

> "In contrast, ipratropium was transported by human OCT1 with 5.2-fold higher capacity and
> 8.4-fold lower affinity than dog OCT1."

And the basis is DIRECT uptake of the compound itself, not inhibition of a probe — Methods:

> "The intracellularly accumulated substrate concentrations were measured using LC-MS/MS"

in "HEK293 cells stably overexpressing human OCT1 or OCT2, mouse OCT1, and dog OCT1 or OCT2".

**Two attribution caveats I am stating rather than leaving implied:**

1. **The paper's primary subject is the DOG ortholog.** Human OCT1 appears as the comparator. The
   human measurement is nonetheless direct and the human transporter is named in the sentence
   quoted, so the determination holds — but a reader must not cite this as a human-focused study.
2. **The roster entry is "Ipratropium bromide"; the paper's reagent is "Ipratropium bromide"** and
   its analyte is written "ipratropium". Salt versus cation is not resolved by this paper, and it
   is the same salt-vs-cation question the roster's own key carries (see
   `2026-10-31-roster-public-provenance.md`, row 87).

## 3 · LEADS — abstract-level only, explicitly NOT verdicts

Recorded so the pass is resumable and so a later reader can see what was found without mistaking
it for an adjudication. **Each needs its full text read before it can become a verdict.** Both
full-text retrievals attempted for the first two FAILED (PDF unavailable).

| lead | DOI | what the ABSTRACT says | why it is not yet a verdict |
|---|---|---|---|
| Salomon et al. 2015, *Mol Pharm* | `10.1021/mp500854e` | titled "Beta-2 Adrenergic Agonists Are Substrates and Inhibitors of Human Organic Cation Transporter 1"; names salbutamol, formoterol, salmeterol in human respiratory epithelial cells | abstract only; **PDF retrieval failed**. Also: the title itself pairs "substrates AND inhibitors", so which compound is which needs the full text |
| Chen et al. 2017, *Biol Chem* | `10.1515/hsz-2016-0236` | ipratropium and trospium "strongly transported by OCTs and MATEs" | abstract only; **PDF retrieval failed**. "OCTs and MATEs" is plural and unresolved — an OCT2 or MATE1 result is not an OCT1 result |
| Jensen et al. 2019, *Biochem Pharmacol* | `10.1016/j.bcp.2019.113731` | stereoselective OCT1 uptake; names (S)-salbutamol and (R,R)-formoterol | abstract only. Stereoselectivity also means the roster's stereo-free keys may not map 1:1 onto the enantiomer tested |
| Mukherjee et al. 2012, *Int J Pharm* | `10.1016/j.ijpharm.2011.12.036` | in Calu-3 bronchial layers, formoterol, salbutamol, ipratropium and budesonide reduced uptake of the probe ASP+ | **this is INHIBITION of a probe, not transport of the compound.** On this pass's own rules it can never be substrate evidence |
| Ito et al. 2014, *J Pharm Sci* | `10.1002/jps.24138` | terbutaline uptake in HEK293 cells transfected with **murine** Oct1 | **murine ortholog.** Not a human OCT1 result |

**One lead I am recording as a trap rather than as support.** Schnegelberger et al. 2022
(`10.3389/fphys.2022.969363`) reports that salbutamol "did not induce" efflux — but that finding
is about **OATP1B1 and OATP1B3**, not OCT1. Citing it as an OCT1 negative would be a correct
reading of a real result attributed to the wrong transporter, which is this project's recurring
defect. It is **not** evidence either way about OCT1.

## 4 · What this pass does NOT establish

1. **It is EXPLORATORY and ratifies nothing.** Row 92's authorisation is explicit, and ledger §1
   remains the primary finding. Nothing here may move the pre-registered axis.
2. **25 of 26 compounds are UNSEARCHED.** That is not a negative result about them. Pass 1
   established the instrument and produced one full-text-backed verdict; it did not adjudicate a
   roster.
3. **Whether a usable CONTRAST GROUP exists is still unknown**, which was the original question.
   One `yes` tells us the positive group is populatable. It says nothing about whether any
   defensible `no` exists, and a contrast design needs both. Ledger §4 item 2 stands.
4. **No biological number is authored here.** The two fold-change figures quoted are the paper's
   own words inside a verbatim quotation with its DOI, not values I derived.
5. **The instrument's reach is not characterised.** One PubMed query over seven compound names
   returned 12 records. That is a probe, not a search: it can find evidence and cannot establish
   absence (§9.1 of the 2026-10-30 ledger).
