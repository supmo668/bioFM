"""Minimal .env loader (no python-dotenv dependency).

We keep this small by design: the pipeline should work with a shell-exported
environment just as well. Precedence: real environment wins over .env file.
"""

from __future__ import annotations

import os
from pathlib import Path


def load_env_file(path: Path | str = ".env", *, override: bool = False) -> dict[str, str]:
    """Load KEY=VALUE pairs from ``path`` into ``os.environ``.

    - ``#`` comments and blank lines are skipped.
    - Values may be quoted with single or double quotes (stripped).
    - Precedence: existing env vars are kept unless ``override=True``.

    Returns a dict of what was applied to os.environ (useful for debug logs).
    """
    p = Path(path)
    if not p.exists():
        return {}
    applied: dict[str, str] = {}
    for raw in p.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if not key:
            continue
        if not override and key in os.environ:
            continue
        os.environ[key] = value
        applied[key] = value
    return applied


def expand(value: str) -> str:
    """Expand ``${VAR:default}`` substitutions against os.environ."""
    if not value.startswith("${") or not value.endswith("}"):
        return value
    inner = value[2:-1]
    name, _, default = inner.partition(":")
    return os.environ.get(name, default)
