"""CTO #245 Q1 — sweep error taxonomy (transient vs programming vs other).

transient → per-cell error record, run continues; anything else → the run
aborts, provenance is finalised ``status="failed"`` with the exception type and
traceback, and the exception propagates.
"""

from __future__ import annotations

import json
import socket

import numpy as np
import pytest
import requests

from perturb_eval.agentic_lifecycle.architect_dispatch import BackboneUnavailableError
from perturb_eval.experiments import heldout
from perturb_eval.experiments import provenance as pv
from perturb_eval.experiments.errors import (
    PROGRAMMING_EXCEPTIONS,
    TRANSIENT_EXCEPTIONS,
    classify,
    transient_error_fields,
)
from perturb_eval.experiments.v05_preflight import PreflightError
from perturb_eval.experiments.v05_sweep import iter_lifecycle_records, run_guarded
from perturb_eval.experiments.v05_tasks import TaskPlan

try:
    import torch
except ImportError:  # torch-less venv: only the OOM cases skip (named below)
    torch = None

_needs_torch = pytest.mark.skipif(torch is None, reason="torch absent: CUDA OOM class")


def _oom():
    return torch.cuda.OutOfMemoryError("CUDA out of memory")


# ---------------------------------------------------------------- classify()
@_needs_torch
def test_torch_oom_transient():
    assert classify(_oom()) == "transient"
    assert torch.cuda.OutOfMemoryError in TRANSIENT_EXCEPTIONS


@pytest.mark.parametrize(
    "exc",
    [
        MemoryError(),
        TimeoutError("timed out"),
        ConnectionError("reset"),
        ConnectionResetError("reset by peer"),
        BrokenPipeError(),
        socket.gaierror("dns"),
        requests.ConnectionError("net"),
        requests.Timeout("slow"),
        requests.HTTPError("503"),
    ],
)
def test_transient(exc):
    assert classify(exc) == "transient"


@pytest.mark.parametrize(
    "exc",
    [
        TypeError("x"),
        AttributeError("x"),
        NameError("x"),
        KeyError("x"),
        ImportError("x"),
        ModuleNotFoundError("x"),
        IndexError("x"),
        ValueError("x"),
        AssertionError("x"),
        NotImplementedError("x"),
        BackboneUnavailableError("scgpt_small unavailable"),
        PreflightError(["key absent"]),
        # ValueError-shaped requests errors are call-site bugs, not the network.
        requests.exceptions.MissingSchema("no scheme"),
        requests.exceptions.InvalidURL("bad"),
        json.JSONDecodeError("x", "doc", 0),
    ],
)
def test_programming(exc):
    assert classify(exc) == "programming"


@pytest.mark.parametrize(
    "exc",
    [
        RuntimeError("CUDA error: illegal memory access"),
        FileNotFoundError("missing"),  # an OSError, but not network → not transient
        PermissionError("denied"),
        ZeroDivisionError(),
    ],
)
def test_other(exc):
    assert classify(exc) == "other"


def test_lists_are_tuples_of_exception_types():
    for t in TRANSIENT_EXCEPTIONS + PROGRAMMING_EXCEPTIONS:
        assert isinstance(t, type) and issubclass(t, BaseException)
    assert FileNotFoundError not in TRANSIENT_EXCEPTIONS


def test_error_fields():
    try:
        raise MemoryError("oom")
    except MemoryError as e:
        f = transient_error_fields(e)
    assert f["error_type"] == "builtins.MemoryError"
    assert f["error_class"] == "transient"
    assert "MemoryError: oom" in f["traceback"] and "Traceback" in f["traceback"]
    assert f["error"] == "MemoryError: oom"
    with pytest.raises(ValueError):
        transient_error_fields(TypeError("not transient"))


