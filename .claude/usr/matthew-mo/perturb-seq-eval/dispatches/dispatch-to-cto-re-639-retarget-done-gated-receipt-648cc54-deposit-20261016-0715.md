---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-10-16T06:15
status: created
priority: normal
size: task
subject: "Re #639: retarget done + gated (receipt 648cc54); deposit rebuilt at 75ec1c5; payload with the principal for the first write"
in_reply_to: null
---

# Re #639: retarget done + gated (receipt 648cc54); deposit rebuilt at 75ec1c5; payload with the principal for the first write

Re #639. Steps 1-4 done and gated: receipt 648cc54 (QGR qgr-rel552-*), boundary 75ec1c5, pushed.
- Deny-list: 20074427 added, test-proven.
- Single Zenodo parent: 10.5281/zenodo.20074427; the notes name the concept DOI; never 20060974.
- Figshare refs and CITATION follow. The gate's one PASS (D1, 90) is fixed: CITATION had said Figshare v5 = v0.5.1, but by md5 it matches v0.5.2.
- Gap declared in the CHANGELOG with README pointers. v0.5.2 is described only by its record (empty notes, v0.5.0 abstract) and the md5 comparison.

Rebuilt with build_deposit.py at 75ec1c5:
- paper.pdf: 0 overfull / 0 undefined;
- run artifacts: 5/5 SHA256SUMS OK; BUILD_INFO pins 75ec1c5;
- validate (no network): 5 files (paper.pdf, paper_build.log, v060_run_artifacts.zip, supplement.zip SUPERSEDED, v050_run_artifacts.zip SUPERSEDED).

The payload is now with the principal for the FIRST WRITE go. Nothing has been written to any venue.
next_handoff: principal's first-write go
