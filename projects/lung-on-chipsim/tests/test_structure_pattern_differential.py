"""E-23 (r2.48): the structure detector, bound by a differential oracle from the start.

`_STRUCTURE_RE` is the ONLY control on the exempt ledger files. Its InChIKey half carried a word
boundary at both ends, which is E-22's defect in its last remaining instance. This file pins the
pattern and compares it against a reference scanner written from the clause's spec sentence
(`tests/structure_reference.py`) over generated input.

PROBE PROVENANCE (r2.48 (i)). Every InChI and InChIKey in this file is INVENTED BY CONSTRUCTION:
keys are one repeated letter per segment or drawn by a seeded generator whose seed is printed
before the run; InChI bodies are meaningless placeholder text. Nothing is copied from any data,
ledger, fixture, dispatch or external source, and nothing is checked against any database.
"""

import itertools
import os
import random
import re
import string
import sys
import unicodedata

import pytest

from chipsim.ingest.drugbank_snapshot import (
    _STRUCTURE_RE,
    _TUPLE_WINDOW,
    REAL_ACCESSION_RE,
)
from tests.association_reference import reference_associations
from tests.structure_reference import reference_spans
from tests.test_accession_pattern_matrix import LEFT_CONTEXTS, RIGHT_CONTEXTS

#: `_INCHI_PREFIX` lived here and is DELETED by r2.49 (f). It named the InChI branch's literal
#: prefix so the equivalence proof could take its second character without spelling a letter --
#: but a constant restating production is still a restatement, and the proof that read it could
#: not notice production changing underneath. The proof now derives both branches' admissible
#: characters from the shipped pattern's own parse tree, so nothing needs to be named twice.

#: The SIGNED pattern (E-23 (a)), pinned over its text AND its flags.
SIGNED_PATTERN = r"InChI=1S?/\S+|[A-Z]{14}-[A-Z]{10}-[A-Z]"
SIGNED_FLAGS = re.UNICODE

#: E-23 (c). Printed BEFORE the corpus is built, so a timeout cannot lose it.
SEED = 20260926

#: r2.49 (a). The single-code-point axis witnesses the SIGNED single-code-point sentence, and it
#: costs 36.8 s while uniquely rejecting NOTHING, so it runs in the extended tier rather than on
#: every suite run. Set this to run it; the quality gate runs it and records the invocation.
EXTENDED = os.environ.get("AIADLC_STRUCTURE_ORACLE_EXTENDED") == "1"

_PIN_MESSAGE = (
    "the structure detector changed. That is a DELIBERATE act: update this pin, the signed E-23 "
    "clause and the reference oracle TOGETHER, in one commit. The pin makes a change VISIBLE; the "
    "differential oracle is what proves the signed pattern meets the spec."
)

# INVENTED: one repeated letter per segment (the CTO's all-A / all-B / C rule).
PROBE_KEY = "A" * 14 + "-" + "B" * 10 + "-" + "C"


def test_the_structure_pattern_is_pinned_over_its_TEXT_and_its_FLAGS():
    """E-23 (a). Text alone is not a pin: an IGNORECASE compile has an identical `.pattern`."""
    assert _STRUCTURE_RE.pattern == SIGNED_PATTERN, _PIN_MESSAGE
    assert _STRUCTURE_RE.flags == SIGNED_FLAGS, _PIN_MESSAGE


def test_a_lowercase_key_shape_is_NOT_a_structure():
    """E-23 (a) behavioural row. The sentence says ASCII UPPERCASE letters, so case is closed here."""
    for probe in (PROBE_KEY.lower(), "a" + PROBE_KEY[1:], PROBE_KEY[:-1] + "c"):
        assert _STRUCTURE_RE.search(probe) is None, f"{probe!r} matched. " + _PIN_MESSAGE


def test_the_sentences_whitespace_and_the_patterns_whitespace_coincide():
    """E-23 (b). The sentence says whitespace (`isspace`); the pattern uses `\\s`. Measured over all
    1,114,112 code points. A disagreement is a FINDING: report it, do not adjust either side."""
    ws = re.compile(r"\s")
    wrong = [cp for cp in range(0x110000) if bool(ws.fullmatch(chr(cp))) != chr(cp).isspace()]
    assert not wrong, f"\\s and isspace disagree on {len(wrong)} code points: {wrong[:8]}"


def test_the_sentences_uppercase_and_the_patterns_uppercase_coincide():
    """E-23 (b). The sentence says ASCII uppercase; the pattern uses `[A-Z]` under re.UNICODE."""
    up = re.compile(r"[A-Z]")
    ascii_up = set(string.ascii_uppercase)
    wrong = [cp for cp in range(0x110000) if bool(up.fullmatch(chr(cp))) != (chr(cp) in ascii_up)]
    assert not wrong, f"[A-Z] and ASCII uppercase disagree on {len(wrong)} code points: {wrong[:8]}"


def test_the_reference_finds_the_invented_probes_and_rejects_their_near_shapes():
    """E-23 (b). A reference that finds nothing agrees with a pattern that finds nothing."""
    assert reference_spans(PROBE_KEY) == [(0, 27)]
    # INVENTED: the InChI prefix plus a meaningless placeholder body.
    placeholder_inchi = "InChI=1S/" + "placeholder"
    assert reference_spans(placeholder_inchi) == [(0, len(placeholder_inchi))]
    assert reference_spans("InChI=1/" + "placeholder") == [(0, 19)]
    assert reference_spans("InChI=1S/ " + "placeholder") == []  # a body must be non-empty
    assert reference_spans(PROBE_KEY.lower()) == []
    assert reference_spans(PROBE_KEY[:-1]) == []  # one letter short


# ------------------------------------------------------------------------------------------- #
# E-23 (c) — GENERATED INPUT. Five axes, seeded, the seed printed before the first string.
#
# The corpus is produced as a stream of CHUNKS rather than one list: the two code-point axes are
# ~6.7M strings between them, and materialising that costs hundreds of megabytes for no benefit.
# Generation is cheap; holding it is not. Each consumer re-walks the stream.
# ------------------------------------------------------------------------------------------- #
# INVENTED: the InChI prefix plus a meaningless placeholder body.
PROBE_INCHI = "InChI=1S/" + "placeholder"

#: Prefix variants around the sentence's "InChI=1", optional "S", "/" clauses. Each one is a
#: question the sentence answers: is the prefix case-sensitive, is the "1" fixed, is the "S"
#: optional rather than free, must the "/" be present, may the body be empty or start with space.
INCHI_PREFIX_VARIANTS = (
    "InChI=1S/",
    "InChI=1/",
    "inchi=1S/",
    "INCHI=1S/",
    "InChI=2S/",
    "InChI=1T/",
    "InChI=1SS/",
    "InChI=1S",
    "InChI=1S/ ",
    "InChI=1 /",
)


def _invented_key(rng):
    """INVENTED BY CONSTRUCTION: 25 letters drawn by the seeded generator, never copied."""
    upper = string.ascii_uppercase
    return (
        "".join(rng.choice(upper) for _ in range(14))
        + "-"
        + "".join(rng.choice(upper) for _ in range(10))
        + "-"
        + rng.choice(upper)
    )


def _invented_inchi_body(rng):
    """INVENTED: meaningless placeholder text. The alphabet is deliberately q/x/z plus punctuation
    two non-ASCII characters, and ASCII UPPERCASE.

    WHY UPPERCASE IS IN THE ALPHABET (gate 6, finding 3). It was deliberately excluded, with the
    reason "so a body cannot accidentally spell a formula layer" — and that exclusion is what blinded
    the oracle. A real InChI's body opens with its formula layer, which is uppercase, so with a
    lowercase-and-punctuation alphabet NO generated body ever had the shape a real one has, and a
    guard refusing an uppercase first body character survived the entire corpus while missing every
    real structure of that form. The only artefacts that killed it were fixtures holding real
    identifiers, i.e. the ones clause (i) directs us to replace.

    Resemblance by SHAPE is not what (i) forbids: it forbids COPYING an identifier and ASSOCIATING
    one with a name or substance. These bodies are drawn character-by-character from the alphabet
    below by a seeded generator whose seed is printed before the corpus, carry no accession and no
    name, and are never read from any data file, ledger, fixture or dispatch. A random run of
    uppercase, digits and punctuation is the SHAPE of a formula layer and is not any formula.
    """
    alphabet = "QXZ" + "qxz0123456789/_.-+=?*" + "é中"
    return "".join(rng.choice(alphabet) for _ in range(rng.randrange(1, 30)))


#: One invented body well past any plausible column or length ceiling. Measured in gate 6: a body
#: length ceiling of 40 and a call-site column ceiling of 200 both survived the whole suite, because
#: the longest reachable body was ~30 characters and the longest first line 49. Length is therefore
#: an axis in its own right, not a property that comes free with the others.
_LONG_BODY_LEN = 260


def _invented_long_inchi_body(rng):
    """Same rule as `_invented_inchi_body`, at a length no ceiling in the range tolerates."""
    alphabet = "QXZ" + "qxz0123456789/_.-+=?*"
    return "".join(rng.choice(alphabet) for _ in range(_LONG_BODY_LEN))


def _one_edit_near_misses(key):
    """Every single-character substitution, deletion and duplication of a key.

    This axis binds the key's LENGTHS and its two hyphen positions, and it binds the letter
    classes only over the seven substitute characters listed below — a lowercase letter, a digit,
    a Latin-1 letter, a Greek capital, an ASCII hyphen, an underscore and an en dash. The last two
    are there because a near-miss that is still 27 characters long is the one a length check would
    miss.

    NOT CLOSED, and measured rather than conceded: widening a segment's letter class by ONE
    non-ASCII character that this list does not contain survives all 7,320,676 corpus strings
    (gate 6). The word "closed" appeared here in an earlier draft; it is exactly the claim r2.47b
    RETRACTED for E-22's token axis, and it was no truer here. The surviving direction
    over-matches, so the guard stays fail-closed — a false sentence rather than an open leak, but
    a false sentence in the file whose job is being checkable by reading.
    """
    out = []
    for pos in range(len(key)):
        for replacement in ("a", "7", "É", "Α", "-", "_", "–"):
            out.append(key[:pos] + replacement + key[pos + 1 :])
        out.append(key[:pos] + key[pos + 1 :])
        out.append(key[:pos] + key[pos] + key[pos:])
    return out


