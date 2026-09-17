"""What can go wrong, as types — and WHOSE FAULT each one is.

A LEAF. This module imports nothing from the package and nothing but the standard library's
`RuntimeError`, which is the whole point: `repo`, `decoding` and `record_content` all need the
exception vocabulary, and whichever of them owned it became a dependency of the others.

WHY IT MOVED HERE (r2.29). `RecordContentScanError` lived in `repo.py` under the rule "the exception
belongs with the layer that RAISES it". That rule was FALSE ON THE FACTS — `repo.py` raises it 5
times and `record_content.py` 24 — and the real reason was cycle avoidance: `record_content` imports
`repo`, so the exception could not live in `record_content` without a cycle. A rule written to
justify a decision already made is the genre this project keeps catching, and that one was written
here.

WHY THERE ARE THREE CLASSES AND ONLY TWO STATES. The gate reports three outcomes — clean, files-fail
(exit 2), could-not-scan (exit 3) — and a failure is one of two things from the CALLER's point of
view: the scan could not be performed at all, or the declaration data it needed was unusable. Those
already have different exit codes and were, until now, distinguished only by WHICH CALL SITE HAPPENED
TO CATCH THEM.

The third class is not a third state. It is a defect in THE GUARD, and it exists because the other
two blame the user's repository. Measured before the split:

    a guard bug raised inside `DeclarationSurface.require()` was caught by `read()`'s broad
    `except RecordContentScanError`, became `structural_error`, and was REPORTED AS EXIT 2 —
    "the declaration data could not be parsed" — for a file that parsed perfectly well.

So a programming error in the guard arrived as an accusation against the tree it was scanning. It
still lands in exit 3 (there is no fourth state, r2.28), but it says whose fault it is, and it is
NOT catchable by the handler that converts declaration problems into a report.
"""

from __future__ import annotations


class RecordContentScanError(RuntimeError):
    """Base. The name is retained because 29 raise sites and a large suite already say it.

    Catching THIS catches everything, which is what the old code did everywhere and is almost never
    what a caller wants. Prefer a subclass; the base is for "any guard failure at all".
    """


class ScanNotPerformed(RecordContentScanError):
    """THE SCAN COULD NOT BE PERFORMED — exit 3, and the repository is the subject.

    Repository topology that cannot be established, a listing that cannot be produced or cannot be
    shown to be of this tree, a container with no reader installed. The remedy is to the checkout or
    the environment, not to any file's content.
    """


class DeclarationDataUnusable(RecordContentScanError):
    """THE DECLARATION DATA IS UNUSABLE — exit 2, and a specific tracked file is the subject.

    The scan WORKS; only the exemption data is unreadable, so nothing is declared (the fail-closed
    direction: more files fail, never fewer) and the listing is still rendered beside the reason.
    That distinction is E-13's ruling, and it is why this may not collapse into `ScanNotPerformed`.
    """


class GuardInvariantViolated(RecordContentScanError):
    """A DEFECT IN THE GUARD ITSELF — never the repository's fault, and never silently converted.

    Raised by the `__post_init__` invariants: a scan whose `exit_code` disagrees with its rows, a
    row whose disposition is neither of the two values the failing-count matches on, a surface
    carrying entries beside a structural error. Every one of those is unreachable unless this
    module has a bug.

    It is deliberately NOT caught by `DeclarationSurface.read`, which exists to turn declaration
    problems into a rendered report. Before the split it WAS caught there, so a guard bug was
    reported to the operator as "the declaration data could not be parsed" — the guard blaming the
    user's file for its own defect. Measured, not hypothesised.
    """
