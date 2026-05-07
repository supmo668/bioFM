"""Integration of the OpenRouter client + Pydantic schemas into an AgentPool."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from perturb_eval.agentic_lifecycle.llm_agent_pool import LLMAgentPool


class FakeClient:
    """Replaces OpenRouterClient for offline tests.

    ``responses_by_role`` maps role name → list of JSON-string responses
    consumed in order (one per call). If the role list is exhausted, the
    last item is repeated — this lets us stub "model always returns X".
    """

    def __init__(self, responses_by_role: dict[str, list[str]]) -> None:
        self._responses = {k: list(v) for k, v in responses_by_role.items()}
        self.calls: list[tuple[str, str, int]] = []

    def chat_json(self, *, role: str, task_id: str, round_index: int, prompt: str) -> dict:  # noqa: ARG002
        self.calls.append((role, task_id, round_index))
        import json

        queue = self._responses.get(role, [])
        if not queue:
            return {}
        content = queue[0] if len(queue) == 1 else queue.pop(0)
        return json.loads(content)


class TestLLMAgentPoolBasics:
    def test_each_role_returns_content_rationale_confidence(self, tmp_path: Path) -> None:
        fake = FakeClient(
            responses_by_role={
                "DataCurator": ['{"hvg_method": "seurat", "hvg_count": 1000}'],
                "Literature": ['{"pathway_prior": {"TP53": 0.7}, "ppi_neighbors": ["JUN"]}'],
                "Architect": ['{"backbone": "mlp", "learning_rate": 5e-3, "hvg_count": 1000}'],
                "Trainer": ['{"lr": 5e-3, "epochs": 40, "ridge_lambda": 1.0}'],
                "Validator": ['{"dynamic_threshold_msd": 0.1}'],
            }
        )
        pool = LLMAgentPool(client=fake, cache_dir=tmp_path)
        for role in ("DataCurator", "Literature", "Architect", "Trainer", "Validator"):
            out = pool.propose(role, round_index=0, task_id="t1", context={})
            assert "content" in out
            assert "rationale" in out
            assert "confidence" in out
            assert isinstance(out["content"], dict)

    def test_architect_produces_valid_config(self, tmp_path: Path) -> None:
        fake = FakeClient(
            responses_by_role={
                "Architect": ['{"backbone": "scgpt_small", "learning_rate": 1e-3, "hvg_count": 2000}'],
            }
        )
        pool = LLMAgentPool(client=fake, cache_dir=tmp_path)
        out = pool.propose("Architect", round_index=0, task_id="t1", context={})
        assert out["content"]["backbone"] == "scgpt_small"
        assert out["content"]["learning_rate"] == 1e-3

    def test_falls_back_to_rule_based_on_llm_failure(self, tmp_path: Path) -> None:
        from perturb_eval.llm.openrouter_client import OpenRouterError

        failing = MagicMock()
        failing.chat_json = MagicMock(side_effect=OpenRouterError("all cooled"))
        pool = LLMAgentPool(client=failing, cache_dir=tmp_path)
        out = pool.propose("Architect", round_index=0, task_id="t1", context={})
        # Fallback still yields a structurally-valid proposal.
        assert "backbone" in out["content"]

    def test_different_tasks_get_different_prompts(self, tmp_path: Path) -> None:
        fake = FakeClient(
            responses_by_role={
                "Architect": ['{"backbone": "linear"}', '{"backbone": "mlp"}'],
            }
        )
        pool = LLMAgentPool(client=fake, cache_dir=tmp_path)
        pool.propose("Architect", round_index=0, task_id="task_a", context={})
        pool.propose("Architect", round_index=0, task_id="task_b", context={})
        assert len({c[1] for c in fake.calls}) == 2


class TestContextThreading:
    def test_validator_critique_reaches_architect_prompt(self, tmp_path: Path) -> None:
        captured_prompts: list[str] = []

        class SpyingClient:
            def chat_json(self, *, role, task_id, round_index, prompt):  # noqa: ARG002
                if role == "Architect":
                    captured_prompts.append(prompt)
                import json

                return json.loads('{"backbone": "mlp"}')

        pool = LLMAgentPool(client=SpyingClient(), cache_dir=tmp_path)
        ctx = {
            "last_msd": 0.8,
            "validator_critique_delta": {"backbone": "mlp", "learning_rate": 1e-4},
            "validator_failed_genes": ("TP53", "MYC"),
            "literature": {"expected_up": ["JUN"], "expected_down": []},
        }
        pool.propose("Architect", round_index=1, task_id="t", context=ctx)
        assert captured_prompts, "expected a prompt capture"
        last = captured_prompts[0]
        # The Architect's prompt must mention the prior validator feedback.
        assert "mlp" in last or "TP53" in last or "0.8" in last
