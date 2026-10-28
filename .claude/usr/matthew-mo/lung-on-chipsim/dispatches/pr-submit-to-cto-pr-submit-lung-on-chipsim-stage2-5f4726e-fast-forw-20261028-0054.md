---
type: pr-submit
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-10-28T00:54
status: created
priority: normal
size: task
subject: "pr-submit: lung-on-chipsim-stage2 @ 5f4726e — FAST-FORWARD pushed (c781e9c..5f4726e), no force, Stage 1 intact at c04e701. Receipt verified, Hash E 24965ba over 106 files, re-checked at BOTH tips the receipt commit and the escalation commit produced. All six row-65/67 items built and falsified; 866/4/0 unselected, 835/4/31 selected, ruff format --check and ruff check both clean, ty 25/31. Not-fixed list reported with the receipt. One thing for your eye at land time: this is the first appearance of the tracked identifier column on a PUBLIC trunk, and it lands with its guard."
in_reply_to: null
---

# pr-submit: lung-on-chipsim-stage2 @ 5f4726e — FAST-FORWARD pushed (c781e9c..5f4726e), no force, Stage 1 intact at c04e701. Receipt verified, Hash E 24965ba over 106 files, re-checked at BOTH tips the receipt commit and the escalation commit produced. All six row-65/67 items built and falsified; 866/4/0 unselected, 835/4/31 selected, ruff format --check and ruff check both clean, ty 25/31. Not-fixed list reported with the receipt. One thing for your eye at land time: this is the first appearance of the tracked identifier column on a PUBLIC trunk, and it lands with its guard.

Agent: lung-on-chipsim
READY TO LAND. Pushed, receipt verified, no force anywhere in the path.

branch:        lung-on-chipsim-stage2
sha:           5f4726e
remote:        origin/lung-on-chipsim-stage2 == 5f4726e, 0 unpushed
push:          FAST-FORWARD c781e9c..5f4726e. No force, no lease.
diff base:     origin/main (0 behind)
receipt:       workstreams/lung-on-chipsim/qgr/...-qgr-pr-prep-20261028-0045-24965ba.md
hash E:        24965ba90b7e8c5c2c932a7a151408fe7cdd36c0b5637cb55b0c1e1b6d45857d (106 files)
receipt-verify: "Receipt verified ... (Hash E: 24965ba)"

STAGE 1 IS UNTOUCHED, verified after the push: origin/lung-on-chipsim is still at c04e701.

I verified your fast-forward finding before acting on it rather than taking it: the remote existed
at c781e9c, is an ancestor of my tip, 0 behind / 231 ahead. You were right and the dilemma was false.

ALSO VERIFIED, because the tip moved twice after I signed: Hash E is UNCHANGED at 24965ba at
f234485 AND at 5f4726e. diff-hash excludes the QGR directory and the coordination artifacts, so the
receipt commit and the escalation commit do not invalidate the receipt. I measured it at each tip
instead of assuming the exclusion covered both.

## SCOPE OF THE PR

The branch's whole route to the trunk: the 26 adjudicated P-gp verdicts (T14), the T15
persist-before-gate ordering fix (row 58) with its regression test, the row-39 identifier gate plus
the four vacuity fixes ruled at row 65, the output-root guard wiring and its 14-test registry, A1's
work-tree anchoring (row 67), and the accumulated Stage 2 coordination record.

## THE IDENTIFIER POSITION, stated so a reader does not have to find it

- configs/pgp_adjudication.csv is TRACKED and its first column is canonical_inchikey. Five columns;
  NO `name`, NO `snapshot_label`. The forbidden (name, structure) pairing is NOT created by the file.
- This PR is the FIRST APPEARANCE ON THE TRUNK of both that file and the gate that covers it.
  Neither is on origin/main today - I measured it, and it corrects the "already committed so this PR
  does not create the exposure" framing, which was true of the branch and false of the trunk.
- Row 39's gate IS built here and its parser table includes .csv, so configs/*.csv is covered on
  this branch, and will be covered on main once this lands. Data and guard land together.
- The pairings in poc_compounds.yaml and label_structure_reference.yaml are pre-ruled at row 33.
- tests/test_relative_stereo.py's identifiers are PINNED EXPECTED OUTPUTS of canonicalize() asserted
  against RDKit over an InChI literal in the same file - derived, not typed, re-proved every run.
  Its DrugBank accessions are in the documented synthetic DB9nnnn range (SOURCES.md:15).

## GATE, commands named both ways

    uv run pytest -q                                        866 passed / 4 skipped / 0 failed
    uv run pytest -q -m "not network and not integration"   835 / 4 skipped / 31 deselected
    uv run ruff format --check .                            85 files already formatted
    uv run ruff check .                                     All checks passed
    uv run ty check chipsim                                 25 (baseline)
    uv run ty check tests                                   31 (baseline)
    quality.typecheck_command_lung-on-chipsim               NOTSCOPED - deliberate waiver, reported

## WHAT IS NOT FIXED, reported with the receipt rather than deferred silently

The ~40 remaining QG findings; the theta sourcing vocabulary on the ratification path; one error
base per package; `unit` in the prior's ENTRY_KEYS; declared_output_roots() does not check root
EXISTENCE so a missing data/interim degrades into the generic refusal instead of E-06's two-message
split; and CONFIGS is defined twice in test_fixture_sources.py. All carried to the programme by your
ruling at rows 65 and 67. The full list with dispositions is inside the receipt (Hash B/C).

## NOTHING I BELIEVE SHOULD NOT REACH THE TRUNK

You asked me to say so if there were. There is one thing worth your eye at landing rather than an
objection: this PR puts the tracked identifier column on a PUBLIC trunk for the first time. It also
brings its guard, which is why holding them together was the right call - but it is the irreversible
half of this PR and it deserves to be a decision at land time, not a surprise.

next_handoff: your verify-pushed + receipt-verify, then land.
