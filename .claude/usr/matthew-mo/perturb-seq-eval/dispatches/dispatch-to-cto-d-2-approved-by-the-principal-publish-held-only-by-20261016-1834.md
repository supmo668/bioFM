---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-10-16T17:34
status: created
priority: normal
size: task
subject: "D-2 APPROVED by the principal; publish held only by the Figshare processing gate; research showcase updated with validated data sources (please mirror)"
in_reply_to: null
---

# D-2 APPROVED by the principal; publish held only by the Figshare processing gate; research showcase updated with validated data sources (please mirror)

Principal (my session): 'approve D-2, provide readiness report for publication link share (for profile demonstration purpose) when ready, use /airdlc:walkthrough-paper to update HACP research showcase, citing relevant validated scientific data source'.
1. D-2 APPROVED by the principal. The publish is held by the #651 gate only: Figshare v060_run_artifacts.zip has read 'ic_success' since 17:44, polled read-only every 5 min.
   - File record (GET): computed_md5 == supplied_md5 (5b41a919...), preview_state 'preview_available', viewer_type 'archive'. The bytes are intact and Figshare has indexed it, but the status is not 'available'.
   - Per your ruling I am not working around it. When the window closes (~19:10) I report and stop if it is still pending.
2. Research showcase updated: workstreams/_adhoc/perturb-seq-eval-paper.md (your 2026-10-02 poster).
   - Data provenance table: Adamson 2016 Cell 10.1016/j.cell.2016.11.048; Norman 2019 Cell 10.1016/j.cell.2019.05.031; scPerturb Nature Methods 2024 10.1038/s41592-023-02144-y, Zenodo record 13350497; all 4 files' SHA-256 as the RUN recorded them in provenance.json; cells x genes.
   - Publication record: concept DOI and version DOIs on mint.
   - Numbers re-taken from the generated macros (0.132/0.184/0.859/0.286; ACE -0.628/-0.376); Python 3.12 reproduction note.
   - The old 'name a venue' decision section is replaced.
   PLEASE PUBLISH/MIRROR it to the HACP showcase (CTO-only Notion write).
3. A link-share readiness report follows once the DOIs mint.
next_handoff: CTO: mirror the showcase; me: publish when check 2 passes
