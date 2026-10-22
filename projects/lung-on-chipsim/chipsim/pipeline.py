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
#: PREDICATE 1 — "IS AN ETL STAGE": it reads an input and writes a derived artifact.
#: SAFE DIRECTION: **include**. Journalled as a run record and gated by the §16 approval prompt.
ETL_SUBCOMMANDS = (
    "fetch",
    "hash-verify",
    "parse",
    "provenance-tests",
    "write",
    # T13. ETL because it reads the snapshot and writes a derived artifact — NOT because it may be
    # automated. See NON_NODE_REASONS: it is deliberately excluded from the workflow.
    "adjudication-worksheet",
)

#: PREDICATE 2 — "MAY BE INVOKED UNATTENDED". The ONLY commands the exported n8n workflow may name.
#: SAFE DIRECTION: **exclude**. This is the opposite direction to the one above, which is precisely
#: why r2.34 forbids the two sharing a tuple: a command can be a legitimate ETL stage AND a thing no
#: unattended chain should ever start. Restored from the Stage 1 branch, where HEAD had collapsed
#: both predicates back into one tuple — the exact conflation r2.34 exists to prevent.
WORKFLOW_NODE_SUBCOMMANDS = (
    "fetch",
    "hash-verify",
    "parse",
    "provenance-tests",
    "write",
)

#: WHY each registered command is not a node — required for every one of them, because a reader who
#: sees only tuple membership cannot recover the reason, and the reasons are not the same.
NON_NODE_REASONS = {
    "panel-seal": (
        "Global Constraint 4 RESERVES running it to a human. Keeping it out of the exported "
        "workflow is the only mechanical support that rule gets: an unattended pipeline must not "
        "be able to invoke it."
    ),
    "adjudication-export": (
        "Publishes a HUMAN artifact — the adjudicated labels T14 produced. An unattended chain "
        "must not publish a verdict nobody gave."
    ),
    "adjudication-worksheet": (
        "REGENERATING MID-ADJUDICATION DESTROYS THE PREMISE OF A 60-90 MINUTE HUMAN TASK. It is a "
        "genuine ETL stage — it reads the snapshot and writes a derived artifact — and it is still "
        "the last thing an unattended chain should start. That combination is r2.34's whole point. "
        "Note the never-clobber rule (defect 22) would preserve filled verdicts anyway; that is a "
        "guard written for a DIFFERENT purpose, and defence by coincidence is not a classification."
    ),
    "theta-scaffold": (
        "Writes an EMPTY S13 template a human then fills. A scheduled re-emit is defect 22's "
        "failure mode exactly."
    ),
    "transport-prior-scaffold": (
        "The S14 counterpart, for the same reason."
    ),
    "theta-check": (
        "A read-only validator over a human-owned file, for a human checking their own work "
        "before the fit runs. There is nothing an automated stage can do with the verdict that a "
        "human has not finished writing their inputs."
    ),
    "transport-prior-check": (
        "The S14 counterpart of the same read-only validator."
    ),
    "reference-compounds-check": (
        "A read-only validator over the human-curated reference set, for the same reason."
    ),
    "sourcing-check": (
        "A read-only sourcing audit. It writes no artifact, so there is nothing for a workflow to "
        "run it FOR."
    ),
}

#: Retained as the former name of the ETL list. HEAD called this `SUBCOMMANDS` while it carried
#: BOTH predicates; the alias keeps that spelling working and the docstring above names which
#: predicate it now is. Nothing outside this module consumed it (measured at 4ebcad7).
SUBCOMMANDS = ETL_SUBCOMMANDS

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
NON_ETL_SUBCOMMANDS = (
    "panel-seal",
    # T14's publisher. Not an ETL stage: it republishes a human's verdicts, so it opens no run
    # record and is not gated by the §16 prompt.
    "adjudication-export",
    # S13/S14 scaffold emitters. They write an EMPTY template a human then fills, so
    # they are not ETL stages and must not sit in an automated pipeline: a scheduled
    # re-emit is exactly defect 22's failure mode. Both writers refuse to blank a
    # filled file on their own, so this exclusion is a second line, not the only one.
    "theta-scaffold",
    "transport-prior-scaffold",
    # Read-only validators over human-owned files, for a human checking their own work
    # before the fit runs. Never pipeline nodes: there is nothing an automated stage can
    # do with the verdict that a human has not finished writing their inputs.
    "theta-check",
    "transport-prior-check",
    "reference-compounds-check",
    "sourcing-check",
)

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


