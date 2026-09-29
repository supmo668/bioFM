"""Anthropic Messages API client for the v0.6.0 lifecycle (pre-registration amendment 4, A4-1).

Same ``chat_json`` contract as :class:`perturb_eval.llm.openrouter_client.OpenRouterClient`
(the agent pool is provider-agnostic), with the A4-1 rules built in:

* roster pinned by model id (:data:`ANTHROPIC_POOL`); failover between the two models;
* every reply constrained to the role's JSON schema by structured outputs
  (``output_config.format``); the wire schema omits numeric ranges and expresses the two
  free-form maps as key/value pair arrays, converted back before the pydantic role schema
  enforces ranges (out of range -> schema failure -> fallback, never a clamp);
* ``stop_reason`` checked on EVERY call and recorded: ``refusal`` -> :class:`ProviderFatalError`
  (never a fallback, never a silent retry elsewhere); ``max_tokens`` -> one retry at 2x the
  ceiling (both billed), a second -> :class:`AnthropicError` (fallback-class);
* the served model (``response.model``) is recorded next to the requested id and asserted
  equal — a mismatch is a fallback-class event (silent substitution is this project's recurring
  defect); the request NEVER carries a ``fallbacks`` parameter;
* 401/402/403 -> :class:`ProviderFatalError`; 408/409/429/5xx/529 and transport errors cool the
  model and the client waits (wall-clock deadline) instead of falling back;
* spend = API-reported ``usage`` x :data:`PRICE_TABLE` (input, output, cache read/write),
  accumulated per call in :attr:`AnthropicClient.call_log` / :attr:`AnthropicClient.spend_usd`;
* sampling: Haiku 4.5 at ``temperature`` 0.3 (raw body; identical to the OpenRouter runs, so H3's
  Architect condition is unchanged); Sonnet 5.5 at API defaults with thinking off
  (``between_tools`` + effort low).
The API key is read from the environment by the caller and never logged.
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any, Callable, Mapping, Optional

from perturb_eval.llm.openrouter_client import (
    ChatResult,
    LLMPool,
    ModelSpec,
    ProviderError,
    ProviderFatalError,
    RateLimitedError,
    _cache_key,
    _extract_json,
)

logger = logging.getLogger(__name__)

HAIKU = "claude-haiku-4-5-20251001"
SONNET = "claude-sonnet-5-5"

ANTHROPIC_POOL = LLMPool(
    models=(
        ModelSpec(
            model_id=HAIKU, family="claude-haiku", param_count_b=0, strengths=("json", "fast")
        ),
        ModelSpec(
            model_id=SONNET,
            family="claude-sonnet",
            param_count_b=0,
            strengths=("json", "reasoning"),
        ),
    ),
    role_preferences={
        "DataCurator": (HAIKU, SONNET),
        "Literature": (HAIKU, SONNET),
        "Architect": (HAIKU, SONNET),
        "Trainer": (HAIKU, SONNET),
        # A4-3: the judge sits on a different tier from the roles it judges.
        "Validator": (SONNET, HAIKU),
    },
)

# $ per million tokens; Anthropic first-party list prices (claude-api skill table cached
# 2026-09-25, re-checked 2026-09-29). Recorded in provenance with every run.
PRICE_TABLE: dict[str, dict[str, float]] = {
    HAIKU: {"input": 1.0, "output": 5.0, "cache_read": 0.10, "cache_write": 1.25},
    SONNET: {"input": 2.0, "output": 10.0, "cache_read": 0.20, "cache_write": 2.50},
}
PRICE_TABLE_SOURCE = "Anthropic first-party list prices; claude-api skill model table cached 2026-09-25; re-cited 2026-09-29"

# A4-1: 4x the dry run's observed maximum output, minimum 256 (CTO #482/#486).
ROLE_CEILINGS: dict[str, int] = {
    "DataCurator": 256,
    "Literature": 1316,
    "Architect": 256,
    "Trainer": 256,
    "Validator": 1192,
}
SAMPLING: dict[str, dict[str, Any]] = {HAIKU: {"temperature": 0.3}, SONNET: {}}
THINKING: dict[str, dict[str, Any]] = {
    HAIKU: {},
    SONNET: {"thinking": {"type": "between_tools"}, "effort": "low"},
}

_FATAL = frozenset({401, 402, 403})
_COOLING = frozenset({408, 409, 429, 500, 502, 503, 504, 529})

_NUM = {"type": "number"}
_INT = {"type": "integer"}
_STR = {"type": "string"}


def _obj(props: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": props,
        "required": list(props),
        "additionalProperties": False,
    }


def role_wire_schema(role: str, backbone_menu: tuple[str, ...]) -> dict[str, Any]:
    """The structured-output schema the model sees (A4-1 implementation note)."""
    if role == "DataCurator":
        return _obj(
            {"hvg_method": _STR, "hvg_count": _INT, "qc_mito_max": _NUM, "confidence": _NUM}
        )
    if role == "Literature":
        return _obj(
            {
                "pathway_prior": {
                    "type": "array",
                    "items": _obj({"pathway": _STR, "weight": _NUM}),
                },
                "tool_calls": {"type": "array", "items": _STR},
                "expected_up": {"type": "array", "items": _STR},
                "expected_down": {"type": "array", "items": _STR},
                "confidence": _NUM,
            }
        )
    if role == "Architect":
        return _obj(
            {
                "backbone": {"type": "string", "enum": list(backbone_menu)},
                "hvg_count": _INT,
                "learning_rate": _NUM,
                "ridge_lambda": _NUM,
                "epochs": _INT,
                "confidence": _NUM,
            }
        )
    if role == "Trainer":
        return _obj({"lr": _NUM, "epochs": _INT, "ridge_lambda": _NUM, "confidence": _NUM})
    if role == "Validator":
        return _obj(
            {
                "dynamic_threshold_msd": _NUM,
                "critique": _obj(
                    {
                        "which_genes_failed": {"type": "array", "items": _STR},
                        "suggested_next_config_delta": {
                            "type": "array",
                            "items": _obj({"field": _STR, "value": _STR}),
                        },
                        "accept_reason": _STR,
                    }
                ),
                "confidence": _NUM,
            }
        )
    raise ValueError(f"unknown role {role!r}")


def to_measurand(role: str, data: Mapping[str, Any]) -> dict[str, Any]:
    """Undo the wire-only adaptations (pair arrays -> dicts). Ranges are NOT touched here:
    the pydantic role schema enforces them afterwards (never a clamp)."""
    out = dict(data)
    if role == "Literature" and isinstance(out.get("pathway_prior"), list):
        out["pathway_prior"] = {
            str(e["pathway"]): e["weight"] for e in out["pathway_prior"] if isinstance(e, Mapping)
        }
    if role == "Validator" and isinstance(out.get("critique"), Mapping):
        crit = dict(out["critique"])
        delta = crit.get("suggested_next_config_delta")
        if isinstance(delta, list):
            crit["suggested_next_config_delta"] = {
                str(e["field"]): e["value"] for e in delta if isinstance(e, Mapping)
            }
        out["critique"] = crit
    return out


class AnthropicError(ProviderError):
    """Fallback-class provider failure (hard 4xx, served-model mismatch, twice-truncated)."""


def _menu() -> tuple[str, ...]:
    from perturb_eval.agentic_lifecycle.proposal_schema import BACKBONE_MENU

    return tuple(BACKBONE_MENU)


class AnthropicClient:
    """Paid Anthropic roster (A4-1). ``create_fn`` is injectable for tests; it must accept the
    Messages API keyword arguments and return an object with ``content`` (blocks with ``.type`` /
    ``.text``), ``model``, ``stop_reason``, optional ``stop_details`` and ``usage``."""

    def __init__(
        self,
        *,
        api_key: str,
        cache_dir: Path,
        pool: LLMPool = ANTHROPIC_POOL,
        cooldown_sec: float = 60.0,
        timeout_sec: float = 60.0,
        max_wait_sec: float = 300.0,
        sleep: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.time,
        create_fn: Optional[Callable[..., Any]] = None,
        price_table: Mapping[str, Mapping[str, float]] = PRICE_TABLE,
        ceilings: Mapping[str, int] = ROLE_CEILINGS,
        sampling: Mapping[str, Mapping[str, Any]] = SAMPLING,
    ) -> None:
        self._api_key = api_key
        self._cache_dir = Path(cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._pool = pool
        self._cooldown_sec = cooldown_sec
        self._timeout_sec = timeout_sec
        self._max_wait_sec = max_wait_sec
        self._sleep = sleep
        self._clock = clock
        self._create = create_fn
        self._price = {k: dict(v) for k, v in price_table.items()}
        self._ceilings = dict(ceilings)
        self._sampling = {k: dict(v) for k, v in sampling.items()}
        self._cooldowns: dict[str, float] = {}
        self.call_log: list[dict[str, Any]] = []
        self.spend_usd: float = 0.0
        self.n_served_mismatch = 0

    # ------------------------------------------------------------ SDK plumbing
    def _sdk_create(self, **kw: Any) -> Any:
        import anthropic

        if self._create is None:
            self._create = anthropic.Anthropic(
                api_key=self._api_key, timeout=self._timeout_sec, max_retries=0
            ).messages.create
        return self._create(**kw)

    def _classify(self, exc: BaseException) -> str:
        """'fatal' | 'cooling' | 'hard'."""
        status = getattr(exc, "status_code", None)
        if status in _FATAL:
            return "fatal"
        if status in _COOLING:
            return "cooling"
        try:
            import anthropic

            if isinstance(exc, (anthropic.APIConnectionError, anthropic.RateLimitError)):
                return "cooling"
        except ImportError:  # pragma: no cover
            pass
        if status is not None:
            return "hard"
        return "cooling" if isinstance(exc, (TimeoutError, ConnectionError, OSError)) else "hard"

    # ------------------------------------------------------------- request shape
    def build_request(
        self, *, model_id: str, role: str, prompt: str, max_tokens: int
    ) -> dict[str, Any]:
        kw: dict[str, Any] = {
            "model": model_id,
            "max_tokens": int(max_tokens),
            "messages": [{"role": "user", "content": prompt}],
            "output_config": {
                "format": {"type": "json_schema", "schema": role_wire_schema(role, _menu())}
            },
        }
        th = THINKING.get(model_id, {})
        if th.get("thinking"):
            kw["thinking"] = dict(th["thinking"])
        if th.get("effort"):
            kw["output_config"]["effort"] = th["effort"]
        samp = self._sampling.get(model_id, {})
        if samp:
            kw["extra_body"] = dict(
                samp
            )  # SDK 1.x removed the typed argument; the API accepts it on Haiku 4.5
        assert "fallbacks" not in kw  # A4-1: never a server-side substitution
        return kw

    def _cost(self, model_id: str, usage: Any) -> tuple[float, dict[str, int]]:
        u = {
            "input_tokens": int(getattr(usage, "input_tokens", 0) or 0),
            "output_tokens": int(getattr(usage, "output_tokens", 0) or 0),
            "cache_read_input_tokens": int(getattr(usage, "cache_read_input_tokens", 0) or 0),
            "cache_creation_input_tokens": int(
                getattr(usage, "cache_creation_input_tokens", 0) or 0
            ),
        }
        p = self._price[model_id]
        cost = (
            u["input_tokens"] * p["input"]
            + u["output_tokens"] * p["output"]
            + u["cache_read_input_tokens"] * p["cache_read"]
            + u["cache_creation_input_tokens"] * p["cache_write"]
        ) / 1e6
        return cost, u

    def _record(self, **rec: Any) -> None:
        self.call_log.append(rec)
        self.spend_usd += float(rec.get("cost_usd") or 0.0)

    # --------------------------------------------------------------- one call
    def _generate(
        self,
        *,
        model_id: str,
        role: str,
        prompt: str,
        task_id: str,
        round_index: int,
        max_tokens: int,
        attempt: int,
    ) -> dict[str, Any]:
        """One API call. Returns the parsed measurand dict, or raises."""
        kw = self.build_request(model_id=model_id, role=role, prompt=prompt, max_tokens=max_tokens)
        r = self._sdk_create(**kw)
        cost, usage = self._cost(model_id, getattr(r, "usage", None))
        served = getattr(r, "model", None)
        stop = getattr(r, "stop_reason", None)
        details = getattr(r, "stop_details", None)
        category = getattr(details, "category", None) if stop == "refusal" else None
        rec = {
            "role": role,
            "task_id": task_id,
            "round_index": round_index,
            "requested_model": model_id,
            "served_model": served,
            "served_equals_requested": served == model_id,
            "stop_reason": stop,
            "stop_category": category,
            "max_tokens": max_tokens,
            "attempt": attempt,
            "cost_usd": round(cost, 6),
            **usage,
        }
        self._record(**rec)
        if served != model_id:
            self.n_served_mismatch += 1
            raise AnthropicError(
                f"served model {served!r} != requested {model_id!r} (fallback-class event)"
            )
        if stop == "refusal":
            raise ProviderFatalError(
                f"{model_id}: refusal (category={category!r}) — aborting the run, never a fallback"
            )
        if stop == "max_tokens":
            raise _Truncated(model_id, max_tokens)
        text = next(
            (b.text for b in getattr(r, "content", []) if getattr(b, "type", "") == "text"), ""
        )
        if not text:
            raise AnthropicError(f"{model_id}: empty reply (stop_reason={stop!r})")
        try:
            data = _extract_json(text)
        except (ValueError, json.JSONDecodeError) as exc:
            raise AnthropicError(f"{model_id}: reply is not a JSON object") from exc
        return to_measurand(role, data)

    def _cache_path(self, key: str) -> Path:
        sub = self._cache_dir / key[:2]
        sub.mkdir(parents=True, exist_ok=True)
        return sub / f"{key}.json"

    def _cooling_ids(self) -> set[str]:
        now = self._clock()
        return {m for m, until in self._cooldowns.items() if until > now}

    def _candidates(self, role: str, hard_failed: set[str]) -> list[str]:
        prefs = list(self._pool.role_preferences.get(role, ()))
        ordered = prefs + [m.model_id for m in self._pool.models if m.model_id not in prefs]
        cooling = self._cooling_ids()
        return [m for m in ordered if m not in cooling and m not in hard_failed]

    def chat_json(
        self, *, role: str, task_id: str, round_index: int, prompt: str, seed: int, dataset: str
    ) -> ChatResult:
        deadline = self._clock() + self._max_wait_sec
        hard_failed: set[str] = set()
        last_err: Optional[str] = None
        ceiling = int(self._ceilings.get(role, 256))
        while True:
            cooling_at_start = self._cooling_ids()
            for model_id in self._candidates(role, hard_failed):
                key = _cache_key(
                    dataset=dataset,
                    task_id=task_id,
                    round_index=round_index,
                    role=role,
                    prompt=prompt,
                    model_id=model_id,
                    seed=seed,
                )
                path = self._cache_path(key)
                if path.exists():
                    try:
                        cached = json.loads(path.read_text())
                    except json.JSONDecodeError:
                        cached = None
                    if cached is not None:
                        self._record(
                            role=role,
                            task_id=task_id,
                            round_index=round_index,
                            requested_model=model_id,
                            served_model=model_id,
                            served_equals_requested=True,
                            stop_reason="cache_hit",
                            stop_category=None,
                            max_tokens=ceiling,
                            attempt=0,
                            cost_usd=0.0,
                        )
                        return ChatResult(
                            content=cached,
                            model_id=model_id,
                            cache_hit=True,
                            stop_reason="cache_hit",
                            served_model=model_id,
                            usage=None,
                        )
                max_tokens = ceiling
                for attempt in (1, 2):
                    try:
                        data = self._generate(
                            model_id=model_id,
                            role=role,
                            prompt=prompt,
                            task_id=task_id,
                            round_index=round_index,
                            max_tokens=max_tokens,
                            attempt=attempt,
                        )
                    except _Truncated:
                        if attempt == 1:
                            max_tokens = ceiling * 2  # A4-1: one retry at 2x, both billed
                            continue
                        last_err = f"{model_id}: max_tokens twice (ceiling {ceiling})"
                        hard_failed.add(model_id)
                        break
                    except ProviderFatalError:
                        raise
                    except AnthropicError as exc:
                        last_err = str(exc)
                        hard_failed.add(model_id)
                        break
                    except Exception as exc:  # SDK / transport errors
                        kind = self._classify(exc)
                        if kind == "fatal":
                            raise ProviderFatalError(
                                f"{model_id}: {type(exc).__name__} status={getattr(exc, 'status_code', None)} — aborting"
                            ) from exc
                        if kind == "cooling":
                            self._cooldowns[model_id] = self._clock() + self._cooldown_sec
                            last_err = f"{model_id}: transient {type(exc).__name__} status={getattr(exc, 'status_code', None)}"
                        else:
                            hard_failed.add(model_id)
                            last_err = f"{model_id}: {type(exc).__name__} status={getattr(exc, 'status_code', None)}"
                        break
                    else:
                        path.write_text(json.dumps(data))
                        last = self.call_log[-1]
                        return ChatResult(
                            content=data,
                            model_id=model_id,
                            cache_hit=False,
                            stop_reason=last["stop_reason"],
                            served_model=last["served_model"],
                            usage={
                                k: last[k]
                                for k in (
                                    "input_tokens",
                                    "output_tokens",
                                    "cache_read_input_tokens",
                                    "cache_creation_input_tokens",
                                )
                            },
                        )
            cooling_now = self._cooling_ids()
            if not cooling_now and not cooling_at_start:
                raise AnthropicError(
                    f"all candidate models for role={role} failed; last_err={last_err}"
                )
            now = self._clock()
            if now >= deadline:
                raise RateLimitedError(
                    f"role={role}: every model cooling and the {self._max_wait_sec:.0f}s wait budget is spent; last_err={last_err}"
                )
            ends = [t for t in self._cooldowns.values() if t > now]
            pause = (min(ends) - now) if ends else 0.0
            self._sleep(min(max(pause, 0.0), deadline - now) + 0.01)

    # ---------------------------------------------------------------- preflight
    def probe_model(
        self, model_id: str, prompt: str, role: str = "Validator"
    ) -> tuple[bool, str, Optional[dict]]:
        """One direct call, no cache, no retry, no failover (preflight liveness per role)."""
        try:
            data = self._generate(
                model_id=model_id,
                role=role,
                prompt=prompt,
                task_id="__preflight__",
                round_index=0,
                max_tokens=int(self._ceilings.get(role, 256)),
                attempt=1,
            )
        except _Truncated:
            return False, "max_tokens at the ceiling", None
        except ProviderFatalError as exc:
            return False, f"fatal: {exc}", None
        except AnthropicError as exc:
            return False, str(exc), None
        except Exception as exc:  # noqa: BLE001 — the verdict is recorded, never raised
            return (
                False,
                f"transport {type(exc).__name__} status={getattr(exc, 'status_code', None)}",
                None,
            )
        return True, "ok", data

    def spend(self) -> dict[str, Any]:
        by_model: dict[str, float] = {}
        stops: dict[str, int] = {}
        for c in self.call_log:
            by_model[c["requested_model"]] = by_model.get(c["requested_model"], 0.0) + float(
                c.get("cost_usd") or 0.0
            )
            stops[str(c.get("stop_reason"))] = stops.get(str(c.get("stop_reason")), 0) + 1
        return {
            "spend_usd": round(self.spend_usd, 6),
            "calls": len(self.call_log),
            "by_model": by_model,
            "stop_reason_counts": stops,
            "served_mismatch_count": self.n_served_mismatch,
            "price_table": self._price,
            "price_table_source": PRICE_TABLE_SOURCE,
            "role_ceilings": self._ceilings,
            "sampling": self._sampling,
            "thinking": THINKING,
        }


class _Truncated(Exception):
    def __init__(self, model_id: str, max_tokens: int) -> None:
        super().__init__(f"{model_id}: stop_reason=max_tokens at {max_tokens}")


__all__ = [
    "ANTHROPIC_POOL",
    "AnthropicClient",
    "AnthropicError",
    "HAIKU",
    "PRICE_TABLE",
    "PRICE_TABLE_SOURCE",
    "ROLE_CEILINGS",
    "SAMPLING",
    "SONNET",
    "THINKING",
    "role_wire_schema",
    "to_measurand",
]
