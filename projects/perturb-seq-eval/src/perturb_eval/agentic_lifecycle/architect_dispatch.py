"""Map Architect agent's proposed configuration to a concrete BackbonePredictor.

v0.5.0 widened the Architect config space so downstream code
(``loop.py``, ``Trainer``) can consume ``{backbone, hvg_count, lr, ...}``
instead of just a backbone string. See
``.claude/plans/v0.5.0-real-perturb-seq.md`` §Phase 2.
"""

from __future__ import annotations

from typing import Any, Optional

from perturb_eval.backbones import _REGISTRY, available_backbones, build_backbone

_ALIAS = {
    "scgpt": "scgpt_small",
    "sc_gpt": "scgpt_small",
    "scgpt_whole_human": "scgpt_small",
    "scgpt_perturb": "scgpt_small",
    "scfoundation": "mlp",
    "geneformer": "mlp",
}


class BackboneUnavailableError(RuntimeError):
    """A KNOWN backbone (registry or alias) cannot be built in this environment.

    C-TORCH-2 (CTO #241): never degraded to ``linear`` — that would make the
    Architect's backbone distribution measure the import, not the agent.
    """


def _canonical_backbone(name: str) -> str:
    """Canonicalise an Architect backbone name.

    * unknown name (not in the registry, not an alias) -> ``"linear"``
      (documented fallback for free-text LLM output);
    * known name not in :func:`available_backbones` -> raises
      :class:`BackboneUnavailableError` (C-TORCH-2).
    """
    lower = name.strip().lower()
    resolved = _ALIAS.get(lower, lower)
    if resolved not in _REGISTRY:
        return "linear"
    available = available_backbones()
    if resolved not in available:
        reason = (
            "torch is not importable" if resolved == "scgpt_small" else "not available"
        )
        raise BackboneUnavailableError(
            f"backbone {resolved!r} (requested as {name!r}) is known but unavailable in "
            f"this environment: {reason}; available: {sorted(available)}"
        )
    return resolved


def resolve_architect_config(
    proposal: dict,
    *,
    critique_delta: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Merge an Architect proposal + (optional) validator critique delta.

    Returns a fully-populated config dict with keys
    ``{backbone, hvg_count, learning_rate, ridge_lambda, epochs,
    n_agents, n_rounds}``. Unknown backbones are canonicalised via the
    alias table and fall back to ``linear`` if still unrecognised; a known
    backbone that is unavailable here raises :class:`BackboneUnavailableError`.

    Parameters
    ----------
    proposal
        Raw Architect output (dict). May be partial — missing keys take
        module defaults.
    critique_delta
        Validator's ``suggested_next_config_delta`` from the previous
        round. Applied after the base proposal; an unrecognised backbone
        delta canonicalises to ``linear``; a known-but-unavailable one raises.
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
