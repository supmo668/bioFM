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
- Duplicates of the same name in DIFFERENT files — **this carve-out is now scoped to ``tests/``
  only.** As of 2026-11-08 the rule DOES reach across the library: see
  ``test_no_public_module_constant_means_two_different_things_in_two_modules`` below. Within
  ``tests/`` each module owning its own constants stays normal.

  **Measured, not asserted.** The first wording of the new cross-file rule justified excluding
  ``tests/`` as "noisy enough to be ignored" — an unmeasured magnitude. Extending the scan there
  yields **2 offenders out of 94 public names**, and one is REAL drift: ``LIVE_PROVENANCE``, spelled
  ``RAW_DIR / 'provenance.yaml'`` in ``test_provenance.py`` and
  ``PROJECT_ROOT / 'data' / 'raw' / 'drugbank' / 'provenance.yaml'`` in ``test_snapshot_fetch.py``.
  That is a KNOWN OPEN ITEM, recorded here rather than hidden behind "noisy" — which is the same
  reasoning error as the retracted carve-out immediately below, made one test later.
- The new cross-file rule's own limits, stated in its docstring: a duplicate public FUNCTION or
  CLASS name is not its business (``test_no_module_imports_one_name_from_two_different_modules``
  catches the shape that bites), and agreement between two definitions is asserted ONLY when both
  right-hand sides are provably literal — anything else REPORTS rather than passes.

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
- (Removed limits, kept here so the history is legible: a two-character cutoff used to exempt
  ``PI``/``NA`` silently, tuple-unpacking targets were skipped, and module-level assignments
  nested in ``if``/``try``/``with`` were invisible. All three are now covered and pinned below.)
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
    """Discover per directory, and FAIL CLOSED per directory.

    `rglob` on a MISSING directory yields nothing and raises nothing, and the old form asserted
    only that the UNION was non-empty — so `tests/` alone satisfied it. Review proved the
    consequence: renaming the `chipsim` entry (what a package rename or a move to `src/` looks
    like) left all five tests green with the ENTIRE LIBRARY unscanned, and a real shadowing
    duplicate planted in `chipsim/harmonize/roster.py` went unreported. A guard whose scope can be
    silently emptied is the defect family this module exists to catch — found in this module.
    """
    files: list[pathlib.Path] = []
    for directory in SOURCE_DIRS:
        root = PROJECT_ROOT / directory
        assert root.is_dir(), (
            f"{directory!r} is not a directory under {PROJECT_ROOT}. The scan would silently "
            "cover nothing there, so this fails instead of reporting 'nothing to check'."
        )
        found = sorted(root.rglob("*.py"))
        assert found, f"no Python files under {directory!r}; the scan would be vacuous there"
        files.extend(found)
    return files


def _module_level(body: list[ast.stmt]) -> list[ast.stmt]:
    """Module-level statements INCLUDING those nested in `if` / `try` / `with`.

    Only `.body` was walked before, so review proved an assignment inside a module-level
    `if True:` block was invisible. Function and class bodies stay excluded: a local rebind is
    not a competing module-level definition.

    LIFTED to module scope 2026-11-08. It was an inner function of `_shadowed_constants`, so
    the cross-file detector added beside it could not reuse it and hand-rolled a shallow
    `.body`-only walk instead — reintroducing the exact gap this function was written to close.
    Two detectors may differ in what they RECORD; they have no reason to differ in what they
    REACH. One walk, one definition.
    """
    out: list[ast.stmt] = []
    for stmt in body:
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        out.append(stmt)
        for attr in ("body", "orelse", "finalbody"):
            out.extend(_module_level(getattr(stmt, attr, None) or []))
        for handler in getattr(stmt, "handlers", None) or []:
            out.extend(_module_level(handler.body))
    return out


