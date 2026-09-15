---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-15T22:06
status: created
priority: high
size: task
subject: "§0 re-key LANDED 1b74814 (pid 56186): /s2 keyed stereo-free + flag + stage + persisted; real snapshot 156->154 (esomeprazole/omeprazole merge, 3 splits, 0 diastereomer merges); DrugBank 'D-' lysine/alanine/cysteine rows carry L structures; my helper's accession guard silently didn't run (verified clean)"
in_reply_to: 122
---

# §0 re-key LANDED 1b74814 (pid 56186): /s2 keyed stereo-free + flag + stage + persisted; real snapshot 156->154 (esomeprazole/omeprazole merge, 3 splits, 0 diastereomer merges); DrugBank 'D-' lysine/alanine/cysteine rows carry L structures; my helper's accession guard silently didn't run (verified clean)

# §0 re-key LANDED (1b74814): relative-stereo keyed stereo-free + flag + merge stage + persisted. Real snapshot 156→154. DrugBank's "D-" lysine/alanine/cysteine rows carry L structures. My commit helper's accession check did not run.

**Sender: claude pid 56186, writer.** Not pushed (0 behind / 33 ahead). No accessions in this
dispatch, per #122 §3. Compounds are named by generic chemical names only.

## 1 · What landed at `1b74814`

- **`canonicalize(..., strip_relative_stereo=True)`**: when the source InChI declares `/s2`,
  **tetrahedral** chiral tags are cleared immediately after parse, before salt-strip.
  `/b` is kept, because InChI double-bond geometry is always absolute and `/s` qualifies only
  the sp3 layers. `False` is a measurement-only mode that reproduces the old behaviour.
- **`Canonicalization.stereo_is_relative`** (describes the SOURCE, so it is also True in
  measurement mode) and **`parsed_as_given`** (the pre-strip parse).
- **`is_relative_stereo(inchi)`** reads the flag from the string's own layers, without RDKit,
  so **unparseable/excluded rows carry it too**.
- **Both `add_canonical_identity` paths emit a `bool` `stereo_is_relative` column**, including
  on empty frames.
- **`MERGE_STAGES` gains `relative-stereo` immediately after `parse`**. `parse` compares the pre-strip
  parse and `relative-stereo` the post-strip parse, so the re-key's merges are attributable.
- **`relative_stereo_effect()`** reports merges **and splits**. Stripping mostly merges, but it also
  separates a relative compound from an absolute one it used to match by RDKit's arbitrary
  assignment. Member IDs live only in memory, for the untracked journal.
- **`PERSISTED_COMPOUND_COLUMNS` now carries `stereo_is_relative`.** This one matters:
  `write_compounds` persists **only** that tuple, so without it **the flag was silently dropped at
  T5a** and could never have reached T10/T13/T15/T18. **Coverage gap:** no existing test pinned
  that tuple, which is why adding the column broke nothing. I will add a pin.

Test-first: `tests/test_relative_stereo.py` (8 tests), confirmed failing for the missing API
before implementation. Structures are cited: CID 205 (stereo-free threonine), 69435
(D-threonine, the key the defect produced), 5960 (L-aspartic acid). The relative threonine
string has no public record and cites the snapshot as source of record. **Two existing tests
updated deliberately:** the stage-order tuple, and the threonine pin in `test_parse.py`, now
CID 205's stereo-free key (it was D-threonine's). **The threonine test's name and label wording
are HELD unchanged, per #122 §6.** Suite **602 passed / 4 skipped**; ruff clean.

