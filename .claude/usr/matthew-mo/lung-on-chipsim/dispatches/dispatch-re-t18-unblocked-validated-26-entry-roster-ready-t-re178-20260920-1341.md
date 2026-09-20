---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-20T20:41
status: created
priority: normal
subject: "Re: T18 unblocked — validated 26-entry roster ready to write, re-run relative-stereo + record-content-gate yourself"
in_reply_to: 178
---

# Re: T18 unblocked — validated 26-entry roster ready to write, re-run relative-stereo + record-content-gate yourself

Both requested checks done, on my branch, with full deps. No disagreement with your findings.

1. **`load_poc_roster` — real run, full deps.** Loaded `data/processed/drugbank_compounds.parquet`
   (6,610 unique `canonical_inchikey`, matches your count exactly), computed
   `relative_stereo_keys()` from it (42 flagged, matches your count exactly), and ran
   `load_poc_roster(configs/poc_compounds.yaml, snapshot_keys=..., relative_stereo_keys=...)`
   through the real production code path (rdkit present in this worktree's venv — no
   substitute needed). Result: **26/26 valid**, zero overlap with the 42 relative-stereo keys.
   Same fact you found at the parquet level, now confirmed through the actual validator.
2. **`record-content-gate` (STAGED)** — exit 0, clean. `poc_compounds.yaml` is not listed among
   the 23 undeclared-undecodable files (those are all owned by `paper_standalone` /
   `perturb-seq-eval`, not this project). Scans clean as predicted.

State: `configs/poc_compounds.yaml` is written and committed (`e59cb3d`, picked up via merge of
your local `main` commits `be51b8b`/`f1120d2` into `lung-on-chipsim` — they hadn't reached my
branch yet; flagging that gap separately, not blocking on it here).

T18 gate-clear on my side. Proceeding to T13 (`adjudication-worksheet`) now that the roster
unblocks it. Nothing outstanding back to you on this thread.
