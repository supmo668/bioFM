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
    ArchitectProposal,
    DataCuratorProposal,
    LiteratureProposal,
    TrainerProposal,
    ValidatorProposal,
    parse_proposal,
)
from perturb_eval.llm.openrouter_client import ChatResult, OpenRouterError

logger = logging.getLogger(__name__)


class _ClientLike(Protocol):
    def chat_json(
        self,
        *,
        role: str,
        task_id: str,
        round_index: int,
        prompt: str,
        seed: int,
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


_SYSTEM_PREAMBLE = (
    "You are a {role} agent in a Perturb-seq experimental-design lifecycle. "
    "Respond ONLY with a single JSON object matching the declared schema. "
    "No markdown fences, no commentary, just JSON."
)


def _architect_prompt(task_id: str, round_index: int, context: dict) -> str:
    prior = context.get("last_msd")
    delta = context.get("validator_critique_delta") or {}
    failed = context.get("validator_failed_genes") or ()
    lit = context.get("literature") or {}
    return (
        _SYSTEM_PREAMBLE.format(role="Architect")
        + "\n\nTask: held-out perturbation {task_id} (round {r}).\n"
        "Prior round MSD: {prior}\n"
        "Validator suggested config delta: {delta}\n"
        "Top-failed genes in prior round: {failed}\n"
        "Literature prior (expected_up={up}, expected_down={down}).\n\n"
        "Schema:\n"
        "{{\n"
        '  "backbone": one of "linear" | "mlp" | "scgpt_small",\n'
        '  "n_agents": int 2..8,\n'
        '  "n_rounds": int 1..5,\n'
        '  "hvg_count": one of 500 | 1000 | 2000 | 5000,\n'
        '  "learning_rate": float > 0,\n'
        '  "ridge_lambda": float >= 0,\n'
        '  "epochs": int 1..500\n'
        "}}"
    ).format(
        task_id=task_id,
        r=round_index,
        prior=prior,
        delta=json.dumps(delta),
        failed=list(failed)[:5],
        up=list(lit.get("expected_up", ()))[:5],
        down=list(lit.get("expected_down", ()))[:5],
    )


def _simple_prompt(role: str, task_id: str, round_index: int, context: dict) -> str:
    return (
        _SYSTEM_PREAMBLE.format(role=role)
        + f"\n\nTask: {task_id} (round {round_index}).\n"
        f"Context: {json.dumps({k: str(v)[:120] for k, v in context.items()})}\n\n"
        "Respond with a JSON object matching the role's declared schema."
    )


def _rule_based_fallback(role: str, context: dict) -> dict:
    """Deterministic schema-valid default when the LLM is unavailable."""
    delta = context.get("validator_critique_delta") or {}
    if role == "DataCurator":
        return DataCuratorProposal().model_dump()
    if role == "Literature":
        return LiteratureProposal().model_dump()
    if role == "Architect":
        base = ArchitectProposal().model_dump()
        # Apply any critique delta deterministically so fallback still
        # refines between rounds.
        for k, v in delta.items():
            if k in base:
                base[k] = v
        return base
    if role == "Trainer":
        return TrainerProposal().model_dump()
    if role == "Validator":
        return ValidatorProposal().model_dump()
    raise ValueError(f"unknown role {role}")


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
    ) -> dict:
        if role == "Architect":
            prompt = _architect_prompt(task_id, round_index, context)
        else:
            prompt = _simple_prompt(role, task_id, round_index, context)

        try:
            result = self.client.chat_json(
                role=role,
                task_id=task_id,
                round_index=round_index,
                prompt=prompt,
                seed=seed,
            )
            parsed = parse_proposal(role, result.content).model_dump()
        except FALLBACK_EXCEPTIONS as exc:
            self._log.warning(
                "LLM pool: role=%s fallback (%s: %s)", role, type(exc).__name__, exc
            )
            fallback = _rule_based_fallback(role, context)
            return {
                "content": fallback,
                "rationale": str(fallback.get("rationale", "")),
                "confidence": 0.7,
                "model_id": None,
                "source": "fallback",
            }

        raw = result.content
        return {
            "content": parsed,
            "rationale": str(raw.get("rationale", parsed.get("rationale", ""))),
            "confidence": float(raw.get("confidence", 0.7)),
            "model_id": result.model_id,
            "source": "llm",
        }


__all__ = ["FALLBACK_EXCEPTIONS", "LLMAgentPool"]