#: The word a human must type to seal. Named so the prompt and the comparison
#: cannot drift apart — they were two separate literals, and a prompt that asks
#: for one word while the check tests another is a lock with no key.
_SEAL_CONFIRMATION = "seal"

#: How long to wait for that word. A bare `readline()` waits FOREVER, which turns
#: an unattended invocation (a cron entry, a CI step with a pty, a wrapper that
#: forgot to close stdin) into a hung process holding the panel open rather than
#: a clean refusal. Timing out fails closed: no answer is not consent.
_SEAL_CONFIRM_TIMEOUT_S = 120.0


def _read_confirmation(timeout_s: float) -> str:
    """One line from stdin, or "" if it does not arrive in time.

    Returns "" on timeout, EOF, interrupt, or a read error — every non-answer
    collapses to the same not-confirmed value, so the caller has no branch in
    which an unanswered prompt can be mistaken for a typed one.
    """
    import select

    try:
        ready, _, _ = select.select([sys.stdin], [], [], timeout_s)
    except (OSError, ValueError, TypeError):
        # stdin has no pollable file descriptor — an in-memory buffer, or a test
        # double. All three exception types mean the same thing and all three do
        # occur: ValueError for a closed file, OSError (io.UnsupportedOperation)
        # for a StringIO, TypeError for an object with no `fileno` at ALL.
        # Catching only the first two left the third crashing the command with a
        # traceback at the moment a human was being asked to confirm.
        #
        # Read it directly. This is NOT a weakening: the unbounded wait the
        # timeout exists to prevent is a kernel read on a real fd, and an object
        # with no fd is not one. Failing closed here instead would refuse every
        # non-fd stdin while protecting against a block that cannot occur.
        return _readline_or_empty()
    if not ready:
        print(
            f"\nERROR: no confirmation within {timeout_s:.0f}s.",
            file=sys.stderr,
        )
        return ""
    return _readline_or_empty()


def _readline_or_empty() -> str:
    """Read one line, mapping every read failure to "" — i.e. to NOT CONFIRMED.

    ONE handler, called from both arms of `_read_confirmation`. It was written
    out twice, and the duplication was not cosmetic: a mutation making the
    interrupt path return "seal" — Ctrl-C at the prompt meaning CONSENT — was
    killed on one copy and survived on the other, because the test that covers
    this reaches only the non-selectable arm. Two copies of a fail-closed rule
    are two places it can independently stop being fail-closed, and a suite that
    exercises one of them reports full coverage of neither.
    """
    try:
        return sys.stdin.readline()
    except (OSError, KeyboardInterrupt):
        return ""


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
    an untouched file: anything able to write the panel can recompute the digest.

    (This paragraph used to end by calling deletion of the seal line a bypass.
    That was true when written and is now FALSE: `load_ratified_panel`
    refuses a ratified panel carrying no seal, so deletion is a refusal, not a
    bypass. Left visible rather than quietly deleted because a stale caveat that
    UNDERSTATES a protection is still a false statement about the system, and the
    next reader would have had no way to tell which half to believe.)

    Real signing with a human-held key is a v2 decision, deferred. Do not let any
    wording here grow past that.
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

    # E-4: a confirmation READ, not merely a TTY check.
    #
    # `isatty()` proves a terminal is attached. It does not prove anyone is at it
    # — a pty allocated by a wrapper, a CI runner with a pseudo-terminal, or a
    # session left open all satisfy it while nobody is present. Requiring an
    # actual line from stdin is what makes the act deliberate, and deliberateness
    # is the exact property the seal is meant to assert.
    #
    # One keystroke is proportionate. It is NOT authentication and nothing here
    # may be described as such: whoever types it is unidentified, and an agent
    # that allocates a pty can also write to it. It raises the floor from
    # "accidentally reachable" to "deliberately circumvented" — the same bound as
    # the TTY gate, for the same reason.
    # The prompt goes to STDERR, not stdout. On stdout, `chipsim panel-seal >
    # log.txt` swallows the question while the command sits waiting on a read the
    # human cannot see they owe it — which reads as a hang, and a hang is exactly
    # the thing someone works around by piping `yes seal` into it.
    print(
        f"About to seal {ns.panel}.\n"
        "This records a tamper-evident digest over the panel and its ratification "
        "fields. It does NOT prove who ran it.\n"
        f"Type '{_SEAL_CONFIRMATION}' to continue, anything else to abort "
        f"(waiting up to {_SEAL_CONFIRM_TIMEOUT_S:.0f}s): ",
        end="",
        file=sys.stderr,
        flush=True,
    )
    answer = _read_confirmation(_SEAL_CONFIRM_TIMEOUT_S)
    if answer.strip().lower() != _SEAL_CONFIRMATION:
        # NOT "nothing was written". The invocation was journalled before this
        # function was reached, deliberately — an abandoned seal attempt is
        # precisely what the trail exists to show. Claiming otherwise would have
        # the command lie about the one record that outlives it.
        print(
            "ERROR: refusing to seal — confirmation not given. The panel was NOT "
            "modified. The attempt itself is recorded in the run journal, as every "
            "invocation is.",
            file=sys.stderr,
        )
        return 2

    from chipsim.harmonize.pgp_label import seal_panel

    digest = seal_panel(ns.panel)
    print(f"sealed {ns.panel}\n{digest}")
    return 0


