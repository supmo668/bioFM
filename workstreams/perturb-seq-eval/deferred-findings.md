# Deferred findings — perturb-seq-eval

Registered defects outside the #202 sweep path. Each is a live defect with a working analogue already fixed
on the sweep path; none is touched by the v0.6.0 regeneration. Registered per CTO #245 ("dispatch prose is
where findings go to die"). Disposition changes require a CTO ruling.

| id | severity | where | defect | fixed analogue on the sweep path | status |
|---|---|---|---|---|---|
| DF-01 | high | `scripts/modal/app_lifecycle.py:144` | broad `except Exception` turns `BackboneUnavailableError` (C-TORCH-2) into an error record — a torch import failure silently becomes a missing lifecycle run | `app_v05.py` lifecycle loop re-raises it (T22) | open |
| DF-02 | high | `scripts/modal/app_lifecycle_optimizer.py:143` | broad `except Exception` **substitutes `msd = 1.0`** for any failure incl. `BackboneUnavailableError` and programming errors — a fabricated score enters the optimizer | `heldout.py` trainer loop + #245 error taxonomy | open |
| DF-03 | high | `scripts/fetch_adamson.py` | downloads via `urllib.request.urlretrieve`, bypassing `data.download` SHA-256 pins; makes A7's fail-closed guarantee conditional on the entry point used. **Confirmed not used by the sweep** (`app_v05.py` fetches via `data.download.fetch_*` with `trust_unpinned=False`); referenced only in docstrings (`adamson_loader.py:8`, `data/protocol.py:90`) — which point readers at it | `data.download._fetch` fail-closed (T19/T21) | open |
| DF-04 | medium | `scripts/paper/fill_v050_numbers.py` | must refuse any `summary.json` whose `status != "ok"` (analyser escape hatches produce `*_DIAGNOSTIC_ONLY` summaries with null gates) | analyser status marking (P3, #245) | open |
| DF-06 | high (mechanism) / none (v0.5.0 exposure) | `e2_adamson.py` random-gene fallback + `norman.py` '+' guard (both removed in T8) | **Nine real labels would have been given a RANDOM target gene if sampled, and none was drawn.** Adamson: `PERK`, `IRE1`, `3x`, `Gal4-4(mod)`; Norman: `C3orf72`, `C3orf72_FOXL2`, `KIAA1804`, `C19orf26`, `TGFBR2_C19orf26`. Checked against all three v0.5.0 artifacts: zero hits. The v0.5.0 numbers are not wrong because of these — nor right because of them; they are **unexposed**, by sampling luck, not design. Sixth silent-substitution instance. T22 preflight would have refused the sweep before GPU time. | fail-closed `resolve_target_indices` (T7/T8) + label contract (#250/#251) | mechanism closed; mapping in progress |
| DF-05 | low | `scripts/live_smoke.py:30,32`, `scripts/modal/collect_traces.py:26-27` | pre-existing F401 unused imports | — | open |

Recommended remedy shape (not authorised): DF-01/02 adopt `experiments/errors.classify` (#245 taxonomy);
DF-03 becomes a thin wrapper over `data.download.fetch_adamson(..., trust_unpinned=False)` or is deleted, and the
two docstrings are repointed.
