"""Repo-wide source hygiene: invariants about the SHAPE of the code, not its behaviour.

Why this module exists
----------------------
`tests/test_fixture_sources.py` defined ``CONFIGS = PROJECT_ROOT / "configs"`` **twice**, at two
different points in one file. The values were identical, so nothing broke — which is exactly why
it survived. A second module-level binding of the same name silently shadows the first, so the
definition that wins depends on its position in the file. Edit one and the other quietly decides
the outcome.

That is this project's recurring failure mode in its structural form: **two definitions of one
subject, free to diverge, with nothing asserting they agree.** The same shape as a stored count
beside the list it counts (which S6 rejected in `unparseable_compounds.yaml`), and as a docstring
beside the projection it describes (which `test_the_export_projection_and_its_docstring_cannot_
drift_apart` pins).

The fix was one deleted line. **This test is here so the class cannot come back** — not "be more
careful" but "an assertion fires".

What it does NOT catch, stated
------------------------------
- Duplicates of the same name in DIFFERENT files. Each test module owning its own constants is
  normal and this rule does not reach across files.

  **A retracted carve-out.** This list used to name ``test_published_snapshot_counts`` and
  ``test_published_roster_provenance`` as a legitimate, documented exception — "rather than
  coupling two suites' collection order for three lines". Review showed that justification was
  factually wrong (a cross-module import does not affect collection order, and the house already
  imports shared helpers from ``conftest``), that it was ~35 lines rather than three, and that the
  two copies had already DRIFTED. So this module was carving out, by name, exactly the shape it
  exists to abolish: two definitions of one subject, free to diverge. The two modules are now one
  (``test_published_snapshot_claims``) and the exception is gone rather than reworded.
- Rebinding inside a function or class body; this looks only at module level.
- Names that are not SCREAMING_CASE, and annotated assignments (``NAME: T = ...``).
- Two constants with different names holding the same value — a real drift hazard this does not
  address.
- **A forward declaration**, i.e. ``NAME = None`` and then a real assignment later. That is a
  legitimate, documented pattern — ``tests/test_transport_fit.py`` uses it for ``_PRIOR``, which
  cannot be built until its helper is defined — and it carries no drift hazard, because ``None``
  is not a value that can disagree with anything. **The rule counts only SUBSTANTIVE bindings.**

  This boundary was not designed; it was discovered. The first version of this invariant said
  "one name, one definition" and immediately flagged that forward declaration. Writing the rule
  as a PROPERTY (ignore ``None`` placeholders) rather than as an exemption LIST keeps it from
  going stale the way a hand-maintained list of allowed offenders would.
"""

from __future__ import annotations

import ast
import pathlib

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
SOURCE_DIRS = ("chipsim", "tests")


def _python_files() -> list[pathlib.Path]:
    files = [f for d in SOURCE_DIRS for f in (PROJECT_ROOT / d).rglob("*.py")]
    assert files, (
        f"no Python files found under {SOURCE_DIRS} in {PROJECT_ROOT}. An empty discovery must "
        "not read as 'nothing to check' — the error path of a discovery is part of the check."
    )
    return sorted(files)


def _shadowed_constants(source: str) -> dict[str, list[int]]:
    """Module-level SCREAMING_CASE names bound more than once, with their line numbers."""
    seen: dict[str, list[int]] = {}
    for node in ast.parse(source).body:
        if not isinstance(node, ast.Assign):
            continue
        # A `NAME = None` placeholder is a forward declaration, not a competing definition:
        # None cannot disagree with a later value, so it carries no drift hazard. Counting it
        # would flag a legitimate documented pattern (see this module's docstring).
        if isinstance(node.value, ast.Constant) and node.value.value is None:
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id.isupper() and len(target.id) > 2:
                seen.setdefault(target.id, []).append(node.lineno)
    return {name: lines for name, lines in seen.items() if len(lines) > 1}


def test_no_module_level_constant_is_defined_twice_in_one_file():
    """The invariant. One name, one definition, per file."""
    offenders = []
    for path in _python_files():
        for name, lines in _shadowed_constants(path.read_text(encoding="utf-8")).items():
            offenders.append(f"{path.relative_to(PROJECT_ROOT)}: {name} at lines {lines}")

    assert not offenders, (
        "module-level constant(s) defined more than once in one file; the later binding shadows "
        "the earlier, so which one wins depends on position:\n  " + "\n  ".join(offenders)
    )


def test_the_scan_actually_reaches_the_files_it_claims_to_cover():
    """Anti-vacuity, DERIVED rather than a hardcoded floor.

    A scan that discovers nothing passes the invariant above trivially. The floor is derived from
    the tracked tree rather than asserted as a numeral, so it cannot go stale.
    """
    found = {p.resolve() for p in _python_files()}
    for required in (
        PROJECT_ROOT / "tests" / "test_fixture_sources.py",
        PROJECT_ROOT / "tests" / "test_source_hygiene.py",
    ):
        assert required.resolve() in found, f"the scan does not reach {required.name}"
    assert len(found) > 20, f"only {len(found)} files discovered; expected the whole package"


def test_the_detector_FIRES_on_a_planted_duplicate():
    """THE PROBE. Without it, the invariant above could be decorative.

    Plants the exact defect that motivated this module — including the harmless-looking identical
    -value case, which is the one that actually survived in the tree — and requires detection.
    """
    planted = _shadowed_constants('CONFIGS = ROOT / "configs"\nX = 1\nCONFIGS = ROOT / "configs"\n')
    assert planted == {"CONFIGS": [1, 3]}, planted


