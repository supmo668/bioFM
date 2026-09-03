"""ETL pipeline CLI — the entrypoints the T16 n8n workflow export names.

Five subcommands, one per workflow node:

    fetch -> hash-verify -> parse -> provenance-tests -> write

T16's done-condition requires that **each node names a CLI entrypoint that exists
in the installed package**. `SUBCOMMANDS` is the single source of truth for that:
the workflow JSON is validated against it, so a node naming a command that was
renamed or removed fails the test rather than failing at 3am in n8n.

**Not in slice 1:** provisioning n8n and executing the workflow end-to-end
(tracked as T16a, deferred). This module is exercised directly by tests.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

from chipsim.journal import (
    ConfigIntegrityError,
    JournalError,
    _recorded_argv,
    finish_run,
    record_invocation,
    source_root,
    start_run,
)

#: Node name -> subcommand. The workflow export is checked against these keys.
SUBCOMMANDS = (
    "fetch",
    "hash-verify",
    "parse",
    "provenance-tests",
    "write",
)

#: Subcommands that are NOT ETL stages and must never appear in the n8n workflow.
#: `panel-seal` (T7a) writes a tamper-evident digest over a ratified panel. Global
#: Constraint (4) reserves running it to a human — a STATED RULE the digest cannot
#: enforce — so it must not sit in an automated pipeline that could invoke it
#: unattended. Keeping it out of the workflow is one of the few places that rule
#: gets any mechanical support at all.
#:
#: Declared separately rather than folded into SUBCOMMANDS so the workflow-export
#: check keeps comparing against the ETL list exactly. Every registered subcommand
#: must appear in exactly one of these two tuples — see test_workflow_export.
NON_ETL_SUBCOMMANDS = ("panel-seal",)

MODULE_PATH = "chipsim.pipeline"


def _cmd_fetch(ns: argparse.Namespace) -> int:
    from chipsim.ingest.drugbank_snapshot import fetch_snapshot

    digests = fetch_snapshot(ns.dest, ns.commit)
    for name, digest in sorted(digests.items()):
        print(f"{digest}  {name}")
    return 0


def _cmd_hash_verify(ns: argparse.Namespace) -> int:
    from chipsim.ingest.drugbank_snapshot import verify_snapshot

    verified = verify_snapshot(ns.dest)
    print(f"verified {len(verified)} file(s) against the manifest")
    return 0


def _cmd_parse(ns: argparse.Namespace) -> int:
    from chipsim.harmonize.ids import add_canonical_identity, canonicalization_disagreements
    from chipsim.ingest.drugbank_snapshot import load_compounds, load_protein_edges

    compounds = add_canonical_identity(load_compounds(ns.raw_dir))
    edges = load_protein_edges(ns.raw_dir)
    disagreements = len(canonicalization_disagreements(compounds))
    print(
        f"compounds={len(compounds)} edges={len(edges)} "
        f"raw_vs_canonical_disagreements={disagreements}"
    )
    return 0


def _cmd_provenance_tests(ns: argparse.Namespace) -> int:
    """Run the provenance contract suite. Named `provenance-tests`, NOT
    `contract tests`: §4.5 sanctions *data*-contract tests, which arrive with the
    ChEMBL plan (defect 29)."""
    import subprocess

    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", str(ns.tests)], check=False
    ).returncode


def _cmd_write(ns: argparse.Namespace) -> int:
    from chipsim.harmonize.ids import add_canonical_identity
    from chipsim.ingest.drugbank_snapshot import load_compounds, write_compounds

    compounds = add_canonical_identity(load_compounds(ns.raw_dir))
    write_compounds(compounds, ns.out)
    print(f"wrote {ns.out}")
    return 0


def _stdin_is_interactive() -> bool:
    """True only if stdin is demonstrably a terminal.

    Fails CLOSED. A stdin that has been replaced or detached may not answer
    `isatty` at all; the honest reading of "cannot tell" is "not interactive",
    because the alternative silently restores the headless sealing path this
    gate exists to close.
    """
    try:
        return bool(sys.stdin.isatty())
    except Exception:  # noqa: BLE001 - unanswerable means not interactive
        return False


def _cmd_panel_seal(ns) -> int:
    """Seal a ratified barrier panel — build-plan T7a.

    *** THIS IS A HUMAN COMMAND. *** Global Constraint (4) reserves it to a human,
    so an agent must never invoke it against the live configs/barrier_panel.yaml.
    Agents build and test it against fixtures only.

    *** THE TTY GATE (r2.7 amendment) — WHAT IT IS WORTH, EXACTLY. ***

    Sealing requires an interactive terminal on stdin. A headless agent session
    has no TTY, so the path that until now yielded a perfectly valid live seal
    simply fails. This is Global Constraint (4)'s FIRST technical enforcement;
    before it, the constraint had none at all.

    Its value is bounded and the bound is the point: it converts an ACCIDENT
    into a DELIBERATE CIRCUMVENTION. It does not prove who ran the command, it
    does not make the seal an attestation, and an agent that deliberately
    allocates a pty defeats it entirely — which is neither hard nor exotic. The
    digest stays unkeyed over public content, so it DETECTS a later edit — the
    repo's sanctioned verb — and never says who ratified it. It does not certify
    an untouched file: anything able to write the panel can recompute the digest,
    and removing the seal line bypasses the check entirely (see pgp_label.py). Real signing with a human-held key is a v2
    decision, deferred. Do not let any wording here grow past that.
    """
    if not _stdin_is_interactive():
        print(
            "ERROR: refusing to seal — `panel-seal` requires an interactive "
            "terminal on stdin and none is attached.\n"
            "Sealing is a human action reserved by Global Constraint (4). This "
            "check makes the headless path fail instead of silently succeeding; "
            "it does NOT establish who is running the command, and it is not "
            "evidence that a human sealed anything.",
            file=sys.stderr,
        )
        return 2

    from chipsim.harmonize.pgp_label import seal_panel

    digest = seal_panel(ns.panel)
    print(f"sealed {ns.panel}\n{digest}")
    return 0


_HANDLERS = {
    "fetch": _cmd_fetch,
    "hash-verify": _cmd_hash_verify,
    "parse": _cmd_parse,
    "provenance-tests": _cmd_provenance_tests,
    "write": _cmd_write,
    "panel-seal": _cmd_panel_seal,
}


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog=f"python -m {MODULE_PATH}")
    sub = ap.add_subparsers(dest="command", required=True)

    p = sub.add_parser("fetch", help="download the pinned snapshot")
    p.add_argument("--dest", required=True, type=Path)
    p.add_argument("--commit", required=True)

    p = sub.add_parser("hash-verify", help="recompute sha256s against the manifest")
    p.add_argument("--dest", required=True, type=Path)

    p = sub.add_parser("parse", help="parse compounds + protein edges")
    p.add_argument("--raw-dir", required=True, type=Path, dest="raw_dir")

    p = sub.add_parser("provenance-tests", help="run the provenance contract suite")
    p.add_argument("--tests", default=Path("tests/test_provenance.py"), type=Path)

    p = sub.add_parser("write", help="persist the compound frame")
    p.add_argument("--raw-dir", required=True, type=Path, dest="raw_dir")
    p.add_argument("--out", required=True, type=Path)

    p = sub.add_parser(
        "panel-seal",
        help=(
            "HUMAN ONLY (T7a) — writes a tamper-evident digest over a ratified panel. "
            "This does not prove a human ran it."
        ),
        # `help=` only shows in the parent listing. Without `description=`, the
        # human who runs `chipsim panel-seal --help` at the moment of sealing —
        # the likeliest place to read it — sees nothing at all about what the
        # seal does or does not establish.
        description=(
            "Write ratified_panel_sha256 over a ratified barrier panel (T7a).\n\n"
            "WHAT THIS DOES: records a tamper-evident digest over the panel, its "
            "ratification fields and its filename, so a later edit is detected.\n\n"
            "WHAT THIS DOES NOT DO: prove a human ran it. The digest is unkeyed "
            "over public content, so anything able to write `ratified: true` can "
            "compute it.\n\n"
            "REQUIRES AN INTERACTIVE TERMINAL: this command refuses to run when "
            "stdin is not a TTY, so the headless path fails instead of quietly "
            "producing a seal. That makes an accidental agent seal into a "
            "deliberate circumvention — it does NOT establish that a human ran "
            "this, and allocating a pty defeats it. Global Constraint (4) "
            "reserves this command to a human; the TTY check is its only "
            "technical support and is not proof of authorship."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--panel", required=True, type=Path)

    return ap


def available_subcommands() -> tuple[str, ...]:
    """The subcommands actually registered on the parser.

    Derived from the parser rather than restated, so the T16 check cannot pass
    against a stale list.
    """
    parser = build_parser()
    actions = [a for a in parser._actions if isinstance(a, argparse._SubParsersAction)]
    return tuple(actions[0].choices) if actions else ()


def _journal_best_effort(action, *, root: Path | None = None, what: str = "record"):
    """Run a journal write, reporting failure without killing an ETL stage.

    A journal that hard-fails an ETL stage is a journal people switch off, and a
    switched-off journal records nothing at all. But stderr alone is not enough:
    under n8n or cron it is routinely discarded, and then nothing distinguishes a
    recorded run from an unrecorded one. So a failure ALSO drops a durable
    `UNRECORDED-<stamp>.json` marker in the journal.

    This is best-effort by design and is NOT used for `panel-seal`, which fails
    closed — see `main`.
    """
    try:
        return action()
    except ConfigIntegrityError:
        # NOT best-effort. A config that escapes the project root, a hard link, or
        # a non-regular file under `configs/` is an operator-SECURITY event, not
        # the transient journal outage this wrapper was written for. Swallowing it
        # ran the stage anyway and exited 0, so an attempted exfiltration and a
        # clean run were indistinguishable from the exit status — and under
        # n8n/cron, where stderr is discarded, the marker was the only trace.
        # The B1 ruling is "FAIL LOUDLY"; this is where loud has to mean non-zero.
        raise
    except Exception as exc:  # noqa: BLE001 - the journal must not break the stage
        print(f"WARNING: run journal unavailable ({what}): {exc}", file=sys.stderr)
        if root is not None:
            try:
                marker_dir = Path(root) / "journal"
                marker_dir.mkdir(parents=True, exist_ok=True)
                stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
                (marker_dir / f"UNRECORDED-{stamp}.json").write_text(
                    json.dumps(
                        {
                            "record_type": "unrecorded",
                            "what": what,
                            "error": f"{type(exc).__name__}: {exc}",
                            "argv": _recorded_argv(None),
                            "at": datetime.now(UTC).isoformat(),
                        },
                        indent=2,
                        sort_keys=True,
                    )
                    + "\n",
                    encoding="utf-8",
                )
            except Exception as marker_exc:  # noqa: BLE001
                # The journal root itself is unwritable. stderr already carried
                # the primary warning; say so too rather than failing the stage.
                print(
                    f"WARNING: could not write an UNRECORDED marker: {marker_exc}",
                    file=sys.stderr,
                )
        return None


def project_root() -> Path:
    """WHERE THE JOURNAL IS WRITTEN — the module directory (AM-4) by default,
    i.e. the parent of the installed `chipsim` package. Overridable with
    CHIPSIM_PROJECT_ROOT so a test or a container can journal somewhere other
    than the source tree.

    That override RELOCATES THE AUDIT TRAIL, so it is recorded inside every record
    (`environment.project_root_override`) and `panel-seal` fails closed if its
    invocation record cannot be written — otherwise one environment variable would
    silently divert the only mechanical support Global Constraint (4) has.

    It is a JOURNAL DESTINATION AND NOTHING ELSE. It does not select the tree git
    is read from — see `journal.source_root`, which is not overridable. It used to,
    and pointing this variable at a planted repository executed that repository's
    `core.fsmonitor` as the pipeline user.

    Treated as untrusted input, because under n8n/cron it arrives from workflow
    config. An override that does not name an existing absolute directory FAILS
    CLOSED rather than falling back: a silent fallback would write the trail into
    the source tree while the operator believes it was diverted, and the one thing
    an audit trail may not do is be somewhere other than where it says.
    """
    override = os.environ.get("CHIPSIM_PROJECT_ROOT")
    if not override:
        return source_root()

    candidate = Path(override)
    if not candidate.is_absolute():
        raise JournalError(
            f"CHIPSIM_PROJECT_ROOT={override!r} is not absolute. The journal "
            "destination must not depend on the working directory."
        )
    # resolve() AFTER the absolute check so symlinks and `..` cannot smuggle the
    # trail somewhere the literal value does not name.
    candidate = candidate.resolve()
    if not candidate.is_dir():
        raise JournalError(
            f"CHIPSIM_PROJECT_ROOT={override!r} is not an existing directory "
            f"(resolved to {candidate}). Refusing to journal to a path that "
            "does not exist rather than silently journalling elsewhere."
        )
    return candidate


def _normalize_exit(code) -> int:
    """A handler returning None means success; argparse/CLI convention is 0."""
    return 0 if code is None else int(code)


def main(argv=None) -> int:
    ns = build_parser().parse_args(argv)
    argv_recorded = list(sys.argv) if argv is None else ["chipsim", *argv]
    root = project_root()

    # `panel-seal` is journalled as an INVOCATION, not a run: argv, environment,
    # timestamp, no digest. Recording every invocation is what makes a Global
    # Constraint (4) violation detectable — the constraint reserves sealing to a
    # human and has no technical force, so this trail is the only mechanical
    # support it gets. The record is an audit trail, NEVER the attestation, and it
    # does not establish who ran the command.
    #
    # This branch FAILS CLOSED. Everywhere else the journal is best-effort, but a
    # seal written with no record of the attempt is precisely the case the trail
    # exists to make visible, so an unrecordable seal does not run at all.
    if ns.command in NON_ETL_SUBCOMMANDS:
        try:
            record_invocation(ns.command, root, argv=argv_recorded)
        except Exception as exc:  # noqa: BLE001 - refuse rather than seal unrecorded
            print(
                f"ERROR: refusing to run {ns.command!r}: its invocation could not be "
                f"journalled under {root}: {exc}",
                file=sys.stderr,
            )
            return 2
        return _normalize_exit(_HANDLERS[ns.command](ns))

    # ETL stages open a run BEFORE any work, so the config snapshot precedes the
    # computation it describes. The outcome is written LAST: a crashed stage
    # leaves no outcome.json and therefore cannot read as a silent success.
    try:
        run_dir = _journal_best_effort(
            lambda: start_run(ns.command, root, argv=argv_recorded),
            root=root,
            what=f"start_run:{ns.command}",
        )
    except ConfigIntegrityError as exc:
        # Fail the stage, loudly and non-zero, WITHOUT running it. A `configs/`
        # tree holding an escaping link, a hard link or a non-regular file is an
        # operator-security event; running the stage anyway and exiting 0 made an
        # attempted exfiltration indistinguishable from a clean run.
        print(f"ERROR: refusing to run {ns.command!r}: {exc}", file=sys.stderr)
        return 2
    try:
        code = _normalize_exit(_HANDLERS[ns.command](ns))
    except SystemExit as exc:
        # A handler exiting via sys.exit(0) succeeded; recording it as a crash
        # would make the journal contradict the process's own exit status.
        status = "ok" if exc.code in (0, None) else "failed"
        if run_dir is not None:
            _journal_best_effort(
                lambda s=status, e=exc: finish_run(
                    run_dir, status=s, detail=f"SystemExit: {e.code}"
                ),
                root=root,
                what="finish_run",
            )
        raise
    except BaseException as exc:
        # `exc` is bound as a lambda default: `except ... as exc` unbinds the name
        # when the block exits, so capturing it by closure would work only by
        # accident of call timing.
        if run_dir is not None:
            _journal_best_effort(
                lambda e=exc: finish_run(
                    run_dir, status="crashed", detail=f"{type(e).__name__}: {e}"
                ),
                root=root,
                what="finish_run",
            )
        raise
    if run_dir is not None:
        _journal_best_effort(
            lambda: finish_run(
                run_dir, status="ok" if code == 0 else "failed", detail=f"exit={code}"
            ),
            root=root,
            what="finish_run",
        )
    return code


if __name__ == "__main__":
    raise SystemExit(main())
