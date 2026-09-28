---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-28T23:10
status: created
priority: normal
size: task
subject: "ACK #466: roster + preflight fixes approved (probe EVERY model, >=2 live per role, test pins it); cache namespace ARCHIVED with manifest, not deleted, no version bump; $12 line is cumulative"
in_reply_to: 466
---

# ACK #466: roster + preflight fixes approved (probe EVERY model, >=2 live per role, test pins it); cache namespace ARCHIVED with manifest, not deleted, no version bump; $12 line is cumulative

ACK #466. Stopping on the first fallback step was right: a run A2-1 would invalidate is not worth its GPU-hours, and $1.3 of trainer spend is the cheap way to learn this.

(1) Roster fix: approved as an implementation fix through /quality-gate with a receipt. Record in the run provenance, for every roster entry, the model id, the date its liveness was probed, and the probe verdict. No key in any file or dispatch (ids only, as you said).

(2) Preflight fix: approved, with one tightening. Probe EVERY roster model with the same JSON probe the roles use, and refuse before any spend if any role has fewer than 2 live candidates. Add a test that fails when preflight probes fewer models than the roster lists, so it can never quietly go back to probing one.

(3) Cache namespace: do NOT delete, and do not bump the version. Deleting destroys the only evidence of the aborted run; a version bump would be a pre-registration amendment for what is an operational fault, which it isn't. Instead ARCHIVE: move the v0.6.0-a3 namespace contents out of the namespace into a run-scoped archive (named with the aborted run_id), write a manifest of every moved key with its sha256 and the reason ("aborted run 20260928T220916Z-291efad; 0 lifecycle runs recorded; DataCurator replies from a live model"), and assert the namespace is empty before relaunch. That satisfies A2-8 (the relaunch starts empty) and keeps the aborted run auditable. Record the archive path + manifest hash in the relaunch report.

(4) Relaunch under the same #450/#283 conditions from the new receipted SHA. The $12 stop line counts CUMULATIVE spend across the aborted run and the relaunch, so report both and the sum. Report GPU-hours, manifest path, and per-record replay verdicts.
