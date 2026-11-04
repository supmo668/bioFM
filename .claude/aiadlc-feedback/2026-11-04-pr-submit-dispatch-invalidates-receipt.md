---
type: plugin-feedback
target: airdlc plugin
plugin_version: 0.90.0
reporter: biofm/matthew-mo/perturb-seq-eval
date: 2026-11-04
scope: plugin / operating-system behavior — NOT repo/app work
---


## 🟠 1. Own pr-submit dispatch invalidates the receipt it cites
**File:** <tool/hook/skill path, with line if known>
**Symptom:** <what the operator observed>
**Root cause:** <the underlying why — proven, not guessed>
**Fix:** <the smallest concrete change>
**Effect:** <what improves once applied>
**Status:** open (filed against airdlc 0.90.0)

Observed 2026-11-04, perturb-seq-eval, airdlc 0.90.0. After `/pr-prep` signed receipt ae59f98 and `/pr-submit` sent dispatch #888, the `context-commit-check` Stop-hook requires the outgoing dispatch .md under `.claude/usr/<p>/<agent>/dispatches/` to be committed. diff-hash counts that file, so Hash E moved to 27916e2 and `receipt-verify --require-pushed` failed: "Code changed after the gate ran". The receipt quoted in the pr-submit body is stale by the time the CTO reads it. This is the same class of failure as the three failed lands on #863.
Workaround used: commit the context first, then sign a `--derived-from` receipt, then send a correction reply.
Suggested fix: have diff-hash exclude `.claude/usr/**` context artifacts, which already never gate code. Or have pr-submit commit its own dispatch before it computes and cites the hash.
