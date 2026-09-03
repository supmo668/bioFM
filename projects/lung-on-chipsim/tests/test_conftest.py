"""Fixture-resolution tests — build-plan S4.

S4's done-condition includes "conftest.py's fixtures resolve". Nothing exercised
them: coverage showed every fixture body unexecuted, because test_fixtures.py
re-derived the paths locally instead of requesting them. A conftest whose loaders
all returned a nonexistent path would have satisfied S4 as measured.
"""

from pathlib import Path

import pytest

from tests.conftest import PATH_FIXTURE_NAMES, load_fixture_yaml


def test_project_root_and_fixture_dir_agree(project_root, fixture_dir):
    assert project_root.is_dir()
    assert fixture_dir == project_root / "tests" / "fixtures"
    assert fixture_dir.is_dir()


@pytest.mark.parametrize("fixture_name", PATH_FIXTURE_NAMES)
def test_path_fixtures_point_at_real_files(fixture_name, request):
    """A typo'd filename in conftest would otherwise surface milestones later."""
    path = request.getfixturevalue(fixture_name)
    assert isinstance(path, Path)
    assert path.is_file(), f"{fixture_name} -> {path} does not exist"


def test_provenance_fixture_loads_as_a_mapping(provenance_fixture):
    assert isinstance(provenance_fixture, dict)
    assert provenance_fixture["source_repo"].endswith("dhimmel/drugbank")


def test_load_fixture_yaml_helper_works():
    assert load_fixture_yaml("barrier_panel_ratified.yaml")["ratified"] is True
