---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-03T09:38
status: created
priority: high
size: task
subject: "r2.7 work order COMPLETE — receipt A 7c667b8 / B 60ddecb / C d2a4dce / E 478df8b; 4 escalations"
in_reply_to: null
---

# r2.7 work order COMPLETE — receipt A 7c667b8 / B 60ddecb / C d2a4dce / E 478df8b; 4 escalations

All five ordered items done, re-gated, receipt signed and verified.

PRECONDITIONS — verified by me, not taken from the dispatch
- Trunk merged. worktree-sync reported 'already up to date' but preflight still
  blocked: the signature commit a9c8629 was on LOCAL main only, not origin/main.
  Merged local main explicitly.
- plan-gate verify --workstream lung-on-chipsim -> exit 0 at bc61506. Run by me,
  four times across the session (before build, after each governance incident).

RECEIPT (standing format)
  Hash A  7c667b8ec3cf362714ddbf9ce218fdb6fd7a6cbc3b3dcdd92b911064594a683e
  Hash B  60ddecb26d5e8afc667c6f51f852add98ed5e1c2611d9d4812cb27343c6a2acf
  Hash C  d2a4dceed2e38731ba34bcfabd31d3d11f35117624a27a0e28a68c39bd8b3b6d
  Hash E  478df8b92492285867ed470ae9f50dbe56788ca8e575f3086983be3b30b0aa57
  Hash D = C (auto-approved; NO principal 1B1 in this session — stated in
  hash_d_source rather than borrowing a transcript that does not exist).
  A, B, C, E are DISTINCT and freshly computed this session — not recycled.
  B and C point at committed artifacts (qgr/findings-*.md, qgr/triage-*.md), so
  they are readable rather than hashes of vanished temp files.
  Receipt: workstreams/lung-on-chipsim/qgr/bioFM-matthew-mo-lung-on-chipsim-lung-on-chipsim-bioFM-qgr-pr-prep-20260903-0235-478df8b.md
  receipt-verify: PASSED. Branch NOT pushed and no PR opened — awaiting your word.

THE FIVE ITEMS
1. Config escape — refuses any config whose RESOLVED path leaves the root, and
   raises, never skips. Two further routes found and closed: rglob does not
   recurse into symlinked DIRECTORIES (so linked configs were silently invisible
   while open() still read them), and HARD LINKS bypass resolve() entirely.
2. argv[0] -> basename, argv[1:] verbatim. Your premise correction is recorded
   in the test comment that previously asserted the opposite.
3. Seed capture: config -> CHIPSIM_SEED override, record names which source won.
   Determinism test delivered — see escalation E-1 on 'scores'.
4. T7a TTY gate: refuses without a TTY, exit 2, writes no seal. Limit stated in
   four places and NOT inflated.
5. Diff/veto removed from the journal record rows, marked v3-only. The
   evaluator's own vetoes are a different concept and were left alone.

THE GATE DID REAL WORK — it was not a formality
30+ findings above threshold, ALL fixed, none deferred. The two that matter:
- HARD-LINK EXFILTRATION (conf 95). 'ln' with no -s reached exactly the
  exfiltration B1 closed for symlinks. Reproduced leaking a secret before the
  fix. Configs are now opened O_NOFOLLOW with st_nlink==1 + S_ISREG checks and
  copied from the DESCRIPTOR.
- A CONFIG ESCAPE DID NOT STOP THE RUN (conf 85). _journal_best_effort swallowed
  it, the stage ran, and the process EXITED 0 — so an attempted exfiltration and
  a clean run were indistinguishable by exit status, and under n8n/cron stderr is
  discarded. 'FAIL LOUDLY' has to mean non-zero; it does now.
Five findings were defects I introduced this iteration, including an exponential
symlink-diamond walk (12 levels -> 8,178 files in 5s) and a TOCTOU 'fix' whose
comment asserted a property the code did not have. That comment was worse than
the gap, because it stops the next reviewer looking.
Also cleared 88 test-authored panel-seal records from the LIVE Constraint (4)
audit trail — the TTY tests were journalling into the real project tree.

ESCALATIONS — four, none silently worked around
E-1 SCORES DO NOT EXIST. Item (3) asks for a test that two runs produce
    byte-identical SCORES. There are none: heads/ and uncertainty/ are empty and
    no build-plan task produces a score, so the literal PoC replay form is not
    executable. I built the strongest true form (byte-identical persisted ETL
    artifact, verified across processes under differing PYTHONHASHSEED, with a
    teeth test and a vacuity guard) and labelled it a STAND-IN. Nothing claims the
    PoC replay test is closed. Naming it 'the PoC form' would have been the exact
    defect S12 exists to fix. Needs your ruling on whether that satisfies (3).
E-2 THE B4 PROVENANCE BLOCK WAS LOST TWICE IN ONE HOUR, both times with
    plan-gate verify GREEN. First the 02:08 re-sign stripped all five disclosure
    fields wholesale; I restored it. Then commit 44b6ff9 corrected invoked_by to
    the worktree agent, and MY merge 7341b7a silently reverted that correction.
    Re-applied. Note my own restoration asserted invoked_by: cto, which was wrong
    — I restored the field without checking who actually invoked the signature.
    Two independent losses by two different mechanisms says the artifact has no
    mechanical protection, and the hash cannot supply it. I see you have already
    moved to restrict plan-gate sign (d4151eb).
E-3 POLICY QUESTION, not a defect. The boundary is the project root, and the root
    also holds .env and .venv. 'configs/x.yaml -> ../.env' resolves IN-root and is
    copied into the published record. That FOLLOWS your ruling as written, so I
    did not change it unilaterally. Restrict to files whose real parent is
    configs/, or state that in-root secrets are in scope for publication?
E-4 The TTY gate tests for a terminal but never READS from it, so any process
    inheriting a terminal passes it unattended — cheaper than allocating a pty and
    not currently on the model card. A one-line confirmation read would close it,
    but it changes the human's sealing UX, so I did not add it unilaterally.

PROCESS DEFECT, MINE: I used a blanket 'git add -A' and swept an external rewrite
of a governance artifact into an implementation commit (26b6780) under my
authorship, in a commit whose message did not mention it. I have stopped using
blanket adds and now stage explicit paths.

STATE: tree clean, 380 tests pass, ruff check + ruff format clean, gate green at
bc61506. Five human artifacts still absent, ratified: false, land blocked at
precondition 6 — unchanged and not something this work moves.

next_handoff: ruling on E-1 (does the stand-in satisfy item 3?) and E-3.
