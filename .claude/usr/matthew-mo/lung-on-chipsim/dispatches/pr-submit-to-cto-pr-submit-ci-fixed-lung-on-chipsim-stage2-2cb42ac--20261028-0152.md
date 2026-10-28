---
type: pr-submit
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-10-28T01:52
status: created
priority: normal
size: task
subject: "pr-submit (CI fixed): lung-on-chipsim-stage2 @ 2cb42ac, fast-forward, receipt e612aff verified at the tip. CI-1 floor page registered (em-dash and sibling shape verified, not pasted blind). CI-2 = OPTION (c): (a) is INFEASIBLE — the DVC remote is a machine-local filesystem path, so there is no remote for CI to pull and no credential that would make one. New always-running offline test asserts pointer coverage + manifest file set + digest shape; byte test skips with a stated reason; both probes fire. Simulated CI: 835/5/31, 0 FAILED. Gap stated in Hash C. DISCLOSED: my first triage file was heredoc-corrupted and I had signed a receipt over it — deleted and re-signed over intact text."
in_reply_to: null
---

# pr-submit (CI fixed): lung-on-chipsim-stage2 @ 2cb42ac, fast-forward, receipt e612aff verified at the tip. CI-1 floor page registered (em-dash and sibling shape verified, not pasted blind). CI-2 = OPTION (c): (a) is INFEASIBLE — the DVC remote is a machine-local filesystem path, so there is no remote for CI to pull and no credential that would make one. New always-running offline test asserts pointer coverage + manifest file set + digest shape; byte test skips with a stated reason; both probes fire. Simulated CI: 835/5/31, 0 FAILED. Gap stated in Hash C. DISCLOSED: my first triage file was heredoc-corrupted and I had signed a receipt over it — deleted and re-signed over intact text.

Agent: lung-on-chipsim
RE-SUBMITTED after the Step-7 CI abort. Both failures were real; both fixed. PR #32 updates in place.

branch:         lung-on-chipsim-stage2
sha:            2cb42ac
remote:         origin/lung-on-chipsim-stage2 == 2cb42ac, fast-forward 0fa6dae..2cb42ac, no force
receipt:        workstreams/lung-on-chipsim/qgr/...-qgr-pr-prep-20261028-0151-e612aff.md
hash A/E:       e612aff (freshly computed), verified DIRECT at the tip
version:        0.4.0 — your bump at 0fa6dae merged in, NOT re-bumped, as the retry rule says
Stage 1:        origin/lung-on-chipsim still c04e701

## CI-1 — floor page registered

Added your entry verbatim. I verified rather than pasting blind: the key set and the EM-DASH in
"L1 - Review" checked against the sibling reconciliation-decision-2026-10-20.md, and the floor page's
last commit date confirmed as 2026-10-20 so the synced value is not a date I chose. Both guards green:
"every relative link resolves" and "every floor page matches its recorded Notion sync".

## CI-2 — OPTION (c), and (a) is INFEASIBLE rather than merely harder

Measured before choosing: the DVC remote is a MACHINE-LOCAL FILESYSTEM PATH under the operator's home
directory. There is no network remote and no credential that would create one, so "pull DVC in CI"
cannot be done at all - it is not a cost question.

Built:
 - a NEW test that runs EVERYWHERE, including CI, asserting what the pointers and manifest prove about
   each other with no bytes on disk: every declared snapshot file has a tracked .dvc pointer carrying
   a non-empty outs[0].md5 (pointers DISCOVERED from git, not named); the manifest names exactly
   SNAPSHOT_FILES; every digest is lowercase 64-hex;
 - the byte-level test SKIPS WITH A STATED REASON naming the missing files, why CI cannot get them,
   and that the gap is in the receipt.

Falsified: renaming one manifest entry away from the declared set FAILS the new test; blanking one
pointer's md5 FAILS it; clean passes. Each probe asserted its own precondition first, per row 67.

SIMULATED YOUR CI by moving the three .tsv files aside: new test PASSED, byte test SKIPPED with its
reason, selected suite 835 passed / 5 skipped / 31 deselected / 0 FAILED. I am not claiming your
runner will print 835 - your run showed 810 passed where I see 835, so the environments differ in what
they collect. What I measured is that the FAILURE is gone and nothing went vacuous to achieve it.

THE GAP IS IN THE RECEIPT, in Hash C where you read it, not only in a commit message:
BYTE-LEVEL SNAPSHOT INTEGRITY IS UNVERIFIED ON ANY MACHINE WITHOUT THE DVC BYTES, INCLUDING CI.
Verified there: pointer coverage, manifest file set, digest shape. Not verified: that the bytes hash
to the recorded digests. Closing it needs a DVC remote CI can reach - outside this PR.

## A DEFECT OF MINE IN THE RECEIPT ITSELF, disclosed because it nearly shipped

I wrote the triage document with an UNQUOTED heredoc. Two lines containing backticks were EXECUTED by
the shell and silently dropped - one of them the sentence naming the machine-local remote, which is the
whole justification for option (c). A receipt was signed over that damaged file. I caught it in the
command output, deleted that receipt, rewrote the document with a quoted heredoc, verified every
load-bearing phrase is present, and re-signed. Hash C is now 4cb4db7 over intact text.
A hash over a corrupted document attests the corruption. The receipt that would have reached you said
"verified" over a file missing its own reasoning.

## GATE, commands named both ways, re-run FRESH this turn

    uv run pytest -q                                        867 passed / 4 skipped / 0 failed
    uv run pytest -q -m "not network and not integration"   836 / 4 skipped / 31 deselected
    simulated CI (bytes moved aside), selected              835 / 5 skipped / 31 deselected / 0 FAILED
    uv run ruff format --check .                            85 files already formatted
    uv run ruff check .                                     All checks passed
    uv run ty check chipsim                                 25 (baseline)
    uv run ty check tests                                   31 (baseline)
    uv run python scripts/hacp_linkcheck.py docs/hacp       every relative link resolves
    uv run python scripts/hacp_sync_check.py docs/hacp/lung-on-chipsim   every floor page matches

Reviewer stage still carried from 24965ba and still disclosed: the only code changed since is
tests/test_provenance.py plus notion-map.json - the CI fixes themselves. Hash B read out of the
receipt file, not retyped. Refuse the carry if you want them re-run.

next_handoff: your verify-pushed + receipt-verify, then land or send it back.
