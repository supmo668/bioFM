"""Append-only run journal — build-plan S12, A&D §4.4a.

A&D §4.4 lists `journal/` in the repository tree and §5 requires a **replay test**:
*"re-run any kept diff from journal + seed and reproduce the trajectory exactly."*
The original record spec — *"diff, seeds, scores, veto state"* — **named no
configuration**, and the two are incompatible. A replay reading only diff + seed
picks up whatever `configs/` holds **at replay time**, reproduces *a* trajectory,
and reports success. The control could never fail for the reason it exists.

So a run record carries a **copy of every config file used** — copies, never
references. A config edited tomorrow must not change what yesterday's run says it
used. That is the whole requirement in one sentence.

It bites hardest where `pyarrow` and `rdkit` are `==`-pinned: parquet bytes are
sha256'd and rdkit computes the canonical InChIKey every join and the sealed
allocation key on, so a record omitting resolved versions cannot show that two runs
were the same computation.

*** WHAT THIS DETECTS, AND WHAT IT DOES NOT ***

DETECTS: modification of a run record after the fact. Change the manifest and
`read_manifest` raises.

DOES **NOT** establish who wrote it. The manifest digest is UNKEYED over content
the writer controls, so anything able to write a record can compute its digest.
This is tamper-EVIDENCE, the same limit as the panel seal (Global Constraint (4)).
No module, docstring or CLI text may describe the journal as authenticating anyone
— detection is not attestation. Giving it real force requires signing
(minisign/age/GPG with a pinned public key); that trade is with the principal.

**A dirty tree is RECORDED, never hidden or refused.** A run from a dirty tree is
not reproducible from its commit alone; the honest response is to say so in the
record, the same posture as `unknown` in the P-gp label, where the third state
survives into the schema rather than being rounded to a convenient answer.
"""

from __future__ import annotations

import getpass
import hashlib
import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import uuid
from datetime import UTC, datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

__all__ = [
    "JournalError",
    "ManifestVerificationError",
    "finish_run",
    "manifest_digest",
    "read_manifest",
    "record_invocation",
    "start_run",
]

#: The manifest field holding the digest. Excluded from its own preimage.
DIGEST_KEY = "manifest_sha256"

#: Packages whose version changes the OUTPUT, not merely the runtime. `pyarrow`
#: and `rdkit` are `==`-pinned for exactly this reason (pyproject / defect 27); the
#: rest are recorded because they move numbers.
OUTPUT_DETERMINING_PACKAGES = ("pyarrow", "rdkit", "pandas", "numpy", "PyYAML")

#: Seed-bearing environment variables. Recorded when set; recorded as absent when
#: not, because "unset" and "unrecorded" must not look the same at replay.
SEED_ENV_VARS = ("CHIPSIM_SEED", "PYTHONHASHSEED", "SOURCE_DATE_EPOCH")


class JournalError(RuntimeError):
    """A run could not be opened — e.g. its run id is already taken."""


class ManifestVerificationError(JournalError):
    """A manifest is missing its digest, or does not match it."""


# --------------------------------------------------------------------------
# digest
# --------------------------------------------------------------------------


