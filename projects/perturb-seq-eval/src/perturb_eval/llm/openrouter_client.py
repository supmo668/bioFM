"""Free-tier OpenRouter chat client with weight-inclusive rotation.

Policy:
  * All models are free-tier (``*:free`` suffix). Highest-weight
    (Nemotron 253 B, DeepSeek V3 671 B MoE) are peers of fastest
    (Gemini Flash) — no strict priority outside role preference.
  * Per-model cooldown on 429 / 5xx / transient network error.
  * Per-day cap (``daily quota exceeded``) triggers a 6-hour cooldown.
  * sha256 disk cache keyed on (task, round, role, canonical prompt,
    model_id). Re-runs are cheap and resumable.
  * Parse failures get one retry with an explicit reformat prompt; then
    the caller must fall back to a rule-based default.

Env:
  * ``OPENROUTER_API_KEY`` — loaded from process env (use ``load_dotenv``
    at process start).
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import requests

logger = logging.getLogger(__name__)

_OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


@dataclass(frozen=True)
class ModelSpec:
    """One free-tier OpenRouter model endpoint."""

    model_id: str
    family: str  # "nemotron", "qwen", "llama", "deepseek", "gemini"
    param_count_b: float  # billions, for logging/telemetry
    strengths: tuple[str, ...]  # soft tags: "reasoning", "json", "fast"


@dataclass(frozen=True)
class LLMPool:
    """Weight-inclusive pool + role preference table."""

    models: tuple[ModelSpec, ...]
    role_preferences: dict[str, tuple[str, ...]]


DEFAULT_POOL = LLMPool(
    models=(
        ModelSpec(
            model_id="inclusionai/ling-2.6-1t:free",
            family="ling",
            param_count_b=1000,  # MoE, advertised 1T parameters
            strengths=("reasoning", "long-context"),
        ),
        ModelSpec(
            model_id="nousresearch/hermes-3-llama-3.1-405b:free",
            family="hermes",
            param_count_b=405,
            strengths=("reasoning", "json"),
        ),
        ModelSpec(
            model_id="nvidia/nemotron-3-super-120b-a12b:free",
            family="nemotron",
            param_count_b=120,
            strengths=("reasoning", "json"),
        ),
        ModelSpec(
            model_id="openai/gpt-oss-120b:free",
            family="oss",
            param_count_b=120,
            strengths=("instruct-following", "json"),
        ),
        ModelSpec(
            model_id="qwen/qwen3-next-80b-a3b-instruct:free",
            family="qwen",
            param_count_b=80,
            strengths=("broad-knowledge", "instruct"),
        ),
        ModelSpec(
            model_id="meta-llama/llama-3.3-70b-instruct:free",
            family="llama",
            param_count_b=70,
            strengths=("json", "instruct-following"),
        ),
        ModelSpec(
            model_id="google/gemma-4-31b-it:free",
            family="gemma",
            param_count_b=31,
            strengths=("fast", "instruct-following"),
        ),
        ModelSpec(
            model_id="google/gemma-3-27b-it:free",
            family="gemma",
            param_count_b=27,
            strengths=("fast", "high-quota"),
        ),
    ),
    role_preferences={
        "Architect": (
            "inclusionai/ling-2.6-1t:free",
            "nvidia/nemotron-3-super-120b-a12b:free",
            "nousresearch/hermes-3-llama-3.1-405b:free",
        ),
        "Literature": (
            "nvidia/nemotron-3-super-120b-a12b:free",
            "qwen/qwen3-next-80b-a3b-instruct:free",
            "nousresearch/hermes-3-llama-3.1-405b:free",
        ),
        "Validator": (
            "openai/gpt-oss-120b:free",
            "meta-llama/llama-3.3-70b-instruct:free",
            "qwen/qwen3-next-80b-a3b-instruct:free",
        ),
        "DataCurator": (
            "meta-llama/llama-3.3-70b-instruct:free",
            "google/gemma-4-31b-it:free",
            "qwen/qwen3-next-80b-a3b-instruct:free",
        ),
        "Trainer": (
            "google/gemma-3-27b-it:free",
            "google/gemma-4-31b-it:free",
            "meta-llama/llama-3.3-70b-instruct:free",
        ),
    },
)


class OpenRouterError(Exception):
    """All attempts across the rotation pool failed."""


class RateLimitedError(OpenRouterError):
    """Every candidate model is currently in cooldown."""


_WS = re.compile(r"\s+")


def _canonical_prompt(prompt: str) -> str:
    return _WS.sub(" ", prompt.strip())


def _cache_key(
    *, task_id: str, round_index: int, role: str, prompt: str, model_id: str
) -> str:
    payload = json.dumps(
        {
            "task_id": task_id,
            "round_index": int(round_index),
            "role": role,
            "prompt": _canonical_prompt(prompt),
            "model_id": model_id,
        },
        sort_keys=True,
    ).encode()
    return hashlib.sha256(payload).hexdigest()


def _extract_json(text: str) -> dict:
    """Best-effort JSON extract from a model response. Raises ValueError."""
    text = text.strip()
    # Fast path: direct JSON.
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Try to find a fenced code block.
    fence = re.search(r"```(?:json)?\s*(.+?)```", text, re.DOTALL)
    if fence:
        return json.loads(fence.group(1))
    # Try to find the outermost {...}.
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        return json.loads(text[start : end + 1])
    raise ValueError(f"no JSON object in response: {text[:200]!r}")


class OpenRouterClient:
    """Free-tier rotation chat client."""

    def __init__(
        self,
        *,
        api_key: str,
        cache_dir: Path,
        pool: LLMPool = DEFAULT_POOL,
        cooldown_sec: float = 60.0,
        timeout_sec: float = 60.0,
        session: Optional[requests.Session] = None,
    ) -> None:
        self._api_key = api_key
        self._cache_dir = Path(cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._pool = pool
        self._cooldown_sec = cooldown_sec
        self._timeout_sec = timeout_sec
        self._cooldowns: dict[str, float] = {}  # model_id -> unix timestamp until
        self._session = session if session is not None else requests.Session()

    def _candidate_models(self, role: str) -> list[ModelSpec]:
        preferred = self._pool.role_preferences.get(role, ())
        by_id = {m.model_id: m for m in self._pool.models}
        ordered: list[ModelSpec] = []
        seen: set[str] = set()
        for mid in preferred:
            if mid in by_id and mid not in seen:
                ordered.append(by_id[mid])
                seen.add(mid)
        for m in self._pool.models:
            if m.model_id not in seen:
                ordered.append(m)
                seen.add(m.model_id)
        now = time.time()
        return [m for m in ordered if self._cooldowns.get(m.model_id, 0) <= now]

    def _cache_path(self, key: str) -> Path:
        sub = self._cache_dir / key[:2]
        sub.mkdir(parents=True, exist_ok=True)
        return sub / f"{key}.json"

    def _cached(self, key: str) -> Optional[dict]:
        path = self._cache_path(key)
        if path.exists():
            try:
                return json.loads(path.read_text())
            except json.JSONDecodeError:
                return None
        return None

    def _save_cache(self, key: str, payload: dict) -> None:
        self._cache_path(key).write_text(json.dumps(payload))

    def _call(self, model_id: str, prompt: str) -> tuple[int, str]:
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": model_id,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
            "temperature": 0.3,
        }
        r = self._session.post(
            _OPENROUTER_URL, headers=headers, json=body, timeout=self._timeout_sec
        )
        if r.status_code != 200:
            return r.status_code, ""
        try:
            data = r.json()
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, ValueError):
            return r.status_code, ""
        return 200, content

    def chat_json(
        self,
        *,
        role: str,
        task_id: str,
        round_index: int,
        prompt: str,
    ) -> dict:
        """Return a parsed JSON object from the first responsive model.

        Raises :class:`OpenRouterError` if every candidate in the pool
        fails (network, 429, unparseable response).
        """
        candidates = self._candidate_models(role)
        if not candidates:
            raise RateLimitedError("no models available (all cooling)")

        last_err: Optional[str] = None
        for model in candidates:
            key = _cache_key(
                task_id=task_id,
                round_index=round_index,
                role=role,
                prompt=prompt,
                model_id=model.model_id,
            )
            cached = self._cached(key)
            if cached is not None:
                logger.debug("cache hit role=%s model=%s", role, model.model_id)
                return cached

            status, content = self._call(model.model_id, prompt)
            if status in (429, 502, 503, 504):
                self._cooldowns[model.model_id] = time.time() + self._cooldown_sec
                last_err = f"{model.model_id}: http {status}"
                continue
            if status != 200 or not content:
                last_err = f"{model.model_id}: http {status} / empty"
                continue

            try:
                parsed = _extract_json(content)
            except (ValueError, json.JSONDecodeError):
                # One reformat retry.
                reformat = (
                    "Your previous response was not valid JSON. Reply ONLY with "
                    "the JSON object, no markdown fencing, no commentary. "
                    f"Original task:\n{prompt}"
                )
                status2, content2 = self._call(model.model_id, reformat)
                if status2 == 200 and content2:
                    try:
                        parsed = _extract_json(content2)
                    except (ValueError, json.JSONDecodeError):
                        last_err = f"{model.model_id}: JSON parse failed after retry"
                        continue
                else:
                    last_err = f"{model.model_id}: retry http {status2}"
                    continue

            self._save_cache(key, parsed)
            return parsed

        raise OpenRouterError(
            f"all candidate models for role={role} failed; last_err={last_err}"
        )
