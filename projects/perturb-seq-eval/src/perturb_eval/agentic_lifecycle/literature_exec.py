"""Extract expected-up/down gene lists + pathways from the Literature agent.

The Literature agent uses BioGPTMechanismTool in the BioFM-grounded
configuration; this executor passes its structured proposal through
so downstream components (Validator) can reference the same gene set.
"""

from __future__ import annotations


def extract_expected_genes(proposal: dict) -> dict:
    return {
        "up": list(proposal.get("expected_up", [])),
        "down": list(proposal.get("expected_down", [])),
        "pathways": list(proposal.get("pathways", [])),
    }
