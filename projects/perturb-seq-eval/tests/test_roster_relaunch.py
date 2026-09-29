"""Relaunch fixes after the aborted v0.6.0 run (CTO #467; principal 2026-09-28: paid, cheapest JSON-capable tier).

1. The roster has NO :free endpoints (they died / rate-limit into fallbacks, and A2-1 makes a fallback fatal);
   every role names 3 preferred models that are in the pool; the pool spans >= 5 families.
2. A 429 / 5xx never becomes a fallback while a model is merely cooling: chat_json WAITS (bounded) for the
   earliest cooldown, then retries; it raises only when the wait budget is exhausted or nothing is cooling.
3. Preflight probes EVERY roster model with the Validator JSON schema, records a liveness table, refuses when
   any role has < 2 live preferred models, and FAILS when it probed fewer models than the roster lists.
4. The liveness table (id, probed_at, verdict) is recorded in provenance; app_v05 passes it.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from types import SimpleNamespace

import pytest

from perturb_eval.llm import openrouter_client as oc
from perturb_eval.llm.openrouter_client import DEFAULT_POOL, LLMPool, ModelSpec, OpenRouterClient

ROLES = ("DataCurator", "Literature", "Architect", "Trainer", "Validator")


# ------------------------------------------------------------------ 1. roster
class TestRoster:
    def test_no_free_endpoints_three_prefs_per_role_five_families(self) -> None:
        ids = [m.model_id for m in DEFAULT_POOL.models]
        assert ids and not any(i.endswith(":free") for i in ids), ids
        assert len(set(ids)) == len(ids)
        for role in ROLES:
            prefs = DEFAULT_POOL.role_preferences[role]
            assert len(prefs) == 3 and len(set(prefs)) == 3
            assert set(prefs) <= set(ids), (role, prefs)
        assert len({m.family for m in DEFAULT_POOL.models}) >= 5


# ------------------------------------------------------- 2. bounded cooldown wait
class _Resp:
    def __init__(self, status: int, content: str | None) -> None:
        self.status_code = status
        self._content = content

    def json(self) -> dict:
        if self._content is None:
            raise ValueError("no body")
        return {"choices": [{"message": {"content": self._content}}]}


class _Session:
    """Scripted responses per model id, consumed in order; the last one repeats."""

    def __init__(self, script: dict[str, list], *, on_post=None, max_calls: int = 200) -> None:
        self.script = {k: list(v) for k, v in script.items()}
        self.calls: list[str] = []
        self.on_post = on_post
        self.max_calls = (
            max_calls  # QG-10: an iteration guard so a broken loop fails instead of hanging
        )

    def post(self, url, headers=None, json=None, timeout=None):  # noqa: ANN001
        mid = json["model"]
        self.calls.append(mid)
        assert len(self.calls) <= self.max_calls, "runaway retry loop"
        if self.on_post is not None:
            self.on_post(mid)
        q = self.script[mid]
        item = q.pop(0) if len(q) > 1 else q[0]
        if isinstance(item, Exception):
            raise item
        return item


def _two_model_pool() -> LLMPool:
    a = ModelSpec(model_id="x/a", family="fa", param_count_b=1, strengths=())
    b = ModelSpec(model_id="x/b", family="fb", param_count_b=1, strengths=())
    return LLMPool(models=(a, b), role_preferences={r: ("x/a", "x/b") for r in ROLES})


def _client(
    tmp_path: Path, session: _Session, **kw
) -> tuple[OpenRouterClient, list[float], list[float]]:
    clock = [1000.0]
    slept: list[float] = []

    def fake_sleep(s: float) -> None:
        slept.append(s)
        clock[0] += s

    c = OpenRouterClient(
        api_key="k",
        cache_dir=tmp_path,
        pool=_two_model_pool(),
        cooldown_sec=10.0,
        session=session,
        sleep=fake_sleep,
        clock=lambda: clock[0],
        **kw,
    )
    return c, slept, clock


class TestCooldownWait:
    def test_waits_for_cooldown_then_succeeds_instead_of_falling_back(self, tmp_path: Path) -> None:
        good = '{"confidence": 0.5, "dynamic_threshold_msd": 0.1}'
        sess = _Session(
            {
                "x/a": [_Resp(429, None), _Resp(200, good)],
                "x/b": [_Resp(429, None), _Resp(429, None)],
            }
        )
        c, slept, _ = _client(tmp_path, sess, max_wait_sec=60.0)
        res = c.chat_json(
            role="Validator", task_id="t", round_index=0, prompt="p", seed=0, dataset="d"
        )
        assert res.content["confidence"] == 0.5 and res.model_id == "x/a" and res.cache_hit is False
        # QG-10: it waited ONCE for the 10 s cooldown (no busy polling) and then retried x/a first.
        assert sess.calls == ["x/a", "x/b", "x/a"]
        assert len(slept) == 1 and slept[0] == pytest.approx(10.01, abs=0.02)

    def test_raises_only_after_wait_budget_exhausted(self, tmp_path: Path) -> None:
        sess = _Session({"x/a": [_Resp(429, None)], "x/b": [_Resp(503, None)]})
        c, slept, _ = _client(tmp_path, sess, max_wait_sec=25.0)
        with pytest.raises(oc.OpenRouterError):
            c.chat_json(
                role="Validator", task_id="t", round_index=0, prompt="p", seed=0, dataset="d"
            )
        assert 20.0 <= sum(slept) <= 25.0 + 10.0

    def test_dead_models_do_not_wait(self, tmp_path: Path) -> None:
        sess = _Session({"x/a": [_Resp(404, None)], "x/b": [_Resp(404, None)]})
        c, slept, _ = _client(tmp_path, sess, max_wait_sec=60.0)
        with pytest.raises(oc.OpenRouterError, match="404"):
            c.chat_json(
                role="Validator", task_id="t", round_index=0, prompt="p", seed=0, dataset="d"
            )
        assert slept == []  # nothing is cooling: no point waiting

    def test_probe_model_reports_live_and_verdict(self, tmp_path: Path) -> None:
        good = '{"confidence": 0.5, "dynamic_threshold_msd": 0.1}'
        sess = _Session({"x/a": [_Resp(200, good)], "x/b": [_Resp(404, None)]})
        c, _, _ = _client(tmp_path, sess)
        live, verdict, parsed = c.probe_model("x/a", "p")
        assert live and parsed["confidence"] == 0.5
        live_b, verdict_b, parsed_b = c.probe_model("x/b", "p")
        assert not live_b and "404" in verdict_b and parsed_b is None


# ------------------------------------------------------------- 3. preflight
from tests.test_v05_preflight import _POOL, _liveness, _run  # noqa: E402


class TestPreflightProbesEveryRosterModel:
    def test_probing_fewer_models_than_the_roster_fails(self, tmp_path: Path) -> None:
        from perturb_eval.experiments.v05_preflight import PreflightError

        partial = _liveness()
        del partial[_POOL.models[-1].model_id]  # one model never probed at all
        with pytest.raises(PreflightError, match=r"probed 2 of 3 roster models"):
            _run(tmp_path, probe_fn=lambda env: partial)

    def test_role_with_fewer_than_two_live_preferred_models_fails(self, tmp_path: Path) -> None:
        from perturb_eval.experiments.v05_preflight import PreflightError

        table = _liveness(live=["stub/one"])  # Architect prefs = (one, two, three): only one live
        with pytest.raises(PreflightError, match=r"Architect.*1 live preferred"):
            _run(tmp_path, probe_fn=lambda env: table)

    def test_report_carries_liveness_table_with_probe_dates(self, tmp_path: Path) -> None:
        rep = _run(tmp_path)
        assert set(rep.roster_liveness) == {m.model_id for m in _POOL.models}
        for e in rep.roster_liveness.values():
            assert (
                e["live"] is True
                and re.match(r"\d{4}-\d{2}-\d{2}T", e["probed_at"])
                and e["verdict"]
            )

    def test_default_probe_marks_schema_invalid_reply_as_not_live(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        """A bare {"confidence"} reply fails the Architect (backbone) and Validator (threshold, A3-3)
        schemas; a model preferred for either is therefore not live, with the role named."""
        from perturb_eval.experiments import v05_preflight as pf

        monkeypatch.setattr(
            OpenRouterClient, "probe_model", lambda self, m, p: (True, "ok", {"confidence": 0.5})
        )
        table = pf.openrouter_probe_all({"OPENROUTER_API_KEY": "k"})
        strict = set(DEFAULT_POOL.role_preferences["Architect"]) | set(
            DEFAULT_POOL.role_preferences["Validator"]
        )
        for mid in strict:
            assert table[mid]["live"] is False and "schema failed" in table[mid]["verdict"], mid
        assert any(
            "Architect" in table[m]["verdict"] for m in DEFAULT_POOL.role_preferences["Architect"]
        )


# ------------------------------------------------------------ 4. provenance
class TestLivenessInProvenance:
    def test_build_provenance_records_liveness(self) -> None:
        from tests.test_provenance import _prov

        table = {"m/one": {"live": True, "verdict": "ok", "probed_at": "2026-09-28T23:00:00+00:00"}}
        p = _prov(llm_roster_liveness=table)
        assert p["llm_roster_liveness"] == table
        assert "llm_roster_liveness" in _prov()  # always present (None when not supplied)

    def test_build_provenance_rejects_malformed_liveness(self) -> None:
        from tests.test_provenance import _prov

        with pytest.raises(ValueError, match="llm_roster_liveness"):
            _prov(llm_roster_liveness={"m/one": {"live": "yes"}})

    def test_app_v05_passes_liveness_to_provenance(self) -> None:
        src = (Path(__file__).resolve().parents[1] / "scripts" / "modal" / "app_v05.py").read_text()
        assert "llm_roster_liveness=report.roster_liveness" in src


# ================================================================ relaunch QG
import requests  # noqa: E402

GOOD = '{"confidence": 0.5, "dynamic_threshold_msd": 0.1}'


class TestQG1TransportErrorsFailOver:
    def test_connection_error_on_first_model_fails_over_and_cools_it(self, tmp_path: Path) -> None:
        sess = _Session({"x/a": [requests.ConnectionError("reset")], "x/b": [_Resp(200, GOOD)]})
        c, slept, _ = _client(tmp_path, sess)
        res = c.chat_json(
            role="Validator", task_id="t", round_index=0, prompt="p", seed=0, dataset="d"
        )
        assert res.model_id == "x/b" and sess.calls == ["x/a", "x/b"] and slept == []
        assert c._cooldowns.get("x/a", 0) > 1000.0  # the transport failure cooled x/a

    def test_timeout_never_escapes_as_a_fallback_exception(self, tmp_path: Path) -> None:
        sess = _Session(
            {"x/a": [requests.Timeout("t")], "x/b": [requests.Timeout("t"), _Resp(200, GOOD)]}
        )
        c, slept, _ = _client(tmp_path, sess, max_wait_sec=60.0)
        res = c.chat_json(
            role="Validator", task_id="t", round_index=0, prompt="p", seed=0, dataset="d"
        )
        assert res.model_id == "x/b" and slept  # both cooled, waited, then x/b answered


class TestQG3HardFailuresNotRebilledAndClockDeadline:
    def test_hard_failed_model_is_skipped_on_later_passes(self, tmp_path: Path) -> None:
        sess = _Session({"x/a": [_Resp(404, None)], "x/b": [_Resp(429, None), _Resp(200, GOOD)]})
        c, slept, _ = _client(tmp_path, sess, max_wait_sec=60.0)
        res = c.chat_json(
            role="Validator", task_id="t", round_index=0, prompt="p", seed=0, dataset="d"
        )
        assert res.model_id == "x/b"
        assert sess.calls == ["x/a", "x/b", "x/b"]  # x/a (404) is NOT re-called (and not re-billed)

    def test_http_time_counts_against_the_wait_budget(self, tmp_path: Path) -> None:
        clock = [1000.0]
        slept: list[float] = []

        def fake_sleep(s: float) -> None:
            slept.append(s)
            clock[0] += s

        sess = _Session(
            {"x/a": [_Resp(429, None)], "x/b": [_Resp(429, None)]},
            on_post=lambda mid: clock.__setitem__(0, clock[0] + 100.0),
        )  # each call takes 100 s
        c = OpenRouterClient(
            api_key="k",
            cache_dir=tmp_path,
            pool=_two_model_pool(),
            cooldown_sec=10.0,
            session=sess,
            sleep=fake_sleep,
            clock=lambda: clock[0],
            max_wait_sec=150.0,
        )
        with pytest.raises(oc.RateLimitedError, match="wait budget"):
            c.chat_json(
                role="Validator", task_id="t", round_index=0, prompt="p", seed=0, dataset="d"
            )
        assert clock[0] - 1000.0 <= 150.0 + 100.0 + 0.1  # deadline is wall-clock, not sleep-sum
        assert len(sess.calls) <= 4


class TestQG4StatusClassesAndFatal:
    def test_500_and_408_cool_down_and_are_retried(self, tmp_path: Path) -> None:
        sess = _Session(
            {
                "x/a": [_Resp(500, None), _Resp(200, GOOD)],
                "x/b": [_Resp(408, None), _Resp(408, None)],
            }
        )
        c, slept, _ = _client(tmp_path, sess, max_wait_sec=60.0)
        res = c.chat_json(
            role="Validator", task_id="t", round_index=0, prompt="p", seed=0, dataset="d"
        )
        assert res.model_id == "x/a" and slept

    @pytest.mark.parametrize("status", [401, 402])
    def test_401_402_are_fatal_not_fallback(self, tmp_path: Path, status: int) -> None:
        sess = _Session({"x/a": [_Resp(status, None)], "x/b": [_Resp(200, GOOD)]})
        c, slept, _ = _client(tmp_path, sess)
        with pytest.raises(oc.ProviderFatalError):
            c.chat_json(
                role="Validator", task_id="t", round_index=0, prompt="p", seed=0, dataset="d"
            )
        assert not issubclass(oc.ProviderFatalError, oc.OpenRouterError)

    def test_pool_does_not_swallow_a_fatal_provider_error(self, tmp_path: Path) -> None:
        from perturb_eval.agentic_lifecycle.llm_agent_pool import FALLBACK_EXCEPTIONS, LLMAgentPool

        class _Fatal:
            def chat_json(self, **kw):
                raise oc.ProviderFatalError("http 402")

        assert not any(issubclass(oc.ProviderFatalError, e) for e in FALLBACK_EXCEPTIONS)
        pool = LLMAgentPool(client=_Fatal(), cache_dir=tmp_path)
        with pytest.raises(oc.ProviderFatalError):
            pool.propose("Validator", 0, "TFA", {}, seed=0, dataset="adamson_full")

    def test_app_v05_stops_the_sweep_on_the_first_fallback_step(self) -> None:
        src = (Path(__file__).resolve().parents[1] / "scripts" / "modal" / "app_v05.py").read_text()
        assert 'reason="fallback"' in src and "first fallback step" in src


class TestQG5CooldownExpiringDuringAPass:
    def test_model_available_again_after_the_pass_is_retried_not_skipped(
        self, tmp_path: Path
    ) -> None:
        clock = [1000.0]
        sess = _Session(
            {"x/a": [_Resp(200, GOOD)], "x/b": [_Resp(404, None)]},
            on_post=lambda mid: clock.__setitem__(0, clock[0] + 10.0),
        )
        c = OpenRouterClient(
            api_key="k",
            cache_dir=tmp_path,
            pool=_two_model_pool(),
            cooldown_sec=10.0,
            session=sess,
            sleep=lambda s: clock.__setitem__(0, clock[0] + s),
            clock=lambda: clock[0],
            max_wait_sec=60.0,
        )
        c._cooldowns["x/a"] = 1005.0  # cooling at pass start; expires while x/b is being tried
        res = c.chat_json(
            role="Validator", task_id="t", round_index=0, prompt="p", seed=0, dataset="d"
        )
        assert res.model_id == "x/a" and sess.calls == ["x/b", "x/a"]


class TestQG2SpendAccounting:
    def test_key_usage_usd_reads_and_memoises(self, tmp_path: Path) -> None:
        class _S:
            def __init__(self):
                self.gets = 0

            def get(self, url, headers=None, timeout=None):  # noqa: ANN001
                self.gets += 1
                return SimpleNamespace(status_code=200, json=lambda: {"data": {"usage": 4.25}})

        s = _S()
        clock = [0.0]
        c = OpenRouterClient(
            api_key="k",
            cache_dir=tmp_path,
            pool=_two_model_pool(),
            session=s,
            clock=lambda: clock[0],
        )
        assert c.key_usage_usd() == 4.25 and c.key_usage_usd() == 4.25 and s.gets == 1  # memoised
        clock[0] += 31.0
        assert c.key_usage_usd() == 4.25 and s.gets == 2

    def test_key_usage_failure_returns_none_never_raises(self, tmp_path: Path) -> None:
        class _S:
            def get(self, url, headers=None, timeout=None):  # noqa: ANN001
                raise requests.ConnectionError("down")

        c = OpenRouterClient(api_key="k", cache_dir=tmp_path, pool=_two_model_pool(), session=_S())
        assert c.key_usage_usd() is None

    def test_app_v05_counts_llm_and_prior_spend(self) -> None:
        from perturb_eval.experiments import provenance as pv

        src = (Path(__file__).resolve().parents[1] / "scripts" / "modal" / "app_v05.py").read_text()
        assert "prior_spend_usd" in pv.REQUIRED_ENTRYPOINT_KWARGS
        for needle in ("llm_cost_usd", "gpu_cost_usd", "prior_spend_usd", "key_usage_usd()"):
            assert needle in src, needle


class TestQG6PerRoleSchemaProbe:
    def test_preferred_models_are_probed_with_their_roles_schema(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        from perturb_eval.experiments import v05_preflight as pf

        seen: list[tuple[str, str]] = []

        def fake_probe_model(self, model_id, prompt):  # noqa: ANN001
            role = next(r for r in ROLES if r in prompt)
            seen.append((model_id, role))
            payload = dict(pf.ROLE_PROBE_PAYLOADS[role])
            if model_id == "openai/gpt-oss-20b" and role == "Architect":
                payload.pop("backbone")  # a model that cannot meet the Architect schema
            return True, "ok", payload

        monkeypatch.setattr(OpenRouterClient, "probe_model", fake_probe_model)
        table = pf.openrouter_probe_all({"OPENROUTER_API_KEY": "k"})
        for role, prefs in DEFAULT_POOL.role_preferences.items():
            for mid in prefs:
                assert (mid, role) in seen
        assert set(table) == {m.model_id for m in DEFAULT_POOL.models}
        e = table["openai/gpt-oss-20b"]
        assert (
            e["live"] is False
            and e["roles"]["Architect"]["ok"] is False
            and "schema" in e["roles"]["Architect"]["verdict"]
        )
        assert e["roles"]["Validator"]["ok"] is True
        assert all(t["live"] for m, t in table.items() if m != "openai/gpt-oss-20b")

    def test_role_check_uses_the_roles_own_probe_result(self, tmp_path: Path) -> None:
        from perturb_eval.experiments.v05_preflight import PreflightError

        table = _liveness()
        # stub/one answers every role except Architect: Architect has only 2 live preferred -> still ok
        table["stub/one"]["roles"] = {"Architect": {"ok": False, "verdict": "schema"}}
        rep = _run(tmp_path, probe_fn=lambda env: table)
        assert rep.ok
        table["stub/two"]["roles"] = {"Architect": {"ok": False, "verdict": "schema"}}
        with pytest.raises(PreflightError, match=r"Architect.*1 live preferred"):
            _run(tmp_path, probe_fn=lambda env: table)


class TestQG7LiveThresholdBoundary:
    def test_exactly_two_live_preferred_passes(self, tmp_path: Path) -> None:
        rep = _run(tmp_path, probe_fn=lambda env: _liveness(live=["stub/one", "stub/two"]))
        assert rep.ok and rep.roster_liveness["stub/three"]["live"] is False

    def test_only_the_role_with_dead_preferences_is_named(self, tmp_path: Path) -> None:
        from perturb_eval.experiments.v05_preflight import PreflightError

        ms = tuple(
            ModelSpec(model_id=f"p/{n}", family=n, param_count_b=1, strengths=()) for n in "abcd"
        )
        pool = LLMPool(
            models=ms,
            role_preferences={
                **{r: ("p/a", "p/b", "p/c") for r in ROLES if r != "Trainer"},
                "Trainer": ("p/d", "p/c", "p/b"),
            },
        )
        table = {
            m.model_id: {
                "live": m.model_id != "p/d" and m.model_id != "p/c",
                "verdict": "x",
                "probed_at": "2026-09-28T23:00:00+00:00",
            }
            for m in ms
        }
        with pytest.raises(PreflightError) as ei:
            _run(tmp_path, pool=pool, probe_fn=lambda env: table)
        role_fails = [f for f in ei.value.failures if "live preferred" in f]
        assert len(role_fails) == 1 and "Trainer" in role_fails[0]


class TestQG8DefaultPoolPath:
    def test_probe_count_pin_holds_for_the_real_roster(self, tmp_path: Path) -> None:
        from perturb_eval.experiments.v05_preflight import PreflightError
        from tests.test_label_contract import _full_liveness

        table = _full_liveness({})
        missing = DEFAULT_POOL.models[-1].model_id
        del table[missing]
        with pytest.raises(PreflightError, match=r"probed 7 of 8 roster models") as ei:
            _run(tmp_path, pool=None, probe_fn=lambda env: table)
        assert missing in str(ei.value)

    def test_probe_all_uses_the_pool_it_is_given(self, tmp_path: Path, monkeypatch) -> None:
        from perturb_eval.experiments import v05_preflight as pf

        seen: list[str] = []
        monkeypatch.setattr(
            OpenRouterClient,
            "probe_model",
            lambda self, m, p: (
                seen.append(m) or True,
                "ok",
                dict(pf.ROLE_PROBE_PAYLOADS["Validator"]),
            ),
        )
        table = pf.openrouter_probe_all({"OPENROUTER_API_KEY": "k"}, pool=_POOL)
        assert set(table) == {m.model_id for m in _POOL.models} and set(seen) == set(table)

    def test_app_v05_calls_preflight_without_a_pool_override(self) -> None:
        import ast

        src = (Path(__file__).resolve().parents[1] / "scripts" / "modal" / "app_v05.py").read_text()
        calls = [
            n
            for n in ast.walk(ast.parse(src))
            if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "preflight"
        ]
        assert calls and all(all(k.arg != "pool" for k in c.keywords) for c in calls)


class TestQG9LegacyAndNoneProbes:
    def test_legacy_str_probe_fails_against_the_real_roster(self, tmp_path: Path) -> None:
        from perturb_eval.experiments.v05_preflight import PreflightError

        with pytest.raises(PreflightError, match=r"probed 1 of 8 roster models"):
            _run(tmp_path, pool=None, probe_fn=lambda env: "openai/gpt-oss-20b")

    def test_none_probe_fails(self, tmp_path: Path) -> None:
        from perturb_eval.experiments.v05_preflight import PreflightError

        with pytest.raises(PreflightError, match="no usable model"):
            _run(tmp_path, probe_fn=lambda env: None)

    def test_no_single_model_probe_helper_remains(self) -> None:
        from perturb_eval.experiments import v05_preflight as pf

        assert not hasattr(
            pf, "openrouter_probe"
        )  # QG-9: deleted (it made 8 paid calls and was unused)


class TestQG11ProbeAllVerdicts:
    def test_transport_error_and_404_are_recorded_not_raised(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        from perturb_eval.experiments import v05_preflight as pf

        def fake(self, model_id, prompt):  # noqa: ANN001
            if model_id.startswith("deepseek/"):
                raise requests.ConnectionError("x")
            if model_id.startswith("z-ai/"):
                return False, "http 404", None
            role = next(r for r in ROLES if r in prompt)
            return True, "ok", dict(pf.ROLE_PROBE_PAYLOADS[role])

        monkeypatch.setattr(OpenRouterClient, "probe_model", fake)
        table = pf.openrouter_probe_all({"OPENROUTER_API_KEY": "k"})
        assert table["deepseek/deepseek-v4-flash"]["live"] is False
        assert "transport ConnectionError" in table["deepseek/deepseek-v4-flash"]["verdict"]
        assert (
            table["z-ai/glm-4.7-flash"]["live"] is False
            and "404" in table["z-ai/glm-4.7-flash"]["verdict"]
        )
        assert sum(1 for e in table.values() if e["live"]) == 6
        assert all(re.match(r"\d{4}-\d{2}-\d{2}T", e["probed_at"]) for e in table.values())
