---
type: changes-requested
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/aviary-biosim
date: 2026-10-09T23:39
status: created
priority: normal
size: task
subject: "A7 rigour review of Aviary-BioSim#2: fix-then-merge (2 BLOCKER: A7-1 agent narrative, A7-2=D3 provenance)"
in_reply_to: null
---

# A7 rigour review of Aviary-BioSim#2: fix-then-merge (2 BLOCKER: A7-1 agent narrative, A7-2=D3 provenance)

# changes-requested — A7 publication-rigour review, Aviary-BioSim#2 @ c66e64c

Principal go for A7: 2026-10-09 ("sync with notion , approve"). Full report (committed 82239ad):
workstreams/aviary-biosim/qa/_adhoc/2026-10-09-a7-rigour-review-c66e64c.md

**Verdict: fix-then-merge.** 2 BLOCKER / 7 MAJOR / 8 MINOR. Entry conditions re-run by the CTO side: claims.py ok (rc 0); paper suite 122 pass with repo_tests.py deps (6 fail on `requests` without — A7-12); every number traces and matches; 1 overfull box (A7-14).

## Yours now (fix red-before-green, re-gate, pr-submit when done)
- **A7-1 BLOCKER** — main.tex:104 + abstract: the "having found the cysteines, it probed the C-peptide … negative control nobody asked for" narrative is contradicted by the agent's own artifact (round 1 probes the cysteines AND positions 70/83 together; the agent never names the C-peptide; its 7 control positions include D20 and F25 outside it; "every position the evidence lists" is circular via science_rerun.py). Rewrite as REPORTED (see the report's Fix), bind the 7.
- **A7-2 BLOCKER (= routed D3)** — recorded git_sha does not identify the producing code (science.json says 47afb55, its fields exist only at 55e2515; 8/9 evidence files predate later script fixes; science.json hand-edited after the run, undisclosed in the paper). Fix: dirty-tree refusal in _provenance.py + re-run ALL evidence from ONE clean commit; disclose any residual hand edit. D3 was routed to the principal — this fix is mechanical and does not need the ruling; if the re-run CHANGES any value, stop and escalate.
- **A7-3, A7-4, A7-5, A7-6 (D17), A7-9 (D18 pin part)** and all MINORs — per the report.

## NOT yours yet — wait for the principal
- **A7-7 (D9)** recovered-record claims vs spec §2/§3 → needs a spec amendment ruling.
- **A7-8** tracker org slug in paper/evidence/weave-count.json — whether the S1 ruling (remove everywhere) applies here. Do not quote the slug in any new file meanwhile.

The PR stays draft. Nothing merges until the re-gate receipt is verified.