def _cmd_theta_scaffold(ns: argparse.Namespace) -> int:
    from chipsim.transport.theta import SCAFFOLD_RELPATH, write_scaffold

    out = ns.out or (project_root() / SCAFFOLD_RELPATH)
    print(f"theta scaffold written: {write_scaffold(out, force=ns.force)}")
    print(
        "Copy it to configs/theta_priors.yaml yourself and fill it. No agent step "
        "creates that path: its absence is how Global Constraint #1 is enforced (S6)."
    )
    return 0


def _cmd_transport_prior_scaffold(ns: argparse.Namespace) -> int:
    from chipsim.transport.prior import SCAFFOLD_RELPATH, write_scaffold

    out = ns.out or (project_root() / SCAFFOLD_RELPATH)
    print(f"transport-prior scaffold written: {write_scaffold(out, force=ns.force)}")
    return 0


def _cmd_theta_check(ns: argparse.Namespace) -> int:
    """Report whether a filled theta file would be accepted by the M1 fit.

    Exits non-zero on refusal so a human can gate on it, and prints the cited/assumed
    split either way: two of six assumed is a stated limitation, not a failure.
    """
    from chipsim.transport.theta import ThetaConfig, ThetaError

    try:
        cfg = ThetaConfig.load(ns.theta)
    except ThetaError as exc:
        print(f"theta REFUSED: {exc}")
        return 1
    print(f"theta accepted: {ns.theta}")
    print(f"  cited: {cfg.cited_count}  assumed: {cfg.assumed_count}")
    if cfg.assumed_fields():
        print(f"  assumed field(s): {', '.join(cfg.assumed_fields())}")
    return 0


def _cmd_transport_prior_check(ns: argparse.Namespace) -> int:
    from chipsim.transport.prior import TransportPrior, TransportPriorError

    try:
        prior = TransportPrior.load(ns.prior)
    except TransportPriorError as exc:
        print(f"transport prior REFUSED: {exc}")
        return 1
    print(f"transport prior accepted: {ns.prior}")
    assumed = prior.assumed_entries()
    print(f"  explicit assumption(s): {', '.join(assumed) if assumed else 'none'}")
    return 0


def _cmd_sourcing_check(ns: argparse.Namespace) -> int:
    """Validate an M1 input sourcing worksheet and report how much of it is backed.

    Exits non-zero only when a row carries a value it cannot back. An unfinished
    worksheet exits 0: the honest state of work whose sources are unreachable is not a
    failure, and failing it would push whoever holds it to fill the rows from memory.
    """
    from chipsim.transport.sourcing import (
        SourcingError,
        completion_report,
        load_sourcing_worksheet,
    )

    try:
        worksheet = load_sourcing_worksheet(ns.worksheet)
    except SourcingError as exc:
        print(f"sourcing worksheet REFUSED: {exc}")
        return 1
    print(f"sourcing worksheet accepted: {ns.worksheet}")
    for group, counts in completion_report(worksheet).items():
        print(
            f"  {group}: {counts['filled']}/{counts['rows']} backed "
            f"(cited {counts['cited']}, derived {counts['derived']}, "
            f"assumed {counts['assumed']}, empty {counts['empty']})"
        )
    return 0


