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
import sys
from pathlib import Path

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


def main(argv=None) -> int:
    ns = build_parser().parse_args(argv)
    return _HANDLERS[ns.command](ns)


if __name__ == "__main__":
    raise SystemExit(main())
