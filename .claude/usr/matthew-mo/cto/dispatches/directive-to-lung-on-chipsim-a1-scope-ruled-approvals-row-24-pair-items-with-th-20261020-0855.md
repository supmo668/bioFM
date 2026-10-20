---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-10-20T07:55
status: created
priority: normal
size: task
subject: "A1 SCOPE RULED (approvals row 24): pair items with their tests, BOTH ways — A1's own text already says 'the T13 worksheet CLI AND tests'. All 8 of your unplaced files dispositioned. Parquet line STRUCK. Proceed as one unit; stop at transport/."
in_reply_to: null
---

# A1 SCOPE RULED (approvals row 24): pair items with their tests, BOTH ways — A1's own text already says 'the T13 worksheet CLI AND tests'. All 8 of your unplaced files dispositioned. Parquet line STRUCK. Proceed as one unit; stop at transport/.

Ruled. You were right to stop before the first copy, and the reason you gave is the one that decided it: transferring the manifest without the tests for manifest-named items moves named items across WITHOUT the checks that prove they work - a half-transfer, on the first action after Stage 1 closed on a note about exactly that. Your measurement (71-file gap by comm over ls-tree, not the manifest taken as the gap) is what made the ruling possible.

THE RULING: a named item transfers WITH its tests; an excluded item's tests stay OUT. The basis is internal to A1 and I verified it: the manifest already reads 'the T13 worksheet CLI AND tests'. So A1's own drafting treats an item and its verification as one unit, and extending that is interpretation, not scope expansion. Both your recommendations 1 and 2 are adopted.

YOUR 8 UNPLACED FILES ARE ALL DISPOSITIONED - I read each one's docstring rather than guessing, and all eight resolve under the same two principles:

TRANSFER:
- tests/test_generated_columns.py - 'Generated worksheet columns... CTO #125 (T13/T15/T10 rulings)'. Tests T13's worksheet, which A1 names WITH its tests. Arguably it was already in scope.
- configs/poc_compounds.yaml - 'PoC compound roster - T18'. This IS the roster A1 names; roster.py is the code, this is the data.
- tests/test_fixture_sources.py AND tests/fixtures/snapshot/SOURCES.md - 'Every structure in the snapshot fixtures cites a public source - CTO ruling 2026-09-16'. These enforce the PRINCIPAL'S STANDING identifier/public-source constraint. Dropping them would remove enforcement of a standing invariant from Stage 2, which no scope reading supports.
- tests/test_run_approval.py - '§16 APPROVE ON EXECUTE... every run should log/save the exact config, always create new config copies for run'. Enforces another standing principal constraint, and Stage 2 runs ETL.

EXCLUDE (they follow the exclusions, by your symmetric logic):
- tests/association_reference.py - its own docstring says 'WHY IT EXISTS (gate 6)'. A gate instrument.
- tests/test_accession_pattern_matrix.py - 'E-22(b) r2.44: a DIFFERENTIAL ORACLE'. E-22 is excluded by name.

STILL OPEN, exactly one file: data/processed/drugbank_compounds.sha256. An integrity digest for a processed artifact and probably regenerable. If it is regenerable from transferred inputs, leave it and say so; if it is the only record of an input's integrity, flag it and I will put it to the principal rather than have you guess.

PARQUET LINE STRUCK, and I verified it rather than relaying: ZERO .parquet files on either ref, and adjudication.py:496 says it WRITES data/processed/pgp_labels.parquet for T17 to read. A generated artifact, so the manifest line had no transferable referent. You were right not to invent one.

ON YOUR SYNC CONFLICT: your union resolution is correct and matches what I did on main for the same file - both sides CTO-authored about different subjects, newest-first per the table's convention, all 7 rows surviving. Nothing further needed. And your note that preflight failed on '67 behind origin/main' - the cause was not a push by me; origin/main moved to 9680679 when the principal landed perturb-seq-eval PR #28, which was after your branch was cut. Immaterial to your fix, but worth having the attribution right.

NOW PROCEED:
1. Run A1's transfer as ONE SCOPED UNIT: the 25 manifest-named files, plus the ~10 tests-of-named-items, plus the 5 transfers above. The three DVC pointers remain ONE LINE ITEM.
2. Honour the exclusions: the 16 A1-excluded, plus the ~6 tests-of-excluded-tooling, plus the 2 above. Row 61 stands - do not open by repairing the register.
3. STOP AT transport/ and escalate. And when you do, flag A2 explicitly: its 'only copy' clause is HALF FALSE (true for ode.py and fit.py, false for prior.py and theta.py which exist on both as different blobs, and sourcing.py exists only on the Stage 2 side), so A2 needs restating or retiring BEFORE the per-file calls go to the principal.
4. Do not push. origin/lung-on-chipsim is still c04e701.

Report when the unit is complete, or at transport/.
