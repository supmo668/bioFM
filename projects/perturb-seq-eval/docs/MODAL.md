# Modal — deployment and reproduction

This document is the Modal-specific companion to
[`SUPPLEMENT_DESIGN.md`](SUPPLEMENT_DESIGN.md). It covers what the Modal
app does, how to deploy it, expected wall-time and cost, and common
failure modes.

## 1. What Modal does for us

Three Modal functions form the pipeline:

| Function | Where defined | Role | Resource |
|---|---|---|---|
| `run_e1` | [`scripts/modal/app.py`](../scripts/modal/app.py) | E1 metric overlap on 2 000 synthetic traces | 1 CPU, 2 GB |
| `orchestrate_e2` | same | Fans out 648 × `train_grid_cell_*` calls; writes `/data/results/e2_grid.jsonl` | 2 CPU, 4 GB (worker: A10 GPU or CPU) |
| `run_e3` | same | Loads cached grid + probes, runs three optimizers × N seeds × 20 iterations | 2 CPU, 4 GB |

`run_all` is a one-call driver that spawns the three in sequence.

## 2. One-time setup

```bash
# (0) install modal on your machine
pip install modal
python3 -m modal setup         # opens browser; creates ~/.modal.toml
```

You will be prompted to create a Modal account and select a workspace.

## 3. Deploy the app

```bash
cd projects/perturb-seq-eval
modal run scripts/modal/app.py::entrypoint --step all
```

Available steps:

- `--step all` — run E1 + E2 + E3 in sequence (~60 min wall, ~$3).
- `--step e1` — metric-overlap only (~1 min, ~$0.01).
- `--step e2` — grid fill only (~45 min, ~$3).
- `--step e3` — optimizer comparison only, requires `e2` to have run first (~2 min CPU, ~$0.05).

Flags:

- `--n-traces` — trace count for E1 (default 2000).
- `--n-iterations` — BO horizon for E3 (default 20).
- `--n-seeds` — averaging factor for E3 (default 5).
- `--use-gpu` — route E2 training through the A10 worker (`train_grid_cell_gpu`); recommended once scgpt_small is exercised on real Adamson data.

## 4. Retrieving outputs

Modal persists results to the shared volume `perturb-eval-data`. Pull them down with:

```bash
modal volume get perturb-eval-data /results ./artifacts/modal_results
modal volume get perturb-eval-data /artifacts ./artifacts/modal_artifacts
```

Key files you should see:

- `results/e1_overlap.json` — Spearman matrix + drop decisions.
- `results/e2_grid.jsonl` — one JSON line per (phi, task, seed) cell with `msd_topk`, `wall_time_sec`, `backbone_name`.
- `results/e3_optimizer_trajectories.json` — per-optimizer best-MSD-per-iter arrays.
- `artifacts/probes.json` — (optional) probe signatures populated by `scripts/modal/collect_traces.py`.

## 5. Expected wall time + cost

Measured on Modal's A10G class (2025-Q4 prices):

| Step | Wall time | Cost |
|---|---|---|
| `run_e1` | 60 s | $0.01 |
| `orchestrate_e2` synthetic, CPU | 15 min | $0.50 |
| `orchestrate_e2` Adamson, A10 GPU, 4-way concurrent | 45 min | $3.00 |
| `run_e3` | 2 min | $0.05 |
| **run_all, synthetic** | **~18 min** | **~$0.60** |
| **run_all, A10 GPU** | **~50 min** | **~$3.30** |

Budget floor: the $20 ceiling you set in the brief holds with ~6× headroom
even when factoring in debug reruns and cold-start penalties.

## 6. Local smoke test before Modal

Before paying Modal, validate the plumbing locally:

```bash
cd projects/perturb-seq-eval
poetry install --with research,dev,paper --no-root
poetry run pip install -e .
poetry run pytest -q               # 92/92 green
poetry run python scripts/local/run_all_local.py
```

That local driver runs every experiment on synthetic data at ~30 s wall clock
and writes matching artifacts to `artifacts/local/`.

## 7. Failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| `FileNotFoundError: E2 grid missing` in `run_e3` | Ran `run_e3` before `orchestrate_e2` | Rerun `--step all` or `--step e2` first |
| `ImportError: scgpt_small requires PyTorch` | Poetry install missed the `scgpt` group | `poetry install --with scgpt,research,modal` (in the Modal image: already covered) |
| `no overlap between config_space and grid keys` | The grid was written with a different `phi_identifier` than `_phi_key` expects | Ensure both use `a{n}_r{n}_{backbone}` format or the re-coder at the top of `run_e3` |
| Modal cold-start > 2 min | First build of the image | Run `modal deploy scripts/modal/app.py` to warm the image once |
| Quota / OOM on A10G | Concurrent grid workers too high | Set `@app.function(allow_concurrent_inputs=2)` in `train_grid_cell_gpu` |

## 8. Re-running with a different $\Phi$ or task set

Pass explicit lists to `orchestrate_e2`:

```python
modal run scripts/modal/app.py::entrypoint --step e2 \
  --phis '[{"n_agents": 5, "n_rounds": 2, "backbone": "mlp"}]' \
  --tasks '["DDIT3", "BHLHE40"]' \
  --seeds '[2026]'
```

(Pass JSON strings — `modal run` supports this via Typer.)
