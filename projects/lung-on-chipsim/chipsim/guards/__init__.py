"""Guards: rules about WHERE things may be written and WHAT may be read.

Kept out of `ingest/` and `harmonize/` deliberately. Both call these rules, so a guard living in
either would make one a dependency of the other, and the guard vocabulary had already outgrown the
module hosting it (CTO ruling, QG §6 E6-6).
"""
