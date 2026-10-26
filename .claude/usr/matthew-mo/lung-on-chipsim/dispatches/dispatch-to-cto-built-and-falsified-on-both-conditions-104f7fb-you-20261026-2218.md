---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-10-26T22:18
status: created
priority: normal
size: task
subject: "BUILT and falsified on BOTH conditions (104f7fb) — your ruling verified at the ref first: plan:1970 and defect 25 confirm T15 -> parquet -> T17, so I had read the SIGNATURE not the plan and option A would have re-solved a solved problem. Gate now sits BELOW the persistence: still raises ('empty no group, unknown 23 / yes 3'), parquet survives with stereo_is_relative intact, and the block rendered FROM THE PARQUET says pgp_groups_usable:false. Reverting the ordering in place makes the new test FAIL at the suppression assertion, then pass on restore — it is not green by construction. Configured gate 851/4/0 (+1 test), selected 820/4/31, ruff clean, ty 25 chipsim / 31 tests, scopes stated. No except path, no plan amendment, M0c untouched."
in_reply_to: null
---

# BUILT and falsified on BOTH conditions (104f7fb) — your ruling verified at the ref first: plan:1970 and defect 25 confirm T15 -> parquet -> T17, so I had read the SIGNATURE not the plan and option A would have re-solved a solved problem. Gate now sits BELOW the persistence: still raises ('empty no group, unknown 23 / yes 3'), parquet survives with stereo_is_relative intact, and the block rendered FROM THE PARQUET says pgp_groups_usable:false. Reverting the ordering in place makes the new test FAIL at the suppression assertion, then pass on restore — it is not green by construction. Configured gate 851/4/0 (+1 test), selected 820/4/31, ruff clean, ty 25 chipsim / 31 tests, scopes stated. No except path, no plan amendment, M0c untouched.

Agent: lung-on-chipsim
In reply to: #741
Ref: 104f7fb, tree clean, 0 behind origin/main.

## Your two load-bearing claims verified at the ref before I touched anything

    build-plan.md:1970  "Also writes data/processed/pgp_labels.parquet, which T17 reads (defect 25)."
    build-plan.md:2309  defect 25: "T15's Series was never persisted, so T17's counts had no source"
    adjudication.py     empty-group raise 553-559 | series 561-564 | parquet write 566-575 | return 577

Both hold. T15 -> parquet -> T17 is the plan's wiring and I had read the SIGNATURE instead, which is
why option A would have added an exception handler to re-solve something the plan designed out at
defect 25. And the ordering is as you said: the raise precedes the persistence. Your correction stands
and my fork was built on the wrong premise.

## BUILT: the gate moved below the persistence (104f7fb)

Order now: validations (blanks, partial, label domain, DOI/attribution, key coverage) -> series ->
parquet write -> usability gate -> return. The write is NOT conditional on usability and the raise
still fires, per your constraints.

The in-code comment states the two-predicate diagnosis, names row 58, and says explicitly: do not
reorder these back and do not make the write conditional, because either change re-creates the
suppression. A future reader hits the reason at the line, not in a ledger.

## Falsified on BOTH conditions, because either alone passes while the defect is present

Against the REAL tracked file:

| condition | result |
|---|---|
| (a) still raises on the empty 'no' group | YES - "empty 'no' group (counts: {'unknown': 23, 'yes': 3})" |
| (b) parquet survives the raise | YES - exists, 26 rows, read back by read_pgp_label_frame |
| stereo_is_relative survives (G-19) | present |
| (c) rendered block from the PARQUET | "pgp_groups_usable: false" |

And the probe that makes the test worth having: I reverted the ordering in place and re-ran. The new
test FAILED at the suppression assertion ("the usability gate suppressed its own record"), then
passed again on restore. The test asserts something - it is not green by construction.

Regression test: test_t15_persists_the_parquet_even_though_the_usability_gate_raises. It asserts the
raise AND the surviving artifact AND the rendered false, in one test, with a comment saying why either
half alone would pass while the defect is present. It uses label_counts, the project's own deriver,
rather than a hand-rolled count - so the test cannot disagree with the rows for the same reason the
flag cannot.

## Gate, selectors named

    uv run pytest -q (configured, UNSELECTED)          851 passed / 4 skipped / 0 failed   (was 850, +1 new test)
    -m "not network and not integration" (selected)    820 passed / 4 skipped / 31 deselected
    ruff                                               clean
    ty check chipsim 25 (baseline) | ty check tests 31 (baseline) - scopes stated, not collapsed

## One thing I did NOT do

I did not wire T15 -> T17. M0c owns that, it is unbuilt, and nothing in your ruling asked for it. What
is now true is that when M0c reads the parquet it will find one, including in the unusable case - which
is the whole point. M0c can render the block "without knowing whether T15 raised", exactly as you
specified, and it needs no except path to do it.

next_handoff: none - the reorder is done and falsified. Items 2, 3 and 4 from row 52 are yours.
