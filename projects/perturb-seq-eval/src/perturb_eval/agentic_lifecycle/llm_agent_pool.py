"""LLM-driven :class:`AgentPool` for the v0.5.0 lifecycle.

Each of the five agents emits a Pydantic-validated proposal, with the
validator's structured critique threaded into the next round's Architect
prompt. On a *documented runtime* LLM failure (see
:data:`FALLBACK_EXCEPTIONS`) a deterministic rule-based fallback keeps the
lifecycle runnable; the proposal is tagged ``source="fallback"``,
``model_id=None`` so the analyser excludes it from entropy (D4) and the
real sweep can refuse the run (C-KEY-2). Programming errors (TypeError,
AttributeError, NameError, KeyError, ...) propagate — they never
masquerade as a fallback.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

import requests
from pydantic import ValidationError

from perturb_eval.agentic_lifecycle.proposal_schema import (
    BACKBONE_MENU,
    parse_proposal,
    schema_defaults,
)
from perturb_eval.llm.openrouter_client import ChatResult, OpenRouterError

logger = logging.getLogger(__name__)

_ROLES = ("DataCurator", "Literature", "Architect", "Trainer", "Validator")


class _ClientLike(Protocol):
    def chat_json(
        self,
        *,
        role: str,
        task_id: str,
        round_index: int,
        prompt: str,
        seed: int,
        dataset: str,
    ) -> ChatResult: ...


# The ONLY exceptions that may turn an LLM proposal into a rule-based
# fallback. Everything else is a bug in our code and must propagate.
#   * OpenRouterError (incl. RateLimitedError): pool exhausted / every
#     candidate failed on HTTP status or JSON parse after the reformat retry.
#   * requests.RequestException: network / HTTP transport failure raised by
#     ``session.post`` (ConnectionError, Timeout, HTTPError, ...).
#   * json.JSONDecodeError: unparseable model output reaching us.
#   * pydantic.ValidationError: the served JSON violates the role schema
#     (including a non-object payload).
FALLBACK_EXCEPTIONS: tuple[type[BaseException], ...] = (
    OpenRouterError,
    requests.RequestException,
    json.JSONDecodeError,
    ValidationError,
)


# Amendment 2 (A2-8): every prompt for every role states the dataset and its
# modality in the system preamble. Keyed by the sweep's dataset name; an
# unknown dataset is refused (never a prompt without it).
DATASET_DESCRIPTIONS: dict[str, str] = {
    "adamson_full": "Adamson 2016: K562 cells, CRISPR interference (CRISPRi, knockdown)",
    "adamson": "Adamson 2016: K562 cells, CRISPR interference (CRISPRi, knockdown)",
    "norman": "Norman 2019: K562 cells, CRISPR activation (CRISPRa, overexpression)",
}

_SYSTEM_PREAMBLE = (
    "You are a {role} agent in a Perturb-seq experimental-design lifecycle. "
    "Dataset: {dataset_description}. "
    "Respond ONLY with a single JSON object matching the declared schema. "
    "No markdown fences, no commentary, just JSON."
)

# A2-1: the required, verbalised confidence line every role's schema carries.
_CONFIDENCE_LINE = (
    '  "confidence": number in [0, 1], your own confidence in this proposal '
    "(required; a missing or out-of-range value is rejected)"
)

# A2-6: the pinned menu, as the Architect sees it.
_BACKBONE_CHOICES = " | ".join(f'"{b}"' for b in BACKBONE_MENU)

_ROLE_SCHEMA_LINES: dict[str, tuple[str, ...]] = {
    "DataCurator": (
        '  "hvg_method": one of "seurat" | "scanpy",',
        '  "hvg_count": one of 500 | 1000 | 2000 | 5000,',
        '  "qc_mito_max": float in (0, 100],',
        '  "split_strategy": one of "per_pert_holdout" | "unseen_gene",',
        '  "batch_correction": one of "none" | "combat" | "harmony",',
    ),
    "Literature": (
        '  "pathway_prior": object mapping gene -> weight in [0, 1],',
        '  "ppi_neighbors": list of gene symbols,',
        '  "tool_calls": list of strings,',
        '  "expected_up": list of gene symbols,',
        '  "expected_down": list of gene symbols,',
    ),
    "Architect": (
        f'  "backbone": one of {_BACKBONE_CHOICES} (required),',
        '  "n_agents": int 2..8,',
        '  "n_rounds": int 1..5,',
        '  "hvg_count": one of 500 | 1000 | 2000 | 5000,',
        '  "learning_rate": float > 0,',
        '  "ridge_lambda": float >= 0,',
        '  "epochs": int 1..500,',
    ),
    "Trainer": (
        '  "lr": float > 0,',
        '  "epochs": int 1..500,',
        '  "ridge_lambda": float >= 0,',
    ),
    "Validator": (
        '  "dynamic_threshold_msd": float in [0.02, 0.3],',
        (
            '  "critique": {"which_genes_failed": [...], '
            '"suggested_next_config_delta": {...}, "accept_reason": "..."},'
        ),
    ),
}


def _preamble(role: str, dataset: str) -> str:
    try:
        desc = DATASET_DESCRIPTIONS[dataset]
    except KeyError:
        raise ValueError(
            f"unknown dataset {dataset!r}: no dataset/modality description "
            f"(A2-8); known: {sorted(DATASET_DESCRIPTIONS)}"
        ) from None
    return _SYSTEM_PREAMBLE.format(role=role, dataset_description=desc)


def _schema_block(role: str) -> str:
    lines = (*_ROLE_SCHEMA_LINES[role], _CONFIDENCE_LINE)
    return "Schema:\n{\n" + "\n".join(lines) + "\n}"


def _architect_prompt(task_id: str, round_index: int, context: dict, dataset: str) -> str:
    prior = context.get("last_msd")
    delta = context.get("validator_critique_delta") or {}
    failed = context.get("validator_failed_genes") or ()
    lit = context.get("literature") or {}
    return (
        _preamble("Architect", dataset) + "\n\nTask: held-out perturbation {task_id} (round {r}).\n"
        "Prior round MSD: {prior}\n"
        "Validator suggested config delta: {delta}\n"
        "Top-failed genes in prior round: {failed}\n"
        "Literature prior (expected_up={up}, expected_down={down}).\n\n"
    ).format(
        task_id=task_id,
        r=round_index,
        prior=prior,
        delta=json.dumps(delta),
        failed=list(failed)[:5],
        up=list(lit.get("expected_up", ()))[:5],
        down=list(lit.get("expected_down", ()))[:5],
    ) + _schema_block("Architect")


def _simple_prompt(role: str, task_id: str, round_index: int, context: dict, dataset: str) -> str:
    return (
        _preamble(role, dataset) + f"\n\nTask: {task_id} (round {round_index}).\n"
        f"Context: {json.dumps({k: str(v)[:120] for k, v in context.items()})}\n\n"
        + _schema_block(role)
    )


def _rule_based_fallback(role: str, context: dict) -> dict:
    """Deterministic default content when the LLM step failed.

    Only the schema's OPTIONAL fields are filled: no ``confidence`` and no
    Architect ``backbone`` is ever invented (A2-1/A2-6). The step is tagged
    ``source="fallback"``, which makes the run invalid (C-KEY-2).
    """
    if role not in _ROLES:
        raise ValueError(f"unknown role {role}")
    base = schema_defaults(role)
    if role == "Architect":
        # Apply any critique delta deterministically so fallback still
        # refines between rounds (a delta ``backbone`` is the Validator's, not
        # a stated one; the loop records stated=None for this step).
        delta = context.get("validator_critique_delta") or {}
        for k, v in delta.items():
            if k in base:
                base[k] = v
    return base


@dataclass
class LLMAgentPool:
    """Real-LLM agent pool that plugs into :func:`run_agentic_lifecycle`."""

    client: _ClientLike
    cache_dir: Path
    _log: logging.Logger = field(default_factory=lambda: logger)

    def propose(
        self,
        role: str,
        round_index: int,
        task_id: str,
        context: dict,
        *,
        seed: int,
        dataset: str,
    ) -> dict:
        # ``dataset`` goes into the client's cache key (QG C6) and, with its
        # modality, into every role's system preamble (A2-8).
        if role == "Architect":
            prompt = _architect_prompt(task_id, round_index, context, dataset)
        else:
            prompt = _simple_prompt(role, task_id, round_index, context, dataset)

        try:
            result = self.client.chat_json(
                role=role,
                task_id=task_id,
                round_index=round_index,
                prompt=prompt,
                seed=seed,
                dataset=dataset,
            )
            # A2-1/A2-6: a missing / non-numeric / non-finite / out-of-range
            # confidence, or a missing / off-menu Architect backbone, raises
            # ValidationError here -> fallback -> run invalid.
            model = parse_proposal(role, result.content)
        except FALLBACK_EXCEPTIONS as exc:
            self._log.warning("LLM pool: role=%s fallback (%s: %s)", role, type(exc).__name__, exc)
            fallback = _rule_based_fallback(role, context)
            return {
                "content": fallback,
                "rationale": "",
                # A2-1: never imputed. A fallback step has no stated confidence.
                "confidence": None,
                "model_id": None,
                "source": "fallback",
                "stated_fields": (),
            }

        raw = result.content
        return {
            "content": model.model_dump(exclude={"confidence"}),
            "rationale": str(raw.get("rationale", "")),
            "confidence": float(model.confidence),
            "model_id": result.model_id,
            "source": "llm",
            "cache_hit": bool(result.cache_hit),
            # A2-3: the fields the model actually stated (schema defaults
            # filled the rest); config precedence reads only stated fields.
            "stated_fields": tuple(sorted(model.model_fields_set - {"confidence"})),
        }


__all__ = ["DATASET_DESCRIPTIONS", "FALLBACK_EXCEPTIONS", "LLMAgentPool"]
