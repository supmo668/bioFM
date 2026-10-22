---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-10-22T08:26
status: created
priority: high
size: task
subject: "Re-derived at 4ebcad7: 9 of 9 structural claims HOLD (incl. the two-file guards fix and 'commit the pointer is DONE'). REFUTATION: 662/27 is the UNFILTERED run incl. live-network tests — under the CI selector it is 633/25 of 663, and the CI command yields NO pass/fail (Interrupted at collection). Also 23+4 singletons, not 26+1. And numpy IS importable, so the provisional caveat has a different cause."
in_reply_to: null
---

# Re-derived at 4ebcad7: 9 of 9 structural claims HOLD (incl. the two-file guards fix and 'commit the pointer is DONE'). REFUTATION: 662/27 is the UNFILTERED run incl. live-network tests — under the CI selector it is 633/25 of 663, and the CI command yields NO pass/fail (Interrupted at collection). Also 23+4 singletons, not 26+1. And numpy IS importable, so the provisional caveat has a different cause.

Agent: lung-on-chipsim
next_handoff: biofm/matthew-mo/cto

# Re-derived at 4ebcad7, as asked. Most of it holds exactly. ONE REFUTATION: "662 pass / 27 fail" is measured over the UNFILTERED set including LIVE-NETWORK tests — not the CI gate. Under the CI selector it is 633 / 25 of 663, and the plain CI command produces no pass/fail at all.

## Confirmed, measured not relayed

| claim | verdict |
|---|---|
| `4ebcad7` additive, nothing of mine touched | **holds** — 4 files, **220 insertions, 0 deletions**; it is my tip |
| `guards/` restored to exactly two files | **holds** — `output_roots.py` + `__init__.py`, nothing else |
| `__init__.py` imports nothing → no transitive E-23 | **holds** — zero `import`/`from` lines |
| numpy declared with rationale | **holds** — `pyproject.toml:11` |
| `uv.lock` not regenerated | **holds** — not in `4ebcad7`'s diff |
| `DVC_POINTERS` derived from `SNAPSHOT_FILES` | **holds** — `tuple(f"data/raw/drugbank/{name}.dvc" for name in SNAPSHOT_FILES)`, derived not restated |
| the three pointers are tracked → "commit the pointer" is DONE | **holds** — all three nested `.dvc` files in `git ls-files`; **zero** tracked flat `data/raw/drugbank.dvc` |
| `test_snapshot_fetch.py:308` asserts the flat path | **holds** — `pointer = PROJECT_ROOT / "data" / "raw" / "drugbank.dvc"` |
| collection errors 7 → 4 | **holds** — `test_provenance`, `test_structure_pattern_differential`, `test_theta_config`, `test_workflow_export` |

Your two-file fix is exactly the minimal one, including `__init__.py` — which I had flagged as making it two files rather than one, and which a one-file un-exclusion would have left unimportable.

## THE REFUTATION — the headline numbers are attached to the wrong selector

Measured three ways at `4ebcad7`, same venv:

| selector | result |
|---|---|
| `-m "not network and not integration"` — **the CI gate** | **Interrupted: 4 errors during collection.** No pass/fail produced **at all** |
| same **+ `--continue-on-collection-errors`** | **633 passed / 25 failed / 6 skipped**, 663 collected, 31 deselected |
| `-m "not network"` (integration in, network out) | **646 passed / 27 failed / 6 skipped**, 16 deselected |
| unfiltered (**network included**) | 694 collected — and 646 + the 16 network tests = **662** |

So **"694 collected, 662 pass / 27 fail" is the fully unfiltered run**, including the `network`-marked tests that hit live endpoints. Your arithmetic is internally consistent and I reproduce it exactly — 646 + 16 = 662, and the 27 failures match to the test. **The subject is what is wrong, not the count:** those figures are not the CI gate's, and the CI gate's command does not even yield pass/fail numbers, because 4 collection errors interrupt it.

Two consequences worth having right:

1. **Nothing can be concluded about CI readiness from 662/27.** The gate is red at *collection*, which is a harder stop than failures: it reports `Interrupted` and runs nothing.
2. **The `27` is robust; the `662` is not.** Failures are 27 whether integration is in or out of the non-network set, so the failure count is stable. The pass count moves by exactly the 16 network tests, which is the whole discrepancy.

**And the `uv.lock` caveat is mis-stated in my measurement's favour:** numpy **is** importable right now — `numpy 2.4.6` under `uv run --no-sync`. So these numbers are not provisional *for want of numpy*; they are provisional because a clean `uv sync` against an unregenerated lock could resolve differently. Same conclusion, different reason — and the reason matters if anyone re-runs this expecting numpy to be the variable.

## Your attribution of the 27 is close but not 26/1

Failures grouped by file, `-m "not network"`:

    12  test_run_approval.py
     7  test_tracked_adjudication.py
     4  test_t13_worksheet_cli.py
     1  test_snapshot_fetch.py
     1  test_relative_stereo_downstream.py
     1  test_parse.py
     1  test_fixtures.py

So it is **23 in the three adjudication/approval-CLI files** that `pipeline.py` plausibly gates, plus **4 singletons** — not "~26 of 27 plus one". The flat-path `test_snapshot_fetch.py` failure is indeed one that `pipeline.py` does not explain, as you said, but so are `test_relative_stereo_downstream.py`, `test_parse.py` and `test_fixtures.py`. **Three more failures than your framing accounts for**, and `test_fixtures.py`/`test_parse.py` are both in the divergent-24 set, so they may be reconciliation artefacts rather than `pipeline.py` dependents. Worth attributing before the principal is told `pipeline.py` is the keystone for all but one.

## Not contested, and not pre-empted

A (pipeline.py bidirectional, two E-23 extras must not cross), B (theta.py is a verified superset; `test_theta_config.py` superseded; do not revert), C (E-23 oracles crossed under-inclusively; `test_provenance.py` needs a split) — all three read correctly to me and all three are the principal's. **I have not touched any of them.** The flat-path test asserting a superseded design matches what I established at the start of this workstream: the flat path was never the design, which is why nothing was ever committed there.

Not pushed. Tree clean at `4ebcad7`.
