---
type: escalation
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-08-31T18:00
status: created
priority: normal
size: task
subject: "Iteration P0.1 complete on lung-on-chipsim — scaffold green; 5 human blockers + 5 plan defects need a CTO ruling"
in_reply_to: null
---

# Iteration P0.1 complete on lung-on-chipsim — scaffold green; 5 human blockers + 5 plan defects need a CTO ruling

event: iteration-complete (filed as 'escalation' — 'iteration-complete' is not in VALID_TYPES; this dispatch also carries five items that genuinely need your ruling)
workstream: lung-on-chipsim
iteration: P0.1
phase: P0 (Scaffold)
branch: lung-on-chipsim
commit_hash: 52d2f9b
diff_base: 10d98aa
files_changed: 55
qgr_receipt: workstreams/lung-on-chipsim/qgr/bioFM-matthew-mo-lung-on-chipsim-lung-on-chipsim-bioFM-qgr-iteration-complete-20260831-1059-0653839.md
plan_gate: verified green at 737a8d9 (unchanged)
emitted_at: 2026-08-31T10:59

summary: |
  All 11 scaffold tasks (S1-S11) complete. P0 gate PASSED: editable install +
  pytest --collect-only exit 0. Suite 106 passed / 5 skipped; ruff clean.
  Quality gate ran 4 reviewers + own review at threshold 80: 20 findings fixed,
  2 rejected as verifiably false, 1 deferred with rationale. Nothing deferred
  for convenience. Two of the plan's own done-conditions were UNTRUE or
  UNFALSIFIABLE as written and were made real rather than signed off.

blocked_on_human: |
  Five human blockers. Artifacts correctly ABSENT - nothing fabricated. No
  provenance file, commit SHA, UniProt ratification, roster entry or evidence
  DOI was invented.
    T2  pin the snapshot commit        -> gates T1, T4a  (~2 min)
    T1  ratify the licence posture     -> gates T11      (~5 min)
    T8  ratify the UniProt panel       -> gates T9       (~10 min)
    T18 curate the PoC compound roster -> gates T13      (~30-45 min)
    T14 adjudicate the P-gp labels     -> gates T15      (~60-90 min)
  Agent-side code and tests for each are built around them against committed
  fixtures, per Global Constraints / defect 33.

plan_defects_needing_cto_ruling: |
  E-1 BLOCKING T11 SIGN-OFF. T1/T11 say provenance.yaml has 'eight keys
      non-empty', but T2+T1 define NINE keys, and T2 requires
      commit_change_rationale to be EMPTY when source_commit == audited_commit.
      'All keys non-empty' is self-contradictory with T2's own interface.
      Implemented as: nine present, eight always non-empty, rationale non-empty
      IFF the commits differ. Needs your ratification.
  E-2 S3's done-condition is not achievable as worded: 'collect-only exits
      non-zero if testpaths is removed' is false - pytest's default
      norecursedirs skips .venv, so tests/ is collected either way (verified).
      Asserted against parsed config instead. Wording needs amending.
  E-3 S4 prescribes skip reason 'M0 slice 3 - splits/ODE' for test_monotonicity,
      which waits on the M1 ODE solver, not the slice-3 splits. Used the
      accurate reason.
  E-4 S7's probe set is INSUFFICIENT and it bit. Its two stated probes pass
      against a .gitignore that silently ignores data/raw/drugbank/
      provenance.yaml, PROVENANCE.md and SHA256SUMS.json - T1/T2's human
      artifacts and T4 done-condition (d). Needs extending to nested paths.
  E-5 The DVC remote resolves INSIDE the git worktree (plan-specified
      ../../.dvc-storage), so 'git worktree remove' destroys the only copy of
      the snapshot. Flagged rather than deviated from - your call.

top_quality_gate_catches: |
  F-01 data/raw/* excluded the data/raw/drugbank/ DIRECTORY; git cannot
       re-include a file beneath an excluded directory. This silently
       git-ignored T1/T2's provenance.yaml and T3/T4's SHA256SUMS.json.
  F-02 .dvc-storage/ was ignored nowhere. After a dvc push it holds
       DrugBank-derived bytes as extensionless md5 blobs that git add -A would
       vendor. T11's planned test_drugbank_not_vendored matches *.tsv and would
       not have caught it.
  F-03 The fixture-boundary test forbade exactly the artifacts T1/T2/T18 must
       produce - it would have gone red on the first human task to land.
  F-04 The same test had no positive control and went vacuous when a scanned
       tree was absent. It now carries five positive controls.

framework_friction: |
  /iteration-complete step 5 instructs the agent to append the QGR to the plan
  file. Doing so BREAKS tools/plan-gate, which hash-locks build-plan.md to the
  human approval signature. Verified: the append moved the hash 737a8d9 ->
  abd3ef4 and plan-gate exited 2. Reverted; report filed in
  plan/quality-gate-reports.md instead. Recommend amending the skill.

next_action: continue the remaining agent-side tasks (T3, T5, T5a, T5b, T6, T7,
  T9, T10, T11, T12, T13, T15, T16, T17, T19, S11a) against committed fixtures,
  leaving the five human artifacts absent.
next_handoff: cto ruling on E-1 (blocks T11 sign-off) + schedule the 5 human blockers
