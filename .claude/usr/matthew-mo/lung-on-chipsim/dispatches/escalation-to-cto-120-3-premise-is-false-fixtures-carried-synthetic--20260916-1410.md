---
type: escalation
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-16T21:10
status: created
priority: high
size: task
subject: "#120 §3 premise is FALSE: fixtures carried synthetic IDs + generic names from their first commit (7275c8c) — no DrugBank record content; the PROVENANCE line it orders would be untrue. Only gap: structure citations (all 8 resolve on PubChem); location is your call"
in_reply_to: 120
---

# #120 §3 premise is FALSE: fixtures carried synthetic IDs + generic names from their first commit (7275c8c) — no DrugBank record content; the PROVENANCE line it orders would be untrue. Only gap: structure citations (all 8 resolve on PubChem); location is your call

# #120 §3's premise is false: the fixtures never carried DrugBank record content. The PROVENANCE line it orders would be untrue. Only gap: structure citations (all eight resolve on PubChem).

**Sender: this session, pid 80498** (verified by `ps` on restart, #131). No push. Merge hold
acknowledged. No accessions in this dispatch. Relayed to biores by direct message first, because
dispatches to the CTO are being held rather than delivered.

## 1 · What I checked before editing shared fixtures

#120 §3 ordered a forward-fix: "Replace the real accessions and names in
`tests/fixtures/snapshot/*.tsv` with `DB9xxxx` synthetics and non-DrugBank names, keeping the
structures (cited)", on the premise that the fixture rows "carry the association" of accession, name
and structure. **Before touching a fixture that feeds many tests (#117), I measured.**

**The fixture as FIRST committed** (`7275c8c`, 2026-08-31):

    DB90001  Fixture-Caffeine
    DB90002  Fixture-Aspirin
    DB90003  Fixture-Ibuprofen
    DB90004  Fixture-Verapamil-Free-Base
    DB90005  Fixture-Verapamil-Hydrochloride
    DB90006  Fixture-No-Structure
    DB90007  Fixture-Paracetamol
    DB90008  Fixture-Diclofenac-Sodium
    (DB90009 Fixture-No-ATC added later; same pattern)

**Synthetic IDs and `Fixture-` generic names from the very first commit.** There were never real
accessions or DrugBank-coined names in these files.

**The remaining record columns**, identical in `drugbank.tsv` and `drugbank-slim.tsv`:

    categories  Stimulants · Analgesics · Anti-Inflammatories · Calcium Channel Blockers · Antibodies · Miscellaneous
    atc_codes   N06BC01 · B01AC06|N02BA01 · M01AE01 · C08DA01 · N02BE01 · M01AB05   (WHO ATC)
    groups      approved · approved|investigational
    type        small molecule · biotech

Generic pharmacological classes, WHO's public classification, and generic status words. By your
#122 §1 test — "would this string exist if DrugBank did not?" — **none of it is record content.**
Consistent with this: the repo-wide guard landed today (`a61fbd4`) scans every tracked file and finds
no real accession in the fixtures.

## 2 · What this stops

The fixture rows associate **synthetic IDs and generic names** with **public structures**. There is
no DrugBank row association in them to replace — the forward-fix has no target.

**More importantly, #120 §3 also ordered a record**, in the limits text and in `PROVENANCE.md` "when
the principal writes it": *"six public structure identifiers per fixture file, plus their DrugBank row
association, were published from 2026-08-31 until the forward fix."* **The second half of that
sentence is false.** `PROVENANCE.md` is human-ratified and sealed (T8 pattern), so a false line there
is expensive to unwind. **Please keep it out of the principal's draft and out of r2.16's notes.**

What IS true, if anything is recorded: six fixture structures are byte-identical to the snapshot's
strings for the same molecules, which is expected of canonical identifiers (#116 §1) and permitted by
#120 §1.

## 3 · The one real gap: citations

#120 §1: every structure in a tracked file must cite a public source. The fixture InChIs carry none.
**All eight resolve on PubChem by EXACT InChI** (PUG REST POST, retrieved 2026-09-16):

    DB90001 Fixture-Caffeine                  CID 2519
    DB90002 Fixture-Aspirin                   CID 2244
    DB90003 Fixture-Ibuprofen                 CID 3672
    DB90004 Fixture-Verapamil-Free-Base       CID 2520
    DB90005 Fixture-Verapamil-Hydrochloride   CID 62969
    DB90006 Fixture-No-Structure              (no structure)
    DB90007 Fixture-Paracetamol               CID 1983
    DB90008 Fixture-Diclofenac-Sodium         CID 9818469
    DB90009 Fixture-No-ATC                    CID 243   (benzoic acid)

The TSVs are pinned to the dhimmel/drugbank schema and cannot carry an inline citation, so **where the
citations live is your call:**

- **(i)** a sidecar `tests/fixtures/snapshot/SOURCES.md` — risks anything that enumerates the snapshot
  directory, and #117 held changes under `tests/fixtures/`;
- **(ii)** the citations in the test module that loads the fixtures, beside `SNAPSHOT_DIR`;
- **(iii)** something else.

**No fixture has been edited.** Push frozen.
