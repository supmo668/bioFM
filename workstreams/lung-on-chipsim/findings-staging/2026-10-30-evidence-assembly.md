---
type: findings-staging
status: UNRATIFIED — NOT FOR ANY PUBLIC SURFACE OR DEPOSIT
authorization: principal 2026-10-30, cto-loop arm-time, authorization (1) — the agent MAY DRAFT
  findings and numbers, each marked cited/derived/assumed WITH ITS SOURCE. Ratification by the
  principal is the gate. This file IS the staging ledger that authorization names.
track: lung-on-chipsim, EVIDENCE ASSEMBLY (secondary; aviary-biosim leads this window)
agent: biofm/matthew-mo/lung-on-chipsim
measured_at: 6006903 (origin/main 71efacc)
---

# Evidence assembly — staging ledger, 2026-10-30

**What this file is.** Drafted findings for the principal to ratify or reject. **Nothing here is
ratified and nothing here may reach the paper, a deposit, or any public surface until it is.**
Every number carries a marker and a source:

| marker | means |
|---|---|
| **cited** | taken from a named external source with a DOI, or from a named tracked in-repo file |
| **derived** | computed by me in this session from tracked repository data; the command is stated |
| **assumed** | no source; a stated gap. Carries its width or its reason, never a bare value |

**This does not suspend "no coding agent writes a biological number."** Every biological value below
is either `cited` to a DOI the principal already accepted, or `derived` by running the project's own
code over the principal's own ratified verdicts. I have introduced no new biological value.

---

## 1 · THE PRIMARY RESULT — the pre-registered contrast axis could not be populated

**Written as a result, not as a gap.** This is the finding, not an obstacle in front of one.

### 1.1 The measurement

| quantity | value | marker | source |
|---|---|---|---|
| roster size | 26 | **derived** | `len()` over `configs/pgp_adjudication.csv` |
| `yes` | 3 | **derived** | `chipsim.eval.provenance_block.label_counts`, the project's own deriver |
| `no` | **0** | **derived** | same call |
| `unknown` | 23 | **derived** | same call |
| `pgp_groups_usable` | **False** | **derived** | `pgp_groups_usable(counts)` — `yes>0 AND no>0` |
| `yes` rows carrying a DOI | 3 of 3 | **derived** | non-blank `evidence_doi` where label is `yes` |
| `unknown` rows carrying a DOI | 0 | **derived** | required 0; `CITED_LABELS` is `{yes, no}` |

The three accepted sources, as the principal ratified them:
`10.1016/j.taap.2012.03.008`, `10.1208/s12248-019-0313-2`, `10.1038/sj.bjp.0704390` — **cited**,
read from the `evidence_doi` column of the tracked file.

### 1.2 The result, stated

**On a pre-registered P-glycoprotein substrate axis over a 26-compound ATC R03 roster, the
literature supports a positive group and does not support a negative group at all.** `no = 0` is not
a shortfall in search effort: all 26 were searched, the search record is published, and `unknown`
here is a finding reached *after* searching rather than an absence of searching (**cited** —
approvals rows 49, 54).

**No relaxation of the positive bar can populate the negative group.** The criterion was amended
mid-adjudication by the principal — a single well-cited source may carry a verdict, conflicts resolve
to the better-cited source (**cited**, approvals row 54, principal's words). Applying it moved `yes`
from 2 to 3 and left `no` at 0. The reason is structural rather than procedural: the only
sub-threshold compounds in the governing source are not on this roster, and that source's conclusion
about the compound class is *comparative* rather than a per-compound negative (**cited**, row 54).

**So the pre-registered grouping variable is unpopulatable from the published literature, and the
study reports that rather than substituting a different variable after seeing the result.**

### 1.3 Why this is a result and not an excuse — two independent reasons

1. **It was predicted before the verdicts were typed, not discovered after.** The arithmetic
   consequence — `pgp_groups_usable` false, the downstream gate raising on an empty group — was
   recorded *before* any verdict was entered (**cited**, approvals rows 49 and 54; row 49's words:
   "THE CONSEQUENCE THE PRINCIPAL MUST SEE BEFORE TYPING RATHER THAN AFTER"). A null result stated
   in advance of the data is a different epistemic object from one discovered afterwards.
2. **The axis's biological aptness was independently challenged, and the challenge was recorded as a
   limitation rather than used to discard the axis.** Four sources concur that P-gp is largely absent
   from human airway epithelium, and in the one model that has it functionally it is on the
   **wrong membrane** (**cited**: `10.1016/j.ejps.2025.107333`, `10.1183/13993003/erj.38.suppl_55.p843`,
   `10.1016/j.ejpb.2013.06.010`, `10.1211/jpp.61.03.0003`, and `10.1038/sj.bjp.0704390` for the
   basolateral mislocalisation). The ruling was to **keep** the pre-registered axis and carry the
   finding as a cited limitation (**cited**, approvals row 48) — i.e. the axis was not abandoned once
   it became inconvenient.

### 1.4 The honest scope of the claim

This is a claim about **the literature**, not about lung biology. What is established is that *a
two-source (as amended, well-cited-single-source) bar over this roster yields no negative group*.
What is **not** established is that any roster compound is not a P-gp substrate — absence of a
published finding is not evidence of non-substrate status (**cited**, row 49). The coverage claim the
PoC can make is therefore about **the method**, not about lung P-gp biology (**cited**, row 48).

---

## 2 · DRAFT REPLACEMENT TEXT for the methods note's dead citation

Per the CTO's revised ruling (**CTO dispatch, 2026-10-30**, and its correction — **no approvals
row covers it**; the "approvals row 79" citation used here until 2026-10-31 was wrong, see the
AUTHORITY note in `configs/poc_compounds.yaml`): inline what survives, state the
loss as a finding, **do not reconstruct the per-row tiers**. This is draft text for the principal to
ratify as author of record — the methods note is hash-covered and I have not touched it.

