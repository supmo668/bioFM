---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-10-15T14:31
status: created
priority: normal
size: task
subject: "Re #620: deposit replanned as NEW STANDALONE records + gated (receipt 1b563e1); create/publish mechanically two gos; runbook + Py>=3.12 reproducibility for you; nothing sent"
in_reply_to: null
---

# Re #620: deposit replanned as NEW STANDALONE records + gated (receipt 1b563e1); create/publish mechanically two gos; runbook + Py>=3.12 reproducibility for you; nothing sent

Re #620. Deposit replanned for NEW STANDALONE records and gated. NOTHING sent to any venue: no writes and no reads; step (a) is still waiting on the principal's Infisical login.

Branch perturb-seq-eval @ e00a478b8fdcc4efdabf97fe2573dddf0fea86e2 (fresh from origin/main 357944b; pushed). Receipt 1b563e1: workstreams/perturb-seq-eval/qgr/bioFM-matthew-mo-perturb-seq-eval-perturb-seq-eval-bioFM-qgr-iteration-complete-20261015-1530-1b563e1.md. QGR qgr-standalone-*.

What changed (scripts/publish/submit_to_venues.py, publish.yml, tests):
- Own state file per release: publish.yml state_file publish.state.v060.json, anchored to publish.yml's dir (contained, no symlink) and printed at start. publish.state.json stays the v0.5.x record and is never written.
- Lineage: isNewVersionOf relations, a Zenodo "notes" field and Figshare "references". Both fields are checked against the venues' public API docs. The notes say why the version chain breaks.
- Guards:
  - PublishedRecordError as before, plus a hard deny-list of superseded ids on Zenodo, Figshare and OSF, applied even if a state file is hand-seeded.
  - DraftRequiredError: a publish run with no recorded draft is refused before any write, so create and publish can never happen in one run. That enforces your "two gos" mechanically.
  - DraftMismatchError: refuses a same-name file whose content changed since the draft was created.
  - Resume re-sends Figshare metadata and reuses the reserved DOI. Zips are byte-reproducible.
- Deposit-time sequence rewritten:
  - no newversion, no edit, no deletion;
  - step 2 = read-only GETs;
  - step 3 = first write (--dry-run creates the drafts), then commit the v060 state;
  - step 4 = separate publish go.

Gate: code, security and test reviewers plus the scorer. 3 passed:
- C1: runbook, header and docstring. Header and docstring fixed; the runbook goes to you, see below.
- C4/S1/T6: state path relative to cwd. Fixed.
- T1: main() untested. Fixed with a real main() harness.
12 of the 15 filtered findings were also fixed. Each key regression was mutation-checked and fails a test. 1187 tests pass on the committed HEAD; lint and the generated-file checks are clean.

FOR YOU:
(1) research/PUBLISHING_RUNBOOK.md §6 (~466-532; also 313, 347, 581, 592, 600) still scripts Zenodo newversion on publish.state.json's deposit_id, Figshare delete+replace in article 32086920, and an OSF delete+re-upload, all forbidden now. It's outside my module, so please update or retire that section.
(2) The analyser reproduces summary.json bit-for-bit only on Python >= 3.12: 3.12 made float sum() compensated, and on 3.11 one entropy value differs in the last bit. The paper's "the landed analyser ... reproduces every committed value" is true but needs Python >= 3.12. Recording that is your call. My test venv was rebuilt on 3.12 with the principal's approval.
(3) C7: the relation 10.6084/m9.figshare.32086920.v5 is unconfirmed. Step (a)'s GETs will settle it before any write.

Next, unchanged: step (a) once the principal logs in to Infisical. The prefix names come from them out of band and never go into a dispatch. Then the payload goes to the principal for the first write.
next_handoff: CTO: runbook + reproducibility note; principal: Infisical login for step (a)
