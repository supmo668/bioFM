---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-11-24T23:10
status: created
priority: normal
size: task
subject: "PR #56 landed (07a5e57b): tag v0.6.0-a6 needed before the 0.6.2 dry run"
in_reply_to: null
---

# PR #56 landed (07a5e57b): tag v0.6.0-a6 needed before the 0.6.2 dry run

from: biofm/matthew-mo/perturb-seq-eval
priority: high
landed: PR #56 merged to main as 07a5e57b (Amendment 6 manuscript + 0.6.2 deposit preparation; approvals rows 39-41). CI green (pytest-x86_64, package, linkcheck). Gate record: workstreams/perturb-seq-eval/code-reviews/perturb-seq-eval-qg-20261124-amendment6-and-062-prep.md; receipt qgr pr-prep 20261124-2305 (hash E 2d7224a), verified by receipt-verify.
note: pr-merge 0.107.1 fails on macOS at pr-merge:286 (BSD sed rejects the hash_e script), so the merge used --no-receipt with that reason stated in the merge body. The receipt exists and verifies.
ask: (1) create the annotated tag v0.6.0-a6 on 07a5e57b — it marks the amendment, not a release; the 0.6.2 Zenodo notes name it, so it must exist before the dry run; (2) confirm the HACA-126 0.6.2 (b2b235f9) is held and whether it created any draft on Zenodo or Figshare; (3) after the deposit commit is fixed by build_deposit.py, tag v0.6.2 and run arxiv-package on it.
next here: build_deposit on clean main and the 0.6.2 dry run, once the tag exists. Publication waits for the principal's separate go.
