"""What a project WAIVES, as a type — the seam between the guard and whoever owns the content.

A LEAF, like `errors`. It imports nothing from the package, and that is the point (r2.29): the seam
exists so the guard need not know about DrugBank, and until this move it forced DrugBank to import
the guard — `chipsim/ingest/drugbank_snapshot.py` pulled in the ENTIRE 1,329-line
`guards/record_content.py` to construct a TWO-FIELD DATACLASS. A seam that couples its two sides
more tightly than no seam at all is not yet a seam.

THE TWO PREDICATES HAVE OPPOSITE SAFE DIRECTIONS, which is why neither is defaulted and why they are
a type rather than two arguments that travel together by convention.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path


def nothing_is_waived(root: Path, rel: str) -> bool:
    """Default readability waiver: nothing is waived. Fail-closed."""
    return False


def nothing_is_content_exempt(rel: str) -> bool:
    """Default content-exemption predicate: nothing is exempt. Fail-closed."""
    return False


@dataclass(frozen=True)
class ContentPolicy:
    """What the OWNING project waives, injected rather than imported.

    The guard must not know about DrugBank. There is NO default: the two predicates have opposite
    safe directions — waiving nothing makes the scan noisier, exempting nothing makes it QUIETER,
    because the double-exemption defect stops firing and the declaration it would have broken then
    holds. A default that is fail-closed for one member and fail-open for the other is worse than
    no default, because its docstring can only be half true.

    THE NAME IS NARROWER THAN IT READS, and a reviewer was right to say so: a type called
    `ContentPolicy` invites the conclusion that this is where policy lives, and it holds two of the
    guard's policy decisions. `_OWNERSHIP_PREFIXES`, the two declaration-file locations, the
    minimum-plausible-tracked floor and `THIS_PROJECT` are all equally policy and all still module
    constants in `record_content`. That mis-naming is part of why project identity never looked like
    something that needed injecting. Left as-is here deliberately — renaming or widening it is a
    ruling, not a refactor, and it is open with the CTO.
    """

    #: "This file's readability is not this gate's business."
    #: SAFE DIRECTION: waiving nothing makes the scan read MORE, so refusing nothing is fail-closed
    #: here — but it is stated per predicate and not defaulted, because the other one is the reverse.
    readability_waived: Callable[[Path, str], bool]
    #: "This path is ALREADY exempt by the content mechanism", so declaring it too would exempt it
    #: twice and make it invisible to both halves of the guard. This one DOES cover the ledger.
    #: SAFE DIRECTION: THE OPPOSITE. Exempting nothing means the double-exemption defect never fires,
    #: so the declaration HOLDS and the file is CLEARED. Fail-closed here would be exempting
    #: EVERYTHING, which is absurd as a default — which is the whole reason neither has one.
    content_exempt: Callable[[str], bool]


#: Waives nothing and exempts nothing. NOT a default — a caller must choose it deliberately,
#: because "exempt nothing" is the QUIETER direction for declarations, not the safer one.
NOTHING_WAIVED = ContentPolicy(
    readability_waived=nothing_is_waived, content_exempt=nothing_is_content_exempt
)
