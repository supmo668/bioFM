# QGR — perturb-seq-eval v0.6.0 conclusion (pr-prep, derived)

Scope: full branch diff vs origin/main, for landing. Derived from AV-1 (receipt hash_e 8795772, boundary 2fccf95), the last full gate (code/design/test/security reviewers + scorer). Every code path in the PR was reviewed by AV-1 or its ancestors (SA-1, REV-1, D8-1, PY-1).

## Delta since AV-1 (no code)
- Published state: publish.state.v060.json (`published: true` on both venues).
- Records: CITATION.cff (date-released 2026-10-16; Zenodo 10.5281/zenodo.23422745, Figshare .v6), CHANGELOG ([0.6.0] released; C3 declared).
- HACP: publish-review.md, publish-complete.md, decision.md (D-1/D-2 resolved), showcase publication record.
- Coordination dispatches.

## Checks (fresh, on the committed HEAD 1ae73e4)
- pytest: 1218 passed, 0 failed.
- fill_v060_numbers --check: generated_numbers.tex matches the artifacts.
- ruff: the rebuilt venv's ruff 0.17.0 reports pre-existing findings (I001, EXE001, RUF100, UP0xx) that origin/main's same files also fail under 0.17; none introduced by this branch's logic. CI does not run ruff. Not reformatted: v05_sweep.py is pinned by paper/data/land_v060.json.

## Findings
| ID | Conf | Finding | Disposition |
|---|---|---|---|
| C3 | — | Pre-registered version defined twice (v05_sweep.PREREGISTERED_VERSION, v05_preflight.PREREGISTERED_VERSIONS); both "v0.6.0" | Declared known gap in CHANGELOG (principal 2026-10-18); fixing requires a land-record amendment |
| L1 | — | ruff 0.17 pre-existing lint | Disclosed; out of scope |

Nothing sent to any venue during this gate.