> **Provenance of the compound roster.** The 26-entry roster was selected from a mechanically derived
> candidate pool: every compound in the pinned snapshot carrying an ATC R03 code, giving **39
> candidates** against a pre-registered band of 20–40 (**cited** —
> `qa/_adhoc/lung-on-chipsim-t18-candidate-list.md`, tracked). All 39 were searched; **26 carry a
> resolvable DOI and 13 do not, each with its reason recorded**, and of the 26, **9 rest on measured
> human lung exposure or deposition** while the remainder establish class pharmacology, clinical
> inhaled use, or in-vitro deposition (**cited**, same file). Each of the 26 roster entries carries
> its own `evidence_doi` in the tracked configuration (**derived** — 26 of 26 verified by the
> project's own roster loader).
>
> **A part of this provenance record is unrecoverable, and we state which part.** The full per-row
> table — per compound: what each source showed, and a per-row confidence tier — together with the
> 13 rejections' *individual* reasons, was recorded only on an ephemeral, account-scoped surface that
> no longer resolves. The aggregate counts above survive in the repository; **the reasoning behind
> each individual row does not.** We have not reconstructed it: a confidence tier recovered from
> recollection or re-inferred from the sources would be a fabricated provenance record, which is the
> precise failure this study's integrity model exists to prevent. Restoring per-row tiers would
> require a new adjudication pass, not a repair.
>
> **The general lesson, which we report because it cost us this record.** Links to account-scoped
> ephemeral surfaces are not citations. Such a URL is unreadable from any account but its author's,
> and therefore dead for *every* reader of a published paper from the moment of publication — it was
> never alive for anyone else. Provenance that a reader must be able to check belongs in the
> versioned repository.

---

## 3 · CANDIDATE NOVEL COMPUTATIONAL CLAIMS — named with evidence, NOT built

Task 3. These are **candidates**, not results. Each states what would have to be true for it to be
novel, which I have **not** established — see §4.

### 3.1 Stereochemical-identity loss across a public reference drug set
**Claim shape:** a measurable fraction of a widely used public drug snapshot carries *relative*
rather than absolute stereochemistry, so any pipeline keying on a canonical structure hash silently
merges distinct stereoisomers unless it detects and flags that case.
**Evidence in hand:** the snapshot contains **42** relative-stereo compounds, of which **13** were
classified by InChI layers against PubChem (**cited** — the header of
`projects/lung-on-chipsim/tests/test_relative_stereo.py`, tracked; marked `cited` and **not**
`derived`, because I read it from an in-repo comment rather than recomputing it this session).
**Why it may be novel:** the M0 spine already detects it per compound and carries
`stereo_is_relative` as a generated column into downstream joins.
**What is missing:** I have not recomputed 42/13 myself, and I have not checked whether this is
already published.

### 3.2 The asymmetry of transporter-substrate literature, measured
**Claim shape:** for a therapeutically coherent compound set, the published literature supports
positive substrate assignments and supplies **no** defensible negative assignments at a stated
evidential bar — so a case/control design over such an axis is unpopulatable *in principle from the
literature*, not merely unpopulated here.
**Evidence in hand:** `yes = 3, no = 0, unknown = 23` over 26 compounds at a stated, pre-registered,
and then principal-amended bar, with the full search record published (**derived** + **cited** as in
§1).
**Why it may be novel:** it is a quantitative statement about publication practice, derived from an
auditable adjudication ledger rather than asserted.
**What is missing:** `n = 26` on one transporter in one ATC class. Generalisation would need a second
transporter or a second class, which is a new adjudication pass.

### 3.3 Identity-layer coverage loss from toolchain refusal
**Claim shape:** a pinned cheminformatics toolchain refuses a measurable, enumerable subset of a
public snapshot's structure strings, and that subset is a reproducible coverage gap rather than a
data defect.
**Evidence in hand:** **8** compounds recorded as unparseable, with the reason stated as the pinned
RDKit version refusing complete source strings (**cited** —
`projects/lung-on-chipsim/configs/unparseable_compounds.yaml`, tracked; 8 **derived** by counting it).
**Why it may be novel:** the exclusion set is tracked, named and reproducible against a pinned
version, which is unusual — such compounds are normally dropped silently.
**What is missing:** whether the refusal reproduces on other RDKit versions. Untested.

### 3.4 A candidate I am NOT advancing, and why
I recalled a finding about an organism-field convention in a public protein dataset silently dropping
a human edge set. **I searched `approvals.md` for its supporting measurement and did not find it.**
It is therefore **unsourced recollection** and I am not drafting it as a finding, not even marked
`assumed` — an `assumed` value needs a stated width or reason, and "I remember measuring this" is
neither. If it was measured, the record is somewhere I did not look; if it was not, it must not enter
a ledger. Recorded here so the candidate is not lost, explicitly as unusable in its current state.

---

## 4 · WHAT THIS DOES NOT ESTABLISH

Task 4, stated before anyone finds it.

1. **No novelty claim is substantiated.** §3 names candidates. I ran no prior-art search for any of
   them — the `researcher` subagent provably cannot reach PubMed or Undermind (**cited**, approvals
   row 49) and `CLAUDE.md:100` forbids answering from search snippets. **Every "why it may be novel"
   above is a hypothesis, not a finding.**
2. **Whether an OCT1 axis would yield a usable contrast group is unknown**, and it is the question
   that decides whether the downstream uncertainty milestone is recoverable at all. It needs the
   CTO's connectors. Until answered, §3.2's "in principle" is stronger than the evidence: I have
   shown it for *this* transporter, not for the apt one.
3. **No biological number in §1 originates with me.** All three `yes` DOIs are the principal's
   accepted sources; the counts are derived from their ratified verdicts by the project's own code.
4. **The per-row provenance loss in §2 is permanent** on current evidence. I did not attempt
   recovery, and §2 explicitly forbids reconstruction.
5. **42/13 in §3.1 is `cited` from an in-repo comment, not `derived`.** I did not recompute it. A
   figure read from a comment is exactly the "wrong extent" hazard this workstream documents, so it
   is marked as what it is.
6. **The JOTE fee position is unverified at source** — the journal's pages returned HTTP 403 and a
   403 is reported, never routed around. Opening the fee page remains the principal's submission-time
   act (**cited**, the methods note's own instruction).
7. **Nothing here is ratified.** This file is staging. If any number above appears on a public
   surface without the principal's ratification, that is the failure this ledger exists to prevent.

---

## 5 · ADDENDUM 2026-10-30 — the CTO's partial search: what it changed, and what it did not

Source: CTO dispatch #786, answering the two research questions this ledger left open. It
reported **partial** results and disclosed its own instrument failures. Recorded here as a new
section rather than folded into §1–§4, so that **§4 stands exactly as it was written before
anyone searched.** Nothing in this section is ratified either.

### 5.1 OCT1 — the axis is not obviously unpopulatable. §4 item 2 STANDS UNCHANGED.

| quantity | value | marker | source |
|---|---|---|---|
| PubMed records, `"SLC22A1 lung"` | 20 | **cited** | CTO dispatch #786, PubMed via the CTO's connector |
| PubMed records, `"OCT1 bronchial epithelial"` | 10 | **cited** | same |

**What this establishes.** An OCT1-in-lung literature **exists**; the axis is not obviously
unpopulatable. That is a genuine narrowing — beforehand it was unknown in both directions.

**What it does not establish, and why §4 item 2 is not weakened.** A record count is not a
verdict. Neither query asked, and neither answer reports, whether **defensible per-compound
negative assignments** exist at a stated evidential bar — and that is the only thing that could
populate a contrast group. The CTO stated this limit itself and directed that §4 item 2 not be
weakened on the strength of its dispatch. It is not weakened. Settling it needs a scoped
adjudication pass over a named roster, which is **not authorized and has not been started**.

### 5.2 Two instrument failures, both disclosed — and both the house defect

- **A nine-term PubMed query returned 0 records** (CTO, self-disclosed). PubMed ANDs every term,
  so a conjunction that narrow is expected to return nothing. **A 0 from that query is a broken
  instrument, not an absent literature.** Read as absence it would have been this project's
  recurring defect exactly: a correct reading of a real measurement attributed to the wrong
  subject.
- **The prior-art tool caps at 3 results.** Three results is a sample, not a prior-art search.
  **§4 item 1 therefore stands in full** — no novelty claim in §3 is substantiated — and the cap
  is now a *measured* reason rather than an assumed one.

### 5.3 One adjacent lead, recorded with its limits stated

**Rollison et al., *Drug Metabolism and Disposition*, 2024 — an IQ Consortium survey**
(**cited** as a bibliographic lead from CTO dispatch #786; **I have NOT read it at source**, so
it is marked as a lead and no number from it is reproduced here). Reported finding: in vitro
transporter **inhibitors** were largely not followed up clinically, whereas **substrates**
generally were.

**Why it is recorded rather than omitted.** It is adjacent to §3.2 and any reviewer would find
it. Quietly omitting a known adjacent result while drafting a novelty-adjacent claim is the
citation-hygiene failure this ledger exists to prevent.

**Why it does not support §3.2 — stated plainly, because the resemblance is the trap.** It is an
asymmetry in the **clinical follow-up** of in vitro findings. §3.2 claims an asymmetry in the
**publication of negative substrate determinations**. Those are different objects: a compound can
be followed up and still never yield a publishable negative determination, and one never followed
up may have had a negative determination published. **The lead is context, not evidence for the
claim, and it must not be cited as if it were.** Whether to frame §3.2 against it at all is the
principal's call; the CTO declined to rule, correctly, since it is a judgement about my own
claim's framing.

---

## 6 · THE NUMBER-SUBJECT SWEEP, and a draft methods statement it produced

CTO #792 escalated 6,802-vs-6,610 as a **paper item, not housekeeping**, and asked for a sweep:
for every number here, ask *what else would produce that number*, then assert the distinguishing
property. Three independent instances had already turned up (`pgp_groups_usable` false two ways;
42 rows vs 42 identities; 6,802 rows vs 6,610 keys), which is why it is a sweep and not three
fixes.

### 6.1 Draft methods statement — subject-naming for the snapshot counts

For the principal to ratify as author of record. It belongs with the stereo-identity material,
and the CTO's judgement is that it is a **better-evidenced version of §3.1's claim than §3.1
currently makes**. Not written to the methods note, which is hash-covered and untouched.

> **Two counts describe the pinned snapshot, and they are not interchangeable.** The snapshot
> contains **6,802 rows** and **6,610 distinct canonical identities** (**derived** —
> `tests/test_published_snapshot_counts.py`, which pins both against the artifact). The
> difference of **192** is not an error in either figure: canonical keys are assigned
> **stereo-free**, so rows the source never distinguished stereochemically pool onto one
> identity. That pooling is the intended consequence of the keying rule adopted for this study,
> not a defect in the data (**cited** — the relative-stereo ruling, approvals row for 2026-09-15).
>
> **We therefore name the subject of every count in the same sentence as the count**, as
> *rows* or as *distinct canonical identities*, and never write a bare "compounds" where the two
> diverge. A quantity that is correct on two surfaces and means something different on each is a
> defect in the writing rather than in the data, and it is the failure mode this study documents:
> a correct reading of real evidence attributed to the wrong subject.
>
> **The same rule governs the relative-stereo count.** The snapshot carries **42** relative-stereo
> entries, and those 42 rows resolve to **42 distinct identities** — no two share a canonical key
> (**derived** — same module). The count is therefore a statement about 42 compounds, not 42 rows
> of unknown overlap. Of the 42, **13** were classified by InChI layers against PubChem as the
> mirror image of the key they had been given (**cited** — the relative-stereo ruling; this figure
> rests on an external per-compound comparison and is **not** reproducible from this repository).

### 6.2 The sweep, item by item

What else would produce this number, and is the distinguishing property asserted?

| number | what else would produce it | distinguishing property | asserted |
|---|---|---|---|
| roster 26 | 26 rows of anything; 26 rows with blanks | key set equals the roster's; no duplicate key; 26 typed | **yes** — `50c13b1` |
| `yes` 3 | 3 casing variants projected; 3 without a citation | out-of-domain refusal; every `yes` carries a DOI | **yes** — `50c13b1` |
| **`no` 0** | nothing adjudicated at all; the label column absent | `yes > 0`, counts sum to 26, column asserted present | **yes** — `50c13b1` |
| `unknown` 23 | 23 blanks read as `unknown` | nulls refused; `unknown` is a completed verdict, not a blank | **yes** — T15, pre-existing |
| `pgp_groups_usable` False | **both** groups empty (a different result) | `no == 0` **and** `yes > 0` asserted separately | **yes** — `50c13b1` |
| 6,802 | the distinct-key count; a different snapshot | pinned beside 6,610 with the relation asserted | **yes** — `156980e` |
| 6,610 | the row count | as above | **yes** — `156980e` |
| 9 attributes | nine *different* columns | the **named** column tuple, not the numeral | **yes** — `156980e` |
| 42 relative-stereo | 42 rows pooling to fewer identities | flagged rows **==** flagged keys | **yes** — `156980e` |
| 8 unparseable | 8 of anything | exact ID set **plus** RDKit version and source commit | **yes** — pre-existing |
| 39 candidates | a broken extractor returning any number; 39 rows pooling to fewer | instrument precondition, negative control, identities | **yes** — `1400bf7` |
| 26 selected | 26 chosen by any other means | every roster key is in the derived pool; **zero** outside | **yes** — `1400bf7` |
| 13 unselected | **13 lacking a resolvable DOI — a different predicate** | pool size pinned *before* the complement | **partly** — see 6.3 |
| 13 mirror-image | — | external InChI-layer comparison against PubChem | **no** — not derivable here |
| 9 on measured exposure | — | external judgement about each source | **no** — not derivable here |

### 6.3 The two numerals that are NOT what they look like

1. **13 unselected ≠ 13 without a resolvable DOI.** Both are 13 and they denote the same *set*,
   but only because selection was *defined* as "every candidate carrying a resolvable citation".
   The repository records which candidates were **selected**; it never recorded why each
   unselected one was rejected, and that per-row record died with the account-scoped surface
   (§2). So the complement is **derived** and the DOI predicate stays **cited**. A paper sentence
   that writes "13 lacked a resolvable DOI" is making the stronger claim and must cite the
   external search, not the pool arithmetic.
2. **A set difference is insensitive to a member leaving the pool.** Found by falsifying, not by
   reading: strip the R03 code from one *roster* compound and the pool falls 39 → 38 while
   `candidates − roster` stays 13, because both sides shrink together. The first draft of that
   test asserted only the difference and **passed on that broken tree**. It now pins the pool
   size and the intersection first. *A count asserted without its subject is not a measurement.*

### 6.4 What the sweep changed about §3.1 and §2

- §2's **39** moves from `cited` to `derived`, and its central provenance claim — that the roster
  was selected *from* the mechanical ATC R03 pool — is now **asserted** rather than narrated.
- §3.1's **42** moves from `cited` to `derived`; its **13** cannot move and is marked as such.
- Three numerals examined turned into **fifteen**; two are irreducibly external and one is a
  predicate collision. Nothing in §1–§5 was found to be *wrong*. What was missing was the
  **subject**, which is exactly the finding.

---

## 7 · A PRIOR-ART INSTRUMENT BECAME AVAILABLE, and it found evidence AGAINST §3.2

Recorded the same day. **This section weakens one of my own candidate claims.** It is here because
§5.3 established the rule that a known adjacent result is recorded rather than omitted, and that
rule cannot apply only when the result is convenient.

### 7.1 The instrument — and the subject distinction, which matters

The **Undermind** MCP connector became reachable in this session and was **probed today**
(the principal's own connected account — identity deliberately not recorded here; one workspace,
11 pre-existing deep searches, none covering
this question). **derived** — the probe ran and returned results.

**§4 item 1 is NOT refuted, and I am not restating it as false.** Its cited constraint (approvals
row 49) is that *the `researcher` subagent* provably cannot reach PubMed or Undermind. That is a
claim about **a different instrument**. What changed is that *another* instrument, reachable
directly from this session, now exists. Row 49 stands as written about its own subject.

**One semantic query returning 12 results is a PROBE, not a prior-art search**, and the asymmetry
is the whole point:

> A probe can **refute** novelty — one genuine hit suffices. It can **never establish** novelty,
> because absence in a sample says nothing about the corpus.

That is the same logic as this study's own `no = 0`, applied to my own claim. So what follows is
load-bearing in one direction only.

### 7.2 §3.2's novelty is now substantially in doubt

| paper | DOI | status | why it threatens §3.2 |
|---|---|---|---|
| Lee et al. 2022, *Pharmaceutics* | `10.3390/pharmaceutics14102078` | **abstract read at source**; PDF available, full text NOT read | a systematic, quantitative audit of in vitro transporter-mediated findings and their follow-up/labeling for FDA approvals 2017–2021, reporting what fraction of substrate findings reach a label |
| Cicali et al. 2020, *Clin Pharmacol Ther* | `10.1002/cpt.1768` | **title only** — abstract not retrieved | "A Scoping Review of the Evidence Behind CYP2D6 Inhibitor Classifications" — the same methodological move (audit the evidence base behind a classification) already published in a neighbouring domain |
| McFeely et al. 2019, *Clin Transl Sci* | `10.1111/cts.12623` | **title only** | systematic identification and evaluation of clinical substrates for OATP1B1/1B3 |

**What this establishes.** §3.2's stated ground for novelty — "a quantitative statement about
publication practice, derived from an auditable adjudication ledger rather than asserted" — is
**no longer a hypothesis in an empty field**. Published work does the same *kind* of thing, and
at least one piece does it for transporters specifically.

**What it does not establish.** Whether any of them makes §3.2's *specific* claim — that the
literature supplies **no defensible negatives at a stated bar**, so a contrast design is
unpopulatable *in principle* — is **unknown**, because I have read one abstract and two titles.

**The operative consequence:** §3.2 must not be advanced as novel until Lee et al. 2022 is read
in full. Its PDF is available, so that is a cheap, concrete next step rather than an open-ended
search.

### 7.3 §5.3 upgraded — the Rollison lead is read at the abstract, and my stated limit is CONFIRMED

Rollison et al. 2024, *Drug Metabolism and Disposition* 52:582–596, `10.1124/dmd.123.001587`
(**cited** — abstract read at source today; full text NOT read, no PDF available).

Verbatim from the abstract: *"the majority of in vitro inhibitors were not reported to be followed
up with a clinical study by the submitting company, whereas those compounds identified as
substrates generally were."*

Two results, both worth stating:

1. **The CTO's relayed characterization was accurate** — now *verified at the source* rather than
   carried on relay.
2. **§5.3's limit statement is confirmed, not merely plausible.** It is an asymmetry in clinical
   **follow-up**, not in the **publication of negative substrate determinations**. §5.3 drew that
   distinction before the abstract was available; the abstract supports it. It remains **context,
   not evidence for §3.2.**

### 7.4 A NEW, CHECKABLE DIRECTION on the question the CTO could not answer — and it is not where anyone was looking

From Lee et al. 2022's abstract: drugs *"were not labeled on the drug interactions with claims for
their low interaction potential, evidenced by clinical studies or scientific rationales."*

**Reading (one abstract — a lead, not a finding):** defensible **negative** determinations about
transporter interaction evidently *do* get made and documented — in **regulatory submissions and
labeling**, which are not the PubMed-indexed primary literature the adjudication searched.

If that holds, it implies a **scope qualifier**, not a reversal:

- §1.4 currently says the claim is "about **the literature**". The sharper statement may be "about
  the **PubMed-indexed primary literature**" — because a negative group might be populatable from
  **regulatory/labeling sources at a different evidential bar**, which the pre-registration did
  not contemplate.
- This is **cheaper to check than an OCT1 adjudication pass** and bears on the same blocker.

**§4 item 2 remains VERBATIM and unweakened.** This is an additional direction to evaluate, not a
weakening of a stated gap, and nothing here is ratified. **Do not write the qualifier into §1
until the principal rules**, because narrowing a published claim's scope is an author's decision.

---

## 8 · CORRECTING §7, WHICH IS AN HOUR OLD — I read Lee 2022 in full and §7 was wrong twice

§7 rested on **one abstract**. I then read the full text (open access). It corrects §7 in **both**
directions, and §7 is left standing above rather than edited, because a ledger that quietly
revises itself is not a record.

Source: Lee, Chang, Yoon, Jin & Chae, *Pharmaceutics* 2022, 14, 2078,
`10.3390/pharmaceutics14102078` — **full text read**, not an abstract.

### 8.1 §3.2's novelty is NOT refuted by this paper. §7.2 overstated the threat.

The full text does **not** make §3.2's claim, on any of the three counts that matter:

- It **does not** state or quantify that the literature supplies no defensible **negative**
  substrate determinations, and **sets no evidential bar** for one.
- It **does not** construct a case/control or substrate-vs-nonsubstrate design, and **does not**
  say such a grouping cannot be populated. Its groupings are by transporter, labeling outcome and
  follow-up action.
- It is **mainly a tabulation of labeling outcomes and follow-up actions**, *not* an audit of the
  evidence behind substrate/inhibitor classifications.

Decisively, on the exact confusion §3.2 turns on: the paper reports how often a substrate study
was *available* and how often a drug was *identified as a substrate* — and **availability of a
study and a positive result are distinct categories in its tables.** It does **not** characterise
every other drug as a tested negative.

**So §7.2's "substantially in doubt" was an overstatement generated from an abstract.** The
abstract's framing *sounded* like §3.2's claim; the paper's actual object is different. That is
**the house defect, committed by me, in the section announcing the sweep for it** — a correct
reading of a real abstract attributed to the wrong *subject*, where the subject is what the paper
is actually about.

**Where §3.2 now stands:** unrefuted by this paper and still **unestablished** — a probe cannot
establish novelty. The closest remaining threat is **Cicali et al. 2020** (`10.1002/cpt.1768`),
a scoping review of *the evidence behind* CYP2D6 inhibitor classifications, which is the
evidence-audit move §3.2 claims. It is **unread — no PDF available.**

### 8.2 §7.4's labeling lead is substantially WEAKER than I reported — and the paper warns against my exact inference

§7.4 inferred that defensible negative determinations live in regulatory labeling. The full text
does not support that, and specifically cautions against it:

- The no-label evidence comes from **FDA NDA review documents, approval letters and labels** —
  per-drug in the regulatory record, potentially citable as a review or label, but the paper
  **does not establish that any of it was published in the peer-reviewed literature.**
- The decisive distinction: these are **negative DDI findings, or rationales for not labeling an
  interaction** — ***not*** necessarily determinations that a compound **is not a substrate**.
  The rationales include high permeability, low solubility, weak transporter involvement, short
  treatment duration, or the transporter not being a major elimination route. The reading is
  explicit that these "should not be recast as a general, evidentially standardized set of 'not a
  substrate' determinations."
- **Provenance caveat the paper states about itself:** where FDA acceptance was not stated, the
  authors' analysis reflected **the sponsor's claim**. So the rationales are not uniformly
  independent regulatory conclusions.

**A THIRD PREDICATE COLLISION, and it is the same shape as the other two.**

| reading | what it is |
|---|---|
| "negative DDI finding" | this drug does not produce a clinically relevant interaction |
| "negative substrate determination" | this drug is not transported by this transporter |

Different claims. A regulatory record full of the first supplies **none** of the second. §7.4 read
the first as the second. Compare 6,802-vs-6,610 (rows vs identities) and 13-unselected-vs-13-
without-a-DOI (selection vs citation): **three collisions, three different numbers, one shape.**

### 8.3 The net effect on §1 — it is STRENGTHENED, not weakened

The correction cuts the other way from how §7.4 read it. If the regulatory record holds
no-DDI-label rationales rather than standardized not-a-substrate determinations, then **the
negative group is not quietly available in labeling either**, and §1's finding is *more* robust
than §7.4 implied, not less.

The honest adjacent support, and it is weaker than §3.2's claim — **cited**, verbatim:

> "Less information was available for hepatic and renal transporter substrates compared to that
> for transporter inhibition, potentially because drug developers do not necessitate the
> determination of whether the drugs are substrates for all transporters; however, most drugs
> should be evaluated for their inhibitory effects on transporters."

That is an asymmetry in **what gets determined at all** — adjacent to §3.2, not the same claim,
and recorded with the difference stated.

**§1 is NOT amended and §4 item 2 remains VERBATIM.** No scope qualifier is written into §1.4:
§7.4 proposed one on the strength of an abstract, this section withdraws the ground for it, and
in any case narrowing a published claim is the author's decision.

### 8.4 What this episode is, as a method note

Inside one hour: an abstract produced a confident conclusion in **two** directions, and the full
text reversed **both**. Nothing was fabricated and no number was wrong — the readings were
attributed to the wrong subject. *An abstract states what a paper is about; it does not state
what the paper establishes.* Treat an abstract as a locator, never as evidence.

---

## 9 · METHOD STATEMENT, the exact strengthening of §1, and one paper I cannot read

Written at CTO direction (#796), which asked for three things: the probe-asymmetry rule stated as
a method statement rather than a footnote; **exactly how** §1 is strengthened, so the principal
ratifies the strengthened version and not the one they last saw; and Cicali 2020 recorded
honestly.

### 9.1 METHOD STATEMENT — the evidential asymmetry of a sampled literature probe

> **A sampled probe of the literature can refute a novelty claim but can never establish one.**
> One genuine prior-art hit is sufficient to refute: existence needs a single witness. No number
> of misses is sufficient to establish: absence in a sample says nothing about the corpus.
>
> This is the same logic as this study's own central result. `no = 0` over 26 compounds is a
> finding about **the searched literature**, not a demonstration that no compound is a
> non-substrate (§1.4). Applied to our own claims, it means **every "why it may be novel" in §3
> is a hypothesis for as long as our prior-art evidence is a sample** — and all of it is a sample.

Stated as a standing rule because it was earned twice in one day, in opposite directions: a
3-result cap (CTO, §5.2) and a 12-result semantic probe (§7.1) are both samples, and the second
being four times larger changes nothing about what it can establish.

### 9.2 EXACTLY HOW §1 IS STRENGTHENED — ratify this version, not the earlier one

§1's text does **not** change. What changed is the **evidential standing** of the claim it makes,
in two specific and separable ways. Both arrived from reading Lee et al. 2022 in full
(`10.3390/pharmaceutics14102078`).

**(i) A named alternative source for the negative group was checked, and it does not supply one.**

Before today, §1 asserted that the literature yields no negative group, and the obvious objection
— *you searched the wrong corpus; negative determinations live in regulatory filings* — had never
been tested. §7.4 raised exactly that objection from an abstract. The full text answers it: the
regulatory record carries **negative DDI findings and rationales for not labeling an
interaction**, which are **not** determinations that a compound is not a substrate, and some of
which are **the sponsor's claim rather than an independent regulatory conclusion** (§8.2).

So §1 now carries a **survived challenge**, which it did not have this morning: the most plausible
alternative home for a negative group was named, checked, and found not to contain one. *A claim
that has survived a specific attempt to break it is a different epistemic object from one that
has merely not been attacked.*

**(ii) §1's asymmetry now has a published mechanism, where before it had only a pattern.**

§1.2 established *that* the literature supports a positive group and not a negative one. It did
not say *why*. Lee et al. 2022 supplies a reason, **cited** verbatim:

> "Less information was available for hepatic and renal transporter substrates compared to that
> for transporter inhibition, potentially because drug developers do not necessitate the
> determination of whether the drugs are substrates for all transporters; however, most drugs
> should be evaluated for their inhibitory effects on transporters."

Read precisely: **substrate status is not systematically determined**, whereas inhibition
generally is. That is a mechanism for a shortfall in substrate determinations of all kinds, and it
makes §1's finding an instance of a documented structural feature rather than a local accident of
our roster.

**What (ii) does NOT license.** It is an asymmetry in **what gets determined at all**, not in the
**publication of negative determinations**, and not evidence for §3.2's stronger claim. The
distinction is the same one §5.3 drew about the Rollison lead, and it holds here too.

### 9.3 Cicali 2020 — unread, and recorded as a stated limitation

Cicali et al. 2020, *Clinical Pharmacology and Therapeutics*, `10.1002/cpt.1768`, "A Scoping
Review of the Evidence Behind CYP2D6 Inhibitor Classifications."

| property | status |
|---|---|
| bibliographic identity | **confirmed** — journal, pages 116–125, DOI resolved via the connector |
| abstract | **not retrieved** |
| full text | **UNAVAILABLE** — measured, not assumed: the PDF route returned `unavailable` for this paper |
| what I have read of it | **the title, and nothing else** |

It is the **closest open threat to §3.2**, because a scoping review of *the evidence behind* a
classification is precisely the move §3.2 claims as novel — in a neighbouring domain (CYP2D6
rather than transporters).

**It is not characterised here from its abstract, and must not be.** §8 is the demonstration of
why: an abstract made Lee 2022 sound like it occupied this ground and the full text showed it did
not. Inferring this paper's object from its title would repeat that error with less evidence.

**So §3.2 carries this as a stated limitation:** *a scoping review performing the same evidential
audit in a neighbouring domain exists and has not been read; §3.2's novelty cannot be asserted
until it is.* No route around the paywall was attempted, per the project's standing rule. Reading
it requires a human with access or an uploaded PDF.

### 9.4 Status of every external source touched today

| source | DOI | how far I read | status |
|---|---|---|---|
| Lee et al. 2022 | `10.3390/pharmaceutics14102078` | **full text** | read; §7 corrected by it (§8) |
| Rollison et al. 2024 | `10.1124/dmd.123.001587` | **abstract** | abstract read at source; full text unavailable |
| Cicali et al. 2020 | `10.1002/cpt.1768` | **title only** | full text unavailable; §3.2 limitation |
| McFeely et al. 2019 | `10.1111/cts.12623` | **title only** | not characterised; PDF available but unread |

Every DOI above was resolved through the connector. **None was written from memory**, and no value
anywhere in this ledger comes from a search snippet.

---

## 10 · Cicali 2020 READ IN FULL — the closest threat does NOT occupy §3.2's ground, and §3.2 is still not novel

The principal uploaded the PDF. **Availability measured, not assumed:** the PDF route returned
`available` for Cicali and still `unavailable` for Rollison, which matches what the principal
said — one uploaded, the other abstract-only.

Read in full: Cicali et al. 2020, *Clin Pharmacol Ther* 108:116–125, `10.1002/cpt.1768`.
This discharges the stated limitation §9.3 placed on §3.2 — **by reading it, not by assuming it.**

### 10.1 What the paper does and does not do

| §3.2's ground | Cicali 2020 |
|---|---|
| a pre-specified **evidential bar** for accepting/rejecting a determination | **No.** It pre-specifies *numerical AUC cutoffs* for classifying inhibition strength (strong ≥5-fold, moderate ≥2–<5, weak ≥1.25–<2, insignificant <1.25) — a **classification rule, not an evidence-quality standard**. Nothing about study quality, certainty or sufficiency. |
| audit of the **evidence behind** published classifications | **Yes** — and it finds real discordance. |
| an **asymmetry** between positive and negative determinations | **No.** It does not investigate whether negatives are missing or rarely published. |
| a **positive-vs-negative grouping** / contrast design, or a claim one cannot be assembled | **No.** Its contrast is *FDA-listed category vs observed AUC-derived category*. |
| **transporters** | **No.** CYP2D6 and metabolic enzymes only. |

Its audit result, **cited** (read at source): concordance of observed with FDA-listed
classification was **55 of 89** inhibitor–substrate pairs (**62%**), and **27 of 48** (**56%**)
restricted to sensitive substrates; it recommends removing one entry from the FDA table and
downgrading two others.

**The paper's own bottom line, as the full text supports:** it makes a **different, narrower
claim** — that FDA-listed moderate/weak CYP2D6 inhibitor classifications do not always match
classifications derived from observed AUC changes. It does **not** claim the literature supplies
positives but no defensible negatives, and does **not** claim a contrast design cannot be
populated.

### 10.2 §3.2 IS STILL NOT NOVEL, and §9.1 is the reason

The temptation here is to write "the closest threat is cleared, so §3.2 looks novel." **That would
break the method statement adopted one section ago**, so it is not written.

> §9.1: a sampled probe can **refute** a novelty claim but can **never establish** one.

Clearing the closest **identified** threat eliminates one candidate witness. It says nothing about
the corpus, because **the candidate set itself came from a 12-result sample** (§7.1). The set of
threats I have checked is exactly the set the probe happened to surface.

So the honest state of §3.2:

- **Unoccupied by every threat so far identified** — Lee 2022 (full text, §8), Cicali 2020 (full
  text, here). Both read, neither makes the claim.
- **Still UNESTABLISHED as novel.** §4 item 1 stands: no novelty claim in §3 is substantiated.
- What changed is **not** the novelty status. What changed is that §9.3's specific stated
  limitation is **discharged**, and §3.2's remaining limitation is now the general one — our
  prior-art evidence is a sample — rather than a named unread paper.

### 10.3 A better use for Cicali 2020 than prior art: precedent for the METHOD

Reading it turned up something more useful than a threat. Cicali 2020 establishes that
**auditing the evidence behind a published classification is an established, publishable move
that finds real defects** — 38% of the audited classifications did not match the observed data.

That is **precedent for the genre, not pre-emption of the claim.** §3.2 can cite it to show the
method is legitimate and consequential, while remaining the thing that paper is not: a statement
about the *availability of negative determinations*, on *transporters*, at a *stated evidential
bar*.

Precedent for a method strengthens a paper; prior art for a claim sinks it. **Cicali 2020 is the
first and not the second** — and that distinction is only visible because the full text was read
rather than inferred from the title, which is what §9.3 forbade and §8 explains.

### 10.4 Read-depth table, updated

| source | DOI | how far I read | status |
|---|---|---|---|
| Lee et al. 2022 | `10.3390/pharmaceutics14102078` | **full text** | read; corrected §7 (§8) |
| **Cicali et al. 2020** | `10.1002/cpt.1768` | **full text** (principal-uploaded PDF) | read; does not occupy §3.2; **method precedent** |
| Rollison et al. 2024 | `10.1124/dmd.123.001587` | **abstract only** | full text still `unavailable` — measured again today |
| McFeely et al. 2019 | `10.1111/cts.12623` | **title only** | not characterised; PDF available, unread |

Rollison stays **abstract-only** and nothing in this ledger upgrades it. Every DOI resolved
through the connector; none written from memory.
