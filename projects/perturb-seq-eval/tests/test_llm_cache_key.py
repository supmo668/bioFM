"""T4 / A2: the LLM cache key must include the lifecycle seed."""

from __future__ import annotations

import inspect

import pytest

from perturb_eval.llm.openrouter_client import OpenRouterClient, _cache_key

_BASE = dict(dataset="adamson_full", task_id="t1", round_index=0, role="Architect",
             prompt="p", model_id="m")


def test_different_seeds_give_different_keys() -> None:
    assert _cache_key(**_BASE, seed=1) != _cache_key(**_BASE, seed=2)


def test_same_seed_gives_same_key() -> None:
    assert _cache_key(**_BASE, seed=1) == _cache_key(**_BASE, seed=1)


def test_cache_key_seed_is_required() -> None:
    with pytest.raises(TypeError):
        _cache_key(**_BASE)  # type: ignore[call-arg]


def test_chat_json_seed_is_required_keyword() -> None:
    param = inspect.signature(OpenRouterClient.chat_json).parameters["seed"]
    assert param.kind is inspect.Parameter.KEYWORD_ONLY
    assert param.default is inspect.Parameter.empty
