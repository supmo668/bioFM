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

from chipsim.pipeline import (
    ETL_SUBCOMMANDS,
    MODULE_PATH,
    NON_ETL_SUBCOMMANDS,
    NON_NODE_REASONS,
    WORKFLOW_NODE_SUBCOMMANDS,
    available_subcommands,
)

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
    # Every registered subcommand must be declared in exactly one category. The
    # ETL list stays exact — a rename or a stale entry still fails — while
    # panel-seal (T7a) is declared non-ETL because Global Constraint 4 reserves
    # running it to a human. That is a stated rule the digest cannot enforce, so
    # keeping it out of the exported workflow is the only mechanical support the
    # rule gets: an unattended pipeline must not be able to invoke it.
    assert set(registered) == set(ETL_SUBCOMMANDS) | set(NON_ETL_SUBCOMMANDS), (
        f"registered subcommands {registered} do not match the declared "
        f"ETL {ETL_SUBCOMMANDS} + non-ETL {NON_ETL_SUBCOMMANDS}"
    )
    assert not set(ETL_SUBCOMMANDS) & set(NON_ETL_SUBCOMMANDS), "a subcommand is in both categories"
    assert tuple(c for c in registered if c in ETL_SUBCOMMANDS) == ETL_SUBCOMMANDS, (
        "the ETL subcommands must stay registered in pipeline order"
    )

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


def test_the_node_list_is_a_SEPARATE_predicate_from_the_etl_list():
    """r2.34. "Is an ETL run" and "may be invoked unattended" have OPPOSITE safe directions —
    include for journalling, exclude for automation — so one membership test cannot serve both.

    `adjudication-worksheet` is the witness and the reason the rule was written: a genuine ETL stage
    (it reads the snapshot and writes a derived artifact, so it earns a per-run config snapshot and
    the §16 approval prompt) that no unattended chain may start, because regenerating a worksheet
    mid-adjudication destroys the premise of a 60-90 minute human task.

    If this assertion ever reads `set(ETL) == set(NODES)`, the two predicates have silently rejoined.
    """
    assert set(WORKFLOW_NODE_SUBCOMMANDS) < set(ETL_SUBCOMMANDS), (
        "every node must be an ETL stage, and the node list must be STRICTLY smaller — equality "
        "means the conflation r2.34 removed has come back"
    )
    assert "adjudication-worksheet" in ETL_SUBCOMMANDS
    assert "adjudication-worksheet" not in WORKFLOW_NODE_SUBCOMMANDS


def test_every_non_node_command_records_WHY(workflow):
    """The reasons differ and none is recoverable from tuple membership: `panel-seal` is excluded
    because Global Constraint 4 reserves it to a human; T13 because regenerating mid-adjudication
    destroys a human task's premise. A reader who sees only which tuple a command sits in learns
    neither."""
    registered = available_subcommands()
    non_nodes = [c for c in registered if c not in WORKFLOW_NODE_SUBCOMMANDS]

    assert non_nodes, "anti-vacuity: there must be commands outside the node list to explain"
    for command in non_nodes:
        assert command in NON_NODE_REASONS, (
            f"{command!r} is not a workflow node and records no reason. r2.34 requires the reason "
            f"to be written down, because it cannot be recovered from membership."
        )
        assert len(NON_NODE_REASONS[command]) > 40, f"{command!r}'s reason is a placeholder"

    assert set(NON_NODE_REASONS) == set(non_nodes), (
        "a reason for a command that IS a node, or that is not registered at all, is a stale "
        "entry — the same phantom the writer registry refuses"
    )


def test_the_exported_workflow_names_only_node_commands(workflow):
    """The check r2.34 requires: the JSON is validated against the NODE list, not the ETL list.

    Measured when this was written: the exported workflow names exactly the five node commands, and
    `adjudication-worksheet` was NOT among them — so T13 was never actually exported, though the
    conflated tuple said it was eligible. The hazard was latent rather than live, and this assertion
    is what keeps it that way.
    """
    for node in workflow["nodes"]:
        command = re.match(
            rf"^python -m {re.escape(MODULE_PATH)} (\S+)", node["parameters"]["command"]
        ).group(1)
        assert command in WORKFLOW_NODE_SUBCOMMANDS, (
            f"node {node['name']} invokes {command!r}, which is not declared as a workflow node. "
            f"Reason it must not be: {NON_NODE_REASONS.get(command, '(none recorded)')}"
        )
