"""Free-tier OpenRouter chat client with weight-inclusive rotation.

Policy:
  * All models are free-tier (``*:free`` suffix). Highest-weight
    (Nemotron 253 B, DeepSeek V3 671 B MoE) are peers of fastest
    (Gemini Flash) — no strict priority outside role preference.
  * Per-model cooldown on 429 / 5xx / transient network error.
  * Per-day cap (``daily quota exceeded``) triggers a 6-hour cooldown.
  * sha256 disk cache keyed on (dataset, task, round, role, canonical
    prompt, model_id, seed). Re-runs are cheap and resumable; every
    :class:`ChatResult` says whether it was a cache hit.
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
from typing import Callable, Optional

import requests

logger = logging.getLogger(__name__)

_OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Amendment 2 (A2-8): the pre-registered version, pinned at the lock. Each
# pre-registered version starts with an EMPTY LLM cache namespace
# ``<cache_dir>/<prereg_version>/``; a non-empty start or any cache hit makes
# the run a replay.
PREREG_VERSION = "v0.6.0-a3"  # amendment 3 (2026-09-28)


def versioned_cache_dir(cache_dir: str | Path, prereg_version: str = PREREG_VERSION) -> Path:
    """``<cache_dir>/<prereg_version>`` — the LLM cache namespace a run reads and writes."""
    if not prereg_version or "/" in prereg_version or prereg_version in (".", ".."):
        raise ValueError(f"invalid prereg_version {prereg_version!r}")
    return Path(cache_dir) / prereg_version


def count_cache_entries(namespace: str | Path) -> int:
    """Number of cached replies (``*.json`` files) under ``namespace``; 0 if absent."""
    root = Path(namespace)
    if not root.is_dir():
        return 0
    return sum(1 for p in root.rglob("*.json") if p.is_file())


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
    # Relaunch roster (principal ruling 2026-09-28; CTO #467): PAID, cheapest
    # JSON-capable tier, one model per family. The earlier ":free" roster died on
    # OpenRouter (6/8 ids gone; the rest rate-limited into fallbacks, which A2-1
    # makes fatal). Every id is probed at preflight and its liveness recorded in
    # provenance. The pre-registration pins "a rotating pool ... recorded in
    # provenance", not the ids.
    models=(
        ModelSpec(
            model_id="deepseek/deepseek-v4-flash",
            family="deepseek",
            param_count_b=0,
            strengths=("reasoning", "json", "long-context"),
        ),
        ModelSpec(
            model_id="openai/gpt-oss-20b",
            family="oss",
            param_count_b=20,
            strengths=("instruct-following", "json"),
        ),
        ModelSpec(
            model_id="qwen/qwen3.7-flash",
            family="qwen",
            param_count_b=0,
            strengths=("broad-knowledge", "instruct", "json"),
        ),
        ModelSpec(
            model_id="google/gemma-3-12b-it",
            family="gemma",
            param_count_b=12,
            strengths=("fast", "instruct-following"),
        ),
        ModelSpec(
            model_id="mistralai/mistral-nemo",
            family="mistral",
            param_count_b=12,
            strengths=("fast", "json"),
        ),
        ModelSpec(
            model_id="meta-llama/llama-3.1-8b-instruct",
            family="llama",
            param_count_b=8,
            strengths=("json", "instruct-following"),
        ),
        ModelSpec(
            model_id="nvidia/nemotron-3-nano-30b-a3b",
            family="nemotron",
            param_count_b=30,
            strengths=("reasoning", "json"),
        ),
        ModelSpec(
            model_id="z-ai/glm-4.7-flash", family="glm", param_count_b=0, strengths=("fast", "json")
        ),
    ),
    role_preferences={
        "Architect": ("deepseek/deepseek-v4-flash", "openai/gpt-oss-20b", "qwen/qwen3.7-flash"),
        "Literature": ("qwen/qwen3.7-flash", "google/gemma-3-12b-it", "deepseek/deepseek-v4-flash"),
        "Validator": ("openai/gpt-oss-20b", "z-ai/glm-4.7-flash", "mistralai/mistral-nemo"),
        "DataCurator": (
            "mistralai/mistral-nemo",
            "meta-llama/llama-3.1-8b-instruct",
            "google/gemma-3-12b-it",
        ),
        "Trainer": (
            "nvidia/nemotron-3-nano-30b-a3b",
            "meta-llama/llama-3.1-8b-instruct",
            "z-ai/glm-4.7-flash",
        ),
    },
)


@dataclass(frozen=True)
class ChatResult:
    """One successful :meth:`OpenRouterClient.chat_json` response.

    ``model_id`` is the pool model that actually served ``content`` — after
    rotation past cooled / failing candidates, and on a disk-cache hit the
    model whose cache entry was hit (the cache key includes ``model_id``).
    ``cache_hit`` is True when ``content`` was replayed from the disk cache
    rather than served by a fresh call (QG C6).
    """

    content: dict
    model_id: str
    cache_hit: bool = False


class OpenRouterError(Exception):
    """All attempts across the rotation pool failed."""


class RateLimitedError(OpenRouterError):
    """Every candidate model is currently in cooldown."""


_WS = re.compile(r"\s+")


def _canonical_prompt(prompt: str) -> str:
    return _WS.sub(" ", prompt.strip())


def _cache_key(
    *,
    dataset: str,
    task_id: str,
    round_index: int,
    role: str,
    prompt: str,
    model_id: str,
    seed: int,
) -> str:
    payload = json.dumps(
        {
            # QG C6: a gene symbol can be a task in two datasets (SNAI1, SPI1).
            "dataset": dataset,
            "task_id": task_id,
            "round_index": int(round_index),
            "role": role,
            "prompt": _canonical_prompt(prompt),
            "model_id": model_id,
            "seed": int(seed),
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
        max_wait_sec: float = 300.0,
        sleep: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.time,
    ) -> None:
        self._api_key = api_key
        self._cache_dir = Path(cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._pool = pool
        self._cooldown_sec = cooldown_sec
        self._timeout_sec = timeout_sec
        self._cooldowns: dict[str, float] = {}  # model_id -> unix timestamp until
        self._session = session if session is not None else requests.Session()
        # CTO #467 relaunch: a 429/5xx marks a model cooling; while ANY model is
        # cooling, chat_json waits (bounded by max_wait_sec per call) instead of
        # falling back -- a fallback step invalidates the run (A2-1).
        self._max_wait_sec = max_wait_sec
        self._sleep = sleep
        self._clock = clock

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
        now = self._clock()
        return [m for m in ordered if self._cooldowns.get(m.model_id, 0) <= now]

    def _earliest_cooldown_end(self) -> Optional[float]:
        now = self._clock()
        pending = [t for t in self._cooldowns.values() if t > now]
        return min(pending) if pending else None

    def probe_model(self, model_id: str, prompt: str) -> tuple[bool, str, Optional[dict]]:
        """One direct call to ONE model, no failover, no cache (preflight, CTO #467).

        Returns ``(live, verdict, parsed)``: ``live`` is True only when the model
        answered 200 with a JSON object; ``verdict`` is a short reason otherwise.
        """
        status, content = self._call(model_id, prompt)
        if status != 200:
            return False, f"http {status}", None
        if not content:
            return False, "http 200 / empty", None
        try:
            parsed = _extract_json(content)
        except (ValueError, json.JSONDecodeError):
            return False, "not a JSON object", None
        return True, "ok", parsed

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
        seed: int,
        dataset: str,
    ) -> ChatResult:
        """Return the parsed JSON object from the first responsive model,
        together with that model's id (:class:`ChatResult`).

        ``seed`` and ``dataset`` are part of the cache key only (A2, QG C6);
        they are not sent to the provider.

        Raises :class:`OpenRouterError` if every candidate in the pool
        fails (network, 429, unparseable response).
        """
        waited = 0.0
        last_err: Optional[str] = None
        while True:
            candidates = self._candidate_models(role)
            if candidates:
                res = self._try_candidates(
                    candidates,
                    role=role,
                    task_id=task_id,
                    round_index=round_index,
                    prompt=prompt,
                    seed=seed,
                    dataset=dataset,
                )
                if isinstance(res, ChatResult):
                    return res
                last_err = res
            # Nothing answered. Wait for the earliest cooldown (bounded) if any
            # model is merely cooling; raise only when nothing is cooling or the
            # wait budget is spent.
            end = self._earliest_cooldown_end()
            if end is None:
                if not candidates:
                    raise RateLimitedError("no models available (all cooling)")
                raise OpenRouterError(
                    f"all candidate models for role={role} failed; last_err={last_err}"
                )
            remaining = self._max_wait_sec - waited
            if remaining <= 0:
                raise RateLimitedError(
                    f"role={role}: every model cooling and the {self._max_wait_sec:.0f}s "
                    f"wait budget is spent; last_err={last_err}"
                )
            pause = max(0.0, min(end - self._clock(), remaining)) + 0.01
            self._sleep(pause)
            waited += pause

    def _try_candidates(
        self,
        candidates: list[ModelSpec],
        *,
        role: str,
        task_id: str,
        round_index: int,
        prompt: str,
        seed: int,
        dataset: str,
    ) -> "ChatResult | str | None":
        """One pass over ``candidates``; a ChatResult, else the last error text."""
        last_err: Optional[str] = None
        for model in candidates:
            key = _cache_key(
                dataset=dataset,
                task_id=task_id,
                round_index=round_index,
                role=role,
                prompt=prompt,
                model_id=model.model_id,
                seed=seed,
            )
            cached = self._cached(key)
            if cached is not None:
                logger.debug("cache hit role=%s model=%s", role, model.model_id)
                return ChatResult(content=cached, model_id=model.model_id, cache_hit=True)

            status, content = self._call(model.model_id, prompt)
            if status in (429, 502, 503, 504):
                self._cooldowns[model.model_id] = self._clock() + self._cooldown_sec
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
            return ChatResult(content=parsed, model_id=model.model_id, cache_hit=False)
        return last_err