def _shadowed_constants(source: str) -> dict[str, list[int]]:
    """Module-level SCREAMING_CASE names bound more than once, with their line numbers."""
    seen: dict[str, list[int]] = {}

    for node in _module_level(ast.parse(source).body):
        if not isinstance(node, ast.Assign):
            continue
        # A `NAME = None` placeholder is a forward declaration, not a competing definition:
        # None cannot disagree with a later value, so it carries no drift hazard. Counting it
        # would flag a legitimate documented pattern (see this module's docstring).
        if isinstance(node.value, ast.Constant) and node.value.value is None:
            continue
        # Walk each target so TUPLE/LIST unpacking is covered — review proved `A_B, C_D = 1, 2`
        # followed by `A_B = 3` went unreported, because only a bare `ast.Name` target was
        # examined. The floor is now 2 characters, not 3, so `PI`/`NA` are no longer exempt.
        for target in node.targets:
            for name in ast.walk(target):
                if isinstance(name, ast.Name) and name.id.isupper() and len(name.id) >= 2:
                    seen.setdefault(name.id, []).append(node.lineno)
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
    """Anti-vacuity, now actually DERIVED — the docstring used to outrun the code.

    It claimed the floor was "derived from the tracked tree rather than asserted as a numeral" and
    the code read `len(found) > 20`, a literal that `tests/` satisfies on its own (it holds more
    than 20 files). Both required members were test files too, so a scan missing the whole library
    passed. Now the floor is the real per-directory total and members from BOTH directories are
    required.
    """
    found = {p.resolve() for p in _python_files()}
    for required in (
        PROJECT_ROOT / "tests" / "test_fixture_sources.py",
        PROJECT_ROOT / "tests" / "test_source_hygiene.py",
        PROJECT_ROOT / "chipsim" / "harmonize" / "roster.py",
        PROJECT_ROOT / "chipsim" / "eval" / "provenance_block.py",
    ):
        assert required.resolve() in found, f"the scan does not reach {required.name}"
    expected = sum(len(list((PROJECT_ROOT / d).rglob("*.py"))) for d in SOURCE_DIRS)
    assert len(found) == expected, f"discovered {len(found)} files, expected {expected}"


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


def test_the_detector_covers_the_three_shapes_it_used_to_MISS():
    """Pins what review proved it missed, so the coverage is a property and not a claim."""
    # tuple unpacking as the FIRST binding
    assert _shadowed_constants("A_B, C_D = 1, 2\nA_B = 3\n") == {"A_B": [1, 2]}
    # a module-level assignment nested in a compound statement
    assert _shadowed_constants("if True:\n    CONFIGS = 1\nCONFIGS = 2\n") == {"CONFIGS": [2, 3]}
    # two-character names are no longer silently exempt
    assert _shadowed_constants("AB = 1\nAB = 2\n") == {"AB": [1, 2]}
    # and a rebind inside a FUNCTION body is still not a module-level duplicate
    assert _shadowed_constants("def f():\n    AB = 1\n    AB = 2\n") == {}


def _literal(node: ast.expr | None) -> tuple[bool, object]:
    """(is_provably_literal, value). Used to decide whether two RHS AGREE.

    Comparing `ast.unparse` text was the first attempt and it was wrong in BOTH
    directions, measured 2026-11-08:
      - FALSE NEGATIVE: `SCAFFOLD = _TEMPLATES / _NAME` in two modules over different
        private `_NAME`s unparses identically, so a real path divergence read as agreement.
        That is the very defect this guard exists to catch, one tidy-up down.
      - FALSE POSITIVE: `Path("x")` vs `pathlib.Path("x")` are the same value and read as
        disagreement.
    So agreement is now asserted ONLY when both sides are provably literal. Anything else
    is UNDECIDABLE, and undecidable reports — the fail-closed direction this module already
    takes for an unparseable file and for an emptied scan scope.
    """
    if node is None:
        return False, None
    try:
        return True, ast.literal_eval(node)
    except (ValueError, TypeError, SyntaxError, MemoryError, RecursionError):
        return False, None


def _is_reexport(name: str, node: ast.expr | None) -> bool:
    """True for `X = other_module.X` — an ALIAS, not a competing definition.

    Found by this guard firing on its own author: `theta.py` re-exports
    `S6_FORBIDDEN_RELPATHS = _s6.S6_FORBIDDEN_RELPATHS` so the S6 guard has one
    definition, and a textual comparison called that a collision with `_s6`'s. It is the
    legitimate "one fact, stated once and pointed at" case, and flagging it would push an
    author back toward two real definitions — the opposite of the point.
    """
    return isinstance(node, ast.Attribute) and node.attr == name


