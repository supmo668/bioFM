---
type: pr-submit
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-10-13T19:22
status: created
priority: normal
size: task
subject: "Ready for PR landing: perturb-seq-eval — + RR-2 (text-only correction of RR-1, #598); new receipt 5d0c91d supersedes 1b8e57f; deposit held"
in_reply_to: null
---

# Ready for PR landing: perturb-seq-eval — + RR-2 (text-only correction of RR-1, #598); new receipt 5d0c91d supersedes 1b8e57f; deposit held

Re #598. RR-2 done and gated; branch re-submitted for landing. Receipt 1b8e57f is superseded by the one below. Deposit NOT run (held for the principal's go).

branch: perturb-seq-eval
receipted sha: 03b943716204dbf6500655ff8fec2589a893bd2b (origin equal; 0 behind origin/main). This dispatch's payload goes on top as a QG-exempt coord commit, as before.
diff-hash vs origin/main: 5d0c91d
receipt: workstreams/perturb-seq-eval/qgr/bioFM-matthew-mo-perturb-seq-eval-perturb-seq-eval-bioFM-qgr-iteration-complete-20261013-1221-5d0c91d.md
QGRs on the branch: qgr-rr1-*, qgr-key-retire-*, qgr-rr2-* (plus DEPOSIT-PREP at 5407606)
draft: false
migrations_pending: none

RR-2: a new entry appended after RR-1 in paper/data/run_record_amendments.json. It replaces RR-1's rerun_note, also_replaced_in_docs and out_of_scope in full. files: [], so no hash rows. The appendix now names RR-2, with the date generated from the record (resRRTwoDate). The approval log has row 2.

#598 conditions:
1. Exact allowlist: ids must equal ["RR-1","RR-2"]. Adding RR-3 fails (mutation-checked).
2. Fails both ways, mutation-checked:
   - A false, filler, emptied or extra-keyed RR-2 fails: the entry is pinned by digest, its key set is exact, and its claims are cross-checked against code and docs.
   - Superseded wording presented as current fails anywhere: every .md/.tex/.py/.cff/.yml outside tests, artifacts, build and paper/data is scanned, normalised for case, LaTeX escapes, ~ and line-broken hyphens. % comments are stripped only in .tex.
3. RR-1 byte-identical to ded9cfc: the parsed entry and the serialised prefix are both checked. The digest and bb3e2e2 tests are untouched. No pre-RR-1 values appear.

Gate: 4 findings passed (T2 90, T1 88, T3 85, D1 82); all 10 fixed, including 6 filtered. Side fix: two older tests' comment-strip regex looked behind for two backslashes instead of one, so an escaped \% was treated as a comment; corrected.
Checks on the committed HEAD: 1177 tests pass; lint clean; fill and render --check match; tectonic 0 overfull / 0 undefined.

CTO action: re-verify, then the principal lands with /airdlc:pr-cto-land perturb-seq-eval --no-release in your session. I park until master-updated or changes-requested.
next_handoff: CTO re-verify + principal land
