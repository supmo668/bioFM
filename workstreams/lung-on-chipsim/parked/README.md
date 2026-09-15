# Parked work — lung-on-chipsim

## 2026-09-15-stereo-guard-red-tests.patch — §2 stereo guard, RED tests only — **APPLIED 2026-09-15 at `7592f56`** (ruling CTO #106: {t,m,s}, /b excluded); patch file removed, content lives in `tests/test_parse.py` + `tests/test_merge_report.py`

Dispatch #98 §2 ruled a stereo guard on `canonical_inchikey`; CTO #102 §2 put the
**implementation on HOLD** pending the principal's ruling on which InChI stereo layers
are compared ({/t,/m,/s} alone, {/b} alone, or all four). No module code was written.

What the patch holds (written test-first, HEAD 3fa54e3). RED state per file:
`tests/test_parse.py` — 9 failed / 1 passed (the Nitisinone regression guard passes today);
`tests/test_merge_report.py` — **collection error**, not failures: it imports `MERGE_STAGES` and
`merge_stage_report` from `chipsim.harmonize.ids`, neither of which exists yet. Expect the
ImportError on resume; it is the RED for that half, not a bad patch.
- `tests/test_parse.py`: L/D-threonine, L/allo-isoleucine, L/D-aspartate stay DISTINCT
  (snapshot InChIs, identified here by InChIKey — see note); the guard returns the
  PRE-tautomer InChIKey (pinned literals, rdkit 2026.3.5); Nitisinone keto/enol
  (`OUBCNLGXQFSTLU-UHFFFAOYSA-N` PubChem CID 115355 / `PMHVFNYNPNKNRO-UHFFFAOYSA-N`
  CID 5289053, no /b layer) must STILL merge — passes today, regression guard.
  - isoleucine / allo-isoleucine: `AGPKZVBTJJNPAG-WHFBIAKZSA-N` / `AGPKZVBTJJNPAG-UHNVWZDZSA-N`
  - L- / D-aspartate: `CKLJMWTZIZZHCS-REOHCLBHSA-N` / `CKLJMWTZIZZHCS-UWTATZPHSA-N`
  - threonine pair: `AYFVYJQAPQTCCC-STHAYSLISA-N` (as pinned at `7592f56`) / `AYFVYJQAPQTCCC-PWNYCUMCSA-N`

  **Note (forward fix, CTO #122 §4, 2026-09-15).** This entry originally identified the
  pairs by DrugBank accession; accessions are DrugBank record content and were replaced
  with InChIKeys (this file was already on origin, so the change is forward-only). The
  threonine labels above are DrugBank's and are wrong twice: the "L-" member is a
  relative-stereo (`/s2`) string that the pipeline then keyed as D-threonine's
  `…-STHAYSLISA-N` — since the relative-stereo re-key (`1b74814`) it keys stereo-free
  `AYFVYJQAPQTCCC-UHFFFAOYSA-N` — and the "D-" member's structure is D-allothreonine
  (PubChem CID 90624). Wording left as historical; the test rename is held (#122 §6).
- `tests/test_merge_report.py`: `merge_stage_report` — one row per merge group with the
  stage it merges at (`upstream-duplicate | parse | salt | uncharge | tautomer`).

Before-state on the real snapshot (reproduced independently, matches CTO #97):
191 groups = 100 upstream-duplicate / 2 parse / 19 salt / 22 uncharge / 48 tautomer;
46 of the 48 tautomer-stage groups had stereo layers before the tautomer step.

Resume: `git apply workstreams/lung-on-chipsim/parked/2026-09-15-stereo-guard-red-tests.patch`
from the repo root, re-run the RED, then implement per the principal's layer ruling.
