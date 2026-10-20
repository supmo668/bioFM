---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-10-20T08:31
status: created
priority: high
size: task
subject: "adjudication.py diff shape: stage1 is a STRICT SUPERSET (9 extra symbols, ZERO stage2-unique; the 26 stage2-only lines are pre-hardening forms; param rename safe — every HEAD caller is positional or docstring-only). STOPPED for the principal. SCOPE CORRECTION: divergent set is 24 files NOT five — five came from what broke, not a scan — and A1 names FIVE of them for transfer, incl. both S13/S14 templates. pyproject.toml + uv.lock divergent too."
in_reply_to: null
---

# adjudication.py diff shape: stage1 is a STRICT SUPERSET (9 extra symbols, ZERO stage2-unique; the 26 stage2-only lines are pre-hardening forms; param rename safe — every HEAD caller is positional or docstring-only). STOPPED for the principal. SCOPE CORRECTION: divergent set is 24 files NOT five — five came from what broke, not a scan — and A1 names FIVE of them for transfer, incl. both S13/S14 templates. pyproject.toml + uv.lock divergent too.

Agent: lung-on-chipsim
next_handoff: biofm/matthew-mo/cto

# adjudication.py diff shape reported, STOPPED for the principal as instructed. And the divergent set is **24 files, not five** — the five came from what happened to break, not from a scan.

## 1. adjudication.py — the diff shape

| | stage1 | stage2 (HEAD) |
|---|---|---|
| lines | **649** | **286** |
| top-level symbols | 21 | 12 |
| symbols the other side lacks | **9** | **0** |

**Only on stage1:** `export_tracked_adjudication`, `TRACKED_COLUMNS`, `EXPORT_DROPPED_COLUMNS`, `GENERATED_COLUMNS`, `WRITTEN_COLUMNS`, `read_pgp_label_frame`, `_read_tracked_adjudication`, `_exclusive_temp`, `_relative_by_key`.

**Only on stage2: nothing.** Not one symbol.

**The 26 stage2-only LINES are not features — they are the pre-hardening forms of functions stage1 also has.** Examples: stage2 writes its temp file as `out.with_name(out.name + ".tmp")` where stage1 routes through `_exclusive_temp(out)`; several of stage2's error strings are stage1's, rephrased. So on the evidence **stage1 is a strict evolution of stage2's version**, not a divergent branch of it.

**Compatibility, checked rather than assumed:**
- `adjudicate_pgp_labels`' first parameter is **renamed** — stage2 `worksheet`, stage1 `adjudication`. That breaks keyword callers.
- The only HEAD callers are `tests/test_adjudication.py`, which calls it **positionally** (`adjudicate_pgp_labels(FIXTURES / "...")`), and `chipsim/harmonize/pgp_label.py`, which **only mentions it in docstrings and never calls it.** So the rename is safe for every actual caller on HEAD.
- `read_pgp_labels` and `write_adjudication_worksheet` signatures match.

**My reading — not a decision, and I have changed nothing:** taking stage1's version wholesale looks like the correct reconciliation, because it is a superset in symbols, a hardening in the shared bodies, and compatible with every real caller. It also restores `export_tracked_adjudication` and so **unblocks D6**. The one caveat is below.

**The caveat: `tests/test_adjudication.py` is ITSELF divergent** (stage1 `79d5496` / HEAD `ffc9dd5`). So the module and its test are *both* live, and reconciling the module while leaving stage2's test is the half-reconciliation equivalent of the half-transfer we already caught. They should be decided together.

## 2. The scope correction: the divergent set is 24 files, not five

I had five. **Five was the count of modules that happened to raise ImportErrors** — i.e. derived from what broke during collection, not from a scan. So I scanned: `git ls-tree -r` on both refs, joined on path, blob hashes compared.

**24 files are present on both refs with different content.** None is in my 41-file unit — disjoint, confirmed, consistent with the commit's 41 A / 0 M.

| area | count | includes |
|---|---|---|
| production code | **8** | `adjudication.py`, `ids.py`, `pgp_label.py`, `roster.py`, `drugbank_snapshot.py`, **`pipeline.py`**, `transport/prior.py`, `transport/theta.py` |
| tests | **9** | `test_adjudication.py`, `test_provenance.py`, `test_scaffold.py`, `test_snapshot_fetch.py`, `test_fixtures.py`, `test_journal.py`, `test_parse.py`, `test_monotonicity.py`, `test_workflow_export.py` |
| config / build | **7** | **`pyproject.toml`**, **`uv.lock`**, `configs/templates/theta_priors.scaffold.yaml`, `configs/templates/transport_prior.scaffold.yaml`, `data/raw/sources.yaml`, `README.md`, `docs/adr/0003-...md` |

**Why this is worse than a bigger number.** The gap method cannot see divergence **by construction** — I built the 71-file gap as "on stage1, absent on HEAD", so anything present on both was invisible to it. The five surfaced only because they broke an import. **A divergent file that nothing imports would never have appeared at all**, and `pipeline.py`, `README.md` and the two scaffold templates are exactly that shape.

**And A1 names five of the 24 for transfer:** `roster.py`, **both** `configs/templates/*.scaffold.yaml` (the S13/S14 templates), `data/raw/sources.yaml`, and `docs/adr/0003-power-floor-and-stratified-roster.md`. So `roster.py` was not a one-off — **A1's presence-vs-absence assumption misclassifies five items, not one.**

**`pyproject.toml` and `uv.lock` are divergent**, so the two sides may not even resolve the same dependency set. That should probably be reconciled before any test result from either side is trusted as evidence.

## 3. What I need, and what I have not done

1. **`adjudication.py` + `test_adjudication.py` together** — the principal's call. My reading is "take stage1's" with the reasoning above, but I have **not** merged in either direction and will not on my own authority.
2. **Re-scope the reconciliation to 24 files, not 5 + transport.** `transport/` is 2 of the 24 (`prior.py`, `theta.py`) plus 2 Stage-1-only additions (`ode.py`, `fit.py`) and 1 Stage-2-only file (`sourcing.py`).
3. **`pyproject.toml` / `uv.lock` first, or at least before trusting suite results.**
4. **A2 AND A1 to the principal together, as agreed, now with the sharper form:** A2's "only copy" clause is **half false**; A1's presence-vs-absence assumption is **wrong in five named places**. Both need restating or retiring before the per-file calls are settled.

**Nothing merged, nothing reverted, nothing pushed.** `97fe634` stands as ruled. Suite still red, cause unchanged. `transport/` untouched.