def _cmd_reference_compounds_check(ns: argparse.Namespace) -> int:
    from chipsim.harmonize.reference_compounds import (
        ReferenceCompoundError,
        load_reference_compounds,
    )

    try:
        frame = load_reference_compounds(ns.reference)
    except ReferenceCompoundError as exc:
        print(f"reference compounds REFUSED: {exc}")
        return 1
    print(f"reference compounds accepted: {ns.reference} ({len(frame)} entries)")
    return 0


#: Subcommand -> handler. Declared after every handler is defined, and asserted
#: against the parser in tests/test_workflow_export.py so a registered subcommand
#: without a handler fails there rather than at a user's first invocation.
def _cmd_adjudication_worksheet(ns: argparse.Namespace) -> int:
    """T13 — emit the adjudication worksheet the principal fills in at T14.

    THE WRITER HAD NO PRODUCTION CALLER. Thirty-odd test call sites and no way for a human to run
    it; T16's workflow export is descoped, so the CLI is the only invocation path there was going
    to be. This is that path.

    THE ROSTER IS THE AUTHORITY ON WHICH ROWS EXIST (T13's done-condition: exactly one row per T18
    entry). It is a HUMAN artifact and `roster.load_poc_roster` validates it without ever
    generating one, so this command REFUSES when it is absent rather than emitting a worksheet over
    whatever the snapshot happened to contain — a worksheet with the wrong rows costs T14's 60-90
    minutes, which is the cost T13's never-clobber rule already exists to protect.

    THE ABCB1 ACCESSION IS RESOLVED FROM THE RATIFIED PANEL, never hard-coded here: composition is
    configuration, not code (defect 4 / AM-2). This command does not resolve it itself — it passes
    the panel path down to `pgp_substrate_label`, which owns that resolution.
    """
    from chipsim.guards.output_roots import OutputRootError
    from chipsim.harmonize.adjudication import write_adjudication_worksheet
    from chipsim.harmonize.ids import (
        add_canonical_identity_excluding,
        load_preregistered_exclusions,
        relative_stereo_keys,
    )
    from chipsim.harmonize.label_reference import load_label_reference
    from chipsim.harmonize.pgp_label import barrier_panel_edges, pgp_substrate_label
    from chipsim.harmonize.roster import load_poc_roster
    from chipsim.ingest.drugbank_snapshot import load_compounds, load_protein_edges

    roster_path = Path(ns.roster)
    if not roster_path.exists():
        print(
            f"ERROR: no roster at {roster_path}. T13 emits exactly one row per T18 roster entry, "
            f"and T18 is human-owned — `load_poc_roster` validates a roster a human wrote and "
            f"never generates one. Refusing to emit a worksheet over an unratified row set.",
            file=sys.stderr,
        )
        return 2

    compounds, _excluded = add_canonical_identity_excluding(
        load_compounds(ns.raw_dir),
        preregistered=load_preregistered_exclusions(Path(ns.exclusions)),
    )
    panel_edges = barrier_panel_edges(load_protein_edges(ns.raw_dir), Path(ns.panel))
    labels = pgp_substrate_label(compounds, panel_edges, Path(ns.panel))

    roster = load_poc_roster(
        roster_path,
        snapshot_keys=set(compounds["canonical_inchikey"]),
        relative_stereo_keys=relative_stereo_keys(compounds),
    )
    # The roster SELECTS; it never invents. A key it names that the labeller did not produce is a
    # disagreement between two human-ratified inputs, and it must surface rather than become a
    # silently shorter worksheet.
    missing = [k for k in roster["canonical_inchikey"] if k not in labels.index]
    if missing:
        print(
            f"ERROR: {len(missing)} roster key(s) have no snapshot label. The roster and the "
            f"snapshot disagree about what exists; emitting the rows that happen to match would "
            f"hide that.",
            file=sys.stderr,
        )
        return 2
    labels = labels.loc[list(roster["canonical_inchikey"])]

    reference = load_label_reference(ns.label_reference) if ns.label_reference else None
    try:
        rows = write_adjudication_worksheet(labels, compounds, ns.out, label_reference=reference)
    except OutputRootError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(f"wrote {ns.out} (rows={rows})")
    return 0



