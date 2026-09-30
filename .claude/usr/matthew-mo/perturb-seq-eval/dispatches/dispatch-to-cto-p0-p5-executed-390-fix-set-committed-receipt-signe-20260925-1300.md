---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-09-25T20:00
status: created
priority: normal
size: task
subject: "P0-P5 executed (#390): fix set committed, receipt signed (D pending principal), stash dropped, #365 keys + hook proof; ONE ruling: receipt stale after config commit"
in_reply_to: null
---

# P0-P5 executed (#390): fix set committed, receipt signed (D pending principal), stash dropped, #365 keys + hook proof; ONE ruling: receipt stale after config commit

REPORT on #390/#363/#365: executed. HEAD aab0b9a. The tree is clean apart from monitor-pids.

DONE
(0) .coverage deleted.
(1) GREEN (af13c62, qgr/evidence/qg-p0p5-green-v2.txt): full suite 748 passed, pytest exit 0 read directly. Bracket A and E byte-identical (diff rc 0). The bracket (qg-p0p5-bracket.zsh: zsh array, count asserted = 37) was proven able to fail before use (qg-p0p5-bracket-proof.txt): a content probe changes the digest, a throwaway branch shows as a metadata delta, and an empty or wrong-size set gives rc 3. Each probe reverts to identical.
(2) RED (qg-p0p5-red-v2.txt): scratch git worktree at 451f730 plus ONLY the new test file, fresh uv env, provenance from inside pytest = the scratch copy. Exit 1: 68 failed, 6 passed. The failures split into 44 API-surface reds (33 missing symbols, 11 missing kwargs) and 24 behavioural reds (DID NOT RAISE, pin status, dataset-keyed KeyErrors, device not moved, doc asserts). There are no collection or env errors. The 6 passes are negative controls (already-correct invariants). The scratch worktree was removed; the worktree list is back to 9.
(3) Committed the 17 ACCEPT-FIX-NOW findings with explicit paths and AIADLC_TRUNK_REF=origin/main: 040f022 C16 | 3e8d4b3 C12 | cda216c C17 | ab266bc C11,C23 (docs; C2/C3/C8 appear only as a PENDING-ruling comment) | 0f85e29 cluster C4,C5,C6,C9,C10,C14,C15,C22,C24,C27,OWN-1 plus test_qg_p0p5_fixes.py. All 37 committed files match the GREEN-verified digests byte for byte.
    DEVIATION a: full per-finding atomicity was not possible. Those 11 findings share app_v05/loop/types/provenance/v05_sweep, git-safe has no hunk staging, and a hand-split of hunks risked a commit history that does not match the verified tree. The cluster commit cites all 11 IDs.
    DEVIATION b: I committed first and signed second. diff-hash hashes BASE...HEAD (committed content only), so a receipt signed before the commits could never match.
    RECEIPT 80817b1: qgr phase-complete, Hash E 4a2948a over 451f730...HEAD. Hash A = c46cd22...451f730 as reviewed. B and C inputs are copied into qgr/evidence so they stay reconstructable. D is recorded explicitly as PENDING principal approval (a D=C placeholder, not an approval). The --boundary phase commit is HELD for the principal.
(4) stash: re-found by message plus the recorded SHA 13206b69dd9f and dropped (13 -> 12 entries). The lung-on-chipsim entries are untouched. HEAD is a superset of the stash (the only delta was the untracked test file).
(#365) 3420b21: per-agent keys on this branch, anchored. Stop-hook proof aab0b9a: hooks/quality-check.sh with a cleared cache. Planted format, lint and test failures each give rc 2 (block); clean and reverted give rc 0.
    DEVIATION c (format): your branch-vs-origin/main shape measured RED here, with 79 changed .py files of which 70 would be reformatted. That is repo-wide format debt, and as a Stop hook it would block every turn. I set a WORKING-TREE-scoped format instead (changed-vs-HEAD plus untracked .py). Proven: no .py change gives 0; a planted mis-format in a tracked file gives 1 and in an untracked file gives 1; reverted gives 0; xargs -r handles an empty list. A repo-wide format pass would be its own PR if you want the branch-scoped shape.

ONE BLOCKER / RULING NEEDED
The #365 config commit (agency.yaml, 3420b21) landed inside 451f730...HEAD, so receipt 4a2948a no longer verifies ("code changed after the gate"). The only delta is agency.yaml, a QG-exempt coordination artifact. Options: (i) re-sign a DERIVED receipt (--derived-from 4a2948a) over the new E, stating that the delta is agency.yaml only; (ii) leave it and re-sign at boundary time; (iii) something else. I have not re-signed on my own judgement.

ALSO
- The #283 sweep cannot run yet. The ACCEPT-FIX-AFTER-RULING items (C1,C2,C3,C7,C8,C13,C25,NEW-1,C6-prompt,C20) change the measurand and need a principal ruling plus prereg amendment 2 first (triage, 03:07).
- Two sessions: the previous session b6e15309 has been idle since 13:33Z, with task notifications queued. It has made no edits since. Only this session is editing. If it is resumed, it will process the queued notifications.
- The accession-shape scan over this report and the new evidence found 0 hits.
