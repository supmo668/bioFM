"""Run provenance for the v0.6 sweep (T13 builder, T14 record 0, T17 config copy).

The provenance record is written three times per run: ``provenance.json``, and
as record 0 (``{"record_type": "provenance", ...}``) of both
``trainer_runs.jsonl`` and ``lifecycle_runs.jsonl``. It is built at the start of
the run and completed by :func:`finalize_provenance` at the end.

``git_sha`` / ``git_dirty`` are computed on the HOST by :func:`git_state` (the
Modal container has no ``.git``) and passed into the remote function.

This module is pure (stdlib only) so it can be tested without ``modal``.
"""

from __future__ import annotations

import copy
import datetime as _dt
import importlib
import importlib.metadata as _md
import json
import platform
import re
import subprocess
import sys
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0"

# A&D §3: every resolved sweep kwarg that must appear in ``entrypoint_kwargs``.
REQUIRED_ENTRYPOINT_KWARGS: tuple[str, ...] = (
    "norman_n_singletons",
    "norman_n_doublets",
    "adamson_n_per_bin",
    "adamson_n_bins",
    "seeds",
    "n_top_hvg",
    "max_cells_per_pert",
    "n_sweep",
    "r_sweep",
    "backbones",
    "doublet_delim",
    "cooldown_sec",
    "temperature",
)

REQUIRED_KEYS: tuple[str, ...] = (
    "record_type",
    "schema_version",
    "run_id",
    "git_sha",
    "git_dirty",
    "started_at",
    "python",
    "lib_versions",
    "entrypoint_kwargs",
    "datasets",
    "tasks",
    "tasks_excluded",
    "hvg_selection",
    "llm_pool",
    "gpu",
    "hourly_usd",
    "budget_cap_usd",
    "known_limitations",
)

REQUIRED_FINAL_KEYS: tuple[str, ...] = REQUIRED_KEYS + (
    "finished_at",
    "wall_clock_sec",
    "gpu_seconds",
    "gpu_seconds_source",
    "cost_usd_actual",
    "counts",
    "entropies",
    "params_per_task",
    "budget_hit",
    "status",
    # CTO #245 Q2: always written, even as two empty lists — an absent field and
    # a zero are different claims.
    "unparseable_lines",
)

# The two sweep JSONLs whose unparseable lines are located in provenance.
JSONL_NAMES: tuple[str, str] = ("trainer_runs.jsonl", "lifecycle_runs.jsonl")
PREVIEW_CHARS = 80

STATUSES: frozenset[str] = frozenset({"ok", "failed_fallback", "partial", "failed"})

KNOWN_LIMITATIONS: tuple[str, ...] = (
    # CTO #227: stated, not changed.
    "deg_eval_genes_from_heldout_shift (CPA/GEARS convention, stated not changed)",
)

# (key in lib_versions, distribution name for importlib.metadata, import name)
_LIBS: tuple[tuple[str, str, str], ...] = (
    ("torch", "torch", "torch"),
    ("numpy", "numpy", "numpy"),
    ("pandas", "pandas", "pandas"),
    ("anndata", "anndata", "anndata"),
    ("h5py", "h5py", "h5py"),
    ("scanpy", "scanpy", "scanpy"),
    ("scipy", "scipy", "scipy"),
    ("pydantic", "pydantic", "pydantic"),
    ("requests", "requests", "requests"),
    ("modal", "modal", "modal"),
)

_SHA_RE = re.compile(r"[0-9a-f]{40}")
_CONSTRAINT_RE = re.compile(r"[<>=~!^*,]")


def utc_now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


def _resolved_version(dist: str, module: str) -> str | None:
    try:
        return _md.version(dist)
    except _md.PackageNotFoundError:
        pass
    mod = sys.modules.get(module)
    v = getattr(mod, "__version__", None) if mod is not None else None
    return str(v) if v is not None else None


def resolve_lib_versions() -> dict[str, str | None]:
    """Versions actually installed in THIS interpreter (never a constraint string).

    ``torch_cuda`` is ``torch.version.cuda`` (``None`` on a CPU build or when torch
    is absent). Missing packages map to ``None``.
    """
    out: dict[str, str | None] = {
        key: _resolved_version(dist, module) for key, dist, module in _LIBS
    }
    cuda: str | None = None
    if out["torch"] is not None:
        try:
            torch = importlib.import_module("torch")
            c = getattr(getattr(torch, "version", None), "cuda", None)
            cuda = str(c) if c is not None else None
        except Exception:  # noqa: BLE001 — torch installed but unimportable: record None
            cuda = None
    out["torch_cuda"] = cuda
    return out


