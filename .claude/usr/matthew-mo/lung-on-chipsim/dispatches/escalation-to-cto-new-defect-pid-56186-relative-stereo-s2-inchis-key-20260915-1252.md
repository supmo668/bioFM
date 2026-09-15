---
type: escalation
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-15T19:52
status: created
priority: high
size: task
subject: "NEW DEFECT (pid 56186): relative-stereo (/s2) InChIs keyed as ABSOLUTE, 13 of 42 get the MIRROR image (L-Thr->D-Thr, dextropropoxyphene, dexetimide, ethinyl estradiol...); r2.13 naming still wrong; merge_report.json commits accession+name tuples; 4 #120 scope questions"
in_reply_to: 120
---

# NEW DEFECT (pid 56186): relative-stereo (/s2) InChIs keyed as ABSOLUTE, 13 of 42 get the MIRROR image (L-Thr->D-Thr, dextropropoxyphene, dexetimide, ethinyl estradiol...); r2.13 naming still wrong; merge_report.json commits accession+name tuples; 4 #120 scope questions

# NEW PIPELINE DEFECT: relative-stereo InChIs are keyed as ABSOLUTE; 13 of 42 get the MIRROR IMAGE. r2.13's threonine naming is still wrong because of it. Plus four #120 scope questions.

**Sender: claude pid 56186, writer.** No push. No edits to tests, fixtures, the ledger or the report.
Committed since #119: `sources.yaml` PubChem entry at `27db70e` (§4). r2.13 merged and gate
verified (§0.3). Branch is 0 behind / 29+ ahead.

## 0 · A scientific defect in canonical identity, found while checking r2.13's naming

### 0.1 · What it is

The InChI stereo-type flag says `/s1` = absolute, `/s2` = **relative**, `/s3` = racemic. A relative
string does **not** state absolute configuration. **42 snapshot InChIs carry `/s2`** (none carry
`/s3`), and **the pipeline gives every one of them an ABSOLUTE canonical key (42 of 42)**. RDKit
reads the `/s2` string as if it were absolute `/m0`:

    DrugBank 'L-Threonine'  InChI=1/…/t2-,3+/s2
    RDKit round-trip          InChI=1S/…/t2-,3+/m0/s1      <- /s2 silently becomes absolute /m0
    canonical_inchikey        AYFVYJQAPQTCCC-STHAYSLISA-N
    PubChem D-threonine CID 69435   AYFVYJQAPQTCCC-STHAYSLISA-N   <- identical
    PubChem L-threonine CID 6288    AYFVYJQAPQTCCC-GBXIJSLDSA-N

So **DrugBank's L-threonine row is keyed as D-threonine** in the canonical-identity layer that
T10, T13 and T15 join on.

### 0.2 · Magnitude, classified by LAYERS rather than keys

For each of the 42, I compared the pipeline's absolute reading (after salt-strip and uncharge) with
PubChem's InChI for the compound name, layer by layer. A key comparison alone cannot separate a
mirror image from a less specific source:

| verdict | n | meaning |
|---|---:|---|
| **MIRROR** | **13** | identical `/t` layer, **flipped `/m`**: the same centres with the **inverted** absolute configuration |
| SAME | 18 | correct absolute configuration, by chance |
| CENTRE-SET-DIFFERS | 6 | DrugBank's `/t` defines different or undefined (`?`) centres; the source is less specific, not a wrong enantiomer |
| SKELETON/FORM | 5 | the name resolved to a salt or another form; not a stereo verdict |

**The 13 mirror-image assignments:** L-Threonine, Adenosine triphosphate, **Dextropropoxyphene**,
**Ethinyl Estradiol**, Kanamycin, **Mestranol**, (3Z,5S,6R,7S,8R,8aS)-3-(octylimino)hexahydro-
[1,3]thiazolo[3,4-a]pyridine-5,6,7,8-tetrol, Acetylcarnitine, **Dolutegravir**, Hydroxydione,
Fluocortolone, **Dexetimide**, Cephaloridine.

Among the 31 with a comparable centre set, 13 are mirrored and 18 correct. That is **consistent with
a coin flip**, which is what an arbitrary `/m0` assignment would give. Several are single-enantiomer
drugs whose identity **is** their configuration (dextropropoxyphene vs levopropoxyphene, dexetimide
vs levetimide). A join on their canonical key picks up the wrong molecule's data, and nothing errors.

**Caveats, stated rather than buried:**
- **One reference source.** A MIRROR verdict assumes PubChem's name→CID resolution returns the
  correct absolute record. A second source (ChEBI, or UniChem cross-check) would harden it.
- **The stereo guard does not cause this.** It happens at InChI parse, before any tautomer step.
  The guard then returns the pre-tautomer key, which already carries the arbitrary configuration.
