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

Open with the CTO (raised in reply to #233): #233 permits the trainer sweep to run before the key exists. That
would make trainer and lifecycle two processes — the A1 shape #202 forbids. Proposed: one process once the key
lands; if a split is ruled acceptable, the lifecycle run must load the trainer provenance record and hard-fail
unless its resolved task list, dataset digests and git SHA are identical.
