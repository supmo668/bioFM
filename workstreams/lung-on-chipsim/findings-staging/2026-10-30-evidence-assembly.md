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

Per the CTO's revised ruling (approvals row 79 and its correction): inline what survives, state the
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
