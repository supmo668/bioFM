"""The authorship-overclaim scan, shared by the source and card honesty tests.

Extracted because two tests were nominally enforcing the same rule and only one
of them actually enforced anything. `test_card_never_claims_the_seal_proves_
authorship` checked that four disclaimer SUBSTRINGS were present, which a card
saying the exact opposite still satisfies — "it **does** establish who ratified
it" contains "establish who"; "not authentication **in the pedantic sense**"
contains "not authentication". Its docstring delegated the negative half to
`test_no_wording_claims_the_journal_authenticates_anyone`, whose source list did
not include the card module. The highest-damage overclaim surface in the repo was
governed by presence-only checks on one side and an absent file on the other.

Both callers now run the same polarity-aware scan: a forbidden phrase is a
failure unless a negation precedes it in the same sentence.
"""

from __future__ import annotations

import re

#: Claims the seal and the journal cannot support. The digest is unkeyed over
#: public content: it DETECTS modification and says nothing about who wrote it.
#: `(?:proves?|proved|proof)` — the NOUN form was missing, and "the seal is
#: proof a human checked every accession" therefore passed a scan built to catch
#: exactly that sentence. Overclaims arrive as nouns at least as often as verbs.
_PROVE = r"(?:proves?|proved|proof(?: that)?|evidence)"

FORBIDDEN = [
    rf"{_PROVE} (?:the |that )?(?:a )?human",
    r"authenticat(?:e|es|ing|ion)\b(?!\w)",
    rf"{_PROVE} who",
    r"attests? (?:that )?(?:a )?human",
    r"establish(?:es)? who",
    r"identif(?:y|ies) who",
    r"who[- ]ran",
    # TTY-gate paraphrases. The gate checks that stdin is a terminal; it does not
    # establish a human is present, and a pty defeats it.
    r"ensures? (?:a|the) human",
    r"impossible for an agent",
    r"prevents? an agent",
    r"guarantees? (?:a )?human",
    r"requires? a human to be present",
]

_NEGATION = re.compile(r"\b(?:not|never|cannot|no|nothing|neither)\b")


def normalize(raw: str) -> str:
    """Lowercase, collapse whitespace, AND close implicit-concatenation seams.

    The seam is the hole this function exists for. Collapsing `\\s+` alone leaves
    `"…proves a " "human sealed this panel."` reading as `proves a " "human`, so
    an adjacency pattern never matches — while the program PRINTS the sentence
    intact. Implicit concatenation is the dominant wrapping style in exactly the
    files this scan governs, so the scan was blind to its own subject matter in
    the ordinary case, not an exotic one. Verified: that message passed the scan
    and was printed verbatim to an operator's terminal.

    A `", "` between two list items keeps its comma and is left alone, so joining
    genuinely separate strings is not a risk.
    """
    text = re.sub(r"\s+", " ", raw.lower())
    return re.sub(r"[\"']\s*[\"']", "", text)


def assert_no_unqualified_claims(raw: str, label: str) -> int:
    """Raise if a forbidden claim appears without a preceding negation.

    Returns the number of matches inspected so the caller can assert the scan
    matched SOMETHING — a scan of text that says nothing about the limitation
    passes trivially, which is how a wholesale deletion of the disclaimers would
    otherwise read as compliance.
    """
    text = normalize(raw)
    inspected = 0
    for pattern in FORBIDDEN:
        for match in re.finditer(pattern, text):
            inspected += 1
            # The negation must appear BEFORE the claim and in the same sentence.
            # Searching the whole line let "authenticates the operator who wrote
            # it, no question" pass — the guard was bypassable with a "no" placed
            # after the claim.
            sentence_start = max(text.rfind(". ", 0, match.start()) + 1, 0)
            window = text[max(sentence_start, match.start() - 160) : match.start()]
            assert _NEGATION.search(window), (
                f"{label} appears to claim the journal or seal authenticates "
                f"someone: …{text[max(0, match.start() - 90) : match.start() + 60]}…"
            )
    return inspected