def _cmd_adjudication_export(ns) -> int:
    """T14's publish step (r2.19, G-18), on the `chipsim panel-seal` precedent (C4).

    A helper whose only invocation is a Python call loses to hand-deleting columns in a
    spreadsheet — which is the accident it exists to prevent. The reviewer finishing 60-90
    minutes of adjudication needs a command, and needs a REFUSAL to arrive as a message and a
    non-zero exit rather than a traceback.
    """
    import pandas as pd

    from chipsim.harmonize.adjudication import AdjudicationError, export_tracked_adjudication

    try:
        rows = export_tracked_adjudication(ns.worksheet, ns.out)
    except AdjudicationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except (OSError, UnicodeDecodeError, pd.errors.ParserError, pd.errors.EmptyDataError) as exc:
        # A mistyped --worksheet is the likeliest operator error at the end of a 60-90 minute
        # task, and it used to arrive as a 25-line pandas traceback — the failure mode this
        # command's own docstring promises to abolish.
        print(f"ERROR: cannot read or write: {exc}", file=sys.stderr)
        return 2

    # The filled count, not just the row count: a wholly-blank export is well-formed and T15 will
    # later reject it as "wholly unadjudicated". Saying "24 row(s), 0 carrying a verdict" at the
    # moment the human believes they are finished is the whole point of printing anything.
    try:
        filled = int(
            (pd.read_csv(ns.out, dtype=str, keep_default_na=False)["adjudicated_label"] != "").sum()
        )
    except Exception:  # noqa: BLE001 - reporting must never fail a successful export
        print(f"wrote {rows} row(s) to {ns.out}")
        return 0
    print(f"wrote {rows} row(s) to {ns.out} ({filled} carrying a verdict)")
    return 0



_HANDLERS = {
    "fetch": _cmd_fetch,
    "hash-verify": _cmd_hash_verify,
    "parse": _cmd_parse,
    "provenance-tests": _cmd_provenance_tests,
    "write": _cmd_write,
    "adjudication-worksheet": _cmd_adjudication_worksheet,
    "panel-seal": _cmd_panel_seal,
    "adjudication-export": _cmd_adjudication_export,
    "theta-scaffold": _cmd_theta_scaffold,
    "transport-prior-scaffold": _cmd_transport_prior_scaffold,
    "theta-check": _cmd_theta_check,
    "transport-prior-check": _cmd_transport_prior_check,
    "reference-compounds-check": _cmd_reference_compounds_check,
    "sourcing-check": _cmd_sourcing_check,
}


_RUN_CONFIRMATION = "run"

#: The same bound as the seal prompt: long enough for a human who is present, short enough that an
#: unattended shell does not sit open forever holding a lock on the tree.
_RUN_CONFIRM_TIMEOUT_S = 120.0


def _approval_parent() -> argparse.ArgumentParser:
    """The `--yes` flag, shared by every ETL subparser so it reads `chipsim parse --yes`.

    A RECORDED ESCAPE, NOT A BYPASS. A gate that cannot be satisfied without a terminal is a gate
    that gets deleted the first time someone needs to run the stage from a script — so the escape
    exists, and the run record says which way the run was approved. An UNRECORDED escape would be
    worse than no gate at all: it would make an unattended run indistinguishable from one a human
    agreed to, which is the exact shape of false clean this project keeps finding.
    """
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument(
        "--yes",
        action="store_true",
        help=(
            "approve this run non-interactively. Recorded in the run journal as an explicit "
            "approval mode, so an unattended run is never indistinguishable from an answered one."
        ),
    )
    parent.add_argument(
        "--approved-by",
        metavar="WHO",
        default=None,
        help=(
            "who supplied the approval, when it is not the operator at the terminal — recorded "
            "VERBATIM in the run journal. Omit it and the field is absent; it is never defaulted "
            "and never inferred."
        ),
    )
    return parent


