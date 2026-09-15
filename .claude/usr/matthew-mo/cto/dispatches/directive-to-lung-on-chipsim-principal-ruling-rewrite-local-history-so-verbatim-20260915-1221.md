---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-15T19:21
status: created
priority: high
size: task
subject: "PRINCIPAL RULING: rewrite local history so verbatim snapshot InChIs never reach the remote + add an enforced guard test (with falsification); push still frozen"
in_reply_to: null
---

# PRINCIPAL RULING: rewrite local history so verbatim snapshot InChIs never reach the remote + add an enforced guard test (with falsification); push still frozen

# PRINCIPAL RULING: rewrite the local history, and add a guard test. Push stays frozen.

Decided 2026-09-15, on the fact that nothing is pushed. Two parts, both required.

**1 · The verbatim snapshot InChIs must never reach the remote.** Fold the re-sourced structures into the §2 commits so that NO commit on this branch contains a structure byte-identical to `data/raw/drugbank/*.tsv`. A forward fix on top was considered and rejected: it would push history that carries DrugBank record content and would force the invariant to be reworded everywhere it is claimed.

**2 · The invariant becomes enforced, not asserted.** Add a test that fails if any TRACKED file contains a structure string byte-identical to a row in the snapshot. It lived only in prose and in a docstring that silently became false — that is why this happened at all. The test must have a demonstrated falsification: add a snapshot InChI to a tracked file, watch it fail, remove it, report both states.

## Sequence — do not reorder

0. (from #114) `git-push` out of the commit scripts; push frozen until I clear it in writing.
1. (from #114) commit b9's tail; 2. merge `main` `d230c3b`, gate must report `16b0cc9`.
3. (from #114) **re-source every §2 structure from PubChem**, CID + retrieval date beside each, fix `test_parse.py`'s now-false docstring, extend `sources.yaml`'s PubChem entry. Stop and report if any structure is absent from PubChem.
4. **Now the rewrite.** The §2 commits (`7592f56`, `8cb72bf`) are local-only and unshared, so this is not landed history. Rebase/squash so the final content is the PubChem-sourced version and the verbatim strings appear in no commit. Keep the §2 work as recognisable commits — do not flatten the whole branch.
5. **Prove it, with the tool that answers the question:** `git rev-list --all` + `git log -S'<exact string>' --all --oneline` for EVERY structure that was verbatim, expecting empty output for each. A clean working tree proves nothing about history. Report the commands and their output.
6. Add the guard test from part 2, with its falsification.
7. Re-run the suite AND the module merge report; confirm 1,599 / 191->156 / 48->7 / 41 / 0 new merges still reproduce after re-sourcing. If a figure moves because a structure changed, that is a finding — raise it, do not absorb it.
8. Then the §2 `/iteration-complete` boundary, so the receipt attests what will actually ship. Then ask me for push clearance. Do not push.

## A wider exposure I checked myself, so you do not have to guess

`tests/fixtures/snapshot/*.tsv` also carry InChI strings. My read-only measurement, now:

    FIXTUREVERDICT

Treat that as data for step 6, not as an instruction: if fixture rows are verbatim snapshot content, the guard test will fail on them the moment it exists, and the fix is the same as for the tests — re-source or synthesise, never allow-list. **Report what you find before changing fixtures**, because fixtures feed many tests and I would rather rule on the approach than have it inferred.

## Not authorised

Any push. Any rewrite before step 3 is complete. Any allow-list entry, anywhere, for snapshot-derived content.

next_handoff: you — steps 0-8; me — push clearance after the boundary, and the fixture approach if your measurement disagrees with mine.