def git_state(repo_dir: str | Path) -> tuple[str, bool]:
    """``(HEAD sha, working tree dirty?)`` for ``repo_dir``. Raises if not a repo."""
    def _git(*args: str) -> str:
        proc = subprocess.run(
            ["git", "-C", str(repo_dir), *args],
            capture_output=True, text=True, check=False,
        )
        if proc.returncode != 0:
            raise RuntimeError(
                f"git {' '.join(args)} failed in {repo_dir}: {proc.stderr.strip()}"
            )
        return proc.stdout

    sha = _git("rev-parse", "HEAD").strip()
    if not _SHA_RE.fullmatch(sha):
        raise RuntimeError(f"unexpected git sha {sha!r}")
    dirty = bool(_git("status", "--porcelain", "--untracked-files=no").strip())
    return sha, dirty


def make_run_id(git_sha: str, *, now: _dt.datetime | None = None) -> str:
    now = now or _dt.datetime.now(_dt.timezone.utc)
    return f"{now.strftime('%Y%m%dT%H%M%SZ')}-{git_sha[:7]}"


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise ValueError(msg)


def _validate_lib_versions(lv: Mapping[str, Any]) -> None:
    for k, v in lv.items():
        _require(v is None or isinstance(v, str), f"lib_versions[{k!r}] must be str|None")
        if isinstance(v, str):
            _require(not _CONSTRAINT_RE.search(v),
                     f"lib_versions[{k!r}]={v!r} looks like a constraint, not a resolved version")


def build_provenance(
    *,
    run_id: str,
    git_sha: str,
    git_dirty: bool,
    entrypoint_kwargs: Mapping[str, Any],
    datasets: Iterable[Mapping[str, Any]],
    task_plan: Any,
    tasks_excluded: Iterable[Mapping[str, Any]],
    llm_pool: Iterable[str],
    gpu: str,
    hourly_usd: float,
    budget_cap_usd: float,
    lib_versions: Mapping[str, str | None] | None = None,
    started_at: str | None = None,
    known_limitations: Iterable[str] = (),
) -> dict[str, Any]:
    """Start-of-run provenance record; validates presence and types."""
    _require(isinstance(run_id, str) and bool(run_id), "run_id must be a non-empty str")
    _require(isinstance(git_sha, str) and bool(_SHA_RE.fullmatch(git_sha)),
             f"git_sha must be 40 lowercase hex chars, got {git_sha!r}")
    _require(isinstance(git_dirty, bool), "git_dirty must be bool")
    kw = dict(entrypoint_kwargs)
    missing = [k for k in REQUIRED_ENTRYPOINT_KWARGS if k not in kw]
    _require(not missing, f"entrypoint_kwargs missing {missing}")
    tasks = task_plan.to_dict() if hasattr(task_plan, "to_dict") else dict(task_plan)
    ds_list = [dict(d) for d in datasets]
    for d in ds_list:
        miss = [k for k in ("name", "path", "sha256", "n_cells", "n_genes") if k not in d]
        _require(not miss, f"dataset entry {d.get('name')!r} missing {miss}")
    excl = [dict(e) for e in tasks_excluded]
    for e in excl:
        _require({"label", "reason"} <= set(e), f"tasks_excluded entry needs label+reason: {e}")
    pool = [str(m) for m in llm_pool]
    _require(isinstance(gpu, str) and bool(gpu), "gpu must be a non-empty str")
    _require(isinstance(hourly_usd, (int, float)), "hourly_usd must be a number")
    _require(isinstance(budget_cap_usd, (int, float)), "budget_cap_usd must be a number")
    lv = dict(lib_versions) if lib_versions is not None else resolve_lib_versions()
    _validate_lib_versions(lv)
    limitations = list(KNOWN_LIMITATIONS)
    limitations += [s for s in known_limitations if s not in limitations]

    prov: dict[str, Any] = {
        "record_type": "provenance",
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "git_sha": git_sha,
        "git_dirty": git_dirty,
        "started_at": started_at or utc_now_iso(),
        "python": platform.python_version(),
        "lib_versions": lv,
        "entrypoint_kwargs": kw,
        "datasets": ds_list,
        "tasks": tasks,
        "tasks_excluded": excl,
        # per-task n filled at finalize (CTO #227 cond. 3)
        "hvg_selection": {"mode": "train_only"},
        "llm_pool": pool,
        "gpu": gpu,
        "hourly_usd": float(hourly_usd),
        "budget_cap_usd": float(budget_cap_usd),
        "known_limitations": limitations,
    }
    return prov


