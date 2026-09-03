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

*** "REPLAY TEST" NAMES TWO TESTS. SAY WHICH. ***

Never write "the replay test" unqualified — see CONTEXT.md, where the term is
defined as carrying two meanings at two rungs:

  PoC form (v0+v1)  same config + same seed reproduces the same scores exactly.
  v3 form           re-run a kept diff from the journal + seed and reproduce the
                    trajectory exactly — a test OF THE AGENT EXPLORATION LOOP.

The quotation at the top of this docstring is the **v3 form**. The PoC has no
exploration loop, so it produces no kept diff and no veto state, and **cannot run
the v3 form at all. That absence is not a defect in the PoC** and this module is
not failing to deliver it.

What S12 delivers toward the **PoC form**: the environment half — configs,
resolved versions, platform. The remaining half is the resolved **seed**, which
this record does not yet carry; nothing in the codebase sets `CHIPSIM_SEED`, so
the seeds map is populated only if an operator happens to export one. Until seed
capture lands, an environment recorded here is necessary for the PoC replay form
and not sufficient for it.

Describing this module as closing either form would repeat the seal's own
corrected overclaim — a real mechanism described as doing more than it does.

(The honesty grep in tests/test_journal.py rejected an earlier draft of this
paragraph because it quoted the seal's overclaim verbatim as an example. The guard
cannot distinguish a cited claim from a made one, and tightening it to try would
weaken it — so the wording changed instead. Worth recording that the check fired on
its own author.)

*** WHAT THIS DETECTS, AND WHAT IT DOES NOT ***

DETECTS: modification of a run record after the fact. Change the manifest and
`read_manifest` raises.

DOES **NOT** establish who wrote it. The manifest digest is UNKEYED over content
the writer controls, so anything able to write a record can compute its digest.
This is tamper-EVIDENCE, the same limit as the panel seal (Global Constraint (4)).
No module, docstring or CLI text may describe the journal as authenticating anyone
— detection is not attestation. Giving it real force requires signing
(minisign/age/GPG with a pinned public key); that trade is with the principal.

*** NO GIT STATE. A RECORD CANNOT SHOW THE TREE WAS CLEAN WHEN IT RAN. ***

A&D §4.4a puts "a dirty tree is RECORDED, never hidden or refused" in bold, and
this module **no longer delivers it**. Say so rather than let a reader assume the
record covers it.

