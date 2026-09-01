---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-01T09:51
status: created
priority: high
size: task
subject: "T8 pre-ratification review — panel NOT ratified; 3 plan amendments; T8's deletion clause would have cut ABCB1"
in_reply_to: null
---

# T8 pre-ratification review — panel NOT ratified; 3 plan amendments; T8's deletion clause would have cut ABCB1

Agent: lung-on-chipsim
Re: T8 pre-ratification review complete. Panel NOT ratified — attestation fields remain the principal's.

Ran a structured ratification review with the principal. Three plan amendments fall out of it;
per your standing rule I am reporting them, not touching build-plan.md. Commit 567bf6f.

## STATE — T8 is NOT done

configs/barrier_panel.yaml still carries ratified: false, ratified_by: "", ratified_on: "".
I did not write them and will not. All seven entries stay; TFRC's face is corrected; rationale
is recorded in-file so the eventual attestation is auditable rather than remembered.

T19 verified live against the current file: 15 passed / 1 skipped. All seven accessions resolve,
taxon 9606, primary gene names match. Offline suite unchanged at 284 passed / 6 skipped.

## THE FINDING THAT MATTERS — T8's deletion clause is a trap

T8 says "delete any not expressed in airway epithelium". Read literally against live UniProt
tissue-specificity comments, FIVE OF SEVEN entries have no lung mention — INCLUDING ABCB1.

Following that instruction as written would have deleted the P-gp keystone. T10 would then have
raised (defect 4 working as designed), but the other four deletions would have silently shrunk
the panel, and a smaller panel EMPTIES joins rather than erroring — the exact "failure that looks
like success" the config header warns about.

The root cause is epistemic, and the architecture has already ruled on it once: UniProt's tissue
comment is a curated sample, not an expression atlas, so absence there is a curation gap. This is
the SAME error the three-way P-gp label exists to prevent, one layer up, against a source with the
same incompleteness — and no test catches it, because T19 checks accession/taxon/gene only.

Principal's ruling: delete ONLY on positive evidence of absence from airway epithelium. Silence in
UniProt is not evidence. Recorded in-file.

## AMENDMENT 1 — T8's done-condition must cover `face`

T8's text says check accessions, delete non-expressed, set ratified: true. It never mentions face.
But flipping the flag blesses the whole file, including seven polarity assignments that NO test
verifies and that UniProt corroborates for only four. Ratification is currently silently broader
than the task text.

Principal ruled that ratification explicitly covers face. Please amend T8 to say so.

## AMENDMENT 2 — record that T7's draft exceeds the A&D inventory

Three documents, three panel sizes:
  PVR L147 (minimum viable chip): TWO carrier terms (P-gp efflux + one uptake carrier)
  A&D L91 (binding-site inventory): FIVE — P-gp, BCRP, TfR1, FcRn, PepT1
  barrier_panel.yaml (T7 draft):    SEVEN — those five PLUS ABCC1/MRP1 and SLCO2B1/OATP2B1

ABCC1 and SLCO2B1 are agent additions the A&D never names. Not a defect in my view — drafting is
allowed and both are defensible — but the divergence should be recorded rather than absorbed.

This resolves rather than conflicts, via AM-3: the panel holds IDENTITY, theta_priors holds
QUANTITY. In slice 1 the panel is consumed only for the T9 edge join and T10's ABCB1 resolution —
neither is a modelled carrier term. So PVR's "two carriers" is a theta constraint at M1 under the
5-8 identifiable-parameter budget, not a panel constraint now. Seven join targets cost no
parameters; seven fitted abundances would blow the budget.

Ratification therefore attests to identity and face ONLY, explicitly not to seven carrier terms.
Worth stating in the plan so nobody later reads a ratified 7-entry panel as endorsing 7 mechanisms.

Note ABCC1 is the best-evidenced entry in the set — UniProt lists Lung explicitly, which ABCB1's
comment does not. SLCO2B1 is the weakest: no lung mention, and UniProt gives basal, basolateral
AND apical.

## AMENDMENT 3 (proposal, needs your call) — an `airway_evidence:` field

Under the new deletion criterion, "kept" now means "no positive evidence of absence", which is a
weaker claim than "positive evidence of presence". Those two states are currently indistinguishable
in the file. An optional per-entry airway_evidence: <DOI|PMID> would separate them and make the
panel's justification durable. Schema change, so your call, not mine.

## SUBSTANTIVE CORRECTION — TFRC face apical -> basolateral

The one changed value. I flagged apical as likely wrong; the principal supplied measured
basolateral:apical localization ratios, basolateral-dominant in every system:
  MDCK strain I ~800:1, MDCK strain II ~300:1 (Fuller & Simons, 1986)
  Caco-2 ~40:1 at day 8 post-confluence (shifting from ~1:1 during differentiation)
  HepG2 ~3:1 (~70% basolateral); BeWo ~2:1

Direction unanimous. Two caveats recorded in-file rather than discarded: NONE of these systems is
airway epithelium, so this is extrapolation across polarized epithelia with airway magnitude
unmeasured; and the ratio spans ~400x, so at the low end this is a preference, not exclusive
localization. No DOI was supplied beyond the Fuller & Simons 1986 attribution and I did not
manufacture one.

Related, and NOT fixed: the {apical, basolateral} binary cannot represent a two-faced transporter,
and two of seven are two-faced (FCGRT transcytoses bidirectionally; SLCO2B1 is all three per
UniProt). Recorded as a PoC modelling choice; I recommend M1 widens the schema when directional
transport actually consumes the field, rather than changing a tested schema for a consumer that
does not exist.

## WHAT I AM DOING NEXT

Running /pr-prep now — authorized in your dispatch #14 follow-up, and required because your
coordination commit b9e1a75 landing into my branch invalidated the receipt.

HOLDING /pr-submit per your override, pending the principal's clearance on the push.
Not starting slice 2. Not starting T9/T10 — they need a genuinely ratified panel, and it is not.

## STILL WITH THE PRINCIPAL

- The three attestation fields (ratified/ratified_by/ratified_on) — T8 is not done until they write them.
- The other four human artifacts: T2, T1, T18, T14. T2 remains the keystone.
- AM-6. I put your exit-3 recommendation (pre-register a sample-size contingency, evaluated on the
  sealed allocation as written down before reading) to them. Undecided.
