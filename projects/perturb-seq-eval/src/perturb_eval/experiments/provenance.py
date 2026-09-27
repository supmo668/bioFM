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
    # Amendment 2 A2-4: N is not a trainer-sweep axis (no ``n_sweep``).
    "r_sweep",
    "backbones",
    "doublet_delim",
    "cooldown_sec",
    "temperature",
    # CTO #283 condition 3 (gate finding OWN-1): the stop-and-report spend.
    "spend_stop_usd",
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
    # Amendment 2 A2-4: the trainer grid as run (distinct count, seeds).
    "trainer_grid",
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

# LabelContract.to_provenance() top-level keys (kept literal: this module is stdlib-only).
_LABEL_CONTRACT_KEYS: tuple[str, ...] = ("aliases", "structural_controls", "excluded")

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



_SOURCE_PART = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,99}$")


def llm_key_source(store: str, project_slug: str, env: str, *, home_project: str) -> dict[str, Any]:
    """Describe WHERE the LLM credential came from — never the credential itself.

    Principal directive (2026-09-24) + CTO #265: the key is injected at run time
    (``infisical run ... -- modal run``) and provenance records only its source.
    ``cross_project`` is explicit because a store outside the home project reads,
    out of context, like a typo for the home one. Each part must look like a slug:
    anything shaped like a secret (``sk-...``, over-long, empty) is refused, so the
    value cannot leak into provenance through this field.
    """
    for name, part in (("store", store), ("project_slug", project_slug), ("env", env),
                       ("home_project", home_project)):
        if not isinstance(part, str) or not _SOURCE_PART.match(part) or part.lower().startswith("sk-"):
            raise ValueError(f"llm_key_source.{name} must be a short slug, not a credential-shaped value")
    return {
        "store": store,
        "project_slug": project_slug,
        "env": env,
        "home_project": home_project,
        "cross_project": project_slug != home_project,
    }


def parse_key_source(spec: str | None, *, home_project: str) -> dict[str, Any] | None:
    """Parse ``OPENROUTER_KEY_SOURCE`` (``"<store>:<project_slug>:<env>"``).

    Returns the :func:`llm_key_source` dict, or ``None`` when ``spec`` is
    missing, malformed, or any part is credential-shaped; the preflight then
    refuses the run (C-KEY-SOURCE). The value is never echoed.
    """
    if not isinstance(spec, str) or any(c.isspace() for c in spec):
        return None
    parts = spec.split(":")
    if len(parts) != 3:
        return None
    try:
        return llm_key_source(*parts, home_project=home_project)
    except ValueError:
        return None


def preregistration_record(repo_dir: str | Path, rel_path: str) -> dict[str, str]:
    """Pin the pre-registration the sweep runs under (CTO #265 (a)).

    Returns ``{path, sha256, commit}`` where ``commit`` is the last commit that
    touched the file. Refuses an untracked file or one with UNCOMMITTED edits:
    a hypothesis edited after the fact is not a pre-registration.
    """
    import hashlib

    repo = Path(repo_dir)
    f = repo / rel_path
    if not f.is_file():
        raise ValueError(f"pre-registration {rel_path!r} does not exist")

    def git(*args: str) -> str:
        return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True,
                              text=True).stdout.strip()

    if not git("ls-files", "--", rel_path):
        raise ValueError(f"pre-registration {rel_path!r} is not tracked by git")
    if git("status", "--porcelain", "--", rel_path):
        raise ValueError(f"pre-registration {rel_path!r} has uncommitted edits; commit it before the sweep")
    commit = git("log", "-1", "--format=%H", "--", rel_path)
    return {"path": rel_path, "sha256": hashlib.sha256(f.read_bytes()).hexdigest(), "commit": commit}


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


# ``perturb_eval.experiments.heldout.trainer_grid`` keys (A2-4).
_TRAINER_GRID_KEYS: tuple[str, ...] = (
    "backbones", "r_sweep", "seeds", "n_records_per_task", "n_distinct_per_task",
    "distinct_by_backbone",
)


