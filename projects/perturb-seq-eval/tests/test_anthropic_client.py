"""Amendment 4 (A4-1) AnthropicClient — the CTO #480/#482/#486 test list.

stop_reason recorded on every call; refusal aborts with its category (ProviderFatal, never a fallback);
max_tokens -> one retry at 2x (both billed) then a fallback-class error; served model asserted equal to the
requested id; no `fallbacks` key in any request body; out-of-range value = pydantic schema failure (no clamp);
spend = usage x price table; model_id-per-call provenance; cache-hit replay unchanged; fatal 401/402/403;
transient errors cool + fail over; preflight probes per role with the Anthropic client.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from perturb_eval.llm import anthropic_client as ac
from perturb_eval.llm.anthropic_client import (
    ANTHROPIC_POOL,
    HAIKU,
    SONNET,
    AnthropicClient,
    AnthropicError,
)
from perturb_eval.llm.openrouter_client import ProviderError, ProviderFatalError, RateLimitedError

ROLES = ("DataCurator", "Literature", "Architect", "Trainer", "Validator")
GOOD = {
    "DataCurator": {
        "hvg_method": "seurat",
        "hvg_count": 2000,
        "qc_mito_max": 12.0,
        "confidence": 0.5,
    },
    "Literature": {
        "pathway_prior": [{"pathway": "p53", "weight": 0.4}],
        "tool_calls": [],
        "expected_up": ["MYC"],
        "expected_down": [],
        "confidence": 0.6,
    },
    "Architect": {
        "backbone": "linear",
        "hvg_count": 2000,
        "learning_rate": 0.01,
        "ridge_lambda": 1.0,
        "epochs": 30,
        "confidence": 0.7,
    },
    "Trainer": {"lr": 0.01, "epochs": 30, "ridge_lambda": 1.0, "confidence": 0.5},
    "Validator": {
        "dynamic_threshold_msd": 0.1,
        "critique": {
            "which_genes_failed": [],
            "suggested_next_config_delta": [{"field": "backbone", "value": "mlp"}],
            "accept_reason": "ok",
        },
        "confidence": 0.8,
    },
}


def _msg(payload, *, model, stop="end_turn", category=None, inp=400, out=50, cache_read=0):
    return SimpleNamespace(
        content=[SimpleNamespace(type="text", text=json.dumps(payload))],
        model=model,
        stop_reason=stop,
        stop_details=SimpleNamespace(type="refusal", category=category)
        if stop == "refusal"
        else None,
        usage=SimpleNamespace(
            input_tokens=inp,
            output_tokens=out,
            cache_read_input_tokens=cache_read,
            cache_creation_input_tokens=0,
        ),
    )


class _Fake:
    """Scripted create_fn: per model a list of responses/exceptions (last repeats); records every request."""

    def __init__(self, script):
        self.script = {k: list(v) for k, v in script.items()}
        self.requests: list[dict] = []

    def __call__(self, **kw):
        self.requests.append(kw)
        q = self.script[kw["model"]]
        item = q.pop(0) if len(q) > 1 else q[0]
        if isinstance(item, BaseException):
            raise item
        return item


def _client(tmp_path, fake, **kw):
    clock = [1000.0]
    slept: list[float] = []

    def sleep(s):
        slept.append(s)
        clock[0] += s

    c = AnthropicClient(
        api_key="k",
        cache_dir=tmp_path,
        create_fn=fake,
        cooldown_sec=10.0,
        sleep=sleep,
        clock=lambda: clock[0],
        **kw,
    )
    return c, slept


def _call(c, role="Validator", task="t", rnd=0, prompt="p"):
    return c.chat_json(role=role, task_id=task, round_index=rnd, prompt=prompt, seed=0, dataset="d")


class _Status(Exception):
    def __init__(self, status):
        super().__init__(f"http {status}")
        self.status_code = status


class TestRequestShape:
    @pytest.mark.parametrize("role", ROLES)
    def test_no_fallbacks_key_and_structured_output_on_every_request(self, tmp_path, role):
        model = ANTHROPIC_POOL.role_preferences[role][0]
        fake = _Fake({model: [_msg(GOOD[role], model=model)]})
        c, _ = _client(tmp_path, fake)
        _call(c, role)
        for kw in fake.requests:
            assert "fallbacks" not in kw and "fallbacks" not in json.dumps(kw.get("extra_body", {}))
            assert kw["output_config"]["format"]["type"] == "json_schema"
            assert kw["output_config"]["format"]["schema"]["additionalProperties"] is False
            assert "minimum" not in json.dumps(kw["output_config"]["format"]["schema"])

    def test_sonnet_thinking_between_tools_effort_in_output_config_no_sampling(self, tmp_path):
        fake = _Fake({SONNET: [_msg(GOOD["Validator"], model=SONNET)]})
        c, _ = _client(tmp_path, fake)
        _call(c, "Validator")
        kw = fake.requests[0]
        assert (
            kw["thinking"] == {"type": "between_tools"} and kw["output_config"]["effort"] == "low"
        )
        assert "temperature" not in kw and "extra_body" not in kw

    def test_haiku_temperature_0_3_in_raw_body_no_thinking(self, tmp_path):
        fake = _Fake({HAIKU: [_msg(GOOD["Architect"], model=HAIKU)]})
        c, _ = _client(tmp_path, fake)
        _call(c, "Architect")
        kw = fake.requests[0]
        assert (
            kw["extra_body"] == {"temperature": 0.3}
            and "thinking" not in kw
            and "effort" not in kw["output_config"]
        )

    def test_role_ceiling_is_the_max_tokens(self, tmp_path):
        fake = _Fake({HAIKU: [_msg(GOOD["Literature"], model=HAIKU)]})
        c, _ = _client(tmp_path, fake)
        _call(c, "Literature")
        assert fake.requests[0]["max_tokens"] == ac.ROLE_CEILINGS["Literature"] == 1316


class TestProvenanceAndStopReason:
    def test_model_id_and_stop_reason_recorded_per_call(self, tmp_path):
        fake = _Fake({HAIKU: [_msg(GOOD["Trainer"], model=HAIKU)]})
        c, _ = _client(tmp_path, fake)
        res = _call(c, "Trainer")
        assert (
            res.model_id == HAIKU == res.served_model
            and res.stop_reason == "end_turn"
            and res.cache_hit is False
        )
        log = c.call_log[-1]
        assert (
            log["stop_reason"] == "end_turn"
            and log["served_equals_requested"] is True
            and log["requested_model"] == HAIKU
        )

    def test_refusal_aborts_with_category_recorded_and_is_not_a_fallback(self, tmp_path):
        fake = _Fake(
            {
                SONNET: [_msg({}, model=SONNET, stop="refusal", category="bio")],
                HAIKU: [_msg(GOOD["Validator"], model=HAIKU)],
            }
        )
        c, _ = _client(tmp_path, fake)
        with pytest.raises(ProviderFatalError, match="bio"):
            _call(c, "Validator")
        assert not issubclass(ProviderFatalError, ProviderError)
        assert (
            c.call_log[-1]["stop_reason"] == "refusal" and c.call_log[-1]["stop_category"] == "bio"
        )
        assert [kw["model"] for kw in fake.requests] == [
            SONNET
        ]  # never silently retried on the other model

    def test_max_tokens_one_retry_at_2x_both_billed_then_success(self, tmp_path):
        fake = _Fake(
            {
                HAIKU: [
                    _msg(GOOD["Trainer"], model=HAIKU, stop="max_tokens"),
                    _msg(GOOD["Trainer"], model=HAIKU),
                ]
            }
        )
        c, _ = _client(tmp_path, fake)
        res = _call(c, "Trainer")
        assert res.stop_reason == "end_turn"
        assert [kw["max_tokens"] for kw in fake.requests] == [256, 512]
        assert [r["stop_reason"] for r in c.call_log] == [
            "max_tokens",
            "end_turn",
        ] and c.spend_usd > 0

    def test_max_tokens_twice_is_a_fallback_class_event(self, tmp_path):
        fake = _Fake(
            {
                HAIKU: [_msg(GOOD["Trainer"], model=HAIKU, stop="max_tokens")],
                SONNET: [_msg(GOOD["Trainer"], model=SONNET, stop="max_tokens")],
            }
        )
        c, _ = _client(tmp_path, fake)
        with pytest.raises(AnthropicError, match="max_tokens twice|all candidate"):
            _call(c, "Trainer")
        assert isinstance(AnthropicError("x"), ProviderError)
        assert len(c.call_log) == 4  # two attempts per model, all billed/recorded

    def test_served_model_mismatch_is_a_fallback_class_event(self, tmp_path):
        fake = _Fake(
            {
                HAIKU: [_msg(GOOD["Trainer"], model="claude-something-else")],
                SONNET: [_msg(GOOD["Trainer"], model="claude-other")],
            }
        )
        c, _ = _client(tmp_path, fake)
        with pytest.raises(AnthropicError):
            _call(c, "Trainer")
        assert c.n_served_mismatch >= 1 and c.call_log[0]["served_equals_requested"] is False

    def test_cache_hit_replay_without_a_request(self, tmp_path):
        fake = _Fake({HAIKU: [_msg(GOOD["Trainer"], model=HAIKU)]})
        c, _ = _client(tmp_path, fake)
        a = _call(c, "Trainer")
        b = _call(c, "Trainer")
        assert a.cache_hit is False and b.cache_hit is True and len(fake.requests) == 1
        assert c.call_log[-1]["stop_reason"] == "cache_hit" and c.call_log[-1]["cost_usd"] == 0.0


class TestSpend:
    def test_spend_is_usage_times_price_table_incl_cache_read(self, tmp_path):
        fake = _Fake(
            {
                HAIKU: [_msg(GOOD["Trainer"], model=HAIKU, inp=1000, out=100, cache_read=500)],
                SONNET: [_msg(GOOD["Validator"], model=SONNET, inp=2000, out=200)],
            }
        )
        c, _ = _client(tmp_path, fake)
        _call(c, "Trainer")
        _call(c, "Validator")
        exp = (1000 * 1.0 + 100 * 5.0 + 500 * 0.10) / 1e6 + (2000 * 2.0 + 200 * 10.0) / 1e6
        assert c.spend_usd == pytest.approx(exp, rel=1e-9)
        rep = c.spend()
        assert (
            rep["calls"] == 2
            and rep["price_table"][HAIKU]["output"] == 5.0
            and rep["stop_reason_counts"] == {"end_turn": 2}
        )
        assert rep["role_ceilings"]["Validator"] == 1192 and rep["served_mismatch_count"] == 0


class TestFailureClasses:
    @pytest.mark.parametrize("status", [401, 402, 403])
    def test_fatal_statuses_abort(self, tmp_path, status):
        fake = _Fake({HAIKU: [_Status(status)], SONNET: [_msg(GOOD["Trainer"], model=SONNET)]})
        c, _ = _client(tmp_path, fake)
        with pytest.raises(ProviderFatalError):
            _call(c, "Trainer")

    @pytest.mark.parametrize("status", [429, 529, 503])
    def test_transient_cools_and_fails_over(self, tmp_path, status):
        fake = _Fake({HAIKU: [_Status(status)], SONNET: [_msg(GOOD["Trainer"], model=SONNET)]})
        c, slept = _client(tmp_path, fake)
        res = _call(c, "Trainer")
        assert res.model_id == SONNET and c._cooldowns.get(HAIKU, 0) > 1000.0

    def test_all_cooling_waits_then_raises_after_budget(self, tmp_path):
        fake = _Fake({HAIKU: [_Status(429)], SONNET: [_Status(529)]})
        c, slept = _client(tmp_path, fake, max_wait_sec=25.0)
        with pytest.raises(RateLimitedError, match="wait budget"):
            _call(c, "Trainer")
        assert 20.0 <= sum(slept) <= 25.1

    def test_hard_400_does_not_wait_and_fails_over(self, tmp_path):
        fake = _Fake({HAIKU: [_Status(400)], SONNET: [_msg(GOOD["Trainer"], model=SONNET)]})
        c, slept = _client(tmp_path, fake)
        assert _call(c, "Trainer").model_id == SONNET and slept == []


class TestMeasurandSchema:
    def test_out_of_range_value_is_a_schema_failure_in_the_pool_never_clamped(self, tmp_path):
        from perturb_eval.agentic_lifecycle.llm_agent_pool import LLMAgentPool

        bad = dict(GOOD["Validator"], confidence=1.5)  # out of [0, 1]
        fake = _Fake({SONNET: [_msg(bad, model=SONNET)]})
        c, _ = _client(tmp_path, fake)
        pool = LLMAgentPool(client=c, cache_dir=tmp_path / "pool")
        out = pool.propose("Validator", 0, "TFA", {}, seed=0, dataset="adamson_full")
        assert (
            out["source"] == "fallback" and out["confidence"] is None
        )  # ValidationError -> fallback, no clamp

    def test_pair_arrays_are_converted_back_to_maps(self):
        d = ac.to_measurand("Validator", GOOD["Validator"])
        assert d["critique"]["suggested_next_config_delta"] == {"backbone": "mlp"}
        assert ac.to_measurand("Literature", GOOD["Literature"])["pathway_prior"] == {"p53": 0.4}

    def test_pool_carries_stop_reason_and_served_model(self, tmp_path):
        from perturb_eval.agentic_lifecycle.llm_agent_pool import LLMAgentPool

        fake = _Fake({HAIKU: [_msg(GOOD["Trainer"], model=HAIKU)]})
        c, _ = _client(tmp_path, fake)
        out = LLMAgentPool(client=c, cache_dir=tmp_path / "pool").propose(
            "Trainer", 0, "TFA", {}, seed=0, dataset="adamson_full"
        )
        assert (
            out["source"] == "llm"
            and out["stop_reason"] == "end_turn"
            and out["served_model"] == HAIKU
        )


class TestRosterAndPreflight:
    def test_pool_is_the_pinned_two_model_roster(self):
        ids = [m.model_id for m in ANTHROPIC_POOL.models]
        assert ids == [HAIKU, SONNET] and not any(i.endswith(":free") for i in ids)
        for role in ROLES:
            assert set(ANTHROPIC_POOL.role_preferences[role]) == {HAIKU, SONNET}
        assert (
            ANTHROPIC_POOL.role_preferences["Validator"][0] == SONNET
        )  # A4-3: judge on a different tier
        assert all(
            ANTHROPIC_POOL.role_preferences[r][0] == HAIKU for r in ROLES if r != "Validator"
        )

    def test_preflight_probes_each_role_with_the_role_schema(self, monkeypatch):
        from perturb_eval.experiments import v05_preflight as pf

        seen = []

        def fake_probe(self, model_id, prompt, role="Validator"):
            seen.append((model_id, role))
            return True, "ok", dict(pf.ROLE_PROBE_PAYLOADS[role])

        monkeypatch.setattr(AnthropicClient, "probe_model", fake_probe)
        table = pf.openrouter_probe_all({"ANTHROPIC_API_KEY": "k"})
        assert set(table) == {HAIKU, SONNET} and all(e["live"] for e in table.values())
        for role in ROLES:
            for mid in ANTHROPIC_POOL.role_preferences[role]:
                assert (mid, role) in seen

    def test_preflight_key_name_is_anthropic(self):
        from perturb_eval.experiments import v05_preflight as pf

        assert pf.KEY_NAME == "ANTHROPIC_API_KEY" and pf.KEY_SOURCE_NAME == "LLM_KEY_SOURCE"

    def test_app_v05_wiring(self):
        src = (Path(__file__).resolve().parents[1] / "scripts" / "modal" / "app_v05.py").read_text()
        assert "fallbacks" not in src
        assert (
            '"ANTHROPIC_API_KEY", "LLM_KEY_SOURCE"' in src
            and 'os.environ["ANTHROPIC_API_KEY"]' in src
        )
        assert "AnthropicClient(" in src and "OpenRouterClient(" not in src
        assert '"anthropic>=1.9,<2"' in src  # Modal image dependency
        assert "llm_call_log" in src and "llm_price_table" in src
