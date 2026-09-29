---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-25T15:49
status: created
priority: normal
size: task
subject: "Quality commands ACCEPTED with two fixes (anchor with cd; a concrete diff-scoped format command); set them on YOUR branch per the 6011dec precedent"
in_reply_to: 362
---

# Quality commands ACCEPTED with two fixes (anchor with cd; a concrete diff-scoped format command); set them on YOUR branch per the 6011dec precedent

Accepted: the narrow lint subset (E9,F63,F7,F82, green at baseline), the full test suite, and typecheck explicitly empty. Scoping instead of adopting a red whole-tree command was right; a gate that always fails teaches bypassing.

TWO FIXES before you set them:
1. ANCHOR every command with 'cd projects/perturb-seq-eval && ...'. hooks/quality-check.sh and commit-precheck run from the WORKTREE ROOT (lung-on-chipsim measured an unanchored uv run exiting 2 there), so a bare .venv/bin/... fails for the wrong reason.
2. The FORMAT command must be a concrete command, not '<changed .py files>'. Suggested shape, which you must verify rather than take from me: cd projects/perturb-seq-eval && git diff --name-only --diff-filter=ACMR origin/main -- '*.py' | sed 's|^projects/perturb-seq-eval/||' | xargs -r .venv/bin/ruff format --check. Two things to prove: it fails on a planted mis-format in a CHANGED file, and it does not fail or error when the diff contains no .py files (xargs -r). Note the pipe: the hook's exit status is the last command's (xargs), which is what you want here. State that you checked it.

WHERE: set the four per-role keys (format/lint/test, and typecheck explicitly '') on YOUR branch's agency.yaml, as lung-on-chipsim did at 6011dec, in its own config commit. Do not put them on main: a second copy conflicts at merge. Then prove the Stop hook runs them the way aviary-biosim did (#346): invoke hooks/quality-check.sh directly with a cleared cache, planted failure -> block, reverted -> pass.

Remember the limit: these keys feed the Stop hook only. /quality-gate Step 8 still reads the empty global, so keep running the suite by hand in every gate and record it.

Integration tests needing scGPT weights or network: note in the config comment that they pass because they are mocked or skipped, so the test command is not evidence for those paths.

Sequencing: this is a separate small commit; do it after the P0-P5 fix set is receipted and committed (#363), not before.
