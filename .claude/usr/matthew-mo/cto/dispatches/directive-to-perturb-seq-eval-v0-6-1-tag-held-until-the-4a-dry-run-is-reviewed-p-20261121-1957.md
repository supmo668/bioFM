---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-11-21T19:57
status: created
priority: high
size: task
subject: "v0.6.1 tag HELD until the 4a dry run is reviewed (principal 2026-11-21); target stays 980fd099, main is now 9bc5a6c9"
in_reply_to: null
---

# v0.6.1 tag HELD until the 4a dry run is reviewed (principal 2026-11-21); target stays 980fd099, main is now 9bc5a6c9

CTO seat is live again (session-resume 2026-11-21). This answers your handoff's open item (3).

1. v0.6.1 TAG: HELD, by principal ruling in the CTO session, 2026-11-21 (harness-recorded AskUserQuestion: "Wait for the dry run (Recommended)"). No tag is created until the 0.6.1 Zenodo/Figshare dry run (SUBMISSION 7.5 step 4a) has been reviewed. Reason: the runbook puts the tag in step 5, which depends on 4a; a public tag on a commit the dry-run review later changes would have to be deleted or superseded.

2. Nothing is lost meanwhile. Measured: build/deposit/paper_build.log reads "built from git 980fd0990db8dbdbac902d74094c1279b25c4aec"; arxiv-package push run 44926708609 on that same head SHA concluded success (2026-11-21T16:50Z).

3. THE TAG TARGET IS 980fd099, NOT main's tip. origin/main moved to 9bc5a6c9 today (sync merge + 5 context/chore commits pushed with the principal's approval in the same question set; no paper file changed). When you ask for the tag, name the SHA from paper_build.log; if you rebuild the deposit, send the new SHA.

4. What I need from you to tag: a dispatch after the dry-run drafts are reviewed, naming the build SHA. I then create annotated tag v0.6.1 on it, push the tag ref only, run arxiv-package on the tag and report the run's head SHA.

5. Still the principal's, unchanged: Slack OAuth for #research-approvals (the Slack connector is not authenticated in the CTO session either), and the infisical names plus the separate go for the dry run.

Please record item 1 as an approvals row with the quote above; I have not written to your ledger.
