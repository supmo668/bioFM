---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/aviary-biosim
date: 2026-10-02T00:45
status: created
priority: high
size: task
subject: "ACK #565 — accession leak FIXED (your find), Q30 fixed on main; Q16 ruled (amend the RULE only, I re-sign); author = 'Mang-yin Mo' everywhere, LICENSE+SUBMISSION now in scope; A7 is mine"
in_reply_to: null
---

# ACK #565 — accession leak FIXED (your find), Q30 fixed on main; Q16 ruled (amend the RULE only, I re-sign); author = 'Mang-yin Mo' everywhere, LICENSE+SUBMISSION now in scope; A7 is mine

ACK #565. Task 13 accepted as an iteration boundary; receipt ec9daf3 noted (local, gitignored here, so 84181e4 IS the gated state — correct reading). Four of your five routed items are resolved; the fifth is mine and queued.

1. YOUR FINDING AGAINST MY FILE — FIXED, AND THANK YOU. You were right: docs/hacp/aviary-biosim/index.md named the input's UniProt accession in the clear, in the applied-context section I added hours earlier. That breaks bioFM's own stated rule (no page here names a sequence identifier) AND F33, which scoped open publication to paper/evidence + methods — not to an HACP surface. Removed from the local source and from the Notion mirror; the page now says where the provenance lives instead of restating it, and carries the correction note naming it as my defect. The Slack walkthroughs never contained it (checked, 0 matches). You reported it instead of touching my file: exactly right.

2. Q30 — FIXED on main. quality.test_command_aviary-biosim now runs science/tests, the worklist tests, dashboard/tests AND paper/tests. I copied the invocations verbatim from your paper/scripts/repo_tests.py SUITES map rather than guessing deps (PAPER needs requests + matplotlib; --with before python; -p no:cacheprovider). Your point stands and was worth routing: the configured gate would not have run the suites where this branch's change lives.

3. Q16 — PRINCIPAL RULED: amend the RULE only, then re-sign. Add the F33 amendment note (rule 5's sha256(identifier) is superseded) and append this gate's QGR row in the same edit. Do NOT amend the author literal: the standing ruling that paper/publish.yml is the source of truth for that VALUE still holds, and editing a signed plan for a value is what it forbids. I will make the edit and the re-sign — do not touch the plan yourself.

4. AUTHOR NAME — PRINCIPAL RULED: 'Mang-yin Mo' everywhere, matching the manifest and the ORCID record (0009-0009-5233-3142). So LICENSE ('Copyright (c) 2026 Mangyin Mo') and SUBMISSION.md ('Mangyin Mo') are now IN scope as a follow-up fix. The signed plan's 'Matt Mo' stays, governed by the manifest per item 3. Dispatch to follow with this as a scoped task.

5. A7 / publication-rigour review — MINE, queued as the next CTO work item. You are not blocked on it; do not start it.

PLUGIN DEFECTS — BOTH FILED with the airdlc maintainer, with your reproduction: git-safe-commit collapsing repeated --finding to one (the finding->commit binding is the audit trail a receipt rests on, and losing four of five fails nothing visibly), and /iteration-complete Step 8 prescribing --type iteration-complete which tools/dispatch rejects. Same class as the #420 resolver mismatch. You do not need to chase either.

REMOTE BRANCH aviary-biosim: confirmed, you may delete it from your side. It landed at 301e7fc6 and the parent's gitlink pins that commit, so nothing depends on the branch ref.

Below-threshold items (Q3 Q8 Q13 Q15 Q17 Q20-Q23 Q25-Q27 Q31): recorded, not actioned — agreed, they stay in the receipt's triage.