def _validate_trainer_grid(grid: Any) -> dict[str, Any]:
    _require(isinstance(grid, Mapping), "trainer_grid must be a mapping (A2-4)")
    missing = [k for k in _TRAINER_GRID_KEYS if k not in grid]
    _require(not missing, f"trainer_grid missing {missing} (A2-4)")
    for k in ("n_records_per_task", "n_distinct_per_task"):
        v = grid[k]
        _require(isinstance(v, int) and not isinstance(v, bool) and v >= 0,
                 f"trainer_grid[{k!r}] must be a non-negative int, got {v!r}")
    return copy.deepcopy(dict(grid))


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
    labels_excluded: Iterable[Mapping[str, Any]] = (),
    gpu: str,
    hourly_usd: float,
    budget_cap_usd: float,
    lib_versions: Mapping[str, str | None] | None = None,
    started_at: str | None = None,
    known_limitations: Iterable[str] = (),
    llm_key_source: Mapping[str, Any] | None = None,
    preregistration: Mapping[str, str] | None = None,
    device: str | None = None,
    llm_cache_dir: str | None = None,
    trainer_grid: Mapping[str, Any],
) -> dict[str, Any]:
    """Start-of-run provenance record; validates presence and types.

    ``device`` is the torch device the run trains on (``"cuda"``/``"cpu"``;
    QG C9) and ``llm_cache_dir`` the LLM disk cache the run reads and writes
    (QG C6); both are always present, ``None`` when not supplied.

    ``trainer_grid`` (required; amendment 2 A2-4) is
    :func:`perturb_eval.experiments.heldout.trainer_grid`: records per task,
    distinct fits (the H1/H2 oracle's configuration count), per-backbone
    breakdown and seeds.

    A dataset entry may carry ``label_contract`` (CTO #250: the loader's
    ``LabelContract.to_provenance()``); its shape is validated. Every
    ``labels_excluded`` entry (``{"dataset", "label", "reason"}``, the labels
    the contract dropped) is appended to ``tasks_excluded``.
    """
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
        if "label_contract" in d:
            lc = d["label_contract"]
            _require(
                isinstance(lc, Mapping)
                and all(isinstance(lc.get(k), Mapping) for k in _LABEL_CONTRACT_KEYS),
                f"dataset {d.get('name')!r} label_contract must map each of "
                f"{list(_LABEL_CONTRACT_KEYS)} to a dict",
            )
    excl = [dict(e) for e in tasks_excluded]
    for e in excl:
        _require({"label", "reason"} <= set(e), f"tasks_excluded entry needs label+reason: {e}")
    for e in labels_excluded:
        e = dict(e)
        _require({"dataset", "label", "reason"} <= set(e),
                 f"labels_excluded entry needs dataset+label+reason: {e}")
        excl.append(e)
    pool = [str(m) for m in llm_pool]
    _require(isinstance(gpu, str) and bool(gpu), "gpu must be a non-empty str")
    _require(isinstance(hourly_usd, (int, float)), "hourly_usd must be a number")
    _require(isinstance(budget_cap_usd, (int, float)), "budget_cap_usd must be a number")
    lv = dict(lib_versions) if lib_versions is not None else resolve_lib_versions()
    _validate_lib_versions(lv)
    grid = _validate_trainer_grid(trainer_grid)
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
        "trainer_grid": grid,
        "llm_pool": pool,
        # Principal directive + CTO #265: credential SOURCE only (never the value),
        # and the commit that fixed the hypotheses. Always present; the preflight
        # requires both to be non-null for a real sweep.
        "llm_key_source": dict(llm_key_source) if llm_key_source is not None else None,
        "preregistration": dict(preregistration) if preregistration is not None else None,
        "device": device,
        "llm_cache_dir": llm_cache_dir,
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
    stop_reason: str | None = None,
    cost_usd_at_stop: float | None = None,
) -> dict[str, Any]:
    """Return a completed copy of ``prov``; refuses a record without ``started_at``.

    ``unparseable_lines`` has no default (CTO #245 Q2): the caller must have
    scanned both JSONLs (:func:`scan_unparseable`) and passes both keys, even
    when the lists are empty. ``stop_reason`` (``"spend_stop"`` /
    ``"hard_kill"``) and ``cost_usd_at_stop`` record why and at what spend the
    sweep stopped early (CTO #283 / OWN-1); both ``None`` for a full run.
    """
    _require(bool(prov.get("started_at")), "provenance record has no started_at; refusing to finalize")
    missing = [k for k in REQUIRED_KEYS if k not in prov]
    _require(not missing, f"provenance record missing {missing}")
    _require(status in STATUSES, f"status must be one of {sorted(STATUSES)}, got {status!r}")
    _require(isinstance(budget_hit, bool), "budget_hit must be bool")
    _require((stop_reason is None) == (cost_usd_at_stop is None),
             "stop_reason and cost_usd_at_stop are set together")
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
        "stop_reason": stop_reason,
        "cost_usd_at_stop": float(cost_usd_at_stop) if cost_usd_at_stop is not None else None,
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
    A lifecycle record's counts come from its ``n_params_per_round``
    ``[backbone, n_params]`` pairs when present (QG C15), else from
    ``(backbone_used, n_params)``. Records whose ``record_type`` is
    ``"provenance"`` are ignored.
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
        pairs = r.get("n_params_per_round")
        if pairs is None:
            pairs = [(r.get("backbone_used"), r.get("n_params"))]
        for backbone, n in pairs:
            if n is not None:
                _add(params.setdefault(k, {}).setdefault("lifecycle", {}), str(backbone), n)
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
