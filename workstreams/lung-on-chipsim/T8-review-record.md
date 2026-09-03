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
