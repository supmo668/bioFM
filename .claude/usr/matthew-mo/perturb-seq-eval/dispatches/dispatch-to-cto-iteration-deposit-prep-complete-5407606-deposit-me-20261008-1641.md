---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-10-08T23:41
status: created
priority: high
size: task
subject: "Iteration DEPOSIT-PREP complete (5407606): deposit metadata generated/tested; submitters now refuse published records (figshare would have republished v0.5 metadata); S1 decision on llm_key_source in the DOI"
in_reply_to: null
---

# Iteration DEPOSIT-PREP complete (5407606): deposit metadata generated/tested; submitters now refuse published records (figshare would have republished v0.5 metadata); S1 decision on llm_key_source in the DOI

Agent: perturb-seq-eval. Re #577. event: iteration-complete. DEPOSIT-PREP closed — boundary 5407606, receipt workstreams/perturb-seq-eval/qgr/bioFM-matthew-mo-perturb-seq-eval-perturb-seq-eval-bioFM-qgr-iteration-complete-20261008-1640-47ebb3f.md, QGR workstreams/perturb-seq-eval/qgr/qgr-deposit-prep-20261008T234042Z.md. Prep only; nothing submitted.

(a) Description: scripts/paper/render_publish_description.py renders the manuscript abstract with generated values into publish.yml description AND CITATION.cff abstract (--check is a test). Method sentence = the abstract's "pinned roster ... Haiku 4.5 for the four proposer roles, Sonnet 5.5 for the Validator ... served model recorded and asserted per call", tested against provenance (roster, per-role served models, 0 mismatches, 0 fallback steps); gate sentence tested against summary.json. "best-of-54" is gone (abstract says 27 records per task).
(b) Files: scripts/publish/build_deposit.py — refuses a dirty tree, builds paper.pdf with tectonic and keeps the log (git sha recorded) as paper_build.log; stages v060_run_artifacts (4 run files + manifest + SHA256SUMS + BUILD_INFO); v0.5.0 entry labelled SUPERSEDED; supplement.zip (v0.5-era docs) also labelled SUPERSEDED.
(c) Related identifiers: isNewVersionOf 10.5281/zenodo.20060974 (v4, latest under the concept DOI) and 10.6084/m9.figshare.32086920.v5 — the VERSIONED figshare DOI, because the unversioned one resolves to the latest version, which after deposit would be the new record itself. Repo link: isSupplementedBy, pinned to the run sha tree (ce5f237/projects/perturb-seq-eval); the old isSupplementTo said the deposit supplements the repo.
(d) A1 version cell: em dash with a dagger note in the caption.
(e) creators "Mo, Mang-yin"; paper.tex "Mang-yin Mo"; CITATION given-names "Mang-yin"; ORCID unchanged.

Gate found two submitter defects that would have mattered at deposit time: Figshare would have uploaded the v0.6 files BESIDE the v0.5 ones in the published article 32086920 and republished it with the old description and author name (metadata is only sent when creating a new article); Zenodo state points at a published deposit (v3 19748260) whose bucket is locked. Both submitters now refuse a published record (PublishedRecordError, reported per venue), and publish.yml carries the deposit-time sequence: build_deposit.py → Zenodo actions/newversion on 20060974 → Figshare metadata update + replace files → CITATION date-released + new DOIs → principal approves publish. Keywords now only terms the manuscript uses (dropped "Bayesian optimization", "contextual bandit"); CITATION version 0.6.0 (date at deposit) — flagging in case version fields are yours.

DECISION FOR YOU/PRINCIPAL (S1, not blocking prep): the run files in v060_run_artifacts carry llm_key_source {store infisical, project_slug syntropyhealth-app, env dev, cross_project true} (no secret). Already public in the repo; a DOI makes it permanent. Options: publish as provenance, or redact the staged copies (breaks byte-identity with the committed run and the manifest hash 323af965…).

1183 tests pass; lint clean; tectonic 0 overfull / 0 undefined.
next_handoff: CTO -> principal (deposit approval + S1), then CTO -> perturb-seq-eval (run the deposit sequence, or changes).
