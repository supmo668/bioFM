---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-10-15T05:13
status: created
priority: normal
size: task
subject: "Stage 2 UNPARKED: branch lung-on-chipsim-stage2 cut + worktree ready, r3 signed (4bfa583); scan PASS; clean suite 476 pass / 1 PRE-EXISTING fail (question for you); pivot decisions 1-3 recorded, 4 still open"
in_reply_to: null
---

# Stage 2 UNPARKED: branch lung-on-chipsim-stage2 cut + worktree ready, r3 signed (4bfa583); scan PASS; clean suite 476 pass / 1 PRE-EXISTING fail (question for you); pivot decisions 1-3 recorded, 4 still open

# Stage 2 is UNPARKED. Branch cut, plan r3 signed, worktree ready. Read this before anything.

## Your working surface

| | |
|---|---|
| Branch | `lung-on-chipsim-stage2`, cut from `main` and pushed |
| Worktree | `worktrees/lung-on-chipsim-stage2/` |
| Plan | r3, **signed**, hash `4bfa583` — `plan-gate verify` green on this branch |
| Do NOT use | `worktrees/lung-on-chipsim/` — that is the archived Stage 1 branch. Stage 1 is closed. |

A1 is executed. The 13 commits of Stage 2 work from `claude/inspiring-archimedes-h0we1b` are merged in (M1 input contracts and tests, the sourcing worksheet, the experiment setup, the 2026-10-04 rulings, the 2026-10-14 vision and methodology). A1 predates that work and only spoke of taking Stage 1 files by content — merging it is my reading of A1 extended to work it did not anticipate, recorded as such in §7b.

## Two measurements I ran, so you do not have to trust a claim

- **`scan-artifacts.py` at the archived tip: PASS.** `shapes_on_audit_surface: 0`, `could_not_scan: 0`. A1's precondition, run by me, not taken from the record.
- **Clean suite on this branch: 33.6 s wall, 476 passed, 8 skipped, 1 FAILED.** No concurrent pytest processes — this is the clean re-measurement owed since 2026-10-01. The old "453 s clean vs 900 s killed under 23 concurrent processes" comparison is retired; neither number was comparable.

**The one failure, and a question for you.** `tests/test_snapshot_fetch.py::test_t4_dvc_pointer_tracks_the_snapshot` asserts `data/raw/drugbank.dvc` exists ("T4 has not run"). That pointer is tracked on **neither** `main` nor the design branch. I proved the failure is **pre-existing on `main`** by running that single test in a clean detached `main` checkout, so my merge did not cause it.

But your commit `d271d80` says "resolve the three pre-existing test failures" and reported **447 passed, 0 failed**. The assertion is `pointer.is_file()` on a path tracked nowhere — so that pass may have depended on **untracked files sitting in your worktree**, not on committed state. If so it is the same shape as the `.pyc` finding in aviary-biosim: a check that passes on local state and fails on a clean checkout. **Answer this before building anything**: was the pass real, or environmental?

## The design direction changed. Decisions 1-3 are RECORDED; 4 is still the principal's.

Recorded in `workstreams/lung-on-chipsim/approvals.md` (rows 1-3), from the principal's structured 1B1 of 2026-10-13:

1. **Endpoint: matched pairs, route-restricted.** Primary = discrimination across matched structural pairs within the respiratory route (ATC-R), using the on-disk DrugBank extract. Published on-chip orderings (T21) are demoted to **later external validation**, not a blocking input. Declined: global approved-vs-non-approved (approval mixes efficacy, safety and commercial factors, so a good score need not mean the transport component is right), route-restricted approved-vs-failed (I measured only **8** negatives with ATC-R), and orderings-only (egress-blocked).
2. **Data route: the principal adjudicates the 26 P-gp rows by hand**, each with its `adjudicated_label` and evidence DOI. No agent-drafted verdicts, no fetch route to establish. Every row in `data/interim/pgp_adjudication.csv` currently carries an empty label and reads `unresolved`.
3. **Claim shape: TWO-STAGE.** Stage 1 = matched-pair discrimination on the efflux axis, gated and publishable alone. Stage 2 = the transport fit for delivered exposure, retained in the claim, **not** on the critical path now. Consequence: **the six Huh-chip θ fields, the transport prior and the reference compounds come OFF the critical path.** Do not spend effort sourcing them.

**4 (OPEN — do not build it):** the acceptance test. My recommendation to the principal is a sign test over discordant pairs with the floor fixed by power simulation *before* the model sees the labels, and the subgroup coverage criterion living where the ~20-points-per-group allocation exists rather than at n=26. **Until they rule, build no acceptance test and pre-register no threshold.**

## The methodology decision is load-bearing — read it, do not skim it

`docs/hacp/lung-on-chipsim/methodology-2026-10-14.md`, now on `main` as well. Three things that change the build:

- **Embeddings are a hypothesis, not the architecture.** They enter as one arm of a pre-registered comparison against descriptors and fingerprints. Do not build on them as the method.
- **The `k_sink` single-constant model is refuted by its own primary source**, verbatim: a single constant "will not capture these dynamic concentration distributions". Options A/B/C are on the page; the recommendation is **B** (keep one constant, state the limitation in the authors' quoted words) with **C** as the protocol recommendation — **but the principal has not ruled, and the `k_sink` prior stays empty until they do.** This is stage-2 territory anyway under decision 3.
- **Absolute permeability does not transfer across platforms** (a ~40-fold spread in the chip-to-animal ratio across three compounds). Ratios and **rank ordering** transfer. This independently vindicates the ordering endpoint — the literature and the data arrived there separately.

## Your next actions, in order

1. Answer the `test_t4_dvc_pointer` question above. If the pass was environmental, say so plainly and fix the test or the tracked state — do not quietly make it green.
2. `/session-resume` in the new worktree; confirm `plan-gate verify` green and the suite at the numbers above.
3. Then the week-1 work r3 confirms under B2/B3/B4: emit the typed templates and their validators. **Note:** under decision 3 the θ and transport-prior templates are no longer urgent; the one that matters is whatever the matched-pair endpoint needs.
4. Build nothing that depends on decision 4.

Nothing here authorises a wet-lab claim, a biological number, or a threshold. Report back when step 1 is answered.
