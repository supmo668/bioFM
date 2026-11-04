---
type: pr-submit
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-11-02T02:48
status: created
priority: normal
size: task
subject: "Ready for PR landing: perturb-seq-eval — cs.MA cross-list (row 12) + QG fixes; drafts moved to staging"
in_reply_to: null
---

# Ready for PR landing: perturb-seq-eval — cs.MA cross-list (row 12) + QG fixes; drafts moved to staging

branch: perturb-seq-eval
sha: 09f42d75a88a41965c6a089c4eb916f9cb7303c2
diff_hash: 03e8998 (full 03e8998… — code diff identical to the FRAMING.1 gate's 12d40b4; the delta is .claude/workstreams/perturb-seq-eval/context.json, phase-state only)
receipt: workstreams/perturb-seq-eval/qgr/bioFM-matthew-mo-perturb-seq-eval-perturb-seq-eval-bioFM-qgr-pr-prep-20261102-0247-03e8998.md (receipt-verify --require-pushed: ✓ at 09f42d7)
scope: FRAMING.1 — cs.MA cross-list beside q-bio.QM, primary cs.LG kept (approvals row 12, #848 item 2) + QG fixes F1/F2/F3/F5/F6/F12; the two unratified framing drafts moved OFF this branch to perturb-seq-eval-staging (235b116) per #842. Title, CITATION.cff, abstract, paper.tex, bib: UNTOUCHED (wait on the title pick).
draft: false
migrations_pending: none (migration-delta empty)
base: origin/main 5079a12 (merged; 0 behind)
files (7, code 4): projects/perturb-seq-eval/paper/arxiv.toml · paper/SUBMISSION.md · tests/test_agentic_lifecycle.py · scripts/arxiv_package.py (repo-level, outside my module — see F6) · .aiadlc/instincts/{2 hook bumps, committed as misc per trunk practice} · .claude/workstreams/perturb-seq-eval/context.json
quality_gate: 4 reviewers + scorer (threshold 80), 13 findings, 6 fixed in atomic --finding commits; lint ok · format ok · typecheck NOTSCOPED · tests 1088 passed / 13 skipped / 0 failed (module .venv built from pyproject; torch absent). Iteration receipt 12d40b4 at 3055506; pr-prep receipt 03e8998 at 09f42d7.
what_changed_beyond_the_ruling:
  - SUBMISSION.md: venue item now RULED (row 12), bioRxiv dropped; NEW item 3 "Title — PENDING, BLOCKS submission" (row 12 retitle + row 11 narrowing not yet in paper.tex); paste-ready block REGENERATED from arxiv_package.py metadata — it had carried the non-ASCII CFF abstract arXiv rejects (pre-existing drift) + a "regenerate, never patch" note.
  - scripts/arxiv_package.py: cross_list validation (list, archive.SUBJ ids, no dupes, not the primary) + 6 self-test cases; a bare string used to render "c, s, ., M, A" with exit 0. Repo-level; CI arxiv-package.yml runs self-test → still ALL CHECKS PROVEN LIVE.
  - tests/test_agentic_lifecycle.py: scGPT-alias test now encodes C-TORCH-2 (raise without torch); it was red in every torch-less env and no CI runs this suite.
deferred_below_threshold (for the devex/CTO lane): F7 self-test never exercises load_config's [categories]-last guard; F11 arxiv-package.yml interpolates a workflow_dispatch input into shell (contents:read, pre-existing).
cto_action:
  1. /pr-cto-triage → /pr-cto-land (version bump is yours).
  2. Note scripts/arxiv_package.py is outside my module — if you want F6 split out, /pr-split is cheap; it carries its own self-test.
  3. The staging ledger (perturb-seq-eval-staging @ 235b116) is independent of this PR and awaits the principal's title pick + row-11 ratification.
next_handoff: cto /pr-cto-land → master-updated (or changes-requested) to perturb-seq-eval
