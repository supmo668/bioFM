"""LLM-driven :class:`AgentPool` for the v0.5.0 lifecycle.

Each of the five agents emits a Pydantic-validated proposal, with the
validator's structured critique threaded into the next round's Architect
prompt. On LLM failure (rate-limited, parse error, network), a
deterministic rule-based fallback keeps the lifecycle runnable — the
paper's §5 freedom analysis filters those rows out of the entropy calc.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from perturb_eval.agentic_lifecycle.proposal_schema import (
    ArchitectProposal,
    DataCuratorProposal,
    LiteratureProposal,
    TrainerProposal,
    ValidatorProposal,
    parse_proposal,
)

logger = logging.getLogger(__name__)


class _ClientLike(Protocol):
    def chat_json(
        self,
        *,
        role: str,
        task_id: str,
        round_index: int,
        prompt: str,
    ) -> dict: ...


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
    ) -> dict:
        if role == "Architect":
            prompt = _architect_prompt(task_id, round_index, context)
        else:
            prompt = _simple_prompt(role, task_id, round_index, context)

        try:
            raw = self.client.chat_json(
                role=role,
                task_id=task_id,
                round_index=round_index,
                prompt=prompt,
            )
        except Exception as exc:  # noqa: BLE001 — any LLM failure falls back
            self._log.warning("LLM pool: role=%s fallback (%s)", role, exc)
            raw = _rule_based_fallback(role, context)

        # Schema-validate. On Pydantic failure, fall back to defaults.
        try:
            parsed = parse_proposal(role, raw).model_dump()
        except Exception as exc:  # noqa: BLE001
            self._log.warning("LLM pool: role=%s parse fallback (%s)", role, exc)
            parsed = _rule_based_fallback(role, context)

        return {
            "content": parsed,
            "rationale": str(raw.get("rationale", parsed.get("rationale", ""))),
            "confidence": float(raw.get("confidence", 0.7)),
        }


__all__ = ["LLMAgentPool"]
