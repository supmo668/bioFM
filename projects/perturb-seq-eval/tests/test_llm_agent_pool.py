"""Integration of the OpenRouter client + Pydantic schemas into an AgentPool."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import requests

from perturb_eval.agentic_lifecycle.llm_agent_pool import LLMAgentPool
from perturb_eval.agentic_lifecycle.proposal_schema import schema_defaults
from perturb_eval.llm.openrouter_client import ChatResult, OpenRouterError, RateLimitedError


class FakeClient:
    """Replaces OpenRouterClient for offline tests.

    ``responses_by_role`` maps role name → list of JSON-string responses
    consumed in order (one per call). If the role list is exhausted, the
    last item is repeated — this lets us stub "model always returns X".
    """

    def __init__(self, responses_by_role: dict[str, list[str]]) -> None:
        self._responses = {k: list(v) for k, v in responses_by_role.items()}
        self.calls: list[tuple[str, str, int]] = []

    def chat_json(
        self, *, role: str, task_id: str, round_index: int, prompt: str, seed: int, dataset: str
    ) -> ChatResult:  # noqa: ARG002
        self.calls.append((role, task_id, round_index))
        import json

        queue = self._responses.get(role, [])
        if not queue:
            return ChatResult(content={}, model_id="fake/model")
        content = queue[0] if len(queue) == 1 else queue.pop(0)
        return ChatResult(content=json.loads(content), model_id="fake/model")


class TestLLMAgentPoolBasics:
    def test_each_role_returns_content_rationale_confidence(self, tmp_path: Path) -> None:
        fake = FakeClient(
            responses_by_role={
                # A2-1: every role states its confidence.
                "DataCurator": ['{"hvg_method": "seurat", "hvg_count": 1000, "confidence": 0.6}'],
                "Literature": [
                    '{"pathway_prior": {"TP53": 0.7}, "ppi_neighbors": ["JUN"], "confidence": 0.5}'
                ],
                "Architect": [
                    '{"backbone": "mlp", "learning_rate": 5e-3, "hvg_count": 1000, "confidence": 0.7}'
                ],
                "Trainer": ['{"lr": 5e-3, "epochs": 40, "ridge_lambda": 1.0, "confidence": 0.4}'],
                "Validator": ['{"dynamic_threshold_msd": 0.1, "confidence": 0.8}'],
            }
        )
        pool = LLMAgentPool(client=fake, cache_dir=tmp_path)
        for role in ("DataCurator", "Literature", "Architect", "Trainer", "Validator"):
            out = pool.propose(
                role, round_index=0, task_id="t1", context={}, seed=0, dataset="adamson_full"
            )
            assert "content" in out
            assert "rationale" in out
            assert "confidence" in out
            assert isinstance(out["content"], dict)
            assert out["source"] == "llm"  # A2-1: a stated confidence, not a fallback

    def test_architect_produces_valid_config(self, tmp_path: Path) -> None:
        fake = FakeClient(
            responses_by_role={
                "Architect": [
                    '{"backbone": "scgpt_small", "learning_rate": 1e-3, "hvg_count": 2000, "confidence": 0.5}'
                ],
            }
        )
        pool = LLMAgentPool(client=fake, cache_dir=tmp_path)
        out = pool.propose(
            "Architect", round_index=0, task_id="t1", context={}, seed=0, dataset="adamson_full"
        )
        assert out["content"]["backbone"] == "scgpt_small"
        assert out["content"]["learning_rate"] == 1e-3

    def test_falls_back_to_rule_based_on_llm_failure(self, tmp_path: Path) -> None:
        from perturb_eval.llm.openrouter_client import OpenRouterError

        failing = MagicMock()
        failing.chat_json = MagicMock(side_effect=OpenRouterError("all cooled"))
        pool = LLMAgentPool(client=failing, cache_dir=tmp_path)
        out = pool.propose(
            "Architect", round_index=0, task_id="t1", context={}, seed=0, dataset="adamson_full"
        )
        # Fallback still yields the schema's optional defaults, but A2-6/A2-1:
        # never a stated backbone and never an imputed confidence.
        assert out["source"] == "fallback"
        assert "backbone" not in out["content"]
        assert out["confidence"] is None

    def test_different_tasks_get_different_prompts(self, tmp_path: Path) -> None:
        fake = FakeClient(
            responses_by_role={
                "Architect": ['{"backbone": "linear"}', '{"backbone": "mlp"}'],
            }
        )
        pool = LLMAgentPool(client=fake, cache_dir=tmp_path)
        pool.propose(
            "Architect", round_index=0, task_id="task_a", context={}, seed=0, dataset="adamson_full"
        )
        pool.propose(
            "Architect", round_index=0, task_id="task_b", context={}, seed=0, dataset="adamson_full"
        )
        assert len({c[1] for c in fake.calls}) == 2


class TestContextThreading:
    def test_validator_critique_reaches_architect_prompt(self, tmp_path: Path) -> None:
        captured_prompts: list[str] = []

        class SpyingClient:
            def chat_json(self, *, role, task_id, round_index, prompt, seed, dataset):  # noqa: ARG002
                if role == "Architect":
                    captured_prompts.append(prompt)
                import json

                return ChatResult(content=json.loads('{"backbone": "mlp"}'), model_id="spy/model")

        pool = LLMAgentPool(client=SpyingClient(), cache_dir=tmp_path)
        ctx = {
            "last_msd": 0.8,
            "validator_critique_delta": {"backbone": "mlp", "learning_rate": 1e-4},
            "validator_failed_genes": ("TP53", "MYC"),
            "literature": {"expected_up": ["JUN"], "expected_down": []},
        }
        pool.propose(
            "Architect", round_index=1, task_id="t", context=ctx, seed=0, dataset="adamson_full"
        )
        assert captured_prompts, "expected a prompt capture"
        last = captured_prompts[0]
        # The Architect's prompt must mention the prior validator feedback.
        assert "mlp" in last or "TP53" in last or "0.8" in last


class TestSeedThreading:
    """T4 / A2: the lifecycle seed must reach the LLM client."""

    class _RecordingClient:
        def __init__(self) -> None:
            self.kwargs: list[dict] = []

        def chat_json(self, **kwargs) -> ChatResult:
            self.kwargs.append(kwargs)
            return ChatResult(content={"backbone": "mlp"}, model_id="rec/model")

    def test_propose_forwards_seed_to_chat_json(self, tmp_path: Path) -> None:
        client = self._RecordingClient()
        pool = LLMAgentPool(client=client, cache_dir=tmp_path)
        pool.propose(
            "Architect", round_index=0, task_id="t", context={}, seed=7, dataset="adamson_full"
        )
        assert client.kwargs and client.kwargs[0]["seed"] == 7

    def test_propose_without_seed_raises(self, tmp_path: Path) -> None:
        pool = LLMAgentPool(client=self._RecordingClient(), cache_dir=tmp_path)
        with pytest.raises(TypeError):
            pool.propose("Architect", round_index=0, task_id="t", context={})  # type: ignore[call-arg]

    def test_fallback_path_accepts_seed(self, tmp_path: Path) -> None:
        from perturb_eval.llm.openrouter_client import OpenRouterError

        failing = MagicMock()
        failing.chat_json = MagicMock(side_effect=OpenRouterError("down"))
        pool = LLMAgentPool(client=failing, cache_dir=tmp_path)
        out = pool.propose(
            "Architect", round_index=0, task_id="t", context={}, seed=3, dataset="adamson_full"
        )
        assert out["source"] == "fallback"
        assert "backbone" not in out["content"]  # A2-6: never defaulted


# --- T12 / D4 / C-KEY-2: model_id + source on every proposal ----------------

_ROLES = ("DataCurator", "Literature", "Architect", "Trainer", "Validator")
# A2-1/A2-6: the fallback content is the schema's OPTIONAL defaults only (no
# confidence, no Architect backbone).
_DEFAULTS = {role: (lambda role=role: schema_defaults(role)) for role in _ROLES}


class _StubTransport:
    """Client stub: always serves ``content`` from pool model ``model_id``."""

    def __init__(self, model_id: str = "x/y", content: dict | None = None) -> None:
        self._model_id = model_id
        # A2-1/A2-6: a minimal schema-valid reply for every role.
        self._content = (
            content if content is not None else {"confidence": 0.5, "backbone": "linear"}
        )

    def chat_json(self, *, role, task_id, round_index, prompt, seed, dataset) -> ChatResult:  # noqa: ARG002
        return ChatResult(content=dict(self._content), model_id=self._model_id)


class _RaisingClient:
    def __init__(self, exc: BaseException) -> None:
        self._exc = exc

    def chat_json(self, *, role, task_id, round_index, prompt, seed, dataset):  # noqa: ARG002
        raise self._exc


class TestModelIdAndSource:
    @pytest.mark.parametrize("role", _ROLES)
    def test_llm_success_reports_serving_model_and_source_llm(
        self, tmp_path: Path, role: str
    ) -> None:
        pool = LLMAgentPool(client=_StubTransport("x/y"), cache_dir=tmp_path)
        out = pool.propose(
            role, round_index=0, task_id="t", context={}, seed=0, dataset="adamson_full"
        )
        assert out["model_id"] == "x/y"
        assert out["source"] == "llm"

    @pytest.mark.parametrize(
        "exc",
        [
            RateLimitedError("pool exhausted"),
            OpenRouterError("all candidates failed"),
            requests.ConnectionError("network down"),
            requests.HTTPError("503"),
            requests.Timeout("slow"),
            json.JSONDecodeError("bad", "doc", 0),
        ],
        ids=lambda e: type(e).__name__,
    )
    @pytest.mark.parametrize("role", _ROLES)
    def test_runtime_failure_falls_back_with_schema_default(
        self, tmp_path: Path, role: str, exc: BaseException
    ) -> None:
        pool = LLMAgentPool(client=_RaisingClient(exc), cache_dir=tmp_path)
        out = pool.propose(
            role, round_index=0, task_id="t", context={}, seed=0, dataset="adamson_full"
        )
        assert out["source"] == "fallback"
        assert out["model_id"] is None
        assert out["content"] == _DEFAULTS[role]()
        assert out["confidence"] is None  # A2-1: never imputed

    def test_schema_validation_failure_falls_back(self, tmp_path: Path) -> None:
        # backbone outside the Literal set → pydantic ValidationError.
        pool = LLMAgentPool(
            client=_StubTransport("x/y", {"backbone": "transformer-xl"}), cache_dir=tmp_path
        )
        out = pool.propose(
            "Architect", round_index=0, task_id="t", context={}, seed=0, dataset="adamson_full"
        )
        assert out["source"] == "fallback"
        assert out["model_id"] is None
        assert out["content"] == schema_defaults("Architect")

    def test_non_object_json_falls_back(self, tmp_path: Path) -> None:
        class _ListClient:
            def chat_json(self, **_kw) -> ChatResult:
                return ChatResult(content=[1, 2], model_id="x/y")  # type: ignore[arg-type]

        pool = LLMAgentPool(client=_ListClient(), cache_dir=tmp_path)
        out = pool.propose(
            "Trainer", round_index=0, task_id="t", context={}, seed=0, dataset="adamson_full"
        )
        assert out["source"] == "fallback"
        assert out["content"] == schema_defaults("Trainer")

    @pytest.mark.parametrize(
        "exc",
        [
            TypeError("chat_json() got an unexpected keyword argument"),
            AttributeError("x"),
            NameError("y"),
            KeyError("z"),
        ],
        ids=lambda e: type(e).__name__,
    )
    def test_programming_errors_propagate_no_fallback(
        self, tmp_path: Path, exc: BaseException
    ) -> None:
        pool = LLMAgentPool(client=_RaisingClient(exc), cache_dir=tmp_path)
        with pytest.raises(type(exc)):
            pool.propose(
                "Architect", round_index=0, task_id="t", context={}, seed=0, dataset="adamson_full"
            )

    def test_signature_mismatch_typeerror_propagates(self, tmp_path: Path) -> None:
        class _OldSignatureClient:  # pre-A2 client: no ``seed`` kwarg
            def chat_json(self, *, role, task_id, round_index, prompt):  # noqa: ARG002
                return ChatResult(content={}, model_id="x/y")

        pool = LLMAgentPool(client=_OldSignatureClient(), cache_dir=tmp_path)
        with pytest.raises(TypeError):
            pool.propose(
                "Architect", round_index=0, task_id="t", context={}, seed=0, dataset="adamson_full"
            )

    def test_client_returning_bare_dict_is_a_programming_error(self, tmp_path: Path) -> None:
        class _LegacyDictClient:
            def chat_json(self, **_kw) -> dict:
                return {"backbone": "mlp"}

        pool = LLMAgentPool(client=_LegacyDictClient(), cache_dir=tmp_path)
        with pytest.raises(AttributeError):
            pool.propose(
                "Architect", round_index=0, task_id="t", context={}, seed=0, dataset="adamson_full"
            )
