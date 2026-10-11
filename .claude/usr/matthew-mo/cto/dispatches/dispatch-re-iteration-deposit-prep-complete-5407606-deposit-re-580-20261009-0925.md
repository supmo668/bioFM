---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-10-09T16:25
status: created
priority: normal
subject: "Re: Iteration DEPOSIT-PREP complete (5407606): deposit metadata generated/tested; submitters now refuse published records (figshare would have republished v0.5 metadata); S1 decision on llm_key_source in the DOI"
in_reply_to: 580
---

# Re: Iteration DEPOSIT-PREP complete (5407606): deposit metadata generated/tested; submitters now refuse published records (figshare would have republished v0.5 metadata); S1 decision on llm_key_source in the DOI

DEPOSIT-PREP ACCEPTED (5407606). Receipt noted, 1183 tests, lint clean, tectonic 0 overfull / 0 undefined, nothing submitted. Every item of #577 landed as directed, and two of your own additions are better than what I asked for.

PRINCIPAL RULINGS, both verbatim options taken 2026-10-08:

S1 -> "Remove it everywhere, amend the hash". So:
- Drop llm_key_source from the REPO copies as well as the staged ones. One single-valued record; do not leave the deposit and the repo holding two versions of the same run record.
- Re-derive the run manifest hash and record the change as a DATED AMENDMENT in the approval log and in the paper, the same way every other correction on this project is recorded. The published 323af965... becomes a superseded value with a row saying why; it does not get quietly replaced.
- Rationale to carry in the amendment: the field is not load-bearing for any claim -- a referee learns nothing about validity from a key's storage location -- and it named an organisation project slug, an environment, and a cross-project key practice that a DOI would make permanently citable. Provenance that costs more than it proves.
- If anything else in the run files carries the same class of value (an org slug, an internal env name, a cross-project flag), include it in the same sweep and name it in the amendment rather than doing a second pass later.

DEPOSIT -> "Hold for my explicit go". So: DO NOT run the deposit sequence. Build nothing to Zenodo or Figshare. The sequence in publish.yml is correct and stays armed and unused until the principal says go in a separate message, which I will relay. Keep the submitters' PublishedRecordError guard in place -- it is now load-bearing.

THE TWO SUBMITTER DEFECTS ARE THE MOST VALUABLE THING IN THIS ITERATION, and I want them stated where a referee can see them, not only in a receipt:
- Figshare would have uploaded the v0.6 files BESIDE the v0.5 ones in the published article AND republished it carrying the old description and the old author name, because metadata is only sent when creating a new article. That is a silent wrong-publication, not an error -- the API would have returned success.
- Zenodo's state pointed at a published deposit with a locked bucket.
Both are the fleet's recurring shape -- a mechanism reporting success while the property it exists to guarantee is absent -- and they were found in the step AFTER the one everybody checks. Add a short paragraph on them to the deposit QGR, and keep PublishedRecordError named in publish.yml's comments so the next person cannot un-learn it.

YOUR SHARP CALLS, kept as-is: the VERSIONED figshare DOI for isNewVersionOf (the unversioned one resolves to latest, which after deposit is the new record -- a self-reference you avoided); and flipping isSupplementTo to isSupplementedBy pinned to the run sha tree, which fixes a relation that was pointing the wrong way.

VERSION FIELDS: not mine. framework.version is the only version I single-write. CITATION's version tracks the deposit, so 0.6.0 with the date set at deposit time is right and stays yours.

NEXT: apply S1 as an amendment, re-gate, and report. Then park -- the deposit waits on the principal.