def _write_approval_record(
    run_dir,
    command: str,
    mode: str,
    tty: bool,
    argv: list[str],
    approved_by: str | None = None,
) -> None:
    """Record HOW the run was approved, beside the config snapshot it was approved over.

    Written at approval time rather than at the end, because a stage that crashes must still leave
    evidence of how it came to run. `outcome.json` is written last by design and a crash leaves
    none — approval is not an outcome.

    T29 (r2.40), AND THE GAP THAT PRODUCED IT. T13's first run under r2.38's delegation showed
    that `mode="flag"` with `stdin_was_a_tty=false` is BYTE-FOR-BYTE what an unsupervised agent run
    produces — so the record could not distinguish "approved by an authority that delegated the
    flag" from "nobody was ever asked". `approved_by` closes that, and its three properties are the
    ruling, not conveniences:

      * **VERBATIM** — stored exactly as given, never normalised into a known set.
      * **NO DEFAULT** — omitted means ABSENT, not an empty string and not a placeholder. A
        defaulted value would recreate the ambiguity it exists to remove.
      * **NEVER INFERRED** — not from `agent-identity`, not from `mode`, not from the absence of a
        TTY. This file already states that the manifest digest "does not prove who wrote it", and
        that honesty extends here rather than being quietly eroded by a field that looks like
        authentication. It is a LABEL SOMEONE CHOSE TO ATTACH, and nothing more.

    `mode` and `stdin_was_a_tty` keep their meaning unconditionally; this is additive.
    """
    payload = {
        "record_type": "approval",
        "record_schema": 1,
        "command": command,
        # "interactive" — a human typed the confirmation at a terminal.
        # "flag" — `--yes` was passed; nobody was necessarily present.
        "mode": mode,
        "stdin_was_a_tty": tty,
        "approved_at": datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ"),
        "argv": list(argv),
    }
    # Absent, not defaulted: the key appears only when someone supplied it.
    if approved_by is not None:
        payload["approved_by"] = approved_by
    (Path(run_dir) / "approval.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _approve_etl_run(ns, run_dir, argv: list[str]) -> bool:
    """Ask before writing. Returns True when the stage may proceed.

    WHAT THIS IS WORTH, EXACTLY — the same bound as the seal gate, and stated for the same reason.
    It does NOT identify who approved: whoever types the word is unidentified, and an agent that
    allocates a pty can type it too. It converts an ACCIDENTAL run into a DELIBERATE one, and it
    makes the distinction VISIBLE in the journal afterwards. It is not authentication and nothing
    here may be described as such.

    The prompt goes to STDERR, matching `panel-seal`: on stdout, `chipsim parse > log.txt` swallows
    the question while the command waits on a read the human cannot see they owe it, which reads as
    a hang — and a hang is what people work around by piping `yes` into it.
    """
    tty = _stdin_is_interactive()
    if getattr(ns, "yes", False):
        if run_dir is not None:
            _write_approval_record(
                run_dir, ns.command, "flag", tty, argv, getattr(ns, "approved_by", None)
            )
        return True

    if not tty:
        print(
            f"ERROR: refusing to run {ns.command!r} — this stage writes artifacts and no approval "
            f"was given.\n"
            f"Pass --yes to approve non-interactively (it is RECORDED in the run journal as such), "
            f"or run it from a terminal and answer the prompt.",
            file=sys.stderr,
        )
        return False

    print(
        f"About to run {ns.command!r}, which WRITES ARTIFACTS under this project.\n"
        f"The exact configs for this run are already snapshotted in {run_dir}.\n"
        f"Type '{_RUN_CONFIRMATION}' to continue, anything else to abort "
        f"(waiting up to {_RUN_CONFIRM_TIMEOUT_S:.0f}s): ",
        end="",
        file=sys.stderr,
        flush=True,
    )
    answer = _read_confirmation(_RUN_CONFIRM_TIMEOUT_S)
    if answer.strip().lower() != _RUN_CONFIRMATION:
        print(
            f"ERROR: refusing to run {ns.command!r} — approval not given. Nothing was written by "
            f"the stage. The run record, including its config snapshot, is kept: a declined run is "
            f"exactly what the trail exists to show.",
            file=sys.stderr,
        )
        return False
    if run_dir is not None:
        _write_approval_record(
            run_dir, ns.command, "interactive", tty, argv, getattr(ns, "approved_by", None)
        )
    return True


# --------------------------------------------------------------------------- #
# T25 — the run journal around fit/predict (r2.39 Finding C: FUNCTION-LEVEL ONLY)
# --------------------------------------------------------------------------- #
#
# NO CLI SUBCOMMAND, and that is a ruling rather than a convenience. Finding C (r2.39) settled it:
# T25 wires `journal.start_run` into the existing call path, there is no `chipsim fit` verb at M1,
# and therefore r2.34's ETL_SUBCOMMANDS / node-vs-non-node split and NON_NODE_REASONS do not apply
# — nothing to declare because nothing is exposed. If M2+ adds a CLI entry point, THAT task earns
# the three declarations when it is written, not retroactively here.
#
# NO NEW JOURNAL MECHANISM either: this is the integration point into the one S12 already built.
# Scores ride `finish_run`'s existing `detail` field as canonical JSON, rather than gaining a new
# parameter or a new file in the run directory.


def _scores_detail(payload: dict) -> str:
    """Canonical JSON for the outcome's `detail`, so two identical runs record identical bytes.

    `sort_keys` and fixed separators remove the two ways an equal mapping can serialise
    differently. Floats use Python's repr, which is round-trippable and deterministic for a given
    value — so "bit-identical recorded scores" is a property of the encoding, not a hope about it.
    """
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _journalled_call(command: str, root, argv, work, describe):
    """Open a run, do the work, record the outcome LAST. The shared half of both wrappers.

    ORDERING IS THE CONTRACT. `start_run` snapshots `configs/` BEFORE any work, so the config
    record always precedes the computation it describes. `finish_run` writes `outcome.json` LAST,
    so a process killed mid-work leaves NO outcome — and `read_outcome`'s own docstring is careful
    that absence means "no completion was recorded", never "crashed". A failure this code CATCHES
    gets an explicit `status="crashed"` outcome, which is the distinction that keeps absence
    meaning the weaker, true thing.
    """
    run_dir = start_run(command, Path(root), argv=argv)
    try:
        result = work()
    except BaseException as exc:
        finish_run(run_dir, status="crashed", detail=_scores_detail({"error": type(exc).__name__}))
        raise
    finish_run(run_dir, status="ok", detail=_scores_detail(describe(result)))
    return result, run_dir


def run_transport_fit(
    reference_compounds, theta, *, prior, drug_params_by_key, schedule, t, root=None
):
    """T25: `fit_transport_params` under a journalled run. Returns `(FitResult, run_dir)`.

    A&D §4.4a-ii words the replay property as "same config + same seed reproduces the same scores
    exactly". THERE IS NO SEED HERE, and this signature deliberately does not invent one: the fit
    has no stochastic component — T22's integrator is fixed-step and T23's simplex start is fixed,
    both for exactly this reason. A `seed` parameter that fed nothing would be a knob implying a
    guarantee it does not provide. The replay property holds by construction instead.
    """
    from chipsim.transport.fit import fit_transport_params

    root = Path(root) if root is not None else project_root()
    return _journalled_call(
        "fit-transport-params",
        root,
        [__name__, "fit-transport-params"],
        lambda: fit_transport_params(
            reference_compounds,
            theta,
            prior=prior,
            drug_params_by_key=drug_params_by_key,
            schedule=schedule,
            t=t,
        ),
        lambda r: {
            "alpha": r.alpha,
            "k_sink": r.k_sink,
            "objective": r.objective,
            "n_reference": r.n_reference,
            "converged": r.converged,
        },
    )


def run_transport_ode(theta, drug_params, schedule, t, *, alpha=1.0, root=None):
    """T25: `transport_ode` under a journalled run. Returns `(C_free array, run_dir)`.

    The recorded score is a DIGEST of the returned curve, not the curve itself: a run record is an
    audit trail, and pasting a 600-point array into `detail` would bury the thing a reader is
    checking. Two runs agreeing on the digest is the same claim as agreeing on the array, stated
    in one line.
    """
    from chipsim.transport.ode import transport_ode

    root = Path(root) if root is not None else project_root()
    return _journalled_call(
        "transport-ode",
        root,
        [__name__, "transport-ode"],
        lambda: transport_ode(theta, drug_params, schedule, t, alpha=alpha),
        lambda curve: {
            "c_free_sha256": hashlib.sha256(curve.tobytes()).hexdigest(),
            "n_points": int(curve.size),
        },
    )



def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog=f"python -m {MODULE_PATH}")
    sub = ap.add_subparsers(dest="command", required=True)
    approval = _approval_parent()

    p = sub.add_parser("fetch", help="download the pinned snapshot", parents=[approval])
    p.add_argument("--dest", required=True, type=Path)
    p.add_argument("--commit", required=True)

    p = sub.add_parser("hash-verify", help="recompute sha256s against the manifest", parents=[approval])
    p.add_argument("--dest", required=True, type=Path)

    p = sub.add_parser("parse", help="parse compounds + protein edges", parents=[approval])
    p.add_argument("--raw-dir", required=True, type=Path, dest="raw_dir")

    p = sub.add_parser("provenance-tests", help="run the provenance contract suite", parents=[approval])
    p.add_argument("--tests", default=Path("tests/test_provenance.py"), type=Path)

    p = sub.add_parser("write", help="persist the compound frame", parents=[approval])
    p.add_argument("--raw-dir", required=True, type=Path, dest="raw_dir")
    p.add_argument("--out", required=True, type=Path)

    p = sub.add_parser(
        "adjudication-worksheet",
        help="T13: emit the adjudication worksheet for T14 (one row per T18 roster entry)",
        parents=[approval],
    )
    p.add_argument("--raw-dir", required=True, type=Path, dest="raw_dir")
    p.add_argument("--roster", required=True, type=Path)
    p.add_argument("--panel", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--exclusions", required=True, type=Path)
    p.add_argument(
        "--label-reference",
        dest="label_reference",
        type=Path,
        default=None,
        help=(
            "committed label/structure reference. Omitted, `label_disagrees_with_key` is "
            "'unresolved' rather than silently 'agrees'."
        ),
    )
    p = sub.add_parser(
        "adjudication-export",
        help="publish the filled T14 worksheet as the tracked five-column file",
        description=(
            "Project the reviewer's filled worksheet to the five TRACKED columns "
            "(canonical_inchikey, adjudicated_label, evidence_doi, adjudicated_by, "
            "adjudicated_on) and write it to --out. Refuses any extra column the reviewer "
            "added rather than dropping it, and refuses to blank a verdict the existing "
            "tracked file already carries. `name` is dropped by design: a name beside a "
            "structure key must not be tracked."
        ),
    )
    p.add_argument("--worksheet", required=True, type=Path)
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

    p = sub.add_parser(
        "theta-scaffold",
        help="write S13's EMPTY theta template (no values — T20 is human-owned)",
        description=(
            "Write the theta-priors scaffold: six fields, every value and citation "
            "empty, every field flagged assumed.\n\n"
            "It refuses to write configs/theta_priors.yaml or configs/assumptions.yaml "
            "(S6: their absence is the enforcement mechanism for the rule that no agent "
            "writes a biological number), and it refuses to overwrite a file that "
            "already carries filled entries unless --force is passed."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--out", type=Path, default=None)
    p.add_argument("--force", action="store_true")

    p = sub.add_parser(
        "transport-prior-scaffold",
        help="write S14's EMPTY (alpha, k_sink) prior template",
    )
    p.add_argument("--out", type=Path, default=None)
    p.add_argument("--force", action="store_true")

    p = sub.add_parser(
        "theta-check",
        help="validate a filled theta file the way the fit will (read-only)",
    )
    p.add_argument("--theta", required=True, type=Path)

    p = sub.add_parser(
        "transport-prior-check",
        help="validate a filled transport-prior file (read-only)",
    )
    p.add_argument("--prior", required=True, type=Path)

    p = sub.add_parser(
        "reference-compounds-check",
        help="validate T21's M1 reference-compound file (read-only)",
    )
    p.add_argument("--reference", required=True, type=Path)

    p = sub.add_parser(
        "sourcing-check",
        help="validate an M1 input sourcing worksheet: no value without its quote",
        description=(
            "Check a literature-sourcing worksheet for the M1 inputs.\n\n"
            "A row may be EMPTY; a row may NOT carry a value without the verbatim quote, "
            "the DOI and a confirmed-DOI flag behind it (principal, 2026-10-08: unbacked "
            "data cannot be used). A `derived` value additionally needs its formula, and "
            "an `assumed` one needs a stated width and must NOT quote a source.\n\n"
            "An unfinished worksheet exits 0 and prints how much is backed."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--worksheet", required=True, type=Path)

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
        # operator-security event; running the stage anyway and exiting 0 made an
        # attempted exfiltration indistinguishable from a clean run.
        print(f"ERROR: refusing to run {ns.command!r}: {exc}", file=sys.stderr)
        return 2

    # APPROVE ON EXECUTE — AFTER the config snapshot, BEFORE the work.
    #
    # The order is deliberate and it mirrors `panel-seal`, which journals the attempt before asking:
    # a DECLINED run is exactly what the trail exists to show, so it must leave a record carrying
    # the configs it would have run under. Asking first would make a refusal invisible.
    #
    # This closes the second half of the principal's standing instruction — "every run should log /
    # save the exact config, always create new config copies for run, APPROVE ON EXECUTE". The
    # first half was already built and working; this half existed only for `panel-seal`, so every
    # stage that WRITES ARTIFACTS ran unapproved.
    if not _approve_etl_run(ns, run_dir, argv_recorded):
        if run_dir is not None:
            _journal_best_effort(
                lambda: finish_run(
                    run_dir, status="declined", detail="approval not given before execute"
                ),
                root=root,
                what="finish_run:declined",
            )
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
