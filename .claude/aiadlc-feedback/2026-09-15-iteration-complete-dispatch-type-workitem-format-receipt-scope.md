---
type: plugin-feedback
target: aiadlc plugin (aiadlc-plugins/aiadlc) + skills/iteration-complete + reference/REFERENCE-QUALITY-GATE.md
plugin_version: 0.54.0
reporter: bioFM/matthew-mo/lung-on-chipsim
date: 2026-09-15
scope: plugin / operating-system behavior — NOT repo/app work
---

# /iteration-complete: three places where the skill and the tools it calls disagree

All three hit on one boundary (lung-on-chipsim P0.4, 2026-09-15). Each was worked around; none is app work.

## 🟠 1. `tools/dispatch` rejects the dispatch type the skill prescribes
**File:** `skills/iteration-complete/SKILL.md` Step 8 (`--type iteration-complete`) vs `tools/dispatch` VALID_TYPES.
**Symptom:** `dispatch create --type iteration-complete …` →
`Error: invalid dispatch type 'iteration-complete'. Must be one of: directive seed review review-response commit master-updated escalation pr-submit dispatch ship changes-requested`.
**Root cause:** the skill's Step 8 names a type that is not in the tool's VALID_TYPES (same for `/phase-complete`'s presumptive `phase-complete` type). The class doc even lists `/iteration-complete` and `/phase-complete` as boundary returns to the coordinator.
**Fix:** add `iteration-complete` and `phase-complete` to VALID_TYPES in `tools/dispatch` (and to any consumer switch in the CTO's triage/monitor), or change Step 8 to `--type dispatch` with `event: iteration-complete` in the body. Prefer the former — a typed boundary event is what the coordination daemon is meant to pick up.
**Effect:** boundary dispatches emit as written; no per-agent workaround; the CTO can filter on type.
**Workaround used:** `--type dispatch --priority high`, subject prefixed `ITERATION-COMPLETE`, body `event: iteration-complete`.
**Status:** open

## 🟠 2. `git-safe-commit` rejects the work-item form the skill's own example uses
**File:** `tools/git-safe-commit` work-item validation vs `skills/iteration-complete/SKILL.md` (Step 4 example: `--work-item ITERATION-ws-013`).
**Symptom:** `git-safe-commit "Iteration P0.4: …" --work-item ITERATION-lung-on-chipsim-P0.4 --stage impl --boundary iteration --staged` →
`[ERROR] Invalid work item format: ITERATION-lung-on-chipsim-P0.4 / Expected: REQUEST-<principal>-XXXX, BUG-<workstream>-XXXXX, TASK-id, etc.`
**Root cause:** the validator's accepted prefixes do not include `ITERATION-` (or `PHASE-`/`PLAN-`), while the skill's canonical example uses it.
**Consequence worth naming:** because the rejected commit left the index staged, a following `--staged` coord commit swept the QGR files up under the wrong message (an unshared tip, repaired with `reset --soft`). A rejected boundary commit should probably print "index left staged" loudly.
**Fix:** accept `ITERATION-<ws>-<id>`, `PHASE-<ws>-<id>`, `PLAN-<ws>-<id>` in the validator, or change the skill example to `TASK-…`. One-line regex change either way.
**Effect:** the documented boundary invocation works first time.
**Status:** open

## 🟠 3. `diff-hash`/`receipt-verify` scope the QGR docs, so a boundary commit cannot be verified after it lands
**File:** `tools/diff-hash` (scope of `--base` diff), `tools/receipt-verify`, `reference/REFERENCE-QUALITY-GATE.md` "Proposed Commit" (lists the QGR report among the boundary commit's files), `skills/iteration-complete/SKILL.md` Steps 4–5 (commit, THEN update the plan file).
**Symptom (measured):** Hash E over `3fa54e3..HEAD` = `2e1937e` (10 files) before the QGR docs were committed; after a commit adding `workstreams/<ws>/plan/quality-gate-reports.md`, `workstreams/<ws>/dev-log.md`, `.claude/workstreams/<ws>/context.json` → `2b3623f` (13 files) and `receipt-verify` → `BLOCKED: Found 13 receipt(s) but none match current code`. The `qgr/*.md` receipt file itself is NOT in scope (10 → 10 when it was added), but the report/dev-log/context are.
**Root cause:** `diff-hash --base` diffs base..HEAD over the whole tree except (apparently) `qgr/` and `.claude/usr/`; the QGR report and dev-log are inside the hashed set, so the very commit that records the receipt changes the hash the receipt attests. Verification only passes at commit time (pre-commit HEAD); any later `receipt-verify`, and presumably `receipt-chain-verify` at `/phase-complete`, sees a mismatch by construction.
**Fix:** exclude coordination artifacts from `diff-hash`'s scope — at minimum `<paths.workstreams_root>/*/plan/quality-gate-reports.md`, `<paths.workstreams_root>/*/dev-log.md`, `.claude/workstreams/**` (and `parked/`-style docs if the framework adopts them) — OR have `receipt-verify` recompute E at `<boundary-commit>^` when given a commit. Also reconcile the reference's "Proposed Commit" file list with the skill's commit-then-update order so the two documents prescribe one sequence.
**Effect:** a boundary commit stays verifiable after it lands; `receipt-chain-verify` at the phase boundary can actually re-verify instead of trusting the trailer.
**Status:** open
