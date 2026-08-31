"""Fixture-hygiene tests — build-plan S5.

Fixtures exist so agent-owned done-conditions can fail honestly while the
human-gated tasks (T1/T2/T8/T14/T18) are outstanding. That licence holds only as
long as fixtures stay *out of the pipeline*. The moment a pipeline path reads
one, a synthetic sentinel becomes indistinguishable from a curated human claim —
which is exactly the failure mode the human/agent allocation rule exists to
prevent. These tests are the mechanical guard on that boundary.
"""

import csv
from pathlib import Path

import pytest
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_DIR = PROJECT_ROOT / "tests" / "fixtures"

#: Names that exist ONLY as fixtures. A bare mention of one in shipped source is
#: already a leak — there is no real artifact these could refer to.
FIXTURE_ONLY_NAMES = {
    "barrier_panel_ratified.yaml",
    "barrier_panel_unratified.yaml",
    "pgp_adjudication_filled.csv",
    "pgp_adjudication_blank.csv",
}

#: Names a fixture SHARES with a real artifact it stands in for
#: (data/raw/drugbank/provenance.yaml, configs/poc_compounds.yaml). Shipped source
#: is expected to name these; the leak is only a reference that reaches into
#: tests/fixtures/, so these are matched by path, never bare.
SHARED_NAMES = {
    "provenance.yaml",
    "poc_compounds.yaml",
}

EXPECTED_FIXTURES = FIXTURE_ONLY_NAMES | SHARED_NAMES

#: Trees that make up the shipped package and its configuration — i.e. every
#: path that could constitute a "pipeline path".
NON_TEST_TREES = ("chipsim", "configs", "orchestration")


def test_all_expected_fixtures_exist():
    present = {p.name for p in FIXTURE_DIR.iterdir() if p.is_file()}
    assert EXPECTED_FIXTURES <= present, f"missing fixtures: {EXPECTED_FIXTURES - present}"


@pytest.mark.parametrize("name", sorted(n for n in EXPECTED_FIXTURES if n.endswith(".yaml")))
def test_yaml_fixtures_parse(name):
    loaded = yaml.safe_load((FIXTURE_DIR / name).read_text())
    assert loaded, f"{name} parsed to something empty"


@pytest.mark.parametrize("name", sorted(n for n in EXPECTED_FIXTURES if n.endswith(".csv")))
def test_csv_fixtures_parse(name):
    with (FIXTURE_DIR / name).open(newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert rows, f"{name} parsed to zero rows"


def test_fixtures_live_under_tests_only():
    """No fixture filename may also exist under configs/ or data/."""
    for name in EXPECTED_FIXTURES:
        for tree in ("configs", "data"):
            strays = list((PROJECT_ROOT / tree).rglob(name))
            assert not strays, f"fixture {name} has a stray copy in {tree}/: {strays}"


def test_fixtures_are_not_configs():
    """No fixture path is referenced from outside tests/.

    Scans every shipped source file for a fixture filename or a `tests/fixtures`
    path. A hit means a pipeline path can read a synthetic sentinel — the exact
    confusion between a fixture and a human artifact that S5 forbids.
    """
    offenders = []
    for tree in NON_TEST_TREES:
        root = PROJECT_ROOT / tree
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix in {".parquet", ".pyc"}:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            needles = [n for n in FIXTURE_ONLY_NAMES if n in text]
            # Shared names are legitimate in shipped source (they name the REAL
            # artifact). Only a path reaching into the fixture tree is a leak.
            needles += [f"tests/fixtures/{n}" for n in SHARED_NAMES
                        if f"fixtures/{n}" in text]
            if "tests/fixtures" in text:
                needles.append("tests/fixtures")
            if needles:
                offenders.append(f"{path.relative_to(PROJECT_ROOT)} -> {sorted(set(needles))}")
    assert not offenders, (
        "fixture paths referenced outside tests/ — a pipeline path must never read a "
        "fixture (build-plan S5):\n  " + "\n  ".join(offenders)
    )
