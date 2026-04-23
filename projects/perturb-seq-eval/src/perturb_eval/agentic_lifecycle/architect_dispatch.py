"""Map Architect agent's proposed backbone to a concrete BackbonePredictor."""

from __future__ import annotations

from perturb_eval.backbones import available_backbones, build_backbone


def dispatch_architect(proposal: dict) -> tuple:
    """Returns (backbone_instance, chosen_name). Falls back when unknown."""
    requested = str(proposal.get("backbone", "linear")).lower()
    alias = {
        "scgpt": "scgpt_small",
        "sc_gpt": "scgpt_small",
        "scgpt_whole_human": "scgpt_small",
        "scfoundation": "mlp",
    }
    resolved = alias.get(requested, requested)
    if resolved not in available_backbones():
        resolved = "linear"
    backbone = build_backbone(resolved)
    return backbone, resolved
