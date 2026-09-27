"""Map Architect agent's proposed configuration to a concrete BackbonePredictor.

v0.5.0 widened the Architect config space so downstream code
(``loop.py``, ``Trainer``) can consume ``{backbone, hvg_count, lr, ...}``
instead of just a backbone string. See
``.claude/plans/v0.5.0-real-perturb-seq.md`` §Phase 2.
"""

from __future__ import annotations

from collections.abc import Collection, Mapping
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
        reason = "torch is not importable" if resolved == "scgpt_small" else "not available"
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


# A2-3: every agent-controlled field, its default, and the key each tier states
# it under (schema names; ``n_top_hvg`` / ``pct_mito_max`` are the legacy
# DataCurator keys still emitted by the non-LLM mock pool). Precedence per
# field: Validator delta > Architect > DataCurator > Trainer > default. The
# Trainer tier is not named in amendment 2; it sits just above the default so
# the Trainer's own schema fields are applied only when no ranked tier states
# them (it overlaps the Architect only on learning_rate / ridge_lambda / epochs).
APPLIED_FIELDS: dict[str, dict[str, Any]] = {
    "backbone": {"default": "linear", "architect": ("backbone",)},
    "hvg_count": {
        "default": 2000,
        "architect": ("hvg_count",),
        "datacurator": ("hvg_count", "n_top_hvg"),
    },
    "qc_mito_max": {"default": 12.0, "datacurator": ("qc_mito_max", "pct_mito_max")},
    "learning_rate": {"default": 1e-2, "architect": ("learning_rate",), "trainer": ("lr",)},
    "ridge_lambda": {"default": 1.0, "architect": ("ridge_lambda",), "trainer": ("ridge_lambda",)},
    "epochs": {"default": 40, "architect": ("epochs",), "trainer": ("epochs",)},
}
_TIERS = ("architect", "datacurator", "trainer")


def _stated_value(
    content: Mapping[str, Any] | None, stated: Collection[str] | None, keys: tuple[str, ...]
) -> tuple[bool, Any]:
    """``(True, value)`` for the first of ``keys`` the tier STATED.

    ``stated=None`` (a non-LLM pool, which reports no stated set) treats every
    key present in ``content`` as stated. For an LLM step ``stated`` is the
    parsed model's ``model_fields_set``: a schema default is not a statement.
    """
    if not content:
        return False, None
    for key in keys:
        if key in content and content[key] is not None and (stated is None or key in stated):
            return True, content[key]
    return False, None


def resolve_applied_config(
    *,
    datacurator: Mapping[str, Any] | None,
    datacurator_stated: Collection[str] | None,
    architect: Mapping[str, Any] | None,
    architect_stated: Collection[str] | None,
    critique_delta: Optional[Mapping[str, Any]],
    trainer: Mapping[str, Any] | None = None,
    trainer_stated: Collection[str] | None = None,
) -> tuple[dict[str, Any], dict[str, str]]:
    """The applied configuration for one round, and which tier supplied each field (A2-3).

    Returns ``(values, sources)`` over :data:`APPLIED_FIELDS`; each source is
    ``"validator"``, ``"architect"``, ``"datacurator"``, ``"trainer"`` or
    ``"default"``. Backbone names are canonicalised by :func:`_canonical_backbone`.
    """
    tiers = {
        "architect": (architect, architect_stated),
        "datacurator": (datacurator, datacurator_stated),
        "trainer": (trainer, trainer_stated),
    }
    delta = dict(critique_delta or {})
    values: dict[str, Any] = {}
    sources: dict[str, str] = {}
    for name, spec in APPLIED_FIELDS.items():
        if name in delta and delta[name] is not None:
            values[name], sources[name] = delta[name], "validator"
        else:
            values[name], sources[name] = spec["default"], "default"
            for tier in _TIERS:
                keys = spec.get(tier)
                if not keys:
                    continue
                content, stated = tiers[tier]
                found, val = _stated_value(content, stated, keys)
                if found:
                    values[name], sources[name] = val, tier
                    break
    values["backbone"] = _canonical_backbone(str(values["backbone"]))
    values["hvg_count"] = int(values["hvg_count"])
    values["epochs"] = int(values["epochs"])
    for k in ("qc_mito_max", "learning_rate", "ridge_lambda"):
        values[k] = float(values[k])
    return values, sources


def dispatch_architect(proposal: dict) -> tuple:
    """Backward-compatible tuple return used by :mod:`loop`.

    New callers should prefer :func:`resolve_architect_config`.
    """
    cfg = resolve_architect_config(proposal)
    backbone = build_backbone(cfg["backbone"])
    return backbone, cfg["backbone"]
