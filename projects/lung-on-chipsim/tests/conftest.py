"""Shared pytest fixtures — build-plan S4.

`project_root` anchors every path so tests behave the same whether pytest is
invoked from the project root or the repository root. The loaders below read
ONLY from tests/fixtures/, never from configs/ or data/.
"""

from pathlib import Path

import pytest
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_DIR = PROJECT_ROOT / "tests" / "fixtures"


@pytest.fixture(scope="session")
def project_root() -> Path:
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def fixture_dir() -> Path:
    return FIXTURE_DIR


def load_fixture_yaml(name: str) -> dict:
    """Parse a fixture YAML by bare filename."""
    return yaml.safe_load((FIXTURE_DIR / name).read_text())


@pytest.fixture
def provenance_fixture() -> dict:
    return load_fixture_yaml("provenance.yaml")


@pytest.fixture
def provenance_fixture_path() -> Path:
    return FIXTURE_DIR / "provenance.yaml"


@pytest.fixture
def panel_ratified_path() -> Path:
    return FIXTURE_DIR / "barrier_panel_ratified.yaml"


@pytest.fixture
def panel_unratified_path() -> Path:
    return FIXTURE_DIR / "barrier_panel_unratified.yaml"


@pytest.fixture
def poc_roster_path() -> Path:
    return FIXTURE_DIR / "poc_compounds.yaml"


@pytest.fixture
def adjudication_blank_path() -> Path:
    return FIXTURE_DIR / "pgp_adjudication_blank.csv"


@pytest.fixture
def adjudication_filled_path() -> Path:
    return FIXTURE_DIR / "pgp_adjudication_filled.csv"


#: Every path fixture defined above, for the resolution test in test_scaffold-adjacent
#: coverage. Keeping the list here means a new fixture is one edit, not two.
PATH_FIXTURE_NAMES = (
    "provenance_fixture_path",
    "panel_ratified_path",
    "panel_unratified_path",
    "poc_roster_path",
    "adjudication_blank_path",
    "adjudication_filled_path",
)


@pytest.fixture(autouse=True)
def _isolate_seed_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Clear the seed env vars for EVERY test.

    Verified failure without this: `CHIPSIM_SEED=99 pytest` failed four seed
    tests, because `_resolve_seed` lets the env var override the config and the
    config-source tests inherited ambient state. A suite whose result depends on
    the operator's exported environment cannot be evidence of anything.
    """
    from chipsim.journal import SEED_ENV_VARS

    for name in SEED_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
