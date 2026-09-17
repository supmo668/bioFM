"""Guards: tracked DECLARATIONS of what is permitted, plus a refusal, plus a registry.

Both modules here are the same shape, which is what makes them a package rather than a drawer:

  * a **tracked declaration** of what is allowed — `DECLARED_OUTPUT_ROOTS` in `output_roots`, the two
    `record_content_declarations.yaml` files read by `record_content`;
  * a **refusal** rather than a computation: the guard's job is to say no and say why, not to return
    a value a caller may interpret;
  * a **registry** that makes omission visible, so a new writer or a new project cannot silently opt
    out — the pattern that caught an unregistered fixture writer and an owner minted by `mkdir`.

`output_roots` owns WHERE record-bearing output may be WRITTEN.
`record_content` owns WHAT TRACKED FILES MAY CONTAIN — decodability, containers, repository
topology, project ownership, the declaration surface, and the report a human reads. It arrived here
in the r2.25 E6-6 extraction; before that it was 1,200 lines inside an ingest module.

This docstring is itself a standing example of why the package needs one: for the whole of that
extraction's commit it still read "the READ half still lives in `chipsim/ingest/drugbank_snapshot.py`
until E6-6's extraction lands" — stale in the one file that answers "what is a guard here", in a
paragraph that cited E6-5 to explain why an inaccurate docstring matters.
"""