Capturing it meant running `git status` in a directory arriving from workflow
config — untrusted input — and `git status` executes `core.fsmonitor`. The
mitigations for that (pinned `-c` overrides, a scrubbed `GIT_*` environment, a
separate source-root so the probe could not be redirected) were real and worked,
but they were code that existed *only* because the journal shelled out at all. A
PoC run journal does not need to run git: deleting the sub-feature takes the
attack surface to zero, where hardening only reduced it, and removes the code
rather than adding more to review. (CTO ruling, dispatch #44.)

The partial substitute is the installed package version, recorded with the other
resolved versions — which says what code ran without asking a working tree. It is
strictly weaker: it cannot distinguish a clean checkout from a dirty one at the
same version, and nothing here claims otherwise.
"""

from __future__ import annotations

import getpass
import hashlib
import json
import os
import platform
import shutil
import socket
import sys
import tempfile
import uuid
from datetime import UTC, datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

__all__ = [
    "JournalError",
    "ManifestVerificationError",
    "finish_run",
    "manifest_digest",
    "outcome_digest",
    "read_manifest",
    "read_outcome",
    "record_invocation",
    "source_root",
    "start_run",
]

#: The manifest field holding the digest. Excluded from its own preimage.
DIGEST_KEY = "manifest_sha256"

#: The outcome's own digest field. The outcome cannot live under the manifest
#: digest, which is sealed at run start before any outcome exists.
OUTCOME_DIGEST_KEY = "outcome_sha256"

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


def source_root() -> Path:
    """The tree holding the `chipsim` package that is ACTUALLY RUNNING.

    A pure path computation — it starts no subprocess and reads no repository.
    It is the default journal DESTINATION, used by `pipeline.project_root()`
    when `CHIPSIM_PROJECT_ROOT` is unset.

    It is deliberately NOT overridable. It previously also selected the tree git
    state was read from, which made the relocation variable an
    arbitrary-execution sink; git state is no longer captured at all (CTO ruling,
    dispatch #44), so that sink is gone rather than guarded. The non-overridable
    property is kept regardless: an audit trail whose default location can be
    redirected by an environment variable is one an operator cannot reason about.
    """
    return Path(__file__).resolve().parent.parent


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
    # CHIPSIM_PROJECT_ROOT relocates the journal itself. Recorded explicitly:
    # a record that does not say where it was meant to live cannot show that the
    # trail was diverted. See pipeline.main, which fails CLOSED for panel-seal.
    override = os.environ.get("CHIPSIM_PROJECT_ROOT")
    try:
        user = getpass.getuser()
    except Exception:  # noqa: BLE001 - a container with no passwd entry is fine
        user = None
    return {
        "seeds": seeds,
        "project_root_override": override,
        # NOT an identity. getpass.getuser() reads $LOGNAME/$USER/$LNAME/$USERNAME
        # before any system source, so `USER=impostor` puts "impostor" here.
        # Named to say so in the record itself, not only in this comment: a reader
        # of journal/invocations/*.json sees the caveat, and a plain field called
        # `user` beside a Constraint-(4) trail is the seal's overclaim again in
        # data form.
        "user_claimed_by_env": user,
        "identity_basis": (
            "getpass.getuser(); settable via $USER — NOT authenticated, and not "
            "evidence of who ran this"
        ),
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


def _validate_run_id(run_id: str) -> str:
    """A run id must be ONE safe path component.

    Without this, an id containing `..` or a separator escapes `journal/` and the
    exists()/mkdir guard below then protects the traversed location rather than a
    journal record.
    """
    if not run_id or run_id in {".", ".."} or "/" in run_id or "\\" in run_id:
        raise JournalError(f"invalid run id {run_id!r}: must be a single path component")
    if Path(run_id).name != run_id:
        raise JournalError(f"invalid run id {run_id!r}: must be a single path component")
    return run_id


def _config_sources(source_dir: Path) -> list[Path]:
    """Every config file a run could read, at any depth.

    `.yml` counts as well as `.yaml`, and subdirectories are walked: a config the
    run reads but the journal does not snapshot makes the manifest indistinguishable
    from a run where that file did not exist, and the replay test passes while
    replaying against something never recorded. Silent incompleteness is the one
    failure this module exists to prevent.
    """
    if not source_dir.is_dir():
        return []
    return sorted(
        path
        for path in source_dir.rglob("*")
        if path.is_file() and path.suffix in {".yaml", ".yml"}
    )


def start_run(
    command: str,
    project_root: Path,
    *,
    run_id: str | None = None,
    argv: list[str] | None = None,
) -> Path:
    """Open a run. Called BEFORE any work.

    Creates ``journal/<run_id>/``, **copies** every ``configs/**/*.y[a]ml`` into
    ``journal/<run_id>/configs/``, and writes ``manifest.json``.

    Raises `JournalError` if the run directory already exists. Overwriting would
    let a second run silently inherit the first one's identity, which is the one
    thing an append-only journal must not permit.

    The record is assembled in a temporary directory and moved into place, so a
    run directory is **atomically complete-or-absent**. A crash mid-snapshot
    therefore leaves no record-shaped directory that is missing its manifest —
    such a directory would make every reader raise, and would permanently burn
    its run id against the guard above.

    Returns the run directory.
    """
    project_root = Path(project_root)
    # `is not None`, not truthiness: an explicitly-passed empty id is a caller
    # bug and must raise, not silently become a generated one.
    run_id = _validate_run_id(run_id) if run_id is not None else _new_run_id()
    journal = _journal_dir(project_root)
    run_dir = journal / run_id

    if run_dir.exists():
        raise JournalError(
            f"run id {run_id!r} already exists at {run_dir} — refusing to overwrite. "
            "The journal is append-only; a reused id would erase a prior record."
        )

    journal.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".staging-", dir=journal))
    try:
        snapshot_dir = staging / "configs"
        snapshot_dir.mkdir()
        digests: dict[str, str] = {}
        source_dir = project_root / "configs"
        for config in _config_sources(source_dir):
            relative = config.relative_to(source_dir)
            target = snapshot_dir / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(config, target)
            digests[relative.as_posix()] = hashlib.sha256(target.read_bytes()).hexdigest()

        manifest = {
            "record_type": "run",
            "run_id": run_id,
            "command": command,
            "start": datetime.now(UTC).isoformat(),
            "argv": list(argv) if argv is not None else list(sys.argv),
            "python": sys.version,
            "platform": platform.platform(),
            "packages": _package_versions(),
            "configs": digests,
            "environment": _environment(),
        }
        manifest[DIGEST_KEY] = manifest_digest(manifest)
        (staging / "manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        try:
            os.replace(staging, run_dir)
        except OSError as exc:
            raise JournalError(f"run id {run_id!r} already exists at {run_dir}") from exc
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return run_dir


def read_manifest(run_dir: Path, *, verify_configs: bool = True) -> dict:
    """Verify the record and return the manifest.

    Three checks, because the manifest digest alone covers only the third:

    1. **Identity** — ``run_id`` must equal the directory name. The digest covers
       the manifest's *contents*, not the record's *identity*, so without this an
       entire record can be copied to another id, or a good manifest dropped into
       a different run's directory, and the composite verifies.
    2. **Snapshot integrity** — every config copy is re-hashed against
       ``manifest["configs"]``, and an extra or missing snapshot file is an error.
       The snapshot is the entire point of this module; a digest map that nothing
       checks at read time is decorative.
    3. **Manifest integrity** — ``manifest_sha256`` over the manifest itself.

    REFUSES a manifest carrying no digest — absence is not consent, the same rule
    `barrier_panel_edges` applies to a missing `ratified` key. Loading an
    unverified record would make the digest optional in practice, which is the
    same as not having one.
    """
    run_dir = Path(run_dir)
    path = run_dir / "manifest.json"
    if not path.is_file():
        raise ManifestVerificationError(f"no manifest.json under {run_dir}")

    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
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

    if manifest.get("run_id") != run_dir.name:
        raise ManifestVerificationError(
            f"{path} records run_id {manifest.get('run_id')!r} but sits in directory "
            f"{run_dir.name!r}. The record was copied or relocated."
        )

    if verify_configs:
        _verify_config_snapshot(run_dir, manifest.get("configs") or {})

    return manifest


def _verify_config_snapshot(run_dir: Path, digests: dict) -> None:
    """Re-hash every snapshotted config against the manifest, both directions."""
    snapshot_dir = run_dir / "configs"
    for name, digest in sorted(digests.items()):
        target = snapshot_dir / name
        if not target.is_file():
            raise ManifestVerificationError(
                f"{run_dir}: config snapshot {name!r} is recorded but missing."
            )
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != digest:
            raise ManifestVerificationError(
                f"{run_dir}: config snapshot {name!r} does not match the manifest "
                f"(recorded {digest}, computed {actual}). The snapshot was modified."
            )
    if snapshot_dir.is_dir():
        present = {
            path.relative_to(snapshot_dir).as_posix()
            for path in snapshot_dir.rglob("*")
            if path.is_file()
        }
        extra = present - set(digests)
        if extra:
            raise ManifestVerificationError(
                f"{run_dir}: config snapshot holds unrecorded file(s) {sorted(extra)} "
                "— the snapshot was added to."
            )


def outcome_digest(outcome: dict) -> str:
    """sha256 over the outcome, excluding its own digest field."""
    preimage = {k: outcome[k] for k in outcome if k != OUTCOME_DIGEST_KEY}
    blob = json.dumps(preimage, separators=(",", ":"), sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def finish_run(run_dir: Path, *, status: str, detail: str | None = None) -> Path:
    """Write ``outcome.json`` — **last**, after every other artifact, and **once**.

    Ordering is half the point: an outcome never exists for work that has not
    finished, so no run can read as `ok` before it succeeded. Note the precise
    claim — **absence means "no completion was recorded"**, which covers a hard
    kill, a `finish_run` that itself failed, and a run still in progress. It does
    NOT mean "crashed": the pipeline writes an explicit `status="crashed"` outcome
    when it catches a failure. The weaker statement is the true one, and reading
    absence as a diagnosis is the mistake this wording now refuses to invite.

    **Exclusive creation is the other half.** Without it a crashed run could
    simply be stamped again as a success — abandoning, one function away, the
    append-only rule `start_run` enforces for run ids. A second outcome RAISES.

    The outcome cannot be covered by the manifest digest — the manifest is sealed
    at run start, before the outcome exists — so it carries **its own** digest and
    a copy of the manifest's. `read_outcome` verifies all three: the outcome's own
    digest, that the record's `run_id` matches the directory it was found in, and
    that its bound `manifest_sha256` equals the run's actual manifest. The middle
    check exists because a digest covers a record's contents and says nothing
    about its location, so a copied outcome verified clean without it.
    """
    run_dir = Path(run_dir)
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.is_file():
        raise JournalError(
            f"refusing to write an outcome for {run_dir}: it has no manifest. An "
            "outcome must never be the only record of a run."
        )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    outcome = {
        "record_type": "outcome",
        "run_id": manifest.get("run_id"),
        "manifest_sha256": manifest.get(DIGEST_KEY),
        "status": status,
        "detail": detail,
        "end": datetime.now(UTC).isoformat(),
    }
    outcome[OUTCOME_DIGEST_KEY] = outcome_digest(outcome)

    path = run_dir / "outcome.json"
    payload = json.dumps(outcome, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    try:
        with open(path, "x", encoding="utf-8") as handle:
            handle.write(payload)
    except FileExistsError as exc:
        raise JournalError(
            f"refusing to overwrite {path}: this run already has an outcome. A "
            "crashed run must not be restampable as a success."
        ) from exc
    return path


def read_outcome(run_dir: Path) -> dict | None:
    """Verify and return the outcome, or ``None`` if no completion was recorded.

    ``None`` means **no completion record exists** — the process died before
    finishing, `finish_run` itself failed, or the run is still going. It never
    means success; that distinction is why the outcome is written last. It is
    deliberately NOT read as "crashed": the pipeline writes an explicit
    ``status="crashed"`` outcome when it catches a failure, so absence is the
    weaker, three-way statement rather than a diagnosis.

    Three things are checked, and a record failing any of them is refused rather
    than returned:

    1. the digest is present (never load unverified — deleting a line must not
       be the bypass);
    2. the digest matches (the record was not edited after it was written);
    3. **the record belongs to THIS run** — an outcome names its own ``run_id``
       and it must equal the directory it was found in. Without this, an outcome
       copied from another run verified clean: a successful run's outcome could
       be dropped into a crashed run's directory and read back as ``ok``, with
       every digest intact, because the digest covers the record's contents and
       says nothing about where it lives. The write path already refuses to
       restamp a crash (``finish_run`` creates exclusively), but a ``cp`` is not
       a write to that run at all, so the read path has to carry its own check.
    4. the outcome's copy of ``manifest_sha256`` is **present**, the manifest
       **exists**, and the two **match** — all three unconditionally. Otherwise
       that field is inert decoration and a foreign outcome carrying a foreign
       manifest digest is accepted silently. Checking it only "if both are there"
       is not a weaker check, it is no check: deleting the manifest or dropping
       the field is exactly what a forger does, and it is cheaper than editing
       either.
    """
    run_dir = Path(run_dir)
    path = run_dir / "outcome.json"
    if not path.is_file():
        return None
    outcome = json.loads(path.read_text(encoding="utf-8"))
    recorded = outcome.get(OUTCOME_DIGEST_KEY)
    if not recorded:
        raise ManifestVerificationError(
            f"{path} carries no {OUTCOME_DIGEST_KEY} — refusing to load it unverified."
        )
    actual = outcome_digest(outcome)
    if actual != recorded:
        raise ManifestVerificationError(
            f"{path} does not match its {OUTCOME_DIGEST_KEY}: recorded {recorded}, "
            f"computed {actual}. The outcome was modified after it was written."
        )

    claimed = str(outcome.get("run_id") or "")
    if claimed != run_dir.name:
        raise ManifestVerificationError(
            f"{path} belongs to run {claimed!r} but was found in {run_dir.name!r}. "
            "An outcome verifies its own contents, not its location — a record "
            "copied from another run would otherwise read back as that run's result."
        )

    # UNCONDITIONAL. This check used to read `if bound and manifest_path.is_file()`,
    # which handed the forger two ways to opt out of it: drop `manifest_sha256`
    # from the outcome, or delete the manifest. A verification that can be skipped
    # by removing the thing it verifies is not a verification — and the outcome
    # digest is unkeyed, so recomputing it after either edit is one step. Both
    # absences are now failures, for the same reason check 1 refuses a record
    # carrying no digest rather than treating it as nothing to check.
    manifest_path = run_dir / "manifest.json"
    bound = str(outcome.get("manifest_sha256") or "")
    if not bound:
        raise ManifestVerificationError(
            f"{path} carries no manifest_sha256. `finish_run` never writes an "
            "outcome without one, so its absence means the record was edited — "
            "refusing to read it as this run's result."
        )
    if not manifest_path.is_file():
        raise ManifestVerificationError(
            f"{path} claims manifest digest {bound[:12]}… but {manifest_path} does "
            "not exist. An outcome must never be the only record of a run, and "
            "deleting the manifest must not be the way to skip the check that "
            "binds them."
        )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    computed = manifest_digest(manifest)
    if computed != bound:
        raise ManifestVerificationError(
            f"{path} is bound to manifest digest {bound[:12]}… but "
            f"{manifest_path} computes {computed[:12]}…. The "
            "outcome and the manifest describe different states."
        )

    return outcome


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
    trail of **what-was-attempted-when** is the only mechanical support it gets.
    Not *who* — nothing in this record establishes an identity, and the
    `user_claimed_by_env` field says so in its own name.

    The record carries argv, environment and timestamp, and **no digest field**.
    That is deliberate. A digest here would look like an attestation of the seal,
    and it would not be one — this record is an audit trail, **never** the
    attestation. It does not establish who ran the command.

    **Scope of an invocation record.** It records that the command was *entered*
    — not that it completed, and not what it produced. There is deliberately no
    completion record: a seal that failed halfway is still an invocation worth
    seeing. Read it as "this was attempted here, then", never as "this succeeded".
    """
    project_root = Path(project_root)
    invocation_dir = _journal_dir(project_root) / "invocations"
    invocation_dir.mkdir(parents=True, exist_ok=True)

    record = {
        "record_type": "invocation",
        "command": command,
        "start": datetime.now(UTC).isoformat(),
        "argv": list(argv) if argv is not None else list(sys.argv),
        "environment": _environment(),
    }
    payload = json.dumps(record, indent=2, sort_keys=True, ensure_ascii=False) + "\n"

    # Exclusive create, retried on collision: `write_text` would REPLACE a prior
    # audit record — the same append-only violation `start_run` refuses for run
    # ids. An audit trail that can quietly lose an entry is not one.
    for _ in range(8):
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
        path = invocation_dir / f"{stamp}-{command}.json"
        try:
            with open(path, "x", encoding="utf-8") as handle:
                handle.write(payload)
            return path
        except FileExistsError:
            continue
    raise JournalError(f"could not allocate an invocation record filename under {invocation_dir}")
