"""Unit tests for the OpenRouter free-tier rotation client."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from perturb_eval.llm.openrouter_client import (
    DEFAULT_POOL,
    ChatResult,
    LLMPool,
    OpenRouterClient,
    OpenRouterError,
    RateLimitedError,
    _canonical_prompt,
    _cache_key,
)


class TestLLMPool:
    def test_default_pool_spans_the_families_and_has_no_free_endpoints(self) -> None:
        names = [m.model_id for m in DEFAULT_POOL.models]
        # Relaunch roster (principal 2026-09-28, CTO #467): PAID cheapest
        # JSON-capable tier, one model per family. The ":free" endpoints died
        # (6/8 ids gone from OpenRouter) or rate-limited into fallbacks, which
        # A2-1 makes fatal; liveness of every id is probed at preflight.
        for fam in ("nemotron", "llama", "qwen", "gemma", "deepseek", "mistral"):
            assert any(fam in n.lower() for n in names), fam
        assert len({m.family for m in DEFAULT_POOL.models}) == len(DEFAULT_POOL.models)

    def test_no_model_is_a_free_endpoint(self) -> None:
        for m in DEFAULT_POOL.models:
            assert not m.model_id.endswith(":free"), f"{m.model_id} is a :free endpoint"

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
        base = dict(
            dataset="d", task_id="t1", round_index=0, role="A", prompt="p", model_id="m", seed=0
        )
        a = _cache_key(**base)
        b = _cache_key(**{**base, "task_id": "t2"})
        assert a != b

    def test_same_fields_same_key(self) -> None:
        k1 = _cache_key(
            dataset="d", task_id="t1", round_index=0, role="A", prompt="p", model_id="m", seed=0
        )
        k2 = _cache_key(
            dataset="d", task_id="t1", round_index=0, role="A", prompt="p", model_id="m", seed=0
        )
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
                seed=0,
                dataset="adamson_full",
            )
        assert out.content == {"a": 1}

    def test_cache_hit_skips_network(self, tmp_cache: Path) -> None:
        client = OpenRouterClient(api_key="test", cache_dir=tmp_cache)
        mock_post = MagicMock(return_value=self._make_response('{"x": 42}'))
        with patch.object(client._session, "post", mock_post):
            client.chat_json(
                role="Trainer",
                task_id="t1",
                round_index=0,
                prompt="hi",
                seed=0,
                dataset="adamson_full",
            )
            assert mock_post.call_count == 1
            # Second call — same key.
            client.chat_json(
                role="Trainer",
                task_id="t1",
                round_index=0,
                prompt="hi",
                seed=0,
                dataset="adamson_full",
            )
            assert mock_post.call_count == 1  # still 1; cache hit.

    def test_rotation_on_429(self, tmp_cache: Path) -> None:
        client = OpenRouterClient(api_key="test", cache_dir=tmp_cache, cooldown_sec=0)
        responses = [
            self._make_response("", status=429),
            self._make_response('{"ok": true}', status=200),
        ]
        with patch.object(client._session, "post", side_effect=responses):
            out = client.chat_json(
                role="Validator",
                task_id="t",
                round_index=0,
                prompt="p",
                seed=0,
                dataset="adamson_full",
            )
        assert out.content == {"ok": True}

    def test_rotation_on_5xx(self, tmp_cache: Path) -> None:
        client = OpenRouterClient(api_key="test", cache_dir=tmp_cache, cooldown_sec=0)
        responses = [
            self._make_response("", status=502),
            self._make_response('{"ok": true}', status=200),
        ]
        with patch.object(client._session, "post", side_effect=responses):
            out = client.chat_json(
                role="Validator",
                task_id="t",
                round_index=0,
                prompt="p",
                seed=0,
                dataset="adamson_full",
            )
        assert out.content == {"ok": True}

    def test_all_models_fail_raises(self, tmp_cache: Path) -> None:
        small_pool = LLMPool(
            models=DEFAULT_POOL.models[:2],  # only 2 models
            role_preferences={"Architect": [m.model_id for m in DEFAULT_POOL.models[:2]]},
        )
        client = OpenRouterClient(
            api_key="test", cache_dir=tmp_cache, pool=small_pool, cooldown_sec=0
        )
        with patch.object(
            client._session,
            "post",
            return_value=self._make_response("", status=429),
        ):
            with pytest.raises(OpenRouterError):
                client.chat_json(
                    role="Architect",
                    task_id="t",
                    round_index=0,
                    prompt="p",
                    seed=0,
                    dataset="adamson_full",
                )

    def test_parse_failure_retries_with_reformat(self, tmp_cache: Path) -> None:
        client = OpenRouterClient(api_key="test", cache_dir=tmp_cache, cooldown_sec=0)
        responses = [
            self._make_response("not json at all"),
            self._make_response('{"fixed": true}'),
        ]
        with patch.object(client._session, "post", side_effect=responses):
            out = client.chat_json(
                role="DataCurator",
                task_id="t",
                round_index=0,
                prompt="p",
                seed=0,
                dataset="adamson_full",
            )
        assert out.content == {"fixed": True}

    # --- T12: chat_json reports the pool model that actually served -------

    def test_returns_chat_result_with_serving_model_id(self, tmp_cache: Path) -> None:
        client = OpenRouterClient(api_key="test", cache_dir=tmp_cache)
        with patch.object(client._session, "post", return_value=self._make_response('{"a": 1}')):
            out = client.chat_json(
                role="Architect",
                task_id="t1",
                round_index=0,
                prompt="p",
                seed=0,
                dataset="adamson_full",
            )
        assert isinstance(out, ChatResult)
        assert out.model_id == DEFAULT_POOL.role_preferences["Architect"][0]

    def test_model_id_is_the_rotated_model_not_the_first_candidate(self, tmp_cache: Path) -> None:
        client = OpenRouterClient(api_key="test", cache_dir=tmp_cache, cooldown_sec=0)
        responses = [
            self._make_response("", status=429),
            self._make_response('{"ok": true}', status=200),
        ]
        with patch.object(client._session, "post", side_effect=responses) as post:
            out = client.chat_json(
                role="Validator",
                task_id="t",
                round_index=0,
                prompt="p",
                seed=0,
                dataset="adamson_full",
            )
        served = post.call_args_list[1].kwargs["json"]["model"]
        first = post.call_args_list[0].kwargs["json"]["model"]
        assert out.model_id == served
        assert out.model_id != first

    def test_cache_hit_returns_the_cached_model_id(self, tmp_cache: Path) -> None:
        client = OpenRouterClient(api_key="test", cache_dir=tmp_cache, cooldown_sec=0)
        responses = [
            self._make_response("", status=429),
            self._make_response('{"ok": true}', status=200),
        ]
        with patch.object(client._session, "post", side_effect=responses):
            first = client.chat_json(
                role="Validator",
                task_id="t",
                round_index=0,
                prompt="p",
                seed=0,
                dataset="adamson_full",
            )
        # Fresh client (no cooldowns): the first candidate has no cache entry
        # and now fails on the network; the second hits cache.
        client2 = OpenRouterClient(api_key="test", cache_dir=tmp_cache, cooldown_sec=0)
        with patch.object(
            client2._session, "post", return_value=self._make_response("", status=429)
        ) as post2:
            again = client2.chat_json(
                role="Validator",
                task_id="t",
                round_index=0,
                prompt="p",
                seed=0,
                dataset="adamson_full",
            )
        assert post2.call_count == 1  # first candidate only; second served from cache
        assert again.content == first.content
        assert again.model_id == first.model_id
        assert first.cache_hit is False and again.cache_hit is True  # QG C6

    def test_chat_result_is_frozen(self) -> None:
        r = ChatResult(content={"a": 1}, model_id="x/y")
        with pytest.raises(Exception):
            r.model_id = "z"  # type: ignore[misc]

    def test_rate_limited_error_when_every_model_cools_past_the_wait_budget(self, tmp_path) -> None:
        """QG-12: behavioural replacement for a test that raised and caught its own exception."""
        from perturb_eval.llm.openrouter_client import (
            LLMPool,
            ModelSpec,
            OpenRouterClient,
            RateLimitedError,
        )

        class _S:
            def post(self, url, headers=None, json=None, timeout=None):  # noqa: ANN001
                from types import SimpleNamespace

                return SimpleNamespace(status_code=429, json=lambda: {})

        clock = [0.0]
        pool = LLMPool(
            models=(ModelSpec("m/a", "a", 1, ()),), role_preferences={"Validator": ("m/a",)}
        )
        c = OpenRouterClient(
            api_key="k",
            cache_dir=tmp_path,
            pool=pool,
            cooldown_sec=5.0,
            session=_S(),
            sleep=lambda s: clock.__setitem__(0, clock[0] + s),
            clock=lambda: clock[0],
            max_wait_sec=12.0,
        )
        with pytest.raises(RateLimitedError, match="wait budget"):
            c.chat_json(
                role="Validator", task_id="t", round_index=0, prompt="p", seed=0, dataset="d"
            )
        assert 12.0 <= clock[0] <= 12.0 + 5.1

    def test_cache_written_to_disk(self, tmp_path: Path) -> None:
        client = OpenRouterClient(api_key="test", cache_dir=tmp_path / "cache")
        with patch.object(
            client._session,
            "post",
            return_value=MagicMock(
                status_code=200,
                json=lambda: {"choices": [{"message": {"content": '{"n": 7}'}}]},
            ),
        ):
            client.chat_json(
                role="Trainer",
                task_id="t",
                round_index=0,
                prompt="p",
                seed=0,
                dataset="adamson_full",
            )
        cache_files = list((tmp_path / "cache").rglob("*.json"))
        assert cache_files, "expected at least one cache file"
        payload = json.loads(cache_files[0].read_text())
        assert payload == {"n": 7}
