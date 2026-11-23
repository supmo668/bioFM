# perturb-seq-eval: the x86_64 reference run as the pr-prep test record

HACA-121. Gate policy for citing CI as the test record when the Paperclip host
is not the reference platform.

## Why

Three tests pin numbers bit-exactly and fail by about 2 ulp on the aarch64
Paperclip host, at every commit (base 40c814f included):

- `tests/test_backbones.py::test_single_target_regression_pin_bit_exact[int-MLPBackbone-pin1]`
- `tests/test_backbones.py::test_single_target_regression_pin_bit_exact[1-tuple-MLPBackbone-pin1]`
- `tests/test_fill_v060_numbers.py::test_landed_analyser_reproduces_the_committed_summary`

The pins were recorded on x86_64. The reference platform for this module is
therefore **ubuntu x86_64, Python 3.12**, run by
`.github/workflows/perturb-seq-eval-tests.yml`.

## How a worktree agent cites the run in `/pr-prep`

1. Run the suite on the host as usual (`quality.test_command_perturb-seq-eval`).
   If the only failures are the three tests above, go on. Any other failure is
   a real failure.
2. Push the branch. The workflow runs on every PR that touches
   `projects/perturb-seq-eval/**`. Without a PR, dispatch it:
   `gh workflow run perturb-seq-eval-tests.yml --ref <branch>`.
3. Wait for it: `gh run list --workflow perturb-seq-eval-tests.yml --branch <branch> -L 1`.
   The run must be **green** and on the **same commit as receipt hash E**: the
   "Record the platform" step prints `commit=`; check that it matches.
4. In the receipt, set `test_result: pass` and give the run as the source:
   - `hash_d_source`: `"x86_64 reference run <run URL> green at <sha> (HACA-121 policy)"`
   - Review Summary: host result (N passed / 3 failed, the known set) and the
     reference run result (N passed, 0 failed), with the run URL.
5. If the reference run is red, the receipt is `fail`. Fix it; no waiver.

A pull_request run tests the merge commit with the base branch. That is the
right check for landing; when the receipt is on the branch head, cite a
`workflow_dispatch` run on the branch instead, or check that `module_tree=`
in the log equals `git rev-parse <E>:projects/perturb-seq-eval`.

## What this does not change

- The host run is still required; it catches everything except the three
  known platform-dependent pins.
- A fourth host-only failure is not covered by this policy.
- A plugin-side fix (a baseline-aware `test-result` that knows a platform
  baseline set) is filed as plugin feedback; when it ships, this page is
  replaced by that config.
