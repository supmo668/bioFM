#!/bin/zsh
# QG P0-P5 re-verification tree bracket (CTO #314 rules 3/3b/3c/3d, #373).
# Usage: qg-p0p5-bracket.zsh <label>   -> prints a snapshot; compare two snapshots with diff.
# Gated set = files changed by the P0-P5 fix set (tracked modifications + the new test file),
# EXCLUDING config/monitor-pids.json (tool state, rewritten on every monitor re-arm) and qgr/evidence/*.
set -u
cd "$(git rev-parse --show-toplevel)" || exit 2
typeset -a GATED
GATED=("${(@f)$(git diff --name-only HEAD -- projects/perturb-seq-eval | sort)}")
GATED+=(projects/perturb-seq-eval/tests/test_qg_p0p5_fixes.py)
EXPECTED=${QG_EXPECTED_COUNT:-37}
if (( ${#GATED[@]} == 0 || ${#GATED[@]} != EXPECTED )); then
  echo "BRACKET ERROR: gated count ${#GATED[@]} != expected $EXPECTED"; exit 3
fi
echo "## bracket $1  $(date -u +%FT%TZ)  HEAD=$(git rev-parse HEAD)  gated=${#GATED[@]}"
echo "### status (excluding monitor-pids + evidence)"
git status --porcelain | grep -v -e 'config/monitor-pids.json' -e 'qgr/evidence/'
echo "### digests"
shasum -a 256 "${GATED[@]}"
echo "### worktrees"; git worktree list --porcelain | grep '^worktree '
echo "### branches"; git branch --list --format='%(refname:short) %(objectname:short)'
echo "### tags"; git tag
echo "### stashes (shared stack: delta = investigate, not abort)"; git stash list --format='%H %gs'
