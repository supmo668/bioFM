"""T13/T14/T17: provenance record, finalize, run-config copy, JSONL record 0.

``scripts/modal/app_v05.py`` imports ``modal`` at module top, so it is never
imported here; its kwarg names are read with ``ast``.
"""

from __future__ import annotations

import ast
import importlib.metadata as md
import json
import re
import subprocess
from pathlib import Path

import pytest

from perturb_eval.experiments import provenance as pv
from perturb_eval.experiments.v05_tasks import TaskPlan

APP_V05 = Path(__file__).resolve().parents[1] / "scripts" / "modal" / "app_v05.py"

AND_S3_KWARGS = {
    "norman_n_singletons",
    "norman_n_doublets",
    "adamson_n_per_bin",
    "adamson_n_bins",
    # Amendment 2 A2-4: N is not a trainer-sweep axis, so there is no n_sweep.
    "seeds",
    "n_top_hvg",
    "max_cells_per_pert",
    "r_sweep",
    "backbones",
    "doublet_delim",
    "cooldown_sec",
    "temperature",
    # CTO #283 / OWN-1: the $12 stop-and-report spend is a recorded sweep kwarg.
    "spend_stop_usd",
    "prior_spend_usd",
}


def _sweep_kwarg_names() -> list[str]:
    tree = ast.parse(APP_V05.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "run_v05_sweep":
            a = node.args
            return [x.arg for x in a.posonlyargs + a.args + a.kwonlyargs]
    raise AssertionError("run_v05_sweep not found in app_v05.py")


def _init_repo(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    g = [
        "git",
        "-c",
        "user.name=t",
        "-c",
        "user.email=t@example.invalid",
        "-c",
        "commit.gpgsign=false",
        "-C",
        str(path),
    ]
    subprocess.run([*g, "init", "-q"], check=True)
    (path / "a.txt").write_text("x\n")
    subprocess.run([*g, "add", "a.txt"], check=True)
    subprocess.run([*g, "commit", "-q", "-m", "init"], check=True)
    return path


def _kwargs() -> dict:
    names = _sweep_kwarg_names()
    return {n: f"v_{n}" for n in names}


def _prov(**over) -> dict:
    plan = TaskPlan(
        adamson=("A",),
        norman_singletons=("B",),
        norman_doublets=("B_C",),
        strata={"adamson:A": 0},
        eligible_counts={"adamson": 1},
    )
    kw = dict(
        run_id="20260924T000000Z-abcdef1",
        git_sha="a" * 40,
        git_dirty=False,
        entrypoint_kwargs=_kwargs(),
        datasets=[
            {"name": "norman", "path": "/data/n.h5ad", "sha256": None, "n_cells": 10, "n_genes": 5}
        ],
        task_plan=plan,
        tasks_excluded=[{"label": "X", "reason": "not in target_gene_idx"}],
        llm_pool=["m/one:free", "m/two:free"],
        gpu="A100-40GB",
        hourly_usd=1.32,
        budget_cap_usd=28.0,
        trainer_grid=_GRID,
    )
    kw.update(over)
    return pv.build_provenance(**kw)


# A2-4: the trainer grid as run (heldout.trainer_grid output shape).
_GRID = {
    "backbones": ["linear", "mlp"],
    "r_sweep": [1, 2],
    "seeds": [2026],
    "n_records_per_task": 4,
    "n_distinct_configs_per_task": 3,
    "distinct_configs_by_backbone": {"linear": 1, "mlp": 2},
    "n_distinct_fits_per_task": 3,
    "distinct_fits_by_backbone": {"linear": 1, "mlp": 2},
    "r_seed_invariant_backbones": ["linear"],
}


def test_a2_4_no_n_sweep_kwarg_required_or_in_app() -> None:
    assert "n_sweep" not in pv.REQUIRED_ENTRYPOINT_KWARGS
    assert "n_sweep" not in _sweep_kwarg_names()
    src = APP_V05.read_text()
    assert "n_sweep" not in src and "_DEFAULT_N_SWEEP" not in src


def test_a2_4_trainer_grid_is_required_and_recorded() -> None:
    from perturb_eval.experiments.heldout import trainer_grid

    grid = trainer_grid(
        backbones=("linear", "mlp", "scgpt_small"), r_sweep=(1, 2, 3), seeds=[2026, 2027, 2028]
    )
    prov = _prov(trainer_grid=grid)
    assert prov["trainer_grid"] == grid
    assert "trainer_grid" in pv.REQUIRED_KEYS
    kw = dict(
        run_id="r",
        git_sha="a" * 40,
        git_dirty=False,
        entrypoint_kwargs=_kwargs(),
        datasets=[],
        task_plan={},
        tasks_excluded=[],
        llm_pool=[],
        gpu="g",
        hourly_usd=1.0,
        budget_cap_usd=1.0,
    )
    with pytest.raises(TypeError):
        pv.build_provenance(**kw)  # no trainer_grid: refused
    for bad in (
        None,
        {},
        {**grid, "n_distinct_configs_per_task": "3"},
        {k: v for k, v in grid.items() if k != "seeds"},
    ):
        with pytest.raises(ValueError, match="trainer_grid"):
            _prov(trainer_grid=bad)


def test_a2_4_app_v05_records_the_trainer_grid() -> None:
    src = APP_V05.read_text()
    assert "trainer_grid(" in src
    call = next(
        c
        for c in ast.walk(ast.parse(src))
        if isinstance(c, ast.Call) and getattr(c.func, "id", None) == "build_provenance"
    )
    assert "trainer_grid" in {k.arg for k in call.keywords}


def _finalize_kwargs() -> dict:
    return dict(
        finished_at="2026-09-24T01:00:00+00:00",
        gpu_seconds=12.5,
        gpu_seconds_source="wall_clock_of_gpu_function",
        cost_usd_actual=0.01,
        counts={"n_trainer_runs": 1, "n_lifecycle_runs": 1},
        entropies={"architect_backbone_entropy_nats": 0.0},
        hvg_n_per_task={"norman:B": {"trainer": [2000]}},
        params_per_task={"norman:B": {"trainer": {"linear": [10]}}},
        budget_hit=False,
        status="ok",
        unparseable_lines={"trainer_runs.jsonl": [], "lifecycle_runs.jsonl": []},
    )


# ---------- build ----------


def test_every_required_key_present():
    prov = _prov()
    for k in pv.REQUIRED_KEYS:
        assert k in prov, k
    assert prov["record_type"] == "provenance"
    assert prov["hvg_selection"]["mode"] == "train_only"
    assert prov["tasks"] == _prov()["tasks"]
    assert prov["tasks"]["norman_doublets"] == ["B_C"]
    assert any("deg_eval_genes_from_heldout_shift" in s for s in prov["known_limitations"])
    # started_at is UTC ISO
    assert prov["started_at"].endswith("+00:00")


def test_build_rejects_bad_git_sha():
    with pytest.raises(ValueError):
        _prov(git_sha="abc123")


def test_build_rejects_missing_and_kwarg():
    kw = _kwargs()
    kw.pop("temperature", None)
    with pytest.raises(ValueError, match="temperature"):
        _prov(entrypoint_kwargs=kw)


def test_git_state_from_temp_repo(tmp_path):
    repo = _init_repo(tmp_path / "r")
    sha, dirty = pv.git_state(repo)
    assert re.fullmatch(r"[0-9a-f]{40}", sha)
    head = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()
    assert sha == head
    assert dirty is False
    (repo / "a.txt").write_text("changed\n")
    assert pv.git_state(repo) == (sha, True)
    prov = _prov(git_sha=sha, git_dirty=True)
    assert re.fullmatch(r"[0-9a-f]{40}", prov["git_sha"])


def test_git_state_outside_repo_fails_loud(tmp_path):
    with pytest.raises(RuntimeError):
        pv.git_state(tmp_path)


def test_lib_versions_resolved_not_constraints():
    versions = pv.resolve_lib_versions()
    for name in (
        "torch",
        "torch_cuda",
        "numpy",
        "pandas",
        "anndata",
        "h5py",
        "scanpy",
        "scipy",
        "pydantic",
        "requests",
        "modal",
    ):
        assert name in versions, name
    assert versions["numpy"] == md.version("numpy")
    for v in versions.values():
        assert v is None or isinstance(v, str)
        if isinstance(v, str):
            assert ">=" not in v and "==" not in v and "<" not in v and "~" not in v
    prov = _prov()
    assert prov["lib_versions"]["numpy"] == md.version("numpy")


def test_build_rejects_constraint_string_in_lib_versions():
    with pytest.raises(ValueError):
        _prov(lib_versions={"numpy": ">=1.26"})


# Principal directive + CTO #265: resolved (host-computed) sweep inputs.
PROVENANCE_INPUT_KWARGS = {"llm_key_source", "preregistration", "preregistration_error"}


def test_entrypoint_kwargs_contains_every_sweep_kwarg():
    names = _sweep_kwarg_names()
    assert AND_S3_KWARGS <= set(names), AND_S3_KWARGS - set(names)
    assert PROVENANCE_INPUT_KWARGS <= set(names), PROVENANCE_INPUT_KWARGS - set(names)
    prov = _prov()
    assert set(names) <= set(prov["entrypoint_kwargs"])
    assert AND_S3_KWARGS <= set(prov["entrypoint_kwargs"])


def test_sweep_kwargs_match_required_and_names():
    assert AND_S3_KWARGS <= set(pv.REQUIRED_ENTRYPOINT_KWARGS)


# ---------- finalize ----------


def test_finalize_adds_final_keys():
    fin = pv.finalize_provenance(_prov(), **_finalize_kwargs())
    for k in pv.REQUIRED_FINAL_KEYS:
        assert k in fin, k
    assert fin["hvg_selection"]["n_per_task"] == {"norman:B": {"trainer": [2000]}}
    assert fin["status"] == "ok"


def test_finalize_refuses_missing_started_at():
    prov = _prov()
    del prov["started_at"]
    with pytest.raises(ValueError, match="started_at"):
        pv.finalize_provenance(prov, **_finalize_kwargs())


def test_finalize_rejects_unknown_status():
    kw = _finalize_kwargs() | {"status": "great"}
    with pytest.raises(ValueError):
        pv.finalize_provenance(_prov(), **kw)


def test_finalize_does_not_mutate_input():
    prov = _prov()
    before = json.dumps(prov, sort_keys=True)
    pv.finalize_provenance(prov, **_finalize_kwargs())
    assert json.dumps(prov, sort_keys=True) == before


# ---------- per-task HVG / params collection ----------


def test_collect_hvg_and_params():
    trainer = [
        {
            "dataset": "norman",
            "task": "B",
            "backbone": "linear",
            "hvg_n": 2000,
            "hvg_n_forced": 1,
            "hvg_mode": "train_only",
            "n_params": 10,
        },
        {
            "dataset": "norman",
            "task": "B",
            "backbone": "mlp",
            "hvg_n": 2000,
            "hvg_n_forced": 1,
            "hvg_mode": "train_only",
            "n_params": 99,
        },
        {
            "dataset": "norman",
            "task": "B",
            "backbone": "mlp",
            "error": "boom",
            "msd_topk": float("inf"),
        },
    ]
    lifecycle = [
        {
            "dataset": "norman",
            "task_id": "B",
            "backbone_used": "mlp",
            "hvg_n_per_round": [1000, 1500],
            "hvg_n_forced_per_round": [1, 1],
            "hvg_mode": "train_only",
            "n_params": 42,
        },
    ]
    hvg, params = pv.collect_hvg_and_params(trainer, lifecycle)
    assert hvg["norman:B"]["trainer"]["hvg_n"] == [2000]
    assert hvg["norman:B"]["trainer"]["hvg_mode"] == ["train_only"]
    assert hvg["norman:B"]["lifecycle"]["hvg_n"] == [1000, 1500]
    assert params["norman:B"]["trainer"] == {"linear": [10], "mlp": [99]}
    assert params["norman:B"]["lifecycle"] == {"mlp": [42]}


# ---------- run config (T17) ----------


def test_write_run_config_contents_and_no_overwrite(tmp_path):
    kw = {"seeds": 3, "backbones": ["linear"], "temperature": 0.3}
    p1 = pv.write_run_config(tmp_path, "20260924T000000Z-abcdef1", kw, "a" * 40)
    assert p1 == tmp_path / "configs" / "runs" / "20260924T000000Z-abcdef1.json"
    body = json.loads(p1.read_text())
    assert body["entrypoint_kwargs"] == kw
    assert body["git_sha"] == "a" * 40
    assert body["run_id"] == "20260924T000000Z-abcdef1"
    original = p1.read_text()
    p2 = pv.write_run_config(tmp_path, "20260924T000000Z-abcdef1", kw, "a" * 40)
    assert p2 != p1 and p2.exists()
    assert p1.read_text() == original
    assert json.loads(p2.read_text())["entrypoint_kwargs"] == kw


def test_write_run_config_matches_provenance_block(tmp_path):
    prov = _prov()
    p = pv.write_run_config(tmp_path, prov["run_id"], prov["entrypoint_kwargs"], prov["git_sha"])
    assert json.loads(p.read_text())["entrypoint_kwargs"] == prov["entrypoint_kwargs"]


def test_make_run_id_format():
    rid = pv.make_run_id("0123456789abcdef0123456789abcdef01234567")
    assert re.fullmatch(r"\d{8}T\d{6}Z-0123456", rid)


# ---------- JSONL record 0 (T14 writer half) ----------


def test_jsonl_line_round_trips():
    prov = _prov()
    line = pv.jsonl_provenance_line(prov)
    assert "\n" not in line
    assert json.loads(line) == json.loads(json.dumps(prov))
    assert json.loads(line)["record_type"] == "provenance"


def test_entrypoint_passes_every_sweep_kwarg():
    """The host entrypoint's ``sweep_kwargs`` dict (config copy + .remote call)
    names exactly the kwargs of ``run_v05_sweep``."""
    tree = ast.parse(APP_V05.read_text())
    fn = next(
        n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "entrypoint"
    )
    keys = None
    for node in ast.walk(fn):
        if (
            isinstance(node, ast.Assign)
            and isinstance(node.value, ast.Dict)
            and any(isinstance(t, ast.Name) and t.id == "sweep_kwargs" for t in node.targets)
        ):
            keys = {k.value for k in node.value.keys if isinstance(k, ast.Constant)}
    assert keys is not None, "sweep_kwargs dict not found in entrypoint"
    assert keys == set(_sweep_kwarg_names())
    assert PROVENANCE_INPUT_KWARGS <= keys


# ---------- CTO #245 Q2: unparseable_lines ----------


def test_read_jsonl_locating_records_locations(tmp_path):
    p = tmp_path / "x.jsonl"
    good = json.dumps({"a": 1}) + "\n"
    bad = "{broken" + "x" * 200 + "\n"
    p.write_text(good + "\n" + bad + good)
    rows, bad_lines = pv.read_jsonl_locating(p)
    assert rows == [{"a": 1}, {"a": 1}]
    assert bad_lines == [
        {"line": 3, "byte_offset": len(good) + 1, "preview": ("{broken" + "x" * 200)[:80]}
    ]


def test_read_jsonl_locating_missing_file(tmp_path):
    assert pv.read_jsonl_locating(tmp_path / "nope.jsonl") == ([], [])


def test_clean_run_writes_explicit_empty_unparseable_lines(tmp_path):
    for name in ("trainer_runs.jsonl", "lifecycle_runs.jsonl"):
        (tmp_path / name).write_text(json.dumps({"record_type": "provenance"}) + "\n")
    scanned = pv.scan_unparseable(
        tmp_path / "trainer_runs.jsonl", tmp_path / "lifecycle_runs.jsonl"
    )
    kw = _finalize_kwargs() | {"unparseable_lines": scanned}
    fin = pv.finalize_provenance(_prov(), **kw)
    assert "unparseable_lines" in fin
    assert fin["unparseable_lines"] == {"trainer_runs.jsonl": [], "lifecycle_runs.jsonl": []}
    assert "unparseable_lines" in pv.REQUIRED_FINAL_KEYS
    assert json.loads(json.dumps(fin))["unparseable_lines"]["trainer_runs.jsonl"] == []


@pytest.mark.parametrize(
    "bad",
    [
        None,
        {},
        {"trainer_runs.jsonl": []},
        {"trainer_runs.jsonl": [], "lifecycle_runs.jsonl": None},
    ],
)
def test_finalize_requires_both_unparseable_keys(bad):
    kw = _finalize_kwargs() | {"unparseable_lines": bad}
    with pytest.raises(ValueError, match="unparseable_lines"):
        pv.finalize_provenance(_prov(), **kw)


def test_finalize_has_no_unparseable_default():
    kw = _finalize_kwargs()
    del kw["unparseable_lines"]
    with pytest.raises(TypeError):
        pv.finalize_provenance(_prov(), **kw)


# ---- principal directive / CTO #265: credential source + pre-registration ----


def test_llm_key_source_recorded_and_marked_cross_project() -> None:
    src = pv.llm_key_source("infisical", "syntropyhealth-app", "dev", home_project="biofm")
    prov = _prov(llm_key_source=src)
    assert prov["llm_key_source"] == {
        "store": "infisical",
        "project_slug": "syntropyhealth-app",
        "env": "dev",
        "home_project": "biofm",
        "cross_project": True,
    }


def test_llm_key_source_rejects_anything_that_looks_like_a_secret() -> None:
    for bad in ("sk-or-v1-" + "a" * 40, "x" * 201, ""):
        with pytest.raises(ValueError):
            pv.llm_key_source("infisical", bad, "dev", home_project="biofm")


def test_preregistration_record_from_committed_clean_file(tmp_path) -> None:
    import subprocess

    def git(*a):
        subprocess.run(["git", *a], cwd=tmp_path, check=True, capture_output=True)

    git("init", "-q")
    git("config", "user.email", "t@t")
    git("config", "user.name", "t")
    f = tmp_path / "PREREGISTRATION.md"
    f.write_text("H1: ...\n")
    git("add", ".")
    git("commit", "-qm", "prereg")
    rec = pv.preregistration_record(tmp_path, "PREREGISTRATION.md")
    assert set(rec) == {"path", "sha256", "commit"} and len(rec["commit"]) == 40
    f.write_text("H1: edited after the fact\n")  # uncommitted edit => not a pre-registration
    with pytest.raises(ValueError, match="uncommitted"):
        pv.preregistration_record(tmp_path, "PREREGISTRATION.md")
    with pytest.raises(ValueError, match="not tracked|does not exist"):
        pv.preregistration_record(tmp_path, "MISSING.md")


def test_provenance_carries_preregistration() -> None:
    rec = {"path": "paper/PREREGISTRATION.md", "sha256": "a" * 64, "commit": "b" * 40}
    assert _prov(preregistration=rec)["preregistration"] == rec


def test_parse_key_source_valid_spec() -> None:
    got = pv.parse_key_source("infisical:syntropyhealth-app:dev", home_project="biofm")
    assert got == {
        "store": "infisical",
        "project_slug": "syntropyhealth-app",
        "env": "dev",
        "home_project": "biofm",
        "cross_project": True,
    }
    assert (
        pv.parse_key_source("infisical:biofm:prod", home_project="biofm")["cross_project"] is False
    )


@pytest.mark.parametrize(
    "spec",
    [
        None,
        "",
        "infisical",
        "infisical:app",
        "a:b:c:d",
        "infisical::dev",
        " : : ",
        "infisical:app:dev\n",
    ],
)
def test_parse_key_source_malformed_is_none(spec) -> None:
    assert pv.parse_key_source(spec, home_project="biofm") is None


@pytest.mark.parametrize(
    "spec",
    [
        "sk-or-v1-" + "a" * 40,
        "infisical:sk-or-v1-" + "a" * 40 + ":dev",
        "sk-proj:app:dev",
        "infisical:app:" + "x" * 201,
    ],
)
def test_parse_key_source_credential_shaped_is_none(spec) -> None:
    assert pv.parse_key_source(spec, home_project="biofm") is None
