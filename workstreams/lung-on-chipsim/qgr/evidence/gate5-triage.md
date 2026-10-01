# Gate 5 triage. Every finding at or above threshold is ACCEPTED and fixed in-gate. Below-threshold ones are fixed where cheap.
R01 accept: fixed 46f4bbe (red->green)
R02 accept: fixed 5427d33 (red->green)
R03 accept: fixed 700e0b4 (red->green), pre-existing, on a neighbouring line
R04 accept: prose fixed in-tree; the signed r2.28/r2.29 text needs an r2.47b pointer, which is CTO-owned, so it is ESCALATED in the verdict
R05 accept: axis widened to more bodies plus a docstring stating the exact limit; the signed (b) wording "closed" needs an r2.47b correction, which is CTO-owned, so it is ESCALATED
R06 accept: fixed 5675c80 (mutants killed)
R07 accept: fixed eb960df (mutant killed)
R08 accept: fixed 11152a5 (mutant killed)
R10 accept: shlex-exact binding
R11 accept: exact digit-set equality
R13 accept: fixed 2fccd89 (mutant killed)
R14 accept: comment corrected, trailer on every path pinned or comment narrowed
R09 accept (below): 900/899 of 1000 rows
R12 accept (below): widen _E22_FILES to every file edited in range
R16 accept (below): duplicate-line check; RATIO_ROWS in BOUNDARY_CASES asserted
R15 accept (below): DES-12 line cite, DES-13 long line, DES-6 None wording, DES-9 message, DES-10 runtime, DES-11 BOM check
R17 note: harness dup def is in the committed evidence file; noted, not rewritten (evidence is append-only)
