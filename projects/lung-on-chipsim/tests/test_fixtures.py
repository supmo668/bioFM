"""Fixture-hygiene tests — build-plan S5.

Fixtures exist so agent-owned done-conditions can fail honestly while the
human-gated tasks (T1/T2/T8/T14/T18) are outstanding. That licence holds only as
long as fixtures stay *out of the pipeline*. The moment a pipeline path reads
one, a synthetic sentinel becomes indistinguishable from a curated human claim —
exactly the failure the human/agent allocation rule exists to prevent.

Three separate guards, because they fail differently:
  1. leak scan      — shipped source must not REFERENCE a fixture path
  2. copy escape    — no file outside tests/ may BE a fixture (digest / banner)
  3. content lock   — the fixtures must keep exercising the cases downstream
                      tasks depend on, so a regression surfaces here and not as
                      a mystery failure in P3/P4

The leak scan carries its own positive control. Without one it passes when the
scanner is broken — which it was: a typo in the scanned-tree list made the whole
check a silent no-op.
"""

import csv
import hashlib
import re
from pathlib import Path

import pytest
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_DIR = PROJECT_ROOT / "tests" / "fixtures"

#: Names that exist ONLY as fixtures. A bare mention in shipped source is already
#: a leak — there is no real artifact these could refer to.
FIXTURE_ONLY_NAMES = {
    "barrier_panel_ratified.yaml",
    "barrier_panel_unratified.yaml",
    "barrier_panel_missing_ratified.yaml",
    "barrier_panel_ratified_no_ratifier.yaml",
    "barrier_panel_no_abcb1.yaml",
    "pgp_adjudication_filled.csv",
    "pgp_adjudication_blank.csv",
    "pgp_adjudication_partial.csv",
    "pgp_adjudication_all_unknown.csv",
    "pgp_adjudication_no_missing_doi.csv",
    "pgp_adjudication_single_group.csv",
    "poc_compounds_too_few.yaml",
    "poc_compounds_too_many.yaml",
    "poc_compounds_missing_doi.yaml",
    "provenance_unjustified_swap.yaml",
    "provenance_justified_swap.yaml",
}

#: Names a fixture SHARES with the real artifact it stands in for
#: (data/raw/drugbank/provenance.yaml from T1/T2, configs/poc_compounds.yaml from
#: T18). Shipped source is EXPECTED to name these. The leak is only a reference
#: that reaches into tests/fixtures/, so these are never matched bare — and the
#: real artifact is explicitly allowed to exist.
SHARED_NAMES = {
    "provenance.yaml",
    "poc_compounds.yaml",
}

#: Fixture SUBDIRECTORIES. tests/fixtures/snapshot/ mimics the dhimmel/drugbank
#: TSV *schema* so T5/T5b/T6's parse logic is testable while T2/T4a are blocked.
#: It carries no DrugBank content.
FIXTURE_SUBDIRS = {
    "snapshot": {
        "README.md",
        "drugbank.tsv",
        "drugbank-slim.tsv",
        "proteins.tsv",
    },
}

EXPECTED_FIXTURES = FIXTURE_ONLY_NAMES | SHARED_NAMES

#: Trees that constitute shipped source — anything here is a potential pipeline path.
NON_TEST_TREES = ("chipsim", "configs", "orchestration")

#: Directories never worth scanning.
SKIP_DIRS = {
    ".venv",
    ".git",
    ".dvc",
    ".dvc-storage",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "data",
    "tests",
    ".egg-info",
}

SENTINEL_BANNER = "FIXTURE — SYNTHETIC. NOT A HUMAN ARTIFACT."


# --------------------------------------------------------------------------- #
# existence / parse
# --------------------------------------------------------------------------- #


def test_all_expected_fixtures_exist():
    present = {p.name for p in FIXTURE_DIR.iterdir() if p.is_file()}
    assert EXPECTED_FIXTURES <= present, f"missing fixtures: {EXPECTED_FIXTURES - present}"


