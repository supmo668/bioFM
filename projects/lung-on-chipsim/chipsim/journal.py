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
resolved versions, platform — and now the resolved **seed**. The seed is read
from `configs/env.yaml:seed`, overridable by `$CHIPSIM_SEED`, and the record
names WHICH source won, because a bare number cannot tell a replay which of two
possible values was in force.

**That still does not close the PoC form, and this module does not claim to.**
The PoC form is specified over *scores*, and this build has none — there is no
model, head or scorer in the M0 slice, and no task in the build plan produces a
score. So the seed is recorded but nothing in the code path consumes it yet: the
record is necessary for the PoC replay form and still not sufficient for it. The
determinism control that IS executable today lives in
`tests/test_replay_determinism.py`, over the persisted ETL artifact, and states
that same limit at its head.

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
import re
import shutil
import socket
import stat
import sys
import tempfile
import uuid
from datetime import UTC, datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

__all__ = [
    "ConfigIntegrityError",
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

#: Bounds on the config walk. Generous for any real `configs/` tree and small
#: enough that a symlink diamond is refused in well under a second.
#: Record format version. Bumped when the manifest's SHAPE changes, so an old
#: record and a new one are distinguishable by inspection rather than by probing
#: for a key. r2.7 moved `environment.seeds` from a flat `{VAR: value}` map to
#: `{resolved, source, env}`; without this, both shapes verify clean against
#: their own digest and nothing says which is which — the same "must not look
#: alike" rule the seeds themselves follow. Inside the digest preimage for free.
RECORD_SCHEMA = 2

MAX_CONFIG_DIRS = 512
MAX_CONFIG_DEPTH = 32


def _recorded_argv(argv: list[str] | None) -> list[str]:
    """argv as recorded: ``argv[0]`` reduced to its basename, the rest verbatim.

    ``argv[0]`` arrives as an absolute interpreter or console-script path, so it
    carries the operator's directory layout — home directory, username, checkout
    location — into a record that is published alongside results. It buys
    nothing at replay: ``python``, ``platform`` and ``packages`` already identify
    the interpreter far more precisely than its path does. So it is pure
    disclosure, and only the basename is kept.

    ``argv[1:]`` is recorded VERBATIM and must stay that way. Those are the run's
    actual inputs; a path among them is replay-relevant, and trimming it would
    damage the record to no benefit. This is a disclosure trim, not a
    sanitizer — it does not make argv safe to trust, and nothing downstream
    should read it as though it had.
    """
    values = list(argv) if argv is not None else list(sys.argv)
    if not values:
        return values
    # `os.path.basename` returns "" for a path ending in a separator, which would
    # replace the record of what ran with nothing at all — strictly worse than the
    # disclosure being trimmed. Strip trailing separators first and fall back to
    # the original if there is genuinely no name to keep.
    head = values[0]
    name = os.path.basename(head.rstrip("/\\")) or head
    return [name, *values[1:]]


class JournalError(RuntimeError):
    """A run could not be opened — e.g. its run id is already taken."""


class ConfigIntegrityError(JournalError):
    """A config could not be snapshotted safely — it escapes the project root,
    is a hard link, or is not a regular file.

    A distinct type because callers must treat it differently from an ordinary
    journal outage: this is an operator-security event and must fail the run,
    never degrade to a warning. See `pipeline._journal_best_effort`.
    """


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


def _resolve_seed(project_root: Path) -> dict:
    """Resolve the run's seed and record WHICH source supplied it.

    Precedence: ``CHIPSIM_SEED`` (the operator's explicit override) beats
    ``configs/env.yaml:seed``. The record names the winning source, because a
    bare number cannot tell a replay which of two possible values was in force —
    and a replay that seeds from the wrong one reproduces *a* result and reports
    success, the same failure mode the config snapshot exists to close.

    An absent seed is recorded AS absent (``resolved: None``, ``source:
    "unset"``), never omitted: "unset" and "unrecorded" must not look alike.

    A non-integer seed RAISES rather than being recorded. A string cannot seed
    anything, so recording it would leave the record asserting a seed was in
    force when nothing could have used it.
    """
    raw_env = {name: os.environ.get(name) for name in SEED_ENV_VARS}
    resolved: int | None = None
    source = "unset"

    # `project_root` is REQUIRED, deliberately. An optional root made the easy
    # path for a future caller `{"resolved": None, "source": "unset"}` without
    # ever consulting the config — a positive false statement indistinguishable
    # from a genuinely absent seed, which is the confusion this module refuses.
    config_seed = None
    if True:
        # `.yml` counts as well as `.yaml` — `_config_sources` accepts both and
        # snapshots them, so a seed in `env.yml` would otherwise be recorded as
        # `source: "unset"` while the record's own config copy carries it: a
        # positive false statement, the class this module refuses everywhere.
        candidates = [
            project_root / "configs" / "env.yaml",
            project_root / "configs" / "env.yml",
        ]
        config_path = next((c for c in candidates if c.is_file()), candidates[0])
        if config_path.is_file():
            import yaml

            # The escape check belongs on the READ, not on one caller's loop
            # ordering. `start_run` happened to gate this file first;
            # `record_invocation` does not, so `panel-seal` would otherwise open
            # and parse a `configs/env.yaml` symlinked outside the root.
            # The SAME boundary as the snapshot loop. This previously passed
            # `project_root.resolve()` — the pre-E-3 bound — so `panel-seal`
            # would open and YAML-parse an in-project file the snapshot
            # boundary refuses, and record a seed sourced from it as
            # `config:env.yaml`.
            fd = _open_verified_config(
                config_path, Path(config_path.name), _configs_boundary(project_root)
            )
            try:
                raw = _read_all(fd)
            finally:
                os.close(fd)
            try:
                doc = yaml.safe_load(raw.decode("utf-8"))
            except (yaml.YAMLError, OSError, UnicodeDecodeError) as exc:
                # RAISE rather than fall through to `source: "unset"`. A config
                # that cannot be parsed may well carry a seed, so recording
                # "unset" would put a POSITIVE FALSE STATEMENT in the record —
                # worse than recording nothing, and the same class of silent
                # dishonesty as a snapshot claiming completeness it lacks.
                raise JournalError(
                    f"cannot resolve the seed: {config_path.name} could not be parsed "
                    f"({exc.__class__.__name__}). Refusing to record the seed as "
                    "unset when the config may define one."
                ) from exc
            if isinstance(doc, dict) and doc.get("seed") is not None:
                config_seed = doc["seed"]

    if config_seed is not None:
        resolved, source = _coerce_seed(config_seed, "configs/env.yaml:seed"), "config:env.yaml"

    # An exported-but-empty var reads as UNSET, by POSIX convention. Otherwise
    # `export CHIPSIM_SEED=$SEED` with SEED unset — an ordinary shell accident —
    # hard-fails every run and bricks `panel-seal`.
    env_seed = raw_env.get("CHIPSIM_SEED")
    if env_seed is not None and env_seed.strip() == "":
        env_seed = None
    if env_seed is not None:
        resolved, source = _coerce_seed(env_seed, "$CHIPSIM_SEED"), "env:CHIPSIM_SEED"

    return {"resolved": resolved, "source": source, "env": raw_env}


def _coerce_seed(value: object, origin: str) -> int:
    """A seed must be an integer. Anything else is refused, loudly."""
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise JournalError(
            f"seed from {origin} is a {type(value).__name__}, which cannot seed "
            "anything. Refusing to record a seed no replay could use. (The value "
            "is not echoed here: it is config-sourced data and this message is "
            "written durably.)"
        )
    # A plain decimal integer only. `int()` also accepts underscore separators, so
    # `1_0` would silently become 10 — a recorded seed that differs from the one a
    # human reads in the config is exactly the trust this record exists to carry.
    if isinstance(value, str) and not re.fullmatch(r"[+-]?[0-9]+", value.strip()):
        raise JournalError(
            f"seed from {origin} is not a plain decimal integer. Refusing to record "
            "a seed that does not read as the value it is. (The value is not echoed "
            "here: it is config-sourced data and this message is written durably.)"
        )
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise JournalError(
            f"seed from {origin} is not an integer. Refusing to record a seed no replay could use."
        ) from exc


def _environment(project_root: Path) -> dict:
    """Seed environment plus the coarse host identity.

    `user`/`host` are provenance breadcrumbs, NOT identity claims — see the module
    docstring. Anything able to write the record can write these fields, so they
    must never be read as evidence of who ran it.
    """
    seeds = _resolve_seed(project_root)
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


def _config_sources(source_dir: Path, root_real: Path) -> list[Path]:
    """Every config file a run could read, at any depth.

    `.yml` counts as well as `.yaml`, and subdirectories are walked: a config the
    run reads but the journal does not snapshot makes the manifest indistinguishable
    from a run where that file did not exist, and the replay test passes while
    replaying against something never recorded. Silent incompleteness is the one
    failure this module exists to prevent.

    **Symlinked directories are walked explicitly rather than left to `rglob`.**
    `rglob` does not recurse into them, so a `configs/linked -> /elsewhere` dir
    made every config beneath it invisible to the snapshot while an ordinary
    `open()` in the run still read it — a silent skip of exactly the kind above.
    A linked directory that resolves back inside the project is legitimate and is
    followed; one that escapes the root is refused loudly by the walk itself, before
    descending. Escaping *files* are refused by ``start_run``.
    Cycles are guarded per-branch, against the chain of ANCESTORS currently being
    walked — not against a global set of everything already seen. A global set
    looks equivalent and is not: two distinct logical paths may resolve to the
    same real directory (`configs/panels` and a `configs/linked -> panels`), and
    a global set would walk whichever sorts first and silently drop the other —
    reintroducing precisely the silent skip this function exists to prevent.
    Only a genuine loop revisits a directory that is its own ancestor.

    The walk is BOUNDED and overruns raise. Per-branch cycle detection stops a
    directory being its own ancestor, but it does not stop a *diamond*: N nested
    directories each linking twice to the level above enumerate 2^N distinct
    logical paths, all of them acyclic. Measured: 12 levels produced 8,178 files
    in 5 seconds, so a slightly deeper tree hangs the run and inflates the
    manifest with thousands of aliased duplicates. The bound is a loud refusal
    rather than a silent truncation, for the usual reason — a truncated snapshot
    is a record claiming completeness it does not have.
    """
    if not source_dir.is_dir():
        return []

    found: list[Path] = []
    budget = {"dirs": 0}

    def walk(directory: Path, ancestors: frozenset[Path]) -> None:
        budget["dirs"] += 1
        if budget["dirs"] > MAX_CONFIG_DIRS:
            raise JournalError(
                f"config tree under {source_dir} expands past {MAX_CONFIG_DIRS} "
                "directories — almost certainly a symlink diamond, which enumerates "
                "exponentially many aliased paths. Refusing rather than truncating: "
                "a partial snapshot would claim a completeness it does not have."
            )
        if len(ancestors) > MAX_CONFIG_DEPTH:
            raise JournalError(
                f"config tree under {source_dir} nests deeper than "
                f"{MAX_CONFIG_DEPTH} levels. Refusing rather than truncating."
            )
        try:
            real = directory.resolve()
        except OSError:
            real = directory
        if real in ancestors:
            return
        ancestors = ancestors | {real}
        try:
            entries = sorted(directory.iterdir())
        except OSError as exc:
            raise ConfigIntegrityError(
                f"config directory {directory.name!r} could not be listed "
                f"({exc.__class__.__name__}). Refusing: an unlistable directory "
                "may hold configs the record would silently omit."
            ) from exc
        for entry in entries:
            if entry.is_dir():
                # Refuse before descending: an escaping linked dir must raise,
                # never be quietly passed over.
                _refuse_escaping_config(entry, entry.relative_to(source_dir), root_real)
                # Descend into the LOGICAL path, deliberately — not the resolved
                # one. Walking the resolved directory collapses distinct aliases
                # (`configs/linked` and `configs/panels` for the same real dir)
                # into one relative path and drops a config from the snapshot,
                # which is the silent skip this walk exists to prevent.
                #
                # That means the directory check is NOT verify-then-use, unlike
                # the file check, and it does not need to be: nothing is read
                # from a directory. Every FILE found beneath is independently
                # re-verified against the root immediately before it is copied
                # (see `start_run`), so repointing this link after the check
                # cannot smuggle outside content into the record — the file gate
                # is the one that carries that guarantee.
                walk(entry, ancestors)
            elif entry.is_file() and entry.suffix in {".yaml", ".yml"}:
                found.append(entry)
            elif entry.is_symlink() and entry.suffix in {".yaml", ".yml"}:
                # A DANGLING config link. `is_dir()` and `is_file()` both follow
                # the link and both return False, so without this branch the
                # entry fell off the end of the loop and was passed over in
                # silence — inside a walk whose whole premise is that nothing is.
                # A run reading it would fail; a run recording it as absent would
                # be indistinguishable from one where it never existed.
                rel = entry.relative_to(source_dir).as_posix()
                # Distinguish "target missing" from "target exists but is not a
                # regular file". Both used to report a broken link, so an
                # operator reading the refusal during a possible exfiltration
                # attempt was sent to fix the wrong thing — a `configs/x.yaml`
                # pointing at `/dev/null` or a FIFO is not dangling.
                if not entry.exists():
                    raise ConfigIntegrityError(
                        f"config {rel!r} is a broken symlink — it names a config "
                        "that does not exist. Refusing rather than passing over it "
                        "in silence."
                    )
                raise ConfigIntegrityError(
                    f"config {rel!r} is a symlink to something that is not a "
                    "regular file. Refusing to snapshot it: reading a fifo or a "
                    "device is not a config read, and passing over it would leave "
                    "the record claiming a complete snapshot it does not have."
                )
            elif entry.suffix in {".yaml", ".yml"}:
                # ANYTHING ELSE named like a config: a FIFO, a unix socket, a
                # device node. `is_dir()`, `is_file()` and `is_symlink()` are all
                # False for these, so the entry fell off the end of the loop and
                # was skipped IN SILENCE — the one failure this walk exists to
                # prevent, occurring inside the walk itself.
                raise ConfigIntegrityError(
                    f"config {entry.relative_to(source_dir).as_posix()!r} is neither "
                    "a regular file nor a directory. Refusing to snapshot it rather "
                    "than passing over it in silence."
                )

    walk(source_dir, frozenset())
    return sorted(found)


def _configs_boundary(project_root: Path) -> Path:
    """The ONE boundary every reader of `configs/` must use — E-3.

    Two halves, and each alone is a regression in the other's direction:

      (a) entries must resolve under `configs/` — tighter than the old
          project-root bound, which admitted a config symlinked at anything else
          inside the repository;
      (b) `configs/` must itself resolve STRICTLY INSIDE the project root —
          otherwise (a) silently loosens: `ln -s /etc configs` makes every entry
          resolve under the bound computed from it, admitting a whole directory.

    **Strictly inside, not "inside or equal".** An earlier form allowed
    `configs_real == root_real`, which exempted `ln -s . configs` — a plausible
    "flatten the layout" accident — and thereby restored the exact pre-E-3 bound
    half (a) was written to tighten: the snapshot would walk the project root,
    including `.venv/`, `data/` and `journal/`, and copy every `*.y[a]ml` in the
    tree into a published record. `configs/` resolving TO the root is never
    legitimate. The equality case reads natural because it was borrowed from
    `_refuse_escaping_config`, where it IS meaningful; here it is only ever
    satisfied by the pathological self-link.

    Factored into one function because it had drifted: the snapshot loop used the
    tightened bound while `_resolve_seed` still passed `project_root.resolve()`,
    so `panel-seal` would open and YAML-parse an in-project file the snapshot
    boundary declares out of bounds. Two boundaries for one directory in one
    module is the condition under which one of them stops being maintained.
    """
    project_root = Path(project_root)
    root_real = project_root.resolve()
    configs_real = (project_root / "configs").resolve()
    if root_real not in configs_real.parents:
        raise ConfigIntegrityError(
            f"refusing to read configs: {project_root / 'configs'} resolves to "
            f"{configs_real}, which is not strictly inside the project root "
            f"{root_real}. A `configs/` that links out of the tree — or back to the "
            "root itself — would let every entry beneath it pass a bound computed "
            "from it."
        )
    return configs_real


def _refuse_escaping_config(config: Path, relative: Path, root_real: Path) -> Path:
    """Refuse a config whose REAL path lies outside `root_real`.

    `root_real` is the CONFIG boundary — `configs/` — not the project root, and
    the message used to say "outside the project root {root_real}" regardless.
    Since E-3 tightened the bound, that rendered as "outside the project root
    /…/proj/configs", telling an operator that `configs/` is the project root.
    The wording was accurate when the bound was the project root and was not
    updated when the bound moved. An error message is the only thing a person has
    at the moment something is refused; one that misnames the boundary it just
    enforced sends them looking in the wrong place.

    `shutil.copy2` follows symlinks, so without this a config symlinked at a
    target outside the project has its *content* copied into the record and
    hashed into the manifest. The journal is published alongside results, so
    that is an exfiltration path: anything readable by the process can be
    linked into `configs/` and carried out inside a record that looks routine.

    **This raises rather than skipping, deliberately.** Silently omitting the
    file would be the worse failure: the record would then assert a complete
    snapshot it does not have, and a replay against it would be
    indistinguishable from a replay against a run where the config never
    existed — the exact silent incompleteness `_config_sources` exists to
    prevent. A run that cannot be recorded honestly must not proceed.

    The message names the offending path but never its contents, so the refusal
    does not itself leak what the link pointed at.

    Returns the RESOLVED path. Use `_open_verified_config` for files — this
    function alone is a PATH check, and a path is not an object.
    """
    try:
        real = config.resolve()
    except OSError as exc:  # pragma: no cover - broken link, unreadable parent
        raise JournalError(
            f"config {relative.as_posix()!r} could not be resolved: {exc}. "
            "Refusing to snapshot a config whose real path cannot be established."
        ) from exc

    if real == root_real or root_real in real.parents:
        return real

    raise ConfigIntegrityError(
        f"config {relative.as_posix()!r} resolves to {real}, which is outside the "
        f"permitted config boundary {root_real}. Refusing to snapshot it: copying "
        "would follow the link and hash outside content into this record, and "
        "skipping it would leave the record claiming a complete snapshot it does "
        "not have. Remove the link or move the file inside the boundary."
    )


def _read_all(fd: int) -> bytes:
    """Read a descriptor to EOF. Copies bytes from the OBJECT already verified,
    so the config's name is never resolved a second time."""
    chunks: list[bytes] = []
    while True:
        block = os.read(fd, 1 << 20)
        if not block:
            return b"".join(chunks)
        chunks.append(block)


def _open_verified_config(config: Path, relative: Path, root_real: Path) -> int:
    """Open a config for snapshotting, verified as an OBJECT rather than a name.

    Three checks a path comparison cannot make:

    1. **In-root** — the resolved path must lie under the project root
       (`_refuse_escaping_config`). Closes the symlink escape.
    2. **Not a hard link** — ``st_nlink`` must be 1. ``Path.resolve()`` has
       nothing to resolve for a hard link: a second directory entry for an
       outside inode reports its own in-``configs/`` path and passes every path
       check. Without this, ``ln`` (no ``-s``) reaches the same exfiltration the
       symlink guard closes, with identical preconditions.
    3. **A regular file** — a fifo or device under ``configs/`` would otherwise
       be opened and read.

    The file is opened ``O_NOFOLLOW`` on the ALREADY-RESOLVED path and the caller
    copies from the returned descriptor, so the name is never resolved twice.

    **Residual limit, stated rather than glossed.** This narrows the
    check-to-use window; it does not eliminate it. The resolved path could still
    be replaced by another regular in-root file between ``resolve()`` and
    ``open()``, and only an ``openat`` walk holding a descriptor for every path
    component would close that. On a single-operator PoC that is out of
    proportion; the honest claim is "narrowed and type-checked", not "closed".
    An earlier version of this code claimed the window was shut when it was not,
    which is worse than the gap — a false assurance stops the next reader
    looking.
    """
    real = _refuse_escaping_config(config, relative, root_real)
    try:
        # O_NONBLOCK so `fstat` can run BEFORE any blocking wait. Without it,
        # opening a FIFO under `configs/` blocks indefinitely waiting for a
        # writer, so the S_ISREG guard below — the check that exists to reject
        # exactly that file — is never reached. A guard placed after a blocking
        # call is not a guard; the process simply hangs instead of refusing.
        fd = os.open(
            real,
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0),
        )
    except OSError as exc:
        raise JournalError(
            f"config {relative.as_posix()!r} could not be opened for snapshotting: "
            f"{exc.__class__.__name__}. Refusing to record a config it cannot read."
        ) from exc

    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            raise ConfigIntegrityError(
                f"config {relative.as_posix()!r} is not a regular file. Refusing to "
                "read it into the record."
            )
        if info.st_nlink > 1:
            raise ConfigIntegrityError(
                f"config {relative.as_posix()!r} has {info.st_nlink} hard links, so "
                "its content may live outside the project root — a hard link is "
                "invisible to a path check. Refusing to snapshot it: copying would "
                "hash outside content into this published record. Replace the link "
                "with a copy."
            )
    except BaseException:
        os.close(fd)
        raise
    return fd


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

        # E-3: the snapshot boundary is `configs/`, not the project root.
        #
        # The bound has TWO halves and they must land together, because each
        # alone is a regression in the other's direction:
        #
        #   (a) entries must resolve under `configs/` — tighter than the old
        #       project-root bound, which admitted a config symlinked to
        #       anything else inside the repository;
        #   (b) `configs/` must ITSELF resolve inside the project root —
        #       otherwise (a) silently LOOSENS the one case the old bound caught:
        #       `ln -s /etc configs` makes every entry resolve under
        #       `configs_real` and pass, admitting a whole directory rather than
        #       a single file.
        #
        # Half (a) came from the ruling; half (b) from a peer agent that spotted
        # the regression before either of us shipped it. Reasoning about the two
        # halves separately is how a boundary ends up looking obviously correct
        # and not being.
        configs_real = _configs_boundary(project_root)

        for config in _config_sources(source_dir, configs_real):
            relative = config.relative_to(source_dir)
            fd = _open_verified_config(config, relative, configs_real)
            try:
                payload = _read_all(fd)
            finally:
                os.close(fd)
            target = snapshot_dir / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
            digests[relative.as_posix()] = hashlib.sha256(payload).hexdigest()

        manifest = {
            "record_type": "run",
            "record_schema": RECORD_SCHEMA,
            "run_id": run_id,
            "command": command,
            "start": datetime.now(UTC).isoformat(),
            "argv": _recorded_argv(argv),
            "python": sys.version,
            "platform": platform.platform(),
            "packages": _package_versions(),
            "configs": digests,
            "environment": _environment(project_root),
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
        # A snapshot directory has NO legitimate reason to contain a symlink —
        # `start_run` only ever writes plain files into it. So refuse links
        # outright rather than trying to follow them safely.
        #
        # This previously used `rglob`, which is the exact bug fixed on the write
        # path: `rglob` does not descend into symlinked directories, so files
        # planted under `journal/<run>/configs/more -> /elsewhere/` were invisible
        # to this extra-file check and a tampered snapshot verified clean. The
        # write-path reasoning was not carried to the read path.
        present: set[str] = set()

        def _scan(directory: Path) -> None:
            for entry in sorted(directory.iterdir()):
                if entry.is_symlink():
                    raise ManifestVerificationError(
                        f"{run_dir}: config snapshot holds a symlink "
                        f"{entry.relative_to(snapshot_dir).as_posix()!r}. The "
                        "snapshot is written as plain files only, so this was "
                        "added after the fact."
                    )
                if entry.is_dir():
                    _scan(entry)
                elif entry.is_file():
                    present.add(entry.relative_to(snapshot_dir).as_posix())

        _scan(snapshot_dir)
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
        "argv": _recorded_argv(argv),
        "environment": _environment(project_root),
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
