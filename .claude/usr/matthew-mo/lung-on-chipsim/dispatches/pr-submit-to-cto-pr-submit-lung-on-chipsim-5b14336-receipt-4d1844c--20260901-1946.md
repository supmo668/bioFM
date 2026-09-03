---
type: pr-submit
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-02T02:46
status: created
priority: high
size: task
subject: "PR-SUBMIT: lung-on-chipsim @ 5b14336 — receipt 4d1844c verified, gate 50dbaec, pushed. Slice 1 NOT closed by this merge."
in_reply_to: null
---

# PR-SUBMIT: lung-on-chipsim @ 5b14336 — receipt 4d1844c verified, gate 50dbaec, pushed. Slice 1 NOT closed by this merge.

Agent: lung-on-chipsim
PR-SUBMIT — ChipSim M0 slice 1, agent-side complete against fixtures.

branch:      lung-on-chipsim
head_sha:    5b143362f6d76238178c1dfd86acd3611a5bbf82
pushed:      github.com/supmo668/bioFM (new branch)
receipt:     workstreams/lung-on-chipsim/qgr/bioFM-matthew-mo-lung-on-chipsim-lung-on-chipsim-bioFM-qgr-pr-prep-20260901-1853-4d1844c.md
hash_e:      4d1844c
plan_gate:   50dbaec (r2.4) — verified green
tree:        clean

## Note on the receipt — fdee167 was already superseded

You flagged fdee167 as stale because T7a landed after it. It had already been re-signed: T7a is in
4d1844c, which I signed at 18:53 immediately after committing d1074cc. I re-verified rather than
assuming — receipt-verify passes, tree clean, plan-gate green. No new gate run was needed, and I did
not run one to look busy.

## PR BODY — landing does NOT close slice 1

Use this verbatim if it helps:

---
**ChipSim M0 slice 1 — DrugBank data spine through compound identity and the barrier-panel layer.**

**This merge does not close slice 1.** It lands the agent-implementable half; the human-owned half is
absent by design and nothing has been fabricated in its place.

- 29 CA tasks **+ T7a** (panel seal) complete against committed fixtures
- **298 passed / 6 skipped** offline, **15 passed / 1 skipped** network-marked, `ruff check` and
  `ruff format --check` clean
- **Five human artifacts absent by design** — T2 (pin snapshot commit), T1 (licence posture), T8
  (ratify accessions AND faces), T18 (curate PoC roster), T14 (adjudicate P-gp labels)
- **T4a/T4 blocked on T2**, with `skipif` keyed to the artifact so they **self-lift** when it appears
  rather than sitting silently green
- `configs/barrier_panel.yaml` ships **`ratified: false`**
- **The pipeline is implemented end to end and cannot execute a single stage** until T2 pins the
  snapshot commit. All five stages exist and are tested; execution stops before the first.
- Plan-gate verified green at **`50dbaec`** (r2.4)

T19 verifies each panel accession against the live UniProt API for taxon and gene symbol. **That is a
mechanical check, not a ratification.** The panel remains unratified until a human completes T8.
---

## What changed since your last look (P0.3 gate + T7a)

- **DVC remote portability/disclosure** — url moved to gitignored `.dvc/config.local`; the
  tautological test pinning the literal path deleted; the two real guards now skip cleanly when no
  url is configured. Your E-5 data-loss property is intact.
- **Biological numbers removed from `configs/barrier_panel.yaml`** — relocated to
  `workstreams/lung-on-chipsim/T8-review-record.md`. AM-3 rules that file carries identity, not
  quantities; comment form dodged the validator, not the rule.
- **`load_ratified_panel` validates entries** — a single missing `face` previously became NaN and
  flowed downstream silently; also rejects out-of-domain faces and duplicate symbols.
- **First `face` assertion on the LIVE config** — it had none of any kind, offline or network.
- **Fixture faces propagated to r2.3's T7**, and `test_fixture_face_agreement_with_live_panel`
  unskipped and enforcing.
- **T7a panel seal** — `panel_digest`, `seal_panel`, mismatch detection in `load_ratified_panel`, and
  a `panel-seal` CLI subcommand. Declared in `NON_ETL_SUBCOMMANDS` so it can never enter the n8n
  workflow — an unattended pipeline must not be able to invoke the act of attestation.
- **README correctness pass**, incl. the `data/ ... never in git` claim, which was false and was
  verbatim the misconception that produced F-01.

## HELD OUT of this PR, deliberately

The principal's new requirement — per-run config snapshots — is built (250 lines) and **not
committed**. It is unplanned scope with no task and no review, and dropping it in would have made the
PR body above false. Escalated separately; awaiting your task ruling.

## After you land

Standing by. Not starting slice 2. T9/T10 still refused against an unratified panel. Global
Constraint (4) stands — I will not run `panel seal` against the live config.

Next per your sequencing: `/design` for `chipsim-lbm-audit`, referencing the Linear project you
created.
