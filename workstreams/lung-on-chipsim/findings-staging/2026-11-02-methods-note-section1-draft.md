---
type: findings-staging
status: DRAFTED — UNRATIFIED. This is paper text for the principal to ratify as author of record.
authorization: principal ruling 2026-11-01 (approvals row 89, §1 RATIFIED) and 2026-11-02
  (approvals row 94, superseding-revision path), relayed via CTO #847 and #854
applies: ledger §6.1 subject-naming, ADOPTED at approvals row 91
target: workstreams/lung-on-chipsim/paper/stage1-methods-note.md — by SUPERSEDING REVISION, never
  by an edit. Nothing under paper/ or qgr/ has been touched.
agent: biofm/matthew-mo/lung-on-chipsim
---

# Draft paper text for ledger §1 — DRAFTED, 2026-11-02

**What this is.** The text that carries ledger §1 into the paper, drafted under approvals row 89
(which ratified §1 as stated) and row 94 (which made the superseding-revision path the sanctioned
one). **It is a draft for the principal to ratify as author of record.** Nothing under `paper/` or
`qgr/` has been edited: CLAUDE.md line 95 binds the directory, and row 94 confirms there is no
authorization that lets the note be revised directly.

**Subject-naming (row 91 / §6.1) is applied in the drafting, not retrofitted.** Every count below
names its subject in the same sentence. One point is verified rather than assumed: for this roster
the row count and the distinct-identity count **coincide** — 26 rows and 26 distinct canonical
identities in both the roster and the adjudication file, with no duplicate key in either
(`derived`, measured 2026-11-02 and pinned by `tests/test_published_pgp_result.py`). Where they
coincide the draft says so; it does not silently write "26 compounds" and leave a reader to assume
it.

---

## The draft text

> ### The pre-registered grouping variable could not be populated
>
> The pre-registered analysis grouped the compound panel by P-glycoprotein substrate status. The
> panel comprises **26 rows, which are 26 distinct canonical structure identities** — for this
> panel the two counts coincide, and no identity appears twice. Each was adjudicated against the
> published literature at a bar fixed before any verdict was recorded.
>
> The adjudication returned **three positive assignments, no negative assignments, and
> twenty-three returning the verdict "unknown"** — counts over the same 26 distinct identities.
> Because the grouping variable requires both a populated positive and a populated negative group,
> it could not be constructed.
>
> **The absence of a negative group is a finding, not a shortfall in search effort.** All 26
> identities were searched, the search record is published with the study, and "unknown" here is a
> verdict reached *after* searching rather than a record of not having searched. The two are
> different results and the distinction is preserved throughout the adjudication record.
>
> **No relaxation of the positive bar populates the negative group.** The criterion was amended
> once during adjudication, so that a single well-cited source may carry a verdict and conflicts
> resolve to the better-cited source. Applying the amended criterion moved the positive count from
> two to three and left the negative count at zero. The reason is structural rather than
> procedural: the only sub-threshold compounds in the governing source are not members of this
> panel, and that source's conclusion about the compound class is comparative rather than a
> per-compound negative determination.
>
> **Two features distinguish this from a null result discovered after the fact.** First, the
> arithmetic consequence — an unusable grouping variable, and the downstream gate raising on an
> empty group — was recorded before any verdict was entered, so the null was stated in advance of
> the data rather than found in it. Second, the axis's biological aptness was independently
> challenged during the study and the challenge was carried as a cited limitation rather than used
> to discard the axis: four sources concur that P-glycoprotein is largely absent from human airway
> epithelium, and in the one model where it is functionally present it is localised to the opposite
> membrane. The pre-registered axis was retained.
>
> **The scope of the claim.** This is a claim about the published literature, not about lung
> biology. What is established is that a fixed evidential bar applied to this panel yields no
> negative group. What is **not** established is that any panel member is not a P-glycoprotein
> substrate: the absence of a published finding is not evidence of non-substrate status. The
> coverage claim this study makes is therefore about the method, not about pulmonary
> P-glycoprotein biology.

---

## Provenance of every number in the draft

| number | subject named | marker | source |
|---|---|---|---|
| 26 | rows, and distinct canonical identities (they coincide) | **derived** | `load_poc_roster` + the tracked adjudication file, measured 2026-11-02; pinned by `test_published_pgp_result.py` |
| 3 positive | over the same 26 distinct identities | **derived** | `chipsim.eval.provenance_block.label_counts`, the project's own deriver |
| 0 negative | same | **derived** | same call |
| 23 unknown | same | **derived** | same call |
| 2 → 3 under the amendment | positive assignments | **cited** | approvals row 54, the principal's words |
| four concurring sources | — | **cited** | `10.1016/j.ejps.2025.107333`, `10.1183/13993003/erj.38.suppl_55.p843`, `10.1016/j.ejpb.2013.06.010`, `10.1211/jpp.61.03.0003`; and `10.1038/sj.bjp.0704390` for the basolateral mislocalisation |

**No biological number here originates with me.** The counts are derived from the principal's own
ratified verdicts by the project's own code; the amendment and the four sources are cited to
approvals rows and DOIs the principal already accepted.

## What this draft deliberately does NOT do

1. **It does not name the transporter's gene symbol or any compound.** The result is a statement
   about the panel and the literature, and naming members adds nothing the claim needs.
2. **It does not state the three positive compounds' identities or their DOIs.** Those are in the
   tracked adjudication file and the published search record; the paper text does not need them and
   including them would widen a public surface for no gain.
3. **It does not mention the snapshot's 6,802 rows / 6,610 distinct identities.** Row 91's rule
   governs those counts too, but they are not part of §1's claim and the draft does not import
   them. If a later section needs them, it must name their subject — and for the snapshot, unlike
   this panel, the two counts **diverge by 192**.
4. **It does not claim the axis was apt.** §1.3's second reason is carried as a limitation, which
   is what the record says it is.
5. **It is not placed.** Which section of the methods note this supersedes, and the revision
   mechanics, are the principal's and the CTO's to decide. I have drafted text, not a patch.
