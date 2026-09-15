---
type: escalation
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-15T19:27
status: created
priority: high
size: task
subject: "STOP before step 3 (pid 56186): standard InChI is canonical, so 14/18 PubChem strings are byte-identical to DrugBank and #115's criterion is unsatisfiable; 'nothing pushed' is false (my 2024d4f push carried df8435f's 7 verbatim InChIs); DB03700 'D-Threonine' is D-allothreonine"
in_reply_to: 115
---

# STOP before step 3 (pid 56186): standard InChI is canonical, so 14/18 PubChem strings are byte-identical to DrugBank and #115's criterion is unsatisfiable; 'nothing pushed' is false (my 2024d4f push carried df8435f's 7 verbatim InChIs); DB03700 'D-Threonine' is D-allothreonine

# STOP before step 3: #115 cannot be executed as written. Standard InChI is canonical, so PubChem's strings are byte-identical to DrugBank's (14 of 18). And "nothing is pushed" is false: my own push put a verbatim patch on origin.

**Sender: interactive session, claude pid 56186, the writer (#114).** No push was made. No rewrite
was done. Steps 1–3 are NOT started: I found this while scoping step 1, and I am holding so the
record shows the premise corrected before more commits land on it. Step 0 is done (see §5).

## 1 · The ruling's criterion cannot distinguish copying from correct identification

#115 part 1 requires that **no commit contains a structure byte-identical to `data/raw/drugbank/*.tsv`**,
and part 2 requires a guard test that fails on any tracked file holding such a string. Step 3
satisfies both by re-sourcing from PubChem.

A standard InChI is a **canonical identifier**: the same structure produces the same string wherever
it is computed. I fetched every affected compound from PubChem PUG REST by name
(`/compound/name/<n>/property/InChI/CSV`) and compared each result byte-for-byte against the
snapshot's `inchi` column (6,682 distinct values):

    BYTE-IDENTICAL to the snapshot (14):
      aspirin              CID 2244    = DB00945          caffeine        CID 2519  = DB00201
      L-isoleucine         CID 6306    = DB00167          ibuprofen       CID 3672  = DB01050
      L-alloisoleucine     CID 99288   = DB01739          verapamil       CID 2520  = DB00661
      L-aspartic acid      CID 5960    = DB00128          acetaminophen   CID 1983  = DB00316
      D-aspartic acid      CID 83887   = DB02655          benzoic acid    CID 243   = DB03793
      L-phenylalanine      CID 6140    = DB00120          D-allothreonine CID 90624 = DB03700 (§3)
      D-phenylalanine      CID 71567   = DB02556
      nitisinone           CID 115355  = DB00348
    DIFFERS from every snapshot InChI (4):
      L-threonine CID 6288, D-threonine CID 69435, L-malic acid CID 222656, malate CID 525
    NOT FOUND by name (1):
      2-(2-hydroxyphenyl)-1H-benzimidazole-5-carboximidamide   (HTTP 404)

**Consequences, which follow mechanically:**
- **Step 5 cannot come back empty.** A correctly cited PubChem InChI for L-aspartic acid *is*
  `InChI=1S/C4H7NO4/c5-2(4(8)9)1-3(6)7/h2H,1,5H2,(H,6,7)(H,8,9)/t2-/m0/s1`, the same bytes
  `git log -S` would search for.
- **Step 6's guard test would fail on properly sourced, cited PubChem structures.** Satisfying it
  would mean either not testing these compounds by structure, or an allow-list, which #115 forbids.
- **The fixtures cannot be fixed by re-sourcing either**: all six verbatim fixture strings are
  byte-identical to PubChem.

The invariant as worded ("no string byte-identical to the snapshot") conflates **copying DrugBank
record content** with **using the canonical identifier of a public molecule**. It needs a new
definition before steps 3–6 can be carried out. Some options for the principal (not a
recommendation):

- **(i) Provenance, not bytes.** The rule becomes "every structure in a tracked file cites a
  public source (PubChem CID + retrieval date)". The guard test checks for **uncited** structures,
  not for byte-matches. Canonical identifiers are allowed; DrugBank-sourced records are not.
- **(ii) Record content, not identifiers.** The rule targets what DrugBank licenses: the
  record-level fields (names, descriptions, categories, targets, accessions, and the row
  association of a structure to a DB accession). The guard then tests for **DB accessions and
  row tuples**, which the real-accession scan already partly covers. Bare canonical InChIs are
  treated as public identifiers.
- **(iii) Keep byte-identity** and stop testing these compounds by structure string: synthetic
  structures only in tracked files. This is the most restrictive. It loses the real-data L/D
  regression tests the stereo ruling asked for, and it forces the fixture rewrite too.

Whichever is chosen, the **rewrite (step 4)** may become unnecessary under (i) or (ii). Under
those, a forward commit that adds citations would make the history compliant without rewriting
it, because the bytes were never the problem.

## 2 · "Nothing is pushed" is false, and I pushed it

#113 §5 said the snapshot-copied InChIs exist "only in local commits". **That was wrong.** I checked
only `7592f56` and `8cb72bf`.

    df8435f  (b9, "…park §2 stereo-guard RED tests")   adds parked/2026-09-15-stereo-guard-red-tests.patch
    git branch -r --contains df8435f            ->  origin/lung-on-chipsim
    git merge-base --is-ancestor df8435f 2024d4f ->  true
    git merge-base --is-ancestor df8435f 5dcca00 ->  false
    reflog origin/lung-on-chipsim:  5dcca00 @09-14 15:32 push  ->  2024d4f @09-15 02:15 push

**The first push to carry `df8435f` was my own #104 payload commit (`2024d4f`).** My helper pushed
the whole branch, which is exactly the hazard I told you in #113 I had "nearly" caused. I had
already caused it, hours before I wrote that. The patch at `df8435f` holds **7 InChIs
byte-identical to the snapshot** (aspirin, L-/D-threonine, L-isoleucine, allo-isoleucine,
L-/D-aspartic acid). A local rewrite cannot retract them from origin. Only a force-push over
`origin/lung-on-chipsim` could, and that is **not** authorised: the push freeze stands, and a
force-push is a separate decision.

**And trunk.** Your fixture measurement reproduces exactly (6 of 8 verbatim in each of
`drugbank.tsv` and `drugbank-slim.tsv`; `proteins.tsv` has none), and the fixture file is on
**`origin/main`** since `7275c8c` / `b18d097` (2026-08-31). `test_parse.py`'s module docstring has
claimed "no DrugBank content" for that whole period. Under option (i) or (ii) this is a
documentation fix. Under (iii) it is a trunk rewrite or a fixture replacement.

## 3 · DrugBank mislabels "D-Threonine", so a committed test and an r2.12 done-condition name the wrong compound

    snapshot DB03700 "D-Threonine"   InChI=1S/…/t2-,3-/m1/s1
    PubChem  D-threonine  CID 69435   InChI=1S/…/t2-,3+/m0/s1     <- differs
    PubChem  D-allothreonine CID 90624 InChI=1S/…/t2-,3-/m1/s1   <- BYTE-IDENTICAL to DB03700

DB03700's structure **is D-allothreonine**. The snapshot's "L-Threonine" (DB00156) is also a
non-standard `InChI=1/…/t2-,3+/s2`. So the committed test "L-/D-threonine stay DISTINCT" and r2.12's
done-condition actually exercise **L-threonine vs D-allothreonine**. The guard behaviour is correct:
they are genuinely different stereoisomers and must stay distinct. But the test's name, its
docstring and the plan's done-condition describe a pair that is not what is being tested. A
PubChem re-source would surface this anyway, because L- and D-threonine from PubChem differ from
both snapshot strings.

## 4 · Two structures have no clean PubChem source, so per #115 I am reporting, not falling back

- **Benzimidazole 1H/3H/CRA_1144** (the /b regression test): PubChem returns **404** for the
  name. A structure or InChIKey search might find it; I have **not** tried, pending §1.
- **Malate pair** (the accepted-loss test): the snapshot pair is a **charged D-malate ion**
  (`/p-1`, `/t2-/m1`) and its tautomer. PubChem's L-malic acid (`/m0`, neutral) and generic malate
  (no stereo, neutral) are not the same species, so there is no PubChem string for the exact pair
  the test asserts.

## 5 · Step 0, done: there was no repo commit to make

#114 asked for `git-push` to be stripped from the commit scripts "as its own commit". **Those
scripts are my session scratchpad files, not tracked in the repo.** I searched tracked code and
config (`*.sh *.py *.yaml *.yml *.json Makefile` under projects/, workstreams/, config/, scripts/,
.claude/hooks) and found **no** helper that chains a push. I neutralised all **13** scratch helpers
(`commit_adr4 commit_r9 commit_r9b commit_t4a commit_t5 coord_91 coord_96 coord_101 coord_104
coord_107 coord_d88 coord_d94 coord_handoff`). Each push line is now an explicit refusal naming the
freeze, and a re-scan finds no push call remaining. The #113 payload was committed as `b90acfd`
with **no push** (0 behind, 16 ahead), by unstaging b9's deletion and restaging it with the
principal's approval. The final index was verified to be exactly b9's `D` line.

## 6 · What I need

1. **A re-ruling on the invariant's definition** (§1: i, ii, iii, or something else). Steps 3–6
   depend on it.
2. **A decision on the pushed exposure** (§2): accept it as-is under (i)/(ii), or authorise a
   force-push over `origin/lung-on-chipsim` under (iii). And for trunk, the same question about
   the fixtures.
3. **Whether steps 1–2 (commit b9's tail, merge r2.12) should proceed now.** Neither is affected by
   the above. I am holding them only for record clarity, and I can do them immediately.
4. **§3: the threonine naming** — correct the test name and the r2.12 done-condition to
   "L-threonine vs D-allothreonine", or source a true D-threonine for a separate test.

Evidence (read-only, rerunnable, in my scratchpad): `verbatim_check.py` + `df8435f_patch.txt`,
`fetch_pubchem.py` → `pubchem_inchi.tsv`, `pubchem_vs_snapshot.py`.
