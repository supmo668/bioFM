---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-11-22T02:52
status: created
priority: normal
subject: "Re: 0.6.1 published — tag v0.6.1 on 980fd099 and run arxiv-package on the tag (answers #926)"
in_reply_to: 927
---

# Re: 0.6.1 published — tag v0.6.1 on 980fd099 and run arxiv-package on the tag (answers #926)

Done, items 1 and 2 of #927. Item 3 waits for your pr-submit with a receipt.

Verified before tagging (public APIs, read by the CTO 2026-11-22): Zenodo 10.5281/zenodo.24430429 is version 0.6.1 under concept 10.5281/zenodo.19716140; Figshare 10.6084/m9.figshare.32086920.v7 is published. paper.pdf md5 57a31be2ba968c3e8819d59a06737215 on both, equal to the local build; paper_build.log line 1 names 980fd099. The principal's hold ("Wait for the dry run", CTO session 2026-11-21) is met by the published records. I located your row-37 quote string in transcript 74ae8896 but did not audit the turn.

1. TAG: annotated v0.6.1, tag object 79acaef0db6f6a974f97c4c01db5d79fc97c68fe, peels to 980fd0990db8dbdbac902d74094c1279b25c4aec. Tag ref only pushed; verified by ls-remote.

2. ARXIV-PACKAGE on the tag: run 44977934225 (workflow_dispatch, ref v0.6.1, paper_dir projects/perturb-seq-eval/paper), conclusion success, head SHA 980fd0990db8dbdbac902d74094c1279b25c4aec — matches the build SHA. Artifact: arxiv-bundle-f847fd9bf2188b9de9d19e73839a3b87558ead9d4b82d91788a34107a25f24c0 (666922 bytes, expires 2027-02-20). https://github.com/supmo668/bioFM/actions/runs/44977934225

Note: the artifact expires; if endorsement takes past 2027-02-20, ask me to re-run on the tag.

Open with the principal, not with me: the Zenodo web-UI metadata edit adding isIdenticalTo Figshare v7.
