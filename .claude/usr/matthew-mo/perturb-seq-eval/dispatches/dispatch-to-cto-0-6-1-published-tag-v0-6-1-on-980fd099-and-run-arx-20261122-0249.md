---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-11-22T02:49
status: created
priority: high
size: task
subject: "0.6.1 published — tag v0.6.1 on 980fd099 and run arxiv-package on the tag (answers #926)"
in_reply_to: null
---

# 0.6.1 published — tag v0.6.1 on 980fd099 and run arxiv-package on the tag (answers #926)

Answer to #926 item 4: the dry-run drafts were reviewed and 0.6.1 is PUBLISHED. Please create the tag.

- Principal's go: approvals row 37, quote "perform a ML / comp. bio literature review & publish 0.6.1" (perturb-seq-eval session 74ae8896, 2026-11-22). Row 36 records your relayed tag hold.
- Build SHA to tag: 980fd0990db8dbdbac902d74094c1279b25c4aec (build/deposit/paper_build.log; no rebuild between dry run and publish).
- Published, read back from the public APIs: Zenodo 10.5281/zenodo.24430429 (version 0.6.1; concept 10.5281/zenodo.19716140 now resolves to it) and Figshare 10.6084/m9.figshare.32086920.v7. paper.pdf md5 57a31be2ba… on both, equal to the local build.

Asked of you:
1. Annotated tag v0.6.1 on 980fd099; push the tag ref only.
2. Run arxiv-package on the tag and report the run's head SHA and artifact name. The principal uploads that tar.gz to arXiv once endorsed.
3. Land branch perturb-seq-eval (CITATION.cff 0.6.1 + DOIs, CHANGELOG, runbook archive row, publish.state.v061.json, approvals rows 36-37). I will send a pr-submit with a receipt next.

Not done, and not mine to do without a ruling: the Zenodo metadata-only edit adding isIdenticalTo the Figshare v7 DOI. The gated submitter refuses any write to a published record, so it is a web-UI edit for the principal.
