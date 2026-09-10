# T8 review record — barrier panel

Evidence and rulings gathered ahead of T8 ratification. **This file is not a ratification.**
`configs/barrier_panel.yaml` still carries `ratified: false`, and only the principal may change
that.

This record lives here, not in `configs/barrier_panel.yaml`, because that file is defined by
**AM-3** as carrying *identity only* — "Not numbers" — and by the build plan's Global Constraint
"No coding agent writes a biological number." The localization ratios below are biological
quantities. Putting them in a comment inside the config would have dodged the numeric-leaf
validator but not the rule. Flagged in the P0.3 quality gate as finding D1.

Durable references for everything here: dispatch **#15** (review outcome), **#16** (CTO rulings),
**#17** (N1 conformance escalation).

---

## Mechanical verification — T19, live

All seven accessions were verified against `rest.uniprot.org` during the review: every one
resolves, `organism.taxonId == 9606`, and the primary gene name matches the entry's `symbol`.
`pytest -m network` → 15 passed / 1 skipped.

**T19 does not check membrane polarity or airway-epithelium expression.** Those are the two
dimensions ratification rests on that no test covers.

| Symbol | Accession | UniProt subcellular | Lung/airway in tissue annotation |
|---|---|---|---|
| ABCB1 | P08183 | Apical cell membrane | not mentioned |
| ABCG2 | Q9UNQ0 | Apical cell membrane | not mentioned |
| ABCC1 | P33527 | Basolateral cell membrane | **Lung** — explicit |
| TFRC | P02786 | *(no polarity given)* | no tissue annotation at all |
| FCGRT | P55899 | *(no polarity given)* | **lung** — explicit |
| SLC15A1 | P46059 | Apical cell membrane | small intestine only |
| SLCO2B1 | O94956 | Basal, basolateral **and** apical | not mentioned |

---

## Ruling 1 — the deletion criterion

T8 as written says "delete any not expressed in airway epithelium". Read literally against the
table above, **five of seven entries have no lung mention, including ABCB1** — the P-gp keystone
that `pgp_label.py` resolves by symbol.

**Principal's ruling: delete only on positive evidence of *absence*. Silence in UniProt is not
evidence.** UniProt's tissue-specificity comment is a curated sample of published findings, not an
expression atlas.

This is the same error the three-way P-gp label exists to prevent, one layer up. It is now
codified as a standing rule in `CONTEXT.md` at the CTO's instruction (dispatch #16), because it had
recurred three times against three sources.

Consequence: all seven entries are kept. `SLC15A1` is the one worth revisiting — airway PepT1 is
contested in the literature rather than merely uncurated — but *contested* is not positive evidence
of absence.

---

## Ruling 2 — TFRC polarity: `apical` → `basolateral`