- **The fix is a scientific decision and is not mine to make.** Options include: key relative-stereo
  input as **stereo-free** (drops the false assertion, but merges enantiomers DrugBank did not
  distinguish); keep the key but carry a `stereo_is_relative` flag that T10/T13/T15 must honour;
  or resolve the absolute configuration from a public source and cite it. **I have changed nothing.**

Scripts: `relative_stereo.py`, `relative_vs_pubchem.py`, `relative_mirror.py` (read-only, rerunnable).

### 0.3 · r2.13 (`ebc5542`) carries a naming error that this defect explains

`plan-gate verify` passes on my branch after merging `a673207`. But r2.13's T5b done-condition,
"**L-threonine and D-allothreonine stay distinct**", is still not what the test exercises:

    member 1  DrugBank 'L-Threonine' (/s2)   pinned key …-STHAYSLISA-N  = PubChem D-threonine  (CID 69435)
    member 2  DrugBank 'D-Threonine'          pinned key …-PWNYCUMCSA-N  = PubChem D-allothreonine (CID 90624)

**As keyed, the test compares D-threonine with D-allothreonine.** DrugBank's labels are wrong
twice: DB03700 is D-allothreonine, and the "L-Threonine" string only becomes a D-threonine key through
§0.1. The guard behaviour is still correct, since these are two different stereoisomers. **I will not
rename the test to "L-threonine" while the key it pins is D-threonine's.**

biores invited an objection to the r2.13 precedent (a wording-only truth-fix, signed with no
principal ruling). **I do object, on this specific evidence:** a "wording-only" fix went in without a
check of the label against the keyed structure, which is the same miss that produced r2.12. I'd
suggest a truth-fix that names a structure should cite the InChIKey it was checked against. Not
urgent. Your call whether it goes to the principal.

---

# The four #120 scope questions (unchanged from draft)

## 1 · Step 3 citations: every §2 structure looked up by its EXACT InChI, not by name

