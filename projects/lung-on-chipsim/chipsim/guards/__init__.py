"""Guards: tracked DECLARATIONS of what is permitted, plus a refusal, plus a registry.

SEVEN modules live here. Two are GUARDS, two are LEAVES, and three are the machinery the guards are
built from — and the dependency order is one-way, which is the property the r2.29 split exists to
establish:

    errors, policy            (leaves: import nothing from this package)
      <- report               (presentation + the scan data types; imports `errors` only)
      <- decoding, repo       (bounded byte reading; git topology)
      <- record_content       (the policy that composes them)
      <- chipsim/record_content.py   (the composition root, one level up)

THE TWO GUARDS are the same shape, which is what makes this a package rather than a drawer:

  * a **tracked declaration** of what is allowed — `DECLARED_OUTPUT_ROOTS` in `output_roots`, the two
    `record_content_declarations.yaml` files read by `record_content`;
  * a **refusal** rather than a computation: the guard's job is to say no and say why, not to return
    a value a caller may interpret;
  * a **registry** that makes omission visible, so a new writer or a new project cannot silently opt
    out — the pattern that caught an unregistered fixture writer and an owner minted by `mkdir`.

`output_roots` owns WHERE record-bearing output may be WRITTEN.
`record_content` owns WHAT TRACKED FILES MAY CONTAIN — project ownership, the declaration surface,
the scan as data, and the verdict.

THE TWO LEAVES exist so that no module owning a shared vocabulary becomes a dependency of its peers:
`errors` holds the exception taxonomy — "the scan could not be performed" (exit 3), "the declaration
data is unusable" (exit 2), and a guard's own invariant violation, which is NOT catchable by the
handler that turns declaration problems into a report. `policy` holds `ContentPolicy` and the two
fail-closed predicates, because the seam that keeps the guard ignorant of DrugBank was forcing
DrugBank to import the entire guard for a two-field dataclass.

THE THREE SUPPORTING LAYERS: `decoding` owns BOUNDED READING — magics, container readers, the
decode/readability verdict, every read size-capped, because a guard that exhausts memory on a crafted
file is a guard that did not say no. `repo` owns GIT TOPOLOGY — the repository root, the tracked
listing, and materialising the index, which is how the commit gate reads the bytes it certifies
rather than the working files. `report` owns PRESENTATION and the scan data types, and imports
`errors` and the standard library and nothing else — so "the renderer decides nothing" is a property
a test can check rather than one a reviewer must verify by reading.

THIS DOCSTRING IS A STANDING EXAMPLE OF WHY THE PACKAGE NEEDS ONE, AND IT HAS NOW GONE STALE THREE
TIMES. Through the whole of the E6-6 extraction it still said the READ half lived in the ingest
module. Then E-18 moved decoding and topology out, and for two commits it still said "both modules"
and credited `record_content` with topology and containers. Then r2.29 made seven modules and moved
the exception to a leaf, and this file still said "FOUR modules", still credited `repo` with path
rendering, and — worst — still stated the placement rule that `errors.py` had just retracted as
FALSE ON THE FACTS, sending a reader to `repo` for a vocabulary that had moved and telling them a
rule that had been withdrawn.

Each time, the diff that invalidated this file did not open it. That is the pattern worth naming:
**a change audits what it wrote and not what it invalidated**, and a charter is the file least likely
to be re-read and most likely to be believed.
"""