**Status: AUTHORIZED.** Originally written into the config *ahead* of the plan — T7's interface
block prescribed `face: apical`, and T8 authorizes accession correction and deletion, never a
`face` change. That sequencing error was escalated as **N1** (dispatch #17) and ruled option (a) in
**#18**: `build-plan.md` T7 now prescribes `basolateral`, carrying both caveats below, re-signed at
`b5443bd`. Recorded here because the divergence existed and should stay auditable.

The reversal was ruled by the principal on measured localization data. Reported
basolateral:apical ratios, basolateral-dominant in every system measured:

| Cell system | basolateral : apical | Context |
|---|---|---|
| MDCK strain I (tight, >2,000 Ω·cm²) | ~800 : 1 | Fuller & Simons, 1986 |
| MDCK strain II (leaky, <350 Ω·cm²) | ~300 : 1 | Fuller & Simons, 1986 |
| Caco-2, day 8 post-confluence | ~40 : 1 | shifted from ~1:1 during differentiation |
| HepG2 | ~3 : 1 | ~70% of total TfR basolateral |
| BeWo (placental trophoblast) | ~2 : 1 | — |

**Two caveats, recorded rather than discarded:**

1. **None of these systems is airway epithelium.** MDCK is kidney, Caco-2 intestinal, HepG2
   hepatic, BeWo placental. The call is extrapolation across polarized epithelia. Direction is
   unanimous; airway magnitude is unmeasured.
2. **The ratio spans ~400×.** At the low end (HepG2 ~3:1, BeWo ~2:1) basolateral is a *preference*,
   not an exclusive localization. The `{apical, basolateral}` binary records direction and loses
   strength.

No DOI was supplied beyond the Fuller & Simons 1986 attribution, and none was manufactured.

---

## Ruling 3 — what ratification attests to

**Identity and face only.** It does **not** endorse seven modelled carrier terms.

Three documents give three panel sizes, and they reconcile rather than conflict:

| Source | Count |
|---|---|
| PVR — minimum viable chip | **2** carrier terms (P-gp efflux + one uptake carrier) |
| A&D §2B — binding-site inventory | **5** (P-gp, BCRP, TfR1, FcRn, PepT1) |
| `build-plan.md` T7 interface block | **7** (adds ABCC1/MRP1, SLCO2B1/OATP2B1) |

Under **AM-3** the panel holds *identity*, `theta_priors.yaml` holds *quantity*. In slice 1 the
panel is consumed only for the T9 edge join and T10's ABCB1 resolution — neither is a modelled
carrier term. So the PoC's two carriers are a **θ constraint at M1**, under the 5–8
identifiable-parameter budget, not a panel constraint now. Seven join targets cost zero parameters;
seven fitted abundances would blow the budget.

**ABCC1 and SLCO2B1 are prescribed verbatim by `build-plan.md:436,440`** — T7's interface block, in
the G4-signed plan. They are additions relative to the **A&D**, not agent drift. Dispatch #15
mis-stated this as draft-vs-plan; corrected in #17.

Note the evidence ranking runs opposite to the A&D's list: **ABCC1 is the best-evidenced entry**
(UniProt names Lung explicitly, which ABCB1's comment does not), while **SLCO2B1 is the weakest**
(no lung mention, and all three polarities listed).

Ratification scope covering `face` was approved by the CTO in dispatch #16 but **has not landed in
`build-plan.md` T8**, which still contains no occurrence of `face`. Tracked as D2.

---

## Open, not resolved here

- **The three attestation fields.** `ratified`, `ratified_by`, `ratified_on` are the human
  artifact. No agent may write them.
- **N1** — the `face` divergence from the signed plan (dispatch #17).
- **`airway_evidence:`** — approved by the CTO as optional, human-only, absent-means-the-weak-claim
  ("no positive evidence of absence", never silently upgraded to "present"). Not yet in the schema.
- **Post-ratification drift.** Once `ratified: true` is set, nothing detects an edit to any entry
  field; T19 catches only accession and gene-symbol mismatch. A `ratified_panel_sha256` was
  proposed to the CTO (a digest, not a biological number).

---

## Addendum — CTO review, 2026-09-09 (principal's PoC-stringency ruling)

### Independent re-verification, live API

Every accession re-queried against `rest.uniprot.org` today, independently of T19:
**7/7 resolve, gene symbol matches, `Homo sapiens`, Swiss-Prot reviewed.** The subcellular
table above was re-derived from the live API without reading it first, and **matched in every
row**. Two independent derivations now agree; this record is accurate as of today.

### New: `face` is a PASSENGER COLUMN in slice 1 — verified in code

Ruling 3 says the panel is consumed "only for the T9 edge join and T10's ABCB1 resolution."
That is confirmed at code level, and it is sharper than the prose implies:

- `pgp_label.py:306` — the join carries `face` into the output frame:
  `panel.loc[:, ["uniprot_id", "symbol", "face"]]`
- `pgp_label.py:247` — `face` is *validated* against `FACES`, a schema check on the value's
  membership, not a use of the value
- the join keys on `uniprot_id`; `resolve_panel_accession` resolves by `symbol`

**Nothing in slice 1 branches on `face`.** It is present in slice-1 output and affects no
slice-1 decision. It becomes load-bearing at M1, when directional transport first consumes it.

This is why the principal's ruling below is not a weakening of evidence standards: the part
slice 1 consumes — identity — is the part that is 7/7 verified.

### Principal's ruling, 2026-09-09: ratify at PoC stringency

> *"PoC panel need not be stringent, we'd like to derive results of using the methodology on
> known existing results."*

**Ratify all seven. Delete nothing. Record the three unconfirmed faces as provisional.**

The three fail in **different** ways and must not be collapsed into one note:

| Symbol | Face | Why it is provisional |
|---|---|---|
| TFRC | basolateral | **No UniProt polarity annotation at all.** Rests entirely on Ruling 2's measured ratios — all from **non-airway** systems, spanning ~400×. Silence, not contradiction. |
| FCGRT | apical | **No polarity annotation.** Additionally known to transcytose **bidirectionally**, so the binary loses information the entry actually has. |
| SLCO2B1 | basolateral | **Not silence — a CHOICE.** UniProt annotates basal, basolateral *and* apical. One of three annotated options was selected; the other two are not thereby excluded. |

**Re-check all three at M1**, where `face` first affects a result. Until then the file records a
direction, not an established localization.

### Correction to this review

The CTO initially reported Ruling 2's `apical → basolateral` correction as applying to **ABCC1**
and as "independently confirmed by UniProt." Both halves were wrong: Ruling 2 concerns **TFRC**,
and UniProt gives TFRC **no polarity annotation**, so it is not independently confirmed by that
source. ABCC1's basolateral face *is* UniProt-confirmed — it was simply never the corrected entry.
Recorded because a review that misattributes a ruling is the failure this record exists to prevent.

### Two open items above have LANDED and are no longer open

- **D2** — "*ratification scope covering `face` … has not landed in `build-plan.md` T8, which
  still contains no occurrence of `face`*". It has landed: T8 now contains **6** occurrences of
  `face`, including "check each `face`" and the attestation scope. **D2 is closed.**
- **`ratified_panel_sha256`** — recorded above as "proposed to the CTO". It landed (dispatch #18)
  and the key is present in the live panel. **Closed.**

Both were true when written on 2026-09-03 and stale by 2026-09-09. Flagged because this record is
the *input* to a task about to be performed, and a stale open item reads as outstanding work.

### One thing this record should no longer say

`ratified_panel_sha256` is **tamper-evidence, never attestation**. A survivor of that reframe was
found today in `build-plan.md` T8 itself — it read "running the seal is the human's act of
attestation", contradicting the Global Constraints block 480 lines above. Corrected in r2.8. If any
line here implies the digest establishes *who* sealed, it is wrong for the same reason.
