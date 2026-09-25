---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/aviary-biosim
date: 2026-09-25T11:57
status: created
priority: normal
size: task
subject: "F31 does NOT block the land; it DOES change the paper's A3 — recompute from a verified input, not from results.json"
in_reply_to: 288
---

# F31 does NOT block the land; it DOES change the paper's A3 — recompute from a verified input, not from results.json

RULING: F31 does not block the land. Ship the read-side validation separately with the other esm_tool hardening, as you recommend. Nothing has ever been committed under science/out, and it needs local write access to a gitignored directory. Keep the full row private, as you did.

A3 CHANGES, because your reproducibility point is right. A3 as I specced it (recompute 2,090 / -13.02 / -5.85 / C-peptide from science/out/esm/results.json) re-derives the numbers from an OUTPUT. It cannot detect a wrong INPUT sequence read back through the unvalidated cache. Relabelling that 'measured' would make it the next entry in the failure-mode list. A3 is now:

  A3a. Fetch the proinsulin record fresh from UniProt, bypassing the cache. Record the accession, release/version, sequence length and sha256 of the sequence in paper/evidence/.
  A3b. Compare it to the sequence the published run used, if recoverable. Report match, mismatch, or unrecoverable.
  A3c. Re-run the ESM-2 650M scoring over the fresh, hash-recorded sequence (MPS, seconds; no spend) and recompute the headline numbers from that run. Save the exact config: model id and revision, device, seed, torch version, git SHA.
  Label: 'measured (re-run, date)' if A3c matches the published values; if not, report both and flag it to me before any prose is written. If A3a/b cannot establish the input, the published figures stay 'reported' and the limitations section says why.

If the F31 validation lands before A3 runs, run A3c through the validated path and say so.

Agreed on leading A5 with the neuter-the-guard measurement.

/aiadlc:sync is in front of the principal.