# ---------------------------------------------------------------- trainer loop
def _ds() -> dict:
    labels = np.repeat(np.array(["CTRL", "TFA", "TFB"]), 4)
    X = np.zeros((12, 5), dtype=np.float64)
    X[:, 0] = np.where(labels == "TFA", 0.0, 3.0)
    X[:, 1] = np.where(labels == "TFB", 0.0, 3.0)
    X[:, 2] = np.arange(12) % 3
    return {
        "X": X,
        "labels": labels,
        "control_mask": labels == "CTRL",
        "target_gene_idx": {"TFA": (0,), "TFB": (1,)},
        "hvg_n_top": 3,
    }


class _Stub:
    """fit_and_score stand-in raising ``exc`` on call number ``on`` (1-based)."""

    def __init__(self, exc: BaseException, on: int = 1) -> None:
        self.exc, self.on, self.calls = exc, on, 0

    def __call__(self, view, backbone_name, cfg):
        self.calls += 1
        if self.calls == self.on:
            raise self.exc
        return {"msd_topk": 0.1, "backbone": backbone_name, "n_params": 3}


def _trainer_iter(**over):
    kw = dict(
        dataset_name="t",
        ds=_ds(),
        tasks=["TFA", "TFB"],
        backbones=("linear",),
        r_sweep=(1,),
        seeds=(0,),
    )
    kw.update(over)
    return heldout.iter_trainer_records(**kw)


def _prov() -> dict:
    plan = TaskPlan(
        adamson=("A",),
        norman_singletons=(),
        norman_doublets=(),
        strata={"adamson:A": 0},
        eligible_counts={"adamson": 1},
    )
    kwargs = {k: 1 for k in pv.REQUIRED_ENTRYPOINT_KWARGS}
    return pv.build_provenance(
        run_id="r1",
        git_sha="a" * 40,
        git_dirty=False,
        entrypoint_kwargs=kwargs,
        datasets=[],
        task_plan=plan,
        tasks_excluded=[],
        llm_pool=[],
        gpu="A100-40GB",
        hourly_usd=1.32,
        budget_cap_usd=28.0,
        # A2-4: the trainer grid is a required provenance block.
        trainer_grid=heldout.trainer_grid(backbones=("linear",), r_sweep=(1,), seeds=(0,)),
    )


def _fail(prov, exc, phase):
    return pv.fail_provenance(
        prov,
        exc,
        phase=phase,
        finished_at="2099-01-01T00:00:00+00:00",
        gpu_seconds=1.0,
        cost_usd_actual=0.0,
        counts={"n_trainer_runs": 0},
        hvg_n_per_task={},
        params_per_task={},
        budget_hit=False,
        unparseable_lines={"trainer_runs.jsonl": [], "lifecycle_runs.jsonl": []},
    )


def test_trainer_typeerror_aborts_and_fails_provenance(monkeypatch):
    stub = _Stub(TypeError("bad arg"), on=1)
    monkeypatch.setattr(heldout, "fit_and_score", stub)
    sunk: list[dict] = []
    written: dict = {}
    prov = _prov()

    def on_abort(exc):
        written.update(_fail(prov, exc, "trainer"))

    with pytest.raises(TypeError, match="bad arg"):
        run_guarded(_trainer_iter(), sink=sunk.append, on_abort=on_abort)
    assert stub.calls == 1, "cell 2 must never run"
    assert sunk == []
    assert written["status"] == "failed"
    f = written["failure"]
    assert f["phase"] == "trainer"
    assert f["error_type"] == "builtins.TypeError"
    assert f["error_class"] == "programming"
    assert "TypeError: bad arg" in f["traceback"] and "Traceback" in f["traceback"]
    assert written["unparseable_lines"] == {"trainer_runs.jsonl": [], "lifecycle_runs.jsonl": []}


@pytest.mark.parametrize("exc", [ValueError("v"), IndexError("i"), RuntimeError("r")])
def test_trainer_non_transient_aborts(monkeypatch, exc):
    stub = _Stub(exc, on=1)
    monkeypatch.setattr(heldout, "fit_and_score", stub)
    with pytest.raises(type(exc)):
        list(_trainer_iter())
    assert stub.calls == 1