def test_every_present_fixture_is_registered():
    """Closes the loop on a hand-maintained list.

    `EXPECTED_FIXTURES` drives the parse, banner and digest checks below. A fixture
    added to the directory but not to the list is therefore checked by NOTHING —
    it silently opts out of every guarantee this module provides. This asserts the
    reverse inclusion, so adding a fixture without registering it FAILS here.

    Found by the P0.2 quality gate: tests/fixtures/snapshot/ was added with four
    files, none registered, and the whole suite stayed green.
    """
    top_level = {p.name for p in FIXTURE_DIR.iterdir() if p.is_file()}
    unregistered = top_level - EXPECTED_FIXTURES
    assert not unregistered, (
        f"unregistered fixture file(s): {sorted(unregistered)}. Add them to "
        "FIXTURE_ONLY_NAMES or SHARED_NAMES so they are actually checked."
    )

    present_dirs = {p.name for p in FIXTURE_DIR.iterdir() if p.is_dir()}
    present_dirs -= {"__pycache__"}
    assert present_dirs == set(FIXTURE_SUBDIRS), (
        f"fixture subdirectories out of sync: present={sorted(present_dirs)}, "
        f"registered={sorted(FIXTURE_SUBDIRS)}"
    )
    for name, expected in FIXTURE_SUBDIRS.items():
        actual = {p.name for p in (FIXTURE_DIR / name).iterdir() if p.is_file()}
        assert actual == expected, (
            f"tests/fixtures/{name}/ contents out of sync: "
            f"present={sorted(actual)}, registered={sorted(expected)}"
        )


def test_snapshot_fixture_carries_the_sentinel_banner():
    """TSV has no comment syntax, so the directory's README carries the banner for
    the whole snapshot fixture set."""
    readme = (FIXTURE_DIR / "snapshot" / "README.md").read_text()
    assert SENTINEL_BANNER in readme


def test_snapshot_fixture_is_not_real_drugbank_content():
    """The one assertion that matters legally as well as scientifically: ChipSim
    never redistributes DrugBank. Every identifier in the fixture is namespaced."""
    import csv as _csv

    for name in ("drugbank.tsv", "drugbank-slim.tsv", "proteins.tsv"):
        with (FIXTURE_DIR / "snapshot" / name).open(newline="") as fh:
            rows = list(_csv.DictReader(fh, delimiter="\t"))
        assert rows, f"{name} is empty"
        for row in rows:
            assert row["drugbank_id"].startswith("DB9"), (
                f"{name} carries a non-fixture drugbank_id {row['drugbank_id']!r}; "
                "fixture ids are namespaced DB9xxxx so they cannot collide with real ones"
            )


def test_scanned_trees_actually_exist():
    """Guards the leak scan against a silent no-op.

    Every entry of NON_TEST_TREES must be a real directory. A typo here would make
    the scan iterate nothing and report green forever.
    """
    missing = [t for t in NON_TEST_TREES if not (PROJECT_ROOT / t).is_dir()]
    assert not missing, f"NON_TEST_TREES names non-existent director(ies): {missing}"


@pytest.mark.parametrize("name", sorted(n for n in EXPECTED_FIXTURES if n.endswith(".yaml")))
def test_yaml_fixtures_parse(name):
    assert yaml.safe_load((FIXTURE_DIR / name).read_text())


@pytest.mark.parametrize("name", sorted(n for n in EXPECTED_FIXTURES if n.endswith(".csv")))
def test_csv_fixtures_parse(name):
    with (FIXTURE_DIR / name).open(newline="") as fh:
        assert list(csv.DictReader(fh))


def test_every_fixture_carries_the_sentinel_banner():
    """A fixture must be self-identifying, so a stray copy is recognisable on sight."""
    for name in sorted(EXPECTED_FIXTURES):
        if name.endswith(".csv"):
            continue  # CSV has no comment syntax; covered by digest + key namespace
        assert SENTINEL_BANNER in (FIXTURE_DIR / name).read_text(), f"{name} lost its banner"


# --------------------------------------------------------------------------- #
# guard 1 — the leak scan, with a positive control
# --------------------------------------------------------------------------- #


def _normalize(text: str) -> str:
    """Collapse path punctuation so a composed path reads as one token.

    ``Path(root) / "tests" / "fixtures" / "provenance.yaml"`` contains no literal
    ``tests/fixtures`` substring. Stripping quotes, slashes, commas and whitespace
    turns it into ``...teststfixturesprovenance.yaml``, which the adjacency check
    below catches.
    """
    return re.sub(r"""["'`/\\,\s\]\[()]+""", "", text)


