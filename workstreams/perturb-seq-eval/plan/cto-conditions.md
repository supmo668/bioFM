# CTO conditions attached to signed plan r3 (hash 418cc1e)

Binding build conditions from CTO dispatch #233 (2026-09-24). Kept here, outside `build-plan.md`, so the
principal-signed plan hash is not drifted; each condition tightens a task, none widens scope.

| id | applies to | condition |
|---|---|---|
| C-KEY-1 | T22 preflight | Lifecycle phase FAILS CLOSED when `OPENROUTER_API_KEY` is absent **or** a pool probe returns no usable model. Assertion, not warning, not fallback. Presence check only — the value is never read or printed. |
| C-KEY-2 | T12 / T24 | Any `source=="fallback"` step during the real sweep marks the run FAILED (analyser refuses to summarise; provenance `status: "failed_fallback"`). `source` is diagnostic, never a licence. |
| C-KEY-3 | T24 | Lifecycle sweep BLOCKED until the principal provisions the key. Not provisioned as of #233 (Infisical bioFM/dev: 404). |
| C-RG-1 | T8b | Red-then-green: run the HVG property test against pre-fix code, capture it RED, then fix and capture GREEN. Both transcripts go into the iteration QGR. |
| C-RG-2 | T8 / T11 (D1) | Same red-then-green standard for the Norman doublet assertion. |
| D1-confirm | T2/T11/T24 | "Norman keeps 15+5" = the documented design restored: 15 singletons + 5 doublets = 20 Norman tasks; with 21 Adamson = 41 tasks. |

RESOLVED by CTO #235 — RULED (A): hold the whole sweep until the key exists; run once; do NOT build (B)'s guard.
If the key has not landed when P0-P4 are done, report at the sweep gate (do not idle) — (B) only as a recorded, expiring exception.

History (raised in reply to #233): #233 permits the trainer sweep to run before the key exists. That
would make trainer and lifecycle two processes — the A1 shape #202 forbids. Proposed: one process once the key
lands; if a split is ruled acceptable, the lifecycle run must load the trainer provenance record and hard-fail
unless its resolved task list, dataset digests and git SHA are identical.

## C-TORCH-1 (from the #239 alias-test question) — applies to T22 preflight + T0 baseline
`test_alias_scgpt_to_scgpt_small` is RED because `_canonical_backbone` (`agentic_lifecycle/architect_dispatch.py:25-28`)
returns `"linear"` whenever the resolved name is not in `available_backbones()`, and `available_backbones()` omits
`scgpt_small` when torch is not importable (`backbones/__init__.py:28`). The local venv has no torch, so the alias
resolves `scgpt → scgpt_small → (unavailable) → linear`. The Modal image pins `torch>=2.2` (`app_v05.py:57`), so the
sweep is not affected TODAY — but the mechanism is a silent substitution in the A4 family: if torch ever fails to
import on Modal, every Architect `scgpt_small` pick becomes `linear` with no error, and the backbone-entropy figure
measures the import, not the agent.
- **T22:** preflight asserts every backbone in the resolved `backbones` kwarg is in `available_backbones()`; fails closed.
- **Test:** the alias test gets `pytest.importorskip("torch")` (a local-environment skip, never a pass), plus a new
  torch-independent test that a KNOWN-but-unavailable backbone raises instead of degrading (ruling requested — see reply).

## C-TORCH-2 (CTO #241, RULED) — tightens T22 + adds a small task at the P2 boundary
- `_canonical_backbone`: **known-but-unavailable → raise**; unknown name → `linear` unchanged (documented fallback).
- (a) Verify no caller swallows it: trace every path from `_canonical_backbone` up through the Architect and the
  sweep; any broad `except` around config resolution must re-raise. Name the paths in the report.
- (b) T22 preflight asserts every resolved sweep backbone is in `available_backbones()`, so the raise is dead code
  in a healthy run. If it can fire during a normal sweep, the preflight is incomplete.
- Alias test uses `pytest.importorskip("torch")`; every gate report states skips **counted and named**
  (e.g. "N passed, 1 skipped (torch absent: test_alias_scgpt_to_scgpt_small)"), never folded into green.
- Report back: which local tests pass for the wrong reason without torch (compare suite with vs without torch).

## C-TORCH-3 (CTO #243, RATIFIED + 2 additions) — P2-boundary mini-task + T13/T22
- **Exact pin, not a floor:** `torch==2.14.0` in pyproject's `scgpt` group AND the Modal image (`app_v05.py`), matching the
  local CPU venv. If the Modal image cannot take the exact pin (CUDA wheel availability), keep the floor, say why in the
  report, and the resolved-version record below becomes mandatory.
- **Provenance (T13):** `lib_versions` records the RESOLVED versions imported at run time (`torch.__version__`,
  `torch.version.cuda`, numpy, anndata, h5py, scanpy, pandas, pydantic) — never the constraint string.
- **Skip guards must be seen firing:** `pytest.importorskip("torch")` on `test_alias_scgpt_to_scgpt_small` and
  `test_architect_choice_entropy_above_gate`; run the suite ONCE in a torch-less venv and capture both reported as
  SKIPPED by name → `workstreams/perturb-seq-eval/qgr/evidence/C-TORCH-3-skip-guards-fire.txt`.
- Standing heuristic (CTO): any "if unavailable, use X" is guilty until proven loud — reviewers grep for it at every gate.
