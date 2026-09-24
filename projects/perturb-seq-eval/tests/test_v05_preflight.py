"""T22: in-process preflight for the v0.6 sweep (C-KEY-1, C-TORCH-1/2, CTO #235).

Every failure is collected and raised once as ``PreflightError`` BEFORE any
trainer / lifecycle work. No network: the pool probe is always a stub here.
"""

from __future__ import annotations

import ast
import logging
import subprocess
from pathlib import Path

import numpy as np
import pytest

from perturb_eval.experiments.v05_preflight import (
    PreflightError,
    PreflightReport,
    preflight,
)
from perturb_eval.experiments.v05_tasks import TaskPlan

PROJECT_ROOT = Path(__file__).resolve().parent.parent
APP_V05 = PROJECT_ROOT / "scripts" / "modal" / "app_v05.py"
SENTINEL = "sk-or-SENTINEL-must-never-appear-0123456789"


def _ds(targets: dict[str, tuple[int, ...]], genes: tuple[str, ...]) -> dict:
    return {
        "X": np.zeros((2, len(genes))),
        "labels": np.array(["CTRL", "CTRL"]),
        "control_mask": np.array([True, True]),
        "target_gene_idx": targets,
        "perturbations": tuple(targets),
        "gene_names": genes,
    }


GENES = ("TFA", "TFB", "CBL", "UBASH3A", "G5")


def _datasets() -> dict:
    return {
        "adamson_full": _ds({"TFA": (0,), "TFB": (1,)}, GENES),
        "norman": _ds({"CBL": (2,), "CBL_UBASH3A": (2, 3)}, GENES),
    }


def _plan(adamson=("TFA", "TFB"), singles=("CBL",), doubles=("CBL_UBASH3A",)) -> TaskPlan:
    return TaskPlan(adamson=tuple(adamson), norman_singletons=tuple(singles),
                    norman_doublets=tuple(doubles))


def _kwargs(**over) -> dict:
    kw = {"backbones": ("linear", "mlp"), "version": "v0.6.0", "doublet_delim": "_"}
    kw.update(over)
    return kw


def _probe_ok(env) -> str:
    return "stub/model:free"


def _run(tmp_path: Path, **over):
    args = {
        "kwargs": _kwargs(),
        "datasets_spec_or_loaded": _datasets(),
        "task_plan": _plan(),
        "env": {"OPENROUTER_API_KEY": SENTINEL},
        "out_dir": tmp_path / "v0.6.0",
        "probe_fn": _probe_ok,
    }
    args.update(over)
    return preflight(**args)


def test_all_good_returns_ok_report(tmp_path: Path) -> None:
    rep = _run(tmp_path)
    assert isinstance(rep, PreflightReport)
    assert rep.ok
    assert rep.probe_model_id == "stub/model:free"
    assert rep.task_plan.all_tasks == ("TFA", "TFB", "CBL", "CBL_UBASH3A")
    assert set(rep.datasets) == {"adamson_full", "norman"}


def test_missing_key_fails_and_probe_not_called(tmp_path: Path) -> None:
    calls = []
    with pytest.raises(PreflightError, match="OPENROUTER_API_KEY"):
        _run(tmp_path, env={}, probe_fn=lambda env: calls.append(1) or "m")
    assert calls == []


def test_empty_key_counts_as_missing(tmp_path: Path) -> None:
    with pytest.raises(PreflightError, match="OPENROUTER_API_KEY"):
        _run(tmp_path, env={"OPENROUTER_API_KEY": ""})


def test_key_value_never_in_message_or_logs(tmp_path: Path, caplog) -> None:
    caplog.set_level(logging.DEBUG)

    def leaky_probe(env):  # a probe whose error text echoes the key
        raise RuntimeError(f"auth failed for {env['OPENROUTER_API_KEY']}")

    with pytest.raises(PreflightError) as ei:
        _run(tmp_path, probe_fn=leaky_probe, kwargs=_kwargs(backbones=("nope",)))
    assert SENTINEL not in str(ei.value)
    assert SENTINEL not in repr(ei.value.failures)
    assert SENTINEL not in caplog.text


