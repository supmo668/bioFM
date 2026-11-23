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

## Finding (2026-11-23): x86_64 does not reproduce the pins either

The same three tests fail on ubuntu x86_64 / Python 3.12:

- run 45107486401 (numpy 2.5.5, shallow clone): the 2 MLP pins plus 7 history tests
  that need full history; fixed in the workflow.
- run 45107946442 (numpy 2.4.4 / scipy 1.17.1 / scikit-learn 1.8.0 from the lock, full
  history, PR head 6cb9ef4, module tree 54cc281 = perturb-seq-eval @ 147d915):
  **1246 passed, 3 failed, 1 skipped**. The 3 are exactly the host set.

The MLP output differs by 1 to 2 ulp between numpy 2.5.5 and 2.4.4 on the same x86
CPU, so the pins depend on the numpy/BLAS build, not on the architecture. They were
recorded on 2026-09-24 in an environment nobody can reproduce now. Until the
perturb-seq-eval tests are changed (re-record the pins with the environment written
down, or compare within a few ulp, e.g. `np.testing.assert_array_max_ulp`), no
platform turns these three green and the procedure below does not apply to them.
Until then the CTO's per-PR waiver (HACA-119, comment 16ba31cd) stays the
mechanism, and this run shows that the failing set is the same on x86.

## Resolved (HACA-124): ulp-bounded comparison, no waiver

HACA-124 replaced the three bit-exact checks with a bounded comparison (CTO decision on
HACA-121; the pins were kept, not re-recorded):

- the MLP pin must match within 4 ulp of the pin's largest magnitude (`MLP_PIN_MAX_ULP`).
  A per-element `assert_array_max_ulp(maxulp=4)` cannot hold: element 0 (-0.0094) is a
  cancellation result and moves 12 (aarch64) to 28 (x86_64) of its own ulp, about 5e-17
  absolute, while every element stays within 1 ulp of the scale. The int and 1-tuple
  outputs must still be byte-identical to each other on one build. The linear pin stays
  bit-exact;
- the summary test keeps exact equality for every key except two disclosed keys
  (`H5/weights/one_minus_delta_c`, the `H5/norman_tdi` scores), which match within 4 ulp,
  and every reported (rounded) value must stay identical;
- the checked numeric environments (python, numpy, scipy, scikit-learn, BLAS) are recorded
  in a test fixture note, and a failure prints the build it ran on.

The full suite is now green on both the aarch64 host and this x86_64 workflow, so the
HACA-119 waiver no longer applies: from here on a failure on either platform is a real failure.

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

The workflow checks out the PR head (not the synthetic merge commit) with full
history, so the `commit=` it prints is the branch head; `module_tree=` must
equal `git rev-parse <E>:projects/perturb-seq-eval`.

numpy, scipy and scikit-learn are pinned to the poetry.lock versions: the MLP
pin is pure numpy and moves by 1 ulp with the numpy build (numpy 2.5.5 failed
it on x86_64 too, run 45107486401). Do not unpin them without re-recording the
pins.

## What this does not change

- The host run is still required; it catches everything except the three
  known platform-dependent pins.
- A fourth host-only failure is not covered by this policy.
- A plugin-side fix (a baseline-aware `test-result` that knows a platform
  baseline set) is filed as plugin feedback; when it ships, this page is
  replaced by that config.
