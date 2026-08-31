"""Scaffold done-condition tests — build-plan S1, S2, S3, S6, S7, S11.

Every S-task states a done-condition. Several were verified once by hand at
implementation time and then had nothing holding them. This module makes each one
a standing assertion, so a later edit that quietly breaks the scaffold fails here
rather than in P1-P4.

Two of these were found to be untrue or unfalsifiable as originally verified:
  - S1's negative ("exits non-zero if any __init__.py is removed") was FALSE
    before the guard in chipsim/__init__.py existed — PEP 420 made it import fine.
  - S3's negative ("exits non-zero if testpaths is removed") is STILL not true via
    the CLI: pytest skips .venv by default norecursedirs, so tests/ is collected
    either way. It is asserted here against the config instead, and the plan's
    stated CLI form is recorded as not achievable. See test_s3_testpaths_configured.
"""

import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent

#: A&D §4.4 layer set, in order.
EXPECTED_SUBPACKAGES = (
    "ingest",
    "harmonize",
    "encoders",
    "heads",
    "transport",
    "occupancy",
    "surface",
    "uncertainty",
    "eval",
    "acquire",
)

#: S11 — the five modules later tasks mark "(edit)".
S11_MODULES = {
    "chipsim.ingest.drugbank_snapshot": "chipsim/ingest/drugbank_snapshot.py",
    "chipsim.harmonize.ids": "chipsim/harmonize/ids.py",
    "chipsim.harmonize.pgp_label": "chipsim/harmonize/pgp_label.py",
    "chipsim.harmonize.contracts": "chipsim/harmonize/contracts.py",
    "chipsim.eval.provenance_block": "chipsim/eval/provenance_block.py",
}


@pytest.fixture(scope="module")
def pyproject():
    return tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text())


# --------------------------------------------------------------------------- #
# S1 · package skeleton
# --------------------------------------------------------------------------- #


def test_s1_layer_set_matches_the_and_d():
    import chipsim

    assert chipsim.SUBPACKAGES == EXPECTED_SUBPACKAGES


@pytest.mark.parametrize("name", EXPECTED_SUBPACKAGES)
def test_s1_subpackage_is_a_regular_package(name):
    """A namespace package has spec.origin None — that is the failure to catch."""
    import importlib

    mod = importlib.import_module(f"chipsim.{name}")
    assert mod.__spec__ is not None and mod.__spec__.origin is not None, (
        f"chipsim.{name} is a PEP 420 namespace package, not a regular package"
    )
    assert mod.__file__.endswith("__init__.py")


