---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-10-11T04:35
status: created
priority: normal
size: task
subject: "S1 applied as RR-1 amendment, re-gated (ded9cfc); deposit held; code-retirement ruling needed"
in_reply_to: null
---

# S1 applied as RR-1 amendment, re-gated (ded9cfc); deposit held; code-retirement ruling needed

Re #582. S1 applied as a dated amendment and re-gated. Deposit NOT run (held for the principal's go).

- RR-1 (2026-10-08): llm_key_source removed from provenance.json, both run jsonl files and the three configs/runs manifests. Only that key changed; byte-exact re-serialization; the analyser still reproduces summary.json.
- Run manifest 323af965b631ce83 (superseded, kept with a row saying why) -> 70be925de94bfb37. All 6 before/after SHA-256 values are in paper/data/run_record_amendments.json, and a test checks the before-hashes against bb3e2e2.
- Recorded in plan-approval-log.md (row 1) and in the paper: Results run record, Reproducibility, and a new appendix "Amendments to the v0.6.0 run record". Every prefix and date is a generated macro.
- Re-gate: 3 findings passed the scorer (D1 85, D2+T2 82, T1 80); all fixed, plus most filtered ones. 1186 tests pass; lint clean; generator/render --check match; tectonic 0 overfull. Boundary commit ded9cfc, QGR in workstreams/perturb-seq-eval/qgr/.
- The QGR records the two submitter defects (Figshare would have republished 32086920 with the v0.6 files beside the v0.5 ones and the old metadata, and reported success; Zenodo state pointed at the locked v3 deposit). PublishedRecordError stays named in the publish.yml deposit sequence.

NEEDS A RULING (out of scope, left untouched): the code still writes and requires the field. That is provenance.py, the v05_preflight C-KEY-SOURCE check, and app_v05 _HOME_PROJECT, plus their test fixtures, the pyproject email and one CHANGELOG line. A re-run as documented re-creates the field; the appendix says so. Should I retire it in the code, or leave it?

Next: /pr-prep -> /sync -> /pr-submit for this branch (the path the principal chose). Then park.
next_handoff: CTO ruling on code retirement; deposit go from the principal
