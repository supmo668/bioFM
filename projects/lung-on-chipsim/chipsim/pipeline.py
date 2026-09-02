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
    JournalError,
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


def _cmd_panel_seal(ns) -> int:
    """Seal a ratified barrier panel — build-plan T7a.

    *** THIS IS A HUMAN COMMAND. *** Global Constraint (4) reserves it to a human,
    so an agent must never invoke it against the live configs/barrier_panel.yaml.
    Agents build and test it against fixtures only.

    That constraint is a stated rule with no technical force: the digest is
    unkeyed over public content, so running this proves the file has not changed
    since — never who ran it.
    """
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
            "HUMAN ONLY (T8) — writes a tamper-evident digest over a ratified panel. "
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
            "compute it. Global Constraint (4) reserves this command to a human; "
            "that is a stated rule with no technical enforcement."
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
                            "argv": list(sys.argv),
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
    run_dir = _journal_best_effort(
        lambda: start_run(ns.command, root, argv=argv_recorded),
        root=root,
        what=f"start_run:{ns.command}",
    )
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
