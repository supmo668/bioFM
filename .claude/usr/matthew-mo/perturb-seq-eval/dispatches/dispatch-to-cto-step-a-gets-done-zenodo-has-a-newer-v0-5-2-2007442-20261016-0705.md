---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-10-16T06:05
status: created
priority: normal
size: task
subject: "Step (a) GETs done: Zenodo has a NEWER v0.5.2 (20074427) that no deposit file knows — relation + deny-list need a ruling; Figshare .v5 confirmed"
in_reply_to: null
---

# Step (a) GETs done: Zenodo has a NEWER v0.5.2 (20074427) that no deposit file knows — relation + deny-list need a ruling; Figshare .v5 confirmed

Step (a) DONE: read-only GETs, all GET, nothing written. Tokens came via the principal-supplied infisical prefix (names withheld, per #618); no value entered my context.

LIVE FACTS
Zenodo (concept 10.5281/zenodo.19716140), published versions, newest first:
- 20074427: v0.5.2, published 2026-05-07  <-- NEWEST, known to none of our deposit files
- 20060974: v0.5.1, 2026-05-06 (state done; files supplement.zip, v050_run_artifacts.zip, paper.pdf)
- 19748260: v0.5.0, 2026-04-24
- 19716141: v1, 2026-04-24
Figshare 32086920: public, latest version 5 (versions 1-5; files supplement.zip, v050_run_artifacts.zip, paper.pdf). The ".v5" relation is CORRECT (C7 settled).

DIFFERENCES FROM OUR FILES
1. Zenodo v0.5.2 (20074427) exists and is the latest v0.5.x.
   - publish.yml isNewVersionOf, the Zenodo notes and the Figshare references all name 20060974 (v0.5.1), which #577 called "v4, latest". It is not.
   - publish.state.json records only 19748260 (v0.5.0).
   - SUPERSEDED_RECORDS does not include 20074427, so the deny-list has a hole for exactly the newest published record.
   - The only trace in the repo is AND.md:156 ("releases 0.5.1/0.5.2 exist").
2. publish.state.json's zenodo.deposit_id (19748260) is two versions behind the live chain. It is a historical record and stays as written.

RECOMMENDATION (not done; your ruling):
- Add 20074427 to SUPERSEDED_RECORDS.
- Point isNewVersionOf at 10.5281/zenodo.20074427 (the latest v0.5.x). Optionally keep 20060974 as a second relation.
- Update the notes, references, tests and CITATION.cff to match.
- Normal gate.
- Then rebuild with build_deposit.py (the paper text changed since 357944b), and only then put the payload to the principal for the first write.

Question for the record: do we know what v0.5.2 changed? Nothing in the repo says, and the v0.6.0 corrections appendix cites the v0.5.0 record.
next_handoff: CTO ruling on the relation target + deny-list
