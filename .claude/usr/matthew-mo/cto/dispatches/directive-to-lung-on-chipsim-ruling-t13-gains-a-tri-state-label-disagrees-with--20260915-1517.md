---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-15T22:17
status: created
priority: high
size: task
subject: "RULING: T13 gains a tri-state label_disagrees_with_key generated column (11 genuine label errors measured, 1 artifact, 75 unresolved of 134); roster reports rather than rejects; reference table must be committed, not live-fetched"
in_reply_to: null
---

# RULING: T13 gains a tri-state label_disagrees_with_key generated column (11 genuine label errors measured, 1 artifact, 75 unresolved of 134); roster reports rather than rejects; reference table must be committed, not live-fetched

# RULING on the label/structure question: the warning column is IN. Measured, then classified.

## 1 · The measurement, and why it changed my answer

I measured every snapshot row whose name carries a `D-`/`L-` prefix and compared its key against
PubChem's keys for both enantiomers of the same base name:

    rows with a D-/L- prefix:            134
    resolvable against PubChem (both):    59
    label CONTRADICTS structure:          13
    unresolvable (no record / neither):   75

Then I classified the 13, because a raw contradiction count conflates a source defect with the
pipeline defect you just fixed:

    GENUINE label errors, absolute rows (11):
      D-leucine, D-alanine, D-glutamine, D-glutamic acid, D-proline, D-cysteine,
      D-lysine, D-treitol, D-tyrosine, D-arginine   -> all carry L structures
      one L--prefixed boronic-acid alanine          -> keys as D
      These key identically before and after the re-key. The pipeline can only report them.
    ARTIFACT of the old absolute reading (1):
      "L-Threonine" (relative source) -> keyed as D before, stereo-free now. FIXED by your re-key.
    UNRESOLVED (1): "L-BENZYLSUCCINIC ACID" — not counted.

**11 is a floor, not a total**: 75 rows could not be resolved either way, and I have not attempted
a structure-based lookup for those.

## 2 · Ruling: T13 gets a generated warning column

**You were right that this needs a column, and the number is why.** Three rows would have been a
recorded limit. **Eleven genuine errors, nine of them common amino acids**, is systematic — and the
person most exposed is the reviewer doing 60-90 minutes of adjudication while the worksheet prints
"D-Proline" beside an L structure. A limit in a document does not reach them; a column in the sheet
they are reading does.

- Add it to the **same `GENERATED_COLUMNS` class** just ratified for `stereo_is_relative`: computed
  on every regeneration, **never carried**, **optional on read**. Same semantics, same reasons.
- Name it for what it asserts, e.g. `label_disagrees_with_key`, and make it **tri-state**:
  disagrees / agrees / unresolved. Two-state would force 75 unresolvable rows into a false
  "agrees", which is the same silent-default failure we keep finding.
- Compute it from a **committed reference table** of (base name -> L key, D key) with its retrieval
  date, not from a live API call at worksheet-generation time. A worksheet must regenerate
  identically offline, and a network dependency inside human-artefact generation is a reproducibility
  hazard. Cite the source per row.
- **It does not gate anything.** It informs the reviewer. Nothing is filtered or rejected on it.

## 3 · Roster (T18): report, do not reject

Unlike a flagged relative-stereo key, a label disagreement does not make the identity wrong — the
key is right and the name is wrong. So the roster **reports** disagreements, listing them, and does
not reject. Rejection stays reserved for flagged relative-stereo keys per #122 §0.

## 4 · Recording it

This belongs in the limits text as a measured figure with its classification, not as "some labels
are wrong": **11 genuine mislabels on absolute rows, 1 artifact fixed by the re-key, 75 unresolved,
out of 134 D-/L- prefixed rows.** r2.14 carries the same numbers, signed.

## 5 · What this says about the study, and it is worth saying plainly

Three defects in one layer have now each been found by checking a thing nobody was asked to check:
the `/b` over-breadth, the relative-stereo mis-keying, and now the source's own labels. Every one was
invisible to a green test suite. **The generalisable rule for this project: where a name and a
structure both exist, join on the structure and treat the name as annotation.** That is now in the
plan at T5b (iii) as a pinning rule, and it should survive into the model card.

next: §1-§4 of #125 plus this column, then #122's remaining fixes, guard test, fixtures, ledger,
re-run, §2 boundary. Push stays frozen.
