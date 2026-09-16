---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-16T22:33
status: created
priority: high
size: task
subject: "§3 complete + PUSHED under receipt 5d60397 (origin/lung-on-chipsim = b801329, main untouched): r2.18 T14/T15 implemented; QG found the export CLOBBERED the tracked file (24 verdicts -> 0, reported as success) and a string flag marked every compound relative; 14 fixed, 6 need your ruling"
in_reply_to: null
---

# §3 complete + PUSHED under receipt 5d60397 (origin/lung-on-chipsim = b801329, main untouched): r2.18 T14/T15 implemented; QG found the export CLOBBERED the tracked file (24 verdicts -> 0, reported as success) and a string flag marked every compound relative; 14 fixed, 6 need your ruling

event: iteration-complete
workstream: lung-on-chipsim
iteration: "§3 (T14/T15, r2.18)"
branch: lung-on-chipsim
commit_hash: b801329
plan_hash: 2325057
qgr_receipt: workstreams/lung-on-chipsim/qgr/bioFM-matthew-mo-lung-on-chipsim-lung-on-chipsim-bioFM-qgr-iteration-complete-20260916-1532-5d60397.md
diff_base: 0c4e181
hash_e: 5d60397149967849e3218d8a0b95f974bcfb7b0b1986a0afecc3798ff7952d1e
pushed: YES — origin/lung-on-chipsim = b801329, nothing rejected, main untouched (df89f50)
next_handoff: cto rulings on the six escalations below

## 1. Push report (your three conditions)
1. Guard run IMMEDIATELY before the push, not from memory: 161 passed (record-content guard,
   fixture sources, provenance, fixture registry).
2. Branch only: `git-push lung-on-chipsim` -> `f25e056..b801329  lung-on-chipsim -> lung-on-chipsim`.
   `git ls-remote`: refs/heads/lung-on-chipsim = b801329, refs/heads/main = df89f50 (untouched).
3. Nothing was rejected. Receipt verified FROM THE REPO ROOT: "1 of 15 receipt(s) verified".
This push carries F-14 (7a60e83) and the whole of §3, all under receipt 5d60397.

## 2. Implementation of your option-A ruling
- `export_tracked_adjudication(worksheet, out) -> int`, refusing extra human-added columns
  (including empty ones), dropping name/snapshot_label/stereo_is_relative/label_disagrees_with_key.
- `adjudicate_pgp_labels(adjudication, compounds, parquet_out=None)` reads the tracked five-column
  file and RECOMPUTES the flag per key from `compounds` (any member).
- Six five-column fixtures, each a row-for-row projection of the worksheet fixture of the same case
  (a test pins the projection, so the two families cannot drift). No value invented.
- 703 passed / 5 skipped / 0 failed. ruff check clean.

## 3. Quality gate — 20 kept findings: 14 fixed, 6 escalated, 1 rejected
Four reviewers plus my own review. The three findings that matter:
- G-01 [95] The export CLOBBERED the tracked file. Measured: a BLANK worksheet exported over a
  filled tracked file left 0 of 24 verdicts and returned 24, which reads as success. No
  carelessness needed — data/interim/ is lost (clean checkout, DVC re-pull, new machine), T13
  regenerates the worksheet blank WITHOUT error, and a re-export destroys the adjudication. Defect
  22's never-clobber rule did not cover the one file that is the published record. Now refused.
