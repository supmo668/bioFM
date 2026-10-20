"""E-23 (r2.48) (b): the STRUCTURE-IDENTIFIER reference scanner. Imports no production code.

Written from the clause's SPEC SENTENCE, in plain Python with no regex, one clause per line, so a
reader can check it against the sentence by reading it:

    a STRUCTURE IDENTIFIER is (i) an InChI: the seven ASCII characters `InChI=1`, case-sensitive,
    then optionally `S`, then `/`, then one or more characters none of which is whitespace, running
    to the next whitespace character or the end of the text; or (ii) an InChIKey: fourteen ASCII
    uppercase letters, a hyphen, ten ASCII uppercase letters, a hyphen, and one ASCII uppercase
    letter. Either is recognised whatever precedes or follows it; scanning is left to right, (i) is
    tried before (ii) at each position, and matches do not overlap.

"Whitespace" is `str.isspace()` and "ASCII uppercase" is `string.ascii_uppercase`, because those
are the plain-Python renderings of the words. That they coincide with the pattern's own classes
is MEASURED over every code point by
`test_the_sentences_whitespace_and_the_patterns_whitespace_coincide` and
`test_the_sentences_uppercase_and_the_patterns_uppercase_coincide`, never assumed.
"""

import string

_UPPER = frozenset(string.ascii_uppercase)
_PREFIX = "InChI=1"  # the seven ASCII characters, case-sensitive


def _inchi_body_end(text, start):
    """Given `start` just after the "/", the end of a non-empty non-whitespace run, else None."""
    if start >= len(text) or text[start].isspace():  # one or more characters...
        return None
    end = start
    while end < len(text) and not text[end].isspace():  # ...none of which is whitespace
        end += 1
    return end  # running to the next whitespace character or the end of the text


def _inchi_end(text, i):
    """(i) an InChI starting at `i`: its end, else None."""
    if not text.startswith(_PREFIX, i):
        return None
    j = i + len(_PREFIX)
    if text.startswith("S/", j):  # then optionally `S`, then `/`...
        end = _inchi_body_end(text, j + 2)
        if end is not None:
            return end
    if text.startswith("/", j):  # ...or no `S`, then `/`
        return _inchi_body_end(text, j + 1)
    return None


def _is_key_at(text, i):
    """(ii) an InChIKey at `i`: 14 uppercase, hyphen, 10 uppercase, hyphen, 1 uppercase."""
    piece = text[i : i + 27]
    return (
        len(piece) == 27
        and all(c in _UPPER for c in piece[:14])
        and piece[14] == "-"
        and all(c in _UPPER for c in piece[15:25])
        and piece[25] == "-"
        and piece[26] in _UPPER
    )


def reference_spans(text):
    """The spec sentence over a whole string. Returns match spans, left to right, non-overlapping."""
    spans = []
    i = 0
    while i < len(text):  # scanning is left to right
        end = _inchi_end(text, i)  # (i) is tried before (ii) at each position
        if end is not None:
            spans.append((i, end))
            i = end  # matches do not overlap
            continue
        if _is_key_at(text, i):
            spans.append((i, i + 27))
            i += 27
            continue
        i += 1  # recognised whatever precedes or follows it
    return spans
