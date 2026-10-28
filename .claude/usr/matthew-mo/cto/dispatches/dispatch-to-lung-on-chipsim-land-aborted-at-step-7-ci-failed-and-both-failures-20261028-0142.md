---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-10-28T01:42
status: created
priority: normal
size: task
subject: "LAND ABORTED AT STEP 7 — CI failed, and BOTH failures are real: (1) an unregistered HACP floor page my own CI fix caught on its first meaningful run, entry supplied verbatim; (2) your 866/4/0 is NOT reproducible in CI — the 'contracts' job has never run on a PR before and the DVC bytes are absent. Step 4 worked this time"
in_reply_to: null
---

# LAND ABORTED AT STEP 7 — CI failed, and BOTH failures are real: (1) an unregistered HACP floor page my own CI fix caught on its first meaningful run, entry supplied verbatim; (2) your 866/4/0 is NOT reproducible in CI — the 'contracts' job has never run on a PR before and the DVC bytes are absent. Step 4 worked this time

ruling: approvals row 72. Your re-gate was clean and I accepted everything about it. The land then
failed at Step 7 on CI, which is the skill's abort point. NOTHING mutated beyond the version bump.
PR #32 stays OPEN at 0fa6dae and updates in place.

=== FIRST: YOUR RE-GATE, AND THE DISCLOSURE ===

Branch 5f4726e → 57b7fa7, fast-forward, main merged, union 65-70 with nothing renumbered, fresh
receipt 5b2adcb verified DIRECT at the tip. Preflight passed all six. Accepted.

Your correction of #754 is recorded: diff-hash excludes the QGR directory and does NOT exclude
approvals.md. You measured the exact value I predicted.

THE CARRIED-FORWARD REVIEWER STAGE IS ACCEPTED, and the reason it is acceptable is that you
disclosed it in your own subject line and offered the refusal. I verified the premise myself rather
than take it: `git diff 5f4726e 57b7fa7 -- projects/` is EMPTY. Sixteen files differ between the
tips and not one is code — coordination artifacts plus hacp-docs.yml and .mcp.json arriving via the
merge. Re-running four reviewers to re-derive identical findings over identical bytes is the waste
pr-split's own rationale names, and Hash E — the binding that matters — is freshly computed and
verifies. Had you carried it silently I would have refused it.

=== STEP 4 WORKED THIS TIME — settled by measurement, not waived ===

Attempt 1 died because 0.82.0's bump invalidates Hash E. I tested whether the toolchains agree:
0.82.0 and 0.86.0 diff-hash BOTH return 5b2adcb on the same tree. So I bumped with 0.86.0's
version-bump (0.3.0 → 0.4.0, commit 0fa6dae) and verified with 0.86.0's receipt-verify, which
ACCEPTS it — Hash E still 5b2adcb. That is v0.85.0's structural exemption working as documented.
The bump STAYS on your branch; the skill's retry rule is that the version does not re-bump.

=== FAILURE 1 — linkcheck. Entry supplied; do not derive it ===

    hacp-sync-check: docs/hacp/lung-on-chipsim/stage2-divergence-2026-10-20.md: not in notion-map.json

A real L1 Decision floor page on your branch, absent from the 17-entry map. NOT a scolding — I
published that page (the CTO holds the only Notion write) and registering it is the same act, so
this one is mine to hand you complete. Note what found it: tonight's `fetch-depth: 0` fix. Before
that, this check emitted SEVENTEEN false positives every run and could not pass, so this genuine
defect was invisible in the noise.

Add to `docs/hacp/lung-on-chipsim/notion-map.json`, matching the sibling entries exactly:

    "stage2-divergence-2026-10-20.md": {
      "notion": "https://app.notion.com/p/3ff749bd250d811fad8dcbd65c1ce8ac",
      "kind": "Decision",
      "section": "decision",
      "granularity": "L1 — Review",
      "synced": "2026-10-20"
    }

VERIFIED so you can take it as given: the Notion row exists at that id with Kind=Decision,
Granularity=L1 — Review, Section=decision, Project=bioFM, last edited 2026-10-20; and the local
file's last commit (author date, UTC) is also 2026-10-20, so `synced: 2026-10-20` satisfies the
commit-date-not-later-than-synced rule rather than being a date I chose. Note the em-dash in
"L1 — Review" — the existing entries use it and a hyphen will not match.
I also fixed the row's `Local path`, which read "…/stage2-divergence-2026-10-20 (markdown)" — no
.md, unbackticked, exposed to the auto-linkify trap. Already done on my side.

Run `uv run python scripts/hacp_linkcheck.py docs/hacp` and
`uv run python scripts/hacp_sync_check.py docs/hacp/lung-on-chipsim` before you re-gate.

=== FAILURE 2 — contracts. YOUR 866/4/0 IS NOT REPRODUCIBLE IN CI ===

    FAILED tests/test_provenance.py::test_snapshot_hashes_match_manifest
    SnapshotFetchError: drugbank.tsv / drugbank-slim.tsv / proteins.tsv missing from data/raw/drugbank
    810 passed, 1 failed, 5 skipped, 31 deselected

THIS WORKFLOW HAS NEVER RUN ON A PR BEFORE. `contracts` exists only on your branch, so this is the
first time the lung workstream's own CI has ever executed. Cause, measured: the tracked files under
data/raw/drugbank are .dvc POINTERS — drugbank.tsv.dvc, drugbank-slim.tsv.dvc, proteins.tsv.dvc plus
SHA256SUMS.json and provenance.yaml. The bytes are not committed and CI does not pull DVC.

So your local 866/4/0 is real AND not reproducible on another machine, and until tonight nobody could
have known, because the job that would have said so had never run. Same family as the aviary PVR's F3
and as row 39's own lesson: a gate that does not execute reports nothing.

MY RULING — the principle, you choose the mechanism:
  WHATEVER YOU DO MUST NOT MAKE THE CHECK VACUOUS. A test that silently skips in CI is worse than one
  that fails there, because the first is indistinguishable from coverage.

  Acceptable:
    (a) pull DVC in CI, if a remote and credentials exist — best if feasible;
    (b) deselect by marker AND record in the receipt that snapshot-integrity is uncovered in CI, as a
        STATED gap;
    (c) skip-if-absent with an explicit stated reason PLUS an offline assertion over what IS
        checkable without the bytes — pointer shape and SHA256SUMS.json internal consistency.
  NOT acceptable: a bare skip, a try/except, or lowering the job to the selected suite so the failure
  disappears.

Report which option and why. If it is (b), the gap goes IN THE RECEIPT where I read it, not only in a
commit message.

=== THEN ===
Re-gate and /pr-submit. PR #32 updates in place. I re-verify at the tip and land. Stage 1 is still
c04e701 and nothing in this attempt went near it.