def _scan_file_for_fixture_leaks(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []
    norm = _normalize(text)
    hits = [n for n in FIXTURE_ONLY_NAMES if n in text or _normalize(n) in norm]
    if "tests/fixtures" in text or "testsfixtures" in norm:
        hits.append("tests/fixtures")
    hits += [
        f"tests/fixtures/{n}"
        for n in SHARED_NAMES
        if f"fixtures/{n}" in text or f"fixtures{_normalize(n)}" in norm
    ]
    # conftest is the ready-made front door into the fixture tree.
    if "tests.conftest" in text or "load_fixture_yaml" in text:
        hits.append("tests.conftest import")
    return sorted(set(hits))


def _iter_shipped_files():
    """Every shipped source file: the three trees plus project-root config files."""
    for tree in NON_TEST_TREES:
        root = PROJECT_ROOT / tree
        if not root.is_dir():
            continue
        for p in root.rglob("*"):
            if p.is_file() and not any(part in SKIP_DIRS for part in p.parts):
                yield p
    # Project-root files matter most: a dvc.yaml here IS a pipeline definition.
    for p in PROJECT_ROOT.iterdir():
        if p.is_file() and p.suffix in {".toml", ".yaml", ".yml", ".json", ".cfg", ".ini", ".md"}:
            yield p


def scan_for_fixture_leaks(paths=None) -> list[str]:
    """Return ``"<path> -> [needles]"`` for every shipped file referencing a fixture."""
    offenders = []
    for path in paths if paths is not None else _iter_shipped_files():
        hits = _scan_file_for_fixture_leaks(path)
        if hits:
            rel = path.relative_to(PROJECT_ROOT) if path.is_relative_to(PROJECT_ROOT) else path
            offenders.append(f"{rel} -> {hits}")
    return offenders


@pytest.mark.parametrize(
    "leak",
    [
        pytest.param('P = "tests/fixtures/pgp_adjudication_filled.csv"', id="literal-path"),
        pytest.param('P = open("../tests/fixtures/provenance.yaml")', id="relative-path"),
        pytest.param('P = ROOT / "tests" / "fixtures" / "provenance.yaml"', id="composed-path"),
        pytest.param('P = "barrier_panel_ratified.yaml"', id="bare-fixture-only-name"),
        pytest.param("from tests.conftest import load_fixture_yaml", id="conftest-import"),
    ],
)
def test_leak_scanner_detects_a_planted_reference(tmp_path, leak):
    """POSITIVE CONTROL. Without this, the scan passes when the scanner is broken."""
    planted = tmp_path / "leaky.py"
    planted.write_text(leak)
    assert scan_for_fixture_leaks([planted]), f"scanner MISSED a real leak: {leak}"


def test_leak_scanner_ignores_clean_source(tmp_path):
    """Negative control — the scanner must not flag legitimate source."""
    clean = tmp_path / "clean.py"
    clean.write_text(
        'PROV = "data/raw/drugbank/provenance.yaml"\n'
        'ROSTER = "configs/poc_compounds.yaml"\n'
        'PANEL = "configs/barrier_panel.yaml"\n'
    )
    assert scan_for_fixture_leaks([clean]) == []


def test_fixtures_are_not_configs():
    """No shipped source file references a fixture path."""
    offenders = scan_for_fixture_leaks()
    assert not offenders, (
        "fixture paths referenced outside tests/ — a pipeline path must never read a "
        "fixture (build-plan S5):\n  " + "\n  ".join(offenders)
    )


# --------------------------------------------------------------------------- #
# guard 2 — copy escape
# --------------------------------------------------------------------------- #


def test_fixtures_live_under_tests_only():
    """No fixture-only filename may exist outside tests/.

    Scoped to FIXTURE_ONLY_NAMES deliberately. The earlier version iterated all
    EXPECTED_FIXTURES and so forbade `data/raw/drugbank/provenance.yaml` and
    `configs/poc_compounds.yaml` — the very artifacts T1/T2/T18 are required to
    produce. It would have gone red on the first human-gated task to land.
    """
    for name in sorted(FIXTURE_ONLY_NAMES):
        for tree in ("configs", "data", "chipsim", "orchestration"):
            root = PROJECT_ROOT / tree
            if root.is_dir():
                strays = [p for p in root.rglob(name)]
                assert not strays, f"fixture {name} has a stray copy: {strays}"


def test_no_shipped_file_is_a_copy_of_a_fixture():
    """A fixture must not be installed under a real artifact's name.

    Catches the highest-consequence escape: `cp tests/fixtures/barrier_panel_ratified.yaml
    configs/barrier_panel.yaml` would otherwise install a synthetic `ratified: true`
    panel as a genuine human ratification, and no filename rule would notice.
    """
    digests = {
        hashlib.sha256((FIXTURE_DIR / n).read_bytes()).hexdigest(): n for n in EXPECTED_FIXTURES
    }
    offenders = []
    for path in _iter_shipped_files():
        blob = path.read_bytes()
        d = hashlib.sha256(blob).hexdigest()
        if d in digests:
            offenders.append(f"{path.relative_to(PROJECT_ROOT)} is byte-identical to {digests[d]}")
        elif SENTINEL_BANNER.encode() in blob:
            offenders.append(f"{path.relative_to(PROJECT_ROOT)} carries the fixture banner")
    assert not offenders, "fixture copied into shipped source:\n  " + "\n  ".join(offenders)


@pytest.mark.parametrize("name", sorted(SHARED_NAMES))
def test_real_artifact_is_not_the_fixture(name):
    """When the real artifact exists, it must not be a copy of the sentinel.

    Unlike the fixture-only names, these paths are ALLOWED to exist — the plan
    requires them. What is forbidden is that a human artifact turns out to be the
    fixture wearing its name.
    """
    real_paths = [
        PROJECT_ROOT / "configs" / name,
        PROJECT_ROOT / "data" / "raw" / "drugbank" / name,
    ]
    fixture_bytes = (FIXTURE_DIR / name).read_bytes()
    for rp in real_paths:
        if rp.is_file():
            assert rp.read_bytes() != fixture_bytes, (
                f"{rp.relative_to(PROJECT_ROOT)} is a byte-identical copy of the "
                f"fixture — a synthetic sentinel is masquerading as a human artifact"
            )


# --------------------------------------------------------------------------- #
# guard 3 — content lock
# --------------------------------------------------------------------------- #

INCHIKEY = re.compile(r"^[A-Z]{14}-[A-Z]{10}-[A-Z]$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")


def _load(name):
    return yaml.safe_load((FIXTURE_DIR / name).read_text())


def _rows(name):
    with (FIXTURE_DIR / name).open(newline="") as fh:
        return list(csv.DictReader(fh))


def test_provenance_fixture_shape():
    d = _load("provenance.yaml")
    assert HEX40.match(d["source_commit"])
    assert d["source_commit"] == d["audited_commit"]
    # T2 specifies an EMPTY rationale when the commits match. A filled one here
    # would let T11's commit-substitution test pass under three wrong implementations.
    assert d["commit_change_rationale"] == ""
    assert len(d["attribution"]) == 3
    assert d["upstream_version"] == "4.2" and d["snapshot_date"] == "2015-03-19"


def test_provenance_swap_fixtures_are_distinguishable():
    """The two swap fixtures must differ in exactly the way T11 keys on."""
    bad, good = _load("provenance_unjustified_swap.yaml"), _load("provenance_justified_swap.yaml")
    for d in (bad, good):
        assert d["source_commit"] != d["audited_commit"]
    assert bad["commit_change_rationale"] == ""
    assert good["commit_change_rationale"] != ""


@pytest.mark.parametrize(
    "name,ratified,ratifier_empty",
    [
        ("barrier_panel_ratified.yaml", True, False),
        ("barrier_panel_unratified.yaml", False, True),
        ("barrier_panel_ratified_no_ratifier.yaml", True, True),
    ],
)
def test_panel_fixture_flags(name, ratified, ratifier_empty):
    d = _load(name)
    assert d["ratified"] is ratified  # identity, not truthiness (defect 1)
    assert (d["ratified_by"] == "") is ratifier_empty


def test_panel_missing_ratified_key_has_no_ratified_key():
    assert "ratified" not in _load("barrier_panel_missing_ratified.yaml")


@pytest.mark.parametrize(
    "name,has_abcb1",
    [("barrier_panel_ratified.yaml", True), ("barrier_panel_no_abcb1.yaml", False)],
)
def test_panel_abcb1_presence(name, has_abcb1):
    symbols = {e["symbol"] for e in _load(name)["panel"]}
    assert ("ABCB1" in symbols) is has_abcb1


def test_panel_entries_are_complete():
    for e in _load("barrier_panel_ratified.yaml")["panel"]:
        assert {"symbol", "uniprot", "alias", "face"} <= e.keys()
        assert re.match(r"^[A-Z0-9]{6,10}$", e["uniprot"])
        assert e["face"] in {"apical", "basolateral"}


@pytest.mark.parametrize(
    "name,lo,hi",
    [
        ("poc_compounds.yaml", 20, 40),
        ("poc_compounds_too_few.yaml", 0, 19),
        ("poc_compounds_too_many.yaml", 41, 999),
    ],
)
def test_roster_sizes(name, lo, hi):
    assert lo <= len(_load(name)["compounds"]) <= hi


def test_roster_keys_are_inchikey_shaped():
    """Sentinel keys must still be structurally valid InChIKeys.

    S11a/T5b/T10/T13/T15 all index on canonical_inchikey, and any of them may
    reasonably add a shape check. A malformed sentinel would then be "fixed" in the
    fixture rather than in the validator.
    """
    for c in _load("poc_compounds.yaml")["compounds"]:
        assert INCHIKEY.match(c["canonical_inchikey"]), c["canonical_inchikey"]


def test_roster_missing_doi_fixture_has_exactly_one_gap():
    gaps = [
        c for c in _load("poc_compounds_missing_doi.yaml")["compounds"] if not c["evidence_doi"]
    ]
    assert len(gaps) == 1


def test_worksheet_columns_match_t13():
    expected = [
        "canonical_inchikey",
        "name",
        "snapshot_label",
        "adjudicated_label",
        "evidence_doi",
        "adjudicated_by",
        "adjudicated_on",
    ]
    for n in ("pgp_adjudication_blank.csv", "pgp_adjudication_filled.csv"):
        assert list(_rows(n)[0].keys()) == expected


def test_blank_worksheet_has_no_verdicts():
    for r in _rows("pgp_adjudication_blank.csv"):
        assert not any(
            r[c] for c in ("adjudicated_label", "evidence_doi", "adjudicated_by", "adjudicated_on")
        )


def test_filled_worksheet_populates_both_groups():
    """defect 24 — a single populated group makes the M5 grouping variable unusable."""
    labels = [r["adjudicated_label"] for r in _rows("pgp_adjudication_filled.csv")]
    assert set(labels) == {"yes", "no", "unknown"}  # equality, not subset (defect 9)
    assert labels.count("yes") > 0 and labels.count("no") > 0
    for r in _rows("pgp_adjudication_filled.csv"):
        if r["adjudicated_label"] in {"yes", "no"}:
            assert r["evidence_doi"] and r["adjudicated_by"]


def test_snapshot_label_never_says_no():
    """T10 can only emit yes/unknown — absence of evidence is never 'no'."""
    for n in ("pgp_adjudication_blank.csv", "pgp_adjudication_filled.csv"):
        assert {r["snapshot_label"] for r in _rows(n)} <= {"yes", "unknown"}


@pytest.mark.parametrize(
    "name,check",
    [
        (
            "pgp_adjudication_partial.csv",
            lambda rs: (
                any(r["adjudicated_label"] for r in rs)
                and any(not r["adjudicated_label"] for r in rs)
            ),
        ),
        (
            "pgp_adjudication_all_unknown.csv",
            lambda rs: {r["adjudicated_label"] for r in rs} == {"unknown"},
        ),
        (
            "pgp_adjudication_no_missing_doi.csv",
            lambda rs: any(r["adjudicated_label"] == "no" and not r["evidence_doi"] for r in rs),
        ),
        (
            "pgp_adjudication_single_group.csv",
            lambda rs: {r["adjudicated_label"] for r in rs} == {"yes", "unknown"},
        ),
    ],
)
def test_negative_worksheets_exercise_their_case(name, check):
    assert check(_rows(name)), f"{name} does not exercise the case it exists for"


def test_worksheet_keys_match_the_roster():
    """T13's 'exactly one row per roster entry' is only checkable if these agree."""
    roster = [c["canonical_inchikey"] for c in _load("poc_compounds.yaml")["compounds"]]
    for n in ("pgp_adjudication_blank.csv", "pgp_adjudication_filled.csv"):
        assert [r["canonical_inchikey"] for r in _rows(n)] == roster
