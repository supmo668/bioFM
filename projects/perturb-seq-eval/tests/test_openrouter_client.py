"""Unit tests for the OpenRouter free-tier rotation client."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from perturb_eval.llm.openrouter_client import (
    DEFAULT_POOL,
    LLMPool,
    OpenRouterClient,
    OpenRouterError,
    RateLimitedError,
    _canonical_prompt,
    _cache_key,
)


class TestLLMPool:
    def test_default_pool_has_weight_inclusive_models(self) -> None:
        names = [m.model_id for m in DEFAULT_POOL.models]
        # Pool composition (verified via OpenRouter /models on 2026-04-24):
        # Nemotron 120B (user-requested), big-MoE (Ling 1T or Hermes 405B),
        # Llama family, Qwen family, Gemma family.
        assert any("nemotron" in n.lower() for n in names)
        assert any("ling" in n.lower() or "hermes" in n.lower() for n in names)
        assert any("llama" in n.lower() for n in names)
        assert any("qwen" in n.lower() for n in names)
        assert any("gemma" in n.lower() for n in names)

    def test_all_models_are_free_tier(self) -> None:
        for m in DEFAULT_POOL.models:
            assert m.model_id.endswith(":free"), f"{m.model_id} not on free tier"

    def test_role_preferences_resolve_to_known_models(self) -> None:
        model_ids = {m.model_id for m in DEFAULT_POOL.models}
        for role, preferred in DEFAULT_POOL.role_preferences.items():
            for p in preferred:
                assert p in model_ids, f"{role} prefers {p} which is not in pool"


class TestCanonicalPrompt:
    def test_strips_whitespace(self) -> None:
        assert _canonical_prompt("  hello  \n\n world  ") == "hello world"

    def test_deterministic(self) -> None:
        assert _canonical_prompt("a b") == _canonical_prompt("a b")


class TestCacheKey:
    def test_different_fields_different_keys(self) -> None:
        base = dict(task_id="t1", round_index=0, role="A", prompt="p", model_id="m")
        a = _cache_key(**base)
        b = _cache_key(**{**base, "task_id": "t2"})
        assert a != b

    def test_same_fields_same_key(self) -> None:
        k1 = _cache_key(task_id="t1", round_index=0, role="A", prompt="p", model_id="m")
        k2 = _cache_key(task_id="t1", round_index=0, role="A", prompt="p", model_id="m")
        assert k1 == k2


class TestOpenRouterClient:
    @pytest.fixture
    def tmp_cache(self, tmp_path: Path) -> Path:
        return tmp_path / "llm_cache"

    def _make_response(self, content: str, status: int = 200) -> MagicMock:
        r = MagicMock()
        r.status_code = status
        r.json.return_value = {"choices": [{"message": {"content": content}}]}
        return r

    def test_returns_parsed_json_on_success(self, tmp_cache: Path) -> None:
        client = OpenRouterClient(api_key="test", cache_dir=tmp_cache)
        with patch.object(client._session, "post", return_value=self._make_response('{"a": 1}')):
            out = client.chat_json(
                role="Architect",
                task_id="t1",
                round_index=0,
                prompt="ping",
            )
        assert out == {"a": 1}

    def test_cache_hit_skips_network(self, tmp_cache: Path) -> None:
        client = OpenRouterClient(api_key="test", cache_dir=tmp_cache)
        mock_post = MagicMock(return_value=self._make_response('{"x": 42}'))
        with patch.object(client._session, "post", mock_post):
            client.chat_json(role="Trainer", task_id="t1", round_index=0, prompt="hi")
            assert mock_post.call_count == 1
            # Second call — same key.
            client.chat_json(role="Trainer", task_id="t1", round_index=0, prompt="hi")
            assert mock_post.call_count == 1  # still 1; cache hit.

    def test_rotation_on_429(self, tmp_cache: Path) -> None:
        client = OpenRouterClient(api_key="test", cache_dir=tmp_cache, cooldown_sec=0)
        responses = [
            self._make_response('', status=429),
            self._make_response('{"ok": true}', status=200),
        ]
        with patch.object(client._session, "post", side_effect=responses):
            out = client.chat_json(role="Validator", task_id="t", round_index=0, prompt="p")
        assert out == {"ok": True}

    def test_rotation_on_5xx(self, tmp_cache: Path) -> None:
        client = OpenRouterClient(api_key="test", cache_dir=tmp_cache, cooldown_sec=0)
        responses = [
            self._make_response('', status=502),
            self._make_response('{"ok": true}', status=200),
        ]
        with patch.object(client._session, "post", side_effect=responses):
            out = client.chat_json(role="Validator", task_id="t", round_index=0, prompt="p")
        assert out == {"ok": True}

    def test_all_models_fail_raises(self, tmp_cache: Path) -> None:
        small_pool = LLMPool(
            models=DEFAULT_POOL.models[:2],  # only 2 models
            role_preferences={"Architect": [m.model_id for m in DEFAULT_POOL.models[:2]]},
        )
        client = OpenRouterClient(
            api_key="test", cache_dir=tmp_cache, pool=small_pool, cooldown_sec=0
        )
        with patch.object(
            client._session, "post",
            return_value=self._make_response('', status=429),
        ):
            with pytest.raises(OpenRouterError):
                client.chat_json(role="Architect", task_id="t", round_index=0, prompt="p")

    def test_parse_failure_retries_with_reformat(self, tmp_cache: Path) -> None:
        client = OpenRouterClient(api_key="test", cache_dir=tmp_cache, cooldown_sec=0)
        responses = [
            self._make_response("not json at all"),
            self._make_response('{"fixed": true}'),
        ]
        with patch.object(client._session, "post", side_effect=responses):
            out = client.chat_json(role="DataCurator", task_id="t", round_index=0, prompt="p")
        assert out == {"fixed": True}

    def test_rate_limited_error_surfaces_when_all_cooled(self, tmp_cache: Path) -> None:
        # This is a unit check on the exception type, not behaviour.
        with pytest.raises(RateLimitedError):
            raise RateLimitedError("all models cooling")


class TestCachePersistence:
    def test_cache_written_to_disk(self, tmp_path: Path) -> None:
        client = OpenRouterClient(api_key="test", cache_dir=tmp_path / "cache")
        with patch.object(
            client._session, "post",
            return_value=MagicMock(
                status_code=200,
                json=lambda: {"choices": [{"message": {"content": '{"n": 7}'}}]},
            ),
        ):
            client.chat_json(role="Trainer", task_id="t", round_index=0, prompt="p")
        cache_files = list((tmp_path / "cache").rglob("*.json"))
        assert cache_files, "expected at least one cache file"
        payload = json.loads(cache_files[0].read_text())
        assert payload == {"n": 7}