def finalize_provenance(
    prov: Mapping[str, Any],
    *,
    finished_at: str,
    gpu_seconds: float,
    cost_usd_actual: float,
    counts: Mapping[str, Any],
    entropies: Mapping[str, Any],
    hvg_n_per_task: Mapping[str, Any],
    params_per_task: Mapping[str, Any],
    budget_hit: bool,
    status: str,
    unparseable_lines: Mapping[str, Any],
    gpu_seconds_source: str = "wall_clock_of_gpu_function",
) -> dict[str, Any]:
    """Return a completed copy of ``prov``; refuses a record without ``started_at``.

    ``unparseable_lines`` has no default (CTO #245 Q2): the caller must have
    scanned both JSONLs (:func:`scan_unparseable`) and passes both keys, even
    when the lists are empty.
    """
    _require(bool(prov.get("started_at")), "provenance record has no started_at; refusing to finalize")
    missing = [k for k in REQUIRED_KEYS if k not in prov]
    _require(not missing, f"provenance record missing {missing}")
    _require(status in STATUSES, f"status must be one of {sorted(STATUSES)}, got {status!r}")
    _require(isinstance(budget_hit, bool), "budget_hit must be bool")
    _require(isinstance(gpu_seconds, (int, float)) and gpu_seconds >= 0,
             "gpu_seconds must be a non-negative number")
    _validate_unparseable(unparseable_lines)
    started = _dt.datetime.fromisoformat(prov["started_at"])
    finished = _dt.datetime.fromisoformat(finished_at)
    out = copy.deepcopy(dict(prov))
    out["hvg_selection"] = dict(out["hvg_selection"]) | {"n_per_task": dict(hvg_n_per_task)}
    out.update({
        "finished_at": finished_at,
        "wall_clock_sec": (finished - started).total_seconds(),
        "gpu_seconds": float(gpu_seconds),
        "gpu_seconds_source": gpu_seconds_source,
        "cost_usd_actual": float(cost_usd_actual),
        "counts": dict(counts),
        "entropies": dict(entropies),
        "params_per_task": dict(params_per_task),
        "budget_hit": budget_hit,
        "status": status,
        "unparseable_lines": {k: [dict(e) for e in unparseable_lines[k]] for k in JSONL_NAMES},
    })
    return out


def _validate_unparseable(u: Any) -> None:
    _require(isinstance(u, Mapping) and set(u) == set(JSONL_NAMES),
             f"unparseable_lines must have exactly the keys {list(JSONL_NAMES)}, got {u!r}")
    for k in JSONL_NAMES:
        _require(isinstance(u[k], list), f"unparseable_lines[{k!r}] must be a list, got {u[k]!r}")
        for e in u[k]:
            _require(isinstance(e, Mapping) and {"line", "byte_offset", "preview"} <= set(e),
                     f"unparseable_lines[{k!r}] entry needs line/byte_offset/preview: {e!r}")


def fail_provenance(
    prov: Mapping[str, Any],
    exc: BaseException,
    *,
    phase: str,
    **finalize_kwargs: Any,
) -> dict[str, Any]:
    """Finalise ``prov`` as ``status="failed"`` for an aborted run (CTO #245 Q1).

    Adds a ``failure`` block ``{phase, error_type, error_class, message,
    traceback}``. ``finalize_kwargs`` are :func:`finalize_provenance`'s, minus
    ``status`` and ``entropies`` (an aborted run reports none).
    """
    from perturb_eval.experiments.errors import failure_fields  # keeps this module stdlib-only at import

    _require("status" not in finalize_kwargs, "fail_provenance sets status='failed' itself")
    finalize_kwargs.setdefault("entropies", {})
    out = finalize_provenance(prov, status="failed", **finalize_kwargs)
    out["failure"] = failure_fields(exc, phase=phase)
    return out


def read_jsonl_locating(path: str | Path) -> tuple[list[Any], list[dict[str, Any]]]:
    """Parse a JSONL file; return ``(records, unparseable)`` (CTO #245 Q2).

    Every non-blank line that is not valid JSON is recorded as
    ``{"line": n, "byte_offset": off, "preview": first 80 chars}`` — ``line`` is
    1-based, ``byte_offset`` is the offset of the line's first byte in the file.
    Blank lines are ignored. A missing file yields ``([], [])``.
    """
    p = Path(path)
    if not p.exists():
        return [], []
    records: list[Any] = []
    bad: list[dict[str, Any]] = []
    offset = 0
    for n, raw in enumerate(p.read_bytes().split(b"\n"), start=1):
        start, offset = offset, offset + len(raw) + 1
        text = raw.decode("utf-8", errors="replace").strip()
        if not text:
            continue
        try:
            records.append(json.loads(text))
        except json.JSONDecodeError:
            bad.append({"line": n, "byte_offset": start, "preview": text[:PREVIEW_CHARS]})
    return records, bad