def test_the_detector_does_not_fire_on_a_single_definition_or_on_a_local_rebind():
    """The other half of falsifiability: it must not cry wolf."""
    assert _shadowed_constants("CONFIGS = 1\nOTHER = 2\n") == {}
    assert _shadowed_constants("def f():\n    CONFIGS = 1\n    CONFIGS = 2\n") == {}


def test_a_forward_declaration_is_NOT_a_duplicate_but_two_real_bindings_STILL_ARE():
    """Pins the boundary the real tree taught this module, in both directions.

    The permissive half and the strict half are asserted together, because a rule that only
    stops crying wolf is indistinguishable from a rule that stopped working.
    """
    # The legitimate pattern: placeholder, then the real assignment once the helper exists.
    assert _shadowed_constants("_PRIOR = None  # assigned below\n_PRIOR = _prior()\n") == {}
    # Still caught: two substantive bindings, which is the actual drift hazard.
    assert _shadowed_constants("_PRIOR = _a()\n_PRIOR = _b()\n") == {"_PRIOR": [1, 2]}
    # And a placeholder does not license a later pair.
    assert _shadowed_constants("X_Y = None\nX_Y = _a()\nX_Y = _b()\n") == {"X_Y": [2, 3]}


# --- the no-identifier-in-assertion-operand rule ------------------------------------------------

#: Modules that read a frame pairing a structure key with a substance name. An assertion in one of
#: these must take a pre-bound SCALAR, never the frame or a key set.
_PAIRING_READERS = (
    "test_published_pgp_result.py",
    "test_published_snapshot_claims.py",
)

#: Calls that return a frame or a key collection. Inside an `assert`, pytest's rewriting prints
#: the result, so none of these may appear there.
_COLLECTION_PRODUCERS = frozenset(
    {
        "_load_snapshot_or_skip",
        "_read_tracked_frame",
        "_rows_with_prefix",
        "relative_stereo_keys",
        "load_poc_roster",
        "set",
    }
)


def _assert_operand_offenders(source: str) -> list[str]:
    """Names from `_COLLECTION_PRODUCERS` called inside an `assert` in a `test_*` function."""
    bad: list[str] = []
    for node in ast.walk(ast.parse(source)):
        if not (isinstance(node, ast.FunctionDef) and node.name.startswith("test_")):
            continue
        for stmt in ast.walk(node):
            if not isinstance(stmt, ast.Assert):
                continue
            for inner in ast.walk(stmt.test):
                if (
                    isinstance(inner, ast.Call)
                    and isinstance(inner.func, ast.Name)
                    and inner.func.id in _COLLECTION_PRODUCERS
                ):
                    bad.append(f"{node.name}: {inner.func.id}() at line {inner.lineno}")
    return bad


def test_no_assertion_takes_a_frame_or_key_set_as_an_OPERAND():
    """The published-number modules must assert on scalars, never on a frame or a key set.

    WHY. The snapshot frame carries `canonical_inchikey` beside `name` and `drugbank_id`, so a
    frame in an assertion operand emits an identifier PAIRED with a substance — which this
    project forbids on a public surface, and which lands in CI logs. pytest's assertion rewriting
    prints every subexpression regardless of a custom message, so the fix is the operand, not the
    message. The author's docstring claim that "no identifier is written into any failure message"
    was FALSE until this was enforced.

    WHAT THIS IS NOT. A denylist of known collection-producing calls is a **regression guard, not
    a proof**. It did not find the original defect and could not have: the miss that mattered was
    `assert adjudicated_keys == roster_keys`, a bare set-vs-set compare with no call in it at all,
    and it was found by running deliberately failing variants and grepping the FORMATTED pytest
    report for the identifier shape. Do that whenever these modules' assertions change; this test
    only stops a known shape from returning.
    """
    offenders = []
    for name in _PAIRING_READERS:
        path = PROJECT_ROOT / "tests" / name
        assert path.is_file(), f"{name} is missing; this rule names a module that does not exist"
        offenders.extend(
            f"{name}::{hit}" for hit in _assert_operand_offenders(path.read_text(encoding="utf-8"))
        )
    assert not offenders, (
        "assertion operand(s) that pytest would print as a frame or key set:\n  "
        + "\n  ".join(offenders)
    )


def test_the_operand_rule_FIRES_on_a_planted_violation():
    """THE PROBE, in both directions, on literal source so it never touches the tree."""
    planted = _assert_operand_offenders(
        "def test_x():\n    assert len(_load_snapshot_or_skip()) == 1\n"
    )
    assert len(planted) == 1 and "_load_snapshot_or_skip" in planted[0], planted
    # bound to a local first: the shape the rule exists to require
    assert (
        _assert_operand_offenders(
            "def test_x():\n    n = len(_load_snapshot_or_skip())\n    assert n == 1\n"
        )
        == []
    )
    # a non-test helper may still call it
    assert (
        _assert_operand_offenders("def _helper():\n    assert len(_load_snapshot_or_skip()) == 1\n")
        == []
    )


def test_the_named_collection_producers_all_still_exist_somewhere():
    """Stale-entry guard: a denylist naming a vanished function is a rule that stopped working."""
    haystack = "\n".join(
        (PROJECT_ROOT / "tests" / n).read_text(encoding="utf-8") for n in _PAIRING_READERS
    )
    missing = sorted(n for n in _COLLECTION_PRODUCERS if n != "set" and n not in haystack)
    assert not missing, f"denylisted name(s) no longer present, so the entry is stale: {missing}"
