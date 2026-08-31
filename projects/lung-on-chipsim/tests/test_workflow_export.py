"""ETL workflow export — build-plan T16 (DESCOPED form, see plan section 7).

r1 required a provisioned, running n8n instance and a "byte-identical"
done-condition that was unfalsifiable (no committed baseline, no remote, parquet
bytes not stable across versions) — defects 27, 28. Slice 1 validates the export
STRUCTURALLY instead:

  (a) the JSON parses and carries the five nodes in a connected chain;
  (b) **each node names a CLI entrypoint that exists in the installed package** —
      checked against the parser itself, so a renamed subcommand fails here;
  (c) the recorded sha256 of the processed parquet equals its .sha256 sidecar.

**Not in slice 1:** provisioning n8n and running the workflow end-to-end (T16a).
"""

from __future__ import annotations

import json
import re
from itertools import pairwise
from pathlib import Path

import pytest

from chipsim.pipeline import MODULE_PATH, SUBCOMMANDS, available_subcommands

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = PROJECT_ROOT / "orchestration" / "n8n" / "etl_drugbank.json"

EXPECTED_NODES = ("fetch", "hash-verify", "parse", "provenance-tests", "write")


@pytest.fixture(scope="module")
def workflow() -> dict:
    return json.loads(WORKFLOW.read_text())


def test_t16_export_exists_and_parses(workflow):
    assert workflow["name"]
    assert isinstance(workflow["nodes"], list)


def test_t16_has_the_five_nodes_in_order(workflow):
    assert tuple(n["name"] for n in workflow["nodes"]) == EXPECTED_NODES


def test_t16_validates_against_the_n8n_workflow_schema(workflow):
    """The structural contract n8n itself requires of an importable workflow."""
    assert set(workflow) >= {"name", "nodes", "connections"}
    for node in workflow["nodes"]:
        assert set(node) >= {"parameters", "name", "type", "typeVersion", "position"}
        assert isinstance(node["position"], list) and len(node["position"]) == 2
        assert node["type"].startswith("n8n-nodes-base.")
        assert isinstance(node["typeVersion"], int)

    names = {n["name"] for n in workflow["nodes"]}
    for source, spec in workflow["connections"].items():
        assert source in names
        for group in spec["main"]:
            for link in group:
                assert link["node"] in names, f"connection to unknown node {link['node']}"


def test_t16_nodes_form_a_single_connected_chain(workflow):
    """fetch -> hash-verify -> parse -> provenance-tests -> write."""
    for source, target in pairwise(EXPECTED_NODES):
        assert workflow["connections"][source]["main"][0][0]["node"] == target
    assert EXPECTED_NODES[-1] not in workflow["connections"], "write must be terminal"


def test_t16_every_node_names_a_real_cli_entrypoint(workflow):
    """T16's load-bearing done-condition. Checked against the parser's registered
    subcommands rather than a restated list, so a rename cannot pass silently."""
    registered = available_subcommands()
    assert registered == SUBCOMMANDS

    for node in workflow["nodes"]:
        command = node["parameters"]["command"]
        match = re.match(rf"^python -m {re.escape(MODULE_PATH)} (\S+)", command)
        assert match, f"node {node['name']} does not invoke {MODULE_PATH}: {command!r}"
        assert match.group(1) in registered, (
            f"node {node['name']} names subcommand {match.group(1)!r}, which is not "
            f"registered. Available: {registered}"
        )


def test_t16_provenance_node_is_not_called_contract_tests(workflow):
    """§4.5 sanctions *data*-contract tests, which arrive with the ChEMBL plan
    (defect 29). Naming this node 'contract tests' would claim a check slice 1
    does not perform."""
    names = {n["name"] for n in workflow["nodes"]}
    assert "provenance-tests" in names
    assert "contract tests" not in names


def test_t16_module_is_importable_as_a_cli():
    """`python -m chipsim.pipeline` must actually resolve."""
    import importlib

    module = importlib.import_module(MODULE_PATH)
    assert hasattr(module, "main")


def test_t16_recorded_digest_matches_the_sidecar(tmp_path):
    """Condition (c). Exercised against a generated artifact, because
    data/processed/drugbank_compounds.parquet is blocked on T2/T4a."""
    import hashlib

    import pandas as pd

    from chipsim.harmonize.ids import add_canonical_identity
    from chipsim.ingest.drugbank_snapshot import (
        load_compounds,
        read_digest_sidecar,
        write_compounds,
    )

    compounds = add_canonical_identity(
        load_compounds(PROJECT_ROOT / "tests" / "fixtures" / "snapshot", min_rows=0)
    )
    out = tmp_path / "drugbank_compounds.parquet"
    write_compounds(compounds, out)

    assert read_digest_sidecar(out) == hashlib.sha256(out.read_bytes()).hexdigest()
    assert isinstance(pd.read_parquet(out, engine="pyarrow"), pd.DataFrame)
