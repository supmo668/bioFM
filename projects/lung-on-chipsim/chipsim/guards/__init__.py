"""Guards: tracked DECLARATIONS of what is permitted, plus a refusal, plus a registry.

FOUR modules live here, and the two GUARDS among them are the same shape — which is what makes this
a package rather than a drawer:

  * a **tracked declaration** of what is allowed — `DECLARED_OUTPUT_ROOTS` in `output_roots`, the two
    `record_content_declarations.yaml` files read by `record_content`;
  * a **refusal** rather than a computation: the guard's job is to say no and say why, not to return
    a value a caller may interpret;
  * a **registry** that makes omission visible, so a new writer or a new project cannot silently opt
    out — the pattern that caught an unregistered fixture writer and an owner minted by `mkdir`.

THE TWO GUARDS:
`output_roots` owns WHERE record-bearing output may be WRITTEN.
`record_content` owns WHAT TRACKED FILES MAY CONTAIN — project ownership, the declaration surface,
the scan as data, and the report a human reads. It arrived here in the r2.25 E6-6 extraction; before
that it was 1,200 lines inside an ingest module.

THE TWO SUPPORTING LAYERS, split out of `record_content` at r2.27 E-18 because a policy module that
also owned byte-reading and process-spawning could not be read as either:
`decoding` owns BOUNDED READING — magics, container readers, the decode/readability verdict. Every
read is size-capped: a guard that exhausts memory on a crafted file is a guard that did not say no.
`repo` owns GIT TOPOLOGY — the repository root, the tracked listing, path rendering, and the
anti-vacuity floor. It also holds `RecordContentScanError`, because the exception belongs with the
layer that RAISES it and `record_content` imports `repo`, not the reverse.

THIS DOCSTRING IS A STANDING EXAMPLE OF WHY THE PACKAGE NEEDS ONE, AND IT HAS NOW GONE STALE TWICE.
Through the whole of the E6-6 extraction commit it still read "the READ half still lives in
`chipsim/ingest/drugbank_snapshot.py` until E6-6's extraction lands" — stale in the one file that
answers "what is a guard here", in a paragraph citing E6-5 to explain why an inaccurate docstring
matters. Then E-18 moved decoding and topology OUT, and for two commits this file still said "both
modules" and still credited `record_content` with "decodability, containers, repository topology".
Prose that implies a structure the code does not have is a false claim, and it survives review
precisely because a charter reads as settled. The rule earns its keep by being applied to itself.
"""
