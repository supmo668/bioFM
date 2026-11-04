---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-11-02T02:40
status: created
priority: normal
size: task
subject: "Iteration FRAMING.1 complete on perturb-seq-eval — cs.MA cross-list (row 12) gated; pr-prep → pr-submit next"
in_reply_to: null
---

# Iteration FRAMING.1 complete on perturb-seq-eval — cs.MA cross-list (row 12) gated; pr-prep → pr-submit next

event: iteration-complete
workstream: perturb-seq-eval
iteration: FRAMING.1
phase: FRAMING (paper framing under approvals rows 11-12; not a plan phase)
branch: perturb-seq-eval
commit_hash: 3055506
diff_base: e3a3a1f
hash_a: ab4080a7d0b3b685eb01c1676764da2b5d1f2d3d729c570bbc182e2c65b801f6
hash_e: 12d40b48a5d8c345f5ecc07f8c3452bc00d13c83b20e0eab27023e44cf718d4a
files_changed: 6 — projects/perturb-seq-eval/paper/arxiv.toml, projects/perturb-seq-eval/paper/SUBMISSION.md, projects/perturb-seq-eval/tests/test_agentic_lifecycle.py, scripts/arxiv_package.py, .aiadlc/instincts/{2 hook-written reinforcement files, committed separately as the trunk does}
qgr_receipt: workstreams/perturb-seq-eval/qgr/bioFM-matthew-mo-perturb-seq-eval-perturb-seq-eval-bioFM-qgr-iteration-complete-20261102-0238-12d40b4.md
summary: |
  #848 item 2 applied: arxiv.toml cross_list = ["q-bio.QM", "cs.MA"], primary cs.LG kept, [categories] still last. QG (4 reviewers + scorer, threshold 80) found the diff itself clean but fixed six survivors in atomic commits:
  F1/F3/F5 (design) — SUBMISSION.md listed the venue as an open "arXiv or bioRxiv? Exactly one." after it was ruled; now RULED (row 12), bioRxiv dropped, and a new item 3 "Title — PENDING, BLOCKS submission" records that the retitle (row 12) and the paper.tex narrowing (row 11) must land before anyone pastes Part 2. arxiv.toml comment now says task-difficulty signal (row 11), not compute-allocation.
  F2 (design, 92) — the paste-ready metadata block was the non-ASCII CFF abstract (arXiv rejects it) with one hand-patched line; regenerated wholesale from arxiv_package.py metadata (byte-identical) + "regenerate, never patch" note.
  F6 (test, 80) — scripts/arxiv_package.py: cross_list had no shape check (bare string → "c, s, ., M, A", exit 0; non-string → crash). Added validation + 6 planted self-test cases, red→green. Repo-level script — flagging it since it is outside my module.
  F12 (own, 90) — tests/test_agentic_lifecycle.py accepted 'linear' for the scGPT alias; C-TORCH-2 (3f52e6f) raises when torch is absent, so the configured test command was RED in this fresh torch-less worktree (no CI runs this suite). Test now encodes C-TORCH-2. Pre-existing; no .py in the ruling's diff.
  Checks (fresh, .venv built from pyproject): lint ok · format ok · typecheck NOTSCOPED · tests 1088 passed / 13 skipped / 0 failed. Deferred <80: F7 (self-test for the [categories]-last guard), F11 (arxiv-package.yml interpolates a workflow_dispatch input into shell; contents:read) — devex/CTO lane.
  docs-ticket-align: ALIGNED 0 (no ticket; no docs/usage/perturb-seq-eval.md) — warn at this boundary, inherits to /phase-complete.
next_handoff: perturb-seq-eval /pr-prep → /sync → /pr-submit (scope: cs.MA cross-list + QG fixes; title/CFF/abstract untouched) → cto /pr-cto-land
emitted_at: 2026-11-02T02:40