def _public_module_constants(source: str) -> dict[str, tuple[bool, object]]:
    """Public module-level SCREAMING_CASE names -> (is_literal, value).

    Public only: a leading underscore makes a cross-module import an explicit, loud act,
    so two modules may legitimately carry the same private name.
    """
    out: dict[str, tuple[bool, object]] = {}
    for node in _module_level(ast.parse(source).body):
        if isinstance(node, ast.Assign):
            targets, value = node.targets, node.value
        elif isinstance(node, ast.AnnAssign):
            if node.value is None:
                # A bare `AB: int` DECLARES a type; it does not define a value. Recording
                # it (as `""`) made a declaring module collide with a defining one.
                continue
            targets, value = [node.target], node.value
        else:
            continue
        for target in targets:
            for nm in ast.walk(target):  # tuple/list unpacking too, per the sibling
                if not (isinstance(nm, ast.Name) and nm.id.isupper() and len(nm.id) >= 2):
                    continue
                if nm.id.startswith("_") or _is_reexport(nm.id, value):
                    continue
                out[nm.id] = _literal(value)
    return out


def _cross_module_offenders(by_name: dict[str, dict[str, tuple[bool, object]]]) -> list[str]:
    """The decision, extracted so it can be PROBED rather than only run on a clean tree.

    It used to live inline in the test body, where it was evaluated against the real tree
    alone — which yields no offenders — so the condition could have been weakened to
    anything and the suite would have stayed green with nothing to report. The per-file
    guard beside this one keeps its decision inside its helper for exactly that reason.
    """
    offenders: list[str] = []
    for name, per_module in sorted(by_name.items()):
        if len(per_module) < 2:
            continue
        literal = all(is_lit for is_lit, _ in per_module.values())
        if literal:
            values = {repr(v) for _, v in per_module.values()}
            if len(values) == 1:
                continue  # provably the same fact, stated twice: fine
            verdict = "different values"
        else:
            verdict = "values NOT PROVABLY EQUAL (non-literal right-hand side)"
        where = "; ".join(
            f"{m} = {v!r}" if is_lit else f"{m} = <non-literal>"
            for m, (is_lit, v) in sorted(per_module.items())
        )
        offenders.append(f"{name}: {verdict} — {where}")
    return offenders


def _imports_by_name(source: str) -> dict[str, set[str]]:
    """Bound name -> the set of modules this file imports it FROM, anywhere in the file.

    Walks the WHOLE tree, not just module level, because the hazard this catches lived in
    two FUNCTION bodies.
    """
    out: dict[str, set[str]] = {}
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                out.setdefault(alias.asname or alias.name, set()).add(node.module)
    return out


def _library_files() -> list[pathlib.Path]:
    """The library's own modules, scope DERIVED from SOURCE_DIRS — not re-spelled.

    Hardcoding `PROJECT_ROOT / "chipsim"` here put a SECOND definition of "where the
    library is" into the one file whose thesis is that two definitions of a subject drift.
    """
    library = PROJECT_ROOT / SOURCE_DIRS[0]
    assert library.is_dir(), (
        f"{library} is not a directory. SOURCE_DIRS[0] is {SOURCE_DIRS[0]!r}; if the "
        "package moved, update SOURCE_DIRS and both scans follow."
    )
    found = sorted(library.rglob("*.py"))
    assert found, f"no Python files under {library}; the scan would be vacuous"
    return found


