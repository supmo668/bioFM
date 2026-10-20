---
type: escalation
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-10-16T18:11
status: created
priority: normal
size: task
subject: "Figshare processing gate: still pending at window close, stopped"
in_reply_to: null
---

# Figshare processing gate: still pending at window close, stopped

Agent: perturb-seq-eval
Figshare processing gate: window closed with the file still pending. Nothing published.
Evidence (read-only GETs, 5-min interval, about 17:44-19:06): v060_run_artifacts.zip (file 70243092) stayed ic_success on every poll; the other 4 files are available; computed_md5 equals supplied_md5 (5b41a919...); preview_available.
Per your ruling #655 I stopped and did not publish either venue. Zenodo draft 23422745 and Figshare 32086920 v6 stay prepared and unpublished; v0.5.x untouched.
Options I am putting to the principal: (a) keep waiting and poll again later, (b) delete and re-upload that one file on the private v6 draft, then re-run the dry run, (c) ask Figshare support about the stuck ic_success state.
next_handoff: CTO ack; principal decision relayed back.
