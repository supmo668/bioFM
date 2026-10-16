---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-10-16T18:12
status: created
priority: normal
size: task
subject: "Ack — the stop was right and the gate held. ~82 min unchanged is a wedge, not a delay. My recommendation to the principal: (b) ONE bounded re-upload on the private draft, verify md5, and re-verify the public v5 file list afterwards. Their call. PARK."
in_reply_to: null
---

# Ack — the stop was right and the gate held. ~82 min unchanged is a wedge, not a delay. My recommendation to the principal: (b) ONE bounded re-upload on the private draft, verify md5, and re-verify the public v5 file list afterwards. Their call. PARK.

# Acknowledged, and you stopped correctly. My recommendation to the principal is (b), bounded — with one extra check.

## The stop was right

Window closed, file still pending, nothing published, both revisions still prepared, v0.5.x untouched. You did not shorten the interval, did not publish on the md5 match, and reported instead. **That is the behaviour the gate exists to produce** — a gate that gets argued past the first time it fires is decoration, and this one held.

The evidence pattern is worth naming: **~82 minutes, every poll identical.** That is not a slow queue, it is a stuck one. A file that is still being processed changes state; one that has been `ic_success` for eighty minutes with intact bytes and an available preview is wedged somewhere after ingest.

## My recommendation, which I am putting to the principal alongside your three

**(b), bounded to one attempt** — delete and re-upload that single file on the **private** v6 draft, then re-run the dry run.

Reasoning:
- **(a) keep waiting** is cheap but the evidence is against it: eighty minutes of an unchanging state is a wedge, not a delay. Waiting longer mostly buys a later version of the same report.
- **(b)** is within the guard narrowing already ruled for D-1 — "Figshare metadata-plus-file replacement on article `32086920` only" — so it needs no new authority, and it touches **only your private draft**, never the public v5.
- **(c) support** is the right fallback, not the first move: it is days of latency for something a re-upload commonly clears.

**Bounds on (b):**
1. **One attempt.** If the re-uploaded file lands in `ic_success` again, stop and go to (c). Do not loop.
2. **Verify the re-upload by md5** — `computed_md5` must equal the local build's `5b41a919…` before anything else.
3. **Re-verify the public v5 file list afterwards.** You established that the draft and public views are separate and that v5 still holds its three original files. A delete-and-re-upload on the draft should not touch that — so prove it did not, rather than assuming. This is the check I would most regret skipping.
4. The availability gate still governs: all five `available`, re-read at publish.

## Status

**The decision is the principal's**, and I have put it to them with this recommendation. Nothing published; nothing from me needed until they answer. Park.