def test_probe_no_model_fails(tmp_path: Path) -> None:
    with pytest.raises(PreflightError, match="no usable model"):
        _run(tmp_path, probe_fn=lambda env: None)


def test_unavailable_backbone_fails(tmp_path: Path, monkeypatch) -> None:
    from perturb_eval.experiments import v05_preflight as pf

    monkeypatch.setattr(pf, "available_backbones", lambda: ("linear", "mlp"))
    with pytest.raises(PreflightError, match="scgpt_small"):
        _run(tmp_path, kwargs=_kwargs(backbones=("linear", "scgpt_small")))


def test_unresolvable_target_fails_naming_task_and_no_trainer_call(tmp_path: Path) -> None:
    trainer_calls = 0

    def trainer_stub(report) -> None:
        nonlocal trainer_calls
        trainer_calls += 1

    with pytest.raises(PreflightError, match="BADTF"):
        report = _run(tmp_path, task_plan=_plan(adamson=("TFA", "BADTF")))
        trainer_stub(report)
    assert trainer_calls == 0


def test_task_in_vocab_but_missing_from_target_map_fails(tmp_path: Path) -> None:
    # G5 is a vocabulary gene but the loader never mapped it as a perturbation.
    with pytest.raises(PreflightError, match="G5"):
        _run(tmp_path, task_plan=_plan(singles=("CBL", "G5")))


def test_nonempty_output_dir_fails(tmp_path: Path) -> None:
    out = tmp_path / "v0.6.0"
    out.mkdir()
    (out / "trainer_runs.jsonl").write_text("{}\n")
    with pytest.raises(PreflightError, match="not empty"):
        _run(tmp_path, out_dir=out)


def test_empty_existing_output_dir_ok(tmp_path: Path) -> None:
    (tmp_path / "v0.6.0").mkdir()
    assert _run(tmp_path).ok


def test_loader_failure_is_reported_not_bypassed(tmp_path: Path) -> None:
    def unpinned_loader():
        raise ValueError("adamson_pilot has no pinned sha256 and trust_unpinned=False")

    ds = _datasets()
    ds["adamson_full"] = unpinned_loader
    with pytest.raises(PreflightError, match="trust_unpinned=False"):
        _run(tmp_path, datasets_spec_or_loaded=ds)


def test_callable_loader_and_plan_builder(tmp_path: Path) -> None:
    loaded = _datasets()
    ds = {k: (lambda v=v: v) for k, v in loaded.items()}
    rep = _run(tmp_path, datasets_spec_or_loaded=ds, task_plan=lambda dss: _plan())
    assert rep.ok and rep.datasets["norman"] is loaded["norman"]


def test_plan_builder_failure_reported(tmp_path: Path) -> None:
    def bad_plan(dss):
        raise ValueError("stratum count mismatch: adamson drew 20, expected 21")

    with pytest.raises(PreflightError, match="stratum count mismatch"):
        _run(tmp_path, task_plan=bad_plan)


def test_multiple_failures_all_listed(tmp_path: Path, monkeypatch) -> None:
    from perturb_eval.experiments import v05_preflight as pf

    monkeypatch.setattr(pf, "available_backbones", lambda: ("linear", "mlp"))
    out = tmp_path / "v0.6.0"
    out.mkdir()
    (out / "x").write_text("x")
    with pytest.raises(PreflightError) as ei:
        _run(
            tmp_path,
            env={},
            kwargs=_kwargs(backbones=("scgpt_small",)),
            task_plan=_plan(adamson=("BADTF",)),
            out_dir=out,
        )
    msg = str(ei.value)
    for needle in ("OPENROUTER_API_KEY", "scgpt_small", "BADTF", "not empty"):
        assert needle in msg, needle
    assert len(ei.value.failures) >= 4


