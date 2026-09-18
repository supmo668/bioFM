"""E6-7: the one entry point a non-pytest consumer can call.

Until this module existed, the four halves of the record-content invariant — READABILITY (can every
tracked file be decoded), DECLARATIONS (is every exemption a claim that holds), OWNERSHIP (whose
gate does a failure fall to), and ACCESSION CONTENT (does any readable file carry a real regulatory
identifier) — were composed by the TEST SUITE and by the report renderer. The invariant was
therefore enforced for whoever runs `pytest`, and for nobody else: CI, a pre-commit hook and another
project had nothing to call.

This is a COMPOSITION ROOT and nothing else. It re-implements none of the checks, so there stays one
definition of each — there is no regex here, no magic bytes, no decoding, no git invocation. It
imports the generic guard (`chipsim.guards.record_content`) and this project's DrugBank-specific
half (`chipsim.ingest.drugbank_snapshot`), which is why it lives above both rather than inside
either: the guard must not know about DrugBank, and ingest is about ingesting a snapshot.

THE FAIL LIVES HERE. `enforce_record_content` RAISES on anything but a clean result, so the only way
to receive a value is for the gate to have passed. A consumer that had to inspect a return value
would be re-implementing the decision, and every consumer would do it slightly differently — which
is the state this clause exists to end.

THREE STATES, NOT A BOOLEAN (E-13): `clean` (0), `files-fail` (2), `could-not-scan` (3). "I could
not look" must never arrive at the same answer as "I looked and it was fine", nor at the same one as
"I looked and it failed".
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# Imported as MODULES, not as names. Binding the functions by value would freeze them at import
# time, which hides the coupling and makes the composition untestable — a composition root should
# call through its collaborators, not hold copies of them.
from chipsim.guards import record_content as _guard
from chipsim.guards.errors import RecordContentScanError
from chipsim.guards.record_content import ContentPolicy
from chipsim.ingest import drugbank_snapshot as _drugbank
from chipsim.ingest.drugbank_snapshot import DRUGBANK_CONTENT_POLICY

#: The three outcomes and the exit code each carries, kept together so a consumer cannot map one to
#: the wrong other. `2` is "files fail this gate"; `3` is "the gate could not be evaluated".
_EXIT = {"clean": 0, "files-fail": 2, "could-not-scan": 3}


@dataclass(frozen=True)
class RecordContentResult:
    """A CLEAN result. The failing cases arrive as `RecordContentViolation` instead."""

    status: str
    exit_code: int
    root: Path
    scanned: int
    report: str


class RecordContentViolation(RuntimeError):
    """The gate did not pass. Carries the three-state status rather than flattening it.

    `files-fail` and `could-not-scan` are both failures and are NOT the same failure: the first says
    which files, the second says the question could not be asked. A consumer that collapses them
    loses the only distinction that tells it whether to fix a file or fix its checkout.
    """

    def __init__(self, status: str, report: str, root: Path | None = None, scanned: int = 0):
        super().__init__(f"record-content gate: {status}\n{report}")
        self.status = status
        self.exit_code = _EXIT[status]
        self.report = report
        self.root = root
        self.scanned = scanned


def enforce_record_content(
    policy: ContentPolicy = DRUGBANK_CONTENT_POLICY, *, byte_source: str
) -> RecordContentResult:
    """Run the whole record-content invariant and RAISE unless it is clean.

    Composes, in one call, the four checks that were previously only ever assembled by the test
    suite: readability and declarations and ownership (via the report renderer, which already joins
    those three and is the artifact a human reads), and accession content (the DrugBank half, which
    lives in the ingest module and which nothing outside the suite had ever run alongside the rest).

    Raises `RecordContentViolation` on `files-fail` or `could-not-scan`; returns the result only
    when the gate is clean. The fail lives HERE so that no consumer has to know which checks to run,
    in which order, or which return value means failure.
    """
    try:
        # ONE reading of the tree, shared by both halves. Until r2.27 §11 this called
        # `_tracked_listing` AND `_render_for_root`, which listed the repository TWICE: the
        # `scanned` count on the result came from the first listing and the `scanned` count inside
        # the report text came from the second, so one object carried two numbers claiming to be
        # the same thing — E-14's defect reinstated one layer above the fix for it. It also reached
        # into two PRIVATE guard names while the commit that introduced it claimed none remained.
        with _guard.scan_context(_guard.repo_root(), policy, byte_source) as context:
            scan = _guard.scan_record_content(context)
            report, code = _guard.render_scan(scan)
            # The accession half reads bytes too, so it reads the SAME copy — otherwise one half
            # could certify the staged blobs while the other certified the working files, which is
            # the split-evidence defect E6-5 is about, one level down.
            read_root, paths = context.read_root, list(context.paths)
            hits = _drugbank.real_accession_hits(read_root, paths)
            ledger = _drugbank.ledger_tuple_hits(read_root)
        root = context.root
    except RecordContentScanError as exc:
        raise RecordContentViolation("could-not-scan", str(exc)) from exc

    # The accession half. The scan above answers "can every tracked file be READ"; this answers
    # "does anything readable CARRY a regulatory identifier", which is the other half of the
    # invariant and the one that had no non-pytest caller at all. Same listing, so a file cannot be
    # seen by one half and missed by the other.
    if hits or ledger:
        lines = [report, "", "REAL ACCESSIONS IN TRACKED CONTENT:"]
        lines += [f"  {rel}: {accession}" for rel, accession in hits]
        lines += [f"  {rel}:{line} {accession}" for rel, line, accession in ledger]
        report = "\n".join(lines)
        code = 2

    if code:
        raise RecordContentViolation("files-fail", report, root, len(paths))
    return RecordContentResult("clean", 0, root, len(paths), report)
