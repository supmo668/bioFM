"""The numeric environment a test run used (HACA-124).

Some pinned numbers move by a few ulp with the numpy/BLAS build (HACA-121): the same
CPU gives different last bits under numpy 2.4.4 and 2.5.5, and the aarch64 Paperclip host
and the x86_64 CI runner both differ from the build the pins were recorded on. Those
tests compare within a bounded ulp, and every run prints this record in its terminal
summary (``tests/conftest.py``), so a result can always be tied to the build that produced it.
``tests/fixtures/numeric_environment.json`` keeps the environments the bounds were
checked on.
"""

from __future__ import annotations

import json
import platform
import sys
from importlib import metadata
from typing import Any


def _version(dist: str) -> str | None:
    try:
        return metadata.version(dist)
    except metadata.PackageNotFoundError:
        return None


def _blas() -> dict[str, Any]:
    import numpy as np

    try:
        deps = np.show_config(mode="dicts")["Build Dependencies"]
    except Exception as exc:  # numpy < 1.25 has no mode="dicts"
        return {"error": f"{type(exc).__name__}: {exc}"}
    out: dict[str, Any] = {}
    for key in ("blas", "lapack"):
        d = deps.get(key, {})
        out[key] = {
            "name": d.get("name"),
            "version": d.get("version"),
            "config": d.get("openblas configuration"),
        }
    return out


def _runtime_blas() -> list[dict[str, Any]]:
    """The BLAS cores actually selected at run time (OpenBLAS DYNAMIC_ARCH), if threadpoolctl
    is available; the build config above names only the core the wheel was built on."""
    try:
        from threadpoolctl import threadpool_info

        info = threadpool_info()
    except Exception:  # absent, or a broken library: never fail the run over a record
        return []
    keep = ("internal_api", "version", "architecture", "num_threads")
    return [{k: i.get(k) for k in keep} for i in info if i.get("user_api") == "blas"]


def numeric_environment() -> dict[str, Any]:
    return {
        "machine": platform.machine(),
        "python": sys.version.split()[0],
        "numpy": _version("numpy"),
        "scipy": _version("scipy"),
        "scikit-learn": _version("scikit-learn"),
        "torch": _version("torch"),
        "blas": _blas(),
        "blas_runtime": _runtime_blas(),
    }


def header_line() -> str:
    return "numeric environment: " + json.dumps(numeric_environment(), sort_keys=True)
