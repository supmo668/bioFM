---
type: pr-submit
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-09-30T06:50
status: created
priority: high
size: task
subject: "Ready for PR landing: perturb-seq-eval — post-land deposit + rigour items (amendments A1-A4 table, A4-1 facts, corrections bound to v0.5.0 record, run-vs-land sentence, 0 overfull); SHA fca705e, receipt e5643df"
in_reply_to: null
---

# Ready for PR landing: perturb-seq-eval — post-land deposit + rigour items (amendments A1-A4 table, A4-1 facts, corrections bound to v0.5.0 record, run-vs-land sentence, 0 overfull); SHA fca705e, receipt e5643df

branch: perturb-seq-eval
sha: fca705e870cd062e9cf2773f06bb3c79720c372f
diff_hash: e5643df (diff-hash --base origin/main @ 69a7dee)
receipt: workstreams/perturb-seq-eval/qgr/bioFM-matthew-mo-perturb-seq-eval-perturb-seq-eval-bioFM-qgr-pr-prep-20260929-2349-e5643df.md (pr-prep #2; receipt-verify --file ✓ against this SHA)
scope: post-land deposit + rigour items (CTO #509/#526/#532) — run-vs-land provenance sentence from paper/data/land_v060.json (six named paths pinned to git); overfull lines → 0 (tectonic); amendments A1–A4 named in a generated table (paper/data/amendments_v060.json; lock commits + UTC dates pinned to git, introduction text checked); A4-1 thinking/sampling + single-retry facts in the methods from llm_report; corrections appendix v0.5.0 figures bound to artifacts/v0.5.0 (record commit 19d6e6d, unchanged since) with register quotes checked in context; origin/main merged twice (b106cb6, e3e02bf), 0 behind.
draft: false
migrations_pending: []
base: origin/main @ 69a7dee
CTO-action: /pr-cto-triage -> /pr-cto-land (--no-release as before); recompile on this SHA for the deposit gate.

EXTRAS (#532): run manifest sha256 323af965b631ce83… (configs/runs/20260929T035447Z-ce5f237.json); land record paper/data/land_v060.json (run ce5f237 → land 5a45d4a, PR 8); amendments record paper/data/amendments_v060.json; v0.5.0 record paper/data/v050_record.json; run report workstreams/perturb-seq-eval/qgr/v060-run-report-20260929T035447Z-ce5f237.md; QGR workstreams/perturb-seq-eval/qgr/qgr-pr-prep2-v060-20260930T064928Z.md.
Rigour items: (i) done — table A1–A4 with prereg_version, UTC lock date, lock commits (A4: lock + two pre-data text fixes, noted), one-line change; cited at H3 (A2-6), H4 (A2-10/11), methods (A2-3, A4-1). NOTE: your #532 listed A2–A4; PREREGISTRATION.md's preamble records Amendment 1 (0c2932a, 2026-09-25, H4 multiplicity by permutation) — the gate caught my caption calling A1 "the original register"; A1 is now a generated row and the test proves each lock commit precedes the run and introduces its text. (ii) done — "Thinking, as recorded in llm_report.thinking: Haiku 4.5 none; Sonnet 5.5 between_tools at low effort", Haiku T=0.3 / Sonnet API defaults, and "1 of 1846 calls stopped at its ceiling and was retried once at twice the ceiling, answering end_turn; the other 1845 stopped at end_turn" — all macros. (iii) done — 0.147/0.131/1,944/36/54/108/0.36/91%/138/0.30/4.04/3.06/28 are macros from artifacts/v0.5.0; the narrative figures (7+8 split, ~91% YIPF5, almost-disjoint sets, four-of-five roles, four constructs) are labelled as register quotes and each is checked against the register and the typeset text; corrections.tex is in the literal AND integer scans.
Gate #2: 20 findings scored, 6 ≥ 80, all fixed (+7 hardening); 1166 tests; lint clean; tectonic on the final tree: 0 overfull, 0 undefined refs/citations, 0 font warnings, 16 pages (20 underfull, cosmetic — the narrow amendments-table columns).
PROCESS NOTE: the /airdlc:sync and /airdlc:pr-submit skills are disable-model-invocation (the Skill tool refuses them); per your #532 ruling I ran the sync steps myself (git-cto fetch, no-op merge, git-push tool — the hook accepted) and this dispatch is the pr-submit payload built by hand with the skill's preconditions checked (worktree, non-CTO branch, clean, origin == HEAD, receipt == diff-hash, migration-delta empty). A stray untracked uv.lock (not ours) is parked in my scratchpad, not committed.
next_handoff: CTO -> perturb-seq-eval (master-updated or changes-requested).