@_needs_torch
def test_trainer_transient_records_and_continues(monkeypatch):
    stub = _Stub(_oom(), on=1)
    monkeypatch.setattr(heldout, "fit_and_score", stub)
    sunk: list[dict] = []
    n = run_guarded(_trainer_iter(), sink=sunk.append, on_abort=lambda e: pytest.fail("abort"))
    assert n == 2 and stub.calls == 2
    err, ok = sunk
    assert err["msd_topk"] == float("inf")
    assert err["error_type"].endswith("OutOfMemoryError")
    assert err["error_class"] == "transient"
    assert "OutOfMemoryError" in err["traceback"]
    assert err["hvg_mode"] == "train_only"
    assert "error" not in ok and ok["msd_topk"] == 0.1


# ---------------------------------------------------------------- lifecycle loop
def _life_fn(exc: BaseException | None, on: int = 1):
    calls = {"n": 0}

    def fn(*, task, dataset_name, ds, seed, pool, max_rounds):
        calls["n"] += 1
        if exc is not None and calls["n"] == on:
            raise exc
        return {
            "task_id": task,
            "dataset": dataset_name,
            "seed": seed,
            "final_msd_topk": 0.2,
            "steps": [],
        }

    return fn, calls


def _life_iter(fn):
    return iter_lifecycle_records(
        datasets=[("t", _ds(), ["TFA", "TFB"])],
        seeds=(0,),
        pool=object(),
        record_fn=fn,
    )


def test_lifecycle_typeerror_aborts(monkeypatch):
    fn, calls = _life_fn(TypeError("oops"))
    sunk: list[dict] = []
    seen: list[BaseException] = []
    with pytest.raises(TypeError):
        run_guarded(_life_iter(fn), sink=sunk.append, on_abort=seen.append)
    assert calls["n"] == 1 and sunk == [] and isinstance(seen[0], TypeError)


def test_lifecycle_backbone_unavailable_aborts():
    fn, calls = _life_fn(BackboneUnavailableError("scgpt_small"))
    with pytest.raises(BackboneUnavailableError):
        list(_life_iter(fn))
    assert calls["n"] == 1


def test_lifecycle_transient_records_and_continues():
    fn, calls = _life_fn(requests.ConnectionError("net down"))
    recs = list(_life_iter(fn))
    assert calls["n"] == 2 and len(recs) == 2
    err = recs[0]
    assert err["final_msd_topk"] == float("inf")
    assert err["error_type"] == "requests.exceptions.ConnectionError"
    assert err["error_class"] == "transient"
    assert "net down" in err["traceback"]
    assert err["task_id"] == "TFA" and err["steps"] == [] and err["n_rounds"] == 0
    assert "error" not in recs[1]


def test_lifecycle_task_missing_raises():
    fn, _ = _life_fn(None)
    with pytest.raises(RuntimeError, match="target_gene_idx"):
        list(
            iter_lifecycle_records(
                datasets=[("t", _ds(), ["NOPE"])], seeds=(0,), pool=object(), record_fn=fn
            )
        )


def test_lifecycle_should_stop():
    fn, calls = _life_fn(None)
    recs = list(
        iter_lifecycle_records(
            datasets=[("t", _ds(), ["TFA", "TFB"])],
            seeds=(0,),
            pool=object(),
            record_fn=fn,
            should_stop=lambda: True,
        )
    )
    assert recs == [] and calls["n"] == 0


def test_trainer_transient_memoryerror_records_and_continues(monkeypatch):
    """Torch-independent twin of the OOM case."""
    stub = _Stub(MemoryError("host RAM"), on=1)
    monkeypatch.setattr(heldout, "fit_and_score", stub)
    recs = list(_trainer_iter())
    assert stub.calls == 2 and len(recs) == 2
    assert recs[0]["error_type"] == "builtins.MemoryError"
    assert recs[0]["error_class"] == "transient" and "host RAM" in recs[0]["traceback"]
    assert recs[0]["msd_topk"] == float("inf")
