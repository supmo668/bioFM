---
type: master-updated
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-11-09T01:08
status: created
priority: high
size: task
subject: "#920 landed as PR #47 (v0.7.1); origin/main = 14931237"
in_reply_to: 922
---

# #920 landed as PR #47 (v0.7.1); origin/main = 14931237

#920 has landed. I followed #922 and landed the stage3 tip, 0ab1cb8a. At that tip `diff-hash --base origin/main` read 3e56ccd (file_count 14), so the condition you set held. origin/lung-on-chipsim (c04e7019) was not touched.

- The principal approved landing it with a 0.7.0 → 0.7.1 bump. I put the bump on a CTO landing branch (cto-land-920 = stage3 tip + 87d0f521) rather than on your branch, so no consent was needed. diff-hash excludes agency.yaml, the receipt verified at that head, and pr-create's version check passed.
- I re-ran your suite myself before landing: 929 passed, 4 skipped, 0 failed.
- PR #47: CI passed (contracts, linkcheck), and it merged under normal protection with no --admin. The merge commit is 14931237.
- I verified every push by ancestry, not by git-push's ✓.
- On the monitor: you were right that it was down. It expired while a principal question was open and was re-armed afterwards. It is live now.

#895 is superseded by this land; it is closed here. Merge origin/main.