# ------------------------------------------------------------------ app_v05 source
def _app_tree() -> ast.Module:
    return ast.parse(APP_V05.read_text())


def _run_v05_sweep(tree: ast.Module) -> ast.FunctionDef:
    return next(
        n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "run_v05_sweep"
    )


def test_app_v05_parses_and_ruff_f_clean() -> None:
    _app_tree()
    ruff = PROJECT_ROOT / ".venv" / "bin" / "ruff"
    if not ruff.exists():
        pytest.skip("ruff not installed in .venv")
    r = subprocess.run([str(ruff), "check", "--select", "F", str(APP_V05)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_app_v05_has_no_lifecycle_skip_path() -> None:
    names = {n.id for n in ast.walk(_app_tree()) if isinstance(n, ast.Name)}
    assert "lifecycle_skipped" not in names
    assert "lifecycle_skipped_no_key" not in APP_V05.read_text()


def test_app_v05_preflight_before_first_trainer_or_lifecycle_loop() -> None:
    """Source order: preflight( is called before the first loop that drives the
    trainer or lifecycle, and before the OpenRouter client is built. (Dataset
    fetches run INSIDE preflight via loader closures defined above the call.)"""
    fn = _run_v05_sweep(_app_tree())
    calls = [n for n in ast.walk(fn) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)]
    pre = [c.lineno for c in calls if c.func.id == "preflight"]
    assert pre, "run_v05_sweep never calls preflight("
    work_loops = [
        n.lineno for n in ast.walk(fn)
        if isinstance(n, ast.For) and any(
            isinstance(c, ast.Call) and isinstance(c.func, ast.Name)
            and c.func.id in {"iter_trainer_records", "lifecycle_record"}
            for c in ast.walk(n)
        )
    ]
    clients = [c.lineno for c in calls if c.func.id == "OpenRouterClient"]
    assert work_loops
    assert min(pre) < min(work_loops + clients)


def test_app_v05_no_silent_target_skip() -> None:
    src = APP_V05.read_text()
    assert "not in target_gene_idx (skipped" not in src
    fn = _run_v05_sweep(_app_tree())
    for node in ast.walk(fn):
        if isinstance(node, ast.If) and "target_gene_idx" in ast.unparse(node.test):
            assert not any(isinstance(b, ast.Continue) for b in node.body), ast.unparse(node)


def test_app_v05_lifecycle_except_reraises_backbone_unavailable() -> None:
    fn = _run_v05_sweep(_app_tree())
    tries = [
        t for t in ast.walk(fn)
        if isinstance(t, ast.Try)
        and any(isinstance(c, ast.Call) and isinstance(c.func, ast.Name)
                and c.func.id == "lifecycle_record" for c in ast.walk(t))
    ]
    assert tries, "lifecycle_record is not wrapped — fine, but this test expects the guard"
    for t in tries:
        first = t.handlers[0]
        assert ast.unparse(first.type) == "BackboneUnavailableError"
        assert isinstance(first.body[0], ast.Raise) and first.body[0].exc is None


def test_app_v05_timeout_is_8h() -> None:
    fn = _run_v05_sweep(_app_tree())
    kws = {k.arg: k.value for d in fn.decorator_list if isinstance(d, ast.Call)
           for k in d.keywords}
    assert isinstance(kws["timeout"], ast.Constant) and kws["timeout"].value == 28800


def test_app_v05_fetch_uses_trust_unpinned_false() -> None:
    fn = _run_v05_sweep(_app_tree())
    fetches = [c for c in ast.walk(fn) if isinstance(c, ast.Call)
               and isinstance(c.func, ast.Name) and c.func.id in {"fetch_adamson_all", "fetch_norman"}]
    assert fetches
    for c in fetches:
        kw = {k.arg: k.value for k in c.keywords}
        assert "trust_unpinned" in kw and isinstance(kw["trust_unpinned"], ast.Constant)
        assert kw["trust_unpinned"].value is False
