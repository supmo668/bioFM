---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-09-30T06:00
status: created
priority: high
size: task
subject: "DEPOSIT iteration CLOSED (db74e0f, receipt b2be4dd): run-vs-land provenance sentence (six paths, git-pinned) + overfull → 0 (tectonic); main merged; question: deposit-gate flow (second PR now vs after rigour items)"
in_reply_to: null
---

# DEPOSIT iteration CLOSED (db74e0f, receipt b2be4dd): run-vs-land provenance sentence (six paths, git-pinned) + overfull → 0 (tectonic); main merged; question: deposit-gate flow (second PR now vs after rigour items)

Agent: perturb-seq-eval. Re #526 (master-updated) — deposit-gate items 1 and 2 done; merged main first.

MERGE: origin/main (5a45d4a + your coord commits) merged at b106cb6 (worktree-sync; no conflicts; project files untouched by main; your move of the hacp page to workstreams/perturb-seq-eval/qa/_records/ arrived with it).

ITERATION DEPOSIT — CLOSED: boundary db74e0f (receipt workstreams/perturb-seq-eval/qgr/bioFM-matthew-mo-perturb-seq-eval-perturb-seq-eval-bioFM-qgr-iteration-complete-20260929-2259-b2be4dd.md; derived workstreams/perturb-seq-eval/qgr/bioFM-matthew-mo-perturb-seq-eval-perturb-seq-eval-bioFM-qgr-iteration-complete-20260929-2300-a94dcb8.md); QGR workstreams/perturb-seq-eval/qgr/qgr-deposit-v060-20260930T055925Z.md.
(1) Provenance sentence: in the Results run record (\S Run record) with a short pointer in Reproducibility. Facts come from a new data file paper/data/land_v060.json (run sha ce5f237, land sha 5a45d4a, PR 8, the changed paths) → macros \resLandSha \resLandPR \resPostRunPathCount; no hand-typed value. The named paths are the SIX src/scripts-modal files changed between ce5f237 and 5a45d4a — the gate caught that my first draft named five (openrouter_client.py's legacy docstring was missing); a test now pins the list to `git diff --name-only run..land -- src scripts/modal` and trips if anything under src/scripts-modal changes after the land. Wording: "revision at which v0.6.0 landed on main"; "code paths the run did not reach"; "reproduces every committed value of summary.json; the landed analyser adds one key, served_mismatch_count, equal to \resServedMismatch" — and that reproduction is now a test (analyser on the committed run files == summary.json except the added key = 0).
(2) Overfull: compiled with tectonic on a scratchpad copy (the binary at /opt/homebrew/bin is your install; I installed nothing) — 0 overfull boxes (9 at the land, 7 at my first draft), 0 undefined refs/citations, 0 font-shape warnings, 15 pages; 16 underfull = the 13 pre-existing (incl. the seven badness-10000 lines) + 3 mild ones from sloppypar. Means: \path for identifiers, \emergencystretch 1.5em in the preamble, sloppypar around the run record / pipeline list / backbone-scope paragraph, two rewords (MassGen hooks; CellForge result object), probe signature as display math. Nothing pre-registered touched (design reviewer verified).

Gate: 13 findings scored, 8 ≥ 80, all fixed (+3 filtered fixed); 1160 tests pass; lint clean.

STATE: local branch is 6 commits ahead of origin/perturb-seq-eval (d9d1328 payload, merge b106cb6, 8d5e955, f334a9c, 2654864, 41fc0dc, db74e0f + bookkeeping) — NOT pushed (/sync is principal-only). Question: for the deposit gate, do you want (a) a /pr-prep receipt over the new diff vs origin/main and a second PR (principal runs /sync + /pr-submit), or (b) the rigour-review items first, then one PR at the end? I hold until you say; monitor armed.
next_handoff: CTO -> perturb-seq-eval (deposit-gate flow + rigour-review items).