def test_no_public_module_constant_means_two_different_things_in_two_modules():
    """The cross-file companion to the per-file invariant above.

    `_shadowed_constants` is per-file by construction, so a public constant carrying
    DISJOINT meanings in two modules was invisible to it. Measured 2026-11-06:
    `ENTRY_KEYS` was `("value", "unit", …)` in `transport/theta.py` and
    `("mean_log", "sigma_log", …)` in `transport/prior.py`, and `SCAFFOLD_RELPATH` named
    two different template paths in the same two modules.

    What this does NOT reach, stated because this module's habit is to state it:
      - a duplicate public FUNCTION or CLASS name — see the import test below, which
        catches the shape that actually bites rather than every harmless namesake;
      - a name whose two definitions are both non-literal AND genuinely equal: that is
        reported, not missed, and the author narrows it (fail-closed, see `_literal`);
      - anything under `tests/`. Measured 2026-11-08 rather than asserted: extending the
        scan there yields 2 offenders out of 94 public names, so the earlier claim that it
        would be "noisy" was an unmeasured magnitude. One of the two is REAL drift
        (`LIVE_PROVENANCE`, spelled two ways in `test_provenance.py` and
        `test_snapshot_fetch.py`). It is excluded here because the library is this guard's
        subject, and recorded as a known open item rather than hidden behind "noisy".
    """
    by_name: dict[str, dict[str, tuple[bool, object]]] = {}
    reached = set()
    for path in _library_files():
        rel = path.relative_to(PROJECT_ROOT).as_posix()
        reached.add(rel)
        for name, value in _public_module_constants(path.read_text(encoding="utf-8")).items():
            by_name.setdefault(name, {})[rel] = value

    # Reach floor. `assert found` only proved SOME file was read; these two modules are the
    # ones whose collision motivated the guard, so name them.
    for must in ("chipsim/transport/theta.py", "chipsim/transport/prior.py"):
        assert must in reached, f"{must} was not reached; the scan's scope has drifted"
    assert len(by_name) >= 40, (
        f"only {len(by_name)} public module constants discovered across {len(reached)} "
        "files; the detector has gone quiet and the guard would pass vacuously"
    )

    offenders = _cross_module_offenders(by_name)
    assert not offenders, (
        "public module-level constant(s) sharing a name across modules without provably "
        "sharing a value. A cross-module import then binds whichever module was imported "
        "last, so correctness rests on import placement rather than on the name:\n  "
        + "\n  ".join(offenders)
        + "\nThe rule: PRIVATISE (leading underscore) when the name is not consumed "
        "outside its module; RENAME to a distinct public name only when it must stay "
        "surface. Privatisation is strictly stronger — it removes the import pathway "
        "instead of making a collision merely unlikely."
    )


def test_no_module_imports_one_name_from_two_different_modules():
    """The shape that actually bit: ONE file binding ONE name from TWO modules.

    `chipsim/pipeline.py` imported `SCAFFOLD_RELPATH` AND `write_scaffold` from both
    `transport.theta` and `transport.prior`, in two separate function bodies. It was
    correct only because of that placement: hoisting the imports to module level — the
    ordinary tidy-up — makes the second binding win module-wide, and measured on the
    post-rename tree that sent `theta-scaffold` to the prior's writer, which at the time
    had no S6 refusal at all.

    This catches constants and callables alike, and it is placement-blind by design,
    because placement was the load-bearing thing. It is the companion the constant guard
    needs: a duplicate public FUNCTION name is only a hazard when something imports it
    from both places, so this tests the hazard instead of flagging every namesake
    (`build_parser` and `main` legitimately exist in two modules here).
    """
    offenders = []
    for path in _library_files():
        rel = path.relative_to(PROJECT_ROOT).as_posix()
        for name, modules in sorted(_imports_by_name(path.read_text(encoding="utf-8")).items()):
            if len(modules) > 1:
                offenders.append(f"{rel}: `{name}` imported from {sorted(modules)}")
    assert not offenders, (
        "one name bound from two different modules in a single file. Which definition "
        "wins depends on import ORDER and PLACEMENT, not on the name:\n  "
        + "\n  ".join(offenders)
        + "\nFix by giving the two definitions distinct names, or by importing the "
        "modules and qualifying the call."
    )