def manifest_digest(manifest: dict) -> str:
    """sha256 over the canonically-serialized manifest.

    The digest field itself is excluded — hashing it would make the digest depend
    on its own value. Canonical form: keys sorted, compact separators, UTF-8, so
    a reformat does not trip a digest that nothing meaningful changed. Teaching a
    reader to ignore mismatches is the way a tamper-evidence scheme dies.
    """
    preimage = {k: manifest[k] for k in manifest if k != DIGEST_KEY}
    blob = json.dumps(preimage, separators=(",", ":"), sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------
# environment capture
# --------------------------------------------------------------------------


def _git_state(project_root: Path) -> dict:
    """Commit, dirty flag, and the dirty file list.

    Every failure mode is recorded rather than raised: a run outside a git
    checkout is unusual, not illegitimate, and refusing to journal it would mean
    the least reproducible runs are the ones with no record at all.
    """
    def _git(*args: str) -> str | None:
        try:
            out = subprocess.run(
                ["git", *args],
                cwd=project_root,
                capture_output=True,
                text=True,
                check=False,
                timeout=10,
            )
        except (OSError, subprocess.SubprocessError):
            return None
        return out.stdout.strip() if out.returncode == 0 else None

    commit = _git("rev-parse", "HEAD")
    status = _git("status", "--porcelain")
    if status is None:
        return {"commit": commit, "dirty": None, "dirty_files": [], "available": False}

    dirty_files = sorted(line[3:] for line in status.splitlines() if line.strip())
    return {
        "commit": commit,
        "dirty": bool(dirty_files),
        "dirty_files": dirty_files,
        "available": True,
    }


def _package_versions() -> dict:
    """Resolved versions of the output-determining packages.

    A package that is absent is recorded as ``None`` rather than omitted: at
    replay, "not installed" and "we forgot to look" must not be the same value.
    """
    resolved: dict[str, str | None] = {}
    for pkg in OUTPUT_DETERMINING_PACKAGES:
        try:
            resolved[pkg] = version(pkg)
        except PackageNotFoundError:
            resolved[pkg] = None
    return resolved


def _environment() -> dict:
    """Seed environment plus the coarse host identity.

    `user`/`host` are provenance breadcrumbs, NOT identity claims — see the module
    docstring. Anything able to write the record can write these fields, so they
    must never be read as evidence of who ran it.
    """
    seeds = {name: os.environ.get(name) for name in SEED_ENV_VARS}
    try:
        user = getpass.getuser()
    except Exception:  # noqa: BLE001 - a container with no passwd entry is fine
        user = None
    return {
        "seeds": seeds,
        "user": user,
        "host": socket.gethostname(),
        "cwd": str(Path.cwd()),
    }


# --------------------------------------------------------------------------
# runs
# --------------------------------------------------------------------------


def _journal_dir(project_root: Path) -> Path:
    return Path(project_root) / "journal"


def _new_run_id() -> str:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return f"{stamp}-{uuid.uuid4().hex[:8]}"


def start_run(
    command: str,
    project_root: Path,
    *,
    run_id: str | None = None,
    argv: list[str] | None = None,
) -> Path:
    """Open a run. Called BEFORE any work.

    Creates ``journal/<run_id>/``, **copies** every ``configs/*.yaml`` into
    ``journal/<run_id>/configs/``, and writes ``manifest.json``.

    Raises `JournalError` if the run directory already exists. Overwriting would
    let a second run silently inherit the first one's identity, which is the one
    thing an append-only journal must not permit.

    Returns the run directory.
    """
    project_root = Path(project_root)
    run_id = run_id or _new_run_id()
    run_dir = _journal_dir(project_root) / run_id

    if run_dir.exists():
        raise JournalError(
            f"run id {run_id!r} already exists at {run_dir} — refusing to overwrite. "
            "The journal is append-only; a reused id would erase a prior record."
        )

    # mkdir(exist_ok=False) is the actual guard: the check above is for the
    # message, this closes the race between the check and the create.
    try:
        run_dir.mkdir(parents=True, exist_ok=False)
    except FileExistsError as exc:
        raise JournalError(f"run id {run_id!r} already exists at {run_dir}") from exc

    snapshot_dir = run_dir / "configs"
    snapshot_dir.mkdir()
    digests: dict[str, str] = {}
    source_dir = project_root / "configs"
    if source_dir.is_dir():
        for config in sorted(source_dir.glob("*.yaml")):
            target = snapshot_dir / config.name
            shutil.copy2(config, target)
            digests[config.name] = hashlib.sha256(target.read_bytes()).hexdigest()

    manifest = {
        "record_type": "run",
        "run_id": run_id,
        "command": command,
        "start": datetime.now(UTC).isoformat(),
        "argv": list(argv) if argv is not None else list(sys.argv),
        "git": _git_state(project_root),
        "python": sys.version,
        "platform": platform.platform(),
        "packages": _package_versions(),
        "configs": digests,
        "environment": _environment(),
    }
    manifest[DIGEST_KEY] = manifest_digest(manifest)
    (run_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    )
    return run_dir


def read_manifest(run_dir: Path) -> dict:
    """Verify ``manifest_sha256`` and return the manifest.

    REFUSES a manifest carrying no digest — absence is not consent, the same rule
    `barrier_panel_edges` applies to a missing `ratified` key. Loading an
    unverified record would make the digest optional in practice, which is the
    same as not having one.
    """
    path = Path(run_dir) / "manifest.json"
    if not path.is_file():
        raise ManifestVerificationError(f"no manifest.json under {run_dir}")

    try:
        manifest = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise ManifestVerificationError(f"{path} is not valid JSON: {exc}") from exc

    if not isinstance(manifest, dict):
        raise ManifestVerificationError(
            f"{path} did not parse to a mapping (got {type(manifest).__name__})"
        )

    recorded = manifest.get(DIGEST_KEY)
    if not recorded:
        raise ManifestVerificationError(
            f"{path} carries no {DIGEST_KEY} — refusing to load an unverified record."
        )

    actual = manifest_digest(manifest)
    if actual != recorded:
        raise ManifestVerificationError(
            f"{path} does not match its {DIGEST_KEY}: recorded {recorded}, computed "
            f"{actual}. The record was modified after it was written."
        )
    return manifest


def finish_run(run_dir: Path, *, status: str, detail: str | None = None) -> Path:
    """Write ``outcome.json`` — **last**, after every other artifact.

    Ordering is the whole point: a crashed run leaves no outcome, so absence is
    unambiguous and a crash can never read as a silent success. The outcome is
    deliberately NOT covered by the manifest digest — the manifest is sealed at
    run start, before the outcome exists.
    """
    run_dir = Path(run_dir)
    if not (run_dir / "manifest.json").is_file():
        raise JournalError(
            f"refusing to write an outcome for {run_dir}: it has no manifest. An "
            "outcome must never be the only record of a run."
        )
    outcome = {
        "status": status,
        "detail": detail,
        "end": datetime.now(UTC).isoformat(),
    }
    path = run_dir / "outcome.json"
    path.write_text(json.dumps(outcome, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    return path


# --------------------------------------------------------------------------
# invocations
# --------------------------------------------------------------------------


def record_invocation(
    command: str,
    project_root: Path,
    *,
    argv: list[str] | None = None,
) -> Path:
    """Journal a non-ETL invocation — record type ``invocation``, **no digest**.

    `panel-seal` is journalled here rather than as a run. Recording every
    invocation is what makes a Global Constraint (4) violation *detectable*: the
    constraint reserves sealing to a human and has no technical force, so the
    trail of who-ran-what-when is the only mechanical support it gets.

    The record carries argv, environment and timestamp, and **no digest field**.
    That is deliberate. A digest here would look like an attestation of the seal,
    and it would not be one — this record is an audit trail, **never** the
    attestation. It does not establish who ran the command.
    """
    project_root = Path(project_root)
    invocation_dir = _journal_dir(project_root) / "invocations"
    invocation_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    path = invocation_dir / f"{stamp}-{command}.json"

    record = {
        "record_type": "invocation",
        "command": command,
        "start": datetime.now(UTC).isoformat(),
        "argv": list(argv) if argv is not None else list(sys.argv),
        "environment": _environment(),
    }
    path.write_text(json.dumps(record, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    return path
