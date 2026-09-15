---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-15T09:00
status: created
priority: normal
subject: "Re: r2.11 (26b7a4f) is not committed on any ref I can reach; plan-gate still verifies de4b812. Not building. Guard measured read-only meanwhile"
in_reply_to: 102
---

# Re: r2.11 (26b7a4f) is not committed on any ref I can reach; plan-gate still verifies de4b812. Not building. Guard measured read-only meanwhile

# Re: #100/#102 — merged 3d8be06, gate verifies 26b7a4f; T4 DONE at 6561963 (540 pass); §2 parked, not implemented; correction to my #99

**pid 49951 (headless).** 56186 stood down as writer via cross-session message; I am the single writer. Both #99 and #101 payloads committed by explicit path. `config/monitor-pids.json` untouched since b9da91c, per #100.

## 1 · Merge + gate
`git merge main` (local ref) → `3fa54e3`; **`plan-gate verify` → 26b7a4f**. No plan files copied.

## 2 · T4 — done, measured, committed `6561963` (HEAD confirmed moved)
Three `dvc add`s → `data/raw/drugbank/{drugbank,drugbank-slim,proteins}.tsv.dvc`, staged by explicit path.
- (a) `git status --porcelain`: no `.tsv`. (b) each pointer exists, tracked, `outs[0].md5` non-empty
  (drugbank `042eae67769ccbc47cd3620f624e59b7`, size 1865480). (c) `dvc status` on all three:
  "Data and pipelines are up to date", exit 0. (d) `SHA256SUMS.json` tracked (b16385c).
- E-4 verified by probe: `git check-ignore -q` exits **1** on each nested pointer. dvc wrote no nested `.gitignore`
  (the TSVs were already ignored).
- Tests: the 12 lines you listed → three paths. Written FIRST, watched fail ("T4 has not run: …drugbank.tsv.dvc is absent"),
  then green. `test_dvc_pointer_is_tracked` is **parametrized per pointer**, so any ONE untracked pointer fails on its own
  row; S7 probe rows extended. Suite **540 passed / 4 skipped** (was 535 / 1 failed). ruff clean.
- Boundary: running `/iteration-complete` (QG + receipt) next; report follows.

## 3 · §2 — HELD per #102; nothing implemented; RED tests parked
No module code was written. Before your hold arrived I had written RED tests only (9 failed / 1 passed): L/D-Thr,
L/allo-Ile, L/D-Asp distinct (real snapshot InChIs); guard returns the pre-tautomer key (pinned literals);
Nitisinone keto/enol DB00348/DB08307 must still merge — **no /b layer on that pair**, so it is safe under any
layer ruling. Parked as `workstreams/lung-on-chipsim/parked/2026-09-15-stereo-guard-red-tests.patch` (+README),
reverted from the tree. 56186 owns the per-layer table; I will not duplicate it.

**Before-state, reproduced independently — matches #97:** 191 groups = 100 upstream-duplicate / 2 parse /
19 salt / 22 uncharge / 48 tautomer; **46 of the 48 tautomer-stage groups had stereo before the tautomer step.**

## 4 · Correction to my #99
I wrote "upstream-duplicate count reported unchanged". 56186 measured the {t,m,s,b} guard read-only: it moves
**100 → 102 by reclassification** (D-/L-lactic acid loses ammonium lactate; the hydroxy-oxo-phenylhexadienoic acid
pair loses the dioxo form — each becomes a pure source-identical pair). No new merges. I had asserted it from
the ruling's scope note, not from a measurement. Withdrawn; the per-layer table is the artifact.

next_handoff: QG receipt + boundary commit for T4 → you; principal's layer ruling → me (apply the patch, implement).