def _axis_tokens(rng, n=2000):
    """Seeded keys with their one-edit near-misses, and bodies under every prefix variant."""
    out = []
    for _ in range(n):
        key = _invented_key(rng)
        out.append(key)
        out += _one_edit_near_misses(key)
    for _ in range(n):
        body = _invented_inchi_body(rng)
        out += [prefix + body for prefix in INCHI_PREFIX_VARIANTS]
    # The degenerate prefixes, which no generated body reaches.
    out += ["InChI=1S/", "InChI=1/", "InChI=1S/\n", "InChI=1S/\tX"]
    # LENGTH, as its own axis (gate 6, findings 2 and 4). Measured: the code-point body axis below
    # does NOT kill a body-length ceiling of 40 — bodies there are at most 30 characters — so these
    # rows are what bind length, and nothing else does.
    for _ in range(8):
        long_body = _invented_long_inchi_body(rng)
        out.append("InChI=1S/" + long_body)
        out.append("x" * 210 + " InChI=1S/" + long_body)
    return out


def _axis_contexts(rng, n=150):
    """The E-22 context alphabet, IMPORTED rather than restated, on both sides.

    One alphabet for both detectors: if E-22's grows, this axis grows with it. A second copy
    would drift, and the drift would be invisible.
    """
    tokens = [_invented_key(rng) for _ in range(n)]
    tokens += ["InChI=1S/" + _invented_inchi_body(rng) for _ in range(n)]
    return [
        left + token + right
        for token in tokens
        for left in LEFT_CONTEXTS
        for right in RIGHT_CONTEXTS
    ]


def _axis_single_code_point():
    """Every single code point on each side of each probe. CLOSED around these two tokens only."""
    for probe in (PROBE_KEY, PROBE_INCHI):
        for cp in range(0x110000):
            yield chr(cp) + probe
        for cp in range(0x110000):
            yield probe + chr(cp)


#: Printable ASCII, the alphabet the width-2 axis exhausts. Named because r2.48b's lesson is that
#: an axis must state its ALPHABET and its WIDTH, and because the limit witnesses below cite it.
_ASCII_CONTEXT = tuple(chr(c) for c in range(32, 127))


def _axis_ascii_context_pairs():
    """Every ASCII pair on each side of each probe — the axis gate 6's finding 1 needed.

    WHY PAIRS AND NOT MORE CODE POINTS. `_axis_single_code_point` appends exactly ONE character, so
    at end-of-string a width-2 lookahead always succeeds: measured, `(?![A-Z][A-Z])` scored zero
    disagreements over all 7,320,676 strings of the pre-gate corpus while making the detector miss a
    key written before two capitals. Exhausting pairs over the full code-point range is 1.2 x 10^12
    strings and impossible; exhausting them over printable ASCII is 36,100 and takes 0.1 s. So the
    axis is exhaustive in WIDTH over a stated ALPHABET rather than partial in both.

    Width 1 is already closed over ALL code points by `_axis_single_code_point`. This closes width 2
    over printable ASCII. What stays open is measured and witnessed by the two tests below, not
    guessed: a width-2 guard whose second character is NON-ASCII, and any guard of width 3 or more.
    """
    for probe in (PROBE_KEY, PROBE_INCHI):
        for left in itertools.product(_ASCII_CONTEXT, repeat=2):
            yield "".join(left) + probe
        for right in itertools.product(_ASCII_CONTEXT, repeat=2):
            yield probe + "".join(right)


#: Every NON-ASCII whitespace code point — measured, there are exactly 19. These rows replace what
#: the two deleted code-point axes were actually covering: without them the museum entry "the InChI
#: ends at ASCII whitespace only" goes unrejected, and with them it dies in 0.000 s. That is the
#: whole case for the deletion in one line — 64.2 s of axis bought one entry that 38 rows buy free.
_NON_ASCII_WHITESPACE = tuple(cp for cp in range(0x80, 0x110000) if chr(cp).isspace())


def _axis_non_ascii_whitespace():
    r"""A probe body against each non-ASCII whitespace code point, on each side.

    `\S+` and `isspace()` must agree about where a body ENDS, and the only characters where a
    reader would not guess the answer are these. Exhaustive over the class, not sampled.
    """
    for cp in _NON_ASCII_WHITESPACE:
        yield PROBE_INCHI + chr(cp) + "tail"
        yield chr(cp) + PROBE_INCHI


def _axis_fuzz(rng, n=20000):
    """Breadth only. It is NOT claimed to kill anything here.

    The earlier wording added "and measured, it does not". No shipped test attributes kills
    per axis and the harness the clause cites has no driver, so that clause rested on an
    unrecorded run. The disclaimer is kept; the evidential word is not."""
    alphabet = (
        "".join(LEFT_CONTEXTS)
        + "".join(RIGHT_CONTEXTS)
        + string.ascii_uppercase * 3
        + "--"
        + "InChI=1S/"
        + "É \t"
    )
    return ["".join(rng.choice(alphabet) for _ in range(rng.randrange(1, 70))) for _ in range(n)]


def _corpus_chunks():
    """The five axes as a stream. The seed is printed BEFORE the first string is produced."""
    print(f"\n[structure oracle] seed={SEED}", file=sys.stderr, flush=True)
    rng = random.Random(SEED)
    yield _axis_tokens(rng)
    yield _axis_contexts(rng)
    yield _axis_ascii_context_pairs()
    yield _axis_non_ascii_whitespace()
    yield _axis_fuzz(rng)
    if EXTENDED:
        yield _axis_single_code_point()


def _first_disagreement(pattern):
    """The first string where `pattern` and the reference differ, or None. Early exit by design:
    a museum entry needs ONE disagreement to be rejected, and walking 6.7M strings 17 more times
    to count them would buy nothing."""
    for chunk in _corpus_chunks():
        for text in chunk:
            got = [m.span() for m in pattern.finditer(text)]
            if got != reference_spans(text):
                return text, got, reference_spans(text)
    return None


def _first_disagreements(labelled):
    """One walk, many patterns: `{label: first disagreement or None}`.

    Every pattern here is one we expect to AGREE, so none of them exits early and each costs a full
    pass on its own — the shipped pattern plus the two limit witnesses plus the equivalence proof
    were four walks of 9.5M strings, and the file went from 99 s to 227 s when the witnesses landed.
    Walking once and carrying the patterns along costs one pass for all of them. `reference_spans` is
    computed once per string rather than once per pattern, which is where most of the saving is.

    The museum keeps its own per-entry early-exit walk: those are EXPECTED to disagree, usually in
    the first few strings, so batching them would make them slower rather than faster.
    """
    pending = dict(labelled)
    found = {}
    for chunk in _corpus_chunks():
        for text in chunk:
            if not pending:
                return found
            want = reference_spans(text)
            for label, pattern in list(pending.items()):
                if [m.span() for m in pattern.finditer(text)] != want:
                    found[label] = (text, [m.span() for m in pattern.finditer(text)], want)
                    del pending[label]
    found.update({label: None for label in pending})
    return found


#: r2.49 (a). Every axis in the DEFAULT tier, for the property test below. The extended axis is
#: excluded deliberately: it is kept to witness a signed sentence, not to reject an entry, and the
#: property test would fail it for exactly the reason it was demoted.
_DEFAULT_AXES = (
    "_axis_tokens",
    "_axis_contexts",
    "_axis_ascii_context_pairs",
    "_axis_non_ascii_whitespace",
    "_axis_fuzz",
)


#: Axes kept although they reject nothing UNIQUELY. Each entry names the DIMENSION it covers that
#: no other default axis reaches — a reason string would become a rubber stamp, a dimension can be
#: checked. Measured when this list was written; both are cheap (1.5 s combined) and both cover
#: something the cost table cannot see, which is why the property test alone would give the wrong
#: answer here.
_CARRIED_FOR_BREADTH = {
    # ascii_pairs exhausts widths 1 and 2; this is the ONLY default axis reaching width 3 or more
    # (6 left contexts and 1 right context are longer than two characters). It duplicates every
    # entry it rejects and still covers a width nothing else does.
    "_axis_contexts": "multi-character contexts, width 3+",
    # Already documented as breadth-only and claiming no kills; gate 7 measured it rejecting 0 of 21
    # mutants, which CONFIRMS the disclaimer rather than contradicting it. Kept because an
    # unanticipated mutant is the one thing an enumerated axis cannot be designed against.
    "_axis_fuzz": "random combinations no enumerated axis produces",
}


def test_every_DEFAULT_axis_uniquely_rejects_at_least_one_museum_entry():
    """r2.49 (a): an axis that rejects nothing no other axis rejects has to justify itself HERE.

    Gate 7 measured three code-point axes at 93% of the corpus, 92% of the walk cost, and ZERO
    unique rejections between them — and one of the three had been added, in the previous gate, for
    a mutant that a one-line alphabet change in the same commit had already closed. Nothing in the
    suite noticed, because nothing asked. This test asks.

    A failure is not automatically "delete the axis": it may be that the axis is carried for breadth
    against unanticipated mutants, or to witness a signed sentence. It IS a requirement to say which,
    in the clause, before the axis stays. That is the rule this range needed from the start.
    """
    import random as _random

    entries = [(label, re.compile(p)) for label, p in REGRESSION_MUSEUM]
    rejected_by = {}
    for name in _DEFAULT_AXES:
        rng = _random.Random(SEED)
        builder = globals()[name]
        chunk = builder(rng) if builder.__code__.co_argcount else builder()
        hit = set()
        for text in chunk:
            want = reference_spans(text)
            for label, pattern in entries:
                if label not in hit and [m.span() for m in pattern.finditer(text)] != want:
                    hit.add(label)
        rejected_by[name] = hit

    freeloaders = []
    for name in _DEFAULT_AXES:
        others = set().union(*(v for k, v in rejected_by.items() if k != name))
        if not (rejected_by[name] - others) and name not in _CARRIED_FOR_BREADTH:
            freeloaders.append(name)
    assert not freeloaders, (
        "these default-tier axes reject no museum entry that another axis does not already reject, "
        f"so they cost time and buy nothing measurable: {freeloaders}. Either delete them, or add "
        "them to _CARRIED_FOR_BREADTH naming the DIMENSION they cover that no other axis reaches — "
        "and if you cannot name one, that is the answer."
    )
    stale = [
        name
        for name in _CARRIED_FOR_BREADTH
        if rejected_by.get(name, set())
        - set().union(*(v for k, v in rejected_by.items() if k != name))
    ]
    assert not stale, (
        f"these axes are excused as breadth but now reject something UNIQUELY: {stale}. Remove the "
        "excuse — they earn their place on the measurement and should be held to it."
    )


