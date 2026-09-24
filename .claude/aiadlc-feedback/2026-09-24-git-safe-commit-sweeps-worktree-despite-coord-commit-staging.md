---
type: plugin-feedback
target: aiadlc plugin (tools/git-safe-commit + skills/coord-commit)
plugin_version: 0.60.0
reporter: bioFM/matthew-mo/perturb-seq-eval
date: 2026-09-24
scope: plugin / operating-system behavior — NOT repo/app work
---

## 🔴 1. `/coord-commit` stages selectively, but `git-safe-commit` then runs `git add -A` — implementation code lands in `misc:` commits with no QG
**File:** `tools/git-safe-commit:325-328` (`if [ "$STAGED_ONLY" = false ]; then git add -A; fi`); `skills/coord-commit/SKILL.md` steps 7-8.
**Symptom:** coord-commit staged only `plan/cto-conditions.md` + dispatch files, yet commit `84a8602` also contains `projects/perturb-seq-eval/pyproject.toml`, `scripts/modal/app_v05.py` (unstaged tracked edits) and `plan/baseline.md` (UNTRACKED) — all written by a concurrently running implementer subagent. Implementation code shipped under a `misc:` coordination commit without a QGR receipt.
**Root cause:** `STAGED_ONLY` defaults to `false`, so the default path sweeps the whole worktree. The coord-commit skill tells the agent to stage file-by-file (and `git-safe add` blocks `-A`), then invokes `git-safe-commit` WITHOUT the staged-only flag — so the careful staging is discarded. Worse with subagents: any WIP they have on disk at that moment is captured.
**Fix:** (a) coord-commit step 8 must pass `--staged` (the flag exists: `git-safe-commit:98`); (b) better, invert the default — `git-safe-commit` commits the index only, and sweeping requires an explicit `--all`; (c) in `--no-work-item`/`misc:` mode, refuse if any staged path is outside the coordination-artifact allowlist.
**Effect:** coordination commits cannot carry implementation code; the QG receipt requirement becomes real.
**Status:** open. Local mitigation: the swept T0 files (pyproject pins, Modal image pins, baseline.md) fall inside the P1 iteration range and will be reviewed by that iteration's /quality-gate.
