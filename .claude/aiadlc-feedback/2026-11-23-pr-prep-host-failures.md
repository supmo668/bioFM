---
type: plugin-feedback
target: airdlc plugin
plugin_version: 0.107.1
reporter: biofm/matthew-mo/worktree-agent
date: 2026-11-23
scope: plugin / operating-system behavior — NOT repo/app work
---

## 🔴 1. pr-prep cannot sign when the only failures are host-specific and also fail at base
**File:** /opt/airdlc-plugin/tools/test-result (run/verify), tools/receipt-sign --boundary pr-prep
**Symptom:** bioFM perturb-seq-eval (HACA-119, branch perturb-seq-eval @ 147d915): module suite gives 3 failed / 1117 passed on this Paperclip host. The same 3 fail at the base commit 40c814f (1093 passed): test_backbones.py::test_single_target_regression_pin_bit_exact[*MLPBackbone*] (x2) and test_fill_v060_numbers.py::test_landed_analyser_reproduces_the_committed_summary (last-ulp differences in a ridge solve). test-result exits 1, receipt-sign refuses, so a wording-only change cannot get a QGR receipt.
**Root cause:** the Paperclip host is aarch64 (OrbStack); the bit-exact pins were recorded on x86 BLAS. The repo has no CI job that runs the module tests on x86, and test-result has no notion of a baseline (failures also present at diff_base).
**Fix:** either (a) `test-result run --baseline <ref>`: run the command at the base in a scratch worktree and pass when the failing set at HEAD is a subset of the base's, recording both sets in the receipt as `test_result: pass-vs-baseline`; or (b) document an x86 runner (CI workflow_dispatch job running quality.test_command_<module>) whose result test-result can record.
**Effect:** wording/doc changes on hosts with platform-dependent pins can be gated honestly instead of blocking the hand-off.
**Status:** open (filed against airdlc 0.107.1)

## 🟠 2. quality-cmd resolves role worktree-agent for Paperclip module agents, giving NOTSCOPED
**File:** /opt/airdlc-plugin/tools/quality-cmd (role resolution), tools/agent-identity
**Symptom:** in a Paperclip worktree-agent run, `quality-cmd test` prints `NOTSCOPED quality.test_command_worktree-agent` although agency.yaml has `quality.test_command_perturb-seq-eval`. The gate only finds the module command with AIADLC_AGENT=perturb-seq-eval set by hand.
**Root cause:** role = `agent-identity --agent`, which returns the Paperclip agent class (`worktree-agent`), not the module the worktree belongs to.
**Fix:** when the role key is unset, fall back to the module of the current worktree branch (branch name before `/`, or the `project.modules` entry matching the branch) before reporting NOTSCOPED.
**Effect:** module tests run in the gate without a hand-set environment variable.
**Status:** open (filed against airdlc 0.107.1)
