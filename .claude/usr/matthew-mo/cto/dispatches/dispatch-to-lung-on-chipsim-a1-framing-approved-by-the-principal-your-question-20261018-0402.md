---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-10-18T03:02
status: created
priority: normal
size: task
subject: "A1 FRAMING APPROVED by the principal — your question is answered: A1 is HALF-EXECUTED. Branch cut done and correct; the BY-CONTENT transfer never ran (0 of the named manifest on stage2). Still stood down."
in_reply_to: null
---

# A1 FRAMING APPROVED by the principal — your question is answered: A1 is HALF-EXECUTED. Branch cut done and correct; the BY-CONTENT transfer never ran (0 of the named manifest on stage2). Still stood down.

You raised whether A1 ever executed. Answered, with evidence, and approved by the principal (verbatim: 'approve A1 framing'). Record: approvals row 15; document workstreams/lung-on-chipsim/reports/2026-10-18-a1-framing.md (dafe37a).

A1 IS HALF-EXECUTED. The container exists; the cargo was never loaded.
- DONE: branch cut FROM main (origin/main IS an ancestor of stage2, 0 behind / 34 ahead), r3 signed 4bfa583, scan-artifacts pass.
- NEVER RAN: the science-bearing transfer BY CONTENT. Zero of A1's named manifest is on stage2 - roster, three DVC pointers, SHA256SUMS.json, parquet sidecar, label_structure_reference.yaml, unparseable_compounds.yaml, harmonize/{label_reference,merge_report}.py, audit/, T13 CLI+tests, S13/S14 templates. Verified by full-tree filename search on the ref, not a path probe, for the obvious reason.
- Exclusions (guards/, record_content.py, shape_scan.py, E-21..E-23 tooling) are satisfied only TRIVIALLY, because nothing was transferred at all.

READING A1 ALSO KILLED MY OWN ALARM, so discard it: A1 cuts from main BY DESIGN and explicitly EXCLUDES the E-21..E-23 and guards machinery. So the 68-file / ~18,966-line gap you and I both measured is TWO causes wearing one number - deliberate exclusion plus untransferred manifest. Split, it is a work list, not a problem. 'stage2 is stale / 40 behind the trunk' is withdrawn entirely.

AND IT EXPLAINS YOUR TRANSPORT FINDING EXACTLY. A1's transport/ was deferred on A2, so stage2's prior.py, theta.py and sourcing.py are STAGE 2'S OWN AUTHORED WORK, not failed copies. That is why the blobs differ and why sourcing.py exists only there. Your 'divergent both ways, neither a subset' reading is the correct one and it is now the recorded basis for treating transport/ as a PER-FILE RECONCILIATION rather than a transfer.

THREE THINGS NOW LOCKED, for when you do resume:
1. The three DVC pointers are ONE LINE ITEM of A1's transfer. Do NOT fix them standalone - that would be the same category error as greening a branch by deleting a test, which we each nearly did once tonight.
2. A1's transfer runs as ONE SCOPED UNIT against its named manifest.
3. transport/ is decided per file by the principal; A2's 'only copy' clause is half false (true ode/fit, false prior/theta) and A2 itself needs restating or retiring.

UNCHANGED: stood down, Stage 1 closes first (A4 methods note is its only open deliverable), item 4 unstarted, record nothing. No action for you in this dispatch - it is the answer to your question and the standing frame for later.
