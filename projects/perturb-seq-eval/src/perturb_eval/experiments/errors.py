"""Sweep error taxonomy (CTO #245 Q1): transient vs programming vs other.

Both sweep loops (trainer: :func:`perturb_eval.experiments.heldout.iter_trainer_records`;
lifecycle: :func:`perturb_eval.experiments.v05_sweep.iter_lifecycle_records`)
classify every per-cell exception with :func:`classify`:

* ``"transient"`` — environmental; the cell becomes an error record
  (``msd = inf``, ``error_type``, ``error_class``, ``traceback``) and the run
  continues. The analyser still refuses a summary over any error record unless
  given an explicit ``allow_partial`` reason.
* ``"programming"`` / ``"other"`` — the run ABORTS: provenance is finalised
  ``status="failed"`` with type + traceback and the exception propagates.
  The default is abort: guilty until proven loud. Only the types listed in
  :data:`TRANSIENT_EXCEPTIONS` may continue.

Precedent: ``llm_agent_pool.FALLBACK_EXCEPTIONS`` (runtime-only fallback;
``TypeError`` propagates).

ValueError / IndexError are PROGRAMMING (abort). In this code base they are
raised by our own contract checks (``fit_and_score`` unknown backbone,
``select_for_task`` empty mask / unknown task, ``remap_targets``) and by numpy on
shape/index bugs; nothing environmental raises them. Treating them as transient
would turn a bug into a column of ``inf`` rows. Subclasses follow the same rule:
``json.JSONDecodeError``, ``pydantic.ValidationError``, ``numpy.linalg.LinAlgError``
and the ValueError-shaped ``requests`` errors (``MissingSchema``, ``InvalidURL``,
``InvalidSchema``, ``InvalidHeader``) all abort. LLM transport/parse failures never
reach the sweep loop: ``LLMAgentPool`` handles them inside the pool, and a
fallback step then fails the run under C-KEY-2.
"""

from __future__ import annotations

import socket
import traceback
from typing import Any, Literal

import requests

from perturb_eval.agentic_lifecycle.architect_dispatch import BackboneUnavailableError
from perturb_eval.experiments.v05_preflight import PreflightError

ErrorClass = Literal["transient", "programming", "other"]


def _torch_oom() -> tuple[type[BaseException], ...]:
    try:
        import torch
    except ImportError:  # torch-less env: nothing to list (sweep image pins torch)
        return ()
    found: list[type[BaseException]] = []
    for owner, name in ((torch.cuda, "OutOfMemoryError"), (torch, "OutOfMemoryError")):
        t = getattr(owner, name, None)
        if isinstance(t, type) and issubclass(t, BaseException) and t not in found:
            found.append(t)
    return tuple(found)


# Each entry: one line on why it is environmental, not a bug in our code.
TRANSIENT_EXCEPTIONS: tuple[type[BaseException], ...] = (
    # GPU memory exhausted for this cell's size (backbone x N x HVG); the next,
    # smaller cell can succeed. torch.OutOfMemoryError (>=2.5) is the same class.
    *_torch_oom(),
    # Host RAM exhausted for this cell; resource, not logic.
    MemoryError,
    # Wall-clock limit on an I/O wait (incl. socket.timeout alias).
    TimeoutError,
    # Network OSError family: ConnectionReset/Refused/Aborted, BrokenPipe.
    ConnectionError,
    # DNS resolution failure (OSError subclass, not a ConnectionError).
    socket.gaierror,
    # HTTP transport failures (ConnectionError, Timeout, HTTPError, ...). The
    # ValueError-shaped subclasses (MissingSchema, InvalidURL, ...) are caught
    # as PROGRAMMING first because :func:`classify` checks that list first.
    requests.RequestException,
)

# Always abort. Checked BEFORE the transient list so a class inheriting from
# both (e.g. requests.MissingSchema(RequestException, ValueError)) aborts.
PROGRAMMING_EXCEPTIONS: tuple[type[BaseException], ...] = (
    TypeError,
    AttributeError,
    NameError,
    KeyError,
    ImportError,
    IndexError,
    ValueError,
    AssertionError,
    NotImplementedError,
    # Our own fail-closed contracts (C-TORCH-2, T22): never an error record.
    BackboneUnavailableError,
    PreflightError,
)


def classify(exc: BaseException) -> ErrorClass:
    """``"programming"`` > ``"transient"`` > ``"other"`` (first match wins)."""
    if isinstance(exc, PROGRAMMING_EXCEPTIONS):
        return "programming"
    if isinstance(exc, TRANSIENT_EXCEPTIONS):
        return "transient"
    return "other"


def qualified_name(exc: BaseException) -> str:
    t = type(exc)
    return f"{t.__module__}.{t.__qualname__}"


def format_traceback(exc: BaseException) -> str:
    return "".join(traceback.format_exception(exc))


def transient_error_fields(exc: BaseException) -> dict[str, Any]:
    """Error-record fields for a TRANSIENT exception; refuses anything else."""
    cls = classify(exc)
    if cls != "transient":
        raise ValueError(
            f"{qualified_name(exc)} is {cls!r}, not transient; it must abort the run"
        )
    return {
        "error": f"{type(exc).__name__}: {exc}",
        "error_type": qualified_name(exc),
        "error_class": cls,
        "traceback": format_traceback(exc),
    }


def failure_fields(exc: BaseException, *, phase: str) -> dict[str, Any]:
    """The ``failure`` block of a ``status="failed"`` provenance record."""
    return {
        "phase": phase,
        "error_type": qualified_name(exc),
        "error_class": classify(exc),
        "message": str(exc),
        "traceback": format_traceback(exc),
    }


__all__ = [
    "PROGRAMMING_EXCEPTIONS",
    "TRANSIENT_EXCEPTIONS",
    "classify",
    "failure_fields",
    "format_traceback",
    "qualified_name",
    "transient_error_fields",
]
