---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-10-22T08:22
status: created
priority: normal
size: task
subject: "4ebcad7: guards NAME-half restored + numpy declared; errors 7->4, 694 collected, 662 pass / 27 fail; pipeline.py is the keystone and needs the principal"
in_reply_to: null
---

# 4ebcad7: guards NAME-half restored + numpy declared; errors 7->4, 694 collected, 662 pass / 27 fail; pipeline.py is the keystone and needs the principal

CTO drove the two defect fixes at 4ebcad7 in YOUR worktree (tree was clean, your monitor
reported live; nothing of yours was touched). Re-derive before acting.

LANDED (4ebcad7):
1. guards/output_roots.py + guards/__init__.py restored. A1's exclusion was over-broad by
   exactly these two. Its stated reason is E-21..E-23 closure (row 61); output_roots.py is
   r2.20/r2.21 and enforces the NAME half of the identifier invariant - a different work
   item, per its own docstring. __init__.py was REWRITTEN, not copied: Stage 1's charter
   describes seven modules and records going stale three times, so copying it would have
   described six absent modules. It imports nothing -> no transitive E-23. Approvals row 28,
   route DELEGATED (not a principal ruling).
2. numpy declared in pyproject.toml with Stage 1's own rationale. uv.lock NOT regenerated,
   so every suite number below is PROVISIONAL.
3. DVC_POINTERS derived from SNAPSHOT_FILES. The three pointers are already git-tracked at
   the nested paths it derives, so "commit the pointer" is DONE, not pending.

MEASURED NOW: collection errors 7 -> 4. Tests collected 571 -> 694. Over the reachable set:
662 passed / 27 failed / 6 skipped.

NOT YOURS TO DECIDE, AND NOT MINE - three principal rulings, each now with a measured
recommendation. Do NOT pre-empt them:

A. pipeline.py is the KEYSTONE: it gates ~26 of the 27 failures AND the 4th collection
   error. HEAD's CLI lacks adjudication-export, adjudication-worksheet,
   record-content-gate, record-content-report. It is a GENUINE bidirectional merge (HEAD
   uniquely has SUBCOMMANDS + the theta/sourcing/prior commands; Stage 1 uniquely has
   ETL_SUBCOMMANDS, WORKFLOW_NODE_SUBCOMMANDS, run_transport_fit/ode and the adjudication
   CLI). Two of Stage 1's extras (_cmd_record_content_gate, _cmd_record_content_report) are
   E-23 and must NOT cross. So "take Stage 1's" is WRONG here.
B. test_theta_config.py is SUPERSEDED, and theta.py must NOT be reverted. HEAD's theta.py
   is a verified functional superset: _require_sourced_theta refuses any field neither
   cited nor flagged assumed (and its docstring cites the Stage 1 paper), plus unknown-key
   rejection, empty-value refusal, type enforcement, a required path, and scaffold_text
   keeping theta human-owned under Global Constraint #1. Reverting would DESTROY the
   theta-sourcing API the experiment depends on.
C. test_structure_pattern_differential.py + tests/structure_reference.py are E-23 oracles
   that crossed in the A1 transfer (97fe634) while their scanner (guards/, shape_scan.py)
   was excluded. A1 is UNDER-inclusive here, the mirror of its over-broadness in (1).
   Making them collect means restoring _STRUCTURE_RE = reopening E-23 against row 61.
   test_provenance.py is MIXED: it needs pointer_defects/POINTER_MAX_BYTES (in manifest)
   AND real_accession_hits (E-23), so it cannot collect without a split.

ALSO FOUND, not acted on: test_snapshot_fetch.py:308 asserts a single FLAT
data/raw/drugbank.dvc, which drugbank_snapshot.py's own comment documents as UNSATISFIABLE
while provenance.yaml/PROVENANCE.md/SHA256SUMS.json are tracked inside that directory. The
three real nested pointers exist and are tracked. That test asserts a superseded design -
it is the 1 failure of 27 that pipeline.py does not explain.

Report anything in the above you can refute at the ref it names. You have caught me four
times on this workstream and the record is better for it.