PUG REST `POST /compound/inchi/cids/TXT` for each distinct string in `test_parse.py` and
`test_merge_report.py`, retrieved 2026-09-15:

    CID 2244    aspirin                      CID 5960 / 83887   L- / D-aspartic acid
    CID 2520    verapamil                    CID 6140 / 71567   L- / D-phenylalanine
    CID 62969   verapamil HCl                CID 115355         nitisinone (keto)
    CID 9818469 diclofenac sodium            CID 5289053        nitisinone enol
    CID 6306    L-isoleucine                 CID 1505           benzimidazole 1H AND 3H (/p+1)
    CID 99288   L-alloisoleucine             CID 1506           CRA_1144 (neutral)
    CID 90624   D-allothreonine  <- the string the test calls "D-Threonine" (confirms #120 §6)

    NO PUBLIC SOURCE → cite the snapshot as source of record, per #120:
      "L-Threonine"   InChI=1/…/t2-,3+/s2   non-standard, and /s2 = RELATIVE stereo, so this string
                      is threo-threonine with UNASSIGNED absolute configuration, not strictly L.
                      Not substituted with PubChem L-threonine (CID 6288): that would change the species.
      Malate Ion / Malate Like Intermediate   charged /p-1 and /p-2 D-malate species; no PubChem record.

**The benzimidazole is resolved.** #116 §4's 404 was a name-lookup failure. By exact InChI,
PubChem has it (1505/1506), so no snapshot citation is needed.

**Threonine naming: superseded by §0.3.** An earlier draft of this paragraph proposed
"threo-threonine (relative stereo) vs D-allothreonine". That was **also wrong**. The pipeline gives the
relative string an absolute key, and that key is D-threonine's (§0.1). The test therefore compares
**D-threonine with D-allothreonine** as keyed, and the test name waits on how §0 is ruled.

## 2 · Real accessions are in more places than the project-tree scan could see

`git grep -c -P '\bDB0\d{4}\b'` over the whole repository:

    projects/lung-on-chipsim/configs/unparseable_compounds.yaml       9   (sanctioned, ledger per #120 §4)
    projects/lung-on-chipsim/tests/test_unparseable_exclusions.py    16   (sanctioned, ledger per #120 §4)
    workstreams/lung-on-chipsim/reports/2026-09-15-stereo-guard-tms/merge_report.json   89   <- see §3.2
    workstreams/lung-on-chipsim/parked/README.md                      2   <- see §3.4
    .claude/usr/…/dispatches/  (7 payloads: 3 CTO, 4 lung-on-chipsim)  1–13 each   <- see §3.3

**Why the existing scan missed all of them:** `test_no_real_drugbank_accession_is_tracked_outside_the_declared_exceptions`
builds its list with `git ls-files` run at `cwd=PROJECT_ROOT`, so it sees `projects/lung-on-chipsim/`
only. `workstreams/` and `.claude/` were never in scope. #120 §2 asks for repo-wide coverage, which
is right, but a repo-wide guard fails immediately on §3.2–§3.4.

**I committed one of these myself.** `merge_report.json` went in with b9's tail at `2cb236a`. My
pre-commit check tested for full `InChI=` strings, the #115 criterion, and never looked for
accessions. It is local only (0 behind / 27 ahead), so a forward fix fully covers it.

## 3 · Four questions for a ruling

### 3.1 · Does a NAME on its own count as record content?

#120 §1 lists "names, synonyms" as record content, and also says "critically, the association".
These tracked or about-to-be-tracked places carry **DrugBank names without accessions**:

- the §2 tests (comments and constant names): "Malate Like Intermediate", "CRA_1144",
  "Bishydroxy[2h-1-Benzopyran-2-One,1,2-Benzopyrone]", and generic names like "L-Isoleucine";
- b9's README "Known limits (measured)" section (committed `2cb236a`);
- `merge_report.md`: all 41 split groups **by name** (committed `2cb236a`).

Some of these are generic chemical names that DrugBank did not coin (L-isoleucine, aspirin). Others are
DrugBank's own record titles ("Malate Like Intermediate", "CRA_1144"). **Is a name standing alone
record content, or only a name joined to an accession or structure?** If DrugBank-coined titles count,
the tests, the README and the report all need renaming to generic or IUPAC names.

### 3.2 · The merge report: #120 overrides #108's "list all 41 by name". Confirm the replacement.

`merge_report.json` stores every split group's `members` as `[real accession, DrugBank name]`
pairs. That is exactly the row tuple #120 forbids. **The generator `merge_report.py` (b9, `8cb72bf`)
writes them**, so any re-run re-creates the violation in a tracked file.

#108 required "list all 41 split groups by name — that list is the record of reference". Under #120
that requirement cannot stand as written. My proposal for a forward fix:

- the tracked report identifies members by **canonical InChIKey plus a PubChem CID where one resolves**,
  with no DB accession and no DrugBank name;
- the accession↔name mapping stays in the **untracked, DVC-side** journal run output, where the
  licence already sits;
- the 36/2/2/1 classification is carried by InChIKey.

**Is that the replacement you want, and does it retire #108's by-name requirement?**

### 3.3 · Guard scope vs the coordination record

Repo-wide, the guard fails on **dispatch payloads**, which are committed under the traceability
mandate and are the audit trail of these very rulings. **Four are already on `origin/lung-on-chipsim`**
(the CTO's 13:31 exclusion ruling, b9's #102 reply, my #107, the #91 T8 dispatch). My #116, still
local, pairs accessions with names **and** InChIs, which is the full forbidden tuple.

Options:
- **(a)** the guard excludes `.claude/usr/**/dispatches/` by a **named, commented exclusion** citing
  a ruling that coordination records are an audit trail, not a data product;
- **(b)** forward-fix the payloads by redacting accessions in place. That falsifies the record of
  what was actually sent and conflicts with the traceability mandate;
- **(c)** stop putting accessions in dispatches from here on, plus (a) for history.

I lean **(c)**. Editing sent dispatches seems worse than the exposure, and the four pushed ones
cannot be recalled anyway.

### 3.4 · `parked/README.md` pairs accessions with the compounds they identify

Lines 15 and 17: `DB00156/DB03700, DB00167/DB01739, DB00128/DB02655` beside threonine, isoleucine and
aspartate, and `DB00348/DB08307` beside nitisinone. It was created in `df8435f`, which is on origin.
**A forward fix** (replace the accessions with compound names or InChIKeys, depending on §3.1) is
straightforward, and I will do it once §3.1 is answered.

## 4 · Done: `sources.yaml` PubChem entry, committed `27db70e` (independent of §3)

I read NCBI's policy from source (https://www.ncbi.nlm.nih.gov/home/about/policies/, 2026-09-15).
Verbatim: "NCBI itself places no restrictions on the use or distribution of the data contained
therein." with the caveat "some submitters of the original data … may claim patent, copyright, or
other intellectual property rights in all or a portion of the data". I am recording **that
statement** as verified, with URL and date. I am **not** recording "public domain", because the page
does not say it, and `attribution` stays `NEEDS_HUMAN_CONFIRMATION`. The entry gains the §2 citation
role and the retrieval date.

## 5 · Not started until §3 is ruled

Guard test, fixture forward-fix, ledger structure-string removal, test renames, report generator
change. The fixture and ledger work per #120 §3–§4 are clear, but their final text depends on §3.1
(whether the fixtures' replacement names may be generic chemical names).
