---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-15T19:41
status: created
priority: high
size: task
subject: "PRINCIPAL RE-RULING: invariant = DrugBank RECORD CONTENT (accessions, names, and the row association), not byte-identity; steps 4-5 cancelled; guard test re-scoped; fixtures forward-fixed; ledger keeps accessions, drops structures"
in_reply_to: null
---

# PRINCIPAL RE-RULING: invariant = DrugBank RECORD CONTENT (accessions, names, and the row association), not byte-identity; steps 4-5 cancelled; guard test re-scoped; fixtures forward-fixed; ledger keeps accessions, drops structures

# PRINCIPAL RE-RULING: the invariant is about RECORD CONTENT, not byte-identity. Steps 4-5 are CANCELLED.

#116 was right on every point, and I verified all three myself before taking it to the principal: PubChem's L-aspartic acid and aspirin InChIs are byte-identical to the snapshot's; DB03700's structure matches PubChem's **D-allothreonine** exactly while true D-threonine differs; and `origin/lung-on-chipsim` already carries snapshot-identical structures in **seven** files (both fixtures, the `df8435f` parked patch, `test_parse.py`, `configs/unparseable_compounds.yaml`, `test_unparseable_exclusions.py`, and one of your own dispatch payloads). My #115 criterion was unsatisfiable, and you stopped before executing it. That is exactly the judgement I want from the writer.

## 1 · The invariant, restated (principal, 2026-09-15)

**The project does not redistribute DrugBank RECORD CONTENT.** Record content means the fields DrugBank actually licenses:

- names, synonyms, descriptions, categories, indications, targets/enzymes/transporters/carriers;
- **DB accessions** — these are DrugBank's own identifiers, not public molecule identifiers;
- and critically, **the association** between any of the above and a structure: the row tuple `(accession, name, structure)`.

**A bare canonical structure identifier is NOT record content.** A standard InChI, InChIKey or SMILES is a computed function of the molecule; the same string arises wherever it is computed. Publishing `InChI=1S/C9H8O4/...` says "this is aspirin", not "this is what DrugBank says about aspirin". **But every structure in a tracked file must cite a public source** (PubChem CID + retrieval date), so its provenance is checkable rather than assumed.

## 2 · What this cancels, and what replaces it

- **CANCELLED: step 4 (local history rewrite) and step 5 (the `git log -S` proof).** The bytes were never the problem. No rewrite, no force-push, on any ref. The push freeze stays for a different reason (§5).
- **REPLACED: step 6's guard test.** It must now fail on **record content**, not on structure strings:
  1. any **real DB accession** in a tracked file (extend the existing real-accession scan, which already does most of this) — `DB9xxxx` synthetics remain the sanctioned form;
  2. any **tuple** that associates a structure or a DrugBank name with a real accession — this is the half that does not exist yet and is the point of the test;
  3. it must have a demonstrated falsification: add a real `(accession, name, structure)` row to a tracked file, watch it fail, remove it, report both states.
  Scope it repo-wide. Under this definition the fixture *structures* are fine, so the named-exclusion-with-citation you proposed in #118 §3 is no longer needed for them — see §3.

## 3 · Fixtures: re-source FORWARD, do not touch history (principal ruling)

The fixture TSVs are snapshot-shaped rows — accession + name + structure — so they carry the **association**, which is record content even though the structures themselves are not. They have been on public `origin/main` since 2026-08-31, so:

- **Forward fix only.** Replace the real accessions and names in `tests/fixtures/snapshot/*.tsv` with `DB9xxxx` synthetics and non-DrugBank names, keeping the structures (cited). The fixture keeps testing what it tests.
- **No trunk rewrite, no force-push.** The principal ruled the published history stays: erasure is impossible anyway — forks, clones, caches and the v0.3.0 tag already carry it — and stating the fact plainly beats implying a clean history.
- **Record it**, in the limits text and in `PROVENANCE.md` when the principal writes it: six public structure identifiers per fixture file, plus their DrugBank row association, were published from 2026-08-31 until the forward fix.

## 4 · The exclusion ledger — my ruling, narrowing the above deliberately

`configs/unparseable_compounds.yaml` and `test_unparseable_exclusions.py` pair **eight real accessions with structures**. Under §1 that association is record content. But a study that cannot say which records it excluded cannot report its exclusions.

**Keep the eight accessions; drop the structure strings.** Identification without association: the accession, the exclusion code (`unparseable_inchi`), and if you need a structural fingerprint for reproducibility, a **hash** of the offending string rather than the string. That preserves the falsifiability of the exclusion list and removes the tuple. Reply if that breaks a test you cannot restructure, rather than working around it.

## 5 · Push freeze: still on, for a different reason now

Not licensing — **gating**. §2 is ungated code (no QG receipt) and the branch is 26 commits ahead of a remote that is 0 behind. Nothing goes to origin until the §2 boundary exists and I clear it in writing.

## 6 · Threonine naming — mine to fix, and it was my error

DB03700 is D-allothreonine; I wrote "L-/D-threonine stay distinct" into r2.12's done-conditions from your #99 naming without checking the snapshot's own labels. **I will amend the plan (r2.13) to name L-threonine vs D-allothreonine and to record that DrugBank mislabels DB03700.** You rename the test and its docstring to match; the guard behaviour is correct and unchanged — they are genuinely different stereoisomers. If you want a true L-/D-threonine test as well, source both from PubChem (CID 6288 / 69435, which differ from every snapshot string) and add it as a separate case.

## 7 · Order from here

Steps 3 (PubChem citations for §2 structures + fix `test_parse.py`'s false docstring + extend `sources.yaml`), then the new §2-scoped work: guard test per §2 above, fixture forward-fix per §3, ledger change per §4, test renames per §6. Then re-run the suite and the merge report and confirm 1,599 / 191->156 / 48->7 / 41 / 0 new merges. Then the §2 `/iteration-complete` boundary. Then ask me for push clearance.

The benzimidazole 404 and the malate-species mismatch (#116 §4) stay as you reported them: do not substitute a different species to make a test pass. If a structure has no clean public source, the test cites the snapshot as its source of record and says so — that is a documentation act, not redistribution, now that identifiers are not the issue.
