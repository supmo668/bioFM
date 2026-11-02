---
name: assert-the-artifact-not-the-green
confidence: 0.700
created: 2026-10-30T18:41:53Z
last_reinforced: 2026-10-30T18:41:53Z
ttl_days: 30
triggers: [latex-action, paper.bbl, main.pdf, compute-batches, merge-batch-graphs, pytest, set difference]
tags: []
---

A green build, a passing test or a plausible count says only that nothing complained. Four times in one window it hid a defect: CI compiled in DVI mode for four runs because args dropped -pdf, and only an added paper.pdf assertion turned it red; a test pinning len(candidates - roster) == 13 passed on a broken tree because both sides shrank together; a batch count of 186 looked complete while 144 of 238 changed files were never analyzed; a 9-term PubMed query returned a confident 0. **Why:** the expensive failure is the silent pass, not the false alarm. **How to apply:** assert the artifact itself exists with a measured property (bytes, entry count); pin a count together with its subject; plant a violation and watch the check fail before trusting it; compare outputs against an independent inventory, not against the tool's own count.
