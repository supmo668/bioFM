"""Map Architect agent's proposed configuration to a concrete BackbonePredictor.

v0.5.0 widened the Architect config space so downstream code
(``loop.py``, ``Trainer``) can consume ``{backbone, hvg_count, lr, ...}``
instead of just a backbone string. See
``.claude/plans/v0.5.0-real-perturb-seq.md`` §Phase 2.
"""

from __future__ import annotations

from typing import Any, Optional

from perturb_eval.backbones import available_backbones, build_backbone

_ALIAS = {
    "scgpt": "scgpt_small",
    "sc_gpt": "scgpt_small",
    "scgpt_whole_human": "scgpt_small",
    "scgpt_perturb": "scgpt_small",
    "scfoundation": "mlp",
    "geneformer": "mlp",
}


def _canonical_backbone(name: str) -> str:
    lower = name.strip().lower()
    resolved = _ALIAS.get(lower, lower)
    return resolved if resolved in available_backbones() else "linear"


def resolve_architect_config(
    proposal: dict,
    *,
    critique_delta: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Merge an Architect proposal + (optional) validator critique delta.

    Returns a fully-populated config dict with keys
    ``{backbone, hvg_count, learning_rate, ridge_lambda, epochs,
    n_agents, n_rounds}``. Unknown backbones are canonicalised via the
    alias table and fall back to ``linear`` if still unrecognised.

    Parameters
    ----------
    proposal
        Raw Architect output (dict). May be partial — missing keys take
        module defaults.
    critique_delta
        Validator's ``suggested_next_config_delta`` from the previous
        round. Applied after the base proposal; invalid backbone deltas
        are silently ignored (we fall back to the proposal's backbone).
    """
    cfg: dict[str, Any] = {
        "backbone": "linear",
        "hvg_count": 2000,
        "learning_rate": 1e-2,
        "ridge_lambda": 1.0,
        "epochs": 40,
        "n_agents": 5,
        "n_rounds": 2,
    }
    for key, default in cfg.items():
        if key in proposal and proposal[key] is not None:
            cfg[key] = proposal[key]
        else:
            cfg[key] = default

    if "backbone" in proposal:
        cfg["backbone"] = _canonical_backbone(str(proposal["backbone"]))

    if critique_delta:
        for key, val in critique_delta.items():
            if key == "backbone":
                canon = _canonical_backbone(str(val))
                cfg["backbone"] = canon
            elif key in cfg:
                cfg[key] = val

    # Final sanity pass on backbone in case delta introduced junk.
    cfg["backbone"] = _canonical_backbone(str(cfg["backbone"]))
    return cfg


def dispatch_architect(proposal: dict) -> tuple:
    """Backward-compatible tuple return used by :mod:`loop`.

    New callers should prefer :func:`resolve_architect_config`.
    """
    cfg = resolve_architect_config(proposal)
    backbone = build_backbone(cfg["backbone"])
    return backbone, cfg["backbone"]
