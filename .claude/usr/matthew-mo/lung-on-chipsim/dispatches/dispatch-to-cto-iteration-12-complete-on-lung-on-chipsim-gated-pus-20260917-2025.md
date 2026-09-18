---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-18T03:25
status: created
priority: normal
size: task
subject: "Iteration §12 complete on lung-on-chipsim — gated, pushed, two escalations"
in_reply_to: null
---

# Iteration §12 complete on lung-on-chipsim — gated, pushed, two escalations

event: iteration-complete
workstream: lung-on-chipsim
iteration: §12
branch: lung-on-chipsim
commit_hash: 514ff17
remote_ref: refs/heads/lung-on-chipsim = 514ff17 (was 20e9edd); refs/heads/main = df89f503 UNTOUCHED
qgr_receipt: workstreams/lung-on-chipsim/qgr/bioFM-matthew-mo-lung-on-chipsim-lung-on-chipsim-bioFM-qgr-iteration-complete-20260917-2022-54e27d5.md
hash_a: b7e3429
hash_e: 54e27d5
diff_base: 20e9edd
tests: 1002 passed / 5 skipped
quality: ruff format --check and ruff check both verified by reading output AFTER the last edit
guard_preflight: record-content-gate (STAGED) exit 0; record-content-report (WORKTREE) exit 0; 794 tracked
summary: >
  r2.29's ordered work (signatures first, then errors/policy/report leaves), r2.28's staged-blob
  ruling, derived_from pinning content, and four carried findings — then a four-reviewer gate that
  found THREE FALSE CLEANS (symlink target strings; a record in a numeric-dtype dataset; an unmerged
  index scanned around, staged CLEAN where worktree found the accession), r2.28's ruling implemented
  as a mechanism NOTHING INVOKED (E6-7's defect one iteration after I fixed it), a ScanContext that
  could claim STAGED while reading the worktree, two regressions of mine, and three vacuities of
  mine including one that passed under the exact defect it names.
escalations:
  - pre-commit hook installation: the command (record-content-gate) exists; installing it is
    repository configuration affecting everyone who commits, so it is the CTO's. Until a hook or CI
    calls it, r2.28's property is AVAILABLE rather than ENFORCED.
  - checkout-index applies eol/smudge conversion, so staged mode reads the working-tree RENDERING of
    the index rather than blob bytes when a tracked .gitattributes asks for it. Measured; no live
    .gitattributes; no false clean constructible. Fix (cat-file --batch) changes how the gate reads.
carried_forward: THIS_PROJECT from the import location (fail-closed); ContentPolicy naming; one path
  printing two owners; two unpinned pre-existing repo.py guards.
not_claimed: four cache-key components measured INERT — the two tests written to bind them were
  DELETED rather than kept as vacuities, and the comment corrected to defence-in-depth.
next_handoff: cto ruling on the two escalations
