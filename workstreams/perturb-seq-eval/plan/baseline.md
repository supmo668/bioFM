# T0 baseline: perturb-seq-eval test suite

- **Date:** 2026-09-24
- **Python:** 3.12.13 (uv venv at `projects/perturb-seq-eval/.venv`, project installed editable)
- **Runner:** `cd projects/perturb-seq-eval && .venv/bin/python -m pytest -q -p no:cacheprovider`

## Before the fixes

**209 passed, 3 failed** (pytest exit code 1)

| Test | Cause |
|---|---|
| `tests/test_architect_dispatch_v05.py::TestResolveArchitectConfig::test_alias_scgpt_to_scgpt_small` | Already failing before this work (commit 84fb70f). Left alone. |
| `tests/test_adamson_combined.py::TestLoadAdamsonCombined::test_concatenates_two_subsets` | `TypeError: Accessing a group is done with bytes or str, not <class 'tuple'>` at `e2_adamson.py:156` (`f["var/gene_symbol"][()]`) |
| `tests/test_adamson_combined.py::TestLoadAdamsonCombined::test_single_subset_still_works` | Same as above |

Versions installed at that point: anndata 0.13.4, h5py 3.16.0, **pandas 3.0.6**.

### Root cause
The problem is not in h5py. pandas 3 makes `str` the default dtype for string columns. anndata 0.13.x then writes
string `var`/`obs` columns as an HDF5 **group** (`encoding-type: nullable-string-array`) instead of a plain
string dataset. The raw-h5py reader in `load_adamson_matrix` expects a dataset and runs `[()]` on it. On a
group, that fails with the TypeError above. anndata ≤0.12.x declares `pandas<3`, so installing it pulls pandas
back to 2.3.3 and restores the plain-dataset layout.

## Bisection (`tests/test_adamson_combined.py`, 5 tests)

| anndata | h5py | pandas (resolved) | Result |
|---|---|---|---|
| 0.13.4 | 3.16.0 | 3.0.6 | 2 failed |
| 0.13.4 | 3.15.1 | 3.0.6 | 2 failed |
| 0.13.4 | 3.14.0 | 3.0.6 | 2 failed |
| 0.13.4 | 3.12.1 | 3.0.6 | 2 failed (downgrading h5py has no effect) |
| 0.13.0 | 3.16.0 | 3.0.6 | 2 failed |
| **0.12.19** (newest 0.12.x) | **3.16.0** | 2.3.3 | **5 passed** |
| 0.12.10 / 0.12.6 / 0.12.0 | 3.16.0 | 2.3.3 | 5 passed |
| 0.11.4 | 3.16.0 | 2.3.3 | collection error |
| 0.13.4 | 3.16.0 | 2.3.3 (forced) | 5 passed (confirms pandas 3 is the trigger) |

## Pins chosen
- `anndata==0.12.19`: the newest anndata that passes without a separate pandas pin. Its own metadata requires
  `pandas>=2.1.0,<3,!=2.1.2`, so the pandas cap comes with it.
- `h5py==3.16.0`: the latest release. It was never the cause.
- Where the pins live: `pyproject.toml` `[tool.poetry.group.scgpt.dependencies]`, and the Modal `image` `pip_install` in
  `scripts/modal/app_v05.py`. That file's pydantic/requests entries were already present and were not changed.
- Added to `[project] dependencies`: `pydantic (>=2,<3)` and `requests (>=2.31,<3)`. Both are imported by `src/`
  but were not declared.
- Note: anndata 0.12.19 requires Python ≥3.11. The Modal image (3.11) and the local venv (3.12) meet this. The project's
  `requires-python = ">=3.10"` still allows 3.10 in theory.

## After the fixes

**211 passed, 1 failed** (pytest exit code 1). The only failure is the existing
`test_architect_dispatch_v05.py::TestResolveArchitectConfig::test_alias_scgpt_to_scgpt_small`.

## Installed key package versions (after the fixes)

| Package | Version |
|---|---|
| numpy | 2.5.3 |
| torch | not installed |
| anndata | 0.12.19 |
| h5py | 3.16.0 |
| pandas | 2.3.3 |
| scanpy | 1.12.4 (imports OK) |
| scipy | 1.18.1 |
| scikit-learn | 1.9.1 |
| pydantic | 2.13.5 |
| requests | 2.34.2 |
| cma | 4.5.0 |
| pytest | 9.1.1 |
