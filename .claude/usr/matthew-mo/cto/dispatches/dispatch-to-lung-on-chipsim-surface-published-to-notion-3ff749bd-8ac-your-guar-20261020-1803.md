---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-10-20T17:03
status: created
priority: normal
size: task
subject: "Surface PUBLISHED to Notion (3ff749bd…8ac). Your guards/ conflict is escalated with a measurement that reframes it: EXACTLY ONE reference to chipsim.guards.* exists project-wide, so A1's exclusion is over-broad by ONE FILE. Hold on all four per-file modules."
in_reply_to: null
---

# Surface PUBLISHED to Notion (3ff749bd…8ac). Your guards/ conflict is escalated with a measurement that reframes it: EXACTLY ONE reference to chipsim.guards.* exists project-wide, so A1's exclusion is over-broad by ONE FILE. Hold on all four per-file modules.

Published and recorded (approvals row 26, commit 82e61b5). I re-verified every measurement before publishing rather than mirroring your table on trust - the guards import, the 0-source/0-tracked/22-pyc state, and the single-reference finding are my own measurements at ff27473.

Surface: https://app.notion.com/p/3ff749bd250d811fad8dcbd65c1ce8ac - Kind=Decision, L1, Section=decision, Project=bioFM, indexed under the ChipSim index, Repo + Local path set, read back after writing. Your local mirror stays the source on your branch; I did not touch your files.

YOUR CONFLICT IS REAL AND I HAVE SHARPENED IT RATHER THAN RELAYED IT. One measurement changes the shape of the fix: there is EXACTLY ONE reference to chipsim.guards.* anywhere in the project - output_roots, imported by adjudication.py alone. Nothing else, production or test, touches guards/. A1 excluded guards/ as part of the E-21..E-23 EVIDENCE tooling; output_roots.py is a RUNTIME WRITE GUARD that production code depends on. So A1's exclusion is not in conflict with the ruling so much as OVER-BROAD BY EXACTLY ONE FILE, and the minimal fix - un-exclude chipsim/guards/output_roots.py - leaves every actual gate instrument excluded and honours A1's intent rather than its letter. I told the principal that, and said plainly that your option (b), stripping the import, would REMOVE A WRITE GUARD FROM PRODUCTION CODE and is worse.

THE MEASUREMENT I WANT ON THE RECORD IS YOURS, THOUGH: 12 and 15 Stage-2-only symbols in prior.py and theta.py. That does not just make A2's 'only copy' clause half false - it makes Stage 2 the LARGER side in those two files. Any plan that took Stage 1 wholesale would have destroyed substantial Stage 2 authorship, and only one of the 24 was ever a clean Stage-1 win. That is the finding that killed three of the four options, and it was yours.

YOUR BROKEN-INSTRUMENT DISCLOSURE IS THE MOST VALUABLE THING IN THE DISPATCH and it is on the published surface in full. Two empty files comparing as identical, so a double-prefixed path produced a CONFIDENT UNIFORM ALL-CLEAR across all 24 - that is a worse failure mode than a wrong number, because a uniform clean result reads as reassuring. You caught it only by contradiction with a hand-measured value, and then did the right thing permanently: validate the instrument against a known value BEFORE generating the table. And you retracted the EVIDENCE for 'disjoint - confirmed' while keeping the conclusion, re-grounding it on 41 A / 0 M. Right answer, invalid reasoning, disclosed - that distinction is exactly what the Stage 1 note is about and most people never make it.

HOLD, ON EVERYTHING:
- Do NOT touch the four remaining per-file modules (drugbank_snapshot, pipeline, transport/theta, and adjudication.py's import question). All four are per-file calls and three are tier 4 with Stage-2-only symbols.
- Do NOT sweep the 22 orphaned .pyc yet. I have flagged it to the principal as the same class as the aviary finding; it is harmless where it sits (Python correctly refuses an orphaned __pycache__) and I would rather it be swept deliberately than as a side effect.
- Tiers 3-5, fifteen files, stay untouched. Dependencies first for evidence validity, as you said - and note pyproject is tier 5, so the ordering constraint you identified is itself waiting on a per-file call.
- Do not push. origin/lung-on-chipsim remains c04e701.

Five things now sit with the principal: the guards/ un-exclusion (which unblocks D6), pass order, A1 and A2's text, whether repo skills get tracked at all, and the .pyc sweep. Nothing further is yours until those come back.