- G-03 [90] A non-boolean `stereo_is_relative` column was coerced by truthiness: a compounds frame
  read back from CSV (dtype=str is this project's own convention) reported 24 of 24 compounds as
  relative-stereo, silently, and T17 would receive that as fact. Now refused in a shared helper
  used by BOTH T13 and T15 rather than coerced.
- G-02 [92] The single line binding the recomputed flag to rows was untested; two reviewers
  independently showed that positional assignment kept the whole suite green. The implementation
  was correct; the test was missing.
Also fixed: atomicity of the export pinned (G-04), fixture key namespace asserted (G-05, the
namespace S5 assumes but never checked), fail-closed header check on the real tracked file (G-06),
broader-compounds direction (G-07), derived TRACKED_COLUMNS so the refusal and the projection
cannot drift (G-09), error-message parity and wording (G-10, G-11), branch-specific refusal
assertions (G-12), empty-file cases (G-13), formatting (G-14).

MUTATION EVIDENCE: I re-ran the three mutations that previously left the suite green. All three are
now killed. Two of my own tests passed VACUOUSLY before I caught them: one matched the tmp_path
DIRECTORY NAME (pytest names it after the test, so it contained the word I was asserting), and the
atomicity test twice failed to distinguish a non-atomic implementation — a failure that writes
nothing is indistinguishable from an atomic one, and building the worksheet inside the patched call
raised before the export ran. Both are recorded in the findings file as my own findings.

REJECTED: a HIGH finding claimed an uncommitted edit had deleted the atomic publish. Checked on
receipt: `git diff` empty, the block present on disk and in the commit, tree clean. It never
existed in any commit — see §5.

## 4. Six items for your ruling (NOT fixed; plan is yours)
G-15 [SEC] `write_adjudication_worksheet` validates `compounds` but never `out`, so it will write
  the worksheet shape — `name` at position 2, beside canonical_inchikey — to ANY path, including
  configs/pgp_adjudication.csv. The reviewer demonstrated it. No non-test caller exists today.
  Making the export the ONLY writer of a tracked path is the asymmetry that makes the r2.18 split
  load-bearing, but the obvious check (shelling out to `git ls-files` from library code) needs your
  call. I added the fail-closed test (G-06) as the cheap half.
G-16 T15's "Done when" still says "worksheet" three times; r2.18 changed the interface but not the
  neighbouring clause — the same class as the defect r2.18 repaired.
G-17 The extra-column refusal in `_read_tracked_adjudication` is UNSTATED in the plan. The design
  reviewer judged it justified (it is the only checkable reading of "five-column", and the export
  is bypassable by a human `cp`). Worth an r2.19 clause rather than code-only behaviour.
G-18 T14 is a HUMAN task whose helper has no CLI entry, so the path of least resistance is still
  hand-deleting columns — the accident it exists to prevent. The repo has an explicit precedent
  (`chipsim panel-seal`, C4). A new subcommand is not authorised by r2.18.
G-19 `read_pgp_labels` drops `stereo_is_relative`, so the flag T15 writes "so T17 receives it" is
  unreachable through the module's own reader.
G-20 A compound name typed into a CELL (adjudicated_by, evidence_doi) still reaches the tracked
  file. No column check can catch it; it belongs in T14's human instructions, which are yours.

## 5. Process finding (aiadlc feedback, your call whether to file)
Two reviewers ran MUTATION TESTS against the shared working copy — the tree the gate was hashing —
despite "do not fix anything". One restored byte-for-byte; the other's in-flight mutations were
observed by a third reviewer and produced a HIGH finding against a file state that never existed.
Mutation testing is genuinely valuable here: it is what proved G-02, G-04 and G-07 were real gaps,
and I adopted it. But it must run on a COPY. A mutation left behind at the wrong moment would be
signed into a receipt as the reviewed state, and Hash A/E would attest to it.

## 6. Disclosed, not silently fixed
`ruff format --check` fails on FIVE pre-existing files (chipsim/harmonize/ids.py,
chipsim/harmonize/merge_report.py, chipsim/ingest/drugbank_snapshot.py,
tests/test_merge_report_record_content.py, tests/test_parse.py). I formatted only the files this
iteration touched. Reformatting the rest would put unreviewed churn in a receipted diff. Note the
README declares `ruff format --check` part of the gate while the config's format_command is empty,
so earlier gates — including my §2 receipt — ran `ruff check` only. Your call on whether to fix the
five, the config, or both.
