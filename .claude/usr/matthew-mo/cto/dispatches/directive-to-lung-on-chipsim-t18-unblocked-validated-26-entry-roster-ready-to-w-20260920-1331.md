---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-20T20:31
status: created
priority: high
size: task
subject: "T18 unblocked — validated 26-entry roster ready to write, re-run relative-stereo + record-content-gate yourself"
in_reply_to: null
---

# T18 unblocked — validated 26-entry roster ready to write, re-run relative-stereo + record-content-gate yourself

# T18 unblocked — the candidate-list hand-off I owed you, now a validated roster

## What happened, in order

1. I found the hand-off precondition had never been discharged: the plan requires a CTO-handed
   guarded candidate list before T18's milestone clock starts, and no such list had ever been
   generated. Fixed: 39-candidate mechanical pool + full PubMed evidence ledger, committed at
   `4a0ed7f` (`workstreams/lung-on-chipsim/qa/_adhoc/lung-on-chipsim-t18-candidate-list.md`),
   surfaced at https://claude.ai/artifact/G6xdAqUj5FeuzT32PJVoM4
2. The principal reviewed the ledger and ruled the roster **finalized at all 26 candidates
   carrying a resolvable DOI**, and ruled — explicitly, via AskUserQuestion, given the
   PROVENANCE.md precedent on agent authorship — that the CTO writes the tracked file, on the
   stated grounds: principal-directed transcription of a decision already made, identity+citation
   only, no biological numbers, no curation judgment by the agent.
3. I built `configs/poc_compounds.yaml` in S11a's exact schema (`compounds:` wrapping
   `{canonical_inchikey, name, evidence_doi}` flow-maps) and ran it through the **real**
   `chipsim.harmonize.roster.load_poc_roster` — not my own reading of it.

## What I verified before sending this

- **26 entries**, recounted independently from the committed ledger (26 `class="doi"` rows),
  matching the principal's stated count.
- **Schema + snapshot check: PASSED** against the actual `load_poc_roster(path,
  snapshot_keys=...)`, run from your worktree's own `chipsim` package against the real
  6,610-key snapshot. All 26 `canonical_inchikey` values resolve; no duplicates; no empty
  fields.
- **Relative-stereo check: I could NOT run it.** `load_poc_roster`'s `relative_stereo_keys`
  parameter needs `chipsim.harmonize.ids`, which imports `rdkit`, absent from my minimal venv.
  **What I did instead**, as a substantive substitute, not a skip: read `stereo_is_relative`
  directly off the parquet for all 26 roster keys against the 42 keys the snapshot itself flags
  as relative-stereo. **Zero overlap.** This is the same fact the real check would assert, read
  a different way — but it is not a run of your production code path, and I want that
  distinction on the record rather than smoothed over.
  **Please re-run the real validator with `relative_stereo_keys` populated (full deps, your
  environment) before treating T18 as gate-clear.** If it disagrees with my parquet-level check,
  that disagreement is itself a finding and should stop the boundary.
- **Full InChIKeys resolved from the parquet directly**, not carried over from my own earlier
  summary (which only had skeleton blocks) — cross-checked against the skeleton blocks on the
  committed evidence ledger and they match exactly.
- **I did not run `record-content-gate` against this new file.** It carries public InChIKeys and
  DOIs only, no DrugBank accession identifiers, so it should scan clean — but "should" is not
  "did", and this file has never been through the gate. Run it as part of your own boundary.

## What I did NOT do

I did not select the 26 — the principal did, from the evidence ledger I assembled. I am
transcribing a decision, at explicit principal direction, on the narrower grounds stated above;
this is not a change to T18's standing ownership rule and should not be read as one.

## The file