def test_the_shipped_pattern_agrees_and_the_recorded_limits_hold_in_ONE_walk():
    """E-23 (c) and the limit witnesses, in a single pass over the corpus.

    THE SHIPPED PATTERN must agree everywhere in the generated corpus. THE LIMIT WITNESSES must
    still survive — they are the mutants at the edge of what the context axes close, and asserting
    that they survive is how a recorded limit stays honest instead of drifting into folklore.

    r2.48b's lesson applied: for every axis, state the alphabet and the width, and require a mutant
    at the edge of each. Measured, this is the exact boundary:

        width 1, ALL code points, AROUND THE TWO PROBE BODIES     CLOSED
                                                                  (`_axis_single_code_point`)
        width 1, ALL code points, around ANY OTHER body           COVERED, NOT CLOSED
        width 2, printable ASCII, AROUND THE TWO PROBE BODIES     CLOSED
                                                                  (`_axis_ascii_context_pairs`)
        width 2, printable ASCII, around ANY OTHER body           COVERED, NOT CLOSED
        width 2, non-ASCII second char                            OPEN — witnessed here
        width 3 or more                                           OPEN — witnessed here

    THE "AROUND ANY OTHER BODY" ROWS ARE THE CORRECTION (r2.49 (f), third recurrence). Both context
    axes vary the CONTEXT around a fixed probe body; neither varies the body. Gate 5's R05 measured
    what that leaves open: a guard that spares one exact body survives both tiers. The signed limit
    (r2.47b (1)) says CLOSED around the probes and COVERED, NOT CLOSED elsewhere, and this table
    said CLOSED without the qualifier — the third time the same overstatement has been written
    here. `body x context` is OPEN and is not claimed: exhausting it is about 10^5 x 2.2M.

    Exhausting width 2 over the full code-point range is 1.2 x 10^12 strings, so the limit is real
    rather than laziness.

    IF A WITNESS STARTS FAILING a later axis has closed it. That is an improvement: delete the
    witness and rewrite the limits above in the same commit. Do not just delete the assertion.
    """
    labelled = {"SHIPPED": _STRUCTURE_RE}
    labelled.update({label: re.compile(pattern) for label, pattern in _LIMIT_WITNESSES})
    # The dropped museum entry's corpus witness rides along here rather than walking again: it is
    # another pattern expected to agree, and its own test keeps the part its name promises, the PROOF.
    labelled[_PROVABLY_EQUIVALENT[0]] = re.compile(_PROVABLY_EQUIVALENT[1])
    outcome = _first_disagreements(labelled)

    assert outcome["SHIPPED"] is None, (
        f"the shipped structure pattern disagrees with the spec sentence (seed={SEED}); "
        f"first: {outcome['SHIPPED'][0]!r} pattern={outcome['SHIPPED'][1]} spec={outcome['SHIPPED'][2]}"
    )
    assert outcome[_PROVABLY_EQUIVALENT[0]] is None, (
        "the corpus found a counterexample to an equivalence the disjointness proof says holds — "
        "the proof is wrong. Move the entry into REGRESSION_MUSEUM and fix the reasoning."
    )
    closed = [label for label, _ in _LIMIT_WITNESSES if outcome[label] is not None]
    assert not closed, (
        f"a recorded limit is no longer real — the corpus now rejects {closed}. That is an "
        "IMPROVEMENT: remove those witnesses and rewrite the recorded limits to match what the "
        "axes now close."
    )


# ------------------------------------------------------------------------------------------- #
# E-23 (e) — THE REGRESSION MUSEUM. It INHERITS the oracle's coverage and does not extend it.
# ------------------------------------------------------------------------------------------- #
REGRESSION_MUSEUM = [
    (
        "the shipped key half: a word boundary at BOTH ends",
        r"InChI=1S?/\S+|\b[A-Z]{14}-[A-Z]{10}-[A-Z]\b",
    ),
    ("a boundary on the leading side only", r"InChI=1S?/\S+|\b[A-Z]{14}-[A-Z]{10}-[A-Z]"),
    ("a boundary on the trailing side only", r"InChI=1S?/\S+|[A-Z]{14}-[A-Z]{10}-[A-Z]\b"),
    ("a leading lookbehind", r"InChI=1S?/\S+|(?<![A-Za-z0-9])[A-Z]{14}-[A-Z]{10}-[A-Z]"),
    ("a trailing uppercase guard", r"InChI=1S?/\S+|[A-Z]{14}-[A-Z]{10}-[A-Z](?![A-Z])"),
    (
        "a one-character trailing guard outside the alphabet",
        r"InChI=1S?/\S+|[A-Z]{14}-[A-Z]{10}-[A-Z](?![;])",
    ),
    (
        "a one-character leading lookbehind outside the alphabet",
        r"InChI=1S?/\S+|(?<![;])[A-Z]{14}-[A-Z]{10}-[A-Z]",
    ),
    ("a case-insensitive key half", r"(?i:[A-Z]{14}-[A-Z]{10}-[A-Z])|InChI=1S?/\S+"),
    ("a key segment one letter short", r"InChI=1S?/\S+|[A-Z]{13}-[A-Z]{10}-[A-Z]"),
    ("a key without its final letter", r"InChI=1S?/\S+|[A-Z]{14}-[A-Z]{10}-"),
    ("the InChI requires its S", r"InChI=1S/\S+|[A-Z]{14}-[A-Z]{10}-[A-Z]"),
    ("the InChI body may be empty", r"InChI=1S?/\S*|[A-Z]{14}-[A-Z]{10}-[A-Z]"),
    ("the InChI stops at the next slash", r"InChI=1S?/[^\s/]+|[A-Z]{14}-[A-Z]{10}-[A-Z]"),
    ("a case-insensitive InChI prefix", r"(?i:InChI=1S?/)\S+|[A-Z]{14}-[A-Z]{10}-[A-Z]"),
    (
        "the InChI ends at ASCII whitespace only",
        r"InChI=1S?/[^ \t\n\r\f\v]+|[A-Z]{14}-[A-Z]{10}-[A-Z]",
    ),
    ("the key half anchored to a line", r"InChI=1S?/\S+|^[A-Z]{14}-[A-Z]{10}-[A-Z]$"),
    # ADDED after gate 6. Each of these survived the whole suite before the axes above existed;
    # they are here so the new coverage is PINNED rather than incidental to a generator's alphabet.
    ("the InChI body may not start uppercase", r"InChI=1S?/(?![A-Z])\S+|[A-Z]{14}-[A-Z]{10}-[A-Z]"),
    ("a length ceiling on the InChI body", r"InChI=1S?/\S{1,40}|[A-Z]{14}-[A-Z]{10}-[A-Z]"),
    # ADDED after gate 6 finding 1. Both scored ZERO disagreements before the width-2 axis existed.
    ("a WIDTH-2 trailing guard", r"InChI=1S?/\S+|[A-Z]{14}-[A-Z]{10}-[A-Z](?![A-Z][A-Z])"),
    ("a WIDTH-2 leading guard", r"InChI=1S?/\S+|(?<![A-Z][A-Z])[A-Z]{14}-[A-Z]{10}-[A-Z]"),
]

#: Guards the corpus does NOT reject, kept as WITNESSES rather than hidden. Each one is the mutant
#: at the edge of a stated limit, and `test_the_recorded_context_limits_are_REAL` asserts that it
#: still survives. That is deliberate and it is not a museum entry: if a later axis kills one of
#: these, that test fails and forces the RECORDED LIMIT above it to be rewritten in the same commit.
#: A limit nobody has measured drifts into a limit nobody believes.
_LIMIT_WITNESSES = [
    (
        "width 2 with a NON-ASCII second character",
        "InChI=1S?/" + chr(92) + "S+|[A-Z]{14}-[A-Z]{10}-[A-Z](?![A-Z]" + chr(0xB5) + ")",
    ),
    (
        "width 3 over ASCII",
        "InChI=1S?/" + chr(92) + "S+|[A-Z]{14}-[A-Z]{10}-[A-Z](?![A-Z][A-Z][A-Z])",
    ),
]

#: DROPPED, with the reason, rather than left in the list as a known survivor. Swapping the
#: alternation cannot change any match: an InChI's second character is lowercase `n`, and every
#: character of a key's first segment is ASCII uppercase, so the two branches can never both
#: match at one position. It is PROVABLY EQUIVALENT, not merely unkilled — and a museum that
#: keeps an entry no corpus can reject teaches the reader the wrong thing about the corpus.
_PROVABLY_EQUIVALENT = ("the alternation order swapped", r"[A-Z]{14}-[A-Z]{10}-[A-Z]|InChI=1S?/\S+")


def _regex_parser():
    """`re._parser` (3.11+), else the older `sre_parse`. Private, deliberately.

    Reading the pattern's own parse tree is the only way to derive what it admits WITHOUT
    restating it, and restating is what r2.49 (f) is fixing. If the private API moves, these
    tests fail loudly rather than quietly reverting to a literal.
    """
    parser = getattr(re, "_parser", None)
    if parser is None:  # pragma: no cover - only on interpreters older than 3.11
        import sre_parse as parser
    return parser


def _alternation_branches(pattern: str) -> list[str]:
    """The top-level `|` branches of `pattern`, as source strings, read from its parse tree.

    Splitting on `|` textually would be wrong the moment a branch contains an alternation inside a
    group or a literal bar in a character class.
    """
    parsed = _regex_parser().parse(pattern)
    nodes = list(parsed)
    if len(nodes) == 1 and str(nodes[0][0]) == "BRANCH":
        _, branches = nodes[0][1]
        # `re` offers no unparser, so recover each branch's source by matching it back against the
        # pattern text: the branches partition the top level, so splitting on the bars that the
        # parse tree says are top-level is safe. Verify by re-parsing each piece.
        pieces = pattern.split("|")
        if len(pieces) == len(branches):
            for piece in pieces:
                _regex_parser().parse(piece)  # raises if a piece is not a valid pattern on its own
            return pieces
        raise AssertionError(
            f"the pattern has {len(branches)} top-level branches but splits into {len(pieces)} on "
            "'|', so a bar is nested; this helper does not handle that and must not guess."
        )
    return [pattern]