def test_s1_removing_an_init_makes_import_fail(tmp_path):
    """S1's stated negative condition, end-to-end in a throwaway tree."""
    shutil.copytree(PROJECT_ROOT / "chipsim", tmp_path / "chipsim")
    (tmp_path / "chipsim" / "eval" / "__init__.py").unlink()
    r = subprocess.run(
        [sys.executable, "-c", "import chipsim"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
        env={"PYTHONPATH": str(tmp_path), "PATH": "/usr/bin:/bin"},
    )
    assert r.returncode != 0, "import chipsim succeeded with a missing __init__.py"
    assert "scaffold is incomplete" in r.stderr
    assert "eval" in r.stderr


def test_s1_intact_tree_imports_cleanly(tmp_path):
    """Positive control for the test above — the copy itself is not what fails."""
    shutil.copytree(PROJECT_ROOT / "chipsim", tmp_path / "chipsim")
    r = subprocess.run(
        [sys.executable, "-c", "import chipsim"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
        env={"PYTHONPATH": str(tmp_path), "PATH": "/usr/bin:/bin"},
    )
    assert r.returncode == 0, r.stderr


# --------------------------------------------------------------------------- #
# S2 · dependency set
# --------------------------------------------------------------------------- #


def test_s2_requires_python(pyproject):
    assert pyproject["project"]["requires-python"] == ">=3.11,<3.13"


def test_s2_runtime_dependencies_present(pyproject):
    names = {
        d.split("==")[0].split(">=")[0].strip().lower()
        for d in pyproject["project"]["dependencies"]
    }
    assert {"pandas", "pyarrow", "pyyaml", "requests", "rdkit"} <= names


@pytest.mark.parametrize("pkg", ["pyarrow", "rdkit"])
def test_s2_serialization_critical_deps_are_pinned(pyproject, pkg):
    """pyarrow: parquet bytes are hashed (defect 27). rdkit: it computes the
    canonical InChIKey that every downstream join and the sealed allocation key on.
    Both must be == pinned, not floated."""
    dep = next(
        d
        for d in pyproject["project"]["dependencies"]
        if d.split("==")[0].split(">=")[0].strip().lower() == pkg
    )
    assert "==" in dep, f"{pkg} must be =='-pinned, got {dep!r}"


def test_s2_dev_group_complete(pyproject):
    dev = {
        d.split("==")[0].split(">=")[0].strip().lower()
        for d in pyproject["dependency-groups"]["dev"]
    }
    assert {"pytest", "pytest-cov", "ruff", "dvc"} <= dev


def test_s2_no_empty_dev_extra_shadowing_the_group(pyproject):
    """An empty [project.optional-dependencies] dev makes `pip install -e '.[dev]'`
    succeed while installing nothing — a silent no-op toolchain."""
    extras = pyproject.get("project", {}).get("optional-dependencies", {})
    assert not (("dev" in extras) and not extras["dev"]), (
        "empty 'dev' extra shadows the populated [dependency-groups] dev"
    )


# --------------------------------------------------------------------------- #
# S3 · pytest configuration
# --------------------------------------------------------------------------- #


def test_s3_testpaths_configured(pyproject):
    """S3's done-condition, asserted against config rather than the CLI.

    The plan words it as "`pytest --collect-only` exits non-zero if testpaths is
    removed". That is NOT achievable here: pytest's default norecursedirs skips
    .venv, so with testpaths removed it still discovers tests/ and exits 0
    (verified). Asserting the config is the honest form of the same guarantee.
    """
    assert pyproject["tool"]["pytest"]["ini_options"]["testpaths"] == ["tests"]


def test_s3_markers_registered(pyproject):
    markers = pyproject["tool"]["pytest"]["ini_options"]["markers"]
    names = {m.split(":")[0].strip() for m in markers}
    assert {"network", "integration"} <= names


# --------------------------------------------------------------------------- #
# S6 · configs
# --------------------------------------------------------------------------- #


def test_s6_env_yaml_parses():
    d = yaml.safe_load((PROJECT_ROOT / "configs" / "env.yaml").read_text())
    assert isinstance(d, dict) and {"paths", "snapshot"} <= d.keys()


@pytest.mark.parametrize("name", ["theta_priors.yaml", "assumptions.yaml"])
def test_s6_human_owned_configs_are_absent(name):
    """Global Constraint #1: no coding agent writes a biological number.

    These files are H-owned. Their ABSENCE is the mechanical form of that rule.
    """
    assert not (PROJECT_ROOT / "configs" / name).exists(), (
        f"configs/{name} exists — it is human-owned and no agent may create it"
    )


def test_s6_no_config_carries_a_bare_numeric_value():
    """Survives a rename of the two forbidden files.

    A biological number smuggled into any configs/*.yaml is the failure this
    guards, not the specific filename it arrives under.
    """

    def numeric_leaves(node, path=""):
        if isinstance(node, dict):
            for k, v in node.items():
                yield from numeric_leaves(v, f"{path}.{k}")
        elif isinstance(node, list):
            for i, v in enumerate(node):
                yield from numeric_leaves(v, f"{path}[{i}]")
        elif isinstance(node, (int, float)) and not isinstance(node, bool):
            yield path

    offenders = []
    for p in (PROJECT_ROOT / "configs").glob("*.yaml"):
        offenders += [f"{p.name}{loc}" for loc in numeric_leaves(yaml.safe_load(p.read_text()))]
    assert not offenders, (
        f"numeric value(s) in configs/ — biological numbers are H-owned: {offenders}"
    )


# --------------------------------------------------------------------------- #
# S7 · gitignore behaviour
# --------------------------------------------------------------------------- #


def _check_ignore(rel: str) -> bool:
    r = subprocess.run(
        ["git", "check-ignore", "-q", rel], cwd=PROJECT_ROOT, capture_output=True, check=False
    )
    return r.returncode == 0


@pytest.mark.integration
@pytest.mark.parametrize(
    "rel,should_be_ignored",
    [
        # bulk data never enters git
        ("data/raw/probe.tsv", True),
        ("data/raw/drugbank/drugbank.tsv", True),
        ("data/processed/drugbank_compounds.parquet", True),
        # ...but everything that makes it recoverable and auditable must stay tracked
        ("data/raw/drugbank.dvc", False),
        ("data/raw/drugbank/proteins.tsv.dvc", False),
        ("data/raw/drugbank/SHA256SUMS.json", False),  # T4 done-condition (d)
        ("data/raw/drugbank/provenance.yaml", False),  # T2/T1 human artifact
        ("data/raw/drugbank/PROVENANCE.md", False),  # T1 human artifact
        ("data/processed/drugbank_compounds.sha256", False),
        ("data/raw/.gitkeep", False),
    ],
)
def test_s7_gitignore_keeps_pointers_trackable(rel, should_be_ignored):
    """The first .gitignore satisfied S7's two stated probes while defeating its
    purpose: `data/raw/*` excluded the data/raw/drugbank/ DIRECTORY, and git cannot
    re-include a file under an excluded directory. That silently ignored T1/T2's
    provenance.yaml and T3/T4's SHA256SUMS.json."""
    assert _check_ignore(rel) is should_be_ignored


@pytest.mark.integration
def test_s7_dvc_store_is_never_committable():
    """The DVC remote holds the DrugBank snapshot as extensionless md5 blobs.
    T11's test_drugbank_not_vendored matches *.tsv and would not catch them."""
    assert _check_ignore(".dvc-storage/files/md5/ab/cdef0123")


# --------------------------------------------------------------------------- #
# S11 · module stubs
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("module,relpath", sorted(S11_MODULES.items()))
def test_s11_edit_targets_exist_and_import(module, relpath):
    """defect 12/13 was '(edit)' pointed at a nonexistent file. This is the guard."""
    import importlib

    assert (PROJECT_ROOT / relpath).is_file(), f"{relpath} missing"
    assert importlib.import_module(module) is not None


def test_s11_card_py_is_not_created():
    """defect 13: T17 was retargeted to provenance_block.py; M0c owns the card."""
    assert not (PROJECT_ROOT / "chipsim" / "eval" / "card.py").exists()