```yaml
# ============================================================================
# PoC compound roster — T18 (build-plan human-owned task).
#
# Which 20-40 compounds are "lung-relevant with published exposure" is a
# CLAIM, so this file is hand-curated by the principal. It is validated,
# never generated, by chipsim.harmonize.roster.load_poc_roster (S11a) --
# that module parses and checks this file; it does not write it.
#
# Selection: every candidate carrying a resolvable exposure/deposition/
# pharmacology citation, out of the mechanically-derived ATC R03 candidate
# pool (39 candidates; evidence assembled via PubMed at the principal's
# direction, /grill-with-res). Candidate list and full evidence ledger:
#   workstreams/lung-on-chipsim/qa/_adhoc/lung-on-chipsim-t18-candidate-list.md
#   https://claude.ai/artifact/G6xdAqUj5FeuzT32PJVoM4
#
# Identity and citation only -- no biological numbers.
# ============================================================================

compounds:
  - {canonical_inchikey: ASMXXROZKSBQIH-VITNCHFBSA-N, name: "Aclidinium", evidence_doi: "10.1007/164_2016_68"}
  - {canonical_inchikey: SGRYPYWGNKJSDL-UHFFFAOYSA-N, name: "Amlexanox", evidence_doi: "10.1002/bmc.5288"}
  - {canonical_inchikey: IBIIDGIPJPTFBZ-XYWKZLDCSA-N, name: "Beclomethasone", evidence_doi: "10.1089/jamp.2021.0046"}
  - {canonical_inchikey: FZGVEKPRDOIXJY-UHFFFAOYSA-N, name: "Bitolterol", evidence_doi: "10.1002/j.1875-9114.1985.tb03410.x"}
  - {canonical_inchikey: UNISKOOZAQCSPC-KWVAZRHASA-N, name: "Budesonide", evidence_doi: "10.1186/s12931-015-0318-z"}
  - {canonical_inchikey: STJMRWALKKWQGH-UHFFFAOYSA-N, name: "Clenbuterol", evidence_doi: "10.1016/bs.podrm.2017.02.002"}
  - {canonical_inchikey: KSCFJBIXMNOVSH-UHFFFAOYSA-N, name: "Dyphylline", evidence_doi: "10.1016/0091-6749(75)90128-1"}
  - {canonical_inchikey: UCTWMZQNUQWSLP-VIFPVBQESA-N, name: "Epinephrine", evidence_doi: "10.1007/s11095-026-04048-w"}
  - {canonical_inchikey: XSFJVAJPIHIPKU-XWCQMRHXSA-N, name: "Flunisolide", evidence_doi: "10.2500/aap.2015.36.3835"}
  - {canonical_inchikey: WMWTYOKRWGGJOA-CENSZEJFSA-N, name: "Fluticasone Propionate", evidence_doi: "10.1111/bph.15621"}
  - {canonical_inchikey: BPZSYCZIITTYBL-UHFFFAOYSA-N, name: "Formoterol", evidence_doi: "10.1089/jamp.2021.0046"}
  - {canonical_inchikey: ZJVFLBOZORBYFE-UHFFFAOYSA-N, name: "Ibudilast", evidence_doi: "10.1517/14656560903426189"}
  - {canonical_inchikey: QZZUEBNBZAPZLX-QFIPXVFZSA-N, name: "Indacaterol", evidence_doi: "10.1056/NEJMoa1516385"}
  - {canonical_inchikey: OEXHQOGQTVQTAT-JRNQLAHRSA-N, name: "Ipratropium bromide", evidence_doi: "10.1007/164_2016_68"}
  - {canonical_inchikey: HUYWAWARQUIQLE-UHFFFAOYSA-N, name: "Isoetarine", evidence_doi: "10.1007/BF02991319"}
  - {canonical_inchikey: UCHDWCPVSPXUMX-TZIWLTJVSA-N, name: "Montelukast", evidence_doi: "10.1002/(sici)1099-081x(199712)18:9<769::aid-bdd60>3.0.co;2-k"}
  - {canonical_inchikey: RQTOOFIXOKYGAN-UHFFFAOYSA-N, name: "Nedocromil", evidence_doi: "10.1177/106002809302700515"}
  - {canonical_inchikey: VQDBNKDJNJQRDG-UHFFFAOYSA-N, name: "Pirbuterol", evidence_doi: "10.2165/00003495-198530010-00002"}
  - {canonical_inchikey: FKNXQNWAXFXVNW-BLLLJJGKSA-N, name: "Procaterol", evidence_doi: "10.3390/ijms19071999"}
  - {canonical_inchikey: MNDBXUUTURYVHR-UHFFFAOYSA-N, name: "Roflumilast", evidence_doi: "10.1016/bs.apha.2023.05.001"}
  - {canonical_inchikey: NDAUXUAQIAJITI-UHFFFAOYSA-N, name: "Salbutamol", evidence_doi: "10.1111/bph.15621"}
  - {canonical_inchikey: GIIZNNXWQWCKIB-UHFFFAOYSA-N, name: "Salmeterol", evidence_doi: "10.1111/bph.15621"}
  - {canonical_inchikey: XWTYSIMOBUGWOL-UHFFFAOYSA-N, name: "Terbutaline", evidence_doi: "10.1056/NEJMoa1715274"}
  - {canonical_inchikey: ZFXYFBGIUFBOJW-UHFFFAOYSA-N, name: "Theophylline", evidence_doi: "10.1016/bs.apha.2023.05.001"}
  - {canonical_inchikey: LERNTVKEWCAPOY-KYQOMENCSA-N, name: "Tiotropium", evidence_doi: "10.2165/00003495-200262080-00008"}
  - {canonical_inchikey: GFNANZIMVAIWHM-OBYCQNJPSA-N, name: "Triamcinolone", evidence_doi: "10.1089/08942680152484090"}
```

## Next

1. Write this to `projects/lung-on-chipsim/configs/poc_compounds.yaml` on your branch.
2. Re-run `load_poc_roster` yourself with full deps (`relative_stereo_keys` populated) and
   `record-content-gate` (STAGED) before your boundary. Report if either disagrees with what I
   found.
3. This is the T18 artifact — T13 (`adjudication-worksheet`) is unblocked. Proceed at your own
   pace; nothing else is outstanding from me.