# r2.50a mechanism (4): a derivation consumes the WHOLE artefact -- pattern AND flags -- or it
# asserts the flags it assumes. Gate 8 (C-3, found independently by the code reviewer and by me)
# found the equivalence proof deriving from `.pattern` alone, 640 lines after this same file says
# that "an IGNORECASE compile has an identical `.pattern`". Measured: the shipped object carries
# flags 32 (UNICODE); the same text compiled with IGNORECASE carries 34 and an IDENTICAL pattern
# string. Under IGNORECASE the key branch's `[A-Z]{14}` admits lowercase, the two branches stop
# being disjoint at index 1, and the proof would report an equivalence the artefact does not have.
#
# `_characters_at` reads character classes literally, so it is sound only under flags that do not
# change what a class admits. UNICODE is the default for str patterns and changes nothing here.
_DERIVABLE_FLAGS = re.UNICODE


def _assert_flags_are_derivable(compiled: "re.Pattern[str]", what: str) -> None:
    """Refuse to derive from a compiled object whose flags this helper cannot model.

    Refusing is the honest answer; deriving anyway would hand back a set that looks like evidence
    and is not -- the same failure as H-1, one level up.
    """
    extra = compiled.flags & ~_DERIVABLE_FLAGS
    if extra:
        raise AssertionError(
            f"{what} is compiled with flags this derivation cannot model: "
            f"{re.RegexFlag(extra)!r}. Character classes are read literally here, so a flag that "
            "changes what a class admits (IGNORECASE above all) would make every derived set "
            "wrong while the pattern TEXT stayed identical. Extend the derivation deliberately or "
            "keep the flag off the shipped object."
        )


def _characters_at(pattern: str, index: int) -> set[str]:
    """Every character that can stand at `index` of a match for `pattern`.

    Derived from the parse tree, and DELIBERATELY INCOMPLETE: it understands literals, character
    classes, and fixed-count repeats of either, and RAISES on anything else. A helper that guessed
    at a construct it did not understand would hand back a set that looks like evidence and is not
    -- which is precisely the failure being corrected here.
    """
    position = 0
    for op, arg in _regex_parser().parse(pattern):
        name = str(op)
        if name == "LITERAL":
            if position == index:
                return {chr(arg)}
            position += 1
        elif name == "IN":
            if position == index:
                return _class_characters(arg)
            position += 1
        elif name == "MAX_REPEAT":
            low, high, sub = arg
            if low != high:
                raise AssertionError(
                    f"a variable-length repeat {(low, high)} stands before index {index} in "
                    f"{pattern!r}, so the character at that index is not determined by the prefix. "
                    "This proof cannot be derived and must not be faked."
                )
            inner = list(sub)
            if len(inner) != 1:
                raise AssertionError(f"unsupported multi-node repeat body in {pattern!r}")
            inner_op, inner_arg = inner[0]
            inner_name = str(inner_op)
            # r2.50a mechanism (3), gate-8 H-1: this check used to sit INSIDE `position == index`,
            # so an unsupported body raised only when the index landed on it and otherwise
            # advanced `position` by one however many characters the body consumed. A counted
            # capturing group then shifted every later index and the helper returned a wrong set
            # -- silently, which its own docstring forbids. The refusal must not depend on which
            # index is being asked for, so it is made before any position is advanced.
            if inner_name not in {"IN", "LITERAL"}:
                raise AssertionError(
                    f"unsupported repeat body {inner_name} in {pattern!r}: its width is not known "
                    "to this helper, so no index after it can be derived either. Extend the helper "
                    "deliberately rather than letting the proof degrade into a guess."
                )
            # Both supported bodies consume exactly one character, which is what makes the
            # single-step advance below correct.
            for _ in range(low):
                if position == index:
                    if inner_name == "IN":
                        return _class_characters(inner_arg)
                    return {chr(inner_arg)}
                position += 1
        else:
            raise AssertionError(
                f"unsupported regex construct {name} before index {index} in {pattern!r}. Extend "
                "this helper deliberately rather than letting the proof degrade into a guess."
            )
    raise AssertionError(f"{pattern!r} has no determined character at index {index}")


def _class_characters(items) -> set[str]:
    """The characters of a parsed character class. Raises on categories such as `\\S`."""
    out: set[str] = set()
    for op, arg in items:
        name = str(op)
        if name == "RANGE":
            low, high = arg
            out.update(chr(c) for c in range(low, high + 1))
        elif name == "LITERAL":
            out.add(chr(arg))
        else:
            raise AssertionError(
                f"unsupported character-class item {name}; this helper must not guess what a "
                "category admits."
            )
    return out


def test_the_oracle_REJECTS_every_entry_in_the_structure_museum():
    """Rule 3b: an oracle nobody has seen fail is not evidence. These patterns are known-wrong."""
    survived = [
        label
        for label, pattern in REGRESSION_MUSEUM
        if _first_disagreement(re.compile(pattern)) is None
    ]
    assert not survived, (
        "these structure patterns are known-wrong and the oracle did not reject them, so it no "
        "longer binds: " + ", ".join(survived)
    )


def test_the_dropped_museum_entry_is_equivalent_BY_PROOF_not_by_absence_of_a_counterexample():
    """Why the swapped alternation may be dropped rather than kept as a known survivor.

    CORRECTED after gate 6. This test used to assert only `_first_disagreement(...) is None` under
    the name "...really IS equivalent and not merely unkilled" — which is the definition of MERELY
    UNKILLED, the very status the comment above refuses to accept as equivalence. The docstring
    stated a real proof and the body checked something weaker. Two reviewers found it
    independently, and they were right: a corpus that finds no counterexample is not a proof.

    The proof, now rendered as an assertion. Alternation order can only matter where two branches
    can both match AT THE SAME POSITION. The InChI branch requires its second character to be
    lowercase `n`; the key branch requires its first fourteen characters to be ASCII uppercase, so
    its second character is uppercase. No character is both, so no position admits both branches,
    so the order is unobservable — for EVERY input, not merely for this corpus.

    The corpus check is kept as a second, weaker witness, and it runs in the single-walk test above
    rather than here: if it ever fails, the proof below is wrong and the entry belongs in
    `REGRESSION_MUSEUM`.
    """
    _, pattern = _PROVABLY_EQUIVALENT
    assert re.compile(pattern).pattern != _STRUCTURE_RE.pattern, "the entry must differ in TEXT"

    # THE PROOF NOW READS THE ARTEFACTS (r2.49 (f)). It used to compare `_INCHI_PREFIX[1]` with
    # `string.ascii_uppercase` -- two TEST-SIDE literals. Neither is production's pattern, so the
    # assertion held no matter what the shipped pattern said: widen the key branch to `[A-Za-z]{14}`
    # in production and this "proof" went on passing while its conclusion became false. A proof that
    # cannot notice the thing it is about is the same defect as a corpus that finds no
    # counterexample, one level up.
    # r2.50a mechanism (4): consume the compiled object, not just its text. Both sides are
    # checked -- the shipped object AND the museum entry's compile -- because either carrying a
    # flag this derivation cannot model invalidates the conclusion, not just the shipped one.
    _assert_flags_are_derivable(_STRUCTURE_RE, "the shipped structure pattern")
    _assert_flags_are_derivable(re.compile(pattern), "the museum entry under proof")

    shipped_branches = _alternation_branches(_STRUCTURE_RE.pattern)
    swapped_branches = _alternation_branches(pattern)
    assert len(shipped_branches) == len(swapped_branches) == 2, (
        "the proof is written for a two-branch alternation; the patterns now have "
        f"{len(shipped_branches)} and {len(swapped_branches)} branches, so it no longer applies."
    )
    assert sorted(shipped_branches) == sorted(swapped_branches), (
        "the swapped entry is no longer a REORDERING of the shipped pattern's branches, so "
        "alternation order is not the only difference and this proof does not cover it."
    )

    first, second = (_characters_at(branch, 1) for branch in shipped_branches)
    assert first and second, "a branch admitted no character at index 1; the derivation is wrong"
    assert first.isdisjoint(second), (
        f"the equivalence proof has FAILED: {sorted(first & second)[:8]!r} can stand at index 1 of "
        "BOTH branches, so some position admits both, alternation order becomes observable, and "
        "the swapped pattern is a real museum entry rather than an equivalent one. Move it into "
        "REGRESSION_MUSEUM."
    )

    # The corpus witness for this entry rides in the single-walk test above; repeating it here
    # cost a second full pass over 9.5M strings for the same answer.


# ------------------------------------------------------------------------------------------- #
# E-23 (d) — THE CALL SITE, driven through a no-disk seam.
#
# The pin and the oracle both bind a CONSTANT. Gate 5's R06 measured why that is not enough: a
# filter at the call site is invisible to both. `accession_structure_tuples` takes a STRING, so
# the seam needs no disk at all — generated documents go straight in.
#
# ONE STRUCTURE PER DOCUMENT WAS THE ORIGINAL DESIGN, and it was wrong. The reasoning was that
# since the call site reports `near[0]`, a document with several structures cannot tell us which one
# it saw — so keeping one per document made the observation unambiguous. It also made four wrong
# call sites INDISTINGUISHABLE: naming the last nearby structure instead of the first, reporting only
# the first accession on a line, deduplicating on the accession alone, and taking one structure per
# line all produce identical output on a document that has one of each. Measured: all four survived
# the rebuilt full-tuple comparison until the documents below existed.
#
# The ambiguity that justified it is gone, and the rebuild is what removed it: `reference_associations`
# renders the same rule from its sentence, so for a multi-structure document there IS a stated right
# answer to compare against. The richer documents became possible the moment the expectation stopped
# being derived from the call site.
#
# THE ACCESSION SITS ON THE NEXT LINE, so the window is exercised too: a call site that stopped
# looking across lines would report nothing and this axis would fail.
#
# WHAT THIS AXIS DOES NOT DO, measured rather than assumed. It is 96,900 documents built from the
# E-22 context alphabet, and it binds the CALL SITE, not the pattern. Measured against mutants:
# the old key half with a word boundary at both ends gives 26,400 disagreements and dies here,
# but a one-character trailing guard over a character OUTSIDE that alphabet gives 0 and SURVIVES
# this axis. What rejects that one is the code-point axes above, and the museum entry that pins
# it. Written down so this axis is not read as wider than it is.
# ------------------------------------------------------------------------------------------- #
#: The documented probe body: shape-valid, all zeros, deliberately unassigned. Assembled from
#: fragments because this file is not accession-excluded (`test_record_content_guard.py:68-75`).
#: Column positions the seam axis reaches. A call-site column ceiling BELOW the longer of these is
#: visible; one ABOVE it is not, and that limit is witnessed rather than assumed (see
#: `_CALL_SITE_LIMIT_WITNESSES`). 240 is just past the 200 the gate-6 mutant used; 2,048 is past any
#: line a hand-maintained ledger plausibly carries.
_SEAM_COLUMN_PAD = 240
_SEAM_LONGEST_LINE = 2048