def test_no_chipsim_file_binds_one_private_name_from_two_modules():
    """What makes PRIVATISATION sound rather than merely conventional.

    The constant guard exempts underscore names on the premise that a private name cannot
    collide across modules by accident. The premise breaks in exactly one way: if two
    modules both export `_ENTRY_KEYS` and ONE file imports both, the second binding wins
    and no guard here would see it, because the exemption is the cover.

    So this asserts the narrow thing the exemption needs, not a blanket ban on private
    imports. A first draft DID ban them outright and failed on its own author — it flagged
    `from chipsim.transport import _s6`, which imports a private MODULE and is the pattern
    this file's own text recommends, and `_recorded_argv` from `chipsim.journal`, a
    pre-existing single private-member import that carries no collision. A guard that
    forbids the remedy it recommends is not a stricter guard; it is a wrong one.
    """
    offenders = []
    for path in _library_files():
        rel = path.relative_to(PROJECT_ROOT).as_posix()
        private: dict[str, set[str]] = {}
        for name, modules in _imports_by_name(path.read_text(encoding="utf-8")).items():
            if name.startswith("_") and not name.startswith("__"):
                private.setdefault(name, set()).update(modules)
        for name, modules in sorted(private.items()):
            if len(modules) > 1:
                offenders.append(f"{rel}: `{name}` from {sorted(modules)}")
    assert not offenders, (
        "one PRIVATE name bound from two modules in a single file. The cross-file constant "
        "guard exempts private names on the premise that this cannot happen:\n  "
        + "\n  ".join(offenders)
        + "\nEither give them distinct names, or import the modules and qualify."
    )


def test_cross_file_detectors_are_not_vacuous():
    """Proof every piece above can fail. The per-file guard is proved the same way."""
    # --- extraction: the real shape ---
    assert _public_module_constants('ENTRY_KEYS = ("a", "b")\n') == {
        "ENTRY_KEYS": (True, ("a", "b"))
    }
    # nested in a module-level compound statement — the gap the shallow walk had
    assert "AB" in _public_module_constants("if True:\n    AB = 1\n")
    assert "AB" in _public_module_constants("try:\n    AB = 1\nexcept Exception:\n    pass\n")
    assert "AB" in _public_module_constants("if TYPE_CHECKING:\n    AB = 1\n")
    # tuple unpacking, as the sibling covers
    got = _public_module_constants("AB, CD = 1, 2\n")
    assert "AB" in got and "CD" in got
    # private, lowercase and single-char stay out of scope
    assert _public_module_constants('_ENTRY_KEYS = ("a",)\n') == {}
    assert _public_module_constants("entry_keys = 1\nX = 2\n") == {}
    # a bare annotation DECLARES, it does not define
    assert _public_module_constants("AB: int\n") == {}
    assert _public_module_constants("AB: int = 1\n") == {"AB": (True, 1)}
    # a function body is not a module-level definition
    assert _public_module_constants("def f():\n    AB = 1\n") == {}
    # a re-export is an alias, not a competing definition
    assert _public_module_constants("AB = other.AB\n") == {}
    assert "AB" in _public_module_constants("AB = other.DIFFERENT\n")
    # literal detection
    assert _literal(ast.parse("1").body[0].value) == (True, 1)
    assert _literal(ast.parse("_X / _Y").body[0].value)[0] is False

    # --- the DECISION, probed directly rather than only against a clean tree ---
    L = lambda v: (True, v)
    NL = (False, None)
    assert _cross_module_offenders({"A": {"m1.py": L(1)}}) == []  # one module
    assert _cross_module_offenders({"A": {"m1.py": L(1), "m2.py": L(1)}}) == []  # same value
    two = _cross_module_offenders({"A": {"m1.py": L(1), "m2.py": L(2)}})
    assert len(two) == 1 and "m1.py" in two[0] and "m2.py" in two[0]
    # identical SOURCE TEXT over different private helpers is non-literal -> REPORTED
    assert len(_cross_module_offenders({"A": {"m1.py": NL, "m2.py": NL}})) == 1
    # three modules, one dissenting
    assert len(_cross_module_offenders({"A": {"m1.py": L(1), "m2.py": L(1), "m3.py": L(2)}})) == 1
    # Path("x") vs pathlib.Path("x") both literal-eval to the same string -> no offender
    assert _cross_module_offenders({"A": {"m1.py": L("x"), "m2.py": L("x")}}) == []

    # --- the import detectors ---
    assert _imports_by_name("from a import X\nfrom b import X\n")["X"] == {"a", "b"}
    assert _imports_by_name("def f():\n    from a import X\ndef g():\n    from b import X\n")[
        "X"
    ] == {"a", "b"}
    assert _imports_by_name("from a import X as Y\nfrom b import Z as Y\n")["Y"] == {"a", "b"}
    assert _imports_by_name("from a import X\n")["X"] == {"a"}
