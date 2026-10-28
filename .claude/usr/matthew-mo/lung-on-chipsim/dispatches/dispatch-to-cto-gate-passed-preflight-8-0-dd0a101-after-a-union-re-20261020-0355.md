---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-10-20T02:55
status: created
priority: high
size: task
subject: "Gate PASSED (preflight 8/0, dd0a101 after a union-resolved docs/hacp/decision.md conflict). A1 transfer STOPPED BEFORE FIRST COPY: measured gap is 71 files, manifest covers 25, 16 excluded, 6 transport — and 24 are named NEITHER way, ~10 of them being the TESTS FOR MANIFEST-NAMED ITEMS. Also: the manifest's parquet sidecar has no referent on either ref. Scope ruling needed."
in_reply_to: null
---

# Gate PASSED (preflight 8/0, dd0a101 after a union-resolved docs/hacp/decision.md conflict). A1 transfer STOPPED BEFORE FIRST COPY: measured gap is 71 files, manifest covers 25, 16 excluded, 6 transport — and 24 are named NEITHER way, ~10 of them being the TESTS FOR MANIFEST-NAMED ITEMS. Also: the manifest's parquet sidecar has no referent on either ref. Scope ruling needed.

Agent: lung-on-chipsim
next_handoff: biofm/matthew-mo/cto

# Step 1 and the gate are DONE — preflight 8/0, "Session ready". A1's transfer is STOPPED BEFORE THE FIRST COPY: the manifest is incomplete against the real gap, and 24 files are named neither way. Scope ruling needed before one scoped unit can be one.

## Gate passed

`lung-on-chipsim` @ **dd0a101**. Worktree, `.aiadlc-agent` and branch all agree — *"✓ On the agent's 'lung-on-chipsim' branch"*, *"✓ Running in a linked worktree"*, **8 passed / 0 failed, "Session ready."**

Getting there needed one thing you did not anticipate: preflight failed on **67 behind origin/main** (you had pushed; `origin/main` moved to `9680679`). `worktree-sync` hit a conflict and auto-aborted cleanly. The conflict was `docs/hacp/decision.md` and it was **not** a pick-a-side — **both** sides are CTO-authored about different subjects: my lineage carried 5 decision rows (A7 review, perturb-seq-eval S1, deposit timing, Stage 1 archive, F08), `origin/main` added 2 (perturb-seq-eval v0.6.0 D-1/D-2). I checked the table's convention (reverse-chronological), unioned them with your 2026-10-16 rows first, verified all 7 rows survived by count and that no markers remained. Merged, never rebased. Commit `dd0a101`.

## The measured gap: 71 files, and the manifest covers 25 of them

I did not take the manifest as the gap. I measured it — `comm` over `git ls-tree` on both refs — and classified every file:

| bucket | files | disposition |
|---|---|---|
| **manifest-named** | **25** | transfer — roster.py, the 3 DVC pointers + SHA256SUMS.json, label_structure_reference.yaml, unparseable_compounds.yaml, harmonize/{label_reference,merge_report}.py, chipsim/audit/ (5), tests/audit/ (4), configs/templates/ (S13/S14), the T13 CLI test + tracked-adjudication test + 8 adjudication fixtures |
| **A1-excluded** | **16** | leave out — chipsim/guards/ (8), record_content.py, shape_scan.py + its test, record_content_declarations.yaml, the record-content tests |
| **transport — stop** | **6** | `chipsim/transport/` (2: `ode.py`, `fit.py`) + 4 `tests/test_transport_*.py` |
| **RESIDUE — named by neither** | **24** | **needs your ruling** |

**The parquet sidecar in the manifest does not exist as a file on either ref** — no `*.parquet` anywhere under the project. `adjudication.py` says it *writes* `data/processed/pgp_labels.parquet`, so it is a generated artifact, not a transferable one. The manifest line has no referent; I am not inventing one.

## Why I stopped before copying anything

A1 says the transfer runs as **ONE scoped unit**. It cannot be one unit while 24 files in the gap are unassigned — and the residue is not miscellaneous. **Roughly ten of them are the tests for manifest-named items:**

- `test_label_reference_committed.py` → tests `harmonize/label_reference.py` *(named)*
- `test_merge_report.py` → tests `harmonize/merge_report.py` *(named)*
- `test_unparseable_exclusions.py` → tests `unparseable_compounds.yaml` *(named)*
- `test_structure_pattern_differential.py`, `test_relative_stereo.py`, `test_relative_stereo_downstream.py`, `structure_reference.py` → test `label_structure_reference.yaml` *(named)*
- `test_theta_scaffold.py`, `test_theta_config.py`, `fixtures/theta_SYNTHETIC_not_literature_sourced.yaml` → test the S13/S14 templates *(named)*

**Transferring the manifest without these moves named items across without the checks that prove they work.** That is a half-transfer of exactly the shape this project keeps hitting — a thing moved without its verification — and doing it quietly would be the mechanism again, on the first action after Stage 1 closed on a note about it.

A second group follows the **exclusions** rather than the manifest, by the same logic: `test_claims_vs_records.py`, `test_redact_records.py`, `test_bracket.py`, `test_record_bearing_writers.py`, `readability_reference.py`, `test_readability_differential.py` are tests of the E-21..E-23 gate instruments A1 excludes. Including them would drag the excluded tooling back in by its tests.

A third group I genuinely cannot place from the manifest: `configs/poc_compounds.yaml`, `data/processed/drugbank_compounds.sha256`, `tests/association_reference.py`, `tests/fixtures/snapshot/SOURCES.md`, `test_accession_pattern_matrix.py`, `test_fixture_sources.py`, `test_generated_columns.py`, `test_run_approval.py`.

## What I recommend, not what I have done

1. **Extend the unit to include the ~10 tests-of-named-items.** A named item and its test are one thing; splitting them makes two half-units.
2. **Extend the exclusion to the ~6 tests-of-excluded-tooling**, for the symmetric reason.
3. **Rule the remaining ~8 individually** — I will not guess, and they are small enough to decide in one pass.
4. **Strike the parquet-sidecar line** or point it at a real path; it currently refers to nothing.
5. Then I run it as one unit, honour the exclusions, and **stop at `transport/`** — where the shape is confirmed and **A2's "only copy" clause is half false**, so A2 needs restating or retiring before the per-file calls are put to the principal.

**Nothing copied, nothing excluded, nothing pushed.** The only commit is the sync merge. Holding for the scope ruling.
