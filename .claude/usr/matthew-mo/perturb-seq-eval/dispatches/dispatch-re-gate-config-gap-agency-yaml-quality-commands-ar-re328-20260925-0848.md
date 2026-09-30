---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-09-25T15:48
status: created
priority: normal
subject: "Re: Gate config gap: agency.yaml quality commands are all EMPTY; send your exact commands + proof each can fail"
in_reply_to: 328
---

# Re: Gate config gap: agency.yaml quality commands are all EMPTY; send your exact commands + proof each can fail

QUALITY COMMANDS for perturb-seq-eval (answers #328). All run from: projects/perturb-seq-eval (inside the worktree), using that directory's .venv.

Measured in a SCRATCH GIT WORKTREE at HEAD 451f730 (git worktree add, a fresh uv venv built from the live venv's freeze, editable install; pytest provenance printed from inside the run = /private/tmp/.../pse-qg328/...). Exit codes read directly. The scratch worktree was removed and git worktree list is back to its prior 9 entries.

BASELINE FINDING FIRST: with the whole tree in scope, format and lint are RED at HEAD. `ruff format --check src tests scripts` exits 1 (97 files would be reformatted). `ruff check src tests scripts` exits 1 (~190 findings, mostly RUF100/I001/C408/UP style; 5 are F401). Used whole-tree, either command could never pass, so it would block every gate. Hence the scoping below. Tests are GREEN (674 passed).

  format_command:    .venv/bin/ruff format --check <changed .py files>   (scoped to the diff until a repo-wide format pass lands; I can propose that as its own PR)
  lint_command:      .venv/bin/ruff check --select E9,F63,F7,F82 src tests scripts   (syntax errors, undefined names, invalid comparisons; green at baseline)
  typecheck_command: none   (no mypy/pyright configured or installed)
  test_command:      .venv/bin/python -m pytest -q -p no:cacheprovider tests

PROOF EACH CAN FAIL (plant -> rc -> revert -> rc):
  FORMAT: target src/perturb_eval/__init__.py. Pre rc=0. Planted `x = [1,2 ,3]`: rc=1, "File would be reformatted". Reverted: rc=0.
  LINT:   planted `_qg328_probe = undefined_name_qg328` in agentic_lifecycle/loop.py: rc=1, "F821 Undefined name `undefined_name_qg328`". Reverted: rc=0.
  TEST:   planted `assert 1 == 2` test in tests/test_agentic_lifecycle.py: rc=1, "FAILED tests/test_agentic_lifecycle.py::test_qg328_planted_failure", "1 failed, 674 passed". Reverted: rc=0, 674 passed.

Caveats: (1) the lint subset is deliberately narrow. Widening to F would need the 5 F401s fixed first, and widening to the full inherited rule set needs a cleanup PR. (2) The test suite excludes nothing, but integration-marked tests need scGPT weights/network. They passed here because those paths are mocked or skipped. No deselection was needed.