## 2 · Effect on the real snapshot (6,802 kept, 8 excluded)

    stereo_is_relative = True:       42
    merge groups, strip OFF -> ON:   156 -> 154
    new merges (relative-stereo):    1
    splits:                          3
    diastereomer merges:             0   (every new merge's members share a /t layer or have none)
    stage breakdown WITH re-key:     upstream-duplicate 101 | salt 19 | uncharge 26 | tautomer 7 | relative-stereo 1

**The one new merge: esomeprazole + omeprazole.** DrugBank records esomeprazole with relative
stereo, so it now merges with omeprazole (no stereo). This is the ruling's accepted, honest
outcome, but it should be stated plainly because **esomeprazole is by definition the
single S-enantiomer**. After the re-key, the study cannot tell it from omeprazole on DrugBank's
evidence alone.

**The three splits:** relative "L-lysine", "L-alanine" and "L-cysteine" each separate from an
absolute row labelled "D-" that used to share their key.

**No diastereomer merges.** I had held a concern that stripping all sp3 stereo could merge threo
and erythro forms DrugBank did distinguish. Measured on the real snapshot, it does not happen.

## 3 · The splits expose three MORE DrugBank label errors, now confirmed against PubChem

    lysine    PubChem L = …-YFKPBYRVSA-N   PubChem D = …-RXMQYKEDSA-N
      row labelled "D-Lysine"   (absolute)  keys …-YFKPBYRVSA-N  -> = PubChem L   (before AND after re-key)
    alanine   PubChem L = …-REOHCLBHSA-N   PubChem D = …-UWTATZPHSA-N
      row labelled "D-Alanine"  (absolute)  keys …-REOHCLBHSA-N  -> = PubChem L
    cysteine  PubChem L = …-REOHCLBHSA-N   PubChem D = …-UWTATZPHSA-N
      row labelled "D-Cysteine" (absolute)  keys …-REOHCLBHSA-N  -> = PubChem L

**The snapshot rows labelled D-lysine, D-alanine and D-cysteine carry the L structure.** That makes
three more label/structure mismatches of the DB03700 kind.

**What it means for joins, now that the re-key has landed:** the canonical keys for **L**-lysine,
L-alanine and L-cysteine belong **only to rows DrugBank labels "D-"**. The rows it labels "L-" are
relative and sit on stereo-free keys. So a lookup of L-lysine by canonical key returns a row whose
DrugBank label says D-lysine. **The join is chemically correct**: the key follows the structure, which
is the whole point. **But any label-bearing output** (the adjudication CSV's `name`, a roster
built from names, a card) will print "D-" beside an L structure. I have changed nothing. This is
worth recording as a limit, and possibly a label-vs-key consistency check.

## 4 · Disclosure: my commit helper's accession check silently did not run

`commit_s0.sh` guarded the commit with `grep -P '\bDB(?!9\d{4}\b)\d{5}\b'`. **macOS `grep` has no
`-P`**, so it exited 2 with a usage error, and inside `if grep …; then` that reads as "no match". The
script continued. **The check reported clean without executing.** That is the "check that cannot fail"
defect again, in my own helper.

Verified retroactively with the tool that supports it, over exactly the five committed files at
`HEAD`:

    git grep -n -P '\bDB(?!9\d{4}\b)\d{5}\b' HEAD -- <the five files>
    (no output)   exit 1 = no match   ->  CLEAN: no real accession entered 1b74814

From here on, helper guards use `git grep -P` (or Python), and any guard's exit status is checked
explicitly rather than folded into `if`.

## 5 · Plan coverage

**The `/s2` rule is not in the signed plan** (r2.13, `ebc5542`). You said no r2.14 until the
re-key lands. It has now landed, so the amendment is owed: T5b's done-conditions should name
the flag, the persisted column, the `relative-stereo` stage, and the threonine test's members
**by the InChIKeys it pins** (your adopted rule, #122 §6). Under the re-key, those are CID 205's
stereo-free key vs D-allothreonine's `…-PWNYCUMCSA-N` (CID 90624).

## 6 · Next, in #122's order

T10/T13/T15 honour the flag, and T18's roster can exclude flagged compounds. Then §1 (DrugBank-coined
titles), §2 (`merge_report.py`: InChIKey + CID, no accessions or names), §4 (`parked/README.md`),
§5 (repo-root scan with falsification), the guard test, fixtures, ledger, then the re-run of suite
and report, then the §2 boundary. Push stays frozen.
