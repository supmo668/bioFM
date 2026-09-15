# Parked work — lung-on-chipsim

## 2026-09-15-stereo-guard-red-tests.patch — §2 stereo guard, RED tests only (HELD by CTO #102)

Dispatch #98 §2 ruled a stereo guard on `canonical_inchikey`; CTO #102 §2 put the
**implementation on HOLD** pending the principal's ruling on which InChI stereo layers
are compared ({/t,/m,/s} alone, {/b} alone, or all four). No module code was written.

What the patch holds (written test-first, watched fail — 9 failed / 1 passed, HEAD 3fa54e3):
- `tests/test_parse.py`: L/D-threonine, L/allo-isoleucine, L/D-aspartate stay DISTINCT
  (real snapshot InChIs, DB00156/DB03700, DB00167/DB01739, DB00128/DB02655); the guard
  returns the PRE-tautomer InChIKey (pinned literals, rdkit 2026.3.5); Nitisinone
  keto/enol (DB00348/DB08307, no /b layer) must STILL merge — passes today, regression guard.
- `tests/test_merge_report.py`: `merge_stage_report` — one row per merge group with the
  stage it merges at (`upstream-duplicate | parse | salt | uncharge | tautomer`).

Before-state on the real snapshot (reproduced independently, matches CTO #97):
191 groups = 100 upstream-duplicate / 2 parse / 19 salt / 22 uncharge / 48 tautomer;
46 of the 48 tautomer-stage groups had stereo layers before the tautomer step.

Resume: `git apply workstreams/lung-on-chipsim/parked/2026-09-15-stereo-guard-red-tests.patch`
from the repo root, re-run the RED, then implement per the principal's layer ruling.
