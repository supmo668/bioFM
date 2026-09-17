"""Guards: rules about WHERE record-bearing output may be WRITTEN.

The READ half — the repo-wide record-content scan, its declarations and the ownership map — still
lives in `chipsim/ingest/drugbank_snapshot.py` until E6-6's extraction lands. Saying so here
matters: a package docstring claiming both halves is an overclaim of coverage by a guard, which is
the thing E6-5 forbids, one directory above the two docstrings E6-5 made scrupulous about it.

Kept out of `ingest/` and `harmonize/` deliberately. Both call these rules, so a guard living in
either would make one a dependency of the other, and the guard vocabulary had already outgrown the
module hosting it (CTO ruling, QG §6 E6-6).
"""