PROBE_ACCESSION = "DB" + "0" * 5


def _seam_documents(rng, n=120):
    """Generated documents. DOCUMENTS ONLY — the expectation is derived separately, on purpose.

    Until the gate-6 rebuild this returned `(text, reference_spans(first_line))`: the structure
    reference evaluated on the line the CALL SITE had split off. That put the call site's own line
    splitting inside its expectation, so the one decision the reference did not share was the decision
    the expectation matched by construction. Measured: 0 of 96,900 documents could distinguish
    `splitlines()` from splitting on LF, and five further call-site mutants survived for the same
    reason. The expectation now comes from `reference_associations`, which reads the whole document
    and derives its own lines.
    """
    tokens = [_invented_key(rng) for _ in range(n)]
    tokens += ["InChI=1S/" + _invented_inchi_body(rng) for _ in range(n)]
    tokens += [_invented_key(rng)[:-1] for _ in range(n // 2)]  # near-misses: expect NOTHING
    out = []
    for token in tokens:
        for left in LEFT_CONTEXTS:
            for right in RIGHT_CONTEXTS:
                first = left + token + right
                if "\n" in first:  # a context may carry a newline; keep the doc two lines
                    continue
                out.append(first + "\n" + "carrier " + PROBE_ACCESSION)
    # LONG FIRST LINES (gate 6, finding 2). Measured: a call site scanning only `line[:200]` was
    # INDISTINGUISHABLE from production over this axis, because its longest first line was 49
    # characters. A column ceiling is invisible to any corpus whose lines are shorter than it, so
    # line LENGTH is an axis dimension in its own right — the same lesson as the InChI body's length.
    # `_SEAM_LONGEST_LINE` is the number the limit below is stated against, so it is named once.
    for token in tokens[:: max(1, len(tokens) // 8)]:
        for pad in (_SEAM_COLUMN_PAD, _SEAM_LONGEST_LINE):
            first = "x" * pad + " " + token
            out.append(first + "\n" + "carrier " + PROBE_ACCESSION)
    out += _distinguishing_documents(tokens)
    return out


def _distinguishing_documents(tokens):
    """Documents whose SHAPE can tell the call site's choices apart, one family per wrong behaviour.

    Each family exists because a specific mutant was measured to survive without it. A corpus of
    one-structure, one-accession documents cannot observe which structure is named or how accessions
    are deduplicated, so these are not extra breadth — they are the only rows that see four of the
    six entries in `_CALL_SITE_MUSEUM`.
    """
    keys = [t for t in tokens if "InChI" not in t][:4]
    inchis = [t for t in tokens if "InChI" in t][:4]
    if not keys or not inchis:  # pragma: no cover - the generators always produce both
        return []
    second = "DB" + "0" * 4 + "1"  # INVENTED: a second shape-valid probe, one digit from the first
    out = []
    for key, inchi in zip(keys, inchis, strict=False):
        # TWO structures on DIFFERENT lines inside the window, accession between them: the only shape
        # that can see `near[0]` become `near[-1]`.
        out.append(f"{key}\ncarrier {PROBE_ACCESSION}\n{inchi}")
        # TWO structures on ONE line: sees "one structure per line".
        out.append(f"{key} {inchi}\ncarrier {PROBE_ACCESSION}")
        # TWO accessions on ONE line beside a structure: sees "first accession only".
        out.append(f"{key}\n{PROBE_ACCESSION} and {second}")
        # The SAME accession on two lines, each within the window: sees dedup on the accession alone
        # rather than on (line, accession).
        out.append(f"{PROBE_ACCESSION}\n{key}\n{PROBE_ACCESSION}")
        # Both at once, so a mutant cannot pass by getting one family right.
        out.append(f"{key} {inchi}\n{PROBE_ACCESSION} and {second}\n{PROBE_ACCESSION}")
    out += _clause_documents()
    return out


#: r2.49 (b). THREE CLAUSES A DIFFERENTIAL CANNOT SEE, bound by construction instead.
#: Gate 7 measured each surviving the whole suite because production, the spec sentence and the
#: reference all state the clause IDENTICALLY — a differential is blind to a clause on which its two
#: sides agree by construction, however large the corpus. 9,585,016 generated strings could not see
#: any of these; three documents can.
def _clause_documents():
    """One document per clause, each measured to distinguish the reading the clause rules out."""
    key, inchi = PROBE_KEY, PROBE_INCHI
    return [
        # "each (line, accession) pair is reported at most once" — the same accession twice on ONE
        # line. Measured: 0 of 96,938 corpus documents did this, so no-dedup-at-all was invisible.
        f"{key}\n{PROBE_ACCESSION} and {PROBE_ACCESSION}",
        # no whole-document bound — the pair at the END of a long document. Measured: the corpus's
        # longest document was 2,102 bytes and 3 lines, while the exempt ledger is 8,033 bytes and
        # 192 lines, so every plausible cap sat above the corpus and below the real file.
        "\n".join(f"filler line {i}" for i in range(400)) + f"\n{key}\ncarrier {PROBE_ACCESSION}",
        # "the FIRST in document order" — two in-window structures at DIFFERENT distances, the
        # NEARER one later. Measured: 0 corpus documents separated the distances, so first-in-order
        # and nearest-wins were indistinguishable even though a museum entry existed for pick=-1.
        f"{key}\n{inchi}\ncarrier {PROBE_ACCESSION}",
        # the window's UPPER edge — a structure exactly ONE LINE OUTSIDE the window, which the clause
        # says is not an association. Importing `_TUPLE_WINDOW` (above) stops the two sides silently
        # restating DIFFERENT values, but it does not let the corpus SEE a call site that uses a
        # wider one: measured, windows 3, 4 and 8 all gave 0 disagreements because the tallest
        # document was 3 lines. Those are two different properties and only the first was in (c).
        # Measured with this row: window 2 agrees, windows 3 and 4 DISAGREE.
        key + ("\nfiller" * _TUPLE_WINDOW) + f"\ncarrier {PROBE_ACCESSION}",
    ]


def _call_site_variant(
    text,
    *,
    window=2,
    column_limit=None,
    pick=0,
    first_accession_only=False,
    dedup_on_accession_only=False,
    one_structure_per_line=False,
    dedup=True,
    byte_limit=None,
    line_limit=None,
):
    """The call site's algorithm, parameterised so a WRONG version of it can be exercised.

    A reimplementation is a risk: it can drift from production and then the museum tests something
    that no longer exists. `test_the_call_site_museum_has_not_DRIFTED_from_production` is the guard —
    it runs this with every knob at its production setting and requires agreement with the real
    `accession_structure_tuples` over the whole seam axis. If production changes, that test fails
    first and says so, rather than the museum silently testing a fossil.

    The knobs are exactly the wrong behaviours gate 6 found surviving, one per finding.
    """
    # r2.49 (c): the window comes from PRODUCTION, never from a literal restated here. Gate 7
    # measured that a restated constant is a drift channel nothing checks.
    if window is None:
        window = _TUPLE_WINDOW
    lines = text.splitlines()
    if byte_limit is not None and len(text) > byte_limit:
        lines = []
    if line_limit is not None and len(lines) > line_limit:
        lines = []
    structures = []
    for i, line in enumerate(lines):
        scanned = line if column_limit is None else line[:column_limit]
        matches = list(_STRUCTURE_RE.finditer(scanned))
        if one_structure_per_line:
            matches = matches[:1]
        structures += [(i, m.group(0)) for m in matches]
    found, seen = [], set()
    for i, line in enumerate(lines):
        accessions = list(REAL_ACCESSION_RE.finditer(line))
        if first_accession_only:
            accessions = accessions[:1]
        for match in accessions:
            near = [st for j, st in structures if abs(j - i) <= window]
            if pick == "nearest":  # r2.49 (b): the reading the clause does NOT specify
                near = [
                    st
                    for _, st in sorted(
                        ((abs(j - i), st) for j, st in structures if abs(j - i) <= window),
                        key=lambda pair: pair[0],
                    )
                ]
            token = match.group(0)
            key = token if dedup_on_accession_only else (i, token)
            if near and (not dedup or key not in seen):
                seen.add(key)
                found.append((i + 1, token, near[0 if pick == "nearest" else pick]))
    return found


#: WRONG call-site behaviours, each measured to survive the pre-gate seam axis. The pin and the
#: pattern oracle cannot see any of them: they change the ARGUMENTS and the bookkeeping, not the
#: pattern. Finding 2 is the column ceiling; the rest are the five the test reviewer found beside it
#: and are closed by the (d) rebuild.
_CALL_SITE_MUSEUM = [
    ("a column ceiling at 200", {"column_limit": 200}),
    ("a column ceiling at 1024", {"column_limit": 1024}),
    # The five gate 6 found beside the ceiling. Every one survived the OLD axis, whose expectation was
    # one structure per document compared on its third element only; full tuple equality against an
    # independent reference is what makes them visible.
    ("it names the LAST nearby structure, not the first", {"pick": -1}),
    ("it reports only the first accession on a line", {"first_accession_only": True}),
    ("it deduplicates on the accession alone", {"dedup_on_accession_only": True}),
    ("the window is closed to a single line", {"window": 0}),
    ("the window is WIDENED past the clause", {"window": _TUPLE_WINDOW + 1}),
    # r2.49 (b). Each of these survived gate 7's entire suite; each is now rejected by exactly one
    # of the three constructed documents above, and by nothing else in the corpus.
    ("the (line, accession) dedup removed entirely", {"dedup": False}),
    ("a whole-document byte cap", {"byte_limit": 4096}),
    ("a whole-document line cap", {"line_limit": 8}),
    ("the NEAREST structure wins, not the first in document order", {"pick": "nearest"}),
]

#: RETIRED BY PROOF, not kept as a survivor. `near[0]` is the EARLIEST structure in document order
#: within the window, and dropping the non-first matches ON A LINE can never change which is
#: earliest: every match on a line shares one line index and therefore one window distance. So the
#: output of `accession_structure_tuples` is identical, for every input, not merely for this corpus.
#:
#: A gate-6 reviewer listed this among the surviving mutants. It was a hypothesis until measured, and
#: measuring it moved it here rather than into the museum.
#:
#: THE EQUIVALENCE IS CONTINGENT on the call site naming ONE structure per (line, accession). If it
#: ever reports more than one, this becomes observable and belongs back in `_CALL_SITE_MUSEUM`.
_CALL_SITE_PROVABLY_EQUIVALENT = (
    "it takes only one structure per line",
    {"one_structure_per_line": True},
)


def _measured_longest_line() -> int:
    """The axis's longest line, REGENERATED from the corpus (r2.49 (f)).

    The limit used to be stated against `_SEAM_LONGEST_LINE`, which is the PAD, not a line: the
    longest line is the pad plus a separator plus a token. Measured, the difference is 38
    characters, and that gap is not cosmetic -- it made the axis claim to be blind to ceilings it
    actually closes. A number that is TYPED drifts silently from the thing it describes; a number
    that is regenerated cannot.
    """
    return max(
        len(line) for text in _seam_documents(random.Random(SEED)) for line in text.split("\n")
    )


#: The first column ceiling the seam axis genuinely CANNOT see: the axis exercises lines up to
#: `_measured_longest_line()` characters, so a ceiling at that width or above truncates nothing it
#: generates. Recorded here for the witness label and CHECKED against the regenerated corpus by
#: `test_the_recorded_column_limit_is_MEASURED_not_TYPED`, which fails if the two ever part company.
_SEAM_FIRST_INVISIBLE_COLUMN = 2086

#: Call-site limits the seam axis does NOT close, kept as witnesses for the same reason the pattern
#: axis keeps its own: a ceiling ABOVE the longest line in the corpus cannot be seen by it.
#:
#: CORRECTED (r2.49 (f)). The label used to name `_SEAM_LONGEST_LINE` (2048) as "the axis's longest
#: line". It is the pad. Measured, ceilings across [2049, 2085] are CLOSED by this axis and were
#: being reported as open -- a limit recorded as wider than it really is, which is this workstream's
#: defect family pointed at its own limit record. The first genuinely invisible ceiling is 2,086.
_CALL_SITE_LIMIT_WITNESSES = [
    (
        (
            "a column ceiling at or above the axis's longest LINE "
            f"({_SEAM_FIRST_INVISIBLE_COLUMN}; the pad is {_SEAM_LONGEST_LINE}, and "
            f"[{_SEAM_LONGEST_LINE + 1}, {_SEAM_FIRST_INVISIBLE_COLUMN - 1}] are CLOSED, not open)"
        ),
        {"column_limit": _SEAM_FIRST_INVISIBLE_COLUMN},
    ),
]


def _seam_disagreements(**kwargs):
    """Documents where a variant call site differs from the INDEPENDENT reference. Early exit.

    Full tuple equality, not "one tuple whose third element matches": the old shape could not see
    which structure was named, how accessions were deduplicated, or how many were reported, which is
    why five call-site mutants survived it.
    """
    rng = random.Random(SEED)
    for text in _seam_documents(rng):
        if _call_site_variant(text, **kwargs) != reference_associations(text):
            return text
    return None


def test_the_three_clauses_a_DIFFERENTIAL_CANNOT_SEE_are_bound_by_construction():
    """r2.49 (b). Full tuple equality on three documents, one per clause.

    WHY THESE ARE NOT LEFT TO THE CORPUS. A differential compares production against a reference; it
    is blind to any clause on which the two agree by construction, and it stays blind however large
    the corpus grows. Gate 7 measured exactly that: the dedup clause, the absence of a document
    bound, and "the first in document order" each survived 9,585,016 strings, because production,
    the signed sentence and `association_reference` all say the same thing and nothing outside that
    triangle checked it. Adding axes could never have found them. Three documents do.

    Each document is also in the seam corpus, so the matching mutant is rejected by the museum too —
    the assertion here says WHICH clause each document pins, which a corpus walk cannot say.
    """
    from chipsim.ingest.drugbank_snapshot import accession_structure_tuples

    dedup_doc, long_doc, order_doc, window_doc = _clause_documents()

    assert accession_structure_tuples(dedup_doc) == reference_associations(dedup_doc)
    assert len(accession_structure_tuples(dedup_doc)) == 1, (
        "the same accession twice on ONE line must be reported once — the clause says each "
        "(line, accession) pair is reported at most once"
    )

    assert accession_structure_tuples(long_doc) == reference_associations(long_doc)
    assert len(accession_structure_tuples(long_doc)) == 1, (
        f"a pair at the end of a {len(long_doc)}-byte, {len(long_doc.splitlines())}-line document "
        "must still be found — the clause states no whole-document bound, and the exempt ledger is "
        "larger than this"
    )

    tuples = accession_structure_tuples(order_doc)
    assert tuples == reference_associations(order_doc)
    assert tuples and tuples[0][2] == PROBE_KEY, (
        "with two in-window structures at DIFFERENT distances, the clause names the FIRST in "
        "document order — here the more distant one. Naming the nearer is a different rule that no "
        "corpus in this file can distinguish."
    )

    assert accession_structure_tuples(window_doc) == reference_associations(window_doc)
    assert accession_structure_tuples(window_doc) == [], (
        f"a structure exactly {_TUPLE_WINDOW + 1} lines away — one past the window — is NOT an "
        "association. Importing the window stops the two sides restating different values; this row "
        "is what lets the corpus see a call site that WIDENS it, which the import alone does not."
    )


def test_the_call_site_museum_has_not_DRIFTED_from_production():
    """The anti-drift guard for the reimplementation above — it must equal production exactly.

    Without this the museum could test a call site the project no longer has, and every entry would
    keep passing while proving nothing about the shipped code. This is the same failure the (d) axis
    had in a different form: machinery that agrees with itself.
    """
    from chipsim.ingest.drugbank_snapshot import accession_structure_tuples

    rng = random.Random(SEED)
    for text in _seam_documents(rng):
        assert _call_site_variant(text) == accession_structure_tuples(text), (
            "the parameterised call site no longer matches production, so every museum entry below "
            f"it is testing a fossil. Re-derive it from the current call site. Document: {text!r}"
        )


def test_the_seam_axis_REJECTS_every_wrong_call_site_in_the_museum():
    """Rule 3b for the call-site axis, which gate 6 measured as having none of its own."""
    survived = [
        label for label, kwargs in _CALL_SITE_MUSEUM if _seam_disagreements(**kwargs) is None
    ]
    assert not survived, (
        "these call-site behaviours are known wrong and the seam axis did not reject them: "
        + ", ".join(survived)
    )


def test_the_one_structure_per_line_variant_is_equivalent_BY_PROOF():
    """Why it is retired rather than kept as a survivor, checked rather than asserted.

    The proof: `near[0]` is the earliest structure in document order within the window, and every
    match on a line shares that line's index, hence its distance. Dropping the non-first matches on a
    line therefore cannot change which structure is earliest-within-window, so the reported tuple is
    unchanged for EVERY input.

    Rendered as two assertions: the contingency the proof rests on (one structure named per tuple),
    and the equivalence itself over documents built to expose it if the proof were wrong.
    """
    _, kwargs = _CALL_SITE_PROVABLY_EQUIVALENT
    multi = [
        f"{PROBE_KEY} {PROBE_INCHI}\ncarrier {PROBE_ACCESSION}",
        f"carrier {PROBE_ACCESSION}\n{PROBE_KEY} {PROBE_INCHI}",
        f"{PROBE_KEY} {PROBE_INCHI} {PROBE_KEY}\ncarrier {PROBE_ACCESSION}",
        f"{PROBE_KEY} {PROBE_INCHI}\ncarrier {PROBE_ACCESSION}\n{PROBE_INCHI} {PROBE_KEY}",
    ]
    for text in multi:
        tuples = _call_site_variant(text)
        assert all(len(row) == 3 for row in tuples), (
            "the proof rests on each tuple naming exactly ONE structure; if the call site now reports "
            "several, this variant becomes observable and belongs back in _CALL_SITE_MUSEUM"
        )
        assert tuples == _call_site_variant(text, **kwargs), (
            "dropping the non-first structures on a line CHANGED the output, so the equivalence proof "
            f"is wrong. Move it back into _CALL_SITE_MUSEUM. Document: {text!r}"
        )


def test_the_recorded_call_site_limits_are_REAL():
    """The mutant at the EDGE of the seam axis — asserted to survive, on purpose.

    A column ceiling is invisible to any corpus whose lines are all shorter than it, so the axis
    closes ceilings below its longest line and nothing above. Stated, witnessed, and rewritten in the
    same commit as any axis that closes it — same contract as the pattern-side witnesses.
    """
    still_open = [
        label
        for label, kwargs in _CALL_SITE_LIMIT_WITNESSES
        if _seam_disagreements(**kwargs) is None
    ]
    assert still_open == [label for label, _ in _CALL_SITE_LIMIT_WITNESSES], (
        "a recorded call-site limit is no longer real. That is an IMPROVEMENT: remove the witness "
        "and rewrite the limit it recorded."
    )


def test_the_recorded_column_limit_is_MEASURED_not_TYPED():
    """r2.49 (f). The recorded boundary must equal the corpus the axis actually generates.

    This is the test that would have caught the defect it was written for. The limit was stated
    against `_SEAM_LONGEST_LINE`, the PAD, while the longest LINE is the pad plus a separator plus a
    token -- 38 characters more. So the axis advertised itself as blind to ceilings from 2,049
    upward when it in fact closes everything below 2,086. A typed number drifts from the thing it
    describes and nothing notices; a regenerated one cannot.
    """
    measured = _measured_longest_line()
    assert _SEAM_FIRST_INVISIBLE_COLUMN == measured, (
        f"the recorded first-invisible column ({_SEAM_FIRST_INVISIBLE_COLUMN}) is not the corpus's "
        f"longest line ({measured}). Regenerate the number and rewrite the witness label in the "
        "same commit -- do not retype it."
    )
    assert measured > _SEAM_LONGEST_LINE, (
        "the longest LINE must exceed the PAD; if it does not, the corpus no longer appends a token "
        "to the padded line and the whole column axis has stopped testing what it claims to."
    )


@pytest.mark.parametrize(
    "ceiling",
    [
        pytest.param(_SEAM_LONGEST_LINE, id="at-the-pad-2048"),
        pytest.param(_SEAM_LONGEST_LINE + 1, id="just-above-the-pad-2049"),
        pytest.param(_SEAM_FIRST_INVISIBLE_COLUMN - 1, id="last-closed-2085"),
    ],
)
def test_the_band_ABOVE_THE_PAD_and_below_the_longest_line_is_CLOSED(ceiling):
    """The band that was mis-recorded as open, asserted closed one ceiling at a time.

    [pad + 1, longest_line - 1] was reported as beyond the axis because the limit named the pad.
    Each ceiling here must be VISIBLE to the axis -- that is what "closed" means: a call site
    truncating at this column disagrees with the reference on some generated document, so the axis
    would reject it.
    """
    assert _seam_disagreements(column_limit=ceiling) is not None, (
        f"a column ceiling at {ceiling} is NOT closed by this axis after all, so the recorded band "
        "[pad+1, longest-1] is wrong in the other direction. Re-measure and rewrite the record."
    )


def test_the_CALL_SITE_agrees_with_the_INDEPENDENT_association_reference():
    """E-23 (d), rebuilt. The expectation comes from a reference the call site cannot influence.

    Full tuple equality against `reference_associations`, which reads the whole document and derives
    its own line numbers from line feeds. Measured after the rebuild: the reference agrees with
    production on all 96,918 LF-only documents in this axis, and DISAGREES on a document whose
    accession and structure sit on one physical line separated by non-LF break characters — the
    registered gate-6 finding, which this axis could not see before and now can. That case is carried
    by `test_the_splitlines_line_definition_DIVERGES_from_the_sentence` below.
    """
    from chipsim.ingest.drugbank_snapshot import accession_structure_tuples

    rng = random.Random(SEED)
    wrong = []
    for text in _seam_documents(rng):
        got = accession_structure_tuples(text)
        want = reference_associations(text)
        if got != want:
            wrong.append((text, got, want))
    assert not wrong, (
        f"the call site and the association reference disagree on {len(wrong)} of the generated "
        f"documents (seed={SEED}); first: text={wrong[0][0]!r} call-site={wrong[0][1]} "
        f"reference={wrong[0][2]}"
    )


#: Every code point `str.splitlines()` breaks on EXCEPT line feed itself. r2.49 (f) PARAMETRISES
#: the xfail over all of them: the previous version looped inside ONE test, so the first failing
#: character raised and the other eight never ran -- the reason string said "nine code points" and
#: the body exercised five, of which exactly one was ever reached. Measured before parametrising:
#: all of them diverge, so every case below is a genuine strict xfail rather than an optimistic one.
#: A partial fix now shows up as a single XPASS, which strict turns into a failure naming the one
#: character that was fixed, instead of being invisible behind whichever case happened to run first.
def _derive_splitlines_breakers() -> list[str]:
    """Every code point `str.splitlines()` breaks on, EXCEPT line feed -- measured, not listed.

    r2.50a mechanism (1): a quantifier in a name or message must be backed by a parametrisation
    whose cardinality is DERIVED from the artefact it quantifies over. The previous version was a
    hand-written list of nine `pytest.param`s beside a reason string that said "nine code points",
    and the design note's own example of the failure is the neighbouring one: the four invented
    tails were wrong precisely BECAUSE the set was hand-written, while these nine were right only
    because someone had enumerated them correctly by hand that day. Right-by-luck and wrong-by-luck
    are the same mechanism.

    `str.splitlines()` is the artefact, so it is asked directly. The scan is the whole Unicode
    range rather than a bounded guess: bounding it would reintroduce a hand-chosen number one level
    up, and measured, the full sweep costs about 0.1 s at import.
    """
    breakers = [chr(cp) for cp in range(0x110000) if len(("a" + chr(cp) + "b").splitlines()) > 1]
    return [ch for ch in breakers if ch != "\n"]


def _breaker_id(ch: str) -> str:
    """A readable id, derived from the code point rather than named by hand."""
    try:
        return unicodedata.name(ch).lower().replace(" ", "-")
    except ValueError:
        return f"u+{ord(ch):04x}"


_DERIVED_BREAKERS = _derive_splitlines_breakers()

#: The count is DERIVED. Nothing below states it as a literal, and the xfail reason interpolates it.
_SPLITLINES_BREAKER_COUNT = len(_DERIVED_BREAKERS)

_SPLITLINES_BREAKERS = [pytest.param(ch, id=_breaker_id(ch)) for ch in _DERIVED_BREAKERS]


class RegisteredSplitlinesDivergence(AssertionError):
    """The ONE outcome the strict xfail below is allowed to accept.

    It subclasses AssertionError so the failure still reads as an assertion failure, but it is a
    DISTINCT type, and that is the whole point: `raises=AssertionError` accepted any assertion from
    anywhere in the call, so an unrelated `assert` at the call site -- an input guard, a sanity
    check, a typo -- silently became "the expected failure" and retired the registered finding with
    the suite green.

    Because the divergence now has a name, only the code that WITNESSES it can raise it.
    """


@pytest.mark.parametrize("breaker", _SPLITLINES_BREAKERS)
@pytest.mark.xfail(
    strict=True,
    # raises=<a DEDICATED type> (pr-prep blocker 4, round 2 C-3). The history matters:
    #   v1: no raises=       -> strict xfail accepted ANY exception, including a crash.
    #   v2: raises=AssertionError -> narrower, still broken TWO ways. Reviewers proved both:
    #       (a) the guard test accepted any tuple CONTAINING AssertionError, so
    #           `(AssertionError, Exception)` restored "accepts everything" while passing the guard;
    #       (b) even unwidened, an idiomatic bare `assert` at the call site made all nine cases
    #           raise BEFORE the witnessing assertion; pytest counted each as the expected failure
    #           and the file reported 37 passed / 9 xfailed, byte-identical to baseline, with the
    #           registered gate-6 finding exercised by nothing.
    #   v3 (here): the divergence has its own TYPE, raised only by the code that witnesses it. An
    #       unrelated AssertionError is no longer that type, so it fails the test instead of
    #       impersonating the finding. The check is structural, not a claim about the marker.
    raises=RegisteredSplitlinesDivergence,
    reason=(
        "REGISTERED GATE-6 FINDING, not authorised for repair in this iteration: production splits "
        f"lines with str.splitlines(), which breaks on {_SPLITLINES_BREAKER_COUNT} code points "
        "besides line feed, while the "
        "association sentence says line feed. An accession and a structure on ONE PHYSICAL LINE can "
        "therefore be several 'lines' apart and the association is lost - measured, 1,775 of 3,000 "
        "generated zero-newline documents. STRICT on purpose: when the finding is fixed this test "
        "passes, strict fails it, and the marker must be removed in the same commit. That is how the "
        "axis carries a known defect without hiding it or blocking the gate."
    ),
)
def test_the_splitlines_line_definition_DIVERGES_from_the_sentence(breaker):
    """The rebuilt axis can now SEE the line-definition defect; before the rebuild it could not.

    This is what deriving the expectation from `reference_associations` buys instead of deriving it
    from the call site's own first line: measured, 0 of 96,900 documents could distinguish
    `splitlines()` from splitting on line feed under the old design. The class is EXERCISED here
    rather than quietly excluded from the corpus, so the gap shows up in the test report and not only
    in a dispatch.

    It also replaces the old rule-3b row for this axis, which built its own two-line string and
    called the function directly: that proved the FUNCTION honours its `window` argument, not that
    the AXIS can reject anything. The window is now entry six of `_CALL_SITE_MUSEUM`, driven through
    the axis like every other entry.
    """
    from chipsim.ingest.drugbank_snapshot import accession_structure_tuples

    text = PROBE_ACCESSION + breaker * 3 + " " + PROBE_KEY
    assert "\n" not in text, "the point of the case is that it contains NO line feed"
    assert text.splitlines() != [text], (
        f"{breaker!r} is not a line break for str.splitlines() after all, so this case cannot "
        "witness the divergence and does not belong in the table above."
    )
    # Raised explicitly, not asserted: an `assert` here would be indistinguishable from any other
    # assertion in the call, which is exactly how this xfail came to accept unrelated failures.
    if accession_structure_tuples(text) != reference_associations(text):
        raise RegisteredSplitlinesDivergence(
            f"break character {breaker!r}: the call site and the sentence disagree on what a line is"
        )


# --- r2.50a mechanism (3): a helper that promises to raise is PROVEN to raise -------------------
#
# Gate 8 (H-1) found `_characters_at` SILENTLY WRONG for a counted capturing group -- the exact
# failure its own docstring forbids. The hole was in the arm that LOOKED handled: the body-type
# check sat inside `if position == index`, so an unsupported body raised only when the index
# landed on it, and otherwise advanced `position` by 1 however many characters the body consumed.
# Measured before the fix on `(Xn){1}[A-Z]{25}`: index 0 raised, index 1 returned 26 uppercase
# letters where the truth is `n`, index 2 was right by accident.
#
# The MECHANISM, not the repair: the contract is proven by a PROPERTY over regex constructs with
# `re` itself as the oracle, never by a hand-maintained list of node types. A list of node types
# is what was already here, and it is what missed this.

_PROOF_ALPHABET = "XnAB-"
_PROOF_MAX_LENGTH = 4

_PROOF_PATTERNS = [
    "Xn",
    "X[AB]",
    "[AB][AB]",
    "[AB]{2}-",
    "X[AB]{2}",
    "(Xn){1}[AB]{2}",  # counted CAPTURING group -- the gate-8 verdict-flipper
    "(?:Xn){1}[AB]{2}",  # counted NON-capturing group
    "((X)){1}n",  # nested groups
    "(X|n){1}[AB]",  # group holding an alternation
]


def _proof_strings():
    for size in range(1, _PROOF_MAX_LENGTH + 1):
        for combo in itertools.product(_PROOF_ALPHABET, repeat=size):
            yield "".join(combo)


def _proof_matches(pattern):
    compiled = re.compile(pattern)
    return [text for text in _proof_strings() if compiled.fullmatch(text)]


def _truth_at(matches, index):
    """Every character that REALLY stands at `index`, taken from actual matches.

    `re` is the oracle. Deliberately brute force: it cannot share a mistake with the derivation
    under test, which is the whole point of a differential.
    """
    return {text[index] for text in matches}


@pytest.mark.parametrize("pattern", _PROOF_PATTERNS, ids=_PROOF_PATTERNS)
def test_characters_at_is_never_SILENTLY_WRONG_it_is_right_or_it_RAISES(pattern):
    """The contract as a property: at EVERY index, raise or be exactly right.

    Not "it raises on the constructs I listed" -- that is the check which already existed and
    already missed the counted group. A construct this helper cannot handle must fail LOUDLY at
    every index, not only at the index that happens to land on it.
    """
    matches = _proof_matches(pattern)
    assert matches, f"{pattern!r} matches nothing over the proof alphabet; the case is vacuous"
    lengths = {len(text) for text in matches}
    assert len(lengths) == 1, (
        f"{pattern!r} matches several lengths {sorted(lengths)}; this proof is defined only for "
        "fixed-length patterns"
    )
    length = lengths.pop()

    wrong = []
    for index in range(length):
        truth = _truth_at(matches, index)
        try:
            derived = _characters_at(pattern, index)
        except AssertionError:
            continue  # raising is always permitted: it is the honest answer
        restricted = derived & set(_PROOF_ALPHABET)
        if restricted != truth:
            wrong.append(
                f"index {index}: derived {sorted(restricted)} but the truth is {sorted(truth)}"
            )
    assert not wrong, (
        f"{pattern!r}: _characters_at returned a WRONG set instead of raising -- a set that looks "
        "like evidence and is not. " + "; ".join(wrong)
    )


def test_the_proof_corpus_actually_EXERCISES_the_construct_that_broke_it():
    """Anti-vacuity: the corpus must still contain a counted CAPTURING group.

    A proof whose corpus quietly lost its hard case is the family again, so the corpus is checked
    rather than trusted.
    """
    counted_capturing = [p for p in _PROOF_PATTERNS if re.search(r"\((?!\?)[^)]*\)\{\d", p)]
    assert counted_capturing, (
        "the proof corpus no longer contains a counted CAPTURING group -- the construct that "
        "produced gate 8's H-1. Without it this property test cannot fail for the original reason."
    )


# --- r2.50a mechanism (4): the flag guard is LOAD-BEARING, not decoration ----------------------

_UNMODELLABLE_FLAGS = [
    pytest.param(re.IGNORECASE, id="IGNORECASE-makes-A-Z-admit-lowercase"),
    pytest.param(re.VERBOSE, id="VERBOSE-changes-how-the-text-parses"),
    pytest.param(re.DOTALL, id="DOTALL-changes-what-dot-admits"),
]


@pytest.mark.parametrize("flag", _UNMODELLABLE_FLAGS)
def test_a_derivation_REFUSES_a_compiled_object_whose_flags_it_cannot_model(flag):
    """The guard must fire on the FLAG, with the pattern text held identical.

    This is the false-exclusion shape of mechanism (2) applied to a derivation: the dangerous case
    is not a pattern that looks wrong, it is one that looks IDENTICAL and behaves differently.
    """
    flagged = re.compile(_STRUCTURE_RE.pattern, flag)
    assert flagged.pattern == _STRUCTURE_RE.pattern, (
        "this test is only meaningful while the flagged compile has identical TEXT -- that "
        "identity is the whole reason the guard reads flags instead of text"
    )
    with pytest.raises(AssertionError, match="cannot model"):
        _assert_flags_are_derivable(flagged, "a flagged compile")


def test_the_flag_guard_ACCEPTS_the_object_actually_shipped():
    """Anti-vacuity: a guard that refused everything would pass the test above and prove nothing."""
    _assert_flags_are_derivable(_STRUCTURE_RE, "the shipped structure pattern")
    assert _STRUCTURE_RE.flags & ~_DERIVABLE_FLAGS == 0, (
        "the shipped pattern now carries a flag the derivation cannot model; the equivalence "
        "proof must be extended or the flag removed before this suite can bind again"
    )


def test_IGNORECASE_would_actually_BREAK_the_disjointness_the_proof_relies_on():
    """The guard earns its keep only if the flag it refuses would really change the answer.

    Without this, the guard could be refusing a flag that made no difference -- a check whose
    claim is wider than the risk it covers, which is the family stated the other way round.
    """
    branches = _alternation_branches(_STRUCTURE_RE.pattern)
    assert len(branches) == 2, "the proof is written for a two-branch alternation"
    first, second = (_characters_at(branch, 1) for branch in branches)
    assert first.isdisjoint(second), "precondition: the branches are disjoint as shipped"

    # Model IGNORECASE by hand at index 1 only: a class read case-insensitively admits both cases.
    def case_folded(chars):
        return {c.lower() for c in chars} | {c.upper() for c in chars}

    assert not case_folded(first).isdisjoint(case_folded(second)), (
        "under IGNORECASE the two branches would still be disjoint at index 1, so this guard is "
        "not protecting the conclusion it claims to protect and its justification needs rewriting"
    )


# --- r2.50a mechanism (1): the quantifier is derived, and that is itself checked ----------------


def test_the_breaker_set_is_DERIVED_from_str_splitlines_not_hand_listed():
    """Anti-vacuity for the derivation: re-measure independently and require agreement.

    A derivation nobody re-measures is a hand-written list with extra steps, so this asks
    `str.splitlines()` a second time, by a different route, and compares.
    """
    independently = {
        chr(cp)
        for cp in range(0x110000)
        if len(("x" + chr(cp) + "y").splitlines()) > 1 and chr(cp) != "\n"
    }
    assert set(_DERIVED_BREAKERS) == independently, (
        "the parametrised breaker set no longer equals what str.splitlines() actually breaks on; "
        "the quantifier has drifted from the artefact it quantifies over"
    )
    assert _SPLITLINES_BREAKER_COUNT == len(independently)


def test_no_literal_count_of_the_breakers_is_written_anywhere_in_this_file():
    """The mechanism, enforced on this file: the number must not be typed beside the claim.

    Gate 8's instance was a reason string that said "nine code points" while the body exercised
    one. The number is now interpolated from the derived set, so this asserts the spelled-out and
    digit forms are absent -- if someone re-types it, the claim can drift from the check again.
    """
    with open(__file__, encoding="utf-8") as handle:
        text = handle.read()
    body = text.split("def test_no_literal_count_of_the_breakers")[0]
    offenders = []
    for form in (f" {_SPLITLINES_BREAKER_COUNT} code points", " nine code points"):
        if form in body:
            offenders.append(form.strip())
    assert not offenders, (
        "a literal count of the splitlines breakers is typed beside the claim rather than "
        f"interpolated from the derived set: {offenders}. That is the exact shape of the gate-8 "
        "finding this mechanism exists to prevent."
    )


# --- BLOCKER 4 regression: a non-assertion raise must FAIL, not be swallowed -------------------


def test_an_UNRELATED_assertion_at_the_call_site_is_NOT_the_registered_divergence(monkeypatch):
    """The behavioural half of C-3: drive the impersonation path that twice went undetected.

    reviewer-code inserted a plausible input guard -- `assert "\x0b" not in text, ...` -- at the call
    site. Under `raises=AssertionError` every one of the nine cases then raised before reaching the
    witness, pytest counted each as the expected strict xfail, and the file reported 37 passed /
    9 xfailed, byte-identical to baseline. Nothing said the registered finding had stopped being
    exercised.

    With a dedicated type, that same guard raises a plain AssertionError, which is NOT the type the
    xfail accepts, so pytest reports a failure. Asserting the type relationship directly is what
    makes this a behavioural check rather than another statement about the marker.
    """
    import chipsim.ingest.drugbank_snapshot as production

    def _sanitising_call_site(text):
        # The idiomatic form a maintainer would actually add, patched where they would add it:
        # the PRODUCTION module. The test function imports the symbol locally, so patching the test
        # module's namespace would patch nothing -- which is itself worth stating, because a probe
        # that patched the wrong namespace would pass while exercising nothing.
        assert "\x0b" not in text and "\x0c" not in text, "control characters are not accepted"
        raise AssertionError("unreachable in this probe")

    monkeypatch.setattr(production, "accession_structure_tuples", _sanitising_call_site)

    breaker = _DERIVED_BREAKERS[0]
    with pytest.raises(AssertionError) as caught:
        test_the_splitlines_line_definition_DIVERGES_from_the_sentence(breaker)

    assert not isinstance(caught.value, RegisteredSplitlinesDivergence), (
        "an unrelated assertion at the call site is being treated as the registered divergence -- "
        "this is pr-prep blocker 4, and it is how the gate-6 finding stopped being exercised while "
        "the suite stayed green"
    )


def test_the_registered_divergence_TYPE_is_raised_only_by_the_witness():
    """A second, cheaper guard: the type is raised in exactly one place in this module.

    If a future edit raises it from an input guard or a helper, the type stops being a witness and
    becomes another way to impersonate the finding. Counted from the source rather than asserted in
    prose.
    """
    with open(__file__, encoding="utf-8") as fh:  # Path is not imported in this module
        source = fh.read()
    # ASSEMBLED FROM PARTS. Written as one literal, this line contains the needle it searches for,
    # so the count was 2 and the test failed on its own text -- "never assert on a string the fixture
    # also produces", the rule this suite already carries, violated by the test enforcing it.
    needle = "raise " + "RegisteredSplitlinesDivergence("
    raises_it = source.count(needle)
    assert raises_it == 1, (
        f"RegisteredSplitlinesDivergence is raised in {raises_it} places; it must be raised ONLY by "
        "the assertion that witnesses the divergence, or it stops distinguishing anything"
    )


def test_the_strict_xfail_accepts_ONLY_the_registered_divergence_not_any_exception():
    """The mutant reviewer-test used, made permanent as a property of the marker itself.

    A strict xfail without `raises=` treats a crash as success. This asserts the marker on the
    splitlines test names the exception it expects, so a sanitisation guard (or any other new
    raise) at the call site surfaces as a failure rather than as the registered finding.
    """
    marker = None
    for m in test_the_splitlines_line_definition_DIVERGES_from_the_sentence.pytestmark:
        if m.name == "xfail":
            marker = m
            break
    assert marker is not None, "the splitlines divergence test lost its xfail marker"
    assert marker.kwargs.get("strict") is True, "the xfail must stay strict"
    raises = marker.kwargs.get("raises")
    assert raises is not None, (
        "the strict xfail has no `raises=`, so ANY exception counts as the expected outcome -- "
        "a guard that raises before the assertion would silently retire the registered finding "
        "while the suite stayed green"
    )
    assert raises is RegisteredSplitlinesDivergence, (
        f"the expected failure must be the assertion that witnesses the divergence, not {raises!r}"
    )