def scan_unparseable(trainer_jsonl: str | Path, lifecycle_jsonl: str | Path) -> dict[str, list]:
    """``{"trainer_runs.jsonl": [...], "lifecycle_runs.jsonl": [...]}`` — both keys always."""
    return {
        JSONL_NAMES[0]: read_jsonl_locating(trainer_jsonl)[1],
        JSONL_NAMES[1]: read_jsonl_locating(lifecycle_jsonl)[1],
    }


def format_unparseable(path: str | Path, bad: Iterable[Mapping[str, Any]]) -> str:
    """Human-readable location list naming file, line and byte offset."""
    return "; ".join(
        f"{path}: line {e['line']} (byte offset {e['byte_offset']}): {e['preview']!r}"
        for e in bad
    )


def _add(bucket: dict, key: str, value: Any) -> None:
    if value is None:
        return
    vals = bucket.setdefault(key, [])
    if value not in vals:
        vals.append(value)
        vals.sort(key=lambda x: (str(type(x)), x))


def collect_hvg_and_params(
    trainer_records: Iterable[Mapping[str, Any]],
    lifecycle_records: Iterable[Mapping[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Per-task HVG sizes and learned-parameter counts (CTO #227 cond. 3, 5).

    Keys are ``"<dataset>:<task>"``. Values list the distinct observed values:
    ``hvg[k]["trainer"|"lifecycle"] = {"hvg_n": [...], "hvg_n_forced": [...],
    "hvg_mode": [...]}``; ``params[k]["trainer"|"lifecycle"] = {backbone: [n_params...]}``.
    Records whose ``record_type`` is ``"provenance"`` are ignored.
    """
    hvg: dict[str, Any] = {}
    params: dict[str, Any] = {}

    def _key(r: Mapping[str, Any]) -> str:
        return f"{r.get('dataset')}:{r.get('task', r.get('task_id'))}"

    for r in trainer_records:
        if r.get("record_type") == "provenance":
            continue
        k = _key(r)
        h = hvg.setdefault(k, {}).setdefault("trainer", {})
        _add(h, "hvg_n", r.get("hvg_n"))
        _add(h, "hvg_n_forced", r.get("hvg_n_forced"))
        _add(h, "hvg_mode", r.get("hvg_mode"))
        if r.get("n_params") is not None:
            _add(params.setdefault(k, {}).setdefault("trainer", {}),
                 str(r.get("backbone")), r["n_params"])
    for r in lifecycle_records:
        if r.get("record_type") == "provenance":
            continue
        k = _key(r)
        h = hvg.setdefault(k, {}).setdefault("lifecycle", {})
        for n in r.get("hvg_n_per_round") or ():
            _add(h, "hvg_n", n)
        for n in r.get("hvg_n_forced_per_round") or ():
            _add(h, "hvg_n_forced", n)
        _add(h, "hvg_mode", r.get("hvg_mode"))
        if r.get("n_params") is not None:
            _add(params.setdefault(k, {}).setdefault("lifecycle", {}),
                 str(r.get("backbone_used")), r["n_params"])
    return hvg, params


def write_run_config(
    dir: str | Path,
    run_id: str,
    entrypoint_kwargs: Mapping[str, Any],
    git_sha: str,
) -> Path:
    """Write ``<dir>/configs/runs/<run_id>.json``; never overwrites an existing file.

    If ``<run_id>.json`` exists, ``<run_id>.1.json``, ``<run_id>.2.json`` ... is used.
    """
    runs = Path(dir) / "configs" / "runs"
    runs.mkdir(parents=True, exist_ok=True)
    body = json.dumps(
        {"run_id": run_id, "git_sha": git_sha, "entrypoint_kwargs": dict(entrypoint_kwargs)},
        indent=2, sort_keys=True, default=str,
    ) + "\n"
    i = 0
    while True:
        name = f"{run_id}.json" if i == 0 else f"{run_id}.{i}.json"
        path = runs / name
        try:
            with path.open("x", encoding="utf-8") as fh:  # exclusive create: no overwrite
                fh.write(body)
            return path
        except FileExistsError:
            i += 1


def jsonl_provenance_line(prov: Mapping[str, Any]) -> str:
    """One-line JSON for record 0 of a JSONL (no trailing newline)."""
    _require(prov.get("record_type") == "provenance", "not a provenance record")
    return json.dumps(dict(prov), default=str, sort_keys=True)
